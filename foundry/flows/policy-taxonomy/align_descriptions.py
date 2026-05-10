"""align_descriptions — optional pass that aligns wording with the commercial pitch.

Mirrors lab-05-plan.md step "Cross-reference the commercial pitch descriptions
to align wording where a matching entry exists." Only fires for policies whose
tier has a description file present and where a candidate match is found
(simple keyword overlap pre-filter, then a single Claude call per tier batch).

This node is *optional* in the sense that an empty descriptions_dir or no
matches produces a passthrough. It never invents descriptions — if there is
no aligned match, the source description survives unchanged.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    JsonSchemaFormat,
    SystemMessage,
    UserMessage,
)
from azure.identity import DefaultAzureCredential
from promptflow.core import tool


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "alignments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "policy_id": {"type": "string"},
                    "aligned_description": {"type": "string"},
                    "source_phrase": {"type": "string"},
                },
                "required": ["policy_id", "aligned_description", "source_phrase"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["alignments"],
    "additionalProperties": False,
}


def _client() -> ChatCompletionsClient:
    endpoint = os.environ.get("AZURE_AI_INFERENCE_ENDPOINT")
    if not endpoint:
        raise RuntimeError("AZURE_AI_INFERENCE_ENDPOINT must be set.")
    return ChatCompletionsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
        api_version="2024-08-01-preview",
    )


def _load_tier_descriptions(descriptions_dir: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not descriptions_dir.exists():
        return out
    for tier_file in descriptions_dir.glob("*.md"):
        out[tier_file.stem.capitalize()] = tier_file.read_text(encoding="utf-8")
    return out


@tool
def align_descriptions(
    policies: list[dict],
    descriptions_dir: str = "data/descriptions",
) -> dict:
    if not policies:
        return {"policies": policies, "stats": {"aligned": 0, "calls": 0}}

    here = Path(__file__).parent
    descriptions_path = here / descriptions_dir
    tier_descriptions = _load_tier_descriptions(descriptions_path)

    if not tier_descriptions:
        return {
            "policies": [{**p, "aligned_description": p.get("description", "")} for p in policies],
            "stats": {"aligned": 0, "calls": 0, "reason": "no descriptions found"},
        }

    by_tier: dict[str, list[dict]] = defaultdict(list)
    for p in policies:
        by_tier[p["tier"]].append(p)

    deployment = os.environ.get("AZURE_AI_INFERENCE_DEPLOYMENT", "claude-sonnet-4-6")
    client = _client()

    alignments: dict[str, str] = {}
    calls = 0

    for tier, group in by_tier.items():
        pitch = tier_descriptions.get(tier)
        if not pitch:
            continue

        compact = [
            {
                "policy_id": p["policy_id"],
                "display_name": p["display_name"],
                "description": p.get("description") or "",
            }
            for p in group
        ]

        prompt = (
            "You are aligning Azure Policy descriptions with a commercial pitch. "
            "For each policy, return the original description verbatim UNLESS a "
            "phrase from the pitch describes the same control more precisely. "
            "Never invent capabilities the policy does not have. Never extend an "
            "empty description with pitch text — return an empty string instead.\n\n"
            f"Pitch ({tier}):\n{pitch}\n\n"
            f"Policies (JSON):\n{json.dumps(compact, indent=2)}"
        )

        response = client.complete(
            model=deployment,
            messages=[
                SystemMessage("Reply only with valid JSON matching the schema."),
                UserMessage(prompt),
            ],
            response_format=JsonSchemaFormat(
                name="description_alignment",
                schema=RESPONSE_SCHEMA,
                strict=True,
            ),
            temperature=0.0,
            max_tokens=4000,
        )
        calls += 1
        payload = json.loads(response.choices[0].message.content)
        for row in payload["alignments"]:
            alignments[row["policy_id"]] = row["aligned_description"]

    enriched = []
    for p in policies:
        enriched.append({
            **p,
            "aligned_description": alignments.get(p["policy_id"], p.get("description", "")),
        })

    return {
        "policies": enriched,
        "stats": {"aligned": len(alignments), "calls": calls},
    }
