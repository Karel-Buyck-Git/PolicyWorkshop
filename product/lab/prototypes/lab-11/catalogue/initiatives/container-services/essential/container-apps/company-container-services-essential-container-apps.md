# Company Container Services Essential — Container Apps

## Tier rationale

**Essential** — Baseline hygiene for Container Apps: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-container-services-essential-container-apps.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-container-services-essential-container-apps.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-container-services-essential-container-apps.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-container-services-essential-container-apps.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Authentication should be enabled on Container Apps | 2b585559-a78e-4cc4-b1aa-fb169d2f6b96 |  | Container Apps Authentication is a feature that can prevent anonymous HTTP requests from reaching the Container App, or authenticate those that have tokens before they reach the Container App | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Container Apps | Container Services | 1.0.1 | BuiltIn | Essential |
| 2 | Container App should configure with volume mount | 7c9f3fbb-739d-4844-8e42-97e3be6450e0 |  | Enforce the use of volume mounts for Container Apps to ensure availability of persistent storage capacity. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Container Apps | Container Services | 1.0.1 | BuiltIn | Essential |
| 3 | Container Apps should disable external network access | 783ea2a8-b8fd-46be-896a-9ae79643a0b1 |  | Disable external network access to your Container Apps by enforcing internal-only ingress. This will ensure inbound communication for Container Apps is limited to callers within the Container Apps environment. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Container Apps | Container Services | 1.1.0 | BuiltIn | Essential |
| 4 | Container Apps should only be accessible over HTTPS | 0e80e269-43a4-4ae9-b5bc-178126b8a5cb |  | Use of HTTPS ensures server/service authentication and protects data in transit from network layer eavesdropping attacks. Disabling 'allowInsecure' will result in the automatic redirection of requests from HTTP to HTTPS connections for container apps. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Container Apps | Container Services | 1.0.1 | BuiltIn | Essential |
| 5 | Managed Identity should be enabled for Container Apps | b874ab2d-72dd-47f1-8cb5-4a306478a4e7 |  | Enforcing managed identity ensures Container Apps can securely authenticate to any resource that supports Azure AD authentication | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Container Apps | Container Services | 1.0.1 | BuiltIn | Essential |
