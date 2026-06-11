# Company Integration Professional — Web PubSub

## Tier rationale

**Professional** — Active security posture for Web PubSub: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-integration-professional-web-pubsub.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-integration-professional-web-pubsub.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-integration-professional-web-pubsub.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-integration-professional-web-pubsub.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Web PubSub Service should disable public network access | bf45113f-264e-4a87-88f9-29ac8a0aca6a |  | Disabling public network access improves security by ensuring that Azure Web PubSub service isn't exposed on the public internet. Creating private endpoints can limit exposure of Azure Web PubSub service. Learn more at: https://aka.ms/awps/networkacls. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Web PubSub | Integration | 1.0.0 | BuiltIn | Professional |
| 2 | Configure Azure Web PubSub Service to disable public network access | 5b1213e4-06e4-4ccc-81de-4201f2f7131a |  | Disable public network access for your Azure Web PubSub resource so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://aka.ms/awps/networkacls. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Web PubSub | Integration | 1.0.0 | BuiltIn | Professional |
