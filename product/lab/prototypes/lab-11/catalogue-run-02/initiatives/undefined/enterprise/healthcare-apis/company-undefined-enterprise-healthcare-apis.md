# Company undefined Enterprise — Healthcare APIs

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Healthcare APIs: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers customer-managed keys (CMK / BYOK) for cryptographic sovereignty and direct mapping to regulatory framework controls. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-undefined-enterprise-healthcare-apis.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-undefined-enterprise-healthcare-apis.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-undefined-enterprise-healthcare-apis.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-undefined-enterprise-healthcare-apis.roles.json` | role assignments (lab helper) | Not present for this group (no Modify/DeployIfNotExists policy). Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | DICOM Service should use a customer-managed key to encrypt data at rest | 14961b63-a1eb-4378-8725-7e84ca8db0e6 |  | Use a customer-managed key to control the encryption at rest of the data stored in Azure Health Data Services DICOM Service when this is a regulatory or compliance requirement. Customer-managed keys also deliver double encryption by adding a second layer of encryption on top of the default one done with service-managed keys. | No | No | Audit, Disabled | Audit | Audit | Audit | Healthcare APIs | undefined | 1.0.0 | BuiltIn | Enterprise |
| 2 | FHIR Service should use a customer-managed key to encrypt data at rest | c42dee8c-0202-4a12-bd8e-3e171cbf64dd |  | Use a customer-managed key to control the encryption at rest of the data stored in Azure Health Data Services FHIR Service when this is a regulatory or compliance requirement. Customer-managed keys also deliver double encryption by adding a second layer of encryption on top of the default one done with service-managed keys. | No | No | Audit, Disabled | Audit | Audit | Audit | Healthcare APIs | undefined | 1.0.0 | BuiltIn | Enterprise |
