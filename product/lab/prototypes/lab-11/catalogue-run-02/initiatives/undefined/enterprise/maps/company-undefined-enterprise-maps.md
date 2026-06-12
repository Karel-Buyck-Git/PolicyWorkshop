# Company undefined Enterprise — Maps

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Maps: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-undefined-enterprise-maps.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-undefined-enterprise-maps.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-undefined-enterprise-maps.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-undefined-enterprise-maps.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Maps Accounts should use private link. | cb26889c-214c-4b29-811e-6f2109a1959f |  | Azure Private Link lets you connect your virtual networks to Azure services without a public IP address at the source or destination. The Private Link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to Maps Account, you can reduce data leakage risks. | No | No | Audit, Disabled | Audit | Audit | Audit | Maps | undefined | 1.0.0 | BuiltIn | Enterprise |
| 2 | Configure private DNS zones for private endpoints that connect to Azure Maps Accounts. | a58f2efa-faf4-434a-8fe9-2dca18adb5f5 |  | Private DNS records allow private connections to private endpoints. Private endpoint connections allow secure communication by enabling private connectivity to your Azure Maps Account without a need for public IP addresses at the source or destination. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Maps | undefined | 1.0.0 | BuiltIn | Enterprise |
| 3 | Public network access should be disabled for Azure Maps Accounts. | a46d869a-f759-4404-8289-7737e7a1f79e |  | Disabling public network access on a Maps Account improves security by ensuring your Maps Account can only be accessed from a private endpoint. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Maps | undefined | 1.0.0 | BuiltIn | Enterprise |
