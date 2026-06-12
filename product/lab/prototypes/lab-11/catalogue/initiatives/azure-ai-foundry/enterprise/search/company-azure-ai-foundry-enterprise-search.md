# Company Azure AI Foundry Enterprise — Search

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Search: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers diagnostic settings streaming to Log Analytics / Event Hub / Sentinel and customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-azure-ai-foundry-enterprise-search.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-azure-ai-foundry-enterprise-search.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-azure-ai-foundry-enterprise-search.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-azure-ai-foundry-enterprise-search.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure AI Search services should use customer-managed keys to encrypt data at rest | 76a56461-9dc0-40f0-82f5-2453283afa2f |  | Enabling encryption at rest using a customer-managed key on your Azure AI Search services provides additional control over the key used to encrypt data at rest. This feature is often applicable to customers with special compliance requirements to manage data encryption keys using a key vault. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Search | Azure AI Foundry | 2.1.0 | BuiltIn | Enterprise |
| 2 | Configure Azure AI Search services to enforce customer-managed keys to encrypt data at rest | 356da939-f20a-4bb9-86f8-5db445b0e354 |  | Enabling encryption at rest using a customer-managed key on your Azure AI Search services provides additional control over the key used to encrypt data at rest. This feature is often applicable to customers with special compliance requirements to manage data encryption keys using a key vault. | No | No | Deny, Disabled | Deny | Deny | Deny | Search | Azure AI Foundry | 1.0.1 | BuiltIn | Enterprise |
| 3 | Resource logs in Search services should be enabled | b4330a05-a843-4bc8-bf9a-cacce50c67f4 |  | Audit enabling of resource logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Search | Azure AI Foundry | 5.0.0 | BuiltIn | Enterprise |
