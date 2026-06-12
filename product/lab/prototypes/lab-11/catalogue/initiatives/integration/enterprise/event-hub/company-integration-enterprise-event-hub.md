# Company Integration Enterprise — Event Hub

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Event Hubs: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers diagnostic settings streaming to Log Analytics / Event Hub / Sentinel and customer-managed keys (CMK / BYOK) for cryptographic sovereignty. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-integration-enterprise-event-hub.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-integration-enterprise-event-hub.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-integration-enterprise-event-hub.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-integration-enterprise-event-hub.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Event Hub namespaces should use a customer-managed key for encryption | a1ad735a-e96f-45d2-a7b2-9a4932cab7ec |  | Azure Event Hubs supports the option of encrypting data at rest with either Microsoft-managed keys (default) or customer-managed keys. Choosing to encrypt data using customer-managed keys enables you to assign, rotate, disable, and revoke access to the keys that Event Hub will use to encrypt data in your namespace. Note that Event Hub only supports encryption with customer-managed keys for namespaces in dedicated clusters. | No | No | Audit, Disabled | Audit | Audit | Audit | Event Hub | Integration | 1.0.0 | BuiltIn | Enterprise |
| 2 | Resource logs in Event Hub should be enabled | 83a214f7-d01a-484b-91a9-ed54470c9a6a |  | Audit enabling of resource logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Event Hub | Integration | 5.0.0 | BuiltIn | Enterprise |
