# `definition_gen/` — custom-definition generators

This package is the home for **on-demand generators of custom Azure Policy definitions** —
controls that aren't in Microsoft's built-in set. Each generator authors a family of definitions
(and usually one initiative that bundles them) and **overlays** them into the catalogue alongside
the built-in producer's output.

It is **not** part of the built-in producer chain ([`../catalogue_builder/`](../catalogue_builder/)).
Generators run *on demand* — typically when the source convention they mirror changes — and are
each self-contained: one script, one output family.

## Generators

| Generator | Script | Output family | Mirrors | Status |
| --- | --- | --- | --- | --- |
| **dlw-az-naming** | `gen_dlw_naming_definitions.py` | `definitions/custom/dlw-az-naming/` + the `management-esn-naming` initiative | `getResourceName.bicep` (naming convention) | ✅ built — see [`gen_dlw_naming_definitions.md`](gen_dlw_naming_definitions.md) |
| **dlw-az-tagging** | `gen_dlw_tagging_definitions.py` | `definitions/custom/dlw-az-tagging/` + the `management-esn-tagging` initiative | `getResourceTags.bicep` (mandatory tags) | ✅ built — see [`gen_dlw_tagging_definitions.md`](gen_dlw_tagging_definitions.md) |
| **az-apim** | `gen_az_apim.py` | `definitions/custom/az-apim/` (definitions only) | ALZ / enterprise-scale `Deny-APIM-TLS` | ✅ built — see [`gen_az_apim.md`](gen_az_apim.md) |

## How a generator fits (the shared contract)

Every generator follows the same pattern, so adding one is low-friction and the output stays
consistent with the built-in catalogue:

1. **Owns one family folder.** Writes its definitions to
   `catalogue/definitions/custom/<family>/` (e.g. `dlw-az-naming`, `dlw-az-tagging`); existing
   files in that folder are overwritten on each run (full regenerate).
2. **Bundles into one initiative** at a chosen `(domain, tier, category)`, written to
   `catalogue/initiatives/<domain>/<tier>/<category>/`, using the **same EPAC artifact set**
   (`.policyset/.assignment/.exemptions/.md`) the built-in producer emits per group.
3. **Borrows the naming convention** from [`../shared/naming.py`](../shared/naming.py): the EPAC
   *asset* names come out brand-neutral and within the Azure hard limits (`<domain>-<tier>-<abbr>`,
   `<Domain> <Tier> — <Category>`), identical in shape to the built-in flow. The *policy rule* the
   definitions enforce is the generator's own and is unrelated to `config/`.
4. **Must pass QC.** [`../catalogue_builder/quality_control.py`](../catalogue_builder/quality_control.py)
   validates the *whole* catalogue, overlays included — hard limits, brand-neutral, unique names.
   Build names via `shared/naming.py` and this is free; a name clash or over-limit name fails the
   gate loudly.
5. **Not in `index.json`.** The built-in producer owns the catalogue manifests, so an overlay is
   present in the tree but not selectable by the consumer — it deploys alongside, not via a
   customer manifest selection.

> There is no orchestrator that runs every generator; each `gen_*` script is run by hand on demand.

## The generators

### dlw-az-naming  ✅
Generates one `naming-*` definition per Azure resource type that audits/denies resources whose
names don't follow the DLW landing-zone convention (the policy-side mirror of
`getResourceName.bicep`), plus the `management-esn-naming` initiative that bundles them. Full
manual — the convention, special cases, check kinds, parameters, deployment — in
[`gen_dlw_naming_definitions.md`](gen_dlw_naming_definitions.md).

```
python flows/definition_gen/gen_dlw_naming_definitions.py
```

### dlw-az-tagging  ✅
The tagging counterpart: audits/denies resources missing the organisation's **mandatory tags**
(`environment`, `costCenter`, `workload`, `owner`, `creationDate`, `service`; `description`
optional) — validating tag *presence* only, with values supplied by the deploying Bicep. It is the
policy-side mirror of `getResourceTags.bicep`, landing as `Audit` (brownfield discovery) then
flipped to `Deny` (greenfield enforcement). It writes one definition
(`tagging-require-mandatory-tags`) and the `management-esn-tagging` initiative (placed under a
distinct `Tagging` category so it does not collide with the built-in `management-esn-tags` group).
Full manual: [`gen_dlw_tagging_definitions.md`](gen_dlw_tagging_definitions.md).

```
python flows/definition_gen/gen_dlw_tagging_definitions.py
```

> Reconstructed from the single surviving artifact in the pre-py-package run, using
> `gen_dlw_naming_definitions.py` as the structural template; the regenerated definition's
> `policyRule` / `parameters` / `mandatoryTags` match the original byte-for-byte (only the
> description was shortened to fit Azure's 512-char limit).

### az-apim  ✅
Custom **API Management hardening** definitions derived from the **Azure Landing Zones /
enterprise-scale** policy set (via azadvertizer). First control: `apim-tls` — APIM services should
use **TLS 1.2** (denies/audits services with TLS 1.0/1.1 enabled in `customProperties`), adapted
from upstream `Deny-APIM-TLS` with its **`Deny`** default preserved. Full manual:
[`gen_az_apim.md`](gen_az_apim.md).

```
python flows/definition_gen/gen_az_apim.py
```

> **Definitions only — no initiative.** Its category (`API Management`) is owned by the built-in
> producer (`integration-esn-apim`), so a bundling overlay initiative would collide; add one under
> a distinct category if the family grows. The generator is **expandable** — add a builder to
> `DEFINITIONS` and it is picked up. The ALZ source's ARM-escaped `[[…]` expressions are
> un-escaped to the standalone `[…]` form.

## Adding a new generator

1. Copy the shape of an existing generator: own family folder + own rule logic/data. A
   **definition-only** generator (like `az-apim`) stops here — write the defs and you're done.
2. *(If it also bundles an initiative)* build the asset names via `shared/naming.py` and pick a
   **unique** `(domain, tier, category)` — supply a category code inline (as dlw-az-naming does
   with `naming`) or add a row to
   [`../../config/azure-category-abbreviation.md`](../../config/azure-category-abbreviation.md).
   It must not collide with a built-in group; QC enforces uniqueness.
3. Run it, then run `quality_control.py` and confirm 0 errors.
4. Add a row to the **Generators** table above and a per-generator doc named after the script
   (like [`gen_dlw_naming_definitions.md`](gen_dlw_naming_definitions.md)).
