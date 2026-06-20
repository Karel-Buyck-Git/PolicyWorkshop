"""Generate the dlw-az-tagging Azure Policy definition(s) from the DLW mandatory-tag
convention, plus a `tagging` initiative that bundles them.

Policy-side mirror of `getResourceTags.bicep`: where the Bicep module *applies* the
organisation's mandatory tags at deploy time, this policy *verifies* their presence at
the platform — catching resources created outside the module. It validates tag
**presence** only (values are owned by the deploying template); land as `Audit`
(brownfield discovery), then flip the initiative's `effect` to `Deny` to enforce.

Outputs (existing `tagging-*.json` in the family folder are replaced):
  - catalogue/definitions/custom/dlw-az-tagging/tagging-*.json   one policyDefinition
  - catalogue/initiatives/management/essential/tagging/management-esn-tagging.*
    the `tagging` initiative, using the shared brand-neutral within-limit asset naming
    (flows/shared/naming.py) — identical in shape to the built-in producer's groups.

EPAC asset names follow `shared/naming.py`; the **policy rule** (the mandatory-tag list,
the presence check) is this generator's own. Run on demand; not part of the built-in chain.
"""
import glob
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # flows/ root
from shared.paths import CATALOGUE_DIR  # noqa: E402  the ONE catalogue path
from shared.mdtable import slugify, md_escape  # noqa: E402
from shared import naming  # noqa: E402  shared EPAC-asset naming (brand-neutral, within-limit)

_EPAC = "https://raw.githubusercontent.com/Azure/enterprise-azure-policy-as-code/main/Schemas"
SCHEMA_DEF = f"{_EPAC}/policy-definition-schema.json"
SCHEMA_POLICYSET = f"{_EPAC}/policy-set-definition-schema.json"
SCHEMA_ASSIGNMENT = f"{_EPAC}/policy-assignment-schema.json"
SCHEMA_EXEMPTIONS = f"{_EPAC}/policy-exemption-schema.json"

SOURCE = "getResourceTags.bicep"
OUT = CATALOGUE_DIR / "definitions" / "custom" / "dlw-az-tagging"

# The convention the policy enforces (edit here to change the mandatory set, then re-run).
MANDATORY_TAGS = ["environment", "costCenter", "workload", "owner", "creationDate", "service"]
OPTIONAL_TAGS = ["description"]            # present-but-not-validated; deployers may add more
DEF_NAME = "tagging-require-mandatory-tags"

# ---- 'tagging' initiative (a distinct category from the built-in 'Tags' group) ----
# EPAC asset names use the shared convention (flows/shared/naming.py); the placement is
# 'Tagging' (not 'Tags') so the overlay name does not collide with the built-in
# `management-esn-tags` group.
INIT_DOMAIN = "Management"
INIT_TIER = "Essential"
INIT_CATEGORY = "Tagging"          # leaf category (folder slug = 'tagging')
INIT_CAT_ABBR = "tagging"          # custom category code (not a built-in resource category)
INIT_NAME = f"{slugify(INIT_DOMAIN)}-{naming.tier_code(INIT_TIER)}-{INIT_CAT_ABBR}"  # brand-neutral, <=24
INIT_DISPLAY = naming.display_name(INIT_DOMAIN, INIT_TIER, INIT_CATEGORY)
INIT_DIR = CATALOGUE_DIR / "initiatives" / "management" / "essential" / "tagging"
INIT_RATIONALE = (
    "**Essential** — Mandatory-tag guardrails for every taggable Azure resource: audits "
    "(or denies) resources missing the organisation's mandatory tags. Consistent tags are "
    "baseline hygiene — they underpin cost allocation, ownership, automation and incident "
    "response. Effects default to Audit and are tuned from a single initiative parameter."
)


def cap(text, limit=naming.DESCRIPTION_MAX):
    """Trim to the Azure description hard limit (512)."""
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def catalogue_version():
    """Reuse the producer's catalogue version when present, else today's UTC date."""
    cat = CATALOGUE_DIR / "catalogue.json"
    if cat.exists():
        try:
            return json.loads(cat.read_text(encoding="utf-8")).get("catalogueVersion") or ""
        except (json.JSONDecodeError, OSError):
            pass
    return datetime.now(timezone.utc).strftime("%Y.%m.%d")


