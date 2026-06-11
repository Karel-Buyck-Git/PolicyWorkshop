# Company Compute Enterprise — Desktop Virtualization

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Azure Virtual Desktop: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-compute-enterprise-desktop-virtualization.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-compute-enterprise-desktop-virtualization.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-compute-enterprise-desktop-virtualization.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-compute-enterprise-desktop-virtualization.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Virtual Desktop service should use private link | ca950cd7-02f7-422e-8c23-91ff40f169c1 |  | Using Azure Private Link with your Azure Virtual Desktop resources can improve security and keep your data safe. Learn more about private links at: https://aka.ms/avdprivatelink. | No | No | Audit, Disabled | Audit | Audit | Audit | Desktop Virtualization | Compute | 1.0.0 | BuiltIn | Enterprise |
| 2 | Configure Azure Virtual Desktop hostpool resources to use private DNS zones | 9427df23-0f42-4e1e-bf99-a6133d841c4a |  | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to Azure Virtual Desktop resources. Learn more at: https://aka.ms/privatednszone. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Desktop Virtualization | Compute | 1.0.0 | BuiltIn | Enterprise |
| 3 | Configure Azure Virtual Desktop hostpools with private endpoints | 7b331e6b-6096-4395-a754-758a64505f19 |  | Private endpoints connect your virtual network to Azure services without a public IP address at the source or destination. By mapping private endpoints to your Azure Virtual Desktop resources, you can improve security and keep your data safe. Learn more at: https://aka.ms/avdprivatelink. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Desktop Virtualization | Compute | 1.0.0 | BuiltIn | Enterprise |
| 4 | Configure Azure Virtual Desktop workspace resources to use private DNS zones | 34804460-d88b-4922-a7ca-537165e060ed |  | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to Azure Virtual Desktop resources. Learn more at: https://aka.ms/privatednszone. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Desktop Virtualization | Compute | 1.0.0 | BuiltIn | Enterprise |
| 5 | Configure Azure Virtual Desktop workspaces with private endpoints | 02aa841c-42e8-492f-a43d-1f2c67e58d41 |  | Private endpoints connect your virtual network to Azure services without a public IP address at the source or destination. By mapping private endpoints to your Azure Virtual Desktop resources, you can improve security and keep your data safe. Learn more at: https://aka.ms/avdprivatelink. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Desktop Virtualization | Compute | 1.0.0 | BuiltIn | Enterprise |
