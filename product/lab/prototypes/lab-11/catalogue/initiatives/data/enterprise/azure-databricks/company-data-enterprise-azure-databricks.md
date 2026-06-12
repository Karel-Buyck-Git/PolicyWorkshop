# Company Data Enterprise — Azure Databricks

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Azure Databricks: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface, diagnostic settings streaming to Log Analytics / Event Hub / Sentinel, and customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-data-enterprise-azure-databricks.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-data-enterprise-azure-databricks.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-data-enterprise-azure-databricks.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-data-enterprise-azure-databricks.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Databricks workspaces should be Premium SKU that supports features like private link, customer-managed key for encryption | 2cc2c3b5-c2f8-45aa-a9e6-f90d85ae8352 |  | Only allow Databricks workspace with Premium Sku that your organization can deploy to support features like Private Link, customer-managed key for encryption. Learn more at: https://aka.ms/adbpe. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Databricks | Data | 1.0.1 | BuiltIn | Enterprise |
| 2 | Configure diagnostic settings for Azure Databricks Workspaces to Log Analytics workspace | 23057b42-ca8d-4aa0-a3dc-96a98b5b5a3d |  | Deploys the diagnostic settings for Azure Databricks Workspaces to stream resource logs to a Log Analytics Workspace when any Azure Databricks Workspace which is missing this diagnostic settings is created or updated. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Azure Databricks | Data | 1.0.1 | BuiltIn | Enterprise |
| 3 | Resource logs in Azure Databricks Workspaces should be enabled | 138ff14d-b687-4faa-a81c-898c91a87fa2 |  | Resource logs enable recreating activity trails to use for investigation purposes when a security incident occurs or when your network is compromised. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Azure Databricks | Data | 1.0.1 | BuiltIn | Enterprise |
