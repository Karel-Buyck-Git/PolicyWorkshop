"""
extract-policies.py

Reads Azure Policy JSON files from a scoped resource folder, extracts key fields,
and either writes one Markdown table file per category (default) or emits a flat
JSONL extraction file for downstream agent consumption (--jsonl mode).

Usage:
    python extract-policies.py [--source <folder>] [--out <folder>] [--jsonl]

Modes:
    default   Groups policies by metadata.category and writes one .md per category.
    --jsonl   Writes a single <source-folder-name>.jsonl to <out>. No tier field is
              included — the consuming agent performs tier classification itself.

Defaults:
    --source  C:\\GIT\\Official Azure Policy\\azure-policy\\built-in-policies\\policyDefinitions
    --out     C:\\GIT\\Karel Buyck Git Azure Policy Workshop\\PolicyWorkshop\\product\\lab\\prototypes\\lab-08\\output
"""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Effect hardening rank  (higher = more restrictive)
# ---------------------------------------------------------------------------

_EFFECT_RANK: dict[str, int] = {
    "deny":               7,
    "modify":             6,
    "deployifnotexists":  5,
    "auditifnotexists":   4,
    "audit":              3,
    "append":             2,
    "manual":             1,
    "disabled":           0,
}


def hardened_value(allowed: list[str]) -> str:
    """Return the most hardened (highest-ranked) effect from allowed values."""
    return max(allowed, key=lambda v: _EFFECT_RANK.get(v.lower(), -1), default="")


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
# Tier classification — keyword rationale
#
# Classification is based on the commercial tier definitions in the pitch deck
# ("What's included in each flavour?"). The tiers are cumulative — Professional
# includes everything in Essential, Enterprise includes everything in Professional.
#
# Matching priority: Enterprise > Professional > Essential > default (Essential)
# The first tier whose keyword set contains a match wins.
#
# ESSENTIAL — Secure baseline: the minimum viable governance layer.
#   Target: organizations embedding governance in their DevOps flow.
#   Keywords cover: identity & access controls, encryption at rest/in transit,
#   certificate and key hygiene, backup and resiliency, tagging and naming,
#   FinOps / SKU governance, and quota controls.
#   Rationale: these are non-negotiable hygiene policies — cheap to enforce,
#   high risk if absent. No advanced networking or observability required.
#
# PROFESSIONAL — Security posture & operations: proactive and network-aware.
#   Target: enterprises running ongoing policy operations.
#   Keywords cover: network hardening (public access, VNet, service endpoints,
#   CORS), vulnerability and threat management (Defender, threat protection),
#   identity governance (PIM), auto-remediation signals, and auditing &
#   observability (audit effects, logging, monitoring).
#   Rationale: these policies require operational maturity — someone needs to
#   act on the findings. Network hardening sits here rather than Essential
#   because it requires architectural decisions (VNet design, endpoint strategy).
#   Auditing sits here rather than Enterprise because compliance reporting
#   is a Professional capability; Enterprise adds the regulatory framework layer.
#
# ENTERPRISE — Governance, zero trust & regulatory alignment.
#   Target: organizations wanting governance fully managed end-to-end.
#   Keywords cover: private connectivity (private endpoints, private link),
#   diagnostic settings and resource logs (deep telemetry pipelines),
#   Security Center / Sentinel integration, regulatory compliance signals,
#   zone redundancy / high availability (99.99% SLA commitments), and
#   data sovereignty / confidential computing controls.
#   Rationale: these policies either require significant infrastructure investment
#   (private endpoints, availability zones), map directly to regulatory frameworks
#   (NIS2, ISO 27001, CIS), or depend on centralised security tooling
#   (Sentinel, Defender for Cloud at scale). They cannot be self-served without
#   dedicated governance expertise.
# ---------------------------------------------------------------------------

ENTERPRISE_KEYWORDS  = {"private endpoint", "private link", "diagnostic", 
                         "customer-managed key", "resource logs", "diagnostic settings", 
                         "security center", "sentinel", "regulatory", "zone redundant", 
                         "availability zone", "confidential", "sovereignty"}

PROFESSIONAL_KEYWORDS = {"public", "vnet", "virtual network", "cors", "pim", 
                          "service endpoint", "public ip", "disable public network access",
                          "audit", "log", "logging", "monitoring", "observability",
                          "vulnerability", "defender", "threat", "remediate"}

ESSENTIAL_KEYWORDS   = {"identity", "managed identity", "crypto", "tls", "https", 
                         "backup", "tag", "sas", "mfa", "rbac", "sku", "key", 
                         "certificate", "encryption", "service-managed key",
                         "resilience", "recovery", "naming", "quota"}



def classify_tier(name: str, description: str) -> str:
    text = (name + " " + description).lower()

    # Most specific wins: Enterprise > Professional > Essential
    if any(kw in text for kw in ENTERPRISE_KEYWORDS):
        return "Enterprise"
    if any(kw in text for kw in PROFESSIONAL_KEYWORDS):
        return "Professional"
    if any(kw in text for kw in ESSENTIAL_KEYWORDS):
        return "Essential"

    return "Essential"   # safe default; flag for review


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
        "hardened":         hardened_value(allowed),
    }
    if include_tier:
        record["tier"] = classify_tier(clean_name, props.get("description", ""))
    return record


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

HEADER = "| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Hardened Value | Category | Version | Type | Tier |"
SEP    = "|---|---|---|---|---|---|---|---|---|---|---|---|"


def md_row(p: dict, n: int) -> str:
    allowed = ", ".join(p["allowed"]) if p["allowed"] else ""
    desc    = p["description"].replace("|", "\\|").replace("\n", " ")
    name    = p["name"].replace("|", "\\|")
    return (
        f"| {n} | {name} | {p['policy_id']} | {p['tag']} | {desc} | {allowed} | {p['effect']} | {p['hardened']}"
        f" | {p['category']} | {p['version']} | {p['policyType']} | {p['tier']} |"
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
DEFAULT_OUT = (
    r"C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop"
    r"\product\lab\prototypes\lab-08\output"
)


def write_jsonl(policies: list[dict], source_dir: Path, out_dir: Path) -> Path:
    out_file = out_dir / f"{source_dir.name.lower().replace(' ', '-')}.jsonl"
    with out_file.open("w", encoding="utf-8") as fh:
        for p in policies:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    return out_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Azure Policy definitions to Markdown tables or JSONL.")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Scoped policy source folder")
    parser.add_argument("--out",    default=DEFAULT_OUT,    help="Output folder")
    parser.add_argument("--jsonl",  action="store_true",    help="Emit a flat JSONL file for agent consumption (no tier, no MD)")
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
