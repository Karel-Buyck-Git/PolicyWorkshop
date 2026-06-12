# Company Compute Essential — Service Fabric

## Tier rationale

**Essential** — Baseline hygiene for Service Fabric: the non-negotiable controls every deployment should enforce from day one. This tier delivers encryption-at-rest with service-managed keys and key and certificate lifecycle hygiene (rotation, expiration, validity). Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-compute-essential-service-fabric.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-compute-essential-service-fabric.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-compute-essential-service-fabric.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-compute-essential-service-fabric.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Service Fabric clusters should have the ClusterProtectionLevel property set to EncryptAndSign | 617c02be-7f02-4efd-8836-3180d47b6c68 |  | Service Fabric provides three levels of protection (None, Sign and EncryptAndSign) for node-to-node communication using a primary cluster certificate. Set the protection level to ensure that all node-to-node messages are encrypted and digitally signed | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Service Fabric | Compute | 1.1.0 | BuiltIn | Essential |
| 2 | Service Fabric clusters should only use Azure Active Directory for client authentication | b54ed75b-3e1a-44ac-a333-05ba39b99ff0 |  | Audit usage of client authentication only via Azure Active Directory in Service Fabric | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Service Fabric | Compute | 1.1.0 | BuiltIn | Essential |
