"""Expand a tiny human ``input.json`` into a structured customer manifest.

Validates the input against ``input.schema.json``, resolves the ``domain/tier/category``
selection against the catalogue, then seeds a fixed-shape manifest: one
``<REPLACE: …>`` placeholder per required parameter the selected initiatives expose
(value-filled from ``input.parameters`` when the human already supplied it). The human
then fills only values; structure is locked by ``manifest.input.schema.json``.
"""
import json

from epac_builder import validate
from epac_builder.bind import required_param_keys
from epac_builder.catalogue import Catalogue


def parse_selection(selection_strings):
    out = []
    for s in selection_strings:
        domain, tier, category = s.split("/")
        out.append({"domain": domain, "category": category, "tier": tier})
    return out


def expand(input_data, catalogue: Catalogue):
    """Return a manifest dict (placeholders for unknowns) from validated input."""
    schema = json.loads((catalogue.dir.parent / "customer" / "manifests"
                         / "input.schema.json").read_text(encoding="utf-8"))
    validate.validate(input_data, schema, "input")

    selection = parse_selection(input_data["selection"])
    groups = catalogue.resolve(selection)

    required = []
    seen = set()
    for g in groups:
        for k in required_param_keys(catalogue.load_artifacts(g)["assignment"]):
            if k not in seen:
                seen.add(k)
                required.append(k)

    supplied = input_data.get("parameters", {})
    defaults = {k: supplied.get(k, f"<REPLACE: {k}>") for k in required}

    # Pin the catalogue precisely, not just by label (#48). The version label is the UTC
    # date, so two releases in one day share it and the assembler's exact-string version
    # gate cannot tell them apart; the contentHash can. Seeded here so the safe pin is the
    # default rather than an opt-in the author has to know about. Omitted only for a
    # pre-#27 catalogue that publishes no contentHash.
    source = {
        "initiatives": "../../catalogue/initiatives",
        "catalogueVersion": catalogue.version,
    }
    content_hash = catalogue.provenance().get("catalogueContentHash")
    if content_hash:
        source["catalogueContentHash"] = content_hash

    return {
        "schemaVersion": 1,
        "customer": input_data["customer"],
        "prefix": "<REPLACE: prefix-slug>",
        "pacOwnerId": "<REPLACE: pacOwnerId-guid>",
        "source": source,
        "output": {"root": "../package", "flavours": ["json"]},
        "environments": [{
            "selector": "<REPLACE: pacSelector>",
            "tenantId": "<REPLACE: tenantId-guid>",
            "deploymentRootScope": "<REPLACE: /providers/Microsoft.Management/managementGroups/root-mg-id>",
            "managedIdentityLocation": "<REPLACE: location>",
            "enforcement": "<REPLACE: Audit-or-hardened>",
            "logAnalyticsWorkspaceId": "<REPLACE: log-analytics-workspace-resource-id>",
        }],
        "allowedLocations": ["<REPLACE: location>"],
        "notScopes": {"<REPLACE: pacSelector>": ["<REPLACE: scope-resource-id>"]},
        "selection": selection,
        "bindings": {"defaults": defaults, "overrides": {}},
        "effectOverrides": [],
        "exemptions": {},
        "metadata": {
            "owner": "<REPLACE: owner-email>",
            "costCenterTag": "<REPLACE: cost-center-tag>",
            "contact": "<REPLACE: contact-name>",
        },
    }
