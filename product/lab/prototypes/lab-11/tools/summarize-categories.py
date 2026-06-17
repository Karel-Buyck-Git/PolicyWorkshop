"""
summarize-categories.py

Walks every policies.md under the output directory, parses the markdown table,
and summarizes the values found in the "Category" column.

Usage:
    python summarize-categories.py [--source <folder>] [--md <file>]

Default --source:
    C:\\GIT\\Karel Buyck Git Azure Policy Workshop\\PolicyWorkshop\\product\\lab\\prototypes\\lab-xx\\output

When --md is supplied, a markdown report is written to that path instead of
printing to stdout.
"""

import argparse
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_SOURCE = Path(
    r"C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop"
    r"\product\lab\prototypes\lab-xx\output"
)


def split_row(line: str) -> list[str]:
    """Split a markdown table row into stripped cells."""
    parts = line.split("|")
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [cell.strip() for cell in parts]


def is_separator_row(cells: list[str]) -> bool:
    return all(set(c) <= set("-:") and c for c in cells)


def parse_categories(md_path: Path) -> list[str]:
    """Return all values from the Category column in the given policies.md."""
    categories: list[str] = []
    header: list[str] | None = None
    cat_idx: int | None = None

    for raw in md_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = split_row(line)
        if header is None:
            if "Category" in cells:
                header = cells
                cat_idx = cells.index("Category")
            continue
        if is_separator_row(cells):
            continue
        if cat_idx is not None and cat_idx < len(cells):
            value = cells[cat_idx]
            if value:
                categories.append(value)

    return categories


def render_text(
    source: Path,
    files_seen: int,
    overall: Counter,
    per_folder: dict[str, Counter],
    files_without_category: list[str],
) -> str:
    lines: list[str] = []
    total_policies = sum(overall.values())
    unique_categories = len(overall)

    lines.append(f"Scanned {files_seen} policies.md file(s) under {source}")
    lines.append(f"Total policy rows with a category: {total_policies}")
    lines.append(f"Unique category values: {unique_categories}")
    lines.append("")
    lines.append("Category counts (descending):")
    lines.append(f"  {'Count':>6}  Category")
    lines.append(f"  {'-' * 6}  {'-' * 40}")
    for category, count in overall.most_common():
        lines.append(f"  {count:>6}  {category}")

    if files_without_category:
        lines.append("")
        lines.append("Folders with no parsed Category column:")
        for folder in files_without_category:
            lines.append(f"  - {folder}")

    lines.append("")
    lines.append("Categories appearing in only one folder:")
    folder_count_by_category: Counter = Counter()
    for counts in per_folder.values():
        for category in counts:
            folder_count_by_category[category] += 1
    singletons = [c for c, n in folder_count_by_category.items() if n == 1]
    if not singletons:
        lines.append("  (none)")
    else:
        for category in sorted(singletons):
            owning_folder = next(
                folder for folder, counts in per_folder.items() if category in counts
            )
            lines.append(f"  - {category}  (in {owning_folder})")

    return "\n".join(lines)


def render_markdown(
    source: Path,
    files_seen: int,
    overall: Counter,
    per_folder: dict[str, Counter],
    files_without_category: list[str],
) -> str:
    total_policies = sum(overall.values())
    unique_categories = len(overall)

    lines: list[str] = []
    lines.append("# Policy Category Summary")
    lines.append("")
    lines.append(f"- **Source:** `{source}`")
    lines.append(f"- **Files scanned:** {files_seen}")
    lines.append(f"- **Total policy rows with a category:** {total_policies}")
    lines.append(f"- **Unique category values:** {unique_categories}")
    lines.append("")

    lines.append("## Category counts (descending)")
    lines.append("")
    lines.append("| Rank | Count | Category |")
    lines.append("| ---: | ----: | -------- |")
    for rank, (category, count) in enumerate(overall.most_common(), start=1):
        lines.append(f"| {rank} | {count} | {category} |")
    lines.append("")

    if files_without_category:
        lines.append("## Folders with no parsed Category column")
        lines.append("")
        for folder in files_without_category:
            lines.append(f"- {folder}")
        lines.append("")

    folder_count_by_category: Counter = Counter()
    for counts in per_folder.values():
        for category in counts:
            folder_count_by_category[category] += 1
    singletons = [c for c, n in folder_count_by_category.items() if n == 1]

    lines.append("## Categories appearing in only one folder")
    lines.append("")
    if not singletons:
        lines.append("_(none)_")
    else:
        lines.append("| Category | Folder |")
        lines.append("| -------- | ------ |")
        for category in sorted(singletons):
            owning_folder = next(
                folder for folder, counts in per_folder.items() if category in counts
            )
            lines.append(f"| {category} | {owning_folder} |")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--md",
        type=Path,
        default=None,
        help="If set, write a markdown report to this path instead of stdout text.",
    )
    args = parser.parse_args()

    source: Path = args.source
    if not source.is_dir():
        raise SystemExit(f"Source folder not found: {source}")

    overall = Counter()
    per_folder: dict[str, Counter] = defaultdict(Counter)
    files_seen = 0
    files_without_category: list[str] = []

    for md_path in sorted(source.rglob("policies.md")):
        files_seen += 1
        folder = md_path.parent.name
        categories = parse_categories(md_path)
        if not categories:
            files_without_category.append(folder)
            continue
        overall.update(categories)
        per_folder[folder].update(categories)

    if args.md is not None:
        args.md.parent.mkdir(parents=True, exist_ok=True)
        args.md.write_text(
            render_markdown(source, files_seen, overall, per_folder, files_without_category),
            encoding="utf-8",
        )
        print(f"Wrote markdown report to {args.md}")
    else:
        print(render_text(source, files_seen, overall, per_folder, files_without_category))


if __name__ == "__main__":
    main()
