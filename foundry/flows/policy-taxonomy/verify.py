"""verify — deterministic post-conditions on the rendered table.

Replaces the LLM-driven "Verification" step in lab-05-plan.md. Every check
here is a fast assertion that fails the row in batch mode rather than letting
a malformed taxonomy land silently.

Returns:
  - passed: bool
  - row_count: int
  - issues: list[str] of human-readable failures (empty if passed)
"""

from __future__ import annotations

from typing import Any

from promptflow.core import tool

from _storage import read_parquet


VALID_EFFECTS = {
    "Audit",
    "AuditIfNotExists",
    "Deny",
    "DeployIfNotExists",
    "Modify",
    "Append",
    "Disabled",
    "Manual",
}

VALID_TIERS = {"Essential", "Professional", "Enterprise"}


@tool
def verify(
    policies: list[dict],
    output_uri: str,
    catalog_uri: str,
) -> dict:
    issues: list[str] = []

    # 1. Row count > 0 — empty taxonomies are configuration errors.
    if not policies:
        issues.append("Zero rows in classified output.")
        return {"passed": False, "row_count": 0, "issues": issues}

    # 2. Every row has tier + effect + non-empty display name.
    for p in policies:
        pid = p.get("policy_id", "<missing-id>")
        if p.get("tier") not in VALID_TIERS:
            issues.append(f"{pid}: invalid or missing tier '{p.get('tier')}'.")
        if not p.get("display_name", "").strip():
            issues.append(f"{pid}: empty display_name.")
        effect = p.get("effect")
        if effect not in VALID_EFFECTS:
            issues.append(f"{pid}: invalid effect '{effect}'.")

    # 3. No duplicate display names within the file.
    names = [p["display_name"] for p in policies]
    seen: dict[str, int] = {}
    for n in names:
        seen[n] = seen.get(n, 0) + 1
    duplicates = [n for n, c in seen.items() if c > 1]
    if duplicates:
        issues.append(f"Duplicate display names: {duplicates[:5]}{'…' if len(duplicates) > 5 else ''}")

    # 4. Tier consistency heuristics from lab-05-plan.md — these catch the
    # most common rule drift. The list is intentionally small; deeper checks
    # belong in a manual review.
    for p in policies:
        text = f"{p.get('display_name', '')} {p.get('description', '')}".lower()
        tier = p.get("tier")

        if tier == "Essential" and "private endpoint" in text:
            issues.append(
                f"{p['policy_id']}: 'private endpoint' wording but tier=Essential "
                "(expected Enterprise per rules)."
            )
        if tier == "Essential" and "private link" in text:
            issues.append(
                f"{p['policy_id']}: 'private link' wording but tier=Essential."
            )

    # 5. Every policy_id traces back to the source catalog.
    try:
        catalog = read_parquet(catalog_uri)
        valid_ids = set(catalog["policy_id"].astype(str))
        unknown = [p["policy_id"] for p in policies if p["policy_id"] not in valid_ids]
        if unknown:
            issues.append(
                f"{len(unknown)} policy_id values not present in catalog "
                f"(first 3: {unknown[:3]})."
            )
    except Exception as exc:  # noqa: BLE001
        # Don't block on a transient catalog read failure, but record it.
        issues.append(f"Catalog cross-reference skipped: {exc!r}")

    return {
        "passed": len(issues) == 0,
        "row_count": len(policies),
        "issues": issues,
    }
