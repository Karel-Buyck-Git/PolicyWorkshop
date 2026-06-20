# `gen-az-apim` API Management hardening policy generator

> A generator in [`definition_gen/`](README.md). Script: `gen_az_apim.py` · output family:
> `az-apim`. See the package [README](README.md) for how generators fit together.

Generates custom **API Management (APIM) hardening** policy definitions, derived from the **Azure
Landing Zones / enterprise-scale** policy set (`github.com/Azure/Enterprise-Scale`, surfaced via
[azadvertizer](https://www.azadvertizer.net/)). It starts with one control and is **expandable**.

- **Script:** `gen_az_apim.py`
- **Output** (existing `apim-*.json` overwritten): `catalogue/definitions/custom/az-apim/apim-*.json`

```
python flows/definition_gen/gen_az_apim.py
```

## Definitions

| Definition | Control | Upstream |
| --- | --- | --- |
| `apim-tls` | API Management services should use **TLS 1.2** — flags services with TLS 1.0/1.1 enabled | ALZ `Deny-APIM-TLS` |

`apim-tls` targets `Microsoft.ApiManagement/service` and inspects `customProperties` for the legacy
protocol switches `…protocols.tls10` / `…protocols.tls11` set to `true` (both the `"true"` and
`true` JSON forms). If either legacy protocol is enabled, the policy `effect` applies.

## Effect

`effect` is `Audit` / `Deny` / `Disabled`, **default `Deny`** — the enterprise-scale source's
original intent is preserved (new/updated APIM without TLS 1.2 is blocked on create/update;
existing resources are never modified). Override the `effect` parameter at assignment time to
soften to `Audit`.

## Definitions only (no initiative)

Unlike the dlw generators, this one does **not** emit a bundling initiative. Its category is
`API Management`, which the built-in producer already owns (`integration-esn-apim` /
`integration-pro-apim`), so an overlay initiative would collide with those names. The `apim-*`
definitions are standalone custom definitions; add an initiative under a *distinct* category later
if the family warrants one.

## Expanding

Add another builder function returning an EPAC definition dict and append it to the `DEFINITIONS`
list at the bottom of the script — `main()` writes every entry automatically. Keep names
brand-neutral and `apim-` prefixed (e.g. `apim-managed-identity`, `apim-no-public-network`).

## ALZ provenance & the `[[` → `[` un-escaping

The enterprise-scale source stores policy definitions inside ARM templates, so policy expressions
are ARM-template-escaped as **`[[…]`**. A standalone EPAC policy definition uses the single-bracket
**`[…]`** form, so the generator emits expressions un-escaped — e.g. `then.effect` is
`[parameters('effect')]` and each check is `[indexof(toLower(string(field('…/customProperties'))), …)]`.
The policy *rule* and the `Deny` default are otherwise preserved verbatim. The `metadata` keeps the
lineage: `source` (the enterprise-scale URL), `alzPolicy` (`Deny-APIM-TLS`), and
`alzCloudEnvironments`.
