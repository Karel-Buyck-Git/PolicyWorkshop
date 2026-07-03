# Catalogue Builder Pipeline — Azure Policy Taxonomy → EPAC Initiatives

A three-phase agentic pipeline that turns the official Azure built-in policy
definitions into a commercial, tier-classified taxonomy and emits EPAC-ready
deployment artifacts. Each phase is a standalone Python script in [`flows/`](../flows).

## Flow

```
                          ┌──────────────────────────────────────────────┐
                          │   SOURCE OF TRUTH (parameter schema)          │
                          │   $AZURE_POLICY_REPO  (or --source)           │
                          │   ...\policyDefinitions\*.json   (~5009 files)│
                          └───────────────┬──────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        │                                  │                                 │
        ▼                                  │                                 │
┌─────────────────────┐                   │                                 │
│  PHASE 1 — EXTRACT   │                   │                                 │
│  extract_policies.py │                   │                                 │
├─────────────────────┤                   │                                 │
│ • read 5009 JSON     │                   │                                 │
│ • skip deprecated    │                   │                                 │
│ • dedup by Policy ID │   uses           │                                 │
│   (keep highest ver) │   docs\azure-domain-hierachy.md  (Category→Domain) │
│ • first-pass Tier    │                   │                                 │
│   (keyword classify) │                   │                                 │
│ 4455 → 3284 policies │                   │                                 │
└──────────┬──────────┘                    │                                 │
           ▼                               │                                 │
   ┌───────────────────────┐               │                                 │
   │ catalogue/definitions/<category>/     │  94 files    │                                 │
   │ policies.md            │◀─────────────┘                                 │
   │ (16-col table)         │                                                │
   └──────────┬────────────┘                                                 │
              ▼                                                              │
┌─────────────────────────┐                                                 │
│   PHASE 2 — ENRICH       │                                                 │
│   enrich_policies.py     │                                                 │
├─────────────────────────┤                                                 │
│ • re-validate Tier with  │     ← rules: tier-rules.yaml                    │
│   shared engine          │                                                 │
│ • derive Domain          │                                                 │
│ • add "## Tier rationale"│                                                 │
│ • sort by (tier, name)   │                                                 │
└──────────┬──────────────┘                                                 │
           ▼                                                                 │
   ┌────────────────────────┐                                               │
   │ catalogue/definitions/<category>/      │  enriched in place                           │
   │ policies.md             │   = TAXONOMY SOURCE OF TRUTH                  │
   │ (tier + rationale)      │                                               │
   └──────────┬─────────────┘                                               │
              │                                                             │
              ▼                                                             │
┌──────────────────────────────────────────────┐                          │
│   PHASE 3 — CREATE INITIATIVES                 │                          │
│   create_initiatives.py                        │   joins on Policy ID     │
├──────────────────────────────────────────────┤◀─────────────────────────┘
│ • build param index from the repo              │   (param values + schema)
│ • parse table + rationale                      │
│ • group rows by (Domain, Tier, Category)       │   tiers EXCLUSIVE
│   → 189 groups                                 │
│ • emit 4 artifacts per group                   │
└──────────────────────────┬───────────────────┘
                           ▼
    catalogue/initiatives/<domain>/<tier>/<category>/<domain>-<tier>-<categoryAbbr>.*  (brand-neutral, ≤24)
    ┌─────────────────────────────────────────────────────────────┐
    │  .md              table + tier rationale (human spec)        │
    │  .policyset.json  EPAC initiative — effect=hardened,         │
    │                   defaults inline, required params bubbled   │
    │  .assignment.json EPAC scaffold — mock <REPLACE…> refs,      │
    │                   managedIdentity only if Modify/DINE        │
    │  .exemptions.json EPAC Waiver stub                           │
    └─────────────────────────────────────────────────────────────┘
              189 groups  →  870 files  (≈4–5 each)
```

## Two sources, joined on Policy ID

| Concern                                                      | Source of truth                             |
| ------------------------------------------------------------ | ------------------------------------------- |
| Taxonomy — which **tier / domain / category**, the rationale | the enriched `catalogue/definitions/*.md` (Phase 2)        |
| Parameters — schema, defaults, allowed values, resource ID   | the official Azure policy repo (`$AZURE_POLICY_REPO` / `--source`) |

Phase 3 joins the two on **Policy ID**: the markdown decides _what belongs where_, the
repo supplies _the deployable parameter values_.

## What each phase produces

