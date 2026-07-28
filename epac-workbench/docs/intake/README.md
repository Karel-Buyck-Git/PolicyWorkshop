# `docs/intake/` — tenant intake (backlog #14)

**Plane: maintainer.** Nothing in this folder ships to a customer. Per the #23 delivery
boundary the customer receives only the **rendered package**, and the package carries its
own guides (`docs/azure/README.md`, `docs/github/README.md`, emitted verbatim from
`engine/epac_builder/`). These pages are for the engineer standing a tenant up.

## What this is for

**#14 asks a question no amount of byte-diffing can answer: does the generated package
actually deploy?** Everything CI proves today is that the package is *correct and
reproducible*. Whether Azure accepts it is proven by one thing only — a real
`Build-DeploymentPlans` against a real tenant.

## The tenant

**`dlwaemsp.onmicrosoft.com`** — our own demo / lab / sandbox tenant, CSP-covered, and the
**only** tenant whose identifiers may appear in this public repo (backlog #28; a client
engagement's manifest belongs in that client's private deploy repo).

**It is not free yet.** It is currently hosting another project — a PoC for a managed-service
hosting environment. That is a scheduling constraint, and a technical one:

> 🛑 **EPAC owns its `deploymentRootScope` and everything beneath it.** In a *shared* tenant
> that is not a footnote. Three things are non-negotiable when the run happens:
>
> 1. **A dedicated intermediate management group** created for EPAC — never the Tenant Root
>    Group, and never a branch that contains the PoC's resources.
> 2. **`desiredState.strategy` stays `ownedOnly`** (the package's default). `full` would
>    propose **deleting** policy objects the PoC owns.
> 3. **The PoC's subscriptions / MGs go in `notScopes`**, so they are excluded even by
>    accident.
>
> The first run is plan/what-if only in any case — `epac-deploy-verify.yml` emits no deploy
> step at all. **Read the plan** before anything is allowed near the shared tenant.

So everything that does *not* need the tenant is built and sitting here, ready:

| File | What it does |
|---|---|
| [`tenant-intake.md`](tenant-intake.md) | The fill-in sheet. Every value to collect, the **read-only** `az` command that gets it, and the exact manifest key it feeds. One pass on the tenant, nothing forgotten. |
| [`hierarchy-file.md`](hierarchy-file.md) | How to turn the tenant's management-group tree into the `designs/*.json` file the assembler consumes, and render its diagram. |
| [`oidc-checklist.md`](oidc-checklist.md) | The identities and role assignments CI needs, and the order to create them in. |

The workflow that runs the proof is
[`.github/workflows/epac-deploy-verify.yml`](../../../.github/workflows/epac-deploy-verify.yml) —
`workflow_dispatch` only, secrets-gated, and it **skips cleanly when no secrets exist**, so
it is committed and green today rather than waiting.

## Order of work when clearance lands

1. **Collect** — one session on the tenant with [`tenant-intake.md`](tenant-intake.md) open.
   Read-only; nothing here creates or changes an Azure resource.
2. **Build the hierarchy file** — [`hierarchy-file.md`](hierarchy-file.md), then render the
   SVG so the MG tree can be eyeballed before anything targets it.
3. **Create identities** — [`oidc-checklist.md`](oidc-checklist.md). This is the first step
   that *writes* to the tenant, and it needs the permissions named there.
4. **Fill the manifest and build** — `--strict`, so an unfilled placeholder cannot reach a
   plan run.
5. **Run the workflow** — plan/what-if only. Read the plan before letting anything deploy.

## What "done" means for #14

The row closes on **evidence**, not on this scaffolding: a `Build-DeploymentPlans` run
against a live tenant, its plan output attached, and whatever it rejects written up. If it
rejects nothing, that is the result — say so. If it rejects something, that is a finding of
exactly the kind #20 was (an EPAC shape defect a consumer found before we did), and it gets
a backlog row.

> **A note on expectations.** #20 came from a consumer's real what-if run and turned up two
> deploy-blocking shape defects that every green CI run had missed. Assume this run finds
> something. That is what it is for.
