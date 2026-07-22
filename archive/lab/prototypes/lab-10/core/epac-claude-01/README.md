# EPAC starter scaffold

Minimal Enterprise Policy as Code (EPAC) scaffold for this lab.

## Layout

```
epac/
  .gitignore                 # ignores Output/
  Definitions/
    global-settings.jsonc    # pacOwnerId + EPAC environments (epac-dev, tenant)
    policyDefinitions/
      require-tag-on-resource-group.json     # custom policy
    policySetDefinitions/
      org-governance-baseline.json           # custom initiative (uses 2 built-ins + the custom policy)
    policyAssignments/
      governance-baseline.jsonc              # assigns the custom initiative
      allowed-locations.jsonc                # minimal single built-in policy assignment
    policyExemptions/
      epac-dev/              # (empty) add dev exemptions here
      tenant/
        sample-exemption.jsonc               # time-boxed waiver example
```

## Before you run

Edit `Definitions/global-settings.jsonc`:
- `pacOwnerId` -> a real GUID (generate once, keep forever)
- `tenantId` -> your Entra tenant id
- `deploymentRootScope` for each environment -> your management group ids
  - `epac-dev` must be a SEPARATE MG from `tenant` (not nested)
- `managedIdentityLocation` -> your preferred region

Then update the management group ids in the assignment files and the subscription id in the sample exemption.

> EPAC is desired-state: it manages (and deletes) ALL policy within each `deploymentRootScope`. Always test against `epac-dev` first and review the plan before deploying to `tenant`.

## Run it

```powershell
Install-Module EnterprisePolicyAsCode -Scope CurrentUser
Connect-AzAccount -Tenant <tenantId>      # or: az login --tenant <tenantId>

# Always against epac-dev first:
Build-DeploymentPlans -PacEnvironmentSelector "epac-dev" -DefinitionsRootFolder ./Definitions -OutputFolder ./Output
Deploy-PolicyPlan     -PacEnvironmentSelector "epac-dev" -DefinitionsRootFolder ./Definitions -InputFolder ./Output
Deploy-RolesPlan      -PacEnvironmentSelector "epac-dev" -DefinitionsRootFolder ./Definitions -InputFolder ./Output

# Then promote to tenant (gate this behind approval in CI/CD):
Build-DeploymentPlans -PacEnvironmentSelector "tenant" -DefinitionsRootFolder ./Definitions -OutputFolder ./Output
Deploy-PolicyPlan     -PacEnvironmentSelector "tenant" -DefinitionsRootFolder ./Definitions -InputFolder ./Output
Deploy-RolesPlan      -PacEnvironmentSelector "tenant" -DefinitionsRootFolder ./Definitions -InputFolder ./Output
```

See the full guide (`EPAC-Scaffold-Guide.md`) for CI/CD (GitHub Actions / Azure DevOps), service principals, scoping and exemptions.