def build_definition():
    """The mandatory-tag presence policy. The `anyOf` (missing-or-empty per tag) is
    generated from MANDATORY_TAGS so the rule stays in sync with the convention."""
    missing = []
    for tag in MANDATORY_TAGS:
        missing.append({"field": f"tags['{tag}']", "exists": "false"})
        missing.append({"field": f"tags['{tag}']", "equals": ""})

    desc = cap(
        f"Audits or denies resources missing (or with an empty value for) any mandatory tag "
        f"({', '.join(MANDATORY_TAGS)}). Validates tag PRESENCE only — the values are supplied by "
        f"the deploying Bicep; {', '.join(OPTIONAL_TAGS)} is optional and not validated, and extra "
        f"tags are allowed. Land as 'Audit' for brownfield discovery, then 'Deny' to enforce on new "
        f"deployments (Deny gates create/update only — it never touches existing resources)."
    )
    return {
        "$schema": SCHEMA_DEF,
        "name": DEF_NAME,
        "properties": {
            "displayName": "Require mandatory tags on resources",
            "description": desc,
            "policyType": "Custom",
            "mode": "Indexed",
            "metadata": {
                "category": "Tags",
                "version": "1.0.0",
                "source": SOURCE,
                "cafCategory": "Governance",
                "checkKind": "presence",
                "mandatoryTags": MANDATORY_TAGS,
                "optionalTags": OPTIONAL_TAGS,
            },
            "parameters": {
                "excludedResourceTypes": {
                    "type": "Array",
                    "defaultValue": [],
                    "metadata": {
                        "displayName": "Excluded resource types",
                        "description": "Resource types matching any of these wildcard patterns are "
                                       "exempt from the tag check. Useful for child/proxy resource "
                                       "types that do not support tags. Example: 'Microsoft.Network/*/*, "
                                       "Microsoft.Insights/diagnosticSettings'.",
                    },
                },
                "effect": {
                    "type": "String",
                    "allowedValues": ["Audit", "Deny", "Disabled"],
                    "defaultValue": "Audit",
                    "metadata": {"displayName": "Effect",
                                 "description": "The effect of the policy (Audit, Deny or Disabled)."},
                },
            },
            "policyRule": {
                "if": {"allOf": [
                    {"count": {"value": "[parameters('excludedResourceTypes')]", "name": "excludedType",
                               "where": {"field": "type", "like": "[current('excludedType')]"}}, "equals": 0},
                    {"anyOf": missing},
                ]},
                "then": {"effect": "[parameters('effect')]"},
            },
        },
    }


def _member_params(src_params):
    """Bubble 'effect' to the initiative parameter; emit every other parameter inline
    with its definition default (mirrors the built-in producer)."""
    mp = {}
    for pname, pdef in src_params.items():
        if pname == "effect":
            mp["effect"] = {"value": "[parameters('effect')]"}
        elif "defaultValue" in pdef:
            mp[pname] = {"value": pdef["defaultValue"]}
    return mp


def build_policyset(members, version):
    policy_defs = []
    for m in members:
        entry = {
            "policyDefinitionReferenceId": m["ref"],
            "policyDefinitionName": m["ref"],  # custom in-repo definition -> referenced by name
            "groupNames": [INIT_TIER],
            "metadata": {"policyName": m["displayName"]},
        }
        mp = _member_params(m["src_params"])
        if mp:
            entry["parameters"] = mp
        policy_defs.append(entry)
    return {
        "$schema": SCHEMA_POLICYSET,
        "name": INIT_NAME,
        "properties": {
            "displayName": INIT_DISPLAY,
            "description": cap(INIT_RATIONALE),
            "policyType": "Custom",
            "metadata": {
                "category": "Tagging",
                "domain": INIT_DOMAIN,
                "tier": INIT_TIER,
                "catalogueVersion": version,
                "source": SOURCE,
                "hasRemediation": False,
            },
            "policyDefinitionGroups": [{"name": INIT_TIER}],
            "parameters": {
                "effect": {
                    "type": "String",
                    "allowedValues": ["Audit", "Deny", "Disabled"],
                    "defaultValue": "Audit",
                    "metadata": {"displayName": "Effect",
                                 "description": "Effect applied to every tagging policy in this initiative."},
                }
            },
            "policyDefinitions": policy_defs,
        },
    }


def build_assignment(members):
    n = len(members)
    return {
        "$schema": SCHEMA_ASSIGNMENT,
        "nodeName": naming.node_name(INIT_DOMAIN, INIT_TIER, INIT_CATEGORY),
        "assignment": {
            "name": INIT_NAME,
            "displayName": INIT_DISPLAY,
            "description": cap(
                f"Deployment scaffold for {n} mandatory-tag polic{'ies' if n != 1 else 'y'}. Effects "
                f"default to Audit via the initiative's 'effect' parameter — set it to Deny to enforce. "
                f"No managed identity is required. Replace all mock references (<root-mg-id>, "
                f"<pac-environment-selector>, <sub-id>) before deploying."
            ),
        },
        "policySetDefinitionName": INIT_NAME,
        "parameters": {},  # 'effect' has a default; override here to deny
        "scope": {"<pac-environment-selector>": ["/providers/Microsoft.Management/managementGroups/<root-mg-id>"]},
        "notScopes": [],
    }


