# Company Web Essential — App Configuration

## Tier rationale

**Essential** — Baseline hygiene for App Configuration: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials and TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-web-essential-app-configuration.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-web-essential-app-configuration.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-web-essential-app-configuration.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-web-essential-app-configuration.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | App Configuration should use geo-replication | d242c24b-bac7-439e-8af7-22d7dcfd3c4f |  | Use the geo-replication feature to create replicas in other locations of your current configuration store for enhanced resiliency and availability. Additionally, having multi-region replicas lets you better distribute load, lower latency, protect against datacenter outages, and compartmentalize globally distributed workloads. Learn more at: https://aka.ms/appconfig/geo-replication. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | App Configuration | Web | 1.0.0 | BuiltIn | Essential |
| 2 | App Configuration stores should have local authentication methods disabled | b08ab3ca-1062-4db3-8803-eec9cae605d6 |  | Disabling local authentication methods improves security by ensuring that App Configuration stores require Microsoft Entra identities exclusively for authentication. Learn more at: https://go.microsoft.com/fwlink/?linkid=2161954. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | App Configuration | Web | 1.0.1 | BuiltIn | Essential |
| 3 | Configure App Configuration stores to disable local authentication methods | 72bc14af-4ab8-43af-b4e4-38e7983f9a1f |  | Disable local authentication methods so that your App Configuration stores require Microsoft Entra identities exclusively for authentication. Learn more at: https://go.microsoft.com/fwlink/?linkid=2161954. | No | Yes | Modify, Disabled | Modify | Modify | Modify | App Configuration | Web | 1.0.1 | BuiltIn | Essential |
