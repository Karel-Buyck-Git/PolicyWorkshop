# Company Data Enterprise — Stream Analytics

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Stream Analytics: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers diagnostic settings streaming to Log Analytics / Event Hub / Sentinel and customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-data-enterprise-stream-analytics.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-data-enterprise-stream-analytics.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-data-enterprise-stream-analytics.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-data-enterprise-stream-analytics.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Stream Analytics jobs should use customer-managed keys to encrypt data | 87ba29ef-1ab3-4d82-b763-87fcd4f531f7 |  | Use customer-managed keys when you want to securely store any metadata and private data assets of your Stream Analytics jobs in your storage account. This gives you total control over how your Stream Analytics data is encrypted. | No | No | Audit, Audit, Deny, Deny, Disabled, Disabled | Audit | Audit | Deny | Stream Analytics | Data | 1.1.0 | BuiltIn | Enterprise |
| 2 | Resource logs in Azure Stream Analytics should be enabled | f9be5368-9bf5-4b84-9e0a-7850da98bb46 |  | Audit enabling of resource logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Stream Analytics | Data | 5.0.0 | BuiltIn | Enterprise |
