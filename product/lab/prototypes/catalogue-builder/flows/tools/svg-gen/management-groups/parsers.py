"""Three input parsers -> one canonical :class:`model.Node` tree.

A consumer describes their scope hierarchy in whichever format is handiest; all
three produce an identical tree, so the renderers never need to know which was
used. ``detect_format`` + ``parse`` are the entry points.

Formats
-------
indent  Indentation = depth. One node per line: ``[kind:]Name[ | scopeId]``.
edges   ``Parent -> Child`` lines define structure (chains allowed). Optional
        attribute lines ``Name | kind | scopeId`` enrich a node.
json    The canonical model directly: ``{name, kind, scopeId, children:[...]}``.
csv     A management-group inventory export (see ``tabular.py`` for columns).
xlsx    The same inventory as an .xlsx workbook (handled in the loader, since
        it is binary, not text).

Every parser returns a single root Node (a lone tenant root). A forest raises a
clear error asking the author to add a shared root.
"""
from __future__ import annotations

import json
from pathlib import Path

import tabular
from model import KINDS, Node

# --------------------------------------------------------------------------- #
# format detection
# --------------------------------------------------------------------------- #


def detect_format(path: Path, text: str | None = None) -> str:
    """Pick the format from extension, then (for text formats) content.

    ``text`` may be ``None`` for binary inputs — extension alone resolves xlsx.
    """
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return "xlsx"
    if suffix == ".csv":
        return "csv"
    if suffix == ".json":
        return "json"
    stripped = (text or "").lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        return "json"
    # Only count edge arrows on non-comment lines.
    if any("->" in line for line in _significant_lines(text or "")):
        return "edges"
    return "indent"


def parse(text: str, fmt: str) -> Node:
    """Parse a *text* input. (xlsx is binary and handled by the loader.)"""
    if fmt == "json":
        return parse_json(text)
    if fmt == "edges":
        return parse_edges(text)
    if fmt == "indent":
        return parse_indent(text)
    if fmt == "csv":
        return parse_table_csv(text)
    raise ValueError(f"Unknown text format {fmt!r}; expected json, edges, indent or csv.")


def parse_table_csv(text: str) -> Node:
    """Build the tree from CSV inventory text."""
    return tabular.tree_from_rows(tabular.read_csv(text))


# --------------------------------------------------------------------------- #
# shared helpers
# --------------------------------------------------------------------------- #


def _significant_lines(text: str) -> list[str]:
    """Lines that carry data: blanks and ``#`` comments dropped (indent kept)."""
    out = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        out.append(raw.rstrip())
    return out


def _split_kind_name_id(token: str) -> tuple[str, str, str | None]:
    """Parse ``[kind:]Name[ | scopeId]`` into ``(kind, name, scope_id)``."""
    scope_id: str | None = None
    if "|" in token:
        token, scope_id = (part.strip() for part in token.split("|", 1))
        scope_id = scope_id or None
    kind = "mg"
    if ":" in token:
        prefix, rest = token.split(":", 1)
        if prefix.strip() in KINDS:
            kind, token = prefix.strip(), rest
    name = token.strip()
    if not name:
        raise ValueError("Encountered a node with an empty name.")
    return kind, name, scope_id


# --------------------------------------------------------------------------- #
# indent
# --------------------------------------------------------------------------- #


def parse_indent(text: str) -> Node:
    lines = [l for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    if not lines:
        raise ValueError("Indent input is empty.")

    unit = _detect_indent_unit(lines)
    root: Node | None = None
    # stack of (level, node); parent is the deepest entry with a smaller level.
    stack: list[tuple[int, Node]] = []

    for raw in lines:
        indent = len(raw) - len(raw.lstrip())
        if indent % unit:
            raise ValueError(
                f"Inconsistent indentation ({indent} spaces) — expected a multiple "
                f"of {unit}. Line: {raw.strip()!r}"
            )
        level = indent // unit
        kind, name, scope_id = _split_kind_name_id(raw.strip())
        node = Node(name=name, kind=kind, scope_id=scope_id)

        if level == 0:
            if root is not None:
                raise ValueError(
                    f"Multiple top-level nodes ({root.name!r} and {name!r}); "
                    "give them a single shared root."
                )
            root = node
            stack = [(0, node)]
            continue

        while stack and stack[-1][0] >= level:
            stack.pop()
        if not stack or stack[-1][0] != level - 1:
            raise ValueError(f"Node {name!r} is indented too deeply for its parent.")
        stack[-1][1].children.append(node)
        stack.append((level, node))

    assert root is not None
    return root


def _detect_indent_unit(lines: list[str]) -> int:
    """Smallest non-zero indent width (tabs counted as one), defaulting to 2."""
    indents = []
    for raw in lines:
        body = raw.replace("\t", " ")  # one tab == one space for width purposes
        indents.append(len(body) - len(body.lstrip()))
    nonzero = [i for i in indents if i]
    return min(nonzero) if nonzero else 2


# --------------------------------------------------------------------------- #
# edges
# --------------------------------------------------------------------------- #


def parse_edges(text: str) -> Node:
    # name -> attrs (kind, scope_id); name -> ordered child names
    attrs: dict[str, tuple[str, str | None]] = {}
    children: dict[str, list[str]] = {}
    is_child: set[str] = set()

    def ensure(name: str) -> None:
        children.setdefault(name, [])

    for line in _significant_lines(text):
        if "->" in line:
            chain = [part.strip() for part in line.split("->")]
            if any(not part for part in chain):
                raise ValueError(f"Malformed edge line: {line.strip()!r}")
            for parent, child in zip(chain, chain[1:]):
                ensure(parent)
                ensure(child)
                if child not in children[parent]:
                    children[parent].append(child)
                is_child.add(child)
        elif "|" in line:
            parts = [p.strip() for p in line.split("|")]
            name = parts[0]
            kind = parts[1] if len(parts) > 1 and parts[1] else "mg"
            scope_id = parts[2] if len(parts) > 2 and parts[2] else None
            if kind not in KINDS:
                raise ValueError(f"Unknown kind {kind!r} for {name!r} in: {line.strip()!r}")
            ensure(name)
            attrs[name] = (kind, scope_id)
        else:
            ensure(line.strip())

    if not children:
        raise ValueError("Edge input has no nodes.")

    roots = [n for n in children if n not in is_child]
    if len(roots) != 1:
        raise ValueError(
            f"Expected exactly one root, found {len(roots)}: {sorted(roots)}. "
            "Connect them under a single shared root."
        )

    def build(name: str, seen: frozenset[str]) -> Node:
        if name in seen:
            raise ValueError(f"Cycle detected at {name!r}.")
        kind, scope_id = attrs.get(name, ("mg", None))
        node = Node(name=name, kind=kind, scope_id=scope_id)
        node.children = [build(c, seen | {name}) for c in children[name]]
        return node

    return build(roots[0], frozenset())


# --------------------------------------------------------------------------- #
# json
# --------------------------------------------------------------------------- #


def parse_json(text: str) -> Node:
    data = json.loads(text)
    if isinstance(data, list):
        raise ValueError(
            "JSON input must be a single root object, not a list. "
            "Wrap your nodes under one root."
        )
    return _node_from_dict(data)


def _node_from_dict(data: dict) -> Node:
    if "name" not in data:
        raise ValueError(f"JSON node is missing 'name': {data!r}")
    kind = data.get("kind", "mg")
    scope_id = data.get("scopeId", data.get("scope_id"))
    node = Node(name=str(data["name"]), kind=kind, scope_id=scope_id)
    node.children = [_node_from_dict(c) for c in data.get("children", [])]
    return node
