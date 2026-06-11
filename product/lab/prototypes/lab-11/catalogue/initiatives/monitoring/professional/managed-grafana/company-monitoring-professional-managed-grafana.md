# Company Monitoring Professional — Managed Grafana

## Tier rationale

**Professional** — Active security posture for Managed Grafana: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-monitoring-professional-managed-grafana.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-monitoring-professional-managed-grafana.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-monitoring-professional-managed-grafana.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-monitoring-professional-managed-grafana.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Managed Grafana workspaces should disable public network access | e8775d5a-73b7-4977-a39b-833ef0114628 |  | Disabling public network access improves security by ensuring that your Azure Managed Grafana workspace isn't exposed on the public internet. Creating private endpoints can limit exposure of your workspaces. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Professional |
| 2 | Configure Azure Managed Grafana workspaces to disable public network access | 67529aa1-5285-4b1c-8e6f-5ccd861ac98e |  | Disable public network access for your Azure Managed Grafana workspace so that it's not accessible over the public internet. This can reduce data leakage risks. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Managed Grafana | Monitoring | 1.0.0 | BuiltIn | Professional |
