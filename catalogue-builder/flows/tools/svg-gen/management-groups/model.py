"""Canonical scope-tree model shared by the parsers and renderers.

A single ``Node`` type represents every level of an Azure scope hierarchy —
management groups, subscriptions and resource groups — so the three input
formats (indent / edges / json) all produce the same tree and both SVG
variants (minimal / rich) consume it unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# Kinds, ordered shallow -> deep, with the labels used by the rich legend.
KINDS = ("mg", "sub", "rg")
KIND_LABELS = {
    "mg": "Management Group",
    "sub": "Subscription",
    "rg": "Resource Group",
}


@dataclass
class Node:
    """One scope in the hierarchy.

    ``kind`` is one of :data:`KINDS`. ``scope_id`` is the full Azure resource id
    (e.g. ``/providers/Microsoft.Management/managementGroups/contoso``); it is
    optional and only surfaced by the rich variant.
    """

    name: str
    kind: str = "mg"
    scope_id: str | None = None
    children: list["Node"] = field(default_factory=list)
    # Optional extras carried by the tabular importer (e.g. subscription counts,
    # access level). The hand-authored formats leave this empty; the rich
    # renderer surfaces selected keys when present.
    meta: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(
                f"Unknown node kind {self.kind!r} for {self.name!r}; "
                f"expected one of {', '.join(KINDS)}."
            )


def walk(node: Node, depth: int = 0):
    """Yield ``(node, depth)`` pairs in pre-order (root first)."""
    yield node, depth
    for child in node.children:
        yield from walk(child, depth + 1)


def kinds_present(root: Node) -> list[str]:
    """Return the kinds that actually appear in the tree, in :data:`KINDS` order."""
    seen = {n.kind for n, _ in walk(root)}
    return [k for k in KINDS if k in seen]
