You design Azure governance offerings built on Enterprise Policy as Code (EPAC).

## Objective

Produce an Azure Policy taxonomy classified into three commercial tiers (Essential / Professional / Enterprise),covering all major Azure resource categories (compute, networking, storage,
data, identity, monitoring, etc).

Phases 1–3 are the **producer**: they **produce the catalogue that the assembler consumes** (see `docs/assembler-design.md`).

## Tier definitions

The tiers are cumulative — Professional includes everything in Essential,
Enterprise includes everything in Professional.

**Essential** — Secure baseline: the minimum viable governance layer.
For organizations embedding governance in their DevOps flow.
Covers: identity & access, encryption at rest/in transit, certificate and key
hygiene, local backup / soft-delete / recovery, tagging and naming, FinOps / SKU
governance, quota controls. These are non-negotiable hygiene policies — high risk if absent.

**Professional** — Security posture & operations: proactive and network-aware.
For enterprises running ongoing policy operations.
Covers: network hardening (public access, VNet, service endpoints, firewall),
private connectivity (private endpoints, private link, private DNS zones),
vulnerability and threat management (Defender, threat protection), privileged and
external identity governance (PIM, guest/external accounts), auto-remediation.
These policies require operational maturity — someone needs to act on the findings.

**Enterprise** — Governance, zero trust & regulatory alignment.
For organizations wanting governance fully managed end-to-end.
Covers: the diagnostic pipeline (diagnostic settings, resource logs, Log Analytics,
Sentinel) and auditing / observability, customer-managed keys, zone and geo
redundancy / high availability (99.99% SLA), confidential compute, regulatory
framework alignment (NIS2, ISO 27001, CIS, NIST), data sovereignty. These policies
either require significant infrastructure investment or map directly to regulatory frameworks.

## Phase 1 — Run the extraction script

Run the following script:
"C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop\product\lab\prototypes\lab-11\flows\catalogue_builder\extract_policies.py"

- If the script exits with an error, report the error message and stop.
- If it completes successfully, note the output folder it reports and proceed to Phase 2.

**Authorized source folder.** This workshop reads policy definitions exclusively
from the official built-in policy set at
`C:\GIT\Official Azure Policy\azure-policy\built-in-policies\policyDefinitions`
(the default value of `--source`). The script accepts a `--source` override for
local development convenience, but no allowlist is enforced — pointing it at
any other folder is outside the scope of this workshop and the resulting
output should not be treated as a valid lab artifact. Always run with the
default `--source` unless you have an explicit, documented reason to deviate.

## Phase 2 — Enrich the output

The script writes one `policies.md` per Azure resource category to the `catalogue/definitions/` folder.
Each file contains a markdown table with columns: Policy, Policy ID, Tag,
Description, Allowed Values, Default Value, Soft Value, Hardened Value, Category, Domain, Version, Type, Tier.
Soft Value is the least-restrictive non-`Disabled` effect from Allowed Values
(the counterpart to Hardened Value); Disabled is only emitted when it is the
sole allowed effect.
The Domain column is looked up from the row's Category in
`config/azure-domain-hierachy.md` (the ONE authored hierarchy, parsed via the shared
`flows/shared/hierarchy.py`); categories with no hierarchy match get `undefined`.

The Tier column is assigned by the shared classification engine
(`flows/shared/tiers.py`) from the authored keyword rules in `config/tier-rules.yaml`;
duplicate Policy IDs were already removed in Phase 1. Run `flows/catalogue_builder/enrich_policies.py`,
which for every `policies.md` re-applies the tier rules and adds the rationale.

**Re-apply tiers**
The engine assigns exactly one tier per policy (priority Enterprise > Professional

> Essential; see `config/README.md`). The notable placements the rules encode:

- Defender, threat protection, vulnerability → Professional
- Network hardening and private connectivity (private endpoint / link / DNS zone) → Professional
- Auditing / observability and the diagnostic pipeline (diagnostic settings,
  resource logs, Log Analytics, Sentinel) → Enterprise
- Zone and geo redundancy / availability zones → Enterprise (99.99% SLA)
- Customer-managed keys, confidential compute, regulatory frameworks → Enterprise
- Encryption, identity, key/cert hygiene, local backup & recovery, tagging → Essential

To change the tiering, edit `config/tier-rules.yaml` (no code change) and re-run.

