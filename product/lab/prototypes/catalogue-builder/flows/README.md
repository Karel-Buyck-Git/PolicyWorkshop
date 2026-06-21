# `flows/` — Catalogue Builder source root

This is the **source root**: a few **named components** (each a Python subpackage), joined by one
contract — the **catalogue**. In one sentence: a *producer* turns Microsoft's built-in Azure
policies into a versioned catalogue, and a *consumer* turns that catalogue + a customer's manifest
into deployable Infrastructure-as-Code.

Each component has its own README with the detail; this page is the map.

## Components

| Component | Dir | What it is |
| --- | --- | --- |
| **catalogue-builder** | [`catalogue_builder/`](catalogue_builder/) | the **producer** pipeline: `extract → enrich → create-initiatives → apply-overlays → quality-control` → the catalogue |
| **epac-builder** | [`epac_builder/`](epac_builder/) | the **consumer / assembler**: manifest + catalogue → IaC scaffolds (EPAC/JSON · Terraform · Bicep) |
| **definition-gen** | [`definition_gen/`](definition_gen/) | on-demand **custom-definition generators** (`dlw-az-naming`, `dlw-az-tagging`, `az-apim`, …) overlaid into the catalogue |
| **shared** | [`shared/`](shared/) | the internal API imported across components (`paths`, `hierarchy`, `tiers`, `naming`, `mdtable`) |
| **tools** | [`tools/`](tools/) | dev / analyst utilities (`ab_verify`, `catalogue_diff`, `summarize_categories`) — not part of the build |

## The two halves, joined by the catalogue

- **Producer** = the *catalogue-builder*. Runs **occasionally** — only when Microsoft's built-ins
  or the taxonomy change. Extracts + dedups policies, classifies each into a tier, groups them into
  EPAC initiatives, and stamps a versioned catalogue. → [`catalogue_builder/`](catalogue_builder/)
- **Consumer** = the *epac-builder*. Runs **per customer, on demand**. Expands a small input into a
  manifest, resolves it against the catalogue, and renders EPAC/JSON + Terraform + Bicep — reading
  the catalogue only, never re-running the producer. → [`epac_builder/`](epac_builder/)

The two never call each other; they meet at the **catalogue contract**: `catalogue/index.json`
(groups + `domainMap`) + `catalogue/catalogue.json` (the version stamp + content hash) +
`initiatives/` + `definitions/`. The end-to-end design is drawn in
[`../docs/epac-scaffold-generator-flow.svg`](../docs/epac-scaffold-generator-flow.svg).

```
PRODUCER — catalogue-builder (catalogue_builder/)   CATALOGUE @version (the contract)
                                                     ┌─────────────────────────────────┐
  Azure built-in policies ┐                          │ catalogue.json  version·hash     │
                          ├─► ① extract ─► ② enrich ─►③ create-initiatives ─►          │
  config/ hierarchy ──────┘     dedup ·      validate    group · bake roles  │ index.json     groups·domainMap │
                                first-pass    tier ·     · stamp version      │ initiatives/<domain>/<tier>/<cat>/ │
                                tier          rationale  ④ apply-overlays     │ definitions/   policies.md + custom │
                                                            (custom + register)│                                  │
                                          ⑤ quality-control (validate + docs) └─────────────────────────────────┘
                                                                                          │
CONSUMER — epac-builder (per customer, on demand)  ◄─────────────────────────────────────┘
  input.json ─► EXPAND ─► manifest ─► Resolve+Bind ─► Canonical IR ─► render {EPAC/JSON · Terraform · Bicep}
                                                                          └─► customer/initiatives/ ─► Validate ─► PR ─► Deploy
```

> **definition-gen** is the **apply-overlays** step (④): it runs the custom-definition generators
> and registers their output into the catalogue — either as new groups (`management-esn-naming`,
> `management-esn-tagging`) or by enriching a built-in group (`apim-tls` → `integration-esn-apim`).
> So the catalogue carries built-in **and** custom assets. See [`definition_gen/`](definition_gen/).

## Authored inputs and shared convention

The producer derives everything from a few hand-authored files in [`../config/`](../config/) — the
domain hierarchy, the tier rules, and the category-abbreviation map — each with exactly one parser
in [`shared/`](shared/). The **naming convention** (`shared/naming.py`) is the one piece shared
across *all* flows, so producer and consumer always agree on names. Which flow reads which input is
documented in [`../config/README.md`](../config/README.md).

## File-naming convention (governance)

Every file here is **`snake_case`** so it is a valid Python module — runnable *and* importable.
The rule is keyed on what a file *is*:

| Kind | Convention | Examples |
| --- | --- | --- |
| Pipeline / entry-point steps | `verb_noun.py` | `extract_policies.py`, `assemble_scaffold.py` |
| Shared library modules | `noun.py` | `paths.py`, `naming.py` |
| Dev / validation tools | `verb_noun.py` | `ab_verify.py`, `catalogue_diff.py` |

1. **No hyphens** — a hyphen makes a file impossible to `import` (Python reads `-` as minus).
2. **No leading underscore** unless the module is genuinely private; shared helpers that siblings
   import are part of the internal API and stay un-prefixed.
3. Conceptual pipeline steps are still written `extract → enrich → …` in prose/diagrams — that's a
   step label, not a filename.
