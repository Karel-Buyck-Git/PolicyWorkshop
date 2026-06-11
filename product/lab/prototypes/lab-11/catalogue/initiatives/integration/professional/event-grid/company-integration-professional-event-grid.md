# Company Integration Professional — Event Grid

## Tier rationale

**Professional** — Active security posture for Event Grid: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-integration-professional-event-grid.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-integration-professional-event-grid.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-integration-professional-event-grid.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-integration-professional-event-grid.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Event Grid domains should disable public network access | f8f774be-6aee-492a-9e29-486ef81f3a68 |  | Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can limit exposure of your resources by creating private endpoints instead. Learn more at: https://aka.ms/privateendpoints. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Event Grid | Integration | 1.0.0 | BuiltIn | Professional |
| 2 | Azure Event Grid namespaces should disable public network access | 67dcad1a-ec60-45df-8fd0-14c9d29eeaa2 |  | Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can limit exposure of your resources by creating private endpoints instead. Learn more at: https://aka.ms/aeg-ns-privateendpoints. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Event Grid | Integration | 1.0.0 | BuiltIn | Professional |
| 3 | Azure Event Grid topics should disable public network access | 1adadefe-5f21-44f7-b931-a59b54ccdb45 |  | Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can limit exposure of your resources by creating private endpoints instead. Learn more at: https://aka.ms/privateendpoints. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Event Grid | Integration | 1.0.0 | BuiltIn | Professional |
| 4 | Modify - Configure Azure Event Grid domains to disable public network access | 898e9824-104c-4965-8e0e-5197588fa5d4 |  | Disable public network access for Azure Event Grid resource so that it isn't accessible over the public internet. This will help protect them against data leakage risks. You can limit exposure of the your resources by creating private endpoints instead. Learn more at: https://aka.ms/privateendpoints. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Event Grid | Integration | 1.0.0 | BuiltIn | Professional |
| 5 | Modify - Configure Azure Event Grid topics to disable public network access | 36ea4b4b-0f7f-4a54-89fa-ab18f555a172 |  | Disable public network access for Azure Event Grid resource so that it isn't accessible over the public internet. This will help protect them against data leakage risks. You can limit exposure of the your resources by creating private endpoints instead. Learn more at: https://aka.ms/privateendpoints. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Event Grid | Integration | 1.0.0 | BuiltIn | Professional |
