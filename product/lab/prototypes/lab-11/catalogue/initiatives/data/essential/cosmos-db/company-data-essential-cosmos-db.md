# Company Data Essential — Cosmos DB

## Tier rationale

**Essential** — Baseline hygiene for Cosmos DB: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-data-essential-cosmos-db.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-data-essential-cosmos-db.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-data-essential-cosmos-db.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-data-essential-cosmos-db.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Cosmos DB accounts should not exceed the maximum number of days allowed since last account key regeneration. | 9d83ccb1-f313-46ce-9d39-a198bfdb51a0 |  | Regenerate your keys in the specified time to keep your data more protected. | No | No | Audit, Disabled | Audit | Audit | Audit | Cosmos DB | Data | 1.0.0 | BuiltIn | Essential |
| 2 | Azure Cosmos DB allowed locations | 0473574d-2d43-4217-aefe-941fcdf7e684 |  | This policy enables you to restrict the locations your organization can specify when deploying Azure Cosmos DB resources. Use to enforce your geo-compliance requirements. | Yes | No | [parameters('policyEffect')] | [parameters('policyEffect')] | [parameters('policyEffect')] | [parameters('policyEffect')] | Cosmos DB | Data | 1.1.0 | BuiltIn | Essential |
| 3 | Azure Cosmos DB key based metadata write access should be disabled | 4750c32b-89c0-46af-bfcb-2e4541a818d5 |  | This policy enables you to ensure all Azure Cosmos DB accounts disable key based metadata write access. | No | No | Append | Append | Append | Append | Cosmos DB | Data | 1.0.0 | BuiltIn | Essential |
| 4 | Azure Cosmos DB throughput should be limited | 0b7ef78e-a035-4f23-b9bd-aff122a1b1cf |  | This policy enables you to restrict the maximum throughput your organization can specify when creating Azure Cosmos DB databases and containers through the resource provider. It blocks the creation of autoscale resources. | Yes | No | Audit, Audit, Deny, Deny, Disabled, Disabled | Deny | Audit | Deny | Cosmos DB | Data | 1.1.0 | BuiltIn | Essential |
| 5 | Configure Cosmos DB database accounts to disable local authentication | dc2d41d1-4ab1-4666-a3e1-3d51c43e0049 |  | Disable local authentication methods so that your Cosmos DB database accounts exclusively require Azure Active Directory identities for authentication. Learn more at: https://docs.microsoft.com/azure/cosmos-db/how-to-setup-rbac#disable-local-auth. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Cosmos DB | Data | 1.2.0 | BuiltIn | Essential |
| 6 | Cosmos DB database accounts should have local authentication methods disabled | 5450f5bd-9c72-4390-a9c4-a7aba4edfdd2 |  | Disabling local authentication methods improves security by ensuring that Cosmos DB database accounts exclusively require Azure Active Directory identities for authentication. Learn more at: https://docs.microsoft.com/azure/cosmos-db/how-to-setup-rbac#disable-local-auth. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Cosmos DB | Data | 1.2.0 | BuiltIn | Essential |
