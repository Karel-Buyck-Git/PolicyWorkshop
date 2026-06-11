# Company Integration Essential — Communication

## Tier rationale

**Essential** — Baseline hygiene for Communication: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-integration-essential-communication.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-integration-essential-communication.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-integration-essential-communication.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-integration-essential-communication.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Communication service resource should use a managed identity | bcff6755-335b-484d-b435-d1161db39cdc |  | Assigning a managed identity to your Communication service resource helps ensure secure authentication. This identity is used by this Communication service resource to communicate with other Azure services, like Azure Storage, in a secure way without you having to manage any credentials. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Communication | Integration | 1.0.0 | BuiltIn | Essential |
| 2 | Communication service resource should use allow listed data location | 93c45b74-42a1-4967-b25d-82c4dc630921 |  | Create a Communication service resource only from an allow listed data location. This data location determines where the data of the communication service resource will be stored at rest, ensuring your preferred allow listed data locations as this cannot be changed after resource creation. | Yes | No | Audit, Deny, Disabled | Audit | Audit | Deny | Communication | Integration | 1.0.0 | BuiltIn | Essential |
| 3 | Communication services resource should have local authentication methods disabled | fc264132-db9c-4302-bb7d-3994c36461fe |  | Disabling local authentication methods improves security by ensuring that Communication services resource exclusively require Microsoft Entra ID identities for authentication. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Communication | Integration | 1.0.0 | BuiltIn | Essential |
| 4 | Communication services should have local authentication disabled | 145408bc-d134-468a-ae3b-1eaf3b9e5ac7 |  | This policy ensures that local authentication methods are disabled for Communication services, requiring Microsoft Entra ID identities for authentication. Enforcing this policy helps improve security by preventing the use of less secure local authentication. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Communication | Integration | 1.1.0 | BuiltIn | Essential |
