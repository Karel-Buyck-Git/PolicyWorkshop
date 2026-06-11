# Company Data Professional — Synapse

## Tier rationale

**Professional** — Active security posture for Synapse: controls that produce signals an operations team must act on. This tier delivers vulnerability assessment scanning, network hardening (public access disabled, VNet integration, firewall rules), audit-log and monitoring controls that produce signals for ops teams, and auto-remediation deployments. Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-data-professional-synapse.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-data-professional-synapse.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-data-professional-synapse.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-data-professional-synapse.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Auditing on Synapse workspace should be enabled | e04e5000-cd89-451d-bb21-a14d24ff9c73 |  | Auditing on your Synapse workspace should be enabled to track database activities across all databases on the dedicated SQL pools and save them in an audit log. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Synapse | Data | 1.0.0 | BuiltIn | Professional |
| 2 | Azure Synapse workspaces should disable public network access | 38d8df46-cf4e-4073-8e03-48c24b29de0d |  | Disabling public network access improves security by ensuring that the Synapse workspace isn't exposed on the public internet. Creating private endpoints can limit exposure of your Synapse workspaces. Learn more at: https://docs.microsoft.com/azure/synapse-analytics/security/connectivity-settings. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Synapse | Data | 1.0.0 | BuiltIn | Professional |
| 3 | Configure Azure Synapse workspaces to disable public network access | 5c8cad01-ef30-4891-b230-652dadb4876a |  | Disable public network access for your Synapse workspace so that it is not accessible over the public internet. This can reduce data leakage risks. Learn more at: https://docs.microsoft.com/azure/synapse-analytics/security/connectivity-settings. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Synapse | Data | 1.0.0 | BuiltIn | Professional |
| 4 | Managed workspace virtual network on Azure Synapse workspaces should be enabled | 2d9dbfa3-927b-4cf0-9d0f-08747f971650 |  | Enabling a managed workspace virtual network ensures that your workspace is network isolated from other workspaces. Data integration and Spark resources deployed in this virtual network also provides user level isolation for Spark activities. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Synapse | Data | 1.0.0 | BuiltIn | Professional |
| 5 | Vulnerability assessment should be enabled on your Synapse workspaces | 0049a6b3-a662-4f3e-8635-39cf44ace45a |  | Discover, track, and remediate potential vulnerabilities by configuring recurring SQL vulnerability assessment scans on your Synapse workspaces. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Synapse | Data | 1.0.0 | BuiltIn | Professional |
