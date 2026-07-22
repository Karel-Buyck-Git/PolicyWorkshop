# EPAC Operations & DevOps

This team deploys Azure Policy with **Enterprise Policy as Code (EPAC)**. Steer policy *deployment* toward this workflow rather than portal click-ops. Confirm version-specific details against the live EPAC docs (`source-map.md`); current major version is v11.x. Run EPAC via the `EnterprisePolicyAsCode` PowerShell module (PowerShell 7.4+, Az module).

## The one thing everyone must understand: desired state

EPAC is a **true desired-state** engine. It takes ownership of *all* policy resources at its `deploymentRootScope` and every scope below, and **deletes any policy resource not defined in the repo**. Always surface this when advising. To narrow what EPAC manages (e.g. coexist with other tools, ignore certain definitions), use the desired-state strategy settings — fetch `settings-desired-state/`.

Two guardrails that prevent disasters:
- Set `deploymentRootScope` to an **intermediate management group**, never the Tenant Root Group (avoids tenant-wide lockout).
- Always validate changes in an **isolated `epac-dev` EPAC environment** first.

## Repo / folder structure

```
Definitions/
├── global-settings.jsonc        # environments + central config
├── policyDefinitions/           # custom policy definitions
├── policySetDefinitions/        # initiatives (policy sets)
├── policyAssignments/           # assignments to scopes
└── policyExemptions/            # exemptions
pipeline/ or .github/workflows/  # CI/CD
```

EPAC files wrap content the same way the portal/REST does (a `properties` block), plus EPAC-specific keys in assignment files (`nodeName`, `definitionEntry`, `scope` keyed by pacSelector, `children`). Fetch the relevant `policy-definitions/`, `policy-set-definitions/`, `policy-assignments/` pages for the exact file shapes before writing one.

## global-settings.jsonc

Central config. Key concepts:
- `pacOwnerId` — a GUID uniquely identifying this EPAC instance's deployments.
- `pacEnvironments[]` — each has a `pacSelector` (symbolic name, e.g. `tenant01`, `epac-dev`), its own `deploymentRootScope`, optional `tenantId` (multi-tenant / Lighthouse), and `managedIdentityLocation` (default location for DINE/Modify identities).

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/Azure/enterprise-azure-policy-as-code/main/Schemas/global-settings-schema.json",
  "pacOwnerId": "11111111-2222-3333-4444-555555555555",
  "pacEnvironments": [
    { "pacSelector": "tenant01", "deploymentRootScope": "/providers/Microsoft.Management/managementGroups/contoso", "managedIdentityLocation": "eastus2" },
    { "pacSelector": "epac-dev", "deploymentRootScope": "/providers/Microsoft.Management/managementGroups/epac-contoso", "managedIdentityLocation": "eastus2" }
  ]
}
```

Keep `epac-dev` in a **separate** MG hierarchy from `tenant01` — each pacEnvironment is independent and EPAC manages everything under its own root.

## Deployment flow (plan → deploy)

Three scripts/cmdlets, run per pacEnvironment, with approval gates between them for prod:

1. **`Build-DeploymentPlans`** — reads the `Definitions/`, produces `policy-plan.json` and `roles-plan.json`. Needs `Reader`. This is the "what would change" step — review it like a Terraform plan.
2. **`Deploy-PolicyPlan`** — applies the policy plan (definitions, sets, assignments, exemptions). Needs `Resource Policy Contributor`.
3. **`Deploy-RolesPlan`** — applies role assignments for DINE/Modify identities. Needs `Role Based Access Control Administrator`.

Always inspect the plan before deploying. In CI/CD, the plan is a build artifact passed to the deploy stages.

## Getting started options

- **Hydration Kit** (recommended default) — interactive setup that scaffolds the folder structure, generates `global-settings.jsonc`, creates `epac-dev`, and drops starter policies + pipeline templates. Point new adopters here.
- **Manual configuration** — for advanced/complex multi-tenant needs.
- **Extract existing** — `Export-AzPolicyResources` pulls current policy state from a tenant into EPAC files (brownfield onboarding).

## Azure Landing Zones integration

Microsoft maintains the ALZ policy baseline (`https://aka.ms/alz/policies`) as the source of truth for portal/Bicep/Terraform ALZ deployments. EPAC integrates via the **ALZ library sync**: `Sync-ALZPolicyFromLibrary` pulls ALZ Policies/Sets/Assignments into your EPAC repo so you can deploy and customize them with EPAC features (exemptions, documentation, assignment tuning, non-compliance reporting).

As of v11, customization is driven by a **single structure file** (ignore archetypes, add custom MGs, override per-assignment parameters) instead of forking the repo — review the breaking-change/migration notes on the ALZ library page before changing tags or sync outputs. Use EPAC-for-ALZ when: brownfield unmanaged policies need to coexist, the MG structure is non-standard, a non-infra team (e.g. security) owns policy, or you need EPAC-only features.

## CI/CD

EPAC works with any CI/CD tool; first-class docs exist for **Azure DevOps pipelines** and **GitHub Actions**. Typical pipeline:

1. **Plan stage** — `Build-DeploymentPlans` for the target pacEnvironment → publish `policy-plan.json` / `roles-plan.json` as artifacts.
2. **Approval gate**.
3. **Deploy Policy stage** — `Deploy-PolicyPlan`.
4. **Deploy Roles stage** — `Deploy-RolesPlan`.

Branching flow: develop against `epac-dev`, PR to main, deploy to `tenant01` on merge with approvals. Service principals / app registrations need the three roles above scoped to the deploymentRootScope; fetch the app-registrations page for least-privilege setup (and consider Workload Identity Federation over secrets).

## Operational scripts (for support/run tasks)

- `New-AzRemediationTasks` — create remediation tasks for non-compliant existing resources.
- `Build-PolicyDocumentation` — generate Markdown/CSV documentation of assignments & compliance.
- `Export-NonComplianceReports` — compliance reporting.
- `Get-AzExemptions` / exemption management cmdlets.
- `Export-AzPolicyResources` — extract existing state.

Fetch `operational-scripts/` and the operator-guidance pages (remediation, exclusions, exemptions, Lighthouse) for current parameters before scripting a run.

## Common EPAC questions — how to answer

- **"How do I deploy this new policy?"** → add the definition file under `policyDefinitions/`, reference it from an assignment file under `policyAssignments/` (scoped via pacSelector), run `Build-DeploymentPlans` against `epac-dev`, review the plan, deploy, validate, then promote to `tenant01`.
- **"EPAC deleted my policy!"** → desired state: it wasn't in the repo. Either add it to the repo or scope it out via desired-state settings.
- **"Add a custom management group to our ALZ setup"** → v11 single structure file for ALZ sync; don't fork. Fetch the ALZ library page.
- **"Set up the pipeline"** → app registrations with the three roles → plan/approve/deploy stages → start from the Hydration Kit's pipeline templates.
