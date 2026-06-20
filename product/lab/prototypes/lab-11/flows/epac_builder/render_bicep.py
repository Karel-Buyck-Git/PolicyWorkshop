"""Bicep renderer: IR -> a management-group-scoped Bicep module.

Layout written under ``<out>/bicep/``:

    main.bicep                         policySetDefinitions + assignments + role assignments
    policies/<name>.policyset.json     the policyset `properties` (loaded via loadJsonContent)
    policies/<name>.params.json        bound assignment parameters (when any)
    main.parameters.<selector>.json    per-environment parameter file
    README.md

JSON content is loaded with ``loadJsonContent`` so no Bicep object literal emitter is
needed and the member arrays stay readable. Deterministic output (stable order).
"""
from pathlib import Path

from epac_builder.writeutil import write_json, write_text

PS_API = "2021-06-01"
ASG_API = "2022-06-01"
RA_API = "2022-04-01"


def render(ir, out_root):
    root = Path(out_root) / "bicep"
    asg_by_init = {a["initiative"]: a for a in ir["assignments"]}

    for init in ir["initiatives"]:
        write_json(root / "policies" / f"{init['name']}.policyset.json",
                   init["policyset"]["properties"])
        asg = asg_by_init[init["name"]]
        if asg["boundParameters"]:
            params = {k: {"value": v} for k, v in asg["boundParameters"].items()}
            write_json(root / "policies" / f"{init['name']}.params.json", params)

    write_text(root / "main.bicep", _main_bicep(ir, asg_by_init))
    for env in ir["environments"]:
        write_json(root / f"main.parameters.{env['selector']}.json", _param_file(env))
    write_text(root / "README.md", _readme(ir))
    return root


def _bsym(name):
    """A valid Bicep symbolic name (letters, digits, underscore; must start non-digit)."""
    s = "".join(c if (c.isalnum() or c == "_") else "_" for c in name)
    return s if s[:1].isalpha() or s[:1] == "_" else f"_{s}"


def _main_bicep(ir, asg_by_init):
    out = [_HEADER]
    for init in ir["initiatives"]:
        out.append(_policy_set(init))
    for init in ir["initiatives"]:
        out.append(_assignment(init, asg_by_init[init["name"]]))
    for init in ir["initiatives"]:
        out.append(_role_assignments(init))
    return "\n".join(p for p in out if p)


def _policy_set(init):
    sym = _bsym(init["name"])
    return "\n".join([
        f"resource ps_{sym} 'Microsoft.Authorization/policySetDefinitions@{PS_API}' = {{",
        f"  name: '{init['name']}'",
        f"  properties: loadJsonContent('policies/{init['name']}.policyset.json')",
        "}",
        "",
    ])


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


def _readme(ir):
    selectors = ", ".join(e["selector"] for e in ir["environments"])
    return "\n".join([
        f"# Bicep scaffold — {ir['identity']['customer']}",
        "",
        f"Catalogue version `{ir['catalogueVersion']}`. Deploy at management-group scope:",
        "",
        "```bash",
        "az deployment mg create \\",
        "  --management-group-id <root-mg-id> --location <loc> \\",
        "  --template-file main.bicep \\",
        f"  --parameters main.parameters.<selector>.json    # {selectors}",
        "```",
        "",
        "Generated by the epac-builder. Re-run the assembler to regenerate; do not hand-edit.",
        "",
    ])


_HEADER = "\n".join([
    "// Generated by the epac-builder (consumer). Do not hand-edit.",
    "targetScope = 'managementGroup'",
    "",
    "@description('Location for system-assigned identities (remediation).')",
    "param location string = deployment().location",
    "",
])
