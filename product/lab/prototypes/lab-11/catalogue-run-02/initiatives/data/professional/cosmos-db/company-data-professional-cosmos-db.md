# Company Data Professional — Cosmos DB

## Tier rationale

**Professional** — Active security posture for Cosmos DB: controls that produce signals an operations team must act on. This tier delivers Microsoft Defender plans surfacing threat signals and network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-data-professional-cosmos-db.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-data-professional-cosmos-db.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-data-professional-cosmos-db.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-data-professional-cosmos-db.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Cosmos DB accounts should have firewall rules | 862e97cf-49fc-4a5c-9de4-40d4e2e7c8eb |  | Firewall rules should be defined on your Azure Cosmos DB accounts to prevent traffic from unauthorized sources. Accounts that have at least one IP rule defined with the virtual network filter enabled are deemed compliant. Accounts disabling public access are also deemed compliant. | No | No | Audit, Deny, Disabled | Deny | Audit | Deny | Cosmos DB | Data | 2.1.0 | BuiltIn | Professional |
| 2 | Azure Cosmos DB accounts should not allow traffic from all Azure data centers | 12339a85-a25c-4f17-9f82-4766f13f5c4c |  | Disallow the IP Firewall rule, '0.0.0.0', which allows for all traffic from any Azure data centers. Learn more at https://aka.ms/cosmosdb-firewall | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Cosmos DB | Data | 1.0.0 | BuiltIn | Professional |
| 3 | Azure Cosmos DB should disable public network access | 797b37f7-06b8-444c-b1ad-fc62867f335a |  | Disabling public network access improves security by ensuring that your CosmosDB account isn't exposed on the public internet. Creating private endpoints can limit exposure of your CosmosDB account. Learn more at: https://docs.microsoft.com/azure/cosmos-db/how-to-configure-private-endpoints#blocking-public-network-access-during-account-creation. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Cosmos DB | Data | 1.0.0 | BuiltIn | Professional |
| 4 | Configure CosmosDB accounts to disable public network access | da69ba51-aaf1-41e5-8651-607cd0b37088 |  | Disable public network access for your CosmosDB resource so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://docs.microsoft.com/azure/cosmos-db/how-to-configure-private-endpoints#blocking-public-network-access-during-account-creation. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Cosmos DB | Data | 1.0.1 | BuiltIn | Professional |
| 5 | Deploy Advanced Threat Protection for Cosmos DB Accounts | b5f04e03-92a3-4b09-9410-2cc5e5047656 |  | This policy enables Advanced Threat Protection across Cosmos DB accounts. | No | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Cosmos DB | Data | 1.0.0 | BuiltIn | Professional |