**Add rationale**
Above the table in each file, add a short section with 2–3 sentences per tier
explaining what the policies in that tier protect against, grounded in the
context of that specific Azure resource. Reference relevant compliance frameworks
where applicable (NIS2, ISO 27001, CIS Benchmarks, NIST).

## Phase 3 — Create per-tier EPAC-ready initiatives

Run the following script:
"C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop\product\lab\prototypes\lab-11\flows\catalogue_builder\create_initiatives.py"

- If the script exits with an error, report the error message and stop.
- If it completes successfully, note how many groups/files were written and proceed.

The script reads all enriched `policies.md` files from the `catalogue/definitions/` folder and joins each policy
(on its **Policy ID**) against a parameter index built from the official policy repo. It groups
every policy row by `(Domain, Tier, Category)` — tiers are **exclusive**, so each policy lands in
exactly one group — and writes up to five EPAC-ready artifacts per group to
`catalogue/initiatives/<domain-slug>/<tier-slug>/<category-slug>/<domain>-<tier>-<categoryAbbr>.*` (brand-neutral names built by `flows/shared/naming.py`, within Azure hard limits — assignment names ≤24 chars; category abbreviations from `config/azure-category-abbreviation.md`):

- `.md` — the matching tier's rationale paragraph plus the full 16-column policy table (`#` restarts at 1).
- `.policyset.json` — an EPAC `policySetDefinition` (initiative). Each member entry carries
  `metadata.policyName` (display name) for readability beside the GUID. `effect` is the hardened literal;
  parameters with a repo default are emitted inline; required (no-default) parameters are bubbled up
  to top-level initiative parameters (readable camelCase, letters only) that must be supplied at assignment.
  The policyset `metadata` also carries `catalogueVersion`, `hasRemediation`, and (when remediating)
  `roleDefinitionIds` baked from the policy repo.
- `.assignment.json` — an EPAC assignment scaffold with mock tenant references (`<REPLACE: ...>`,
  `<root-mg-id>`, `<pac-environment-selector>`). `managedIdentityLocations` is emitted only when the
  group contains a Modify/DeployIfNotExists policy.
- `.exemptions.json` — an EPAC exemptions template stub (one `Waiver` example with placeholders).
- `.roles.json` — written **only** for groups with a Modify/DeployIfNotExists member: the deduped
  remediation `roleDefinitionIds` (and per-policy map), so the Terraform/Bicep renderers never need
  the policy repo downstream.

