# Company Management Enterprise — Automation

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Automation: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface, customer-managed keys (CMK / BYOK) for cryptographic sovereignty, and direct mapping to regulatory framework controls. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-management-enterprise-automation.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-management-enterprise-automation.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-management-enterprise-automation.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-management-enterprise-automation.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Automation accounts should use customer-managed keys to encrypt data at rest | 56a5ee18-2ae6-4810-86f7-18e39ce5629b |  | Use customer-managed keys to manage the encryption at rest of your Azure Automation Accounts. By default, customer data is encrypted with service-managed keys, but customer-managed keys are commonly required to meet regulatory compliance standards. Customer-managed keys enable the data to be encrypted with an Azure Key Vault key created and owned by you. You have full control and responsibility for the key lifecycle, including rotation and management. Learn more at https://aka.ms/automation-cmk. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Automation | Management | 1.0.0 | BuiltIn | Enterprise |
| 2 | Configure Azure Automation accounts with private DNS zones | 6dd01e4f-1be1-4e80-9d0b-d109e04cb064 |  | Use private DNS zones to override the DNS resolution for a private endpoint. You need private DNS zone properly configured to connect to Azure Automation account via Azure Private Link. Learn more at: https://aka.ms/privatednszone. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Automation | Management | 1.0.0 | BuiltIn | Enterprise |
| 3 | Configure private endpoint connections on Azure Automation accounts | c0c3130e-7dda-4187-aed0-ee4a472eaa60 |  | Private endpoint connections allow secure communication by enabling private connectivity to Azure Automation accounts without a need for public IP addresses at the source or destination. Learn more about private endpoints in Azure Automation at https://docs.microsoft.com/azure/automation/how-to/private-link-security. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Automation | Management | 1.0.0 | BuiltIn | Enterprise |
| 4 | Private endpoint connections on Automation Accounts should be enabled | 0c2b3618-68a8-4034-a150-ff4abc873462 |  | Private endpoint connections allow secure communication by enabling private connectivity to Automation accounts without a need for public IP addresses at the source or destination. Learn more about private endpoints in Azure Automation at https://docs.microsoft.com/azure/automation/how-to/private-link-security | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Automation | Management | 1.0.0 | BuiltIn | Enterprise |
