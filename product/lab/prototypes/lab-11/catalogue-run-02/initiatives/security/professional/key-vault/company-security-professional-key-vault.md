# Company Security Professional — Key Vault

## Tier rationale

**Professional** — Active security posture for Key Vault: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-security-professional-key-vault.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-security-professional-key-vault.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-security-professional-key-vault.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-security-professional-key-vault.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Key Vault Managed HSM should disable public network access | 19ea9d63-adee-4431-a95e-1913c6c1c75f | Preview | Disable public network access for your Azure Key Vault Managed HSM so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://docs.microsoft.com/azure/key-vault/managed-hsm/private-link#allow-trusted-services-to-access-managed-hsm. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Key Vault | Security | 1.0.0-preview | BuiltIn | Professional |
| 2 | Azure Key Vault should disable public network access | 405c5871-3e91-4644-8a63-58e19d68ff5b |  | Disable public network access for your key vault so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://aka.ms/akvprivatelink. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Key Vault | Security | 1.1.0 | BuiltIn | Professional |
| 3 | Azure Key Vault should have firewall enabled or public network access disabled | 55615ac9-af46-4a59-874e-391cc3dfb490 |  | Enable the key vault firewall so that the key vault is not accessible by default to any public IPs or disable public network access for your key vault so that it's not accessible over the public internet. Optionally, you can configure specific IP ranges to limit access to those networks. Learn more at: https://docs.microsoft.com/azure/key-vault/general/network-security and https://aka.ms/akvprivatelink | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Key Vault | Security | 3.3.0 | BuiltIn | Professional |
| 4 | Configure Azure Key Vault Managed HSM to disable public network access | 84d327c3-164a-4685-b453-900478614456 | Preview | Disable public network access for your Azure Key Vault Managed HSM so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://docs.microsoft.com/azure/key-vault/managed-hsm/private-link#allow-trusted-services-to-access-managed-hsm. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Key Vault | Security | 2.0.0-preview | BuiltIn | Professional |
| 5 | Configure key vaults to enable firewall | ac673a9a-f77d-4846-b2d8-a57f8e1c01dc |  | Enable the key vault firewall so that the key vault is not accessible by default to any public IPs. You can then configure specific IP ranges to limit access to those networks. Learn more at: https://docs.microsoft.com/azure/key-vault/general/network-security | No | Yes | Modify, Disabled | Modify | Modify | Modify | Key Vault | Security | 1.1.1 | BuiltIn | Professional |
