# Company Data Professional — Data Factory

## Tier rationale

**Professional** — Active security posture for Data Factory: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-data-professional-data-factory.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-data-professional-data-factory.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-data-professional-data-factory.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-data-professional-data-factory.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Data Factories to disable public network access | 08b1442b-7789-4130-8506-4f99a97226a7 |  | Disable public network access for your Data Factory so that it is not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://docs.microsoft.com/azure/data-factory/data-factory-private-link. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Data Factory | Data | 1.0.0 | BuiltIn | Professional |
| 2 | SQL Server Integration Services integration runtimes on Azure Data Factory should be joined to a virtual network | 0088bc63-6dee-4a9c-9d29-91cfdc848952 |  | Azure Virtual Network deployment provides enhanced security and isolation for your SQL Server Integration Services integration runtimes on Azure Data Factory, as well as subnets, access control policies, and other features to further restrict access. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Data Factory | Data | 2.3.0 | BuiltIn | Professional |
