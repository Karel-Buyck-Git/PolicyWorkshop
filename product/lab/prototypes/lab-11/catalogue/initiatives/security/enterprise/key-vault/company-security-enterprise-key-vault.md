# Company Security Enterprise — Key Vault

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Key Vault: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers diagnostic settings streaming to Log Analytics / Event Hub / Sentinel. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-security-enterprise-key-vault.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-security-enterprise-key-vault.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-security-enterprise-key-vault.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-security-enterprise-key-vault.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Deploy - Configure diagnostic settings for Azure Key Vault to Log Analytics workspace | 951af2fa-529b-416e-ab6e-066fd85ac459 |  | Deploys the diagnostic settings for Azure Key Vault to stream resource logs to a Log Analytics workspace when any Key Vault which is missing this diagnostic settings is created or updated. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Key Vault | Security | 2.0.1 | BuiltIn | Enterprise |
| 2 | Deploy - Configure diagnostic settings to an Event Hub to be enabled on Azure Key Vault Managed HSM | a6d2c800-5230-4a40-bff3-8268b4987d42 |  | Deploys the diagnostic settings for Azure Key Vault Managed HSM to stream to a regional Event Hub when any Azure Key Vault Managed HSM which is missing this diagnostic settings is created or updated. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Key Vault | Security | 1.0.0 | BuiltIn | Enterprise |
| 3 | Deploy Diagnostic Settings for Key Vault to Event Hub | ed7c8c13-51e7-49d1-8a43-8490431a0da2 |  | Deploys the diagnostic settings for Key Vault to stream to a regional Event Hub when any Key Vault which is missing this diagnostic settings is created or updated. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Key Vault | Security | 3.0.1 | BuiltIn | Enterprise |
| 4 | Resource logs in Azure Key Vault Managed HSM should be enabled | a2a5b911-5617-447e-a49e-59dbe0e0434b |  | To recreate activity trails for investigation purposes when a security incident occurs or when your network is compromised, you may want to audit by enabling resource logs on Managed HSMs. Please follow the instructions here: https://docs.microsoft.com/azure/key-vault/managed-hsm/logging. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Key Vault | Security | 1.1.0 | BuiltIn | Enterprise |
| 5 | Resource logs in Key Vault should be enabled | cf820ca0-f99e-4f3e-84fb-66e913812d21 |  | Audit enabling of resource logs. This enables you to recreate activity trails to use for investigation purposes when a security incident occurs or when your network is compromised | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Key Vault | Security | 5.0.0 | BuiltIn | Enterprise |
