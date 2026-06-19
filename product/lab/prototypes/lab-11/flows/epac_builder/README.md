# `epac_builder/` — the EPAC builder app (consumer / assembler)

This package is the **consumer** half of lab-11: the *epac-builder*. It is a standalone,
deterministic transform — **`manifest + catalogue@version → IaC scaffold`**.

It is **not** a step of the producer ([`../catalogue_builder/`](../catalogue_builder/)). The two
halves are joined by one contract: the published **catalogue** (`catalogue/index.json` +
`catalogue/catalogue.json` + `initiatives/` + `definitions/`). The producer runs *occasionally*
(when Microsoft's built-ins or the taxonomy change); the epac-builder runs *per customer, on
demand* and never re-runs the producer.

Full design: [`../../docs/epac-assembler-design.md`](../../docs/epac-assembler-design.md).

## Entry point

```
python flows/epac_builder/assemble_scaffold.py --manifest customer/manifests/<customer>.manifest.jsonc
        # --only json,terraform,bicep   --check (validate, write nothing)   --out <dir>
        # --input <input.json>          (expand an input.json into a manifest, then stop)
```

It **expands** an `input.json` into a manifest (seeding one `<REPLACE: …>` per required
parameter), **validates** (structure lock → strict build gate → resolves/generates
`pacOwnerId`), **resolves + binds** the selection against the catalogue (tier roll-up,
parameter binding, effect posture), builds a flavour-neutral **canonical IR**, and **renders**
EPAC/JSON + Terraform + Bicep into `customer/initiatives/`, plus `lineage.json` + `report.md`.
Roles are already baked by the producer's step ③, so it reads the catalogue only and never
touches the policy repo.

Stays **stdlib-only** (no `jsonschema`/`json5`) to match the producer's zero-dependency house
style. All validation is fail-fast, before any file is written. Output is deterministic — same
manifest + same catalogue ⇒ byte-identical (apart from a generated `pacOwnerId`).

## Modules

| File | Responsibility |
| --- | --- |
| `assemble_scaffold.py` | CLI + orchestration (expand · validate · resolve · bind · IR · render · report). |
| `jsonc.py` | stdlib JSONC reader (strip `//`, `/* */`, trailing commas). |
| `validate.py` | focused JSON Schema 2020-12 subset validator (the keywords the manifest schemas use). |
| `catalogue.py` | catalogue access + selection resolution (tier roll-up, `*` expansion, `undefined` exclusion, empty-expansion hard errors). |
| `expand.py` | `input.json → manifest` (seed `<REPLACE: …>` per required parameter). |
| `bind.py` | parameter binding + type checks; effect posture (Audit-soften / hardened-keep) + surgical `effectOverrides`. |
| `ir.py` | build the canonical IR (re-prefix, scopes, managed identity, role assignments, lineage). |
| `render_json.py` | IR → EPAC `Definitions/` (policySetDefinitions, policyAssignments, global-settings, exemptions). |
| `render_terraform.py` / `hcl.py` | IR → `azurerm` module + per-env tfvars. |
| `render_bicep.py` | IR → MG-scoped `main.bicep` + `loadJsonContent` sidecars + per-env parameter files. |
| `report.py` / `writeutil.py` | `lineage.json` + `report.md`; deterministic writers. |

## Edge cases (confirmed)

- The **`undefined` domain is always excluded** from consumption: a selection naming it is a
  hard error explaining it needs a real domain (producer follow-up); `*` expansion never reaches it.
- A selection resolving to **zero groups** (empty `*` expansion or an unknown category/tier) is a
  **hard error** naming the offending selection and the available categories.
