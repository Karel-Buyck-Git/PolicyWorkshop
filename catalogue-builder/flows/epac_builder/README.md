# `epac_builder/` — the EPAC builder app (consumer / assembler)

This package is the **consumer** half of the Catalogue Builder: the *epac-builder*. It is a standalone,
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
        # --strict  (pre-deploy gate: fail if any <REPLACE:>/placeholder scope survives)
        # --input <input.json>          (expand an input.json into a manifest, then stop)
```

It **expands** an `input.json` into a manifest (seeding one `<REPLACE: …>` per required
parameter), **validates** (structure lock → strict build gate → resolves/generates
`pacOwnerId`), **resolves + binds** the selection against the catalogue (tier roll-up,
parameter binding, effect posture), builds a flavour-neutral **canonical IR**, and **renders**
EPAC/JSON + Terraform + Bicep into `customer/package/` as deployable packages (each with a
pipeline + docs + `README.md` + `lineage.json` + `report.md`).
Roles are already baked by the producer's step ③, so it reads the catalogue only and never
touches the policy repo.

Stays **stdlib-only** (no `jsonschema`/`json5`) to match the producer's zero-dependency house
style. All validation is fail-fast, before any file is written. Output is deterministic — same
manifest + same catalogue ⇒ byte-identical (apart from a generated `pacOwnerId`).

**`--strict` (deploy-readiness gate).** Structure validation proves the manifest is *well-formed*,
not *filled in*: free-string fields (a selector, a location, a Log Analytics id, a bound parameter
value, a metadata field) let an unedited `<REPLACE: …>` sail through and render verbatim into the
package, and a selection with no `managementGroup`/`scope` resolves to a placeholder scope (a
`[warn]`, not an error). `--strict` ([`strict.py`](strict.py)) turns the assembler into a
pre-deploy gate that fails the build listing every such residual placeholder. It honours `--check`
(validate-only), so `--check --strict` is the "is this manifest deploy-ready?" query. Off by
default, so partial scaffolds still build while authoring.

## At a glance

| File | Stage | Responsibility |
| --- | --- | --- |
| [`assemble_scaffold.py`](assemble_scaffold.py) | entry point | CLI + orchestration (expand · validate · resolve · bind · IR · render · report). |
| [`jsonc.py`](jsonc.py) | foundation | stdlib JSONC reader (strips `//`, `/* */`, trailing commas). |
| [`validate.py`](validate.py) | foundation | focused JSON Schema 2020-12 subset validator (the keywords the manifest schemas use). |
| [`strict.py`](strict.py) | foundation | `--strict` deploy-readiness gate: fails on any residual `<REPLACE:>` / placeholder scope. |
| [`writeutil.py`](writeutil.py) | foundation | deterministic JSON/text writers (stable order, trailing newline). |
| [`expand.py`](expand.py) | stage 1 | `input.json → manifest` (seed one `<REPLACE: …>` per required parameter). |
| [`catalogue.py`](catalogue.py) | stage 2 | catalogue access + selection resolution (tier roll-up, `*` expansion, `undefined` exclusion). |
| [`bind.py`](bind.py) | stage 3 | parameter binding + type checks; effect posture (Audit-soften / hardened-keep) + surgical `effectOverrides`. |
| [`ir.py`](ir.py) | stage 4 | build the flavour-neutral **canonical IR**. |
| [`render_json.py`](render_json.py) | stage 5 | IR → EPAC `Definitions/` (policySetDefinitions, policyAssignments, global-settings, exemptions). |
| [`render_terraform.py`](render_terraform.py) + [`hcl.py`](hcl.py) | stage 5 | IR → `azurerm` module + per-env tfvars (`hcl.py` is the HCL literal emitter). |
| [`render_bicep.py`](render_bicep.py) | stage 5 | IR → MG-scoped `main.bicep` + `loadJsonContent` sidecars + per-env parameter files. |
| [`report.py`](report.py) | stage 6 | `lineage.json` (provenance) + `report.md` (coverage). |

## How the modules fit (pipeline order)

`assemble_scaffold.py` is the only entry point; everything else is a pure function it calls in
order. Validation is **fail-fast** — every stage raises before any file is written.

**Foundation (no catalogue knowledge).** [`jsonc.py`](jsonc.py) parses the JSONC manifest
(comments + trailing commas, string-aware) with no `json5` dependency.
[`validate.py`](validate.py) hand-rolls the slice of JSON Schema the three manifest schemas use
(`type`, `required`, `additionalProperties`, `enum`, `pattern`, `if/then`, …) and reports *all*
violations at once. [`writeutil.py`](writeutil.py) is the shared deterministic writer so re-runs
diff cleanly.

**Stage 1 — expand** ([`expand.py`](expand.py)). Turns the tiny human `input.json` (customer +
`domain/tier/category` selection + value-only parameters) into the structured manifest, seeding a
`<REPLACE: …>` placeholder for every required parameter the selected initiatives expose. Humans
then fill values only.

**Stage 2 — resolve** ([`catalogue.py`](catalogue.py)). Loads the published `index.json` and the
`initiatives/` artifacts (never `config/` — the catalogue is self-describing). Resolves each
selection to groups: cumulative tier roll-up (`professional` pulls essential+professional),
`category:"*"` expansion, **`undefined` excluded**, and a hard error on any selection that
resolves to zero groups.

**Stage 3 — bind + posture** ([`bind.py`](bind.py)). Fills each group's `<REPLACE: …>` parameters
from `bindings.defaults`/`overrides`, type-checks against the policyset schema, and applies the
effect posture — `hardened` keeps the baked effects, `Audit` softens every member to `Audit` —
plus surgical per-policy `effectOverrides`.

**Stage 4 — IR** ([`ir.py`](ir.py)). Assembles the one flavour-neutral model all renderers
consume: customer-prefixes the policy-**set** name (`contoso-integration-esn-apim`), keeps the
brand-neutral **assignment** name as-is (≤24, no prefix), resolves scopes/notScopes per
environment, marks managed-identity + role assignments for remediating groups, regenerates a clean
assignment description, and records lineage (manifest hash + group map).

**Stage 5 — render** (`render_json` · `render_terraform`+`hcl` · `render_bicep`). Each renderer is
a pure `IR → files` function, so adding a flavour is one new module. Names are identical across all
three (they come from the IR), which is what keeps the flavours consistent.

**Stage 6 — report** ([`report.py`](report.py)). Writes `lineage.json` and a `report.md` coverage
summary at the output root.

## Edge cases (confirmed)

- The **`undefined` domain is always excluded** from consumption: a selection naming it is a
  hard error explaining it needs a real domain (producer follow-up); `*` expansion never reaches it.
- A selection resolving to **zero groups** (empty `*` expansion or an unknown category/tier) is a
  **hard error** naming the offending selection and the available categories.
