# Company undefined Professional — Internet of Things

## Tier rationale

**Professional** — Active security posture for Internet of Things: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-undefined-professional-internet-of-things.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-undefined-professional-internet-of-things.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-undefined-professional-internet-of-things.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-undefined-professional-internet-of-things.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure IoT Hub device provisioning service instances to disable public network access | 859dfc91-ea35-43a6-8256-31271c363794 |  | Disable public network access for your IoT Hub device provisioning instance so that it's not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://aka.ms/iotdpsvnet. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Internet of Things | undefined | 1.0.0 | BuiltIn | Professional |
| 2 | IoT Hub device provisioning service instances should disable public network access | d82101f3-f3ce-4fc5-8708-4c09f4009546 |  | Disabling public network access improves security by ensuring that IoT Hub device provisioning service instance isn't exposed on the public internet. Creating private endpoints can limit exposure of the IoT Hub device provisioning instances. Learn more at: https://aka.ms/iotdpsvnet. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Internet of Things | undefined | 1.0.0 | BuiltIn | Professional |
