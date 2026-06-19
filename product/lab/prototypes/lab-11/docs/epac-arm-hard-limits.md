# Azure Policy — Hard Limits Reference

> Reference for agents generating JSON assets for Azure Policy (definitions, initiatives, assignments, exemptions).
> All values are limits **enforced by Azure** at create/update time. Validate against these before submitting.
> Source: Microsoft Learn (Azure Policy docs) and `Microsoft.Authorization` resource naming rules. Last verified: 2026-06-19.

## Resource `name` length (the `name` segment of the resource ID)

Enforced by the `Microsoft.Authorization` resource provider. This is the value supplied as `-Name` / the `name` field, **not** the `displayName`.

| Object                             | Resource type                                  | Max name length |
| ---------------------------------- | ---------------------------------------------- | --------------- |
| Policy definition                  | `Microsoft.Authorization/policyDefinitions`    | **64**          |
| Initiative (policy set) definition | `Microsoft.Authorization/policySetDefinitions` | **64**          |
| Policy assignment                  | `Microsoft.Authorization/policyAssignments`    | **24**          |
| Initiative assignment              | `Microsoft.Authorization/policyAssignments`    | **24**          |
| Exemption                          | `Microsoft.Authorization/policyExemptions`     | **64**          |
| Remediation task                   | `Microsoft.PolicyInsights/remediations`        | **260**         |

> ⚠️ **Critical for asset generation:** policy/initiative **assignment** names max out at **24 characters**. This is the strictest and most commonly violated limit. Generate assignment names with this cap in mind (e.g. avoid long descriptive slugs — put detail in `displayName` instead).

## Display name / description / metadata length

Applies identically to policy definitions, initiative definitions, and assignments.

| Field                    | Max length |
| ------------------------ | ---------- |
| `displayName`            | **128**    |
| `description`            | **512**    |
| each `metadata` property | **1,024**  |

## Count and size caps

For definitions, _Scope_ = management group or subscription. For assignments and exemptions, _Scope_ = management group, subscription, resource group, or individual resource.

| Where                                             | What                                 | Max              |
| ------------------------------------------------- | ------------------------------------ | ---------------- |
| Scope                                             | Policy definitions                   | 500              |
| Scope                                             | Initiative definitions               | 200              |
| Tenant                                            | Initiative definitions               | 2,500            |
| Scope                                             | Policy or initiative assignments     | 200              |
| Scope                                             | Exemptions                           | 1,000            |
| Policy definition                                 | Parameters                           | 20               |
| Initiative definition                             | Policies                             | 1,000            |
| Initiative definition                             | Parameters                           | 400              |
| Assignment                                        | Exclusions (`notScopes`)             | 400              |
| Assignment                                        | `resourceSelectors`                  | 10               |
| Resource selector                                 | values in `in` / `notIn`             | 50               |
| Assignment                                        | `overrides`                          | 10               |
| Override                                          | `policyDefinitionReferenceId` values | 50               |
| Policy rule                                       | Nested conditionals                  | 512              |
| Remediation task                                  | Resources                            | 50,000           |
| Definition / initiative / assignment request body | Bytes                                | 1,048,576 (1 MB) |

## Generation checklist

- [ ] Assignment `name` ≤ 24 chars (hard fail otherwise)
- [ ] Definition / initiative / exemption `name` ≤ 64 chars
- [ ] `displayName` ≤ 128 chars; `description` ≤ 512 chars
- [ ] Each `metadata` value ≤ 1,024 chars
- [ ] Initiative references ≤ 1,000 policies; ≤ 400 parameters
- [ ] Policy definition ≤ 20 parameters
- [ ] Total request body < 1 MB
- [ ] `notScopes` ≤ 400 entries

## Sources

- [What is Azure Policy? — Maximum count of Azure Policy objects](https://learn.microsoft.com/en-us/azure/governance/policy/overview)
- [Azure Policy assignment structure](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/assignment-structure)
- [Azure Policy definition structure basics](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure-basics)
- [Naming rules and restrictions for Azure resources — Microsoft.Authorization](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules)
