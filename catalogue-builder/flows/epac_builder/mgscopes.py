"""Resolve management-group NAMES (from the svg-gen hierarchy) to Azure scope ids.

The epac-builder lets each manifest selection name its target management group(s);
this module loads the customer's hierarchy file (any svg-gen format — json/csv/xlsx/
indent/edges) via the self-contained svg-gen tool and returns a ``{name: scope_id}``
index. Selections with no target get :data:`PLACEHOLDER_SCOPE` downstream.
"""
import sys
from pathlib import Path

# A selection with no target MG (and no explicit scope) is rendered with this
# placeholder: a syntactically valid but non-existent management-group id, so EPAC
# plan / the Azure API rejects it loudly — forcing the author to set a target MG or
# drop the selection (no silent fall-back to the deployment root).
PLACEHOLDER_SCOPE = "/providers/Microsoft.Management/managementGroups/REPLACE-set-managementGroup-in-manifest"

# flows/epac_builder/ -> flows/ -> flows/tools/svg-gen/management-groups
_TOOL_DIR = Path(__file__).resolve().parents[1] / "tools" / "svg-gen" / "management-groups"


class HierarchyError(Exception):
    """The management-group hierarchy could not be loaded or a name is unknown."""


def _load_tree(path):
    p = Path(path)
    if not p.is_file():
        raise HierarchyError(f"management-group hierarchy file not found: {p}")
    if not _TOOL_DIR.is_dir():
        raise HierarchyError(f"svg-gen management-groups tool not found at {_TOOL_DIR}")
    sys.path.insert(0, str(_TOOL_DIR))
    try:
        from generate_svg import load_tree  # self-contained tool; puts its dir on sys.path
    except ImportError as exc:  # pragma: no cover - environment misconfiguration
        raise HierarchyError(f"could not import the svg-gen loader from {_TOOL_DIR}: {exc}")
    return load_tree(p)


def load_mg_index(path):
    """Return ``{node_name: scope_id}`` for every node carrying a scope id (MGs + subs)."""
    root = _load_tree(path)
    index = {}

    def walk(node):
        if getattr(node, "scope_id", None):
            index[node.name] = node.scope_id
        for child in node.children:
            walk(child)

    walk(root)
    if not index:
        raise HierarchyError(f"hierarchy '{path}' produced no scope ids")
    return index


def resolve(names, mg_index):
    """Map MG names to scope ids. Returns ``(scope_ids, unknown_names)`` (order-preserving)."""
    lower = {k.lower(): v for k, v in mg_index.items()}
    scope_ids, unknown = [], []
    for name in names:
        sid = mg_index.get(name) or lower.get(name.lower())
        if sid:
            if sid not in scope_ids:
                scope_ids.append(sid)
        else:
            unknown.append(name)
    return scope_ids, unknown
