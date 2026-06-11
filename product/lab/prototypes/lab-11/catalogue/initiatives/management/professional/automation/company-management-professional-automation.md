# Company Management Professional — Automation

## Tier rationale

**Professional** — Active security posture for Automation: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-management-professional-automation.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-management-professional-automation.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-management-professional-automation.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-management-professional-automation.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Automation accounts should disable public network access | 955a914f-bf86-4f0e-acd5-e0766b0efcb6 |  | Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can limit exposure of your Automation account resources by creating private endpoints instead. Learn more at: https://docs.microsoft.com/azure/automation/how-to/private-link-security. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Automation | Management | 1.0.0 | BuiltIn | Professional |
| 2 | Configure Azure Automation accounts to disable public network access | 23b36a7c-9d26-4288-a8fd-c1d2fa284d8c |  | Disable public network access for Azure Automation account so that it isn't accessible over the public internet. This configuration helps protect them against data leakage risks. You can limit exposure of the your Automation account resources by creating private endpoints instead. Learn more at: https://aka.ms/privateendpoints. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Automation | Management | 1.0.0 | BuiltIn | Professional |
