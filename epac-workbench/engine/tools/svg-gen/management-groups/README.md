# `svg-gen/management-groups` — management-group hierarchy → SVG

A generator that turns an Azure **management-group / scope hierarchy** into theme-aware
SVG diagrams. The MG hierarchy isn't part of the catalogue data model (a manifest only
carries a single `deploymentRootScope` plus `notScopes`), so this tool builds the diagram
from a tree you describe (by hand or from a real tenant inventory export).

It is a **dev/engineer-facing backend ("edge") function**, used manually from the repo for
now — it is **self-contained**: it imports nothing outside this folder, reads inputs you point
it at, and writes into its own `output/` folder by default. (Where it eventually plugs into a
front-end app is not decided yet.)

Pure Python, **stdlib only** — no dependencies to install.

## Quick start — the workflow

1. **Pick a template** from [`template/`](template/) (e.g. `input-mgmt-groups.xlsx`).
2. **Copy it into [`input/`](input/) and rename it** to whatever you want the output called,
   e.g. `contoso-mgmt-groups.xlsx`.
3. **Fill it in** with your hierarchy (Excel; the top row is the frozen header).
4. **Run with no arguments** — every file in `input/` is picked up and rendered to `output/`,
   named after the input file:

```bash
# from the catalogue-builder root
python engine/tools/svg-gen/management-groups/generate_svg.py
```

For an input named `contoso-mgmt-groups.xlsx` this writes (override the folder with `--out-dir`):

| File | Variant | Shows |
| --- | --- | --- |
| `output/contoso-mgmt-groups.minimal.svg` | minimal | node names only, depth-shaded boxes |
| `output/contoso-mgmt-groups.rich.svg`    | rich    | scope ids, subscriptions, resource groups, colour-coded by kind + legend |

**Folders:** [`template/`](template/) — fill-in starting points (tracked); [`samples/`](samples/) —
worked examples of the hand-authored formats (tracked); **`input/`** — your working source files
(git-ignored); **`output/`** — generated SVGs (git-ignored).

### Targeting one file

```
python engine/tools/svg-gen/management-groups/generate_svg.py \
    [--input <path>] [--format auto|indent|edges|json|csv|xlsx] \
    [--variant both|minimal|rich] [--out-dir <dir>]
```

`--input` renders just that file (otherwise the whole `input/` folder is scanned). `--format
auto` (default) detects the format from the file extension/content; `--variant both` (default)
emits both SVGs. Output files are always named `<input-name>.<variant>.svg`.

## Four input formats

Pick whichever is handiest — they all parse to the same `Node` tree and feed the same
renderers. The three hand-authored formats (indent / edges / json) are interchangeable
and produce identical SVGs for the same hierarchy; the tabular format (csv / xlsx) is
for ingesting a real tenant inventory export. Working examples live in
[`samples/`](samples/).

**1. Indented text** — indentation is depth; one node per line.
`[kind:]Name [| scopeId]`. `kind` defaults to `mg`; use `sub:` / `rg:`.

```
Contoso | /providers/Microsoft.Management/managementGroups/contoso
  mg:Platform
    sub:Connectivity | /subscriptions/1111...-111111111111
      rg:rg-hub-network | /subscriptions/1111.../resourceGroups/rg-hub-network
  mg:Sandbox | /providers/Microsoft.Management/managementGroups/contoso-sandbox
```

**2. Edges** — `Parent -> Child` lines (chains allowed). Optional attribute lines
`Name | kind | scopeId` enrich a node.

```
Contoso -> Platform -> Connectivity -> rg-hub-network
Contoso -> Sandbox
Connectivity | sub | /subscriptions/1111...-111111111111
rg-hub-network | rg | /subscriptions/1111.../resourceGroups/rg-hub-network
```

**3. JSON** — the canonical model directly; the natural choice when you already have
full scope ids / subscriptions / resource groups:

```json
{ "name": "Contoso", "kind": "mg",
  "scopeId": "/providers/Microsoft.Management/managementGroups/contoso",
  "children": [ { "name": "Platform", "kind": "mg", "children": [] } ] }
```

Node `kind` is one of `mg` (management group), `sub` (subscription), `rg` (resource
group). Blank lines and `#` comments are ignored in the two text formats. Each input
must have a **single root** — give a forest a shared root.

**4. Tabular inventory** (`.csv` / `.xlsx`) — a real management-group export, the natural
template when you already have a tenant inventory. Columns are matched by header name
(case-insensitive; extra/missing columns tolerated). See
[`template/input-mgmt-groups.xlsx`](template/input-mgmt-groups.xlsx) for the fill-in
template, and [`samples/`](samples/) for worked hierarchy examples.

| Column | Used for |
| --- | --- |
| `Display Name` | node name |
| `Type` | kind — `Management group`→mg, `Subscription`→sub, `Resource group`→rg |
| `ID` | synthesises the Azure `scope_id` (an MG name / subscription GUID, or a full `/...` id as-is) |
| `In Scope` | **import filter** — `Yes` is imported, anything else is skipped entirely |
| `Parent` | tree structure (always a management group, whose name is unique) |
| `Full Path` | fallback structure (`A,B,C` ancestor chain) if a `Parent` was filtered out |
| `Total Subscription Count` | shown as a pill on management-group boxes in the rich variant |

Both `.csv` and `.xlsx` are read with the **standard library only** (`csv`; `zipfile` +
`xml.etree` for xlsx) — no dependencies. `In Scope = No` rows are dropped at import, so a
node whose parent was excluded reattaches to its nearest in-scope ancestor.

> **Heads-up on scale:** the tabular format draws *every* in-scope node, so a tenant with
> 100+ subscriptions yields a very wide diagram (the bundled 102-node export renders ~17k px
> wide). That's intended; SVG pans/zooms fine in a browser.

## Embedding it elsewhere (optional)

The tool is self-contained, but the same code is importable, so any caller (a future
front-end app, an epac_builder step, a script) can emit the SVGs and choose its own
destination — `generate()` takes the `out_dir` explicitly, so nothing is hard-wired:

```python
import sys
from pathlib import Path

TOOL = Path("engine/tools/svg-gen/management-groups")
sys.path.insert(0, str(TOOL))
from generate_svg import load_tree, generate  # noqa: E402

source = Path("some/inventory.xlsx")
# stem controls the output filenames: <stem>.minimal.svg / <stem>.rich.svg
generate(load_tree(source), out_dir=Path("wherever/you/want"), variant="both", stem=source.stem)
```

Nothing in the pipeline calls this today — where it plugs in is left open on purpose.

## Files

| Path | Role |
| --- | --- |
| `generate_svg.py` | CLI entry + reusable `load_tree()` / `generate()` API |
| `parsers.py` | the hand-authored parsers (indent / edges / json) → canonical tree |
| `tabular.py` | the csv / xlsx inventory reader → canonical tree |
| `model.py` | `Node` dataclass + tree helpers |
| `layout.py` | dependency-free tidy top-down tree layout |
| `render.py` | shared SVG style + minimal & rich renderers |
| `template/` | fill-in starting points to copy into `input/` (tracked) |
| `samples/` | worked examples of the hand-authored formats — indent / edges / json (tracked) |
| `input/` | your working source files; scanned when `--input` is omitted (git-ignored) |
| `output/` | generated SVGs, named `<input-name>.<variant>.svg` (git-ignored) |
