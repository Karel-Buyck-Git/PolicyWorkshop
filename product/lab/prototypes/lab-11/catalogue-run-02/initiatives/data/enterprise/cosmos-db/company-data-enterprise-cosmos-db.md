# Company Data Enterprise — Cosmos DB

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Cosmos DB: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface, customer-managed keys (CMK / BYOK) for cryptographic sovereignty, and direct mapping to regulatory framework controls. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-data-enterprise-cosmos-db.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-data-enterprise-cosmos-db.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-data-enterprise-cosmos-db.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-data-enterprise-cosmos-db.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Cosmos DB accounts should use customer-managed keys to encrypt data at rest | 1f905d99-2ab7-462c-a6b0-f709acca6c8f |  | Use customer-managed keys to manage the encryption at rest of your Azure Cosmos DB. By default, the data is encrypted at rest with service-managed keys, but customer-managed keys are commonly required to meet regulatory compliance standards. Customer-managed keys enable the data to be encrypted with an Azure Key Vault key created and owned by you. You have full control and responsibility for the key lifecycle, including rotation and management. Learn more at https://aka.ms/cosmosdb-cmk. | No | No | Audit, Audit, Deny, Deny, Disabled, Disabled | Audit | Audit | Deny | Cosmos DB | Data | 1.1.0 | BuiltIn | Enterprise |
| 2 | Configure CosmosDB accounts to use private DNS zones | a63cc0bd-cda4-4178-b705-37dc439d3e0f |  | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to CosmosDB account. Learn more at: https://aka.ms/privatednszone. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Cosmos DB | Data | 2.0.0 | BuiltIn | Enterprise |
| 3 | Configure CosmosDB accounts with private endpoints | b609e813-3156-4079-91fa-a8494c1471c4 |  | Private endpoints connect your virtual network to Azure services without a public IP address at the source or destination. By mapping private endpoints to your CosmosDB account, you can reduce data leakage risks. Learn more about private links at: https://docs.microsoft.com/azure/cosmos-db/how-to-configure-private-endpoints. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Cosmos DB | Data | 1.0.0 | BuiltIn | Enterprise |
| 4 | CosmosDB accounts should use private link | 58440f8a-10c5-4151-bdce-dfbaad4a20b7 |  | Azure Private Link lets you connect your virtual network to Azure services without a public IP address at the source or destination. The Private Link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to your CosmosDB account, data leakage risks are reduced. Learn more about private links at: https://docs.microsoft.com/azure/cosmos-db/how-to-configure-private-endpoints. | No | No | Audit, Disabled | Audit | Audit | Audit | Cosmos DB | Data | 1.0.0 | BuiltIn | Enterprise |
