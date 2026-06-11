# Company Data Professional — Azure Databricks

## Tier rationale

**Professional** — Active security posture for Azure Databricks: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-data-professional-azure-databricks.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-data-professional-azure-databricks.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-data-professional-azure-databricks.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-data-professional-azure-databricks.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Databricks Clusters should disable public IP | 51c1490f-3319-459c-bbbc-7f391bbed753 |  | Disabling public IP of clusters in Azure Databricks Workspaces improves security by ensuring that the clusters aren't exposed on the public internet. Learn more at: https://learn.microsoft.com/azure/databricks/security/secure-cluster-connectivity. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Databricks | Data | 1.0.1 | BuiltIn | Professional |
| 2 | Azure Databricks Workspaces should be in a virtual network | 9c25c9e4-ee12-4882-afd2-11fb9d87893f |  | Azure Virtual Networks provide enhanced security and isolation for your Azure Databricks Workspaces, as well as subnets, access control policies, and other features to further restrict access. Learn more at: https://docs.microsoft.com/azure/databricks/administration-guide/cloud-configurations/azure/vnet-inject. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Databricks | Data | 1.0.2 | BuiltIn | Professional |
| 3 | Azure Databricks Workspaces should disable public network access | 0e7849de-b939-4c50-ab48-fc6b0f5eeba2 |  | Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can control exposure of your resources by creating private endpoints instead. Learn more at: https://learn.microsoft.com/azure/databricks/administration-guide/cloud-configurations/azure/private-link. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Databricks | Data | 1.0.1 | BuiltIn | Professional |
