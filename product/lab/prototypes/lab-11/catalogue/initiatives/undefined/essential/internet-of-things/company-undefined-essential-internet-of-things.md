# Company undefined Essential — Internet of Things

## Tier rationale

**Essential** — Baseline hygiene for Internet of Things: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-undefined-essential-internet-of-things.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-undefined-essential-internet-of-things.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-undefined-essential-internet-of-things.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-undefined-essential-internet-of-things.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure IoT Hub should have local authentication methods disabled for Service Apis | 672d56b3-23a7-4a3c-a233-b77ed7777518 |  | Disabling local authentication methods improves security by ensuring that Azure IoT Hub exclusively require Azure Active Directory identities for Service Api authentication. Learn more at: https://aka.ms/iothubdisablelocalauth. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Internet of Things | undefined | 1.0.0 | BuiltIn | Essential |
| 2 | Configure Azure IoT Hub to disable local authentication | 9f8ba900-a70f-486e-9ffc-faf907305376 |  | Disable local authentication methods so that your Azure IoT Hub exclusively require Azure Active Directory identities for authentication. Learn more at: https://aka.ms/iothubdisablelocalauth. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Internet of Things | undefined | 1.0.0 | BuiltIn | Essential |
