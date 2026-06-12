# Company Compute Professional — Compute

## Tier rationale

**Professional** — Active security posture for Compute: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-compute-professional-compute.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-compute-professional-compute.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-compute-professional-compute.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-compute-professional-compute.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure disk access resources to use private DNS zones | bc05b96c-0b36-4ca9-82f0-5c53f96ce05a |  | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to a managed disk. Learn more at: https://aka.ms/disksprivatelinksdoc. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Compute | Compute | 1.0.0 | BuiltIn | Professional |
| 2 | Configure disk access resources with private endpoints | 582bd7a6-a5f6-4dc6-b9dc-9cb81fe0d4c5 |  | Private endpoints connect your virtual networks to Azure services without a public IP address at the source or destination. By mapping private endpoints to disk access resources, you can reduce data leakage risks. Learn more about private links at: https://aka.ms/disksprivatelinksdoc. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Compute | Compute | 1.0.0 | BuiltIn | Professional |
| 3 | Configure managed disks to disable public network access | 8426280e-b5be-43d9-979e-653d12a08638 |  | Disable public network access for your managed disk resource so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://aka.ms/disksprivatelinksdoc. | Yes | Yes | Modify, Disabled | Modify | Modify | Modify | Compute | Compute | 2.0.0 | BuiltIn | Professional |
| 4 | Disk access resources should use private link | f39f5f49-4abf-44de-8c70-0756997bfb51 |  | Azure Private Link lets you connect your virtual network to Azure services without a public IP address at the source or destination. The Private Link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to diskAccesses, data leakage risks are reduced. Learn more about private links at: https://aka.ms/disksprivatelinksdoc. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Compute | Compute | 1.0.0 | BuiltIn | Professional |
| 5 | Managed disks should disable public network access | 8405fdab-1faf-48aa-b702-999c9c172094 |  | Disabling public network access improves security by ensuring that a managed disk isn't exposed on the public internet. Creating private endpoints can limit exposure of managed disks. Learn more at: https://aka.ms/disksprivatelinksdoc. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Compute | Compute | 2.1.0 | BuiltIn | Professional |
