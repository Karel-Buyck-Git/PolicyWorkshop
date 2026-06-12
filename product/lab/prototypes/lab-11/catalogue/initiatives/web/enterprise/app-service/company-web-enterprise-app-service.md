# Company Web Enterprise — App Service

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for App Service: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers diagnostic settings streaming to Log Analytics / Event Hub / Sentinel. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-web-enterprise-app-service.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-web-enterprise-app-service.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-web-enterprise-app-service.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-web-enterprise-app-service.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | App Service app slots should have resource logs enabled | d639b3af-a535-4bef-8dcf-15078cddf5e2 |  | Audit enabling of resource logs on the app. This enables you to recreate activity trails for investigation purposes if a security incident occurs or your network is compromised. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | App Service | Web | 1.0.0 | BuiltIn | Enterprise |
| 2 | App Service apps should have resource logs enabled | 91a78b24-f231-4a8a-8da9-02c35b2b6510 |  | Audit enabling of resource logs on the app. This enables you to recreate activity trails for investigation purposes if a security incident occurs or your network is compromised. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | App Service | Web | 2.0.1 | BuiltIn | Enterprise |
| 3 | Function app slots should have resource logs enabled | 2b8d966c-439e-4008-8c91-9c782b72aa9a |  | Audit enabling of resource logs on the function app slot. This enables you to recreate activity trails for investigation purposes if a security incident occurs or your network is compromised. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | App Service | Web | 1.0.0 | BuiltIn | Enterprise |
| 4 | Function apps should have resource logs enabled | a209d6bd-0ace-468c-9883-71a82870b46b |  | Audit enabling of resource logs on the function app. This enables you to recreate activity trails for investigation purposes if a security incident occurs or your network is compromised. | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | App Service | Web | 1.0.0 | BuiltIn | Enterprise |
