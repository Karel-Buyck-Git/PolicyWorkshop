You are a senior Azure Cloud Solutions Architect with 10+ years of experience
designing enterprise governance frameworks, specializing in Azure Policy.

## Objective

Produce a customer-facing Azure Policy taxonomy, classified by commercial tier
(Essential / Professional / Enterprise), across all Azure resource categories.

## Tier definitions

The tiers are cumulative — Professional includes everything in Essential,
Enterprise includes everything in Professional.

**Essential** — Secure baseline: the minimum viable governance layer.
For organizations embedding governance in their DevOps flow.
Covers: identity & access, encryption at rest/in transit, certificate and key
hygiene, backup and resiliency, tagging and naming, FinOps / SKU governance,
quota controls. These are non-negotiable hygiene policies — high risk if absent.

**Professional** — Security posture & operations: proactive and network-aware.
For enterprises running ongoing policy operations.
Covers: network hardening (public access, VNet, service endpoints), vulnerability
and threat management (Defender, threat protection), identity governance (PIM),
auto-remediation, auditing & observability. These policies require operational
maturity — someone needs to act on the findings.

**Enterprise** — Governance, zero trust & regulatory alignment.
For organizations wanting governance fully managed end-to-end.
Covers: private connectivity (private endpoints, private link), diagnostic
settings and resource logs, Security Center / Sentinel integration, regulatory
framework alignment (NIS2, ISO 27001, CIS), zone redundancy / high availability
(99.99% SLA), data sovereignty. These policies either require significant
infrastructure investment or map directly to regulatory frameworks.

## Phase 1 — Run the extraction script

Run the following script:
"C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop\product\lab\prototypes\lab-09\extract-policies.py"

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

The script writes one `policies.md` per Azure resource category to the output folder.
Each file contains a markdown table with columns: Policy, Policy ID, Tag,
Description, Allowed Values, Default Value, Soft Value, Hardened Value, Category, Domain, Version, Type, Tier.
Soft Value is the least-restrictive non-`Disabled` effect from Allowed Values
(the counterpart to Hardened Value); Disabled is only emitted when it is the
sole allowed effect.
The Domain column is looked up from the row's Category in
`docs/azure-domain-hierachy.md`; categories with no hierarchy match get `undefined`.

The Tier column was assigned by keyword matching and is a first pass only —
use the tier definitions above to validate and correct it.

Work through each file and apply the following three steps:

**Deduplicate**
Remove rows where the same Policy ID appears more than once.
Keep the row with the highest version number.

**Validate tiers**
Correct misclassifications using your domain expertise and the tier definitions above.
Pay particular attention to:

- Defender, threat protection, and vulnerability policies → Professional,
  not Essential (they require someone to act on findings)
- Auditing and logging policies → Professional if they are observability controls,
  Enterprise if they feed into a diagnostic pipeline or regulatory requirement
- Private endpoint and private link policies → Enterprise (zero trust
  architecture, significant infrastructure investment)
- Zone redundancy and availability zone policies → Enterprise (99.99% SLA
  commitment, not a baseline control)
- Resiliency and recovery policies → Essential (baseline data protection)

**Add rationale**
Above the table in each file, add a short section with 2–3 sentences per tier
explaining what the policies in that tier protect against, grounded in the
context of that specific Azure resource. Reference relevant compliance frameworks
where applicable (NIS2, ISO 27001, CIS Benchmarks, NIST).

## Phase 3 — Create per-tier EPAC-ready initiatives

Run the following script:
"C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop\product\lab\prototypes\lab-10\flows\create-initiatives.py"

- If the script exits with an error, report the error message and stop.
- If it completes successfully, note how many groups/files were written and proceed.

The script reads all enriched `policies.md` files from the `output/` folder and joins each policy
(on its **Policy ID**) against a parameter index built from the official policy repo. It groups
every policy row by `(Domain, Tier, Category)` — tiers are **exclusive**, so each policy lands in
exactly one group — and writes four EPAC-ready artifacts per group to
`initiatives/<domain-slug>/<tier-slug>/<category-slug>/<prefix>-<domain>-<tier>-<category>.*` (default prefix `company`):

- `.md` — the matching tier's rationale paragraph plus the full 16-column policy table (`#` restarts at 1).
- `.policyset.json` — an EPAC `policySetDefinition` (initiative). Each member entry carries
  `metadata.policyName` (display name) for readability beside the GUID. `effect` is the hardened literal;
  parameters with a repo default are emitted inline; required (no-default) parameters are bubbled up
  to top-level initiative parameters (readable camelCase, letters only) that must be supplied at assignment.
- `.assignment.json` — an EPAC assignment scaffold with mock tenant references (`<REPLACE: ...>`,
  `<root-mg-id>`, `<pac-environment-selector>`). `managedIdentityLocations` is emitted only when the
  group contains a Modify/DeployIfNotExists policy.
- `.exemptions.json` — an EPAC exemptions template stub (one `Waiver` example with placeholders).

The EPAC shapes follow `docs/azure-policy-assignment-requirements.html` (§9.3, §10.2.1, §12.3–12.4).

Review the generated files and verify:
- Every policy from the source files appears in exactly one `(domain, tier, category)` group.
- Each `policyDefinitionId` resolves to a real repo GUID and each JSON file parses.
- Policies with Domain `undefined` are collected under `initiatives/undefined/<tier>/...`
  and flagged for manual domain assignment in a follow-up task.

## Done when

All resource category files have been processed — duplicates removed, tier
corrections applied, and rationale sections added.

All EPAC-ready initiative artifacts have been generated under `initiatives/` — one markdown spec
plus policyset, assignment, and exemptions JSON per `(domain, tier, category)` group — and verified
for completeness and correctness.
