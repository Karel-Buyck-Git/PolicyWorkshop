# Manifests — the assembler's customer input

This folder holds one customer's input to the **assembler** — the catalogue _consumer_
that turns a manifest + the shared `catalogue/` into a deployable `Definitions` scaffold
(EPAC/JSON, Terraform, Bicep). The assembler does **not** run the taxonomy pipeline
(phases 1–5); it only reads a published catalogue. See `docs/assembler-design.md`.

**Format: JSONC** (JSON + `//` comments + trailing commas) — stays in the JSON pipeline,
matches EPAC's own `.jsonc`, and keeps the explanatory comments.

## Edit rule (important)

**Change VALUES only.** Do not add, remove, or rename keys; do not introduce new objects
or arrays. Structure is fixed and schema-validated. Fill every `<REPLACE: ...>` placeholder
with a real value.

Enforced by validation, not convention:

| Stage                | File                     | Validated by                    | Allows                                                                      |
| -------------------- | ------------------------ | ------------------------------- | --------------------------------------------------------------------------- |
| Human input          | `input.example.json`        | `input.schema.json`             | customer + selection strings + value-only `parameters`; **no foreign keys** |
| Editing the manifest | `<customer>.manifest.jsonc` | `manifest.input.schema.json`    | placeholders OK; **no added/renamed keys**                                  |
| Build gate           | filled manifest             | `manifest.schema.json` (strict) | real values only — GUIDs, enums, scopes, required params                    |

## Files

| File                         | Role                                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------------- |
| `input.example.json`         | minimal human input: customer + `domain/tier/category` selections + value-only `parameters` |
| `input.schema.json`          | governs the input file (top level closed; selection format; parameters value-only)          |
| `manifest.template.jsonc`    | the empty manifest shape, fixed structure, all `<REPLACE: …>` placeholders + edit-rule comments |
| `manifest.input.schema.json` | structure lock for the manifest (values free)                                               |
| `manifest.schema.json`       | strict schema — the build gate                                                              |

> A real run writes `<customer>.manifest.jsonc` (e.g. `contoso.manifest.jsonc`). It is **not
> gitignored** — if you commit a real deploy package under `customer/`, commit its manifest
> too (with its `input.json` and rendered `package/`) for provenance; see `../NOTICE.md`.
> Scratch `--check` experiments just show as untracked — don't `git add` ones you won't keep.
> `manifest.template.jsonc` is the committed starting point; it is not overwritten by a run.
>
> **Worked example:** a filled, buildable reference manifest lives at
> `examples/contoso/manifests/manifest.example.jsonc` (it produces `examples/contoso/package/`).
> This `customer/` folder is *your* empty working area — see `customer/NOTICE.md`.

## How it points at the catalogue (and where output goes)

Paths in the manifest are resolved **relative to the manifest file**:

| Manifest key              | Value                         | Resolves to                                                              |
| ------------------------- | ----------------------------- | ------------------------------------------------------------------------ |
| `source.initiatives`      | `../../catalogue/initiatives` | the shared catalogue (read)                                              |
| `source.catalogueVersion` | e.g. `2026.06.10`             | pins the catalogue snapshot used (must match `catalogue/catalogue.json`) |
| `source.catalogueContentHash` | e.g. `sha256:c06199a7…`   | the **precise** pin — the exact catalogue bytes. Seeded for you; see below |
| `output.root`             | `../package`                  | `customer/package/` — the deployable package (write)                     |

The assembler reads `catalogue/index.json` to validate the selection and expand
`category:"*"`, and reads each group's baked `roleDefinitionIds` (policyset metadata +
`.roles.json`) for Terraform/Bicep remediation — so a customer build needs **only the
catalogue**, no policy repo and no `config/`/`docs/` files.

**Why there are two pins.** `catalogueVersion` is a human label and only a UTC *date*, so two
catalogue releases in the same day share it — and the assembler's version check is an exact
string compare, which cannot tell those two apart. `catalogueContentHash` is the exact
fingerprint of the catalogue bytes, so it can. Both are filled in for you when the manifest is
generated, and the build fails on either mismatch. You may delete the `catalogueContentHash`
line to pin by label alone; nothing forces you to keep it, but you lose the guarantee that the
package you rebuild tomorrow is the package you built today.

## `parameters` (input)

`parameters` is a flat map whose **keys are generated from the selection** — one per
required parameter of the selected initiatives (read from each group's `.assignment.json`).
Humans fill values only; values are scalars or arrays (no objects). It maps to the
manifest's `bindings.defaults`. Kept as an empty object `{}` until the selection is resolved.

## End-to-end flow

```
catalogue@version  (produced occasionally by phases 1–5)
        │  (read)
form (customer + selections)            -> input.example.json
  -> assembler seeds parameters{} keys from the selection (via catalogue/index.json)
  -> assembler expands -> <customer>.manifest.jsonc (placeholders, structure-locked, committable)
  -> human fills values (value-only edits)
  -> strict schema validates + catalogueVersion & catalogueContentHash verified
  -> render + package -> customer/package/ (flat if one flavour, else {epac,terraform,bicep}/)
       each a deployable package: content + .github/workflows + docs/ + README + lineage.json + report.md
```

## Handover — how a new user creates a manifest

There is **one** scaffold producer (`engine/epac_builder/assemble_scaffold.py --manifest …`); the
`--input` mode only generates a manifest and stops. So the path is:

1. Copy `input.example.json`, set `customer` + `selection` (the `domain/tier/category` strings) and
   any `parameters` values you already know. *(`input.schema.json` validates it.)*
2. `python engine/epac_builder/assemble_scaffold.py --input customer/manifests/<your>.input.json`
   → writes `<customer>.manifest.jsonc` with a `<REPLACE: …>` for everything it can't infer
   (`pacOwnerId`, `tenantId`, `deploymentRootScope`, `managedIdentityLocation`, `enforcement`,
   `logAnalyticsWorkspaceId`, per-selection `managementGroup`, and one per required policy param).
3. Fill those values. Compare against `examples/contoso/manifests/manifest.example.jsonc` for a complete, valid reference.
4. Check you filled everything: `python engine/epac_builder/assemble_scaffold.py --manifest customer/manifests/<customer>.manifest.jsonc --check --strict`
   → **fails** and lists any `<REPLACE: …>` value or unscoped selection still left; writes nothing. Fix what it names.
5. `python engine/epac_builder/assemble_scaffold.py --manifest customer/manifests/<customer>.manifest.jsonc`
   → renders the scaffold into `customer/package/`.

You hand a new user `input.example.json` + the schemas + this README — not a raw manifest.
