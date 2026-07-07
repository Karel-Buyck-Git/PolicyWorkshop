# Enterprise Policy as Code (EPAC) — Scaffold & Deployment Guide

A practical guide to standing up EPAC on an Azure tenant and wiring it into **GitHub Actions** and **Azure DevOps**. It covers the concepts you need first, then the step-by-step: Azure prep, repo scaffold, authoring, assigning, scoping, exempting, and CI/CD.

> Verified against EPAC v11 (`EnterprisePolicyAsCode` PowerShell module) and the official docs (June 2026). Cmdlet names and file schemas are current as of that release.

---

## Table of contents

1. [Mental model: what EPAC actually is](#1-mental-model)
2. [Core concepts you must understand first](#2-core-concepts)
3. [Prerequisites](#3-prerequisites)
4. [Azure setup](#4-azure-setup)
5. [Scaffold the repo (Hydration Kit vs manual)](#5-scaffold-the-repo)
6. [The `global-settings.jsonc` file](#6-global-settingsjsonc)
7. [The deployment flow: plan → deploy policy → deploy roles](#7-deployment-flow)
8. [Authoring: definitions, initiatives (policy sets)](#8-authoring-definitions-and-initiatives)
9. [How to assign](#9-how-to-assign)
10. [How to scope (and exclude scope)](#10-how-to-scope)
11. [How to exempt](#11-how-to-exempt)
12. [Service principals & permissions (CI/CD identity)](#12-service-principals)
13. [GitHub Actions setup](#13-github-actions)
14. [Azure DevOps setup](#14-azure-devops)
15. [Branching flow & day-2 operations](#15-branching-and-operations)
16. [Quick reference](#16-quick-reference)

---

## 1. Mental model

EPAC is **not** a deployment tool you point at one resource. It is a _desired-state_ engine for Azure Policy. You describe the complete set of policy definitions, initiatives, assignments, and exemptions you want **as JSON files in a Git repo**, and EPAC reconciles the live Azure environment to match — creating, updating, and **deleting** anything within its managed scope that isn't in code.

Three things follow from "desired state":

- EPAC treats its `deploymentRootScope` as the **single source of truth**. Anything policy-related in that scope that isn't in your repo will be removed. Scope it deliberately.
- The workflow is always **plan first, then apply**. The plan is a diff; you review it before anything changes.
- It splits "apply" into **two** phases — policy objects, then RBAC role assignments — because they need different permissions.

EPAC is a set of PowerShell cmdlets (`EnterprisePolicyAsCode` module). Any CI/CD system that can run PowerShell works; the project ships starter pipelines for GitHub Actions, Azure DevOps, and GitLab. The `az` CLI's role is essentially authentication — the real work is the cmdlets.

---

## 2. Core concepts

### pacOwnerId

A GUID that uniquely stamps everything this EPAC instance deploys (written into resource `metadata.pacOwnerId`). It's how EPAC knows "I own this, so I may manage/delete it" versus "something else deployed this, leave it alone." Generate one GUID and keep it for the life of the repo.

### deploymentRootScope

The Management Group (recommended) or scope EPAC manages. EPAC controls policy at this scope **and everything beneath it**. Best practice: use an **intermediate root management group**, never the Tenant Root Group — that avoids lockout and keeps flexibility.

### pacEnvironment & pacSelector

An **EPAC Environment** is an isolated target for deployment, identified by a symbolic string called a **pacSelector** (e.g. `epac-dev`, `tenant`). Each has its own `deploymentRootScope`. You almost always run **two**:

| pacSelector | Purpose                                                | Typical deploymentRootScope                 |
| ----------- | ------------------------------------------------------ | ------------------------------------------- |
| `epac-dev`  | Safe, isolated MG hierarchy for testing policy changes | a separate, cloned MG (e.g. `epac-contoso`) |
| `tenant`    | Your real hierarchy                                    | your intermediate root MG (e.g. `contoso`)  |

> Important: the dev environment's scope must be **separate** from (not nested inside) your tenant environment's scope. EPAC manages _all_ policy in a root scope, so nesting would cause the two environments to fight.

> Naming note: call the production-ish one `tenant` (or `tenant01`), not `prod`. This avoids confusing **EPAC Environments** with your normal SDLC environments (prod/dev/test), which are just scopes _inside_ a pacEnvironment.

### Initiative = Policy Set Definition

What the Azure portal calls an **initiative**, the API and EPAC call a **policy set definition**. In EPAC these live as JSON in `Definitions/policySetDefinitions/`. They are not pushed with discrete commands — you author the file, and `Build-DeploymentPlans` figures out the diff.

### Managed identities

`DeployIfNotExists` (DINE) and `Modify` effects need a managed identity plus role assignments to remediate. EPAC creates these automatically and calculates the required roles from the policy's `roleDefinitionIds`. You supply a default location (`managedIdentityLocation`) per environment.

---

## 3. Prerequisites

**Software (on your workstation and CI runners):**

- PowerShell **7.4+**
- **Az** PowerShell module
- **EnterprisePolicyAsCode** module: `Install-Module EnterprisePolicyAsCode -Scope CurrentUser`
- Azure CLI (`az`) — optional but handy for login/scripting

**Knowledge:** Azure Management Groups, Azure Policy, and Policy scope. EPAC assumes you know these.

**Azure RBAC you (the operator) need for initial setup:**

| Role                                      | For                                                                     |
| ----------------------------------------- | ----------------------------------------------------------------------- |
| `Resource Policy Contributor`             | create/manage/delete policy resources                                   |
| `Role Based Access Control Administrator` | create/manage/delete RBAC assignments                                   |
| `Management Group Contributor`            | create MGs (only if using the Hydration Kit to build the dev hierarchy) |

---

## 4. Azure setup

1. **Decide your root scope.** Pick or create an intermediate root MG (e.g. `contoso`). This is your `tenant` environment's `deploymentRootScope`.

2. **Create the EPAC-dev hierarchy.** Create a _separate_ MG (e.g. `epac-contoso`), ideally mirroring your prod MG structure so tests are representative. This is your `epac-dev` scope. (The Hydration Kit can build this for you.)

3. **Pick a managed-identity location** per environment (e.g. `eastus2`) for DINE/Modify remediation identities.

4. **Authenticate** for interactive runs:

   ```powershell
   az login --tenant <tenantId>          # or Connect-AzAccount -Tenant <tenantId>
   az account set --subscription <subId>
   ```

   EPAC uses your current Az context. (CI/CD uses service principals — see §12.)

---

## 5. Scaffold the repo

You have two paths. **Use the Hydration Kit unless you have a strong reason not to.**

### Option A — Hydration Kit (recommended)

An interactive setup that builds the folder structure, generates `global-settings.jsonc`, creates the `epac-dev` environment, seeds starter policies/compliance frameworks, and drops in starter CI/CD pipeline templates. It can also create the dev MG hierarchy.

Install the module, then run the hydration starter cmdlet and answer the prompts:

```powershell
Install-Module EnterprisePolicyAsCode -Scope CurrentUser
New-HydrationDefinitionFolder -DefinitionsRootFolder ./Definitions   # scaffolds the Definitions tree
# then follow the Hydration Kit guide to generate global-settings and starter content
```

> The kit walks you through guided decisions; you can customize everything it generates afterward. See the official Hydration Kit guide (link in Sources).

### Option B — Manual configuration

For advanced/custom setups. Create the folder structure yourself:

```
Definitions/
  global-settings.jsonc
  policyDefinitions/          # custom policy definitions
  policySetDefinitions/       # initiatives (policy sets)
  policyAssignments/          # assignments to scopes
  policyExemptions/           # exemptions, per pacSelector subfolder
Output/                       # generated plans (gitignored)
```

Either way, you end up with a `Definitions/` tree and a `global-settings.jsonc`.

### Bonus — Extract what already exists

If the tenant already has policies, run the extraction script to pull live policy resources **into EPAC format** so you start from reality instead of a blank repo:

```powershell
Export-AzPolicyResources -DefinitionsRootFolder ./Definitions -OutputFolder ./Output
# (or the documented Extracting Policy Resources workflow / Get-AzExemptions.ps1 for exemptions)
```

---

## 6. global-settings.jsonc

The central config. It defines your `pacOwnerId` and your `pacEnvironments`. Minimal two-environment example:

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/Azure/enterprise-azure-policy-as-code/main/Schemas/global-settings-schema.json",
  "pacOwnerId": "11111111-2222-3333-4444-555555555555",
  "pacEnvironments": [
    {
      "pacSelector": "epac-dev",
      "cloud": "AzureCloud",
      "tenantId": "77777777-8888-9999-1111-222222222222",
      "deploymentRootScope": "/providers/Microsoft.Management/managementGroups/epac-contoso",
      "managedIdentityLocation": "eastus2"
    },
    {
      "pacSelector": "tenant",
      "cloud": "AzureCloud",
      "tenantId": "77777777-8888-9999-1111-222222222222",
      "deploymentRootScope": "/providers/Microsoft.Management/managementGroups/contoso",
      "managedIdentityLocation": "eastus2"
    }
  ]
}
```

Key fields: `pacSelector` (the symbolic name you target in commands and in `scope` blocks), `deploymentRootScope` (what EPAC owns), `managedIdentityLocation` (default for remediation identities), `tenantId` (enables multi-tenant), `cloud` (commercial/sovereign). The `$schema` line gives you IntelliSense in VS Code.

---

## 7. Deployment flow

EPAC always runs in three steps, **per EPAC environment**:

```powershell
# 1) PLAN — diff code against the live environment; writes plan files to ./Output
Build-DeploymentPlans `
  -PacEnvironmentSelector "epac-dev" `
  -DefinitionsRootFolder ./Definitions `
  -OutputFolder ./Output

# 2) DEPLOY POLICY — apply definitions, initiatives, assignments, exemptions
Deploy-PolicyPlan `
  -PacEnvironmentSelector "epac-dev" `
  -DefinitionsRootFolder ./Definitions `
  -InputFolder ./Output

# 3) DEPLOY ROLES — apply role assignments needed by remediation managed identities
Deploy-RolesPlan `
  -PacEnvironmentSelector "epac-dev" `
  -DefinitionsRootFolder ./Definitions `
  -InputFolder ./Output
```

- `Build-DeploymentPlans` produces `policy-plan.json` and `roles-plan.json` in `./Output`. If there are no changes, the deploy steps are no-ops — which is what makes this safe to run repeatedly in CI/CD.
- The two deploy steps are split because they need **different identities/permissions** (policy contributor vs RBAC administrator).
- Run and review the plan **before** deploying to `tenant`. Test in `epac-dev` first.

---

## 8. Authoring definitions and initiatives

### Custom policy definition

Drop a JSON file in `Definitions/policyDefinitions/`. Standard Azure policy schema. EPAC injects the correct definition scope, so you reference it later by `policyName`.

### Initiative (policy set definition)

Drop a JSON file in `Definitions/policySetDefinitions/<your-initiative>.json`. Standard Azure policy set schema (`properties.policyDefinitions[]` referencing built-in or your custom member policies). Reference it later by `policySetName`.

You don't "deploy an initiative" with a command — you author the file and let `Build-DeploymentPlans` detect it. Built-in initiatives (ASB, NIST, etc.) don't need a definition file at all; you reference them directly by `policySetId` in the assignment.

---

## 9. How to assign

Assignments live in `Definitions/policyAssignments/` as JSON. EPAC does a **recursive** search of that folder, so organize files however you like. The format is a **hierarchical tree** — each branch accumulates settings, so you avoid copy/paste.

Every collated branch must end up with: a `definitionEntry` (or `definitionEntryList`), assignment naming (`name` + `displayName`), and a `scope`.

### Simplest case — one initiative, dev + prod scope

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/Azure/enterprise-azure-policy-as-code/main/Schemas/policy-assignment-schema.json",
  "nodeName": "/root",
  "definitionEntry": {
    "policySetName": "general-allowed-locations-policy-set", // your custom initiative
    "displayName": "Allowed Locations Initiative"
  },
  "assignment": {
    "name": "allowed-locations", // 24-char limit on concatenated name!
    "displayName": "Allowed Locations",
    "description": "Sets the allowed locations"
  },
  "enforcementMode": "Default",
  "parameters": {
    "AllowedLocations": ["centralus", "eastus", "eastus2", "westeurope"]
  },
  "scope": {
    "epac-dev": ["/providers/Microsoft.Management/managementGroups/Epac-Mg-1"],
    "tenant": ["/providers/Microsoft.Management/managementGroups/contoso"]
  }
}
```

Notes:

- Reference a **custom** initiative with `policySetName`; a **built-in** one with `policySetId`. (Same pattern for single policies: `policyName` / `policyId`.)
- `parameters` use a **simplified** form — no `value` wrapper; EPAC injects it.
- `enforcementMode: "DoNotEnforce"` lets you deploy an assignment for what-if analysis without actually enforcing.

### Assign multiple initiatives at once — `definitionEntryList`

Creates one assignment per list entry at every leaf. Great for stacking compliance frameworks:

```jsonc
"definitionEntryList": [
  {
    "policySetId": "/providers/Microsoft.Authorization/policySetDefinitions/1f3afdf9-d0c9-4c3d-847f-89da613e70a8",
    "displayName": "Azure Security Benchmark",
    "assignment": { "append": true, "name": "asb", "displayName": "Azure Security Benchmark", "description": "ASB Initiative." }
  },
  {
    "policySetId": "/providers/Microsoft.Authorization/policySetDefinitions/179d1daa-458f-4e47-8086-2a68d0d6c38f",
    "displayName": "NIST SP 800-53 Rev. 5",
    "assignment": { "append": true, "name": "nist-800-53-r5", "displayName": "NIST SP 800-53 Rev. 5", "description": "NIST Initiative." }
  }
]
```

### Big initiatives → manage parameters/effects with CSV

For large frameworks (ASB, NIST, PCI…) with dozens/hundreds of parameters and effect overrides, don't hand-write JSON. Point the assignment at a **CSV** file (recommended for >10 included policies). See the CSV Assignment Parameters doc.

### Remediation (DINE/Modify) identities

Add `managedIdentityLocations` (per env or `"*"`). EPAC computes the required roles and writes them to `roles-plan.json`, applied by `Deploy-RolesPlan`. System-assigned identities are the recommended default; user-assigned is supported but needs extra `Managed Identity Operator` permission on the CI/CD SPN.

---

## 10. How to scope

Scope is set per **pacSelector** inside the `scope` block, so the _same_ assignment file targets a test MG in `epac-dev` and the real MG in `tenant`:

```jsonc
"scope": {
  "epac-dev": [ "/providers/Microsoft.Management/managementGroups/Epac-Prod" ],
  "tenant":   [
    "/providers/Microsoft.Management/managementGroups/Contoso-Prod",
    "/providers/Microsoft.Management/managementGroups/Contoso-Prod2"
  ]
}
```

`scope` is required exactly once per tree branch. Scopes can be MGs, subscriptions, resource groups, or resources.

### Excluding scope — `notScopes`

Cumulative from `global-settings` plus the tree. Use `"*"` for all environments. Supports wildcard patterns on RG/subscription names:

```jsonc
"notScopes": {
  "*":      [ "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-pattern*" ],
  "tenant": [ "/providers/Microsoft.Management/managementGroups/sandbox-mg" ]
}
```

> Rule of thumb: use `notScopes` to permanently carve a scope out of an assignment's reach; use **exemptions** (next) for targeted, time-boxed, auditable exceptions to specific policies.

---

## 11. How to exempt

Exemptions live in `Definitions/policyExemptions/<pacSelector>/` — one subfolder **per EPAC environment**. A missing subfolder means EPAC doesn't manage that environment's exemptions. JSON is recommended over CSV.

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/Azure/enterprise-azure-policy-as-code/main/Schemas/policy-exemption-schema.json",
  "exemptions": [
    {
      "name": "sql-waiver-legacy",
      "displayName": "Legacy SQL waiver",
      "description": "Temporary waiver pending migration",
      "exemptionCategory": "Waiver", // Waiver | Mitigated
      "expiresOn": "2026-12-31", // empty = no expiry
      "scopes": ["/subscriptions/11111111-2222-3333-4444-555555555555"],
      "policyDefinitionId": "/providers/Microsoft.Authorization/policyDefinitions/00000000-0000-0000-0000-000000000000"
    }
  ]
}
```

You specify **what** to exempt one of three ways:

- **Option A — by policy definition** (`policyDefinitionId` / `policyDefinitionName`): exempts that policy across _every_ assignment that includes it. Simplest and most readable — **recommended for new exemptions.**
- **Option B — by assignment** (`policyAssignmentId`): the classic approach; good for exempting many policies of one assigned initiative at once. Add `policyDefinitionReferenceIds` to target specific member policies.
- **Option C — by policy set** (`policySetDefinitionId` / `policySetDefinitionName`): one exemption per assignment of that initiative.

And **where** with `scope` (single) or `scopes` (array; recommended — supports MGs, subs, RGs, resources, and wildcard patterns). Set `exemptionCategory` to `Waiver` or `Mitigated`, and optionally `expiresOn` for time-boxing.

> Moving from excluded scopes to exemptions: by default EPAC won't deploy an exemption on a scope that's already excluded from the assignment, and will delete exemptions found on excluded scopes. Override with `-SkipNotScopedExemptions` on `Build-DeploymentPlans`.

---

## 12. Service principals

CI/CD uses Entra ID **service principals** (app registrations), following least-privilege and separation of duties. Recommended layout for a two-environment setup:

| Service principal        | Azure role                                                                | Assigned at               | Used by                                            |
| ------------------------ | ------------------------------------------------------------------------- | ------------------------- | -------------------------------------------------- |
| `spn-epac-plan`          | `Reader`                                                                  | Tenant Root               | Build-DeploymentPlans (all envs)                   |
| `spn-epac-dev`           | `Resource Policy Contributor` + `Role Based Access Control Administrator` | `epac-contoso` (dev root) | dev policy + role deploy (one SPN is fine for dev) |
| `spn-epac-tenant-deploy` | `Resource Policy Contributor`                                             | `contoso` (tenant root)   | Deploy-PolicyPlan (prod)                           |
| `spn-epac-tenant-roles`  | `Role Based Access Control Administrator`                                 | `contoso`                 | Deploy-RolesPlan (prod)                            |

Notes:

- The **plan** SPN only needs `Reader` — it never changes anything.
- Separate **policy** and **role** SPNs in production so the privileged RBAC identity is isolated. In dev you may collapse them into one (both role assignments still required).
- If you use **user-assigned** MIs for remediation, the role-deploy SPN also needs `Managed Identity Operator` (or `Microsoft.ManagedIdentity/userAssignedIdentities/assign/action`) where those identities live.
- Consider RBAC **conditions** to stop the role SPN from granting `Owner`/`User Access Administrator`.

### Credentials: prefer federated (OIDC), avoid secrets

Both GitHub and Azure DevOps support **workload identity federation**, so you don't store/rotate client secrets. On each app registration, add a **Federated Credential** with:

- **Audience:** `api://AzureADTokenExchange`
- **Issuer:** your IdP's OIDC issuer URL (GitHub: `https://token.actions.githubusercontent.com`; ADO uses the service-connection issuer)
- **Subject:** must match the token's `sub` claim (GitHub: e.g. `repo:<org>/<repo>:environment:prod` or `:ref:refs/heads/main`; ADO: generated when you create a workload-identity service connection)

---

## 13. GitHub Actions

**One-time:**

1. Create the app registrations and Azure role assignments from §12.
2. On each app, add a **federated credential**:
   - Issuer `https://token.actions.githubusercontent.com`, Audience `api://AzureADTokenExchange`.
   - Subject matching how you'll run — e.g. `repo:contoso/epac:environment:tenant` if you gate prod with a GitHub **Environment** named `tenant`, or `repo:contoso/epac:ref:refs/heads/main`.
3. Store `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, and each app's `AZURE_CLIENT_ID` as repo/environment **secrets/variables**. Create GitHub **Environments** (`epac-dev`, `tenant`) and put required reviewers on `tenant` to gate prod.
4. Grant the workflow `permissions: id-token: write` and `contents: read` (required for OIDC).

**The starter workflows** (from the Hydration Kit / repo) implement the branching flow below. A minimal plan-and-deploy job looks like:

```yaml
name: EPAC Deploy (tenant)
on:
  push:
    branches: [main]

permissions:
  id-token: write # required for OIDC
  contents: read

jobs:
  plan:
    runs-on: ubuntu-latest
    environment: tenant-plan
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.PLAN_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - shell: pwsh
        run: |
          Install-Module EnterprisePolicyAsCode -Force -Scope CurrentUser
          Build-DeploymentPlans -PacEnvironmentSelector "tenant" `
            -DefinitionsRootFolder ./Definitions -OutputFolder ./Output
      - uses: actions/upload-artifact@v4
        with: { name: plans, path: ./Output }

  deploy-policy:
    needs: plan
    runs-on: ubuntu-latest
    environment: tenant # add required reviewers here to gate prod
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { name: plans, path: ./Output }
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.POLICY_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - shell: pwsh
        run: |
          Install-Module EnterprisePolicyAsCode -Force -Scope CurrentUser
          Deploy-PolicyPlan -PacEnvironmentSelector "tenant" `
            -DefinitionsRootFolder ./Definitions -InputFolder ./Output

  deploy-roles:
    needs: deploy-policy
    runs-on: ubuntu-latest
    environment: tenant
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { name: plans, path: ./Output }
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.ROLES_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - shell: pwsh
        run: |
          Install-Module EnterprisePolicyAsCode -Force -Scope CurrentUser
          Deploy-RolesPlan -PacEnvironmentSelector "tenant" `
            -DefinitionsRootFolder ./Definitions -InputFolder ./Output
```

Each job logs in as a _different_ SPN (`PLAN_/POLICY_/ROLES_CLIENT_ID`) to match the least-privilege split. PRs typically run a plan-only workflow against `epac-dev` as a check.

---

## 14. Azure DevOps

**One-time:**

1. Create the app registrations and Azure role assignments from §12.
2. Create **service connections** — prefer **Workload Identity Federation** (no secret). ADO auto-creates the matching federated credential on the app, or gives you the issuer/subject to add manually. Make one connection per SPN (plan / policy / roles), or per environment.
3. Create **Environments** (`epac-dev`, `tenant`) under Pipelines → Environments, and add **Approvals and checks** on `tenant` to gate production.
4. Add a variable group (or pipeline variables) for tenant/subscription IDs.

**Pipeline** (multi-stage; mirrors the three-step flow). Skeleton:

```yaml
trigger:
  branches: { include: [main] }

stages:
  - stage: Plan
    jobs:
      - job: BuildPlans
        pool: { vmImage: ubuntu-latest }
        steps:
          - task: AzurePowerShell@5
            inputs:
              azureSubscription: "sc-epac-plan" # Reader SPN, workload-identity service connection
              ScriptType: InlineScript
              azurePowerShellVersion: LatestVersion
              pwsh: true
              Inline: |
                Install-Module EnterprisePolicyAsCode -Force -Scope CurrentUser
                Build-DeploymentPlans -PacEnvironmentSelector "tenant" `
                  -DefinitionsRootFolder "$(Build.SourcesDirectory)/Definitions" `
                  -OutputFolder "$(Build.ArtifactStagingDirectory)/Output"
          - publish: $(Build.ArtifactStagingDirectory)/Output
            artifact: plans

  - stage: DeployPolicy
    dependsOn: Plan
    jobs:
      - deployment: DeployPolicy
        environment: tenant # approvals gate here
        pool: { vmImage: ubuntu-latest }
        strategy:
          runOnce:
            deploy:
              steps:
                - download: current
                  artifact: plans
                - task: AzurePowerShell@5
                  inputs:
                    azureSubscription: "sc-epac-tenant-policy" # Resource Policy Contributor SPN
                    ScriptType: InlineScript
                    azurePowerShellVersion: LatestVersion
                    pwsh: true
                    Inline: |
                      Install-Module EnterprisePolicyAsCode -Force -Scope CurrentUser
                      Deploy-PolicyPlan -PacEnvironmentSelector "tenant" `
                        -DefinitionsRootFolder "$(Build.SourcesDirectory)/Definitions" `
                        -InputFolder "$(Pipeline.Workspace)/plans"

  - stage: DeployRoles
    dependsOn: DeployPolicy
    jobs:
      - deployment: DeployRoles
        environment: tenant
        pool: { vmImage: ubuntu-latest }
        strategy:
          runOnce:
            deploy:
              steps:
                - download: current
                  artifact: plans
                - task: AzurePowerShell@5
                  inputs:
                    azureSubscription: "sc-epac-tenant-roles" # RBAC Administrator SPN
                    ScriptType: InlineScript
                    azurePowerShellVersion: LatestVersion
                    pwsh: true
                    Inline: |
                      Install-Module EnterprisePolicyAsCode -Force -Scope CurrentUser
                      Deploy-RolesPlan -PacEnvironmentSelector "tenant" `
                        -DefinitionsRootFolder "$(Build.SourcesDirectory)/Definitions" `
                        -InputFolder "$(Pipeline.Workspace)/plans"
```

Add a separate PR-validation pipeline that runs **only** `Build-DeploymentPlans` against `epac-dev` and publishes the plan for reviewers. Use **branch policies** to require it before merge.

---

## 15. Branching and operations

**Recommended flow** (matches EPAC's starter pipelines):

1. Developer branches, edits Definitions, opens a PR.
2. **PR check** runs `Build-DeploymentPlans` against `epac-dev` (and often deploys to `epac-dev`) so reviewers see the diff and can test in isolation.
3. On merge to `main`, the pipeline runs the full three-step flow against `tenant`, with an **approval gate** before the deploy stages.

**Day-2 operational scripts** (in the module):

- `Export-AzPolicyResources` — extract existing policy/initiatives/assignments into EPAC format.
- `Get-AzExemptions.ps1` — extract existing exemptions to JSON/CSV.
- Remediation helpers to kick off remediation tasks for DINE/Modify policies after deployment.
- Documentation generators to produce readable policy/assignment docs.

**Golden rules:**

- Always test in `epac-dev` before `tenant`.
- Review the plan before applying — it shows deletions too.
- Keep `pacOwnerId` stable; it's how EPAC claims ownership.
- Remember EPAC deletes out-of-band policy within its root scope. Scope deliberately.

---

## 16. Quick reference

**Cmdlets**

| Step             | Cmdlet                                             | Identity / role                           |
| ---------------- | -------------------------------------------------- | ----------------------------------------- |
| Scaffold         | `New-HydrationDefinitionFolder`                    | operator                                  |
| Extract existing | `Export-AzPolicyResources`, `Get-AzExemptions.ps1` | Reader+                                   |
| Plan             | `Build-DeploymentPlans`                            | `Reader`                                  |
| Deploy policy    | `Deploy-PolicyPlan`                                | `Resource Policy Contributor`             |
| Deploy roles     | `Deploy-RolesPlan`                                 | `Role Based Access Control Administrator` |

**Folder structure**

```
Definitions/
  global-settings.jsonc
  policyDefinitions/        # custom policies
  policySetDefinitions/     # initiatives
  policyAssignments/        # assignments (recursive search; folder layout is free)
  policyExemptions/<pacSelector>/   # exemptions per EPAC environment
Output/                     # generated plans (gitignore)
```

**Reference IDs in assignments**

| You want to assign  | Use             |
| ------------------- | --------------- |
| Custom policy       | `policyName`    |
| Built-in policy     | `policyId`      |
| Custom initiative   | `policySetName` |
| Built-in initiative | `policySetId`   |

**24-char limit** on the concatenated assignment `name`. `displayName` ≤128, `description` ≤512.

---

## Sources

- [EPAC — Overview & Prerequisites](https://azure.github.io/enterprise-azure-policy-as-code/start-implementing/)
- [EPAC — Global Settings](https://azure.github.io/enterprise-azure-policy-as-code/settings-global-setting-file/)
- [EPAC — Hydration Kit](https://azure.github.io/enterprise-azure-policy-as-code/start-hydration-kit/)
- [EPAC — Policy Set Definitions (initiatives)](https://azure.github.io/enterprise-azure-policy-as-code/policy-set-definitions/)
- [EPAC — Policy Assignment Files](https://azure.github.io/enterprise-azure-policy-as-code/policy-assignments/)
- [EPAC — Policy Exemptions](https://azure.github.io/enterprise-azure-policy-as-code/policy-exemptions/)
- [EPAC — CI/CD Overview](https://azure.github.io/enterprise-azure-policy-as-code/ci-cd-overview/)
- [EPAC — App Registrations & Service Principal Setup](https://azure.github.io/enterprise-azure-policy-as-code/ci-cd-app-registrations/)
- [EPAC — Azure DevOps Pipelines](https://azure.github.io/enterprise-azure-policy-as-code/ci-cd-ado-pipelines/)
- [EPAC — GitHub Actions](https://azure.github.io/enterprise-azure-policy-as-code/ci-cd-github-actions/)
- [EPAC — Branching Flows](https://azure.github.io/enterprise-azure-policy-as-code/ci-cd-branching-flows/)
- [Microsoft Learn — OIDC from GitHub Actions to Azure](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect)
