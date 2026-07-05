# `customer/` — your working area (start here)

This folder is the **empty scaffold** for one customer's EPAC build. It is *yours to fill
in* — nothing here is a finished example. It ships with only:

- `manifests/manifest.template.jsonc` — the empty manifest shape (all `<REPLACE: …>`), plus
  the schemas (`manifest.schema.json`, `manifest.input.schema.json`, `input.schema.json`) and
  `input.example.json`. See `manifests/README.md` for the fill-in workflow.
- `designs/` — drop your management-group design here (see `designs/README.md`).
- `package/` — **not present until you build.** `assemble_scaffold.py` writes it (the
  template's `output.root` resolves to `customer/package/`).

## Where the worked sample is

A complete, buildable reference — the **contoso** sample — lives at
[`../examples/contoso/`](../examples/contoso/): a filled `manifests/manifest.example.jsonc`, its
`designs/`, and the resulting `package/`. That sample is also the **CI golden fixture**
(`.github/workflows/test.yml` rebuilds it and diffs byte-for-byte), so treat it as read-only
reference — don't edit it to fit your customer. Copy its *shape*, build your own here.

Producer vs. consumer: the shared `catalogue/` is produced by the catalogue-builder
(`/catalogue-builder-run`); this `customer/` area is the **consumer** (epac-builder) input.
