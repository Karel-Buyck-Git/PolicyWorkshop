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

Schemas are shared: the assembler validates every manifest — this one included — against the
schemas in `customer/manifests/`.
