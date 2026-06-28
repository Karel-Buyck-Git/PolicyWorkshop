"""
extract_policies.py

Reads Azure Policy JSON files from a scoped resource folder, extracts key fields,
and either writes one Markdown table file per category (default) or emits a flat
JSONL extraction file for downstream agent consumption (--jsonl mode).

Usage:
    python extract_policies.py [--source <folder>] [--out <folder>] [--hierarchy <file>] [--jsonl]

Modes:
    default   Groups policies by metadata.category and writes one .md per category.
    --jsonl   Writes a single <source-folder-name>.jsonl to <out>. No tier field is
              included — the consuming agent performs tier classification itself.

Defaults:
    --source     C:\\GIT\\Official Azure Policy\\azure-policy\\built-in-policies\\policyDefinitions
    --out        <lab-root>\\catalogue\\definitions            (derived from this script's location)
    --hierarchy  <lab-root>\\docs\\azure-domain-hierachy.md
"""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # flows/ root

from shared.hierarchy import load_domain_map  # shared parser (single source)  # noqa: E402
from shared.tiers import classify             # shared tier engine (single source)  # noqa: E402


# ---------------------------------------------------------------------------
# Effect hardening rank  (higher = more restrictive)
# ---------------------------------------------------------------------------

_EFFECT_RANK: dict[str, int] = {
    "denyaction":         9,
    "deny":               8,
    "modify":             7,
    "enforcesetting":     6,
    "mutate":             6,
    "deployifnotexists":  5,
    "auditifnotexists":   4,
    "audit":              3,
    "append":             2,
    "addtonetworkgroup":  2,
    "manual":             1,
    "disabled":           0,
}

# Canonical casing for known effects. Source allowedValues casing is inconsistent
# (e.g. both "deny" and "Deny", "deployIfNotExists" and "DeployIfNotExists"), so we
# normalise on output. Unknown effects pass through unchanged.
CANONICAL_EFFECT: dict[str, str] = {
    "denyaction":        "DenyAction",
    "deny":              "Deny",
    "modify":            "Modify",
    "enforcesetting":    "EnforceSetting",
    "mutate":            "Mutate",
    "deployifnotexists": "DeployIfNotExists",
    "auditifnotexists":  "AuditIfNotExists",
    "audit":             "Audit",
    "append":            "Append",
    "addtonetworkgroup": "AddToNetworkGroup",
    "manual":            "Manual",
    "disabled":          "Disabled",
}


def canonical_effect(value: str) -> str:
    """Return the canonically-cased form of an effect, or the input unchanged."""
    return CANONICAL_EFFECT.get((value or "").strip().lower(), value)


def hardened_value(allowed: list[str]) -> str:
    """Return the most hardened (highest-ranked) effect from allowed values."""
    return max(allowed, key=lambda v: _EFFECT_RANK.get(v.lower(), -1), default="")


def soft_value(allowed: list[str]) -> str:
    """Return the softest (lowest-ranked) effect, skipping 'Disabled'.

    'Disabled' is treated as "no policy" rather than a real soft setting,
    so we prefer the least-restrictive effect that still does something
    (e.g. Manual / Append / Audit). If only 'Disabled' is allowed, it is
    returned as the fallback.
    """
    if not allowed:
        return ""
    non_disabled = [v for v in allowed if v.lower() != "disabled"]
    pool = non_disabled or allowed
    return min(pool, key=lambda v: _EFFECT_RANK.get(v.lower(), 99))


# ---------------------------------------------------------------------------
# Version comparison (semver-ish: pre-releases lose to GA at same numeric ver)
# ---------------------------------------------------------------------------

def version_key(v: str) -> tuple:
    """Parse '1.2.1' or '1.0.0-preview' into a sortable tuple; higher = newer."""
    if not v:
        return (0, 0, 0, 0)
    is_prerelease = "-" in v
    main = v.split("-", 1)[0]
    parts: list[int] = []
    for p in main.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return (*parts[:3], 0 if is_prerelease else 1)