| Stage               | In → Out                                                                  |
| ------------------- | ------------------------------------------------------------------------- |
| **Phase 1** extract | 5009 JSON → active → deduped → **3284** rows in **95** category `policies.md` |
| **Phase 2** enrich  | 3284 rows, Tier re-applied (same engine as Phase 1 ⇒ ~0 changes), `## Tier rationale` added in place |
| **Phase 3** build   | 3284 rows → **189** (domain × tier × category) groups → **870** files      |

## Tiers (exclusive)

Each policy lands in exactly one tier. The cumulative commercial story
(Professional ⊇ Essential, Enterprise ⊇ Professional) is carried in the rationale text,
not by duplicating policies across files.

| Tier             | Theme                                                                              |
| ---------------- | ---------------------------------------------------------------------------------- |
| **Essential**    | Secure baseline — identity, encryption, key hygiene, backup, tagging               |
| **Professional** | Security posture & ops — network hardening, Defender, private connectivity, remediation |
| **Enterprise**   | Zero trust & regulatory — diagnostics & auditing, CMK, zone/geo redundancy, frameworks |

The exact keyword rules behind these themes are authored in
[`config/tier-rules.yaml`](../config/tier-rules.yaml) and applied by the shared
engine [`flows/shared/tiers.py`](../flows/shared/tiers.py); see
[`config/README.md`](../config/README.md) for the rules, overrides, and the
priority order. Both Phase 1 and Phase 2 call the same engine, so they always
agree.

## Phase 3 EPAC artifacts (per group)

- **`.md`** — the 16-column policy table plus the matching tier's rationale paragraph (human-readable spec).
- **`.policyset.json`** — an EPAC `policySetDefinition` (initiative): `effect` set to the hardened
  literal, parameters with a repo default emitted inline, required (no-default) parameters bubbled
  up to top-level initiative parameters. Each member entry carries `metadata.policyName` (the display
  name, for readability next to the GUID), and bubbled parameters use readable camelCase names derived
  from the policy + parameter (e.g. `certificatesMaximumValidityPeriodMaximumValidityInMonths`).
- **`.assignment.json`** — an EPAC assignment scaffold: `<REPLACE: …>` mocks for required params,
  `<root-mg-id>` / `<pac-environment-selector>` placeholders, and `managedIdentityLocations`
  **only** when the group contains a Modify / DeployIfNotExists policy.
- **`.exemptions.json`** — an EPAC `Waiver` exemption template stub.

EPAC shapes follow [`docs/azure-policy-assignment-requirements.html`](./azure-policy-assignment-requirements.html)
(§9.3 initiative assignment, §10.2.1 exemptions, §12.3–12.4 assignment scaffolds).

### How the effect is set

For a policy that exposes an `effect` **parameter**, the member entry bakes the **hardened**
(most-restrictive) allowed effect as a fixed literal — e.g. `"effect": { "value": "Deny" }`.

Roughly a quarter of built-in policies have **no `effect` parameter** — the effect is hardcoded
in the policy's own `policyRule.then.effect` (typically `DeployIfNotExists` / `Modify` / `Append`).
For these the member entry carries **no `parameters.effect` by design**: EPAC cannot override an
effect the policy does not parameterize. The effect still appears in the `.md` table (read from the
rule); it is simply not settable in the initiative.

## Running it (flag-free)

Defaults derive from each script's location, so the whole pipeline targets this project with no
arguments — **except** the external official policy repo. Rather than have everyone point at a
different local clone (which would make catalogues non-reproducible), fetch the **pinned** version
once; the producer then finds it automatically:

```
python flows/tools/fetch_policy_source.py               # materialise the pinned source (config/policy-source.json)
python flows/catalogue_builder/extract_policies.py     # Phase 1 → catalogue/definitions/
python flows/catalogue_builder/enrich_policies.py      # Phase 2 → catalogue/definitions/ (in place)
python flows/catalogue_builder/create_initiatives.py   # Phase 3 → catalogue/initiatives/
python flows/catalogue_builder/quality_control.py      # Phase 4 → validate + regenerate docs
```

The fetch populates a gitignored `.policy-source/` cache pinned to the commit in
[`config/policy-source.json`](../config/policy-source.json); `fetch_policy_source.py --check` reports
when upstream `master` has moved past the pin. To build against your own clone instead, set the
`AZURE_POLICY_REPO` env var or pass `--source` — both override the pinned cache.

Overridable flags: `--source` (policy repo; default: the pinned `.policy-source/` cache, or
`$AZURE_POLICY_REPO`), `--out` / `--output`, `--hierarchy`, `--initiatives`, `--prefix` (default `company`).
