# Company Monitoring Essential — Managed Grafana

## Tier rationale

**Essential** — Baseline hygiene for Managed Grafana: the non-negotiable controls every deployment should enforce from day one. This tier protects against credential theft, unencrypted data exposure, and accidental data loss for Managed Grafana workloads. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-monitoring-essential-managed-grafana.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-monitoring-essential-managed-grafana.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-monitoring-essential-managed-grafana.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-monitoring-essential-managed-grafana.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Managed Grafana workspaces should disable email settings | b6752a42-6fc3-46cb-8a15-33aa109407b1 |  | Disables SMTP settings configuration of email contact point for alerting in Grafana workspace. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Essential |
| 2 | Azure Managed Grafana workspaces should disable Grafana Enterprise upgrade | a08f2347-fe9c-482b-a944-f6a0e05124c0 |  | Disables Grafana Enterprise upgrade in Grafana workspace. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Managed Grafana | Monitoring | 1.1.0 | BuiltIn | Essential |
| 3 | Azure Managed Grafana workspaces should disable service account | 0656cf40-485c-427b-b992-703a4ecf4f88 |  | Disables API keys and service account for automated workloads in Grafana workspace. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Essential |
| 4 | Configure Azure Managed Grafana workspaces to disable email settings | f757d603-5178-4168-ac45-5223f681023f |  | Disable SMTP settings configuration of email contact point for alerting in Grafana workspace. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Essential |
| 5 | Configure Azure Managed Grafana workspaces to disable service account | cc4dfa24-c7df-47e4-80ff-3728adb3f9a0 |  | Disable API keys and service account for automated workloads in Grafana workspace. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Essential |
