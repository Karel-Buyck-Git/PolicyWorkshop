"""Dependency-free tidy top-down tree layout.

Leaves are placed left-to-right in fixed-width slots; each parent is centred
over its children; depth sets the row. The result is variant-independent —
callers pass the box/step sizes for the minimal or rich look and get back node
centres plus parent->child edges, ready to render.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from model import Node


@dataclass
class Placed:
    node: Node
    cx: float
    cy: float
    depth: int


@dataclass
class Layout:
    placed: list[Placed]
    edges: list[tuple[Placed, Placed]] = field(default_factory=list)
    width: float = 0.0
    height: float = 0.0


def layout_tree(
    root: Node,
    *,
    box_w: float,
    box_h: float,
    x_step: float,
    y_step: float,
    margin_x: float = 24.0,
    margin_y: float = 24.0,
    top_pad: float = 0.0,
) -> Layout:
    by_id: dict[int, Placed] = {}
    order: list[Placed] = []
    leaf_counter = [0]

    def place(node: Node, depth: int) -> Placed:
        if node.children:
            for child in node.children:
                place(child, depth + 1)
            xs = [by_id[id(c)].cx for c in node.children]
            cx = (min(xs) + max(xs)) / 2
        else:
            cx = margin_x + box_w / 2 + leaf_counter[0] * x_step
            leaf_counter[0] += 1
        cy = top_pad + margin_y + box_h / 2 + depth * y_step
        placed = Placed(node=node, cx=cx, cy=cy, depth=depth)
        by_id[id(node)] = placed
        order.append(placed)
        return placed

    place(root, 0)

    edges = [
        (by_id[id(p.node)], by_id[id(child)])
        for p in order
        for child in p.node.children
    ]

    leaves = max(leaf_counter[0], 1)
    max_depth = max((p.depth for p in order), default=0)
    width = margin_x * 2 + box_w + (leaves - 1) * x_step
    height = top_pad + margin_y * 2 + box_h + max_depth * y_step

    return Layout(placed=order, edges=edges, width=width, height=height)
