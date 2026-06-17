# `epac_builder/` — the EPAC builder app (consumer / assembler) ░ to be built ░

This package is the **consumer** half of lab-11: the *epac-builder*. It is a standalone,
deterministic transform — **`manifest + catalogue@version → IaC scaffold`** — and is **not built
yet**. Only the package skeleton + this note exist so the work has a home.

It is **not** a step of the producer ([`../catalogue_builder/`](../catalogue_builder/)). The two
halves are joined by one contract: the published **catalogue** (`catalogue/index.json` +
`catalogue/catalogue.json` + `initiatives/` + `definitions/`). The producer runs *occasionally*
(when Microsoft's built-ins or the taxonomy change); the epac-builder runs *per customer, on
demand* and never re-runs the producer.

Full design: [`../../docs/epac-assembler-design.md`](../../docs/epac-assembler-design.md).

## Planned entry point (reserved name)

```
python flows/epac_builder/assemble_scaffold.py --manifest customer/manifests/<customer>.manifest.jsonc
        # --only json|terraform|bicep   --check (validate, write nothing)   --out <dir>
```

It will: **expand** a tiny `input.json` (customer · selection · parameters) into a manifest
(seeding required params from `index.json`), **resolve + bind** the selection against the
catalogue (tier roll-up, parameter binding, effect posture), build a flavour-neutral **canonical
IR**, and **render** EPAC/JSON + Terraform + Bicep into `customer/initiatives/`, then
validate → PR → deploy. Roles are already baked by the producer's step ③, so it reads the
catalogue only.

When implemented, add `assemble_scaffold.py` here and update
[`../README.md`](../README.md) (the `flows/` index).
