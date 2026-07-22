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
    --source  C:\\GIT\\Official Azure Policy\\azure-policy\\built-in-policies\\policyDefinitions\\App Service
    --out     C:\\GIT\\Karel Buyck Git Azure Policy Workshop\\PolicyWorkshop\\product\\lab\\prototypes\\lab-06\\output
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Tier classification
# ---------------------------------------------------------------------------

ENTERPRISE_KEYWORDS  = {"audit", "log", "logging", "private endpoint", "private link", "diagnostic"}
PROFESSIONAL_KEYWORDS = {"public", "vnet", "virtual network", "cors", "resilience", "recovery", "pim", "zone"}
ESSENTIAL_KEYWORDS   = {"identity", "managed identity", "crypto", "tls", "https", "backup",
                        "tag", "sas", "mfa", "rbac", "sku", "key", "certificate", "encryption"}


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

    effect_param = props.get("parameters", {}).get("effect", {})
    then_effect  = (props.get("policyRule") or {}).get("then", {}).get("effect", "")

    effect  = effect_param.get("defaultValue") or then_effect
    allowed = effect_param.get("allowedValues") or ([then_effect] if then_effect else [])

    record = {
        "name":        name,
        "description": props.get("description", ""),
        "policyType":  props.get("policyType", ""),
        "category":    (props.get("metadata") or {}).get("category", "Uncategorized"),
        "version":     (props.get("metadata") or {}).get("version", ""),
        "effect":      effect,
        "allowed":     allowed,
    }
    if include_tier:
        record["tier"] = classify_tier(name, props.get("description", ""))
    return record


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

HEADER = "| Policy | Description | Effect | Allowed Values | Category | Version | Type | Tier |"
SEP    = "|---|---|---|---|---|---|---|---|"


def md_row(p: dict) -> str:
    allowed = ", ".join(p["allowed"]) if p["allowed"] else ""
    desc    = p["description"].replace("|", "\\|").replace("\n", " ")
    name    = p["name"].replace("|", "\\|")
    return (
        f"| {name} | {desc} | {p['effect']} | {allowed}"
        f" | {p['category']} | {p['version']} | {p['policyType']} | {p['tier']} |"
    )


def write_category_file(category: str, items: list[dict], out_dir: Path) -> Path:
    slug     = "".join(c if c.isalnum() else "-" for c in category.lower()).strip("-")
    out_file = out_dir / f"{slug}-policies.md"

    sorted_items = sorted(items, key=lambda x: (x["tier"], x["name"]))

    lines = [
        f"# {category} Policies",
        "",
        HEADER,
        SEP,
        *[md_row(p) for p in sorted_items],
        "",
    ]
    out_file.write_text("\n".join(lines), encoding="utf-8")
    return out_file


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

DEFAULT_SOURCE = (
    r"C:\GIT\Official Azure Policy\azure-policy\built-in-policies"
    r"\policyDefinitions\App Service"
)
DEFAULT_OUT = (
    r"C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop"
    r"\product\lab\prototypes\lab-06\output"
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
    json_files = list(source_dir.glob("*.json"))
    print(f"Found {len(json_files)} JSON files in {source_dir.name}")

    include_tier = not args.jsonl
    policies = [p for f in json_files if (p := extract_policy(f, include_tier=include_tier)) is not None]
    print(f"Extracted {len(policies)} active policies (deprecated/invalid skipped)")

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
            print(f"  {len(items):>3} policies  ->  {out_file.name}")

    print("\nDone.")


if __name__ == "__main__":
    main()
