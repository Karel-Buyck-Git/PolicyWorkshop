# Company Storage Professional — ElasticSan

## Tier rationale

**Professional** — Active security posture for ElasticSan: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-storage-professional-elasticsan.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-storage-professional-elasticsan.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-storage-professional-elasticsan.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-storage-professional-elasticsan.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ElasticSan should disable public network access | 6a92fe1f-0b86-44ae-843d-2db3d2b571ae |  | Disable public network access for your ElasticSan so that it's not accessible over the public internet. This can reduce data leakage risks. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | ElasticSan | Storage | 1.0.0 | BuiltIn | Professional |
| 2 | ElasticSan Volume Group should use private endpoints | 1abc5157-29f8-4dbd-b28e-ff99526cb8b7 |  | Private endpoints lets administrator connect virtual networks to Azure services without a public IP address at the source or destination. By mapping private endpoints to volume group, administrator can reduce data leakage risks | No | No | Audit, Disabled | Audit | Audit | Audit | ElasticSan | Storage | 1.0.0 | BuiltIn | Professional |
