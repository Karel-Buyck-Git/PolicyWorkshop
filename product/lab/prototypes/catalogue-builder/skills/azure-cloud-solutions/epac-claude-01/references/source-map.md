# Source Map — what to fetch for which question

The skill is live-fetch: before stating an Azure-specific fact, fetch the matching source here, read it, then answer and cite it. Prefer fetching the raw file on GitHub (`raw.githubusercontent.com`) when you need exact JSON; use the rendered docs site for guidance prose.

## Azure Policy built-in definitions & schema

| Question | Fetch |
|---|---|
| Does a built-in policy/initiative exist for X? | Browse `https://github.com/Azure/azure-policy/tree/master/built-in-policies/policyDefinitions` and `.../policySetDefinitions`; or search built-ins on AzAdvertizer `https://www.azadvertizer.net/azpolicyadvertizer_all.html` |
| Exact JSON of a built-in | `https://github.com/Azure/azure-policy/tree/master/built-in-policies` then open the raw file |
| Reference/regulatory initiatives (e.g. CIS, NIST, ISO) | `https://github.com/Azure/azure-policy/tree/master/built-in-references` |
| Reusable policy patterns | `https://github.com/Azure/azure-policy/tree/master/patterns` |
| Custom samples to adapt | `https://github.com/Azure/azure-policy/tree/master/samples` |
| Known issues / resource types policy can't fully evaluate / read-only aliases | README at `https://github.com/Azure/azure-policy` (Known Issues section) |
| Policy definition structure (fields, mode, metadata) | `https://learn.microsoft.com/azure/governance/policy/concepts/definition-structure-basics` |
| Policy effects (audit, deny, deployIfNotExists, modify, etc.) | `https://learn.microsoft.com/azure/governance/policy/concepts/effect-basics` (per-effect pages branch from here) |
| Aliases — discover/list | `https://learn.microsoft.com/azure/governance/policy/concepts/definition-structure#aliases`; live alias lookup on AzAdvertizer `https://www.azadvertizer.net/azpolicyaliases_all.html` |
| Assignment structure / excluded scopes | `https://learn.microsoft.com/azure/governance/policy/concepts/assignment-structure` |
| Exemption structure | `https://learn.microsoft.com/azure/governance/policy/concepts/exemption-structure` |

## EPAC (deployment & operations)

| Question | Fetch |
|---|---|
| Getting started, prerequisites, concepts | `https://azure.github.io/enterprise-azure-policy-as-code/start-implementing/` |
| Hydration Kit (guided setup) | `https://azure.github.io/enterprise-azure-policy-as-code/start-hydration-kit/` |
| `global-settings.jsonc`, pacEnvironments, deploymentRootScope | `https://azure.github.io/enterprise-azure-policy-as-code/settings-global-setting-file/` |
| Desired state strategy (what gets deleted, how to scope) | `https://azure.github.io/enterprise-azure-policy-as-code/settings-desired-state/` |
| Authoring policy definition files | `https://azure.github.io/enterprise-azure-policy-as-code/policy-definitions/` |
| Authoring policy set (initiative) files | `https://azure.github.io/enterprise-azure-policy-as-code/policy-set-definitions/` |
| Authoring assignment files | `https://azure.github.io/enterprise-azure-policy-as-code/policy-assignments/` |
| CSV-driven assignment parameters | `https://azure.github.io/enterprise-azure-policy-as-code/policy-assignments-csv-parameters/` |
| Exemptions | `https://azure.github.io/enterprise-azure-policy-as-code/policy-exemptions/` |
| ALZ integration overview | `https://azure.github.io/enterprise-azure-policy-as-code/integrating-with-alz-overview/` |
| ALZ library sync (`Sync-ALZPolicyFromLibrary`) | `https://azure.github.io/enterprise-azure-policy-as-code/integrating-with-alz-library/` |
| CI/CD overview & branching | `https://azure.github.io/enterprise-azure-policy-as-code/ci-cd-overview/` |
| Azure DevOps pipelines | `https://azure.github.io/enterprise-azure-policy-as-code/ci-cd-ado-pipelines/` |
| GitHub Actions | `https://azure.github.io/enterprise-azure-policy-as-code/ci-cd-github-actions/` |
| App registration / service principal setup | `https://azure.github.io/enterprise-azure-policy-as-code/ci-cd-app-registrations/` |
| Operational scripts (export, document, remediation) | `https://azure.github.io/enterprise-azure-policy-as-code/operational-scripts/` |
| Remediation enforcement guidance | `https://azure.github.io/enterprise-azure-policy-as-code/guidance-remediation/` |
| Exclusions / exemption operator guidance | `https://azure.github.io/enterprise-azure-policy-as-code/guidance-scope-exclusions/` , `.../guidance-exemptions/` |
| Schemas (for VS Code validation) | `https://github.com/Azure/enterprise-azure-policy-as-code/tree/main/Schemas` |
| StarterKit examples | `https://github.com/Azure/enterprise-azure-policy-as-code/tree/main/StarterKit` |
| What changed in a version | `https://github.com/Azure/enterprise-azure-policy-as-code/releases` |

## CAF / Azure Landing Zones (architecture)

| Question | Fetch |
|---|---|
| Cloud Adoption Framework home | `https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/` |
| Landing zone design areas | `https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-areas` |
| Management group hierarchy design | `https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-management-groups` |
| Governance / policy-driven guardrails | `https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/governance` |
| ALZ policy list (what the baseline assigns) | `https://aka.ms/alz/policies` |
| ALZ conceptual architecture | `https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/` |

## Tier 1 — Foundations (scope, MG, RBAC, evaluation)

| Question | Fetch |
|---|---|
| Scope in Azure Policy | `https://learn.microsoft.com/azure/governance/policy/concepts/scope` |
| Management groups overview | `https://learn.microsoft.com/azure/governance/management-groups/overview` |
| Azure Policy overview | `https://learn.microsoft.com/azure/governance/policy/overview` |
| Azure RBAC overview | `https://learn.microsoft.com/azure/role-based-access-control/overview` |

## Tier 3 — Networking & management guardrails

| Question | Fetch |
|---|---|
| Built-in network policies | `https://github.com/Azure/azure-policy/tree/master/built-in-policies/policyDefinitions/Network` |
| Built-in policies by category (tags, monitoring, security, etc.) | `https://github.com/Azure/azure-policy/tree/master/built-in-policies/policyDefinitions` |
| Application Gateway WAF concepts | `https://learn.microsoft.com/azure/web-application-firewall/ag/ag-overview` |
| Defender for Cloud policy initiatives | `https://learn.microsoft.com/azure/defender-for-cloud/` |
| Which guardrails the ALZ baseline already covers | `https://aka.ms/alz/policies` |

## Supporting tools

- **AzAdvertizer** `https://www.azadvertizer.net/` — fastest live lookup for built-in policy/initiative/alias/RBAC changes.
- **Azure Governance Visualizer (AzGovViz)** `https://github.com/JulianHayward/Azure-MG-Sub-Governance-Reporting` — tenant-wide governance reporting/visualization.

## Fetch discipline

- Quote definition IDs and effect names verbatim from the fetched source.
- If two sources disagree, prefer the Azure Policy repo / Learn docs for *what a policy is*, and EPAC docs for *how to deploy it*.
- Always cite the spe