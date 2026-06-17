"""render_markdown — produce the lab-style markdown table from classified rows.

Reads data/table_template.md to discover the column order, then writes a
populated table sorted by tier (Essential → Professional → Enterprise) then
display name. Output is uploaded to outputs/<resourcename>-policies.md.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from promptflow.core import tool

from _storage import write_text


TIER_ORDER = {"Essential": 0, "Professional": 1, "Enterprise": 2}


def _slug(resource_name: str) -> str:
    """Match the lab-05 filename convention: lowercase, alphanumeric only."""
    return re.sub(r"[^a-z0-9]", "", resource_name.lower())


def _column_headers(template_path: Path) -> list[str]:
    """Read the first non-empty line of the template as the column header row."""
    for line in template_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("|") and not re.match(r"^\|[\s\-|]+\|$", line):
            return [c.strip() for c in line.strip("|").split("|")]
    raise ValueError(f"No header row found in template {template_path}")


def _row_for(policy: dict, resource_name: str) -> dict[str, str]:
    """Map a classified policy to template column values.

    Header names from lab-03/table-template.md:
      Service | Policy Display Name | Policy Description | Policy ID |
      Default Value | Allowed Values | Category | Notes | Tier
    """
    desc = policy.get("aligned_description") or policy.get("description") or ""
    allowed = policy.get("allowed_values") or [policy.get("effect") or ""]
    return {
        "Service": resource_name,
        "Policy Display Name": policy.get("display_name", ""),
        "Policy Description": desc.replace("|", "\\|"),
        "Policy ID": policy.get("policy_id", ""),
        "Default Value": policy.get("effect") or "",
        "Allowed Values": ", ".join(str(a) for a in allowed),
        "Category": "Built-in",
        "Notes": "",
        "Tier": policy.get("tier", ""),
    }


@tool
def render_markdown(
    policies: list[dict],
    resource_name: str,
    template_path: str,
    output_prefix: str,
) -> dict:
    here = Path(__file__).parent
    headers = _column_headers(here / template_path)

    sorted_policies = sorted(
        policies,
        key=lambda p: (TIER_ORDER.get(p.get("tier", ""), 99), p.get("display_name", "")),
    )

    lines: list[str] = []
    lines.append(f"# {resource_name} Policies")
    lines.append("")
    lines.append(
        f"_Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} "
        f"— {len(sorted_policies)} policies._"
    )
    lines.append("")
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")

    for policy in sorted_policies:
        row = _row_for(policy, resource_name)
        # Honour the template's column order, even if it gets re-arranged.
        cells = [row.get(h, "") for h in headers]
        lines.append("| " + " | ".join(cells) + " |")

    content = "\n".join(lines) + "\n"

    slug = _slug(resource_name)
    blob_path = f"{output_prefix}/{slug}-policies.md"

    # Construct a full URI from the env-provided account URL when running
    # locally; in Foundry the runtime resolves relative datastore paths.
    import os
    account_url = os.environ.get("STORAGE_ACCOUNT_URL", "")
    if account_url:
        uri = f"{account_url}/{blob_path}"
        actual_uri = write_text(uri, content)
    else:
        # Foundry path style — the runtime writes into the workspace blobstore.
        # We still serialize the markdown so it shows up in run outputs.
        local_out = here / "_out"
        local_out.mkdir(exist_ok=True)
        (local_out / f"{slug}-policies.md").write_text(content, encoding="utf-8")
        actual_uri = str(local_out / f"{slug}-policies.md")

    return {
        "output_uri": actual_uri,
        "row_count": len(sorted_policies),
        "blob_path": blob_path,
    }
