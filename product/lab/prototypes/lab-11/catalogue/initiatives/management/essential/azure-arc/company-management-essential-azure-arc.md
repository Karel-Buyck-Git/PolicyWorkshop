# Company Management Essential — Azure Arc

## Tier rationale

**Essential** — Baseline hygiene for Azure Arc: the non-negotiable controls every deployment should enforce from day one. This tier delivers TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Usage

These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) (Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor validation.

| Artifact | EPAC type | What to do with it |
|---|---|---|
| `company-management-essential-azure-arc.policyset.json` | `policySetDefinition` (initiative) | The set of built-in policies for this (domain, tier, category), hardened effect baked in and required parameters bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |
| `company-management-essential-azure-arc.assignment.json` | `policyAssignment` | Binds the initiative to a scope. Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` parameter mock, then place under `policyAssignments/`. The `description` field states this group's prerequisites (required parameter count, managed identity). |
| `company-management-essential-azure-arc.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and `policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place under `policyExemptions/`. |
| `company-management-essential-azure-arc.roles.json` | role assignments (lab helper) | Present for this group. Lists the `roleDefinitionIds` the assignment's managed identity needs for remediation. Not an EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never need the policy repo downstream. |

**Deployment order:** assign the initiative → (if a managed identity is required) grant the roles from `roles.json` at the assignment scope → run remediation tasks for the Modify/DeployIfNotExists policies.

## Policies

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Azure Arc-enabled Servers to enable automatic upgrades | f9dfba6f-7430-4214-a666-342b3d3d0d62 |  | The Automatic Upgrade feature allows servers to stay updated with no action from the user after opting in. This policy ensures that Azure Arc-enabled servers are configured to be opted in for automatic upgrades. | No | Yes | Modify, Disabled | Modify | Modify | Modify | Azure Arc | Management | 1.0.0 | BuiltIn | Essential |
| 2 | Deny Extended Security Updates (ESUs) license creation or modification. | 4c660f31-eafb-408d-a2b3-6ed2260bd26c | Preview | This policy enables you to restrict the creation or modification of ESU licenses for Windows Server 2012 Arc machines. For more details on pricing please visit https://aka.ms/ArcWS2012ESUPricing | No | No | Deny, Disabled | Deny | Deny | Deny | Azure Arc | Management | 1.0.0-preview | BuiltIn | Essential |
| 3 | Enable Extended Security Updates (ESUs) license to keep Windows 2012 machines protected after their support lifecycle has ended. | 4864134f-d306-4ff5-94d8-ea4553b18c97 | Preview | Enable Extended Security Updates (ESUs) license to keep Windows 2012 machines protected even after their support lifecycle has ended. Learn How to prepare to deliver Extended Security Updates for Windows Server 2012 through AzureArc please visit https://learn.microsoft.com/en-us/azure/azure-arc/servers/prepare-extended-security-updates. For more details on pricing please visit https://aka.ms/ArcWS2012ESUPricing | Yes | Yes | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | Azure Arc | Management | 1.0.0-preview | BuiltIn | Essential |
