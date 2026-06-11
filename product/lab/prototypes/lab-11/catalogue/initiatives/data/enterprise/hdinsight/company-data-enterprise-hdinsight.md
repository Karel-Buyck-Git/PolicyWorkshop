# Company Data Enterprise — HDInsight

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for HDInsight: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface, customer-managed keys (CMK / BYOK) for cryptographic sovereignty, and direct mapping to regulatory framework controls. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-data-enterprise-hdinsight.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-data-enterprise-hdinsight.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-data-enterprise-hdinsight.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-data-enterprise-hdinsight.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure HDInsight clusters should use customer-managed keys to encrypt data at rest | 64d314f6-6062-4780-a861-c23e8951bee5 |  | Use customer-managed keys to manage the encryption at rest of your Azure HDInsight clusters. By default, customer data is encrypted with service-managed keys, but customer-managed keys are commonly required to meet regulatory compliance standards. Customer-managed keys enable the data to be encrypted with an Azure Key Vault key created and owned by you. You have full control and responsibility for the key lifecycle, including rotation and management. Learn more at https://aka.ms/hdi.cmk. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | HDInsight | Data | 1.0.1 | BuiltIn | Enterprise |
| 2 | Azure HDInsight should use private link | c8cc2f85-e019-4065-9fa3-5e6a2b2dde56 |  | Azure Private Link lets you connect your virtual networks to Azure services without a public IP address at the source or destination. The Private Link platform handles the connectivity between the consumer and services over the Azure backbone network. By mapping private endpoints to Azure HDInsight clusters, you can reduce data leakage risks. Learn more about private links at: https://aka.ms/hdi.pl. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | HDInsight | Data | 1.0.0 | BuiltIn | Enterprise |
| 3 | Configure Azure HDInsight clusters to use private DNS zones | 43d6e3bd-fc6a-4b44-8b4d-2151d8736a11 |  | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to Azure HDInsight clusters. Learn more at: https://aka.ms/hdi.pl. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | HDInsight | Data | 1.0.0 | BuiltIn | Enterprise |
| 4 | Configure Azure HDInsight clusters with private endpoints | 2676090a-4baf-46ac-9085-4ac02cc50e3e |  | Private endpoints connect your virtual networks to Azure services without a public IP address at the source or destination. By mapping private endpoints to Azure HDInsight clusters, you can reduce data leakage risks. Learn more about private links at: https://aka.ms/hdi.pl. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | HDInsight | Data | 1.0.0 | BuiltIn | Enterprise |