def deduplicate(policies: list[dict]) -> list[dict]:
    """Collapse rows sharing a Policy ID; keep the highest version."""
    best: dict[str, dict] = {}
    for p in policies:
        pid = p["policy_id"]
        if not pid:
            continue
        existing = best.get(pid)
        if existing is None or version_key(p["version"]) > version_key(existing["version"]):
            best[pid] = p
    return list(best.values())


# ---------------------------------------------------------------------------
# Tier classification
#
# This is the first-pass tier; enrich_policies.py re-runs the same engine as the
# final, authoritative pass. The keyword rules live in the authored
# config/tier-rules.yaml and are parsed by tiers.py, so extract and enrich share
# exactly one definition (`classify`, imported above) — there is no second copy
# to drift. See tier-rules.yaml for the Essential / Professional / Enterprise
# rationale and the full keyword set.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

_TAG_RE = re.compile(r"^\[([^\]]+)\]:\s*")


def extract_tag(display_name: str) -> tuple[str, str]:
    """Return (tag, clean_name). tag is empty string when no bracket prefix."""
    m = _TAG_RE.match(display_name)
    if m:
        return m.group(1), display_name[m.end():]
    return "", display_name


_IDENTITY_EFFECTS = {"deployifnotexists", "modify"}


def requires_managed_identity(allowed: list[str], effect: str) -> str:
    """Return 'Yes' if any allowed effect (or the fixed effect) requires a managed identity."""
    candidates = [v.lower() for v in allowed] if allowed else [effect.lower()]
    return "Yes" if any(v in _IDENTITY_EFFECTS for v in candidates) else "No"


def requires_assignment_params(props: dict) -> str:
    """Return 'Yes' if any non-effect parameter has no defaultValue, else 'No'."""
    for name, param in (props.get("parameters") or {}).items():
        if name.lower() == "effect":
            continue
        if "defaultValue" not in param:
            return "Yes"
    return "No"


def extract_policy(path: Path, include_tier: bool = True) -> dict | None:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  [SKIP] {path.name}: {exc}")
        return None

    props = raw.get("properties", {})
    name  = props.get("displayName")

    if not name:
        print(f"  [SKIP] {path.name}: missing displayName")
        return None

    if name.startswith("[Deprecated]"):
        return None

    tag, clean_name = extract_tag(name)

    effect_param = props.get("parameters", {}).get("effect", {})
    then_effect  = (props.get("policyRule") or {}).get("then", {}).get("effect", "")

    effect  = effect_param.get("defaultValue") or then_effect
    allowed = effect_param.get("allowedValues") or ([then_effect] if then_effect else [])

    record = {
        "name":        clean_name,
        "policy_id":   raw.get("name", ""),
        "tag":         tag,
        "description": props.get("description", ""),
        "policyType":  props.get("policyType", ""),
        "category":    (props.get("metadata") or {}).get("category", "Uncategorized"),
        "version":     (props.get("metadata") or {}).get("version", ""),
        "effect":      effect,
        "allowed":     allowed,
        "soft":        soft_value(allowed),
        "hardened":       hardened_value(allowed),
        "requires_params":   requires_assignment_params(props),
        "requires_identity": requires_managed_identity(allowed, effect),
    }
    if include_tier:
        record["tier"] = classify(clean_name, props.get("description", ""))
    return record


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

HEADER = "| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |"
SEP    = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"


def md_row(p: dict, n: int) -> str:
    allowed  = ", ".join(canonical_effect(v) for v in p["allowed"]) if p["allowed"] else ""
    effect   = canonical_effect(p["effect"])
    soft     = canonical_effect(p["soft"])
    hardened = canonical_effect(p["hardened"])
    desc    = p["description"].replace("|", "\\|").replace("\n", " ")
    name    = p["name"].replace("|", "\\|")
    return (
        f"| {n} | {name} | {p['policy_id']} | {p['tag']} | {desc} | {p['requires_params']} | {p['requires_identity']}"
        f" | {allowed} | {effect} | {soft} | {hardened}"
        f" | {p['category']} | {p['domain']} | {p['version']} | {p['policyType']} | {p['tier']} |"
    )


