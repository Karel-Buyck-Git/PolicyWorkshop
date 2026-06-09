# lab-11 Pipeline — Azure Policy Taxonomy → EPAC Initiatives

A three-phase agentic pipeline that turns the official Azure built-in policy
definitions into a commercial, tier-classified taxonomy and emits EPAC-ready
deployment artifacts. Each phase is a standalone Python script in [`flows/`](../flows).

## Flow

```
                          ┌──────────────────────────────────────────────┐
                          │   SOURCE OF TRUTH (parameter schema)          │
                          │   C:\GIT\Official Azure Policy\...\            │
                          │   policyDefinitions\*.json   (5009 files)     │
                          └───────────────┬──────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        │                                  │                                 │
        ▼                                  │                                 │
┌─────────────────────┐                   │                                 │
│  PHASE 1 — EXTRACT   │                   │                                 │
│  extract-policies.py │                   │                                 │
├─────────────────────┤                   │                                 │
│ • read 5009 JSON     │                   │                                 │
│ • skip deprecated    │                   │                                 │
│ • dedup by Policy ID │   uses           │                                 │
│   (keep highest ver) │   docs\azure-domain-hierachy.md  (Category→Domain) │
│ • first-pass Tier    │                   │                                 │
│   (keyword classify) │                   │                                 │
│ 4455 → 3242 policies │                   │                                 │
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
│   enrich-policies.py     │                                                 │
├─────────────────────────┤                                                 │
│ • re-validate Tier with  │     ← 1676 tier corrections                     │
│   refined rules          │                                                 │
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
│   create-initiatives.py                        │   joins on Policy ID     │
├──────────────────────────────────────────────┤◀─────────────────────────┘
│ • build param index from the repo              │   (param values + schema)
│ • parse table + rationale                      │
│ • group rows by (Domain, Tier, Category)       │   tiers EXCLUSIVE
│   → 194 groups                                 │
│ • emit 4 artifacts per group                   │
└──────────────────────────┬───────────────────┘
                           ▼
    catalogue/initiatives/<domain>/<tier>/<category>/company-<domain>-<tier>-<category>.*
    ┌─────────────────────────────────────────────────────────────┐
    │  .md              table + tier rationale (human spec)        │
    │  .policyset.json  EPAC initiative — effect=hardened,         │
    │                   defaults inline, required params bubbled   │
    │  .assignment.json EPAC scaffold — mock <REPLACE…> refs,      │
    │                   managedIdentity only if Modify/DINE        │
    │  .exemptions.json EPAC Waiver stub                           │
    └─────────────────────────────────────────────────────────────┘
              194 groups × 4  =  776 files
```

## Two sources, joined on Policy ID

| Concern                                                      | Source of truth                             |
| ------------------------------------------------------------ | ------------------------------------------- |
| Taxonomy — which **tier / domain / category**, the rationale | the enriched `catalogue/definitions/*.md` (Phase 2)        |
| Parameters — schema, defaults, allowed values, resource ID   | the official Azure policy repo (`--source`) |

Phase 3 joins the two on **Policy ID**: the markdown decides _what belongs where_, the
repo supplies _the deployable parameter values_.

## What each phase produces

| Stage               | In → Out                                                               |
| ------------------- | ---------------------------------------------------------------------- |
| **Phase 1** extract | 5009 JSON → 4455 active → **3242** deduped → 94 category `policies.md` |
| **Phase 2** enrich  | 3242 rows, **1676** re-tiered, `## Tier rationale` added in place      |
| **Phase 3** build   | 3242 rows → **194** (domain × tier × category) groups → **776** files  |

## Tiers (exclusive)

Each policy lands in exactly one tier. The cumulative commercial story
(Professional ⊇ Essential, Enterprise ⊇ Professional) is carried in the rationale text,
not by duplicating policies across files.

| Tier             | Theme                                                                            |
| ---------------- | -------------------------------------------------------------------------------- |
| **Essential**    | Secure baseline — identity, encryption, key hygiene, backup, tagging             |
| **Professional** | Security posture & ops — network hardening, Defender, auditing, remediation      |
| **Enterprise**   | Zero trust & regulatory — private link, diagnostics, zone redundancy, frameworks |

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

Defaults derive from each script's location, so the whole pipeline targets this lab with no arguments:

```
python flows/extract-policies.py     # Phase 1 → catalogue/definitions/
python flows/enrich-policies.py      # Phase 2 → catalogue/definitions/ (in place)
python flows/create-initiatives.py   # Phase 3 → catalogue/initiatives/
```

Overridable flags: `--source` (policy repo), `--out` / `--output`, `--hierarchy`,
`--initiatives`, `--prefix` (default `company`).
