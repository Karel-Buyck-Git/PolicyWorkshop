# Company undefined Essential — MissionPlatforms

## Tier rationale

**Essential** — Baseline hygiene for MissionPlatforms: the non-negotiable controls every deployment should enforce from day one. This tier delivers TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-undefined-essential-missionplatforms.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-undefined-essential-missionplatforms.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-undefined-essential-missionplatforms.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-undefined-essential-missionplatforms.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Storage Account should enable Secure transfer | f86a882d-7fe6-44e4-916d-ae8c3e792bb2 |  | This policy ensures that data transmitted to storage accounts is protected in transit by requiring secure transfer protocols. Enforcing secure transfer helps prevent unauthorized access and data interception, supporting compliance with security standards and protecting sensitive information. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | MissionPlatforms | undefined | 1.0.0 | BuiltIn | Essential |
| 2 | Storage Account should restrict IP Rules in Storage Account Firewalls. | dad358fa-3aa7-4308-97ba-2c48617d929f |  | IP Rules in Storage Account Firewalls are restricted. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | MissionPlatforms | undefined | 1.0.0 | BuiltIn | Essential |
| 3 | Storage Account should Restrict Source and Destination Targets for Specified Storage Account Object Replication Policies | ac8b77ab-b2cb-457a-a5a7-db8f1dc6a6bc |  | Restrict Source and Destination Targets for Specified Storage Account Object Replication Policies. storageAccountTargets is an array of objects with Storage Account Name, Source Storage Account Names, and Destination Storage Account Names. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | MissionPlatforms | undefined | 1.0.0 | BuiltIn | Essential |
