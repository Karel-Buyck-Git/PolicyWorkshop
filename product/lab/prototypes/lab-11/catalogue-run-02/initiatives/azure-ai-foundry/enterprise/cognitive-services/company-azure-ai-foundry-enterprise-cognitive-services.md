# Company Azure AI Foundry Enterprise — Cognitive Services

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Cognitive Services: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers private endpoints and private link removing the public attack surface and customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-azure-ai-foundry-enterprise-cognitive-services.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-azure-ai-foundry-enterprise-cognitive-services.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-azure-ai-foundry-enterprise-cognitive-services.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-azure-ai-foundry-enterprise-cognitive-services.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure AI Services resources should encrypt data at rest with a customer-managed key (CMK) | 67121cc7-ff39-4ab8-b7e3-95b84dab487d |  | Using customer-managed keys to encrypt data at rest provides more control over the key lifecycle, including rotation and management. This is particularly relevant for organizations with related compliance requirements. This is not assessed by default and should only be applied when required by compliance or restrictive policy requirements. If not enabled, the data will be encrypted using platform-managed keys. To implement this, update the 'Effect' parameter in the Security Policy for the applicable scope. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Cognitive Services | Azure AI Foundry | 2.2.0 | BuiltIn | Enterprise |
| 2 | Cognitive Services accounts should use customer owned storage | 46aa9b05-0e60-4eae-a88b-1e9d374fa515 |  | Use customer owned storage to control the data stored at rest in Cognitive Services. To learn more about customer owned storage, visit https://aka.ms/cogsvc-cmk. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Cognitive Services | Azure AI Foundry | 2.0.0 | BuiltIn | Enterprise |
| 3 | Configure Cognitive Services accounts to use private DNS zones | c4bc6f10-cb41-49eb-b000-d5ab82e2a091 |  | Use private DNS zones to override the DNS resolution for a private endpoint. A private DNS zone links to your virtual network to resolve to Cognitive Services accounts. Learn more at: https://go.microsoft.com/fwlink/?linkid=2110097. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Cognitive Services | Azure AI Foundry | 1.0.0 | BuiltIn | Enterprise |
| 4 | Configure Cognitive Services accounts with private endpoints | db630ad5-52e9-4f4d-9c44-53912fe40053 |  | Private endpoints connect your virtual networks to Azure services without a public IP address at the source or destination. By mapping private endpoints to Cognitive Services, you'll reduce the potential for data leakage. Learn more about private links at: https://go.microsoft.com/fwlink/?linkid=2129800. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Cognitive Services | Azure AI Foundry | 3.0.0 | BuiltIn | Enterprise |
