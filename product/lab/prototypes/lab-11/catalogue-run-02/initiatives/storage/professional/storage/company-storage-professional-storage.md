# Company Storage Professional — Storage

## Tier rationale

**Professional** — Active security posture for Storage: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-storage-professional-storage.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-storage-professional-storage.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-storage-professional-storage.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-storage-professional-storage.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure your Storage account public access to be disallowed | 13502221-8df0-4414-9937-de9c5c4e396b |  | Anonymous public read access to containers and blobs in Azure Storage is a convenient way to share data but might present security risks. To prevent data breaches caused by undesired anonymous access, Microsoft recommends preventing public access to a storage account unless your scenario requires it. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Storage | Storage | 1.0.0 | BuiltIn | Professional |
| 2 | Public network access should be disabled for file share with Microsoft.FileShares | edfb40e6-36fe-4928-96e9-e921bc7dfc70 |  | Disabling the public endpoint allows you to restrict access to your Microsoft.FileShares resource to requests destined to approved private endpoints or service endpoints on your organization's network. You can disable the public endpoint for a file share with Microsoft.FileShares by setting the FileShare publicNetworkAccess of the resource to Disabled. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Storage | Storage | 1.0.0 | BuiltIn | Professional |
| 3 | Storage account public access should be disallowed | 4fa4b6c0-31ca-4c0d-b10d-24b96f62a751 |  | Anonymous public read access to containers and blobs in Azure Storage is a convenient way to share data but might present security risks. To prevent data breaches caused by undesired anonymous access, Microsoft recommends preventing public access to a storage account unless your scenario requires it. | No | No | Audit, Audit, Deny, Deny, Disabled, Disabled | Audit | Audit | Deny | Storage | Storage | 3.1.1 | BuiltIn | Professional |
| 4 | Storage accounts should restrict network access using virtual network rules | 2a1a9cdf-e04d-429a-8416-3bfb72a1b26f |  | Protect your storage accounts from potential threats using virtual network rules as a preferred method instead of IP-based filtering. Disabling IP-based filtering prevents public IPs from accessing your storage accounts. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Storage | Storage | 1.0.1 | BuiltIn | Professional |
| 5 | Storage accounts should restrict network access using virtual network rules (excluding storage accounts created by Databricks) | db4f9b05-5ffd-4b34-b714-3c710dbb3fd6 |  | Protect your storage accounts from potential threats using virtual network rules as a preferred method instead of IP-based filtering. Disabling IP-based filtering prevents public IPs from accessing your storage accounts. | No | No | Audit, Deny, Disabled | Audit | Audit | Deny | Storage | Storage | 1.0.0 | BuiltIn | Professional |
