# `gen-dlw-tagging-definitions` DLW mandatory-tags policy generator

> A generator in [`definition_gen/`](README.md). Script: `gen_dlw_tagging_definitions.py` ·
> output family: `dlw-az-tagging`. See the package [README](README.md) for how generators fit
> together.

Generates the **Azure Policy** that audits/denies resources missing the organisation's mandatory
tags, plus the `management-esn-tagging` initiative that bundles it. It is the policy-side mirror of
the deployment-side **`getResourceTags.bicep`**: where that module *applies* the tags at deploy
time, this policy *verifies their presence* at the platform — catching resources created outside
the module (portal, scripts, other IaC).

- **Script:** `gen_dlw_tagging_definitions.py`
- **Outputs** (existing `tagging-*.json` in the family folder are overwritten):
  - `catalogue/definitions/custom/dlw-az-tagging/tagging-require-mandatory-tags.json` — the policy definition
  - `catalogue/initiatives/management/essential/tagging/management-esn-tagging.*` — the initiative
    (policyset · assignment · exemptions · md), brand-neutral and within the Azure limits via
    [`../shared/naming.py`](../shared/naming.py).

```
python flows/definition_gen/gen_dlw_tagging_definitions.py
```

## What it checks

Validates tag **presence only** — the tag *values* are owned by the deploying Bicep. A resource is
non-compliant when it is missing (or has an empty value for) **any** mandatory tag:

| Mandatory tags | Optional (not validated) |
| --- | --- |
| `environment`, `costCenter`, `workload`, `owner`, `creationDate`, `service` | `description` |

Edit `MANDATORY_TAGS` / `OPTIONAL_TAGS` at the top of the script and re-run — the policy rule's
`anyOf` (a missing-or-empty test per tag) is generated from that list, so the rule stays in sync.

## Parameters

| Parameter | Where | Allowed / type | Default | Notes |
| --- | --- | --- | --- | --- |
| `effect` | initiative (one top-level) + the member | `Audit`, `Deny`, `Disabled` | **`Audit`** | The initiative wires the member's `effect` to its single top-level `effect`, so one value tunes the set. Set to `Deny` at the customer to enforce. |
| `excludedResourceTypes` | definition | array (wildcards) | `[]` | Resource types matching any pattern are exempt — useful for child/proxy types that don't support tags (e.g. `Microsoft.Network/*/*`). |

## Effect handling & deployment

Everything ships as **`Audit`** — non-compliant resources are reported, nothing is blocked. This is
deliberate: land as `Audit` to discover non-compliant existing resources (brownfield), then flip
the initiative's `effect` to **`Deny`** **at assignment time in the customer environment** to
enforce on new deployments (greenfield). `Deny` gates create/update only — it never blocks or
modifies resources that already exist. **Do not** bake `Deny` into the generated artifacts.

Deploy the `tagging-*` definition and the initiative **together** via EPAC (the initiative
references the definition by `policyDefinitionName`). Assign at a management-group scope.

## Why a distinct `Tagging` category

The overlay initiative is placed under `Management / Essential / **Tagging**` (folder
`initiatives/management/essential/tagging/`, name `management-esn-tagging`) rather than the built-in
**`Tags`** category — otherwise its name would collide with the built-in producer's
`management-esn-tags` group, which QC would reject as a duplicate. The category code `tagging` is
supplied inline by the script (it is a custom category, not an Azure resource type, so it is not in
[`../../config/azure-category-abbreviation.md`](../../config/azure-category-abbreviation.md)).

## Lineage

Reconstructed from the single surviving artifact
([`tagging-require-mandatory-tags.json`](../../catalogue-run-pre-py-package/definitions/custom/dlw-az-tagging/tagging-require-mandatory-tags.json)
in the pre-py-package run) using `gen_dlw_naming_definitions.py` as the structural template. The
regenerated definition's `policyRule`, `parameters` and `mandatoryTags` match the original exactly;
only the description was shortened to fit Azure's 512-char limit.
