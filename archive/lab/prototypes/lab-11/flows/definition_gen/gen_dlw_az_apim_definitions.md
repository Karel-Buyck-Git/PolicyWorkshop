# `gen-dlw-az-apim-definitions` API Management hardening policy generator

> A generator in [`definition_gen/`](README.md). Script: `gen_dlw_az_apim_definitions.py` ·
> output family: `dlw-az-apim` · placement: **Enrich**. See the package [README](README.md) for
> the authoring contract.

Generates custom **API Management (APIM) hardening** policy definitions, derived from the **Azure
Landing Zones / enterprise-scale** policy set (`github.com/Azure/Enterprise-Scale`, via
[azadvertizer](https://www.azadvertizer.net/)). First control: `apim-tls` (APIM must use **TLS
1.2**, upstream `Deny-APIM-TLS`). **Expandable** — add a builder to `DEFINITIONS`.

- **Script:** `gen_dlw_az_apim_definitions.py`
- **Output:** `catalogue/definitions/custom/dlw-az-apim/apim-*.json`, and the definitions are
  added as **members of the built-in `integration-esn-apim` initiative** (Enrich placement).

```
python flows/definition_gen/gen_dlw_az_apim_definitions.py    # preview (needs the built-in group)
# or, as part of the producer build:
python flows/definition_gen/apply_overlays.py
```

## Placement — Enrich, not NewGroup

`apim-tls`'s category (`API Management`) is **owned by the built-in producer**
(`integration-esn-apim` / `integration-pro-apim`). So this generator declares an **Enrich**
placement: the `apim-*` definitions become members of the existing `integration-esn-apim`
policyset (referenced by `policyDefinitionName`, `metadata.policyName` set, effect baked). The
producer's `apply_overlays.py` step bumps that group's `policyCount` and marks it
`hasCustomMembers` in `index.json`. (Enrich runs there, not in a standalone gen run, because
`create_initiatives.py` regenerates the built-in policysets each run.)

## Definitions

| Definition | Control | Upstream |
| --- | --- | --- |
| `apim-tls` | API Management services should use **TLS 1.2** — flags services with TLS 1.0/1.1 enabled in `customProperties` | ALZ `Deny-APIM-TLS` |

## Effect

`effect` is `Audit` / `Deny` / `Disabled`, **default `Deny`** — the enterprise-scale source's
intent is preserved (new/updated APIM without TLS 1.2 is blocked on create/update; existing
resources are never modified). As an Enrich member the effect is baked to its default; override at
assignment time to soften to `Audit`.

## ALZ provenance & the `[[` → `[` un-escaping

The enterprise-scale source stores policy definitions inside ARM templates, so policy expressions
are ARM-template-escaped as **`[[…]`**. A standalone EPAC definition uses the single-bracket
**`[…]`** form, so the generator emits expressions un-escaped — `then.effect` is
`[parameters('effect')]` and each check is `[indexof(toLower(string(field('…/customProperties'))), …)]`.
The rule and the `Deny` default are otherwise preserved. `metadata` keeps the lineage: `source`,
`alzPolicy` (`Deny-APIM-TLS`), `alzCloudEnvironments`.

## Expanding

Add a builder function returning an EPAC definition dict and append it to `DEFINITIONS`. Keep
names brand-neutral and `apim-` prefixed (e.g. `apim-managed-identity`, `apim-no-public-network`).
All members land in the same `integration-esn-apim` group unless you change the placement.
