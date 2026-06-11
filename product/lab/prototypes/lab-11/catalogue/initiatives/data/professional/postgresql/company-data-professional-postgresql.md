# Company Data Professional — PostgreSQL

## Tier rationale

**Professional** — Active security posture for PostgreSQL: controls that produce signals an operations team must act on. This tier delivers audit-log and monitoring controls that produce signals for ops teams. Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-data-professional-postgresql.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-data-professional-postgresql.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-data-professional-postgresql.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-data-professional-postgresql.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Auditing with PgAudit should be enabled for PostgreSQL flexible servers | 4eb5e667-e871-4292-9c5d-8bbb94e0c908 |  | This policy helps audit any PostgreSQL flexible servers in your environment which is not enabled to use pgaudit. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | PostgreSQL | Data | 1.0.0 | BuiltIn | Professional |
| 2 | Log checkpoints should be enabled for PostgreSQL flexible servers | 70be9e12-c935-49ac-9bd8-fd64b85c1f87 |  | This policy helps audit any PostgreSQL flexible servers in your environment without log_checkpoints setting enabled. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | PostgreSQL | Data | 1.0.0 | BuiltIn | Professional |
| 3 | Log connections should be enabled for PostgreSQL flexible servers | 086709ac-11b5-478d-a893-9567a16d2ae3 |  | This policy helps audit any PostgreSQL flexible servers in your environment without log_connections setting enabled. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | PostgreSQL | Data | 1.0.0 | BuiltIn | Professional |
