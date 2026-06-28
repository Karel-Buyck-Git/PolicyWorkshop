"""SVG renderers for the scope tree — a minimal and a rich variant.

Both share one visual language (CSS variables with a light/dark ``@media``
override, ``<marker>`` arrowheads, semantic classes) adapted from
``docs/epac-scaffold-generator-flow.svg`` so the output matches the repo's
existing diagram. The two differ only in what each node box shows:

* **minimal** — node name only, depth-shaded boxes.
* **rich**    — kind-coloured boxes (Management Group / Subscription / Resource
  Group) with the Azure scope id as a subtitle, plus a legend.
"""
from __future__ import annotations

from xml.sax.saxutils import escape

from layout import Layout, layout_tree
from model import KIND_LABELS, Node, kinds_present

FONT = "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"

# Shared theme variables (light defaults + dark overrides).
_THEME = (
    "svg{--ink:#1f2328;--sub:#5b6470;--line:#c4cad2;--paper:#ffffff;"
    "--panel:#f3f5f8;--panelLine:#d3d9e0;--acc:#4f46e5;--accLine:#b9bbf3;"
    "--mgBg:#ecedfb;--mgLine:#9d9bf0;--subBg:#e6f5f3;--subLine:#7fcabf;"
    "--rgBg:#fdf0e3;--rgLine:#e9b87e;}"
    "@media (prefers-color-scheme:dark){svg{--ink:#e8ebef;--sub:#a3acb9;"
    "--line:#3a424d;--paper:#0d1117;--panel:#171b21;--panelLine:#2b323b;"
    "--acc:#9b95f5;--accLine:#3d3a66;--mgBg:#23223a;--mgLine:#4a468a;"
    "--subBg:#10302c;--subLine:#2c6a60;--rgBg:#33240f;--rgLine:#6e4f23;}}"
)

# Rough monospace-ish advance for sans text, as a fraction of font-size.
_CHAR_W = 0.56


# --------------------------------------------------------------------------- #
# text helpers
# --------------------------------------------------------------------------- #


def _max_chars(box_w: float, pad: float, font_size: float) -> int:
    return max(1, int((box_w - 2 * pad) / (font_size * _CHAR_W)))


def _fit(text: str, limit: int, *, middle: bool = False) -> str:
    """Truncate to ``limit`` chars with an ellipsis (middle-out for scope ids)."""
    if len(text) <= limit:
        return text
    if limit <= 1:
        return "…"
    if middle:
        head = (limit - 1) // 2
        tail = limit - 1 - head
        return text[:head] + "…" + (text[-tail:] if tail else "")
    return text[: limit - 1] + "…"


# --------------------------------------------------------------------------- #
# shared scaffolding
# --------------------------------------------------------------------------- #


def _open(width: float, height: float, title: str, desc: str, extra_css: str) -> list[str]:
    w, h = round(width), round(height)
    return [
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img"',
        f'     font-family="{FONT}">',
        f"  <title>{escape(title)}</title>",
        f"  <desc>{escape(desc)}</desc>",
        f"  <style>{_THEME}{extra_css}</style>",
        '  <defs>',
        '    <marker id="ah" markerWidth="9" markerHeight="9" refX="7" refY="4.5" '
        'orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="var(--line)"/></marker>',
        '  </defs>',
        f'  <rect x="0" y="0" width="{w}" height="{h}" fill="var(--paper)"/>',
    ]


def _edges_svg(layout: Layout, box_h: float) -> list[str]:
    out = []
    for parent, child in layout.edges:
        py = parent.cy + box_h / 2
        cyt = child.cy - box_h / 2
        mid = (py + cyt) / 2
        out.append(
            f'  <path class="e" d="M{parent.cx:.1f},{py:.1f} V{mid:.1f} '
            f'H{child.cx:.1f} V{cyt:.1f}" marker-end="url(#ah)"/>'
        )
    return out


def _text(x: float, y: float, cls: str, size: float, content: str) -> str:
    return (
        f'  <text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
        f'font-size="{size}">{escape(content)}</text>'
    )


# --------------------------------------------------------------------------- #
# minimal variant
# --------------------------------------------------------------------------- #


