"""Canonical, flavour-neutral IR for the epac-builder.

``build_ir`` resolves binding + posture for every selected group and assembles the
in-memory model the three renderers consume (design §4). Building it once is what
keeps JSON / Terraform / Bicep consistent. The model is pure data; each renderer is
a function ``IR -> files``.
"""
import copy
import hashlib
import json

from epac_builder.bind import (
    apply_posture, bind_parameters, resolve_posture,
)

COMPANY_PREFIX = "company"   # the producer's default prefix in catalogue artifacts


def reprefix(name, prefix):
    """Swap the leading producer prefix token for the customer prefix."""
    head, _, rest = name.partition("-")
    return f"{prefix}-{rest}" if rest and head == COMPANY_PREFIX else name


def reprefix_node(node_name, prefix):
    """Swap the leading path segment of an EPAC ``nodeName`` (``/company/…`` -> ``/prefix/…``)."""
    parts = node_name.split("/")
    if len(parts) > 1 and parts[1] == COMPANY_PREFIX:
        parts[1] = prefix
    return "/".join(parts)


def manifest_hash(manifest):
    blob = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build_ir(manifest, catalogue, groups):
    prefix = manifest["prefix"]
    environments = manifest["environments"]
    bindings = manifest.get("bindings", {}) or {}
    all_overrides = manifest.get("effectOverrides", []) or []
    # selection items keyed for per-selection posture/scope lookup
    sel_by_key = {(s["domain"], s["category"]): s for s in manifest["selection"]}
    sel_star = {s["domain"]: s for s in manifest["selection"] if s["category"] == "*"}

    ir = {
        "identity": {
            "pacOwnerId": manifest["pacOwnerId"],
            "prefix": prefix,
            "customer": manifest["customer"],
        },
        "catalogueVersion": catalogue.version,
        "environments": [_env(e, manifest.get("notScopes", {})) for e in environments],
        "initiatives": [],
        "assignments": [],
        "roleAssignments": [],
        "exemptions": _exemptions(manifest),
        "warnings": [],
        "lineage": {
            "manifestHash": manifest_hash(manifest),
            "catalogueVersion": catalogue.version,
            "groups": [],
        },
    }

    for group in groups:
        art = catalogue.load_artifacts(group)
        dom, tier, cat = group["_slug"]
        sel = sel_by_key.get((dom, cat)) or sel_star.get(dom)

        name = reprefix(group["name"], prefix)
        posture, warn = resolve_posture(group, sel, environments)
        if warn:
            ir["warnings"].append(warn)

        group_key = f"{dom}/{tier}/{cat}"
        group_overrides = [o for o in all_overrides if o.get("group") == group_key]
        policyset = copy.deepcopy(art["policyset"])
        policyset["name"] = name
        apply_posture(policyset, posture, group_overrides)

        roles = art.get("roles") or {}
        role_ids = roles.get("roleDefinitionIds", [])
        has_remediation = bool(group.get("hasRemediation") or role_ids)

        bound = bind_parameters(art, bindings)

        ir["initiatives"].append({
            "name": name,
            "source": group["dir"],
            "policyset": policyset,
            "hasRemediation": has_remediation,
            "roleDefinitionIds": role_ids,
        })

        scopes, not_scopes = _scopes(environments, sel, manifest.get("notScopes", {}))
        ir["assignments"].append({
            "initiative": name,
            "displayName": policyset["properties"]["displayName"],
            "description": art["assignment"]["assignment"].get("description", ""),
            "nodeName": reprefix_node(art["assignment"]["nodeName"], prefix),
            "boundParameters": bound,
            "scopes": scopes,
            "notScopes": not_scopes,
            "effectPosture": posture,
            "managedIdentity": {"required": has_remediation},
            "group": group_key,
        })

        if has_remediation:
            for env in environments:
                for scope in scopes.get(env["selector"], []):
                    for rid in role_ids:
                        ir["roleAssignments"].append({
                            "assignment": name, "selector": env["selector"],
                            "roleDefinitionId": rid, "scope": scope,
                        })

        ir["lineage"]["groups"].append({
            "group": group_key,
            "name": name,
            "source": group["dir"],
            "policyCount": group.get("policyCount"),
            "hasRemediation": has_remediation,
        })

    return ir


def _env(e, manifest_not_scopes):
    return {
        "selector": e["selector"],
        "tenantId": e["tenantId"],
        "rootScope": e["deploymentRootScope"],
        "managedIdentityLocation": e.get("managedIdentityLocation"),
        "enforcement": e["enforcement"],
        "logAnalyticsWorkspaceId": e.get("logAnalyticsWorkspaceId"),
        "notScopes": manifest_not_scopes.get(e["selector"], []),
    }


def _scopes(environments, sel, manifest_not_scopes):
    """Per-selector scope + notScope maps for one group."""
    scopes, not_scopes = {}, {}
    sel_scope = (sel or {}).get("scope") or {}
    sel_not = (sel or {}).get("notScopes") or {}
    for e in environments:
        selector = e["selector"]
        scopes[selector] = sel_scope.get(selector, [e["deploymentRootScope"]])
        merged = list(manifest_not_scopes.get(selector, [])) + list(sel_not.get(selector, []))
        if merged:
            not_scopes[selector] = merged
    return scopes, not_scopes


def _exemptions(manifest):
    out = []
    for selector, items in (manifest.get("exemptions", {}) or {}).items():
        for ex in items:
            out.append(dict(ex, selector=selector))
    return out
