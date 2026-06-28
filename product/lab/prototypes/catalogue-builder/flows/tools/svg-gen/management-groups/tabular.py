"""Tabular inventory input — a management-group export as ``.csv`` or ``.xlsx``.

A consumer can point svg-gen at a real tenant inventory (the kind exported from
the portal / a collection script) instead of hand-authoring the tree. Both file
types are read with the **standard library only** (``csv``; ``zipfile`` +
``xml.etree`` for xlsx), then mapped to the canonical :class:`model.Node` tree.

Expected columns (matched by header name, case-insensitive; extra/missing
columns are tolerated)::

    Display Name | Type | ID | In Scope | Depth | Parent | Full Path |
    [Access Level] | Child Subscription Count | Total Subscription Count | Exclusion Note

Rules
-----
* ``In Scope`` is an import filter: ``Yes`` rows are imported, anything else is
  skipped entirely.
* ``Type`` maps to kind: *Management group*→``mg``, *Subscription*→``sub``,
  *Resource group*→``rg``.
* ``Parent`` (always a management group, whose Display Name is unique) defines
  structure; ``Full Path`` is the fallback when a parent was filtered out.
* ``ID`` synthesises the Azure ``scope_id``; counts ride along in ``Node.meta``.
"""
from __future__ import annotations

import csv
import io
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from model import Node

_TYPE_TO_KIND = {
    "management group": "mg",
    "managementgroup": "mg",
    "subscription": "sub",
    "resource group": "rg",
    "resourcegroup": "rg",
}


# --------------------------------------------------------------------------- #
# readers: file -> list[dict] keyed by header
# --------------------------------------------------------------------------- #


def read_csv(text: str) -> list[dict]:
    """Parse CSV text into a list of header->value dicts."""
    rows = list(csv.reader(io.StringIO(text)))
    return _rows_to_dicts(rows)


def read_xlsx(path: Path) -> list[dict]:
    """Parse the first worksheet of an .xlsx workbook into header->value dicts."""
    with zipfile.ZipFile(path) as z:
        shared = _shared_strings(z)
        sheet_name = _first_worksheet(z)
        grid = _sheet_grid(z.read(sheet_name), shared)
    return _rows_to_dicts(grid)


def _rows_to_dicts(rows: list[list[str]]) -> list[dict]:
    if not rows:
        return []
    header = [h.strip() for h in rows[0]]
    out: list[dict] = []
    for raw in rows[1:]:
        if not any(cell.strip() for cell in raw):
            continue
        out.append({header[i]: (raw[i] if i < len(raw) else "") for i in range(len(header))})
    return out


# --------------------------------------------------------------------------- #
# xlsx internals (stdlib zip + xml)
# --------------------------------------------------------------------------- #

_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _shared_strings(z: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.iter(_NS + "t")) for si in root.findall(_NS + "si")]


def _first_worksheet(z: zipfile.ZipFile) -> str:
    sheets = sorted(n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
    if not sheets:
        raise ValueError("Workbook has no worksheet.")
    return sheets[0]


def _col_index(ref: str) -> int:
    """Excel cell ref (e.g. 'C12') -> 0-based column index."""
    letters = re.match(r"([A-Z]+)", ref).group(1)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _sheet_grid(xml: bytes, shared: list[str]) -> list[list[str]]:
    sheet = ET.fromstring(xml)
    data = sheet.find(_NS + "sheetData")
    grid: list[list[str]] = []
    for row in data.findall(_NS + "row"):
        cells: dict[int, str] = {}
        for c in row.findall(_NS + "c"):
            idx = _col_index(c.get("r", "A1"))
            ctype = c.get("t")
            v = c.find(_NS + "v")
            inline = c.find(_NS + "is")
            if ctype == "s" and v is not None:
                cells[idx] = shared[int(v.text)]
            elif inline is not None:
                cells[idx] = "".join(t.text or "" for t in inline.iter(_NS + "t"))
            elif v is not None:
                cells[idx] = v.text or ""
            else:
                cells[idx] = ""
        width = (max(cells) + 1) if cells else 0
        grid.append([cells.get(i, "") for i in range(width)])
    return grid


# --------------------------------------------------------------------------- #
# rows -> Node tree
# --------------------------------------------------------------------------- #


def tree_from_rows(rows: list[dict]) -> Node:
    if not rows:
        raise ValueError("Inventory has no rows.")

    # case-insensitive header lookup against the first row's keys
    keymap = {k.strip().lower(): k for k in rows[0]}

    def get(row: dict, *aliases: str) -> str:
        for alias in aliases:
            key = keymap.get(alias.lower())
            if key is not None:
                return (row.get(key) or "").strip()
        return ""

    has_scope_col = any(a in keymap for a in ("in scope", "inscope"))

    built: list[tuple[Node, str, str]] = []  # (node, parent_name, full_path)
    mg_by_name: dict[str, Node] = {}
    roots: list[Node] = []

    for row in rows:
        if has_scope_col and get(row, "In Scope", "InScope").lower() != "yes":
            continue
        name = get(row, "Display Name", "DisplayName", "Name")
        if not name:
            continue
        kind = _TYPE_TO_KIND.get(get(row, "Type").lower(), "mg")
        node = Node(name=name, kind=kind, scope_id=_scope_id(kind, get(row, "ID", "Id")))
        node.meta = _meta(get, row)

        parent_name = get(row, "Parent")
        full_path = get(row, "Full Path", "FullPath")
        built.append((node, parent_name, full_path))
        if kind == "mg":
            mg_by_name.setdefault(name, node)
        if not parent_name:
            roots.append(node)

    if len(roots) != 1:
        raise ValueError(
            f"Expected exactly one in-scope root (a row with no Parent), found {len(roots)}."
        )
    root = roots[0]

    for node, parent_name, full_path in built:
        if node is root:
            continue
        parent = mg_by_name.get(parent_name) or _nearest_ancestor(full_path, mg_by_name)
        (parent or root).children.append(node)

    return root


def _scope_id(kind: str, raw_id: str) -> str | None:
    if not raw_id:
        return None
    if raw_id.startswith("/"):
        return raw_id
    if kind == "mg":
        return f"/providers/Microsoft.Management/managementGroups/{raw_id}"
    if kind == "sub":
        return f"/subscriptions/{raw_id}"
    return raw_id


def _nearest_ancestor(full_path: str, mg_by_name: dict[str, Node]) -> Node | None:
    """Walk an ancestor chain ('A,B,C') from deepest to shallowest for a kept MG."""
    if not full_path:
        return None
    for ancestor in reversed([p.strip() for p in full_path.split(",") if p.strip()]):
        if ancestor in mg_by_name:
            return mg_by_name[ancestor]
    return None


def _meta(get, row: dict) -> dict:
    meta: dict = {}
    total = get(row, "Total Subscription Count", "TotalSubscriptionCount")
    child = get(row, "Child Subscription Count", "ChildSubscriptionCount")
    access = get(row, "Access Level", "AccessLevel")
    if total:
        meta["subscriptions"] = total
    if child:
        meta["child_subscriptions"] = child
    if access:
        meta["access_level"] = access
    return meta
