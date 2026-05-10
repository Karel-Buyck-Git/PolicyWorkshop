"""classify_tier — Claude (via Foundry MaaS) assigns Essential/Professional/Enterprise.

This is the only LLM step that's strictly required. We batch policies into
chunks of ~20 to keep each call short and cheap. Claude is asked to return
strict JSON; any row missing tier or rationale fails the run.

Reads:
  - data/tier_rules.md  (extracted from lab-05-plan.md "Tier classification")
  - prompts/classify_tier.jinja2

Auth:
  - AZURE_AI_INFERENCE_ENDPOINT  -> https://<project>.<region>.models.ai.azure.com
  - AZURE_AI_INFERENCE_DEPLOYMENT -> e.g. "claude-sonnet-4-6"
  - Managed identity via DefaultAzureCredential
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    JsonSchemaFormat,
    SystemMessage,
    UserMessage,
)
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from promptflow.core import tool


VALID_TIERS = {"Essential", "Professional", "Enterprise"}

# JSON schema enforced on Claude's response — keeps the parsing trivial.
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "policy_id": {"type": "string"},
                    "tier": {"type": "string", "enum": list(VALID_TIERS)},
                    "rationale": {"type": "string", "maxLength": 200},
                },
                "required": ["policy_id", "tier", "rationale"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}


def _client() -> ChatCompletionsClient:
    endpoint = os.environ.get("AZURE_AI_INFERENCE_ENDPOINT")
    if not endpoint:
        raise RuntimeError(
            "AZURE_AI_INFERENCE_ENDPOINT must be set. In Foundry this is "
            "wired via a connection; locally export it before `pf flow test`."
        )
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    return ChatCompletionsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
        # azure-ai-inference picks up the bearer token automatically when
        # given DefaultAzureCredential; explicit provider kept for clarity.
        api_version="2024-08-01-preview",
    )


def _chunks(seq: list[Any], size: int) -> Iterable[list[Any]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def _render_prompt(rules: str, tier_set: set[str], batch: list[dict]) -> str:
    here = Path(__file__).parent
    env = Environment(
        loader=FileSystemLoader(str(here / "prompts")),
        undefined=StrictUndefined,
        autoescape=False,
    )
    template = env.get_template("classify_tier.jinja2")
    return template.render(
        tier_rules=rules,
        tier_set=sorted(tier_set),
        policies=batch,
    )


@tool
def classify_tier(
    policies: list[dict],
    tier_set: str,
    tier_rules_path: str,
    batch_size: int = 20,
) -> dict:
    if not policies:
        return {"policies": [], "stats": {"calls": 0, "classified": 0}}

    # Resolve paths relative to the flow directory so this works the same
    # locally and in Foundry.
    here = Path(__file__).parent
    rules_text = (here / tier_rules_path).read_text(encoding="utf-8")

    requested_tiers = {t.strip().capitalize() for t in tier_set.split(",") if t.strip()}
    invalid = requested_tiers - VALID_TIERS
    if invalid:
        raise ValueError(f"Unknown tiers in tier_set: {sorted(invalid)}")

    deployment = os.environ.get("AZURE_AI_INFERENCE_DEPLOYMENT", "claude-sonnet-4-6")
    client = _client()

    classifications: dict[str, dict] = {}
    calls = 0

    for batch in _chunks(policies, batch_size):
        # Prompt only includes the four fields the rules rely on — keeps
        # tokens down and prevents the model from latching onto noise.
        compact = [
            {
                "policy_id": p["policy_id"],
                "display_name": p["display_name"],
                "description": p.get("description") or "",
                "effect": p.get("effect") or "",
            }
            for p in batch
        ]
        user_prompt = _render_prompt(rules_text, requested_tiers, compact)

        response = client.complete(
            model=deployment,
            messages=[
                SystemMessage(
                    "You are a senior Azure Cloud Solutions Architect classifying "
                    "Azure Policy definitions into commercial tiers. Follow the "
                    "rules exactly and reply with valid JSON only."
                ),
                UserMessage(user_prompt),
            ],
            response_format=JsonSchemaFormat(
                name="tier_classification",
                schema=RESPONSE_SCHEMA,
                strict=True,
            ),
            temperature=0.0,
            max_tokens=2000,
        )
        calls += 1

        payload = json.loads(response.choices[0].message.content)
        for row in payload["results"]:
            tier = row["tier"]
            if tier not in requested_tiers:
                # Out-of-scope tier — drop the policy from this run rather
                # than mis-tag it. Caller can re-run with a wider tier_set.
                continue
            classifications[row["policy_id"]] = {
                "tier": tier,
                "rationale": row["rationale"],
            }

    enriched: list[dict] = []
    for p in policies:
        cls = classifications.get(p["policy_id"])
        if cls is None:
            # Policy was either out-of-scope or the model dropped it. Skip;
            # verify.py will surface the count delta.
            continue
        enriched.append({**p, **cls})

    return {
        "policies": enriched,
        "stats": {
            "calls": calls,
            "classified": len(enriched),
            "skipped": len(policies) - len(enriched),
        },
    }
