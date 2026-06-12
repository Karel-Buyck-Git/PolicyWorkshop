# Company Container Services Enterprise — Kubernetes

## Tier rationale

**Enterprise** — Zero-trust and regulatory alignment for Kubernetes: controls that require infrastructure investment or map directly to compliance frameworks. This tier delivers diagnostic settings streaming to Log Analytics / Event Hub / Sentinel, customer-managed keys (CMK / BYOK) for cryptographic sovereignty, and direct mapping to regulatory framework controls. Together these policies protect against lateral movement, sovereign-data exfiltration, and audit gaps in regulated workloads. Maps to NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-container-services-enterprise-kubernetes.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-container-services-enterprise-kubernetes.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-container-services-enterprise-kubernetes.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-container-services-enterprise-kubernetes.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Kubernetes Service Private Clusters should be enabled | 040732e8-d947-40b8-95d6-854c95024bf8 |  | Enable the private cluster feature for your Azure Kubernetes Service cluster to ensure network traffic between your API server and your node pools remains on the private network only. This is a common requirement in many regulatory and industry compliance standards. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Kubernetes | Container Services | 1.0.1 | BuiltIn | Enterprise |
| 2 | Both operating systems and data disks in Azure Kubernetes Service clusters should be encrypted by customer-managed keys | 7d7be79c-23ba-4033-84dd-45e2a5ccdd67 |  | Encrypting OS and data disks using customer-managed keys provides more control and greater flexibility in key management. This is a common requirement in many regulatory and industry compliance standards. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Kubernetes | Container Services | 1.0.1 | BuiltIn | Enterprise |
| 3 | Deploy - Configure diagnostic settings for Azure Kubernetes Service to Log Analytics workspace | 6c66c325-74c8-42fd-a286-a74b0e2939d8 |  | Deploys the diagnostic settings for Azure Kubernetes Service to stream resource logs to a Log Analytics workspace. | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Kubernetes | Container Services | 3.0.0 | BuiltIn | Enterprise |
| 4 | Resource logs in Azure Kubernetes Service should be enabled | 245fc9df-fa96-4414-9a0b-3738c2f7341c |  | Azure Kubernetes Service's resource logs can help recreate activity trails when investigating security incidents. Enable it to make sure the logs will exist when needed | No | No | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Kubernetes | Container Services | 1.0.0 | BuiltIn | Enterprise |
| 5 | Temp disks and cache for agent node pools in Azure Kubernetes Service clusters should be encrypted at host | 41425d9f-d1a5-499a-9932-f8ed8453932c |  | To enhance data security, the data stored on the virtual machine (VM) host of your Azure Kubernetes Service nodes VMs should be encrypted at rest. This is a common requirement in many regulatory and industry compliance standards. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Kubernetes | Container Services | 1.0.1 | BuiltIn | Enterprise |
