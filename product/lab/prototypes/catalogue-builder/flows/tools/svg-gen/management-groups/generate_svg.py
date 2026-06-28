"""
generate_svg.py — Azure management-group hierarchy → SVG.

Turns a scope tree into theme-aware SVG diagrams. The tree can be supplied in any
of five formats (auto-detected): indented text, parent -> child edges, canonical
JSON, or a management-group inventory export (csv / xlsx). Two variants are
produced by default, named after the input file:

    <name>.minimal.svg   names only, depth-shaded
    <name>.rich.svg      scope ids, subscriptions, resource groups, legend

Typical workflow (see README.md):
    1. copy a file from template/ into input/, rename it (e.g. contoso-mgmt-groups.xlsx)
    2. fill it in
    3. run with no arguments — every file in input/ is picked up and rendered to
       output/ using the input's own name.

Usage:
    # pick up everything in input/  ->  output/
    python flows/tools/svg-gen/management-groups/generate_svg.py
    # or target one file explicitly
    python flows/tools/svg-gen/management-groups/generate_svg.py --input <path> \\
        [--format auto|indent|edges|json|csv|xlsx] \\
        [--variant both|minimal|rich] [--out-dir <dir>]

The tool is self-contained: default input/ and output/ are its own folders, and it
imports nothing outside this directory. The module also exposes load_tree() /
generate() for embedding elsewhere — see the folder README.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the sibling modules importable when run by path. The tool is fully
# self-contained — it reaches into nothing outside its own folder.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import tabular  # noqa: E402
from model import Node  # noqa: E402
from parsers import detect_format, parse  # noqa: E402
from render import RENDERERS  # noqa: E402

# Default in/out: the tool's own folders (created on demand).
DEFAULT_IN_DIR = _HERE / "input"
DEFAULT_OUT_DIR = _HERE / "output"

VARIANTS = ("minimal", "rich")
# Source files the input/ scan recognises (anything else, e.g. .gitkeep, is skipped).
INPUT_SUFFIXES = {".txt", ".json", ".csv", ".xlsx"}


def output_name(stem: str, variant: str) -> str:
    """Output filename for an input ``stem`` and ``variant`` (e.g. contoso.rich.svg)."""
    return f"{stem}.{variant}.svg"


# --------------------------------------------------------------------------- #
# reusable API (also used when embedding the tool elsewhere)
# --------------------------------------------------------------------------- #


def load_tree(input_path: Path, fmt: str = "auto") -> Node:
    """Read ``input_path`` and parse it into the canonical scope tree.

    xlsx is binary (read as bytes); every other format is text.
    """
    path = Path(input_path)
    if fmt == "auto":
        # Resolve binary formats by extension before touching the bytes as text.
        fmt = detect_format(path, None if path.suffix.lower() == ".xlsx" else path.read_text(encoding="utf-8"))
    if fmt == "xlsx":
        return tabular.tree_from_rows(tabular.read_xlsx(path))
    return parse(path.read_text(encoding="utf-8"), fmt)


def generate(root: Node, out_dir: Path, variant: str = "both", stem: str = "mgmt-groups") -> list[Path]:
    """Render the requested variant(s) into ``out_dir`` as ``<stem>.<variant>.svg``."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = VARIANTS if variant == "both" else (variant,)
    written: list[Path] = []
    for name in wanted:
        svg = RENDERERS[name](root)
        path = out_dir / output_name(stem, name)
        path.write_text(svg, encoding="utf-8")
        written.append(path)
    return written


def discover_inputs(in_dir: Path) -> list[Path]:
    """Return the source files in ``in_dir`` (by recognised extension), sorted."""
    return sorted(
        p for p in Path(in_dir).glob("*")
        if p.is_file() and p.suffix.lower() in INPUT_SUFFIXES
    )


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--input", type=Path, default=None,
        help="A single input file. If omitted, every file in input/ is picked up.",
    )
    parser.add_argument(
        "--format", default="auto",
        choices=["auto", "indent", "edges", "json", "csv", "xlsx"],
    )
    parser.add_argument("--variant", choices=["both", *VARIANTS], default="both")
    parser.add_argument(
        "--out-dir", type=Path, default=DEFAULT_OUT_DIR,
        help="Output folder (default: the tool's own output/ folder).",
    )
    args = parser.parse_args(argv)

    if args.input is not None:
        if not args.input.is_file():
            raise SystemExit(f"Input file not found: {args.input}")
        inputs = [args.input]
    else:
        inputs = discover_inputs(DEFAULT_IN_DIR)
        if not inputs:
            raise SystemExit(
                f"No input files found in {DEFAULT_IN_DIR}.\n"
                "Copy a file from template/ into input/, rename + fill it, then re-run "
                "(or pass --input <path>)."
            )

    for path in inputs:
        try:
            root = load_tree(path, args.format)
        except ValueError as exc:
            raise SystemExit(f"Could not parse {path}: {exc}")
        for written in generate(root, args.out_dir, args.variant, stem=path.stem):
            print(f"Wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
