"""Authoring contract for `definition_gen` overlays.

A generator declares **what** to add (definitions) and **where** (a `Placement`); the
scaffold derives **how** — paths, names, the EPAC artifact set — from `shared/naming.py`,
so a gen can't hand-roll an inconsistent path or a colliding name. Two placements:

- ``NewGroup`` — the custom definitions get their own initiative in a fresh
  ``(domain, tier, category)`` slot (the dlw-naming / dlw-tagging model).
- ``Enrich`` — the custom definitions are added as **members of an existing built-in
  initiative** (e.g. `apim-tls` -> `integration-esn-apim`).

``apply(overlay)`` writes the definitions and the initiative (or enriches the built-in),
returning a manifest record for the producer's `apply_overlays` step to register.
Misconfiguration (bad path, colliding name, missing Enrich target) raises `OverlayError`.
"""
import glob
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from shared.paths import CATALOGUE_DIR, DEFINITIONS_DIR, INITIATIVES_DIR
from shared.mdtable import md_escape, slugify
from shared import naming

_EPAC = "https://raw.githubusercontent.com/Azure/enterprise-azure-policy-as-code/main/Schemas"
SCHEMA_DEF = f"{_EPAC}/policy-definition-schema.json"
SCHEMA_POLICYSET = f"{_EPAC}/policy-set-definition-schema.json"
SCHEMA_ASSIGNMENT = f"{_EPAC}/policy-assignment-schema.json"
SCHEMA_EXEMPTIONS = f"{_EPAC}/policy-exemption-schema.json"


class OverlayError(Exception):
    """A generator's overlay is misconfigured (fail-fast governance)."""


@dataclass
class NewGroup:
    """Place the definitions in their own initiative at a fresh slot."""
    domain: str
    tier: str
    category: str
    category_abbr: str            # custom short code (the category isn't a built-in resource)
    rationale: str                # the tier-rationale paragraph (initiative description)
    metadata_category: str = ""   # policyset metadata.category label; defaults to `category`


@dataclass
class Enrich:
    """Add the definitions as members of an existing built-in initiative."""
    domain: str
    tier: str
    category: str                 # a real built-in (domain, tier, category) group


@dataclass
class Overlay:
    family: str                   # folder under definitions/custom/, e.g. "dlw-az-naming"
    placement: object             # NewGroup | Enrich
    definitions: list             # list of EPAC policyDefinition dicts (authored by the gen)
    source: str = ""
    usage_md: list = field(default_factory=list)   # optional extra markdown lines (NewGroup .md)


# ---------------------------------------------------------------------------
# public entry
# ---------------------------------------------------------------------------

def apply(overlay, version=None):
    """Write an overlay's definitions + initiative/enrichment. Returns a manifest record."""
    version = version or catalogue_version()
    _write_definitions(overlay.family, overlay.definitions)
    members = _members(overlay.definitions)
    if isinstance(overlay.placement, NewGroup):
        return _apply_new_group(overlay, members, version)
    if isinstance(overlay.placement, Enrich):
        return _apply_enrich(overlay, members, version)
    raise OverlayError(
        f"overlay '{overlay.family}': unknown placement {type(overlay.placement).__name__}")


def catalogue_version():
    cat = CATALOGUE_DIR / "catalogue.json"
    if cat.exists():
        try:
            return json.loads(cat.read_text(encoding="utf-8")).get("catalogueVersion") or ""
        except (json.JSONDecodeError, OSError):
            pass
    return datetime.now(timezone.utc).strftime("%Y.%m.%d")


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------

def _write_json(path, obj, schema_url=None):
    if schema_url:
        obj = {"$schema": schema_url, **{k: v for k, v in obj.items() if k != "$schema"}}
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8", newline="\n")  # LF on every host (#52)


def _write_definitions(family, definitions):
    fam_dir = DEFINITIONS_DIR / "custom" / family
    fam_dir.mkdir(parents=True, exist_ok=True)
    for f in glob.glob(str(fam_dir / "*.json")):          # full regenerate of the family
        os.remove(f)
    for d in definitions:
        _write_json(fam_dir / f"{d['name']}.json", d, SCHEMA_DEF)


def _members(definitions):
    out = []
    for d in definitions:
        p = d["properties"]
        out.append({
            "ref": d["name"],
            "displayName": p["displayName"],
            "description": p.get("description", ""),
            "version": (p.get("metadata") or {}).get("version", "1.0.0"),
            "params": p.get("parameters") or {},
        })
    return out


# Parameters a NewGroup promotes to the *initiative* level instead of baking each
# member's default inline: 'effect' (tuned via posture) and 'customerAbbreviation'
# (the per-customer naming anchor — bound from the manifest, never frozen to a brand).
BUBBLED_TO_INITIATIVE = ("effect", "customerAbbreviation")


