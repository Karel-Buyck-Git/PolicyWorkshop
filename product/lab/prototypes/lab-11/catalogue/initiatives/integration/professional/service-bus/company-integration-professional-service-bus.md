# Company Integration Professional — Service Bus

## Tier rationale

**Professional** — Active security posture for Service Bus: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-integration-professional-service-bus.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-integration-professional-service-bus.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-integration-professional-service-bus.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-integration-professional-service-bus.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Service Bus namespaces should use private link | 1c06e275-d63d-4540-b761-71f364c2111d |  | Azure Private Link lets you connect your virtual network to Azure services without a public IP address at the source or destination. The Private Link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to Service Bus namespaces, data leakage risks are reduced. Learn more at: https://docs.microsoft.com/azure/service-bus-messaging/private-link-service. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Service Bus | Integration | 1.0.0 | BuiltIn | Professional |
| 2 | Configure Service Bus namespaces to use private DNS zones | f0fcf93c-c063-4071-9668-c47474bd3564 |  | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to Service Bus namespaces. Learn more at: https://docs.microsoft.com/azure/service-bus-messaging/private-link-service. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Service Bus | Integration | 1.0.0 | BuiltIn | Professional |
| 3 | Configure Service Bus namespaces with private endpoints | 7d890f7f-100c-473d-baa1-2777e2266535 |  | Private endpoints connect your virtual network to Azure services without a public IP address at the source or destination. By mapping private endpoints to Service Bus namespaces, you can reduce data leakage risks. Learn more at: https://docs.microsoft.com/azure/service-bus-messaging/private-link-service. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Service Bus | Integration | 1.0.0 | BuiltIn | Professional |
| 4 | Service Bus Namespaces should disable public network access | cbd11fd3-3002-4907-b6c8-579f0e700e13 |  | Azure Service Bus should have public network access disabled. Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can limit exposure of your resources by creating private endpoints instead. Learn more at: https://docs.microsoft.com/azure/service-bus-messaging/private-link-service | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Service Bus | Integration | 1.1.0 | BuiltIn | Professional |
