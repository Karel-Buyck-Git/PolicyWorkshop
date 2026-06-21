# Source Map — what to fetch for which CAF question

This skill is live-fetch: before stating a CAF-specific fact, fetch the matching page, read it, then answer and cite it. CAF is reorganized periodically, so prefer the live page over memory. All paths are under `https://learn.microsoft.com/azure/cloud-adoption-framework/`.

## Tier 1 — Ready (landing zones & design areas)

| Question | Fetch |
|---|---|
| Ready methodology overview | `.../ready/` |
| Landing-zone design areas + reference architecture | `.../ready/landing-zone/design-areas` |
| Management groups / subscription design | `.../ready/landing-zone/design-area/resource-org` |
| Identity & access | `.../ready/landing-zone/design-area/identity-access` |
| Network topology & connectivity | `.../ready/landing-zone/design-area/network-topology-and-connectivity` |
| Governance design area | `.../ready/landing-zone/design-area/governance` |
| Management design area | `.../ready/landing-zone/design-area/management` |
| Security design area | `.../ready/landing-zone/design-area/security` |
| Platform automation & DevOps | `.../ready/landing-zone/design-area/platform-automation-devops` |
| Implementation options (portal/Bicep/Terraform) | `.../ready/landing-zone/implementation-options` |
| ALZ policy baseline | `https://aka.ms/alz/policies` |

## Tier 2 — Govern

| Question | Fetch |
|---|---|
| Govern overview / build the team | `.../govern/` |
| Build a cloud governance team (+ RACI) | `.../govern/build-cloud-governance-team` |
| Assess cloud risks | `.../govern/assess-cloud-risks` |
| Document governance policies | `.../govern/document-cloud-governance-policies` |
| Enforce policies (Azure governance tools) | `.../govern/enforce-cloud-governance-policies` |
| Monitor compliance | `.../govern/monitor-cloud-governance` |

## Tier 3 — Secure

| Question | Fetch |
|---|---|
| Secure overview | `.../secure/overview` |
| Teams, roles & functions | `.../secure/teams-roles` |
| Secure strategy / plan / ready / adopt / govern / manage | `.../secure/strategy` … `.../secure/manage` |
| Zero Trust adoption framework | `https://learn.microsoft.com/security/zero-trust/adopt/zero-trust-adoption-overview` |
| Defender for Cloud secure score | `https://learn.microsoft.com/azure/defender-for-cloud/secure-score-security-controls` |
| Microsoft Cloud Security Benchmark | `https://learn.microsoft.com/security/benchmark/azure/` |

## Tier 4 — Manage

| Question | Fetch |
|---|---|
| Manage overview | `.../manage/` |
| Management baseline | `.../manage/azure-management-guide/` |
| Operations / business commitments | `.../manage/considerations/` |
| Protect & recover (BCDR) | `.../manage/protect` |
| Azure Monitor | `https://learn.microsoft.com/azure/azure-monitor/` |

## Out of primary scope (governance-leaning skill) — pointers only

If a question strays into Strategy / Plan / Adopt, point the user to these rather than answering in depth:

| Topic | Fetch |
|---|---|
| Strategy (motivations, business case) | `.../strategy/` |
| Plan (digital estate, org alignment, skilling) | `.../plan/` |
| Adopt (Migrate / Innovate) | `.../adopt/` |
| CAF home / get started | `https://learn.microsoft.com/azure/cloud-adoption-framework/` |

## Hand-off to the `epac` skill

CAF says *what/why/where*; the actual Azure Policy implementation is the `epac` skill's job. Whenever a question becomes "write/deploy the policy that enforces this," route to `epac` rather than fetching policy detail here.

## Fetch discipline

- Quote methodology step names and design-area names verbatim from the fetched page (they get renamed).
- Cite the specific page, not just the CAF root.
- If CAF and another Microsoft source disagree, prefer CAF for *adoption methodology*, the security docs for *security control specifics*.