def _bubbled_params(params):
    """NewGroup: wire bubbled params to the initiative parameter; emit other defaults inline."""
    mp = {}
    for pname, pdef in params.items():
        if pname in BUBBLED_TO_INITIATIVE:
            mp[pname] = {"value": f"[parameters('{pname}')]"}
        elif "defaultValue" in pdef:
            mp[pname] = {"value": pdef["defaultValue"]}
    return mp


def _customer_abbr_param(definitions):
    """The shared ``customerAbbreviation`` param definition if any member declares it, else None.

    Naming members carry it; tagging/apim NewGroups don't — so a NewGroup only grows an
    initiative-level ``customerAbbreviation`` (and the assignment ``<REPLACE:>`` mock) when at
    least one member actually anchors on it, keeping other overlays byte-identical.
    """
    for d in definitions:
        ca = (d["properties"].get("parameters") or {}).get("customerAbbreviation")
        if ca:
            return ca
    return None


def _baked_params(params):
    """Enrich: bake every parameter (incl. effect) to its definition default."""
    return {pname: {"value": pdef["defaultValue"]}
            for pname, pdef in params.items() if "defaultValue" in pdef}


def _effect_default(definitions):
    for d in definitions:
        eff = (d["properties"].get("parameters") or {}).get("effect")
        if eff and "defaultValue" in eff:
            return eff["defaultValue"]
    return "Audit"


def _effect_param(default, description):
    return {"type": "String", "allowedValues": ["Audit", "Deny", "Disabled"], "defaultValue": default,
            "metadata": {"displayName": "Effect", "description": description}}


def _initiative_params(definitions, eff_default):
    """Initiative-level parameters: always 'effect'; 'customerAbbreviation' when members use it.

    Reusing the member's own ``customerAbbreviation`` definition (String + neutral defaultValue)
    keeps the schema single-sourced; the assignment carries a ``<REPLACE:>`` mock so the assembler
    forces the customer to bind it rather than silently inheriting the fallback default.
    """
    params = {"effect": _effect_param(
        eff_default, "Effect applied to every policy in this initiative.")}
    ca = _customer_abbr_param(definitions)
    if ca:
        params["customerAbbreviation"] = ca
    return params


def cap(text, limit=naming.DESCRIPTION_MAX):
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _group_dir(domain, tier, category):
    return INITIATIVES_DIR / slugify(domain) / slugify(tier) / slugify(category)


# ---------------------------------------------------------------------------
# placement: NewGroup
# ---------------------------------------------------------------------------

def _apply_new_group(overlay, members, version):
    ng = overlay.placement
    name = naming.compose_name(ng.domain, ng.tier, ng.category_abbr)
    if len(name) > naming.ASSIGNMENT_NAME_MAX:
        raise OverlayError(f"overlay '{overlay.family}': name '{name}' exceeds "
                           f"{naming.ASSIGNMENT_NAME_MAX} chars — pick a shorter category_abbr.")
    group_dir = _group_dir(ng.domain, ng.tier, ng.category)
    display = naming.display_name(ng.domain, ng.tier, ng.category)
    eff_default = _effect_default(overlay.definitions)

    _write_json(group_dir / f"{name}.policyset.json",
                _new_group_policyset(overlay, members, name, display, version, eff_default),
                SCHEMA_POLICYSET)
    _write_json(group_dir / f"{name}.assignment.json",
                _new_group_assignment(overlay, members, name, display), SCHEMA_ASSIGNMENT)
    _write_json(group_dir / f"{name}.exemptions.json", _new_group_exemptions(ng, name),
                SCHEMA_EXEMPTIONS)
    (group_dir / f"{name}.md").write_text(_new_group_md(overlay, members, name, display),
                                          encoding="utf-8", newline="\n")

    record = {
        "domain": ng.domain, "tier": ng.tier, "category": ng.category, "name": name,
        "dir": str(group_dir.relative_to(CATALOGUE_DIR)).replace("\\", "/"),
        "policyCount": len(members), "hasRemediation": False, "custom": True,
    }
    return {"kind": "new", "name": name, "record": record}


def _new_group_policyset(overlay, members, name, display, version, eff_default):
    ng = overlay.placement
    group = naming.tier_display(ng.tier)
    policy_defs = []
    for m in members:
        entry = {
            "policyDefinitionReferenceId": m["ref"],
            "policyDefinitionName": m["ref"],
            "groupNames": [group],
            "metadata": {"policyName": m["displayName"], "custom": True},
        }
        mp = _bubbled_params(m["params"])
        if mp:
            entry["parameters"] = mp
        policy_defs.append(entry)
    return {
        "name": name,
        "properties": {
            "displayName": display,
            "description": cap(ng.rationale),
            "policyType": "Custom",
            "metadata": {
                "category": ng.metadata_category or ng.category,
                "domain": ng.domain, "tier": ng.tier,
                "catalogueVersion": version, "source": overlay.source,
                "hasRemediation": False, "custom": True,
            },
            "policyDefinitionGroups": [{"name": group}],
            "parameters": _initiative_params(overlay.definitions, eff_default),
            "policyDefinitions": policy_defs,
        },
    }


