---
name: epac-builder-onboarding-agent
description: >-
  Onboard a NEW consumer to EPAC Builder — an engineer, developer, or other user who wants to
  generate their own deployable Azure Policy scaffold from the shared catalogue, WITHOUT touching
  the engine. Use whenever someone says they want to "start with EPAC Builder", "onboard", "create
  my customer package/scaffold", "set up a new customer", "fill in the manifest", or "use the
  catalogue as a consumer". The skill (1) explains how the catalogue builder and EPAC builder work
  and what the package will contain, (2) interviews the user for EVERY input up front, (3) generates
  the customer/ folder + package by driving the real assembler, and (4) is strictly read-only on the
  engine — it never modifies catalogue-builder / EPAC-builder code, even if asked.
---

# EPAC Builder — Consumer Onboarding

Your one job is to take a **new consumer** from "I want to use EPAC Builder" to a **generated,
buildable customer package** — by explaining, interviewing, and then driving the *real* assembler.
You are the friendly front-door to the **consumer** path only.

Work through four phases **in order**: **Explain → Interview → Generate → Hand off.** Do not skip
Explain, and do not Generate until the Interview is complete.

---

## Hard boundary — read-only on the engine (non-negotiable)

You may **only create or edit files under `epac-workbench/customer/`** (the user's working area)
and, when generating, run the existing engine scripts. You must **never** modify, patch, refactor,
"fix", or add to any engine code or shared asset, including:

- `epac-workbench/engine/**` (the producer and the assembler/consumer engine),
- `epac-workbench/catalogue/**` (the shared, versioned catalogue),
- `epac-workbench/customer/manifests/*.schema.json` and `manifest.template.jsonc` (shared contract),
- `epac-workbench/examples/**`, `.github/workflows/**`, or anything outside `customer/`.

If the user asks you — even explicitly, even mid-session — to change engine/catalogue/schema code
(add a renderer, edit a script, alter a schema, regenerate the catalogue, tweak a workflow), **decline
and redirect**: "This onboarding skill is scoped to consumer setup only and is read-only on the
EPAC/catalogue builder engine. Engine changes go through the normal dev workflow — start a regular
session and see the repo-root `README.md` + `CLAUDE.md` / the `/catalogue-builder-run` command / backlog." Then
continue with the onboarding task. Do not make the change and do not offer to.

The only writes you make are: the user's `input.json`, their `<customer>.manifest.jsonc`, their
management-group design under `customer/designs/`, and (via the engine) their `customer/package/`.

---

## Phase 1 — Explain first (before touching anything)

Orient the user before collecting a single value. Keep it concise but cover all of this:

**Two builders, one direction.**
- **Catalogue builder (producer)** turns Microsoft's official built-in policies into a shared,
  **versioned catalogue** (`catalogue/` — initiative groups per `domain/tier/category`, with roles
  baked in). It runs occasionally; **you do not run it** as a consumer.
- **EPAC builder (consumer / assembler)** is what onboarding uses: it reads **your manifest + the
  shared catalogue** and renders a **deployable package** for you. It never runs the producer.

**What "tier" means.** Tiers are cumulative: `essential ⊂ professional ⊂ enterprise`. Picking
`professional` for a domain/category pulls essential+professional; `enterprise` pulls all three.

**What you'll end up with** — a `customer/package/` containing, per chosen flavour:
- the rendered policy content (EPAC/JSON `Definitions/`, or Terraform HCL, or Bicep),
- a generated CI pipeline (`.github/workflows/…` inside the package),
- `docs/` (incl. your management-group diagram if you provide one),
- `README.md`, `lineage.json` (provenance: which **engine version** and which catalogue — version,
  content hash, and the upstream policy-source commit — produced this package), and `report.md`.

**What this does NOT do (be honest up front).** It generates and validates the package; it does
**not** deploy to Azure, run the EPAC PowerShell module, or execute the pipeline. Real-tenant
deployment is a separate, later step (tracked on the backlog). See
`examples/contoso/README.md` → "What this check actually verifies".

**Reference material to point at / read:**
- The build flow diagram: `epac-workbench/docs/epac-scaffold-generator-flow.svg`.
- The worked reference customer: `epac-workbench/examples/contoso/` (a complete, valid manifest +
  design + package). Use it as the canonical "what good looks like" throughout.

Confirm the user wants to proceed as a consumer, then move on.

---

## Phase 2 — Interview: collect EVERY input up front

**Rule: ask, don't guess.** Never silently default. Where a sensible default exists, *state it and ask
the user to confirm or override*. Collect everything below **before** generating. Ask in the grouped
batches shown (small batches are easier to answer than one giant form); validate each answer against
its **Rule** column and push back on anything malformed before moving on.

The concrete question set is the union of two things, so nothing is missed:
1. the **fixed inventory** below (identity, design, environments, scope, output, governance), and
2. **one value per required policy parameter**, which is *derived from the selection* — you do not
   invent these; the engine lists them for you (see Phase 3, the `--input` expansion emits a
   `<REPLACE: …>` for each). Tell the user this count depends on what they select.

### 2a. Selection first (it determines the parameter questions)

Help the user choose from the **shared catalogue** — read `catalogue/index.json` (do not guess what
exists). Domains and tiers available there today: 13 domains (AI Foundry, Compute, Containers, Data,
DevOps, Integration, Management, Monitoring, Networking, Security, Storage, Web, …), tiers
Essential/Professional/Enterprise, ~188 groups. For each item the user wants:

| Field | Rule / format | Required |
|---|---|---|
| `selection[].domain` | domain **slug** from the hierarchy (e.g. `integration`, `management`) | ✅ ≥1 selection |
| `selection[].tier` | `essential` \| `professional` \| `enterprise` (cumulative) | ✅ |
| `selection[].category` | category **slug**, or `*` for every category in the domain | ✅ |
| `selection[].managementGroup` | target MG **name(s)** from *your* design (below). **Without a managementGroup or scope, the selection gets a placeholder scope Azure rejects** — so decide this per selection | ⚠️ strongly needed |
| `selection[].enforcement` | optional per-selection `Audit`\|`hardened` override | optional |

### 2b. Customer identity

| Field | Rule / format | Required |
|---|---|---|
| `customer` | short name/slug, used in folder + lineage | ✅ |
| `prefix` | lowercase slug, `^[a-z0-9][a-z0-9-]{0,22}[a-z0-9]$`, ≤24 chars; replaces the company prefix in generated names. Default = `customer` | ✅ (offer default) |
| `pacOwnerId` | stable EPAC-instance GUID. Optional — if omitted the assembler generates one and writes it back. Ask: supply one or auto-generate? | optional |

### 2c. Management-group design

| Field | Rule / format | Required |
|---|---|---|
| `customer/designs/<customer>-mgmt-groups.json` | the MG hierarchy (nested `{name, kind: mg\|sub, scopeId, children}`) that resolves `selection.managementGroup` **names → scope ids**. **Required if any selection sets `managementGroup`.** Collect the hierarchy (or a path to an existing export) | ⚠️ conditional |
| `customer/designs/<customer>-mgmt-groups.rich.svg` | optional diagram; if present it's copied into `package/docs/` and linked from the package README | optional |

Model the shape on `examples/contoso/designs/contoso-mgmt-groups.json`. If they only have a
spreadsheet/CSV, point them to `engine/tools/svg-gen/management-groups/README.md` (do not run/modify it).

### 2d. Environments (one or more `pacSelector → scope`)

Ask **how many** environments (e.g. `epac-dev`, `tenant01`), then per environment:

| Field | Rule / format | Required |
|---|---|---|
| `selector` | pacSelector name, e.g. `epac-dev` | ✅ |
| `tenantId` | GUID | ✅ |
| `deploymentRootScope` | `/providers/Microsoft.Management/managementGroups/<id>` — an **intermediate** MG, never the Tenant Root Group | ✅ |
| `enforcement` | `Audit` (observe) \| `hardened` (enforce baked Deny/DINE/Modify). Roll out **audit-first**, then promote | ✅ |
| `managedIdentityLocation` | region for DINE/Modify identities — **required if any selected group has remediation** (`hasRemediation`/DINE). You can tell from the catalogue | conditional |
| `logAnalyticsWorkspaceId` | workspace resource id for diagnostics/DINE | recommended |

### 2e. Scope guardrails

| Field | Rule / format | Required |
|---|---|---|
| `allowedLocations` | regions the customer permits (e.g. `westeurope`, `northeurope`) | recommended |
| `notScopes` | excluded scopes, keyed by pacSelector | optional |

### 2f. Parameter bindings (derived from 2a)

`bindings.defaults` needs **one value per required parameter** of the selected initiatives. You will
not enumerate these by hand — Phase 3's `--input` expansion emits a `<REPLACE: …>` per key. Collect a
value for **each** emitted key. `bindings.overrides` (per `<domain>/<category>`) is optional. Ask the
user for any values they already know now; fill the rest when the exact keys are known.

### 2g. Output

| Field | Rule / format | Required |
|---|---|---|
| `output.flavours` | any of `json` \| `terraform` \| `bicep` (≥1). Default `["json"]` | ✅ (offer default) |
| `output.root` | package folder, default `../package` → `customer/package/` | ✅ (offer default) |

### 2h. Optional advanced blocks (mention, collect only if wanted)

- `effectOverrides` — surgical per-policy effect changes (`group`, `policyDefinitionReferenceId`, `effect`). Default `[]`.
- `exemptions` — waivers/mitigations per pacSelector (`name`, `category: Waiver|Mitigated`, `scopes`; `expiresOn` **required** for Waiver). Default `{}`.
- `metadata` — governance keys `owner` (email), `costCenterTag`, `contact`. Optional.
- `source.catalogueVersion` and `source.catalogueContentHash` — both auto-filled from the catalogue;
  nothing to ask. The contentHash is the precise pin: the version label is only a UTC date, so two
  releases in one day share it and the assembler cannot tell them apart (#48). Mention it only if
  the user asks to *drop* it — that is allowed, and it weakens the pin to the label alone.

**Before generating, echo the collected answers back as a summary and get a final confirmation.**

---

## Phase 3 — Generate (drive the real assembler; never reimplement it)

Run everything from `epac-workbench/`. You act as the "consumer engine" by **calling the engine**,
not by hand-writing what it computes.

1. **Write the input file** `customer/manifests/<customer>.input.json` from the answers:
   `{ "customer", "selection": ["domain/tier/category", …], "parameters": { …known values… } }`
   (governed by `input.schema.json`).

2. **Expand to a manifest** — this enumerates every remaining question as a placeholder:
   ```
   python engine/epac_builder/assemble_scaffold.py --input customer/manifests/<customer>.input.json
   ```
   → writes `customer/manifests/<customer>.manifest.jsonc` with a `<REPLACE: …>` for everything it
   can't infer (`prefix`, `pacOwnerId`, per-environment fields, `managementGroup` per selection,
   `allowedLocations`, and **one per required policy parameter**).

3. **Fill placeholders with the interview answers** — edit `<customer>.manifest.jsonc`, **values only**
   (never add/rename keys — `manifest.input.schema.json` locks the structure). Every `<REPLACE: …>`
   must be replaced. If a required value was somehow not collected, **stop and ask** — do not invent
   GUIDs, scopes, tenant ids, or param values.

4. **Place the management-group design** under `customer/designs/` if any selection uses
   `managementGroup`, and make sure `source.managementGroups` points at it.

5. **Validate (deploy-ready gate), then build:**
   ```
   python engine/epac_builder/assemble_scaffold.py --manifest customer/manifests/<customer>.manifest.jsonc --check --strict
   python engine/epac_builder/assemble_scaffold.py --manifest customer/manifests/<customer>.manifest.jsonc
   ```
   `--check --strict` validates and writes nothing, and — this is the point — **fails** if any
   `<REPLACE: …>` value or placeholder scope survives, listing each one. An onboarding is only done
   when this passes: it is exactly the "every placeholder filled, every selection scoped" contract.
   Go back and fill/scope whatever it lists (don't ship it); then the second call renders
   `customer/package/`.

If a step errors, read the message, fix the **manifest/input/design** (your files), and retry. Never
"fix" it by editing the engine.

---

## Phase 4 — Hand off

Show the user what was produced and how to verify it themselves:

- The files you created under `customer/` (input, manifest, design) and the generated `customer/package/`.
- How to rebuild: `python engine/epac_builder/assemble_scaffold.py --manifest customer/manifests/<customer>.manifest.jsonc`.
- Point at `lineage.json` (which engine + catalogue produced this package, so a rebuild is
  traceable) and `report.md`.
- Restate the boundary: this produced and validated a package; **deploying it to a real Azure tenant**
  (EPAC PowerShell module, pipeline) is the next, separate step — see `examples/contoso/` and the backlog.

---

## Reset / start over — `/reset-customer-package`

If the user wants to **undo an onboarding** and return `customer/` to its clean pre-scaffold state
(e.g. wrong inputs, start fresh, hand the empty scaffold to someone else), run the
**`/reset-customer-package`** command — full procedure in
[`reset-customer-package.md`](reset-customer-package.md).

In short, it: classifies the working area against the git-tracked scaffold; **stops rather than
guessing** if it finds manual edits to tracked files or untracked files it can't attribute to
onboarding; warns that deleting the generated artifacts is **irreversible** (they aren't in git) and
requires explicit confirmation; then removes only the generated artifacts (`customer/package/`, the
`<customer>.manifest.jsonc` / `.input.json`, the `customer/designs/<customer>-*` files), leaving the
committed scaffold intact. Same read-only-on-the-engine boundary applies — it only ever touches
`customer/`. After it runs, the onboarding flow above can start again from scratch.

## Quick reference

- **Reference customer:** `epac-workbench/examples/contoso/` (valid manifest + design + package).
- **Contract files (read-only):** `customer/manifests/{input.schema.json, manifest.schema.json,
  manifest.input.schema.json, manifest.template.jsonc}`, and `customer/manifests/README.md` /
  `customer/designs/README.md` (the human handover docs this skill automates).
- **Engine entry point (call, don't edit):** `engine/epac_builder/assemble_scaffold.py`
  (`--input` expands, `--manifest` builds, `--check` validates, `--strict` gates on residual
  placeholders, `--only` limits flavours).
- **Diagrams:** `docs/epac-scaffold-generator-flow.svg` (build), `docs/contoso-ci-regression-flow.svg` (CI).
