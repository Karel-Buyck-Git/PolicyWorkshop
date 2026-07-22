# `shared/` — libraries imported across the Catalogue Builder flows

These are the **internal API** of the Catalogue Builder: small, single-responsibility modules that other
packages import so a rule has exactly one implementation and no second copy can drift. They are
**imported, not run**. Imports are absolute from the `engine/` root (`from shared.paths import …`);
each entry-point script puts that root on `sys.path` with a two-line bootstrap.

Each module is the **one** parser/source for its concern — change it once and every flow agrees.

## At a glance

| Module | The one source of… | Imported by |
| --- | --- | --- |
| [`paths.py`](paths.py) | every project filesystem path | all flows |
| [`hierarchy.py`](hierarchy.py) | the domain → category taxonomy | catalogue-builder |
| [`tiers.py`](tiers.py) | the Essential/Professional/Enterprise classification | catalogue-builder |
| [`naming.py`](naming.py) | the brand-neutral, within-limit naming convention | catalogue-builder · definition-gen · epac-builder |
| [`mdtable.py`](mdtable.py) | markdown-table parse/escape + `slugify` | catalogue-builder · tools |

## The modules

### [`paths.py`](paths.py)
Single source of truth for project paths (`CATALOGUE_DIR`, `DEFINITIONS_DIR`, `INITIATIVES_DIR`,
`HIERARCHY_FILE`, `TIER_RULES_FILE`, `CATEGORY_ABBREV_FILE`, the `customer/` manifest + schema
paths, …), all derived from this module's own location (`shared/` → `engine/` → project root). Every
script imports these constants, so a folder rename is a one-line change here.

### [`hierarchy.py`](hierarchy.py)
The **one** parser for the authored domain hierarchy
([`../../config/azure-domain-hierachy.md`](../../config/azure-domain-hierachy.md)). Exposes
`load_domain_map()` (`{category: domain}`) and `load_hierarchy()` (`{domain: [categories]}`). One
authored hierarchy → one parser → one generated `index.json`; no second copy means no drift.

### [`tiers.py`](tiers.py)
The **one** tier-classification engine. Parses the authored
[`../../config/tier-rules.yaml`](../../config/tier-rules.yaml) with a small built-in YAML-subset
parser (no PyYAML dependency) and exposes `classify(name, description, category=None)`. Both
`extract_policies.py` and `enrich_policies.py` import it, so the tiering rules have a single
authored source. The YAML uses plain keyword phrases (space = whitespace, hyphen = space-or-hyphen,
trailing `*` = stem, `…` = arbitrary gap) — see the comments at the top of the file.

### [`naming.py`](naming.py)
The **one** EPAC-asset naming convention, shared by the producer **and** the consumer so a customer
deploys exactly the names QC validated. Brand-neutral and sized to the Azure hard limits: builds
the canonical `name(domain, tier, category)` = `<domain>-<tier>-<abbr>` (≤24), the readable
`display_name` (`<Domain> <Tier> — <Category>`), `exemption_name`, `node_name`, the tier codes
(`esn`/`pro`/`ent`), and the limit constants (`ASSIGNMENT_NAME_MAX`, `DEFINITION_NAME_MAX`, …).
Category abbreviations are read from the authored
[`../../config/azure-category-abbreviation.md`](../../config/azure-category-abbreviation.md). See
[`../../config/README.md`](../../config/README.md) for which flow reads which input.

### [`mdtable.py`](mdtable.py)
Shared markdown-table helpers for the catalogue `policies.md` tables: `parse_table`
(header-discovering row parser), `split_cells` / `md_escape` (pipe-safe round-trip), and
`slugify`. Extracted from `create_initiatives.py` so `quality_control.py`, `summarize_categories.py`
and `naming.py` reuse one implementation instead of importing a producer step.

## Convention

`snake_case`, `noun.py`, no leading underscore — these are part of the internal API, not private
implementation details. (This is why `_paths.py` became `paths.py`: it is the same kind of module
as `hierarchy.py`.) See [`../README.md`](../README.md) for the folder-wide naming rules.
