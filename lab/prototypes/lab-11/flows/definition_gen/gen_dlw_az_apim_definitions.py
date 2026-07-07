"""Generate custom API Management (APIM) hardening definitions (`dlw-az-apim`).

Definitions derived from the **Azure Landing Zones / enterprise-scale** policy set
(github.com/Azure/Enterprise-Scale, via azadvertizer). First control: `apim-tls`
(APIM must use TLS 1.2, upstream `Deny-APIM-TLS`). **Expandable** — add a builder to
`DEFINITIONS`.

Declares an **Enrich** overlay: the `apim-*` definitions are added as members of the
existing built-in `integration-esn-apim` initiative (their category, `API Management`, is
owned by the built-in producer). The ALZ source's ARM-escaped `[[…]` expressions are
un-escaped to the standalone `[…]` form; the rule and the `Deny` default are preserved.

Run standalone (preview — requires the built-in group to already exist) or via the
producer's `apply_overlays.py` step:

    python flows/definition_gen/gen_dlw_az_apim_definitions.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # flows/ root
from definition_gen import scaffold  # noqa: E402
from definition_gen.scaffold import Overlay, Enrich  # noqa: E402

SOURCE = "https://github.com/Azure/Enterprise-Scale/"
ALZ_CLOUDS = ["AzureCloud", "AzureChinaCloud", "AzureUSGovernment"]
FAMILY = "dlw-az-apim"

# APIM `customProperties` keys that indicate a legacy TLS protocol is *enabled*.
_TLS_LEGACY_KEYS = [
    "microsoft.windowsazure.apimanagement.gateway.security.protocols.tls10",
    "microsoft.windowsazure.apimanagement.gateway.security.protocols.tls11",
]


def _effect_param(default):
    return {"type": "String", "allowedValues": ["Audit", "Deny", "Disabled"], "defaultValue": default,
            "metadata": {"displayName": "Effect", "description": "Enable or disable the execution of the policy"}}


def apim_tls():
    """APIM services should use TLS 1.2 (ALZ `Deny-APIM-TLS`); effect default `Deny`."""
    field = "Microsoft.ApiManagement/service/customProperties"
    legacy_enabled = []
    for key in _TLS_LEGACY_KEYS:
        for literal in (f'"{key}":"true"', f'"{key}":true'):
            legacy_enabled.append({
                "value": f"[indexof(toLower(string(field('{field}'))), '{literal}')]", "greater": 0})
    return {
        "name": "apim-tls",
        "properties": {
            "displayName": "API Management services should use TLS version 1.2",
            "description": "Azure API Management service should use TLS version 1.2",
            "policyType": "Custom",
            "mode": "All",
            "metadata": {
                "version": "1.0.0", "category": "API Management", "source": SOURCE,
                "alzPolicy": "Deny-APIM-TLS", "alzCloudEnvironments": ALZ_CLOUDS,
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


def build():
    return Overlay(
        family=FAMILY,
        placement=Enrich("Integration", "Essential", "API Management"),
        definitions=[b() for b in DEFINITIONS],
        source=SOURCE,
    )


def main():
    result = scaffold.apply(build())
    print(f"[{FAMILY}] {len(DEFINITIONS)} definition(s) -> {result['kind']} "
          f"'{result['target_name']}' (+members: {', '.join(result['added']) or 'none new'})")


if __name__ == "__main__":
    main()
