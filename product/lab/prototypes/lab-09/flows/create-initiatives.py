"""
create-initiatives.py

Phase 3 for lab-09:
  - Recursively scans every `output/**/*.md` file produced by the earlier phases.
  - Parses each policies.md markdown table, discovering column indices from the
    header row (no hard-coded positions).
  - Groups every row by its Domain column value (empty / whitespace /
    "undefined" all collapse into the "undefined" bucket).
  - Writes one consolidated initiative file per domain to
    `initiatives/<domain-slug>/initiative.md` at the lab root.
  - Each initiative file is divided into one section per Category
    (alphabetically). Within each section the `#` column restarts at 1.

Run after enrich-policies.py.

Usage:
    python flows/create-initiatives.py
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = LAB_ROOT / "output"
INITIATIVES_DIR = LAB_ROOT / "initiatives"

# Canonical column layout (matches enrich-policies.py).
COLUMNS = [
    "#", "Policy", "Policy ID", "Tag", "Description",
    "Allowed Values", "Default Value", "Hardened Value",
    "Category", "Domain", "Version", "Type", "Tier",
]

HEADER_LINE = (
    "| # | Policy | Policy ID | Tag | Description | Allowed Values | "
    "Default Value | Hardened Value | Category | Domain | Version | Type | Tier |"
)
SEP_LINE = "|---|---|---|---|---|---|---|---|---|---|---|---|---|"

_SEP_RE = re.compile(r"^\|[-:\s|]+\|$")


# ---------------------------------------------------------------------------
# Markdown table parsing
# ---------------------------------------------------------------------------

def parse_table(path: Path) -> list[dict]:
    """Parse the markdown table in ``path`` and return a list of row dicts.

    Column names are discovered from the header row, then each row is re-keyed
    onto COLUMNS so downstream code stays uniform regardless of source layout.
    Returns [] when no table is found.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    header_cells: list[str] | None = None
    rows: list[dict] = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        if header_cells is None and "Policy ID" in stripped:
            header_cells = [c.strip() for c in stripped.strip("|").split("|")]
            in_table = True
            continue
        if _SEP_RE.match(stripped):
            continue
        if in_table and header_cells:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < len(header_cells):
                cells.extend([""] * (len(header_cells) - len(cells)))
            raw_row = dict(zip(header_cells, cells[: len(header_cells)]))
            row = {col: raw_row.get(col, "") for col in COLUMNS}
            rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Domain normalisation
# ---------------------------------------------------------------------------

def normalize_domain(value: str) -> str:
    s = (value or "").strip()
    if not s or s.lower() == "undefined":
        return "undefined"
    return s


def domain_slug(domain: str) -> str:
    return domain.lower().replace(" ", "-")


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def md_row(row: dict, n: int) -> str:
    return (
        f"| {n} | {row['Policy']} | {row['Policy ID']} | {row['Tag']} | "
        f"{row['Description']} | {row['Allowed Values']} | {row['Default Value']} | "
        f"{row['Hardened Value']} | {row['Category']} | {row['Domain']} | "
        f"{row['Version']} | {row['Type']} | {row['Tier']} |"
    )


def write_initiative(domain: str, rows: list[dict]) -> tuple[Path, int]:
    """Write one initiative file for ``domain``; return (path, category_count)."""
    by_category: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_category[r["Category"]].append(r)

    out_path = INITIATIVES_DIR / domain_slug(domain) / "initiative.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [f"# {domain} Initiative", ""]
    for category in sorted(by_category.keys(), key=lambda c: c.lower()):
        section_rows = sorted(by_category[category], key=lambda r: r["Policy"].lower())
        lines.append(f"## {category}")
        lines.append("")
        lines.append(HEADER_LINE)
        lines.append(SEP_LINE)
        for i, r in enumerate(section_rows, start=1):
            lines.append(md_row(r, i))
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path, len(by_category)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not OUTPUT_DIR.exists():
        print(f"ERROR: output folder not found: {OUTPUT_DIR}", file=sys.stderr)
        raise SystemExit(1)

    md_files = [
        p for p in OUTPUT_DIR.rglob("*.md")
        if "initiatives" not in p.parts
    ]

    by_domain: dict[str, list[dict]] = defaultdict(list)
    for path in sorted(md_files):
        rows = parse_table(path)
        if not rows:
            print(f"[Phase 3] WARNING: no table found, skipping {path}")
            continue
        for r in rows:
            domain = normalize_domain(r.get("Domain", ""))
            r["Domain"] = domain
            by_domain[domain].append(r)

    for domain in sorted(by_domain.keys(), key=lambda d: d.lower()):
        rows = by_domain[domain]
        out_path, category_count = write_initiative(domain, rows)
        rel = out_path.relative_to(LAB_ROOT).as_posix()
        suffix = "category" if category_count == 1 else "categories"
        print(f"[Phase 3] Written: {rel}  ({len(rows)} policies across {category_count} {suffix})")


if __name__ == "__main__":
    main()
