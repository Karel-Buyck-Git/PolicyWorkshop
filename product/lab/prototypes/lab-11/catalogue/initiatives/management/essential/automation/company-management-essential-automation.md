# Company Management Essential — Automation

## Tier rationale

**Essential** — Baseline hygiene for Automation: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-management-essential-automation.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-management-essential-automation.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-management-essential-automation.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-management-essential-automation.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Automation Account should have Managed Identity | dea83a72-443c-4292-83d5-54a2f98749c0 |  | Use Managed Identities as the recommended method for authenticating with Azure resources from the runbooks. Managed identity for authentication is more secure and eliminates the management overhead associated with using RunAs Account in your runbook code . | No | No | Audit, Disabled | Audit | Audit | Audit | Automation | Management | 1.0.0 | BuiltIn | Essential |
| 2 | Automation account variables should be encrypted | 3657f5a0-770e-44a3-b44e-9431ba1e9735 |  | It is important to enable encryption of Automation account variable assets when storing sensitive data | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Automation | Management | 1.1.0 | BuiltIn | Essential |
| 3 | Azure Automation account should have local authentication method disabled | 48c5f1cb-14ad-4797-8e3b-f78ab3f8d700 |  | Disabling local authentication methods improves security by ensuring that Azure Automation accounts exclusively require Azure Active Directory identities for authentication. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Automation | Management | 1.0.0 | BuiltIn | Essential |
| 4 | Configure Azure Automation account to disable local authentication | 30d1d58e-8f96-47a5-8564-499a3f3cca81 |  | Disable local authentication methods so that your Azure Automation accounts exclusively require Azure Active Directory identities for authentication. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Automation | Management | 1.0.0 | BuiltIn | Essential |
