# Manifests — format & edit rules

The manifest is the assembler's input. **Format: JSONC** (JSON + `//` comments +
trailing commas) — stays in the JSON family/pipeline, matches EPAC's own `.jsonc`,
and keeps the explanatory comments.

## Edit rule (important)

**Change VALUES only.** Do not add, remove, or rename keys; do not introduce new
objects or arrays. Structure is fixed and schema-validated. Fill every
`<REPLACE: ...>` placeholder with a real value.

Enforced by validation, not convention:

| Stage | File | Validated by | Allows |
|---|---|---|---|
| Human input | `input.example.json` | `input.schema.json` | customer + selection strings + value-only `parameters`; **no foreign keys** |
| Editing the manifest | `contoso.manifest.jsonc` | `manifest.input.schema.json` | placeholders OK; **no added/renamed keys** |
| Build gate | filled manifest | `manifest.schema.json` (strict) | real values only — GUIDs, enums, scopes, required params |

## Files

| File | Role |
|---|---|
| `input.example.json` | minimal human input: customer + `domain/tier/category` selections + value-only `parameters` |
| `input.schema.json` | governs the input file (top level closed; selection format; parameters value-only) |
| `contoso.manifest.jsonc` | expanded manifest, fixed shape, placeholder values (edit values here) |
| `manifest.input.schema.json` | structure lock for the manifest (values free) |
| `manifest.schema.json` | strict schema — the build gate |

## `parameters` (input)

`parameters` is a flat map whose **keys are generated from the selection** — one per
required parameter of the selected initiatives. Humans fill values only; values are
scalars or arrays (no objects). It maps to the manifest's `bindings.defaults`. Kept
as an empty object `{}` until the selection is resolved.

## Two-stage flow

```
form (customer + selections)
  -> assembler seeds parameters{} keys from the selection
  -> assembler expands -> contoso.manifest.jsonc (placeholders, structure-locked)
  -> human fills values (value-only edits)
  -> strict schema validates -> build
```
