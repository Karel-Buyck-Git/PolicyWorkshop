"""Bicep renderer: IR -> a management-group-scoped Bicep module at the package root.

Layout written under the package dir (``pkg_dir``):

    main.bicep                         policyDefinitions + policySetDefinitions + assignments + roles
    policies/<name>.definition.json    a custom member policy's `properties` (loadJsonContent)
    policies/<name>.policyset.json     policyset `properties` minus policyDefinitions (loadJsonContent)
    policies/<name>.params.json        bound assignment parameters (when any)
    main.parameters.<selector>.json    per-environment parameter file

The deploy README + pipeline + provenance are added by the packaging step (package.py).
Static JSON is loaded with ``loadJsonContent``; the policyset's ``policyDefinitions`` array
is built inline so custom members can reference the deployed definition resources' ids.
Deterministic output (stable order).
"""
import re
from pathlib import Path

from epac_builder.writeutil import write_json, write_text

PD_API = "2021-06-01"
PS_API = "2021-06-01"
ASG_API = "2022-06-01"
RA_API = "2022-04-01"

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def render(ir, pkg_dir):
    """Write the Bicep module at the package root (``pkg_dir``).

    The deploy README + pipeline + provenance are added by the packaging step.
    """
    root = Path(pkg_dir)
    asg_by_init = {a["initiative"]: a for a in ir["assignments"]}

    # Custom member-policy bodies (loaded by their own resources).
    for defn in ir["definitions"]:
        write_json(root / "policies" / f"{defn['name']}.definition.json", defn["properties"])

    for init in ir["initiatives"]:
        # The policyset's policyDefinitions array is built inline in main.bicep (members
        # may reference custom definition resource ids), so the loaded JSON holds the
        # static remainder only.
        meta = {k: v for k, v in init["policyset"]["properties"].items()
                if k != "policyDefinitions"}
        write_json(root / "policies" / f"{init['name']}.policyset.json", meta)
        asg = asg_by_init[init["name"]]
        if asg["boundParameters"]:
            params = {k: {"value": v} for k, v in asg["boundParameters"].items()}
            write_json(root / "policies" / f"{init['name']}.params.json", params)

    write_text(root / "main.bicep", _main_bicep(ir, asg_by_init))
    for env in ir["environments"]:
        write_json(root / f"main.parameters.{env['selector']}.json", _param_file(env))
    return root


def _bsym(name):
    """A valid Bicep symbolic name (letters, digits, underscore; must start non-digit)."""
    s = "".join(c if (c.isalnum() or c == "_") else "_" for c in name)
    return s if s[:1].isalpha() or s[:1] == "_" else f"_{s}"


def _main_bicep(ir, asg_by_init):
    out = [_HEADER]
    for defn in ir["definitions"]:
        out.append(_policy_definition(defn))
    for init in ir["initiatives"]:
        out.append(_policy_set(init))
    for init in ir["initiatives"]:
        out.append(_assignment(init, asg_by_init[init["name"]]))
    for init in ir["initiatives"]:
        out.append(_role_assignments(init))
    return "\n".join(p for p in out if p)


def _policy_definition(defn):
    sym = _bsym(defn["name"])
    return "\n".join([
        f"resource pd_{sym} 'Microsoft.Authorization/policyDefinitions@{PD_API}' = {{",
        f"  name: '{defn['name']}'",
        f"  properties: loadJsonContent('policies/{defn['name']}.definition.json')",
        "}",
        "",
    ])


def _policy_set(init):
    sym = _bsym(init["name"])
    members = init["policyset"]["properties"].get("policyDefinitions", [])
    return "\n".join([
        f"resource ps_{sym} 'Microsoft.Authorization/policySetDefinitions@{PS_API}' = {{",
        f"  name: '{init['name']}'",
        f"  properties: union(loadJsonContent('policies/{init['name']}.policyset.json'), {{",
        f"    policyDefinitions: {_members_bicep(members)}",
        "  })",
        "}",
        "",
    ])


