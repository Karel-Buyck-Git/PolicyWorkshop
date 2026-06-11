# Company Data Essential — Cache

## Tier rationale

**Essential** — Baseline hygiene for Cache: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-data-essential-cache.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-data-essential-cache.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-data-essential-cache.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-data-essential-cache.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Cache for Redis should not use access keys for authentication | 3827af20-8f80-4b15-8300-6db0873ec901 |  | Not using local authentication methods like access keys and using more secure alternatives like Microsoft Entra ID (recommended) improves security for your Azure Cache for Redis. Learn more at aka.ms/redis/disableAccessKeyAuthentication | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Cache | Data | 1.0.0 | BuiltIn | Essential |
| 2 | Configure Azure Cache for Redis to disable non SSL ports | 766f5de3-c6c0-4327-9f4d-042ab8ae846c |  | Enable SSL only connections to Azure Cache for Redis. Use of secure connections ensures authentication between the server and the service and protects data in transit from network layer attacks such as man-in-the-middle, eavesdropping, and session-hijacking | No | Yes | Modify, Disabled | Modify | Modify | Modify | Cache | Data | 1.0.0 | BuiltIn | Essential |
| 3 | Only secure connections to your Azure Cache for Redis should be enabled | 22bee202-a82f-4305-9a2a-6d7f44d4dedb |  | Audit enabling of only connections via SSL to Azure Cache for Redis. Use of secure connections ensures authentication between the server and the service and protects data in transit from network layer attacks such as man-in-the-middle, eavesdropping, and session-hijacking | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Cache | Data | 1.0.0 | BuiltIn | Essential |
