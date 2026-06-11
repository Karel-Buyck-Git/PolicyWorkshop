# Company Azure AI Foundry Essential — Search

## Tier rationale

**Essential** — Baseline hygiene for Search: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-azure-ai-foundry-essential-search.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-azure-ai-foundry-essential-search.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-azure-ai-foundry-essential-search.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-azure-ai-foundry-essential-search.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure AI Search services should have local authentication methods disabled | 6300012e-e9a4-4649-b41f-a85f5c43be91 |  | Disabling local authentication methods improves security by ensuring that Azure AI Search services exclusively require Azure Active Directory identities for authentication. Learn more at: https://aka.ms/azure-cognitive-search/rbac. Note that while the disable local authentication parameter is still in preview, the deny effect for this policy may result in limited Azure AI Search portal functionality since some features of the Portal use the GA API which does not support the parameter. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Search | Azure AI Foundry | 1.0.1 | BuiltIn | Essential |
| 2 | Configure Azure AI Search services to disable local authentication | 4eb216f2-9dba-4979-86e6-5d7e63ce3b75 |  | Disable local authentication methods so that your Azure AI Search services exclusively require Azure Active Directory identities for authentication. Learn more at: https://aka.ms/azure-cognitive-search/rbac. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Search | Azure AI Foundry | 2.0.0 | BuiltIn | Essential |