def _members_bicep(members):
    """The policyDefinitions array as a Bicep literal: built-in members keep their id
    string; custom members reference the deployed ``pd_<name>`` resource's ``.id``."""
    objs = []
    for m in members:
        if "policyDefinitionId" in m:
            id_expr = _bstr(m["policyDefinitionId"])
        else:
            id_expr = f'pd_{_bsym(m["policyDefinitionName"])}.id'
        lines = [
            "      {",
            f"        policyDefinitionReferenceId: {_bstr(m['policyDefinitionReferenceId'])}",
            f"        policyDefinitionId: {id_expr}",
        ]
        if m.get("parameters"):
            lines.append(f"        parameters: {_bval(m['parameters'], 4)}")
        if m.get("groupNames"):
            lines.append(f"        groupNames: {_bval(m['groupNames'], 4)}")
        lines.append("      }")
        objs.append("\n".join(lines))
    return "[\n" + "\n".join(objs) + "\n    ]"


def _bval(x, level=0):
    """Emit a Python value as a Bicep literal (objects/arrays use newline separators)."""
    pad, pad2 = "  " * level, "  " * (level + 1)
    if isinstance(x, dict):
        if not x:
            return "{}"
        items = [f"{pad2}{k if _IDENT.match(k) else _bstr(k)}: {_bval(v, level + 1)}"
                 for k, v in x.items()]
        return "{\n" + "\n".join(items) + f"\n{pad}}}"
    if isinstance(x, list):
        if not x:
            return "[]"
        items = [f"{pad2}{_bval(v, level + 1)}" for v in x]
        return "[\n" + "\n".join(items) + f"\n{pad}]"
    if isinstance(x, bool):
        return "true" if x else "false"
    if x is None:
        return "null"
    if isinstance(x, (int, float)):
        return str(x)
    return _bstr(x)


def _assignment(init, asg):
    sym = _bsym(init["name"])
    name = asg["assignmentName"]
    not_scopes = sorted({s for lst in asg["notScopes"].values() for s in lst})
    lines = [f"resource asg_{sym} 'Microsoft.Authorization/policyAssignments@{ASG_API}' = {{",
             f"  name: '{name}'"]
    if asg["managedIdentity"]["required"]:
        lines.append("  location: location")
        lines.append("  identity: {")
        lines.append("    type: 'SystemAssigned'")
        lines.append("  }")
    lines.append("  properties: {")
    lines.append(f"    policyDefinitionId: ps_{sym}.id")
    lines.append(f"    displayName: {_bstr(asg['displayName'])}")
    if asg["boundParameters"]:
        lines.append(f"    parameters: loadJsonContent('policies/{init['name']}.params.json')")
    if not_scopes:
        rendered = ", ".join(_bstr(s) for s in not_scopes)
        lines.append(f"    notScopes: [ {rendered} ]")
    lines.append("  }")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _role_assignments(init):
    if not init["hasRemediation"]:
        return ""
    sym = _bsym(init["name"])
    blocks = []
    for i, rid in enumerate(init["roleDefinitionIds"]):
        blocks.append("\n".join([
            f"resource ra_{sym}_{i} 'Microsoft.Authorization/roleAssignments@{RA_API}' = {{",
            f"  name: guid(managementGroup().id, '{init['name']}', '{_role_guid(rid)}')",
            "  properties: {",
            f"    roleDefinitionId: {_bstr(rid)}",
            f"    principalId: asg_{sym}.identity.principalId",
            "    principalType: 'ServicePrincipal'",
            "  }",
            "}",
            "",
        ]))
    return "\n".join(blocks)


def _role_guid(role_id):
    return role_id.rstrip("/").split("/")[-1]


def _bstr(value):
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


def _param_file(env):
    params = {}
    if env.get("managedIdentityLocation"):
        params["location"] = {"value": env["managedIdentityLocation"]}
    return {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
        "contentVersion": "1.0.0.0",
        "parameters": params,
    }


_HEADER = "\n".join([
    "// Generated by the epac-builder (consumer). Do not hand-edit.",
    "targetScope = 'managementGroup'",
    "",
    "@description('Location for system-assigned identities (remediation).')",
    "param location string = deployment().location",
    "",
])
