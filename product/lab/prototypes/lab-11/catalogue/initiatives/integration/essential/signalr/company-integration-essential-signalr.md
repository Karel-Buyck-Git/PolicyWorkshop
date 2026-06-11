# Company Integration Essential — SignalR

## Tier rationale

**Essential** — Baseline hygiene for SignalR: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-integration-essential-signalr.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-integration-essential-signalr.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-integration-essential-signalr.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-integration-essential-signalr.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure SignalR Service should enable diagnostic logs | d9f1f9a9-8795-49f9-9e7b-e11db14caeb2 |  | Audit enabling of diagnostic logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | SignalR | Integration | 1.0.0 | BuiltIn | Essential |
| 2 | Azure SignalR Service should have local authentication methods disabled | f70eecba-335d-4bbc-81d5-5b17b03d498f |  | Disabling local authentication methods improves security by ensuring that Azure SignalR Service exclusively require Azure Active Directory identities for authentication. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | SignalR | Integration | 1.0.0 | BuiltIn | Essential |
| 3 | Configure Azure SignalR Service to disable local authentication | 702133e5-5ec5-4f90-9638-c78e22f13b39 |  | Disable local authentication methods so that your Azure SignalR Service exclusively requires Azure Active Directory identities for authentication. | No | Yes | Modify, Disabled | Modify | Modify | Modify | SignalR | Integration | 1.0.0 | BuiltIn | Essential |
