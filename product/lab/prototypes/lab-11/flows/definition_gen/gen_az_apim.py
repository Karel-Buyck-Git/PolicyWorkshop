"""Generate custom API Management (APIM) hardening policy definitions.

Definitions derived from the **Azure Landing Zones / enterprise-scale** policy set
(https://github.com/Azure/Enterprise-Scale/, surfaced via azadvertizer) and adapted to
standalone EPAC custom definitions. Starts with one control — `apim-tls` (APIM must use
TLS 1.2, upstream `Deny-APIM-TLS`) — and is **expandable**: add another builder to
`DEFINITIONS` and it is picked up automatically.

This generator emits **definitions only** (no bundling initiative): its category is
`API Management`, which the built-in producer already owns (`integration-esn-apim`), so an
overlay initiative would collide. Add one under a distinct category if/when the family grows.

> The ALZ source stores policy expressions ARM-template-escaped as `[[…]`; here they are
> un-escaped to the single-bracket `[…]` form a standalone policy definition uses. The policy
> *rule* (and the upstream `Deny` default) is preserved.

Output (existing `apim-*.json` are replaced): catalogue/definitions/custom/az-apim/apim-*.json
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # flows/ root
from shared.paths import CATALOGUE_DIR  # noqa: E402  the ONE catalogue path

_EPAC = "https://raw.githubusercontent.com/Azure/enterprise-azure-policy-as-code/main/Schemas"
SCHEMA_DEF = f"{_EPAC}/policy-definition-schema.json"
SOURCE = "https://github.com/Azure/Enterprise-Scale/"
ALZ_CLOUDS = ["AzureCloud", "AzureChinaCloud", "AzureUSGovernment"]
OUT = CATALOGUE_DIR / "definitions" / "custom" / "az-apim"

# The APIM `customProperties` keys that indicate a legacy TLS protocol is *enabled*.
_TLS_LEGACY_KEYS = [
    "microsoft.windowsazure.apimanagement.gateway.security.protocols.tls10",
    "microsoft.windowsazure.apimanagement.gateway.security.protocols.tls11",
]


def _effect_param(default):
    return {
        "type": "String",
        "allowedValues": ["Audit", "Deny", "Disabled"],
        "defaultValue": default,
        "metadata": {"displayName": "Effect",
                     "description": "Enable or disable the execution of the policy"},
    }


def apim_tls():
    """APIM services should use TLS 1.2 — denies/audits services with TLS 1.0/1.1 enabled.

    Adapted from the ALZ `Deny-APIM-TLS` definition; effect default `Deny` preserved.
    """
    field = "Microsoft.ApiManagement/service/customProperties"
    # For each legacy protocol, flag it when present as `"…":"true"` or `"…":true`.
    legacy_enabled = []
    for key in _TLS_LEGACY_KEYS:
        for literal in (f'"{key}":"true"', f'"{key}":true'):
            legacy_enabled.append({
                "value": f"[indexof(toLower(string(field('{field}'))), '{literal}')]",
                "greater": 0,
            })
    return {
        "$schema": SCHEMA_DEF,
        "name": "apim-tls",
        "properties": {
            "displayName": "API Management services should use TLS version 1.2",
            "description": "Azure API Management service should use TLS version 1.2",
            "policyType": "Custom",
            "mode": "All",
            "metadata": {
                "version": "1.0.0",
                "category": "API Management",
                "source": SOURCE,
                "alzPolicy": "Deny-APIM-TLS",
                "alzCloudEnvironments": ALZ_CLOUDS,
            },
            "parameters": {"effect": _effect_param("Deny")},
            "policyRule": {
                "if": {"allOf": [
                    {"field": "type", "equals": "Microsoft.ApiManagement/service"},
                    {"anyOf": legacy_enabled},
                ]},
                "then": {"effect": "[parameters('effect')]"},
            },
        },
    }


# Expandable registry — add more apim-* builders here.
DEFINITIONS = [apim_tls]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in glob.glob(str(OUT / "apim-*.json")):          # full regenerate
        os.remove(f)

    written = []
    for builder in DEFINITIONS:
        d = builder()
        (OUT / f"{d['name']}.json").write_text(
            json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(d["name"])

    print(f"definitions: {len(written)} -> {OUT}")
    for name in written:
        print(f"  {name}")


if __name__ == "__main__":
    main()