def render_minimal(root: Node) -> str:
    box_w, box_h = 150.0, 40.0
    layout = layout_tree(
        root, box_w=box_w, box_h=box_h, x_step=168, y_step=82,
        margin_x=24, margin_y=24, top_pad=34,
    )
    css = (
        ".e{fill:none;stroke:var(--line);stroke-width:1.5;}"
        ".box{stroke:var(--accLine);stroke-width:1.5;}"
        ".t{fill:var(--ink);font-weight:600;}"
        ".band{fill:var(--sub);font-weight:700;letter-spacing:.06em;}"
    )
    parts = _open(
        layout.width, layout.height,
        "Management group hierarchy",
        "A top-down tree of the management-group / scope hierarchy, names only.",
        css,
    )
    parts.append(
        f'  <text class="band" x="24" y="22" font-size="11">MANAGEMENT GROUP HIERARCHY '
        f'· {len(layout.placed)} scopes</text>'
    )
    parts += _edges_svg(layout, box_h)

    char_limit = _max_chars(box_w, 10, 11)
    for p in layout.placed:
        x = p.cx - box_w / 2
        y = p.cy - box_h / 2
        opacity = min(0.06 + p.depth * 0.06, 0.42)
        parts.append(
            f'  <rect class="box" x="{x:.1f}" y="{y:.1f}" width="{box_w}" '
            f'height="{box_h}" rx="8" fill="var(--acc)" fill-opacity="{opacity:.2f}"/>'
        )
        parts.append(_text(p.cx, p.cy + 4, "t", 11, _fit(p.node.name, char_limit)))

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# --------------------------------------------------------------------------- #
# rich variant
# --------------------------------------------------------------------------- #


def render_rich(root: Node) -> str:
    box_w, box_h = 216.0, 54.0
    kinds = kinds_present(root)
    legend_h = 30 if kinds else 0
    layout = layout_tree(
        root, box_w=box_w, box_h=box_h, x_step=236, y_step=104,
        margin_x=24, margin_y=24, top_pad=34 + legend_h,
    )
    css = (
        ".e{fill:none;stroke:var(--line);stroke-width:1.5;}"
        ".node{stroke-width:1.6;}"
        ".k-mg{fill:var(--mgBg);stroke:var(--mgLine);}"
        ".k-sub{fill:var(--subBg);stroke:var(--subLine);}"
        ".k-rg{fill:var(--rgBg);stroke:var(--rgLine);}"
        ".t{fill:var(--ink);font-weight:600;}"
        ".s{fill:var(--sub);}"
        ".pill{fill:var(--mgLine);}"
        ".pilltext{fill:var(--ink);font-weight:600;}"
        ".band{fill:var(--sub);font-weight:700;letter-spacing:.06em;}"
    )
    parts = _open(
        layout.width, layout.height,
        "Management group hierarchy (detailed)",
        "A top-down tree of management groups, subscriptions and resource groups "
        "with their Azure scope ids, colour-coded by scope kind.",
        css,
    )
    parts.append(
        f'  <text class="band" x="24" y="22" font-size="11">AZURE SCOPE HIERARCHY '
        f'· {len(layout.placed)} scopes</text>'
    )

    # legend — one swatch + label per kind present, left to right.
    lx = 24.0
    for kind in kinds:
        parts.append(
            f'  <rect class="node k-{kind}" x="{lx:.1f}" y="32" width="14" '
            f'height="14" rx="3"/>'
        )
        label = KIND_LABELS[kind]
        parts.append(
            f'  <text class="s" x="{lx + 20:.1f}" y="43" font-size="10.5">'
            f'{escape(label)}</text>'
        )
        lx += 20 + len(label) * 6.6 + 22

    parts += _edges_svg(layout, box_h)

    name_limit = _max_chars(box_w, 12, 12)
    id_limit = _max_chars(box_w, 12, 8.5)
    for p in layout.placed:
        x = p.cx - box_w / 2
        y = p.cy - box_h / 2
        parts.append(
            f'  <rect class="node k-{p.node.kind}" x="{x:.1f}" y="{y:.1f}" '
            f'width="{box_w}" height="{box_h}" rx="9"/>'
        )

        # A management group with a subscription count gets a top-right pill;
        # trim its name to leave room so the two never collide.
        subs = p.node.meta.get("subscriptions") if p.node.kind == "mg" else None
        limit = name_limit
        if subs:
            label = f"{subs} subs"
            pill_w = 12 + len(label) * 5.4
            px = x + box_w - pill_w - 7
            parts.append(
                f'  <rect class="pill" x="{px:.1f}" y="{y + 7:.1f}" '
                f'width="{pill_w:.1f}" height="15" rx="7.5"/>'
            )
            parts.append(
                f'  <text class="pilltext" x="{px + pill_w / 2:.1f}" y="{y + 18:.1f}" '
                f'text-anchor="middle" font-size="9">{escape(label)}</text>'
            )
            limit = _max_chars(box_w - pill_w, 12, 12)

        parts.append(_text(p.cx, p.cy - 4, "t", 12, _fit(p.node.name, limit)))
        subtitle = p.node.scope_id or f"({KIND_LABELS[p.node.kind].lower()} — no scope id)"
        parts.append(
            _text(p.cx, p.cy + 13, "s", 8.5, _fit(subtitle, id_limit, middle=bool(p.node.scope_id)))
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


RENDERERS = {"minimal": render_minimal, "rich": render_rich}
