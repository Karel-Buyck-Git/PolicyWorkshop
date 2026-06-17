# my-epac-repo

Enterprise Policy as Code (EPAC) starter repository.

## Structure

```
my-epac-repo/
├── Definitions/
│   ├── global-settings.jsonc                 # pacEnvironments (epac-dev, tenant), root scopes, MI locations
│   ├── policyDefinitions/                     # custom policies
│   │   ├── Security/   deny-public-ip.json, require-tag-owner.json
│   │   ├── Networking/ restrict-nsg-rules.json
│   │   └── Monitoring/ deploy-diagnostic-settings.json   (DeployIfNotExists)
│   ├── policySetDefinitions/                  # initiatives
│   │   ├── Security/    security-baseline-initiative.json
│   │   └── Governance/  tagging-initiative.json
│   ├── policyAssignments/                     # security-baseline, tagging, allowed-locations
│   ├── policyExemptions/<pacSelector>/        # exemptions per EPAC environment
│   └── policyStructures/                      # optional: Defender for Cloud / documentation
├── Output/                                    # generated plans (git-ignored)
├── pipelines/                                 # azure-pipelines.yml, github-actions.yml
└── README.md
```

## What's wired up

- **deny-public-ip** + **restrict-nsg-rules** + **deploy-diagnostic-settings (DINE)** -> bundled in **security-baseline-initiative** -> assigned by `security-baseline.jsonc`.
- **require-tag-owner** (custom) + built-in tag inheritance (Modify) -> bundled in **tagging-initiative** -> assigned by `tagging.jsonc`.
- Built-in **Allowed locations** -> assigned directly by `allowed-locations.jsonc`.

The DINE/Modify assignments declare `managedIdentityLocations`, so EPAC creates the managed identities and computes their role assignments (applied by `Deploy-RolesPlan`).

## Before you run — edit placeholders

In `Definitions/global-settings.jsonc`:
- `pacOwnerId` -> a real GUID (generate once, never change)
- `tenantId` -> your Entra tenant id
- `deploymentRootScope` per environment -> your management group ids (epac-dev MUST be separate from tenant)
- `managedIdentityLocation` -> your region

Then update the management group ids in the three assignment files, the Log Analytics workspace ids in `security-baseline.jsonc`, and the subscription id in `policyExemptions/tenant/exemptions.jsonc`.

> EPAC is desired-state: it manages and DELETES all policy within each `deploymentRootScope`. Always test against `epac-dev` first and review the plan before deploying to `tenant`.

## Run locally

```powershell
Install-Module EnterprisePolicyAsCode -Scope CurrentUser
Connect-AzAccount -Tenant <tenantId>     # or: az login --tenant <tenantId>

# 1) epac-dev first
Build-DeploymentPlans -PacEnvironmentSelector "epac-dev" -DefinitionsRootFolder ./Definitions -OutputFolder ./Output
Deploy-PolicyPlan     -PacEnvironmentSelector "epac-dev" -DefinitionsRootFolder ./Definitions -InputFolder ./Output
Deploy-RolesPlan      -PacEnvironmentSelector "epac-dev" -DefinitionsRootFolder ./Definitions -InputFolder ./Output

# 2) promote to tenant (gate behind approval in CI/CD)
Build-DeploymentPlans -PacEnvironmentSelector "tenant" -DefinitionsRootFolder ./Definitions -OutputFolder ./Output
Deploy-PolicyPlan     -PacEnvironmentSelector "tenant" -DefinitionsRootFolder ./Definitions -InputFolder ./Output
Deploy-RolesPlan      -PacEnvironmentSelector "tenant" -DefinitionsRootFolder ./Definitions -InputFolder ./Output
```

## CI/CD

- **Azure DevOps:** `pipelines/azure-pipelines.yml` — create the three workload-identity service connections and a `tenant` Environment with approvals.
- **GitHub Actions:** copy `pipelines/github-actions.yml` into `.github/workflows/`, set up three OIDC app registrations and the listed secrets/environments.

Service principal model (least privilege): a `Reader` plan SPN, a `Resource Policy Contributor` policy SPN, and a `Role Based Access Control Administrator` roles SPN. See the App Registrations doc.

## Docs

- Getting started: https://azure.github.io/enterprise-azure-policy-as-code/start-implementing/
- Assignments: https://azure.github.io/enterprise-azure-policy-as-code/policy-assignments/
- Exemptions: https://azure.github.io/enterprise-azure-policy-as-code/policy-exemptions/
- App registrations: https://azure.github.io/enterprise-azure-policy-as-code/ci-cd-app-registrations/
