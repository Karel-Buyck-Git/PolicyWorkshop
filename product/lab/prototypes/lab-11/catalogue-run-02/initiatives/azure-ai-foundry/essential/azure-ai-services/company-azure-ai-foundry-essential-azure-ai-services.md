# Company Azure AI Foundry Essential — Azure Ai Services

## Tier rationale

**Essential** — Baseline hygiene for Azure AI Services: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-azure-ai-foundry-essential-azure-ai-services.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-azure-ai-foundry-essential-azure-ai-services.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-azure-ai-foundry-essential-azure-ai-services.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-azure-ai-foundry-essential-azure-ai-services.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure AI Services resources should have key access disabled (disable local authentication) | 71ef260a-8f18-47b7-abcb-62d0673d94dc |  | Key access (local authentication) is recommended to be disabled for security. Azure OpenAI Studio, typically used in development/testing, requires key access and will not function if key access is disabled. After disabling, Microsoft Entra ID becomes the only access method, which allows maintaining minimum privilege principle and granular control. Learn more at: https://aka.ms/AI/auth | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Ai Services | Azure AI Foundry | 1.1.0 | BuiltIn | Essential |
| 2 | Azure AI Services resources should restrict network access | 037eea7a-bd0a-46c5-9a66-03aea78705d3 |  | By restricting network access, you can ensure that only allowed networks can access the service. This can be achieved by configuring network rules so that only applications from allowed networks can access the Azure AI service. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Ai Services | Azure AI Foundry | 3.3.0 | BuiltIn | Essential |
| 3 | Configure Azure AI Services resources  to disable local key access (disable local authentication) | d45520cb-31ca-44ba-8da2-fcf914608544 |  | Key access (local authentication) is recommended to be disabled for security. Azure OpenAI Studio, typically used in development/testing, requires key access and will not function if key access is disabled. After disabling, Microsoft Entra ID becomes the only access method, which allows maintaining minimum privilege principle and granular control. Learn more at: https://aka.ms/AI/auth | No | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Azure Ai Services | Azure AI Foundry | 1.0.0 | BuiltIn | Essential |
| 4 | Configure Azure AI Services resources to disable local key access (disable local authentication) | 55eff01b-f2bd-4c32-9203-db285f709d30 |  | Key access (local authentication) is recommended to be disabled for security. Azure OpenAI Studio, typically used in development/testing, requires key access and will not function if key access is disabled. After disabling, Microsoft Entra ID becomes the only access method, which allows maintaining minimum privilege principle and granular control. Learn more at: https://aka.ms/AI/auth | No | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Azure Ai Services | Azure AI Foundry | 1.0.0 | BuiltIn | Essential |
