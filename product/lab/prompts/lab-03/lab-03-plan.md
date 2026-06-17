# Plan: Create API Management Policies Markdown File

## Context

The user is building an Azure Policy Workshop (lab-03) that documents Azure built-in policies by resource type. The task is to read all Azure API Management built-in policy definitions from the official Azure Policy repository, classify them by tier, and generate a formatted markdown table saved to the lab-03 prompts directory.

## Source Files

- **Policy definitions**: `C:\GIT\Official Azure Policy\azure-policy\built-in-policies\policyDefinitions\API Management\` (15 JSON files total)
- **Table template**: `C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop\product\lab\prompts\lab-03\table-template.md`
- **Output file**: `C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop\product\lab\prompts\lab-03\api-management-policies.md`

## Rules Applied

- **Exclude**: `[Deprecated]` policies — 1 excluded (`MinimumApiVersion_AuditDeny.json`)
- **Tier classification priority**:
  1. **Professional** — primarily networking (VNET, endpoints, protocols, public access)
  2. **Enterprise** — governance-focused with Audit/AuditIfNotExists effect
  3. **Essential** — governance with non-audit effect (Modify, Deny)

## Table Structure (from template)

```
| Service | Policy Description | Policy ID | Effect | Category | Notes | Tier |
```

- **Service**: `API Management`
- **Category**: `Built-in`
- **Notes**: empty

## Policies to Include (14 non-deprecated)

| Policy Description                                                                                           | Policy ID                            | Effect            | Tier         |
| ------------------------------------------------------------------------------------------------------------ | ------------------------------------ | ----------------- | ------------ |
| API Management subscriptions should not be scoped to all APIs                                                | 3aa03346-d8c5-4994-a5bc-7652c2a2aef1 | Audit             | Enterprise   |
| API Management service should use a SKU that supports virtual networks                                       | 73ef9241-5d81-4cd4-b483-8443d1730fe5 | Audit             | Professional |
| API Management calls to API backends should be authenticated                                                 | c15dcc82-b93c-4dcb-9332-fbf121685b54 | Audit             | Enterprise   |
| API Management calls to API backends should not bypass certificate thumbprint or name validation             | 92bb331d-ac71-416a-8c91-02f2cb734ce4 | Audit             | Enterprise   |
| API Management policies should inherit parent scope policies using \<base /\>                                | d5448c98-e503-4fdd-bcd2-784960c00d04 | Audit             | Enterprise   |
| Modify API Management to disable username and password authentication                                        | 1b0d74ac-4b43-4c39-a15f-594385adc38d | Modify            | Essential    |
| API Management should have username and password authentication disabled                                     | ffe25541-3853-4f4e-b71d-064422294b11 | Audit             | Enterprise   |
| API Management direct management endpoint should not be enabled                                              | b741306c-968e-4b67-b916-5675e5c709f4 | Audit             | Enterprise   |
| API Management APIs should use only encrypted protocols                                                      | ee7495e7-3ba7-40b6-bfee-c29e22cc75d4 | Audit             | Professional |
| API Management secret named values should be stored in Azure Key Vault                                       | f1cc7827-022c-473e-836e-5a51cae0b249 | Audit             | Enterprise   |
| Azure API Management platform version should be stv2                                                         | 1dc2fc00-2245-4143-99f4-874c937f13ef | Audit             | Enterprise   |
| API Management should disable public network access to the service configuration endpoints                   | df73bd95-24da-4a4f-96b9-4e8b94b402bd | AuditIfNotExists  | Professional |
| Configure API Management services to disable access to API Management public service configuration endpoints | 7ca8c8ac-3a6e-493d-99ba-c5fa35347ff2 | DeployIfNotExists | Professional |
| API Management services should use a virtual network                                                         | ef619a2c-cc4d-4d03-b2ba-8c94a834d85b | Audit             | Professional |

**Summary**: 1 Essential, 4 Professional, 9 Enterprise

## Implementation Steps

1. Create `api-management-policies.md` at the output path
2. Write a top-level heading `# API Management Policies`
3. Write the markdown table with all 14 policies, sorted by Tier (Essential → Professional → Enterprise), then alphabetically within each tier
4. Verify table renders correctly and all 14 policies are present

## Verification

- Count rows: 14 (total 15 minus 1 deprecated)
- Check all 3 tiers represented: Essential (1), Professional (4), Enterprise (9)
- Confirm no `[Deprecated]` policies included
- Confirm file saved at correct path with correct filename (`api-management-policies.md`)
