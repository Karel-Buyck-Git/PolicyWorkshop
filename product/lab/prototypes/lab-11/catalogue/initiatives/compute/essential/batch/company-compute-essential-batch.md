# Company Compute Essential — Batch

## Tier rationale

**Essential** — Baseline hygiene for Batch: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials, TLS / HTTPS enforcement preventing in-transit interception, and encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-compute-essential-batch.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-compute-essential-batch.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-compute-essential-batch.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-compute-essential-batch.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Batch pools should have disk encryption enabled | 1760f9d4-7206-436e-a28f-d9f3a5c8a227 |  | Enabling Azure Batch disk encryption ensures that data is always encrypted at rest on your Azure Batch compute node. Learn more about disk encryption in Batch at https://docs.microsoft.com/azure/batch/disk-encryption. | No | No | Audit, Disabled, Deny | Audit | Audit | Deny | Batch | Compute | 1.0.0 | BuiltIn | Essential |
| 2 | Batch accounts should have local authentication methods disabled | 6f68b69f-05fe-49cd-b361-777ee9ca7e35 |  | Disabling local authentication methods improves security by ensuring that Batch accounts require Azure Active Directory identities exclusively for authentication. Learn more at: https://aka.ms/batch/auth. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Batch | Compute | 1.0.0 | BuiltIn | Essential |
| 3 | Configure Batch accounts to disable local authentication | 4dbc2f5c-51cf-4e38-9179-c7028eed2274 |  | Disable location authentication methods so that your Batch accounts require Azure Active Directory identities exclusively for authentication. Learn more at: https://aka.ms/batch/auth. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Batch | Compute | 1.0.0 | BuiltIn | Essential |
