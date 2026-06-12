# Company Security Enterprise — Attestation

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Attestation: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-security-enterprise-attestation.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-security-enterprise-attestation.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-security-enterprise-attestation.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-security-enterprise-attestation.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Attestation providers should disable public network access | 5e7e928c-8693-4a23-9bf3-1c77b9a8fe97 |  | To improve the security of Azure Attestation Service, ensure that it isn't exposed to the public internet and can only be accessed from a private endpoint. Disable the public network access property as described in aka.ms/azureattestation. This option disables access from any public address space outside the Azure IP range, and denies all logins that match IP or virtual network-based firewall rules. This reduces data leakage risks. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Attestation | Security | 1.0.0 | BuiltIn | Enterprise |
| 2 | Azure Attestation providers should use private endpoints | 7b256a2d-058b-41f8-bed9-3f870541c40a |  | Private endpoints provide a way to connect Azure Attestation providers to your Azure resources without sending traffic over the public internet. By preventing public access, private endpoints help protect against undesired anonymous access. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Attestation | Security | 1.0.0 | BuiltIn | Enterprise |