def _new_group_assignment(overlay, members, name, display):
    ng = overlay.placement
    n = len(members)
    # Assignment-level mocks the assembler binds fail-fast from the manifest. 'effect' is tuned via
    # posture, so it is NOT a mock here; 'customerAbbreviation' (naming's per-customer anchor) is —
    # emitted only when the initiative exposes it, so tagging/apim assignments stay parameter-free.
    parameters = {}
    if _customer_abbr_param(overlay.definitions):
        parameters["customerAbbreviation"] = "<REPLACE: customerAbbreviation>"
    return {
        "nodeName": naming.node_name(ng.domain, ng.tier, ng.category),
        "assignment": {
            "name": name, "displayName": display,
            "description": cap(
                f"Deployment scaffold for {n} custom polic{'ies' if n != 1 else 'y'} "
                f"({overlay.family}). Tune via the initiative's 'effect' parameter. No managed "
                f"identity is required. Replace all mock references (<root-mg-id>, "
                f"<pac-environment-selector>, <sub-id>) before deploying."),
        },
        # definitionEntry, not a flat policySetDefinitionName — EPAC 11.x rejects the latter on a
        # leaf node (#22). Mirrors build_assignment() in create_initiatives.py; the two emitters
        # produce the same artifact shape for built-in and custom-overlay groups respectively.
        "definitionEntry": {"policySetName": name, "displayName": display},
        "parameters": parameters,
        "scope": {"<pac-environment-selector>": ["/providers/Microsoft.Management/managementGroups/<root-mg-id>"]},
        "notScopes": [],
    }


def _new_group_exemptions(ng, name):
    return {
        "nodeName": naming.node_name(ng.domain, ng.tier, ng.category, "exemptions"),
        "exemptions": [{
            "name": naming.exemption_name(name),
            "displayName": "Example exemption — replace or remove",
            "description": "Template stub. Set the scope/assignment id and the "
                           "policyDefinitionReferenceIds for policies that do not apply.",
            "exemptionCategory": "Waiver",
            "policyAssignmentId": f"/providers/Microsoft.Management/managementGroups/<root-mg-id>"
                                  f"/providers/Microsoft.Authorization/policyAssignments/{name}",
            "policyDefinitionReferenceIds": ["<policy-reference-id>"],
            "scope": "/subscriptions/<sub-id>",
        }],
    }


_MD_HEADER = (
    "| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | "
    "Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |"
)
_MD_SEP = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"


def _new_group_md(overlay, members, name, display):
    ng = overlay.placement
    cat = ng.metadata_category or ng.category
    lines = [f"# {display}", "", "## Tier rationale", "", ng.rationale, ""]
    lines += list(overlay.usage_md)
    lines += ["## Policies", "", _MD_HEADER, _MD_SEP]
    for i, m in enumerate(sorted(members, key=lambda x: x["displayName"].lower()), start=1):
        lines.append(
            f"| {i} | {md_escape(m['displayName'])} | {m['ref']} |  | {md_escape(m['description'])} | "
            f"No | No | Audit, Deny, Disabled | Audit | Audit | Audit | "
            f"{cat} | {ng.domain} | {m['version']} | Custom | {ng.tier} |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# placement: Enrich
# ---------------------------------------------------------------------------

def _apply_enrich(overlay, members, version):
    en = overlay.placement
    target_name = naming.name(en.domain, en.tier, en.category)   # the built-in group name
    group_dir = _group_dir(en.domain, en.tier, en.category)
    ps_path = group_dir / f"{target_name}.policyset.json"
    if not ps_path.exists():
        raise OverlayError(
            f"overlay '{overlay.family}': Enrich target '{target_name}' not found at {ps_path} — the "
            f"built-in group {en.domain}/{en.tier}/{en.category} must exist (run create_initiatives first).")

    ps = json.loads(ps_path.read_text(encoding="utf-8"))
    group = naming.tier_display(en.tier)
    existing = {m.get("policyDefinitionReferenceId") for m in ps["properties"]["policyDefinitions"]}
    added = []
    for m in members:
        if m["ref"] in existing:
            continue
        entry = {
            "policyDefinitionReferenceId": m["ref"],
            "policyDefinitionName": m["ref"],
            "groupNames": [group],
            "metadata": {"policyName": m["displayName"], "custom": True},
        }
        bp = _baked_params(m["params"])
        if bp:
            entry["parameters"] = bp
        ps["properties"]["policyDefinitions"].append(entry)
        added.append(m["ref"])
    ps["properties"].setdefault("metadata", {})["hasCustomMembers"] = True
    _write_json(ps_path, ps, ps.get("$schema"))

    return {"kind": "enrich", "target_name": target_name,
            "dir": str(group_dir.relative_to(CATALOGUE_DIR)).replace("\\", "/"),
            "added": added, "member_count": len(ps["properties"]["policyDefinitions"])}
