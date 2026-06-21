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

def set_definition_name(group_name, prefix):
    """Customer-scoped policy set name: prepend the prefix to the brand-neutral
    catalogue name (policy set names allow up to 64 chars)."""
    return f"{prefix}-{group_name}"


def customer_node(node_name, prefix):
    """Prepend the customer segment to the catalogue's brand-neutral nodeName
    (`/<domain>/…/` -> `/<prefix>/<domain>/…/`)."""
    return f"/{prefix}{node_name}"


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

        group_name = group["name"]                      # brand-neutral catalogue name (<=24)
        set_name = set_definition_name(group_name, prefix)   # customer-scoped policy set name
        posture, warn = resolve_posture(group, sel, environments)
        if warn:
            ir["warnings"].append(warn)

        group_key = f"{dom}/{tier}/{cat}"
        group_overrides = [o for o in all_overrides if o.get("group") == group_key]
        policyset = copy.deepcopy(art["policyset"])
        policyset["name"] = set_name
        apply_posture(policyset, posture, group_overrides)

        roles = art.get("roles") or {}
        role_ids = roles.get("roleDefinitionIds", [])
        has_remediation = bool(group.get("hasRemediation") or role_ids)

        bound = bind_parameters(art, bindings)

        ir["initiatives"].append({
            "name": set_name,
            "source": group["dir"],
            "policyset": policyset,
            "hasRemediation": has_remediation,
            "roleDefinitionIds": role_ids,
        })

        display = policyset["properties"]["displayName"]
        scopes, not_scopes = _scopes(environments, sel, manifest.get("notScopes", {}))
        ir["assignments"].append({
            "initiative": set_name,                      # policySetDefinitionName it references
            "assignmentName": group_name,                # the assignment's own name (<=24, no prefix)
            "displayName": display,
            "description": _assignment_description(display, group.get("policyCount"),
                                                   posture, has_remediation),
            "nodeName": customer_node(art["assignment"]["nodeName"], prefix),
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
                            "assignment": group_name, "selector": env["selector"],
                            "roleDefinitionId": rid, "scope": scope,
                        })

        ir["lineage"]["groups"].append({
            "group": group_key,
            "name": set_name,
            "assignmentName": group_name,
            "source": group["dir"],
            "policyCount": group.get("policyCount"),
            "hasRemediation": has_remediation,
        })

    return ir


def _assignment_description(display, policy_count, posture, has_remediation):
    """A clean, customer-facing description — the catalogue scaffold's mock-replacement
    boilerplate no longer applies once the assembler has bound real values."""
    count = f"{policy_count} polic{'ies' if policy_count != 1 else 'y'}" if policy_count else "policies"
    parts = [f"{display}: {count}, effect posture '{posture}'."]
    if has_remediation:
        parts.append("Contains Modify/DeployIfNotExists policies — a managed identity is "
                     "assigned and remediation runs after deployment.")
    return " ".join(parts)


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
