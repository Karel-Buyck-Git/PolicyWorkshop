# `definition_gen/` — custom-definition generators

This package authors **custom Azure Policy definitions** — controls that aren't in Microsoft's
built-in set — and overlays them into the catalogue alongside the built-in producer's output, under
a **governed contract** so every generator "fits" the catalogue the same way.

A generator is **declarative**: it authors the policy definition(s) and declares **where** they go
(a `Placement`); the shared [`scaffold.py`](scaffold.py) derives **how** (paths, names, the EPAC
artifact set) from [`../shared/naming.py`](../shared/naming.py), and the producer step
[`apply_overlays.py`](apply_overlays.py) runs every generator and **registers** the result into the
catalogue manifests. Misconfiguration (bad path, colliding name, missing target) fails loudly.

## Generators

| Generator | Script | Family | Placement | Mirrors |
| --- | --- | --- | --- | --- |
| **dlw-az-naming** | `gen_dlw_naming_definitions.py` | `dlw-az-naming` | **NewGroup** `management-esn-naming` | `getResourceName.bicep` (naming) |
| **dlw-az-tagging** | `gen_dlw_tagging_definitions.py` | `dlw-az-tagging` | **NewGroup** `management-esn-tagging` | `getResourceTags.bicep` (mandatory tags) |
| **dlw-az-apim** | `gen_dlw_az_apim_definitions.py` | `dlw-az-apim` | **Enrich** `integration-esn-apim` | ALZ / enterprise-scale `Deny-APIM-TLS` |

Each has a companion manual named after its script (e.g. [`gen_dlw_naming_definitions.md`](gen_dlw_naming_definitions.md)).

## The contract — how a generator fits

A generator exposes one function, `build() -> Overlay`. It declares **what** and **where**; the
scaffold does the rest.

```python
from definition_gen.scaffold import Overlay, NewGroup, Enrich
def build():
    return Overlay(family="dlw-az-tagging",
                   placement=NewGroup("Management", "Essential", "Tagging", "tagging", RATIONALE),
                   definitions=[_definition()], source=SOURCE)
```

**Two placements:**

- **`NewGroup(domain, tier, category, category_abbr, rationale)`** — the definitions get their own
  initiative in a fresh slot. The scaffold writes `policyset/assignment/exemptions/md` under
  `catalogue/initiatives/<domain>/<tier>/<category>/`, names everything via `shared/naming.py`
  (`<domain>-<tier>-<abbr>`, ≤24, brand-neutral), and returns a group record.
- **`Enrich(domain, tier, category)`** — the definitions are added as **members of an existing
  built-in initiative** (e.g. `apim-tls` → `integration-esn-apim`), referenced by
  `policyDefinitionName` with their effect baked.

**What the scaffold guarantees (governance):** names come only from `shared/naming.py`; the derived
folder path matches the declared placement; a `NewGroup` name must not collide with a built-in; an
`Enrich` target must exist. The *policy rule* the definitions enforce is the generator's own.

## How it runs — a producer step

Generators are part of the build, run by [`apply_overlays.py`](apply_overlays.py) **after**
`create_initiatives.py` (so built-in groups + a first `index.json` exist) and **before**
`quality_control.py`:

```
extract → enrich → create-initiatives → apply-overlays → quality-control
```

`apply_overlays.py` runs every generator the registry **`config/definition-gens.md`** lists with
`Enabled = yes` (a config allowlist, not a hard-coded Python list — it imports each module
dynamically), then **registers** the customs into the catalogue contract so they are first-class:

- **NewGroup** overlays are added to `index.json[groups]` with `custom: true`;
- **Enrich** overlays bump the target group's `policyCount` and set `hasCustomMembers: true`;
- `catalogue.json` is re-stamped (`counts`, `contentHash`).

```
python flows/definition_gen/apply_overlays.py          # run all generators + register
python flows/definition_gen/gen_dlw_tagging_definitions.py   # or a single gen (preview)
```

> A single `gen_*` run writes that overlay (and, for Enrich, injects its members) but does **not**
> update the manifests — `apply_overlays.py` owns registration. Enrich previews also require the
> built-in target to already exist.

## QC governance

[`../catalogue_builder/quality_control.py`](../catalogue_builder/quality_control.py) validates the
whole catalogue, overlays included, and **exits non-zero on any error**. Beyond the hard-limit /
brand-neutral / uniqueness checks it enforces, for custom overlays:

- **orphan-custom-definition** — every `definitions/custom/**` def must be a member of some initiative;
- **unregistered-custom-group** — every custom `NewGroup` overlay must be in `index.json`;
- **missing-generator-doc** — every `gen_*.py` must have a companion `gen_*.md`.

## The generators

### dlw-az-naming — NewGroup
One `naming-*` definition per Azure resource type (the policy-side mirror of `getResourceName.bicep`),
bundled into `management-esn-naming`. Full manual: [`gen_dlw_naming_definitions.md`](gen_dlw_naming_definitions.md).

### dlw-az-tagging — NewGroup
Mandatory-tag presence check (mirror of `getResourceTags.bicep`), bundled into `management-esn-tagging`
under a distinct `Tagging` category (so it doesn't collide with the built-in `management-esn-tags`).
Full manual: [`gen_dlw_tagging_definitions.md`](gen_dlw_tagging_definitions.md).

### dlw-az-apim — Enrich
APIM hardening from ALZ / enterprise-scale. `apim-tls` (TLS 1.2, `Deny` default) is added as a member
of the built-in `integration-esn-apim` initiative — its category is owned by the built-in producer,
so it **enriches** rather than creating a parallel group. Full manual:
[`gen_dlw_az_apim_definitions.md`](gen_dlw_az_apim_definitions.md).

## Consuming customs (status)

Custom overlays are now **registered in the catalogue** (`index.json`), marked `custom` /
`hasCustomMembers`. The epac-builder (consumer) **emitting the referenced custom `policyDefinitions`**
into a rendered scaffold is a **fast follow** — until then the markers let the consumer detect and
defer custom content cleanly.

## Adding a new generator

1. Write `flows/definition_gen/gen_<family>_definitions.py`: author the definition dict(s) + a
   `build()` returning an `Overlay` with a `NewGroup` or `Enrich` placement.
2. For `NewGroup`, pick a category code (inline, as dlw-naming does with `naming`); the scaffold
   enforces name/path/limits and non-collision. For `Enrich`, name an existing built-in group.
3. Add a row to [`../../config/definition-gens.md`](../../config/definition-gens.md) with
   `Enabled = yes` (the allowlist `apply_overlays.py` reads). Set it to `no` to keep a generator in
   the repo but skip it.
4. Write the companion `gen_<family>_definitions.md` and add a row to the **Generators** table.
5. Run the producer (`create_initiatives → apply_overlays → quality_control`) and confirm 0 errors.
