# `examples/contoso/` — the worked sample (and CI golden fixture)

The canonical, end-to-end **contoso** example: a filled manifest, its management-group
design, and the deployable package the assembler produces from them. It mirrors the shape of
the empty [`customer/`](../../customer/) scaffold — this is what `customer/` looks like once
filled in and built.

```
manifests/manifest.example.jsonc   # filled, buildable reference manifest
designs/contoso-mgmt-groups.json   # management-group hierarchy (+ .rich.svg diagram)
package/                           # the assembler's output (committed)
```

## Golden fixture

`.github/workflows/test.yml` rebuilds `package/` from `manifests/manifest.example.jsonc` and
diffs it byte-for-byte against the committed tree — the epac-builder's determinism contract.
So `package/` is **generated, not hand-edited**: change the manifest (or the catalogue) and
regenerate, never edit `package/` directly.

Verify locally (run from `catalogue-builder/`) — build to a temp dir and diff:

```
python flows/epac_builder/assemble_scaffold.py \
  --manifest examples/contoso/manifests/manifest.example.jsonc \
  --out /tmp/contoso-build
diff -rq /tmp/contoso-build examples/contoso/package   # expect: no differences
```

To accept an intended change, rebuild with `--out examples/contoso/package` and commit the diff.

Schemas are shared: the assembler validates every manifest — this one included — against the
schemas in `customer/manifests/`.