def build_exemptions():
    return {
        "$schema": SCHEMA_EXEMPTIONS,
        "nodeName": naming.node_name(INIT_DOMAIN, INIT_TIER, INIT_CATEGORY, "exemptions"),
        "exemptions": [
            {
                "name": naming.exemption_name(INIT_NAME),
                "displayName": "Example exemption — replace or remove",
                "description": "Template stub. Set the scope/assignment id and the "
                               "policyDefinitionReferenceIds for resource types that should not be tag-governed here.",
                "exemptionCategory": "Waiver",
                "policyAssignmentId": f"/providers/Microsoft.Management/managementGroups/<root-mg-id>"
                                      f"/providers/Microsoft.Authorization/policyAssignments/{INIT_NAME}",
                "policyDefinitionReferenceIds": ["<policy-reference-id>"],
                "scope": "/subscriptions/<sub-id>",
            }
        ],
    }


_MD_HEADER = (
    "| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | "
    "Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |"
)
_MD_SEP = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"


def build_markdown(members):
    lines = [
        f"# {INIT_DISPLAY}", "",
        "## Tier rationale", "", INIT_RATIONALE, "",
        "## Product, purpose & deployment", "",
        "**Product.** Part of DLW's Azure tagging governance as code — generated by "
        "`flows/definition_gen/gen_dlw_tagging_definitions.py` from the dlw MSPE `getResourceTags.bicep` "
        "convention. This initiative bundles the custom `tagging-*` definitions into one assignable set.", "",
        "**Purpose.** Where `getResourceTags.bicep` *applies* mandatory tags at deploy time, these "
        "policies *verify* their presence at the platform — catching resources created outside the module.", "",
        "> ⚠️ **Ships as `Audit`. Enforcement is a decision made at the customer.** Set the initiative's "
        "top-level `effect` parameter to **`Deny`** at assignment time to enforce; leave it at `Audit` to "
        "observe. The policy validates tag **presence** only — values are owned by the deploying Bicep.", "",
        f"**Mandatory tags:** {', '.join(MANDATORY_TAGS)}.  **Optional (not validated):** "
        f"{', '.join(OPTIONAL_TAGS)}.", "",
        "## Usage", "",
        "These are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) artifacts. The member "
        "policies are the custom `tagging-*` definitions under "
        "`catalogue/definitions/custom/dlw-az-tagging/` (referenced by `policyDefinitionName`), so deploy "
        "those alongside this set.", "",
        "**Deployment order:** deploy the `tagging-*` definitions → assign the initiative.", "",
        "## Policies", "", _MD_HEADER, _MD_SEP,
    ]
    for i, m in enumerate(sorted(members, key=lambda x: x["displayName"].lower()), start=1):
        lines.append(
            f"| {i} | {md_escape(m['displayName'])} | {m['ref']} |  | {md_escape(m['description'])} | "
            f"No | No | Audit, Deny, Disabled | Audit | Audit | Audit | "
            f"Tagging | {INIT_DOMAIN} | {m['version']} | Custom | {INIT_TIER} |"
        )
    return "\n".join(lines) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in glob.glob(str(OUT / "tagging-*.json")):       # full regenerate
        os.remove(f)

    definition = build_definition()
    (OUT / f"{DEF_NAME}.json").write_text(
        json.dumps(definition, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    members = [{
        "ref": DEF_NAME,
        "displayName": definition["properties"]["displayName"],
        "description": definition["properties"]["description"],
        "version": definition["properties"]["metadata"]["version"],
        "src_params": definition["properties"]["parameters"],
    }]

    version = catalogue_version()
    INIT_DIR.mkdir(parents=True, exist_ok=True)
    (INIT_DIR / f"{INIT_NAME}.policyset.json").write_text(
        json.dumps(build_policyset(members, version), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (INIT_DIR / f"{INIT_NAME}.assignment.json").write_text(
        json.dumps(build_assignment(members), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (INIT_DIR / f"{INIT_NAME}.exemptions.json").write_text(
        json.dumps(build_exemptions(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (INIT_DIR / f"{INIT_NAME}.md").write_text(build_markdown(members), encoding="utf-8")

    print(f"definitions: {len(members)} -> {OUT}")
    print(f"mandatory tags: {', '.join(MANDATORY_TAGS)}")
    print(f"initiative: {INIT_NAME} ({len(members)} members, catalogueVersion {version}) -> {INIT_DIR}")


if __name__ == "__main__":
    main()
