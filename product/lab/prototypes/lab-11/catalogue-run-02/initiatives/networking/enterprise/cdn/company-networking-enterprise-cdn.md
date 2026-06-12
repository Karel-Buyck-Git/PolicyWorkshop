# Company Networking Enterprise — CDN

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for CDN: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-networking-enterprise-cdn.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-networking-enterprise-cdn.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-networking-enterprise-cdn.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-networking-enterprise-cdn.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Front Door profiles should use Premium tier that supports managed WAF rules and private link | dfc212af-17ea-423a-9dcb-91e2cb2caa6b |  | Azure Front Door Premium supports Azure managed WAF rules and private link to supported Azure origins. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | CDN | Networking | 1.0.0 | BuiltIn | Enterprise |
| 2 | Secure private connectivity between Azure Front Door Premium and Azure Storage Blob, or Azure App Service | daba2cce-8326-4af3-b049-81a362da024d |  | Private link ensures private connectivity between AFD Premium and Azure Storage Blob or Azure App Service over the Azure backbone network, without the Azure Storage Blob or the Azure App Service being publicly exposed to the internet. | No | No | Audit, Disabled | Audit | Audit | Audit | CDN | Networking | 1.0.0 | BuiltIn | Enterprise |
