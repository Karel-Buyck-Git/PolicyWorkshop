# `examples/contoso/` — the worked sample (and CI golden fixture)

The canonical, end-to-end **contoso** example: a filled manifest, its management-group
design, and the deployable package the assembler produces from them. It mirrors the shape of
the empty [`customer/`](../../customer/) scaffold — this is what `customer/` looks like once
filled in and built.

```
manifests/manifest.example.jsonc   # filled, buildable reference manifest
designs/contoso-mgmt-groups.json   # management-group hierarchy (+ .rich.svg diagram)
package/                           # the assembler's json output (committed sample)
fixtures/terraform/                # committed terraform output (regression fixture)
fixtures/bicep/                    # committed bicep output (regression fixture)
```

## Golden fixture

![Contoso CI regression / determinism-check flow](../../docs/contoso-ci-regression-flow.svg)

`verify.sh` rebuilds the sample for **every** renderer flavour and diffs each byte-for-byte
against the committed tree — the epac-builder's determinism contract:

| flavour | committed tree |
|---|---|
| `json` | `package/` (the worked sample a customer sees) |
| `terraform` | `fixtures/terraform/` |
| `bicep` | `fixtures/bicep/` |

CI runs it via `.github/workflows/contoso-epac-build.yml` (the `contoso epac build` check);
the workflow is a thin trigger — the pipeline logic lives here in `verify.sh`. So all three
trees are **generated, not hand-edited**: change the manifest (or the catalogue) and
regenerate, never edit them directly.

Verify locally (from `catalogue-builder/`):

```
bash examples/contoso/verify.sh   # expect: OK — all flavours byte-identical
```

To accept an intended change, rebuild the affected tree in place and commit the diff, e.g.
`--only terraform --out examples/contoso/fixtures/terraform` (json's tree is
`--out examples/contoso/package`).

### What this check actually verifies

It is a **determinism / no-drift guard, not a deployability guard.** It answers one question:
*given the same inputs, does the assembler still produce byte-for-byte the same output?* For
each flavour it re-runs the full assembler path — reads `manifest.example.jsonc`, resolves the
selection against the versioned catalogue artifacts (`catalogue/initiatives/…`), binds
parameters, builds the canonical model, renders — then `diff -rq`s the result against the
committed golden tree.

**It catches** any change in the engine (`flows/**`) *or* the catalogue that alters the
generated output: Definitions / policysets / assignments, the Terraform HCL, the Bicep,
`lineage.json`, `report.md`, the package README, the docs SVG, and the pipeline YAML rendered
*inside* the package.

**It does _not_** (by design):

- touch Azure — no tenant, no `az`, no ARM `what-if`/plan, nothing is deployed;
- run the **EPAC PowerShell module** (`Build-DeploymentPlan` / `Deploy-*`) — it doesn't prove
  the EPAC/json package is *accepted* by the module;
- validate the other flavours (`terraform validate/plan`, `az bicep build`) — only the rendered
  *text* is diffed;
- execute the generated GitHub / Azure DevOps pipeline — that YAML is diffed as a file, never run.

The manifest *is* JSON-schema-validated at build time and the assembler emits warnings (e.g. the
tags placeholder-scope), but a warning does not fail the build. Closing the deployability gap —
contoso deployed against a real tenant, EPAC-module + pipeline verified — is tracked as backlog
**#14** (and the monthly catalogue-upgrade path for deployed packages as **#15**).

Schemas are shared: the assembler validates every manifest — this one included — against the
schemas in `customer/manifests/`.
