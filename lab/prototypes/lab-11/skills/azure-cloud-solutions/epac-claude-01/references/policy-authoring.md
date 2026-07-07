# Policy Authoring & Validation

Use this when writing or fixing a policy definition, initiative (policy set), assignment, or exemption — or debugging why a policy isn't behaving. Always confirm current specifics against the live sources in `source-map.md` before finalizing; the structures below are durable, but effect lists, aliases, and built-in IDs change.

## Before you author: check for an existing definition

Custom policies are a maintenance cost. Prefer, in order:
1. A **built-in policy** (`Azure/azure-policy` repo or AzAdvertizer).
2. A **built-in/ALZ initiative** that already bundles the control.
3. A **community/sample** policy adapted to your needs.
4. Only then, a **custom** definition.

When asked "is there a policy for X", fetch and confirm — don't assert from memory.

## Policy definition structure

A definition's `properties` block:

- `displayName`, `description`, `mode` (`All`, `Indexed`, or a resource-provider mode like `Microsoft.Kubernetes.Data`).
- `metadata` — at minimum `category`; for ALZ-style definitions also `version`.
- `parameters` — typed inputs (`type`, `allowedValues`, `defaultValue`, `metadata.displayName/description`). Add an `effect` parameter so the effect is tunable per assignment.
- `policyRule` — `if` (condition) + `then` (effect).

### Skeleton

```json
{
  "properties": {
    "displayName": "Storage accounts should require secure transfer (HTTPS only)",
    "description": "Audit or deny storage accounts that allow insecure (HTTP) traffic.",
    "mode": "Indexed",
    "metadata": { "category": "Storage", "version": "1.0.0" },
    "parameters": {
      "effect": {
        "type": "String",
        "allowedValues": ["Audit", "Deny", "Disabled"],
        "defaultValue": "Audit",
        "metadata": { "displayName": "Effect", "description": "Enable or disable the policy" }
      }
    },
    "policyRule": {
      "if": {
        "allOf": [
          { "field": "type", "equals": "Microsoft.Storage/storageAccounts" },
          { "field": "Microsoft.Storage/storageAccounts/supportsHttpsTrafficOnly", "notEquals": true }
        ]
      },
      "then": { "effect": "[parameters('effect')]" }
    }
  }
}
```

Aliases (e.g. `Microsoft.Storage/storageAccounts/supportsHttpsTrafficOnly`) must be confirmed live — list them via AzAdvertizer or `az policy` alias discovery. Using a non-existent alias silently never matches.

## Effects — pick deliberately

Common effects: `Audit`, `Deny`, `Append`, `Modify`, `AuditIfNotExists`, `DeployIfNotExists` (DINE), `DenyAction`, `Disabled`, `Manual`. Confirm the current list and exact semantics at the effects doc.

- **Audit/Deny** — evaluate the request; no resource changes. Deny blocks non-compliant creates/updates.
- **AuditIfNotExists / DeployIfNotExists** — check for (or deploy) a *related* resource. DINE and **Modify** require:
  - an `existenceCondition` (DINE/AINE),
  - a `roleDefinitionIds` array (the identity's permissions),
  - a managed identity on the assignment,
  - a `deployment`/`operations` block (DINE) or `operations` (Modify).
  Remediation tasks are needed to fix *existing* resources; DINE only auto-acts on new ones.
- **Append/Modify** — add or change properties. Modify is preferred for tags and supports remediation.

## Initiative (policy set) structure

Bundle definitions, expose a clean parameter surface, set per-policy `groupNames` mapped to compliance controls.

```json
{
  "properties": {
    "displayName": "Storage security baseline",
    "policyType": "Custom",
    "metadata": { "category": "Storage", "version": "1.0.0" },
    "parameters": { "storageHttpsEffect": { "type": "String", "defaultValue": "Deny" } },
    "policyDefinitions": [
      {
        "policyDefinitionReferenceId": "storageHttpsOnly",
        "policyDefinitionId": "<full resource ID of the definition>",
        "parameters": { "effect": { "value": "[parameters('storageHttpsEffect')]" } }
      }
    ],
    "policyDefinitionGroups": [
      { "name": "CIS-3.1", "displayName": "CIS Azure 3.1 - secure transfer" }
    ]
  }
}
```

## Assignment essentials

- `scope` — MG, subscription, or RG. Place guardrails at the MG level per CAF (see `caf-alz-architecture.md`).
- `notScopes` / excluded scopes — carve-outs without exemptions.
- `parameters` — supply the initiative/policy parameters.
- `identity` — required (`SystemAssigned` or `UserAssigned`) for DINE/Modify, plus a `location`.
- `enforcementMode` — `Default` (enforced) vs `DoNotEnforce` (audit-only dry run).
- `nonComplianceMessages` — surface a clear message to resource owners.

## Exemptions

Use when a scope legitimately shouldn't comply. Key fields: `policyAssignmentId`, `exemptionCategory` (`Waiver` or `Mitigated`), optional `expiresOn`, `policyDefinitionReferenceIds` (exempt specific members of an initiative). Prefer time-bound exemptions; avoid exempting whole assignments where an excluded scope would do. Note: some resource types (e.g. `Microsoft.Databricks/*`) don't support exemptions due to deny assignments — use assignment-level exclusions instead.

## Validation checklist (run before returning JSON)

- JSON is well-formed; `properties` wrapper present and correct for the artifact type.
- Every alias used actually exists (verified live).
- Effect is parameterized and `allowedValues` includes `Disabled`.
- DINE/Modify: `roleDefinitionIds` present, `existenceCondition`/`operations` present, assignment will carry an identity + location.
- `metadata.category` (and `version` for set/ALZ-style) set.
- For EPAC: the artifact is placed in the right folder and uses EPAC's file conventions — see `epac-operations.md`.
- Cross-check the target resource type against the **Known Issues** list in the Azure Policy repo README (some types bypass evaluation, have read-only aliases, or can't be denied reliably).

## Debugging "my policy isn't working"

Walk these in order:
1. **Scope & assignment** — is it assigned at/above the resource's scope? `enforcementMode` not `DoNotEnforce`? Resource in `notScopes`?
2. **Alias** — does the alias resolve and the field actually populate on the resource type? Check Known Issues for aliases that are read-only or populated differently on GET vs PUT.
3. **Effect timing** — Deny acts on writes; Audit/DINE compliance updates on the next evaluation cycle (can take up to ~30 min, or trigger an on-demand scan).
4. **DINE not remediating** — existing resources need a remediation task; the managed identity needs the role in `roleDefinitionIds`.
5. **Compliance shows unknown/non-compliant unexpectedly** — check Known Issues for the resource type; some don't support LIST and can't report compliance.
6. **Exemption/exclusion** — is the scope exempted or excluded somewhere up the chain?
