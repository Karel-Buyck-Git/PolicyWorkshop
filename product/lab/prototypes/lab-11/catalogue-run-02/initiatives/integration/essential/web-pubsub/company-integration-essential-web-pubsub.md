# Company Integration Essential — Web PubSub

## Tier rationale

**Essential** — Baseline hygiene for Web PubSub: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-integration-essential-web-pubsub.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-integration-essential-web-pubsub.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-integration-essential-web-pubsub.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-integration-essential-web-pubsub.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Web PubSub Service should enable diagnostic logs | ee8a7be2-e9b5-47b9-9d37-d9b141ea78a4 |  | Audit enabling of diagnostic logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Web PubSub | Integration | 1.0.0 | BuiltIn | Essential |
| 2 | Azure Web PubSub Service should have local authentication methods disabled | b66ab71c-582d-4330-adfd-ac162e78691e |  | Disabling local authentication methods improves security by ensuring that Azure Web PubSub Service exclusively require Azure Active Directory identities for authentication. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Web PubSub | Integration | 1.0.0 | BuiltIn | Essential |
| 3 | Configure Azure Web PubSub Service to disable local authentication | 17f9d984-90c8-43dd-b7a6-76cb694815c1 |  | Disable local authentication methods so that your Azure Web PubSub Service exclusively requires Azure Active Directory identities for authentication. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Web PubSub | Integration | 1.0.0 | BuiltIn | Essential |