def write_category_file(category: str, items: list[dict], out_dir: Path) -> Path:
    slug    = "".join(c if c.isalnum() else "-" for c in category.lower()).strip("-")
    cat_dir = out_dir / slug
    cat_dir.mkdir(exist_ok=True)
    out_file = cat_dir / "policies.md"

    sorted_items = sorted(items, key=lambda x: (x["tier"], x["name"]))

    lines = [
        f"# {category} Policies",
        "",
        HEADER,
        SEP,
        *[md_row(p, i) for i, p in enumerate(sorted_items, start=1)],
        "",
    ]
    out_file.write_text("\n".join(lines), encoding="utf-8")
    return out_file


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

DEFAULT_SOURCE = (
    r"C:\GIT\Official Azure Policy\azure-policy\built-in-policies"
    r"\policyDefinitions"
)
# Output/hierarchy defaults derive from this script's location (project root is two
# levels up), so the pipeline targets its own tree with no flags. --source still
# points at the shared official policy repo.
from shared.paths import PROJECT_ROOT, DEFINITIONS_DIR, HIERARCHY_FILE  # noqa: F401,E402
DEFAULT_OUT = str(DEFINITIONS_DIR)
DEFAULT_HIERARCHY = str(HIERARCHY_FILE)


def write_jsonl(policies: list[dict], source_dir: Path, out_dir: Path) -> Path:
    out_file = out_dir / f"{source_dir.name.lower().replace(' ', '-')}.jsonl"
    with out_file.open("w", encoding="utf-8") as fh:
        for p in policies:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    return out_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Azure Policy definitions to Markdown tables or JSONL.")
    parser.add_argument("--source",    default=DEFAULT_SOURCE,    help="Scoped policy source folder")
    parser.add_argument("--out",       default=DEFAULT_OUT,       help="Output folder")
    parser.add_argument("--hierarchy", default=DEFAULT_HIERARCHY, help="Domain-hierarchy markdown file")
    parser.add_argument("--jsonl",     action="store_true",       help="Emit a flat JSONL file for agent consumption (no tier, no MD)")
    args = parser.parse_args()

    source_dir = Path(args.source)
    out_dir    = Path(args.out)

    if not source_dir.exists():
        print(f"ERROR: source folder not found: {source_dir}")
        raise SystemExit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    # --- Read & extract ---
    json_files = list(source_dir.rglob("*.json"))
    print(f"Found {len(json_files)} JSON files in {source_dir.name}")

    include_tier = not args.jsonl
    policies = [p for f in json_files if (p := extract_policy(f, include_tier=include_tier)) is not None]
    print(f"Extracted {len(policies)} active policies (deprecated/invalid skipped)")

    before = len(policies)
    policies = deduplicate(policies)
    print(f"Deduplicated by Policy ID (kept highest version): {before} -> {len(policies)}")

    if args.jsonl:
        # --- JSONL mode: flat extraction for agent consumption ---
        out_file = write_jsonl(policies, source_dir, out_dir)
        print(f"\nWrote {len(policies)} records -> {out_file}")
    else:
        # --- MD mode: one file per category ---
        hierarchy_path = Path(args.hierarchy)
        if not hierarchy_path.exists():
            print(f"ERROR: hierarchy file not found: {hierarchy_path}")
            raise SystemExit(1)
        domain_map = load_domain_map(hierarchy_path)
        print(f"Loaded domain map: {len(domain_map)} categories from {hierarchy_path.name}")

        for p in policies:
            p["domain"] = domain_map.get(p["category"], "undefined")

        by_category: dict[str, list] = defaultdict(list)
        for p in policies:
            by_category[p["category"]].append(p)

        print(f"\nWriting {len(by_category)} category file(s) to {out_dir}\n")
        for category, items in sorted(by_category.items()):
            out_file = write_category_file(category, items, out_dir)
            print(f"  {len(items):>3} policies  ->  {out_file.relative_to(out_dir)}")

    print("\nDone.")


if __name__ == "__main__":
    main()
