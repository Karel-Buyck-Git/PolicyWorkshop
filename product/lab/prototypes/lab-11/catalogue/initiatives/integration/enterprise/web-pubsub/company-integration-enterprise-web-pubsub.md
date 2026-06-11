# Company Integration Enterprise — Web PubSub

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Web PubSub: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-integration-enterprise-web-pubsub.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-integration-enterprise-web-pubsub.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-integration-enterprise-web-pubsub.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-integration-enterprise-web-pubsub.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Web PubSub Service should use a SKU that supports private link | 82909236-25f3-46a6-841c-fe1020f95ae1 |  | With supported SKU, Azure Private Link lets you connect your virtual network to Azure services without a public IP address at the source or destination. The Private Link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to Azure Web PubSub service, you can reduce data leakage risks. Learn more about private links at: https://aka.ms/awps/privatelink. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Web PubSub | Integration | 1.0.0 | BuiltIn | Enterprise |
| 2 | Azure Web PubSub Service should use private link | eb907f70-7514-460d-92b3-a5ae93b4f917 |  | Azure Private Link lets you connect your virtual networks to Azure services without a public IP address at the source or destination. The private link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to your Azure Web PubSub Service, you can reduce data leakage risks. Learn more about private links at: https://aka.ms/awps/privatelink. | No | No | Audit, Disabled | Audit | Audit | Audit | Web PubSub | Integration | 1.0.0 | BuiltIn | Enterprise |
| 3 | Configure Azure Web PubSub Service to use private DNS zones | 0b026355-49cb-467b-8ac4-f777874e175a |  | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to Azure Web PubSub service. Learn more at: https://aka.ms/awps/privatelink. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Web PubSub | Integration | 1.0.0 | BuiltIn | Enterprise |
| 4 | Configure Azure Web PubSub Service with private endpoints | 1b9c0b58-fc7b-42c8-8010-cdfa1d1b8544 |  | Private endpoints connect your virtual networks to Azure services without a public IP address at the source or destination. By mapping private endpoints to Azure Web PubSub service, you can reduce data leakage risks. Learn more about private links at: https://aka.ms/awps/privatelink. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Web PubSub | Integration | 1.0.0 | BuiltIn | Enterprise |
