"""Shared markdown-table helpers for the Catalogue Builder catalogue.

Parsing/serialising the catalogue `policies.md` tables, cell escaping, and slug
derivation. Extracted from `catalogue_builder/create_initiatives.py` so consumers
(`catalogue_builder/quality_control.py`, `tools/summarize_categories.py`) reuse one
implementation instead of importing a producer step.

`parse_table` discovers column indices from the header row (no hard-coded
positions) and re-keys every row onto `COLUMNS`, returning a list of row dicts.
"""
import re
from pathlib import Path

# Canonical column layout (matches enrich_policies.py / extract_policies.py).
COLUMNS = [
    "#", "Policy", "Policy ID", "Tag", "Description",
    "Requires Parameters", "Requires Managed Identity",
    "Allowed Values", "Default Value", "Soft Value", "Hardened Value",
    "Category", "Domain", "Version", "Type", "Tier",
]

_SEP_RE = re.compile(r"^\|[-:\s|]+\|$")

# Cells are pipe-separated; a literal pipe inside a value is escaped as ``\|``.
# Split only on *unescaped* pipes so policy names/descriptions containing a pipe
# (e.g. NIST control titles "… | Cryptographic Protection") stay in one cell —
# otherwise the columns shift and the real GUID lands in the wrong column,
# breaking the Policy-ID join. Cells are unescaped on read; md_escape re-escapes
# on write so the round-trip is stable.
_CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")


def split_cells(stripped: str) -> list[str]:
    inner = stripped.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.strip().replace("\\|", "|") for c in _CELL_SPLIT_RE.split(inner)]


def md_escape(value: str) -> str:
    return (value or "").replace("|", "\\|").replace("\n", " ")


def slugify(value: str) -> str:
    """Lowercase, replace any run of non-alphanumerics with a single hyphen."""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (value or "").lower())).strip("-")


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
            header_cells = split_cells(stripped)
            in_table = True
            continue
        if _SEP_RE.match(stripped):
            continue
        if in_table and header_cells:
            cells = split_cells(stripped)
            if len(cells) < len(header_cells):
                cells.extend([""] * (len(header_cells) - len(cells)))
            raw_row = dict(zip(header_cells, cells[: len(header_cells)]))
            row = {col: raw_row.get(col, "") for col in COLUMNS}
            rows.append(row)
    return rows
