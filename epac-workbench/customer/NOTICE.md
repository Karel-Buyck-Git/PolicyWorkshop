# `customer/` — your working area (start here)

This folder is the **empty scaffold** for one customer's EPAC build. It is *yours to fill
in* — nothing here is a finished example. It ships with only:

- `manifests/manifest.template.jsonc` — the empty manifest shape (all `<REPLACE: …>`), plus
  the schemas (`manifest.schema.json`, `manifest.input.schema.json`, `input.schema.json`) and
  `input.example.json`. See `manifests/README.md` for the fill-in workflow.
- `designs/` — drop your management-group design here (see `designs/README.md`).
- `package/` — **not present until you build.** `assemble_scaffold.py` writes it (the
  template's `output.root` resolves to `customer/package/`).

## Committing a real deploy package here

`customer/` starts empty, but a real (non-sample) deploy package **may** be committed here —
this is your working tree. When you do, commit the three artifacts **together** for provenance:
your `<customer>.input.json`, the `<customer>.manifest.jsonc` it expands to, and the rendered
`package/`. None of these are gitignored. The one thing that never belongs in git is EPAC's
plan output — `package/Output/` (written by `Build-DeploymentPlans`) is ignored repo-wide.
The worked **contoso** sample stays in `../examples/contoso/` as the CI golden fixture; a
package committed here is *your* deploy, not that fixture.

### 🛑 Which repo that rule applies in (decided 2026-07-28, backlog #28)

**Commit-for-provenance is a rule about a _private deploy repo_, not about this one.**

A filled manifest is not inert configuration — it carries the **`tenantId`**, the
**`deploymentRootScope`** (root management-group id), the **`logAnalyticsWorkspaceId`** and the
**`pacOwnerId`**. Committing it publishes those.

- **This repo is public.** The only tenant whose identifiers may appear here is
  **`dlwaemsp.onmicrosoft.com`** — our own demo / lab / sandbox tenant, covered under our CSP
  agreement, whose entire purpose is being used like this. That is a deliberate, accepted
  exposure of *our* tenant, not a general licence.
- **A customer engagement never commits here.** If you are building for a client — internal,
  freelance or consulting — the input/manifest/package trio belongs in **that customer's own
  private deploy repo**, which is where the package is delivered anyway (the customer receives
  the rendered package, never this repo). Publishing a client's tenant GUID and root MG id to a
  public repo is not yours to do.

The mechanism is unchanged — all three artifacts stay committable and none are gitignored.
What is scoped is *where*.

## Where the worked sample is

A complete, buildable reference — the **contoso** sample — lives at
[`../examples/contoso/`](../examples/contoso/): a filled `manifests/manifest.example.jsonc`, its
`designs/`, and the resulting `package/`. That sample is also the **CI golden fixture**
(`.github/workflows/contoso-epac-build.yml` → `examples/contoso/verify.sh` rebuilds it for
every flavour and diffs byte-for-byte), so treat it as read-only reference — don't edit it to
fit your customer. Copy its *shape*, build your own here.

Producer vs. consumer: the shared `catalogue/` is produced by the catalogue-builder
(`/catalogue-builder-run`); this `customer/` area is the **consumer** (epac-builder) input.