The parameter-index join also reads each policy's `roleDefinitionIds` from the repo (for the baking
above). A version label is set with `--version` (default: today's UTC date).

Finally, two catalogue manifests are written at the catalogue root:

- `catalogue/index.json` — the group list + `domainMap` (category → domain) + tiers, stamped with `catalogueVersion`.
- `catalogue/catalogue.json` — the version stamp: `catalogueVersion`, `generatedAt`, `inputs`
  (built-ins git ref, hierarchy hash, tier-rules hash), `counts`, `tools`, and a `contentHash`
  fingerprint. At this point the `contentHash` is **`sha256:pending`** — Phase 4 (apply-overlays)
  writes the authoritative fingerprint over the whole catalogue (built-in + custom).

The EPAC shapes follow `docs/azure-policy-assignment-requirements.html` (§9.3, §10.2.1, §12.3–12.4).

Review the generated files and verify:

- Every policy from the source files appears in exactly one `(domain, tier, category)` group.
- Each `policyDefinitionId` resolves to a real repo GUID and each JSON file parses.
- Policies with Domain `undefined` are collected under `catalogue/initiatives/undefined/<tier>/...`
  and flagged for manual domain assignment in a follow-up task.

> **Provisional stamp.** Phase 3 writes `catalogue.json` with `contentHash: "sha256:pending"`. The
> catalogue is **not finalized** until **Phase 4 (apply-overlays)** stamps the authoritative
> `contentHash` over the whole catalogue. Running Phase 5 on a `pending` catalogue fails with
> `catalogue-not-finalized`.

## Phase 4 — Apply custom overlays

Run the following script:
"C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop\product\lab\prototypes\lab-11\flows\definition_gen\apply_overlays.py"

- If the script exits with an error, report the error message and stop.
- If it completes successfully, note the summary line (new groups / enriched / catalogue groups).

This is the **custom-overlay** step of the producer. It reads the authored allowlist
[`config/definition-gens.md`](../config/definition-gens.md) — only generators with **Enabled = yes**
run — and applies each via the shared scaffold (`flows/definition_gen/scaffold.py`). Each generator
declares a **placement**:

- **NewGroup** — the custom definitions get their own initiative in a fresh `(domain, tier, category)`
  slot (e.g. `management-esn-naming`, `management-esn-tagging`).
- **Enrich** — the custom definitions are added as **members of an existing built-in initiative**
  (e.g. `apim-tls` → `integration-esn-apim`).

It then **registers** the customs into the catalogue contract — NewGroup overlays are added to
`index.json` (`custom: true`); Enrich bumps the target group's `policyCount` and sets
`hasCustomMembers: true` — and writes the **authoritative** `catalogue.json` stamp (the real
`contentHash` over built-in + custom, plus `inputs.definitionGensHash` and `tools.applyOverlays`).
The custom definitions live under `catalogue/definitions/custom/<family>/`; the policy *rule* each
generator enforces is its own — see [`flows/definition_gen/README.md`](../flows/definition_gen/README.md).

To build a **built-in-only** catalogue, set every row in `config/definition-gens.md` to
`Enabled = no`; apply-overlays then applies nothing but still finalizes the stamp.

## Phase 5 — Quality control output (producer step ⑤)

Run the following script:
"C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop\product\lab\prototypes\lab-11\flows\catalogue_builder\quality_control.py"

- If the script exits with an error, report the error message and stop.
- If it completes successfully, note the summary line it prints (counts + findings).

> **Scope note.** This QC step is the **fifth and final step of the *producer*** — it validates and
> documents the catalogue the first four steps built (built-in + custom overlays).
> It is *not* the "assembler". The **epac-builder** (consumer / assembler) is a separate,
> not-yet-built app that consumes the published catalogue; see
> [`flows/epac_builder/README.md`](../flows/epac_builder/README.md).

This is the repeatable QC gate run at the **end of every catalogue-builder run**. It reads the
freshly generated catalogue (custom definitions under `catalogue/definitions/custom/`, the
built-in `policies.md` tables, and the `initiatives/**/*.policyset.json` + `*.assignment.json`
artifacts), runs a validation pass, and regenerates three outputs:

- `catalogue/naming-samples.md` — naming-result samples plus the live `name` ↔ `displayName`
  pair tables (custom definitions, built-ins, initiatives, assignments, initiative members).
- `docs/epac-naming-convention.md` — the explanatory naming / identifiers guide, with the same
  live pair tables.
- `catalogue/quality-control.json` — a machine-readable report: `catalogueVersion`,
  `generatedAt`, `counts`, and the `findings` list.

The validation pass flags: missing `displayName`, duplicate technical names, empty initiatives,
orphan assignments, members without a `metadata.policyName`, the **Azure hard limits** (assignment
name ≤24, definition/set/exemption ≤64, displayName ≤128, description ≤512 — see
`docs/epac-arm-hard-limits.md`), a **brand-neutral** guard, the **custom-overlay governance**
(orphan custom definitions, unregistered custom groups, a companion `.md` per generator), and the
**finalize gate** (`catalogue-not-finalized` if Phase 4 didn't stamp the catalogue). The script
**exits non-zero when any `error`-level finding is present** — treat that as a stop condition and resolve the
findings before the run is considered complete. The two markdown files are generated artifacts
(a banner says so); edit the templates in `flows/catalogue_builder/quality_control.py`, not the files. Output is
deterministic — re-running on an unchanged catalogue is byte-identical apart from `generatedAt`.
Use `--check-only` to run the validation/report without rewriting the docs.

## Done when

All resource category files have been processed — duplicates removed, tier
corrections applied, and rationale sections added.

All EPAC-ready initiative artifacts have been generated under `catalogue/initiatives/` — one markdown spec
plus policyset, assignment, exemptions (and a `.roles.json` for remediating groups) per
`(domain, tier, category)` group — and verified for completeness and correctness.

The custom overlays have been applied (Phase 4): the generators enabled in
`config/definition-gens.md` have run, their custom definitions/initiatives are registered in
`catalogue/index.json` (`custom` / `hasCustomMembers`), and `catalogue/catalogue.json` carries the
**authoritative** `contentHash` (no longer `pending`).

The catalogue manifests `catalogue/index.json` and `catalogue/catalogue.json` have been written and
carry the `catalogueVersion` stamp.

The quality-control step has run: `catalogue/naming-samples.md` and `docs/epac-naming-convention.md`
have been regenerated from the catalogue, `catalogue/quality-control.json` has been written, and the
validation report shows **no `error`-level findings**.
