"""Terraform renderer: IR -> an ``azurerm`` policy module at the package root.

Layout written under the package dir (``pkg_dir``):

    main.tf                       provider + policy set definitions + assignments + role assignments
    variables.tf                  per-environment inputs (management group, location, …)
    environments/<selector>.tfvars

The deploy README + pipeline + provenance are added by the packaging step (package.py).
One Terraform config parameterised per environment via tfvars (pick with
``-var-file``). Member effects are already posture-applied in the IR policyset, so
they render as literal ``parameter_values``. Deterministic output (stable order).
"""
from pathlib import Path

from epac_builder.writeutil import write_text
from epac_builder.hcl import hcl_str, hcl_value, tf_ident


def render(ir, pkg_dir):
    """Write the Terraform module at the package root (``pkg_dir``).

    The deploy README + pipeline + provenance are added by the packaging step.
    """
    root = Path(pkg_dir)
    write_text(root / "main.tf", _main_tf(ir))
    write_text(root / "variables.tf", _variables_tf())
    for env in ir["environments"]:
        write_text(root / "environments" / f"{env['selector']}.tfvars", _tfvars(ir, env))
    return root


def _main_tf(ir):
    out = [_HEADER]
    for defn in ir["definitions"]:
        out.append(_policy_definition(defn))
    for init in ir["initiatives"]:
        out.append(_policy_set(init))
    asg_by_init = {a["initiative"]: a for a in ir["assignments"]}
    for init in ir["initiatives"]:
        out.append(_assignment(init, asg_by_init[init["name"]]))
    role_blocks = _role_assignments(ir)
    if role_blocks:
        out.append(role_blocks)
    return "\n".join(out)


def _policy_definition(defn):
    """A custom member policy as an ``azurerm_policy_definition`` resource (MG-scoped)."""
    ident = tf_ident(defn["name"])
    p = defn["properties"]
    lines = [
        f'resource "azurerm_policy_definition" "{ident}" {{',
        f'  name                = {hcl_str(defn["name"])}',
        '  policy_type         = "Custom"',
        f'  mode                = {hcl_str(p.get("mode", "All"))}',
        f'  display_name        = {hcl_str(p.get("displayName", defn["name"]))}',
        '  management_group_id = var.management_group_id',
        f'  policy_rule         = jsonencode({hcl_value(p["policyRule"], 1)})',
    ]
    if p.get("parameters"):
        lines.append(f'  parameters          = jsonencode({hcl_value(p["parameters"], 1)})')
    if p.get("metadata"):
        lines.append(f'  metadata            = jsonencode({hcl_value(p["metadata"], 1)})')
    lines += ['}', '']
    return "\n".join(lines)


def _policy_set(init):
    ident = tf_ident(init["name"])
    props = init["policyset"]["properties"]
    lines = [
        f'resource "azurerm_policy_set_definition" "{ident}" {{',
        f'  name                = {hcl_str(init["name"])}',
        '  policy_type         = "Custom"',
        f'  display_name        = {hcl_str(props["displayName"])}',
        '  management_group_id = var.management_group_id',
        '',
    ]
    for m in props["policyDefinitions"]:
        if "policyDefinitionId" in m:
            pid = hcl_str(m["policyDefinitionId"])                      # built-in: literal id
        else:
            pid = f'azurerm_policy_definition.{tf_ident(m["policyDefinitionName"])}.id'  # custom: resource id
        lines.append('  policy_definition_reference {')
        lines.append(f'    policy_definition_id = {pid}')
        lines.append(f'    reference_id         = {hcl_str(m["policyDefinitionReferenceId"])}')
        if m.get("parameters"):
            lines.append(f'    parameter_values     = jsonencode({hcl_value(m["parameters"], 2)})')
        if m.get("groupNames"):
            lines.append(f'    policy_group_names   = {hcl_value(m["groupNames"], 2)}')
        lines.append('  }')
    lines.append('}')
    lines.append('')
    return "\n".join(lines)


def _assignment(init, asg):
    ident = tf_ident(init["name"])
    lines = [
        f'resource "azurerm_management_group_policy_assignment" "{ident}" {{',
        f'  name                 = {hcl_str(asg["assignmentName"])}',
        '  management_group_id  = var.management_group_id',
        f'  policy_definition_id = azurerm_policy_set_definition.{ident}.id',
        f'  display_name         = {hcl_str(asg["displayName"])}',
    ]
    if asg["boundParameters"]:
        params = {k: {"value": v} for k, v in asg["boundParameters"].items()}
        lines.append(f'  parameters           = jsonencode({hcl_value(params, 1)})')
    not_scopes = sorted({s for lst in asg["notScopes"].values() for s in lst})
    if not_scopes:
        lines.append(f'  not_scopes           = {hcl_value(not_scopes, 1)}')
    if asg["managedIdentity"]["required"]:
        lines.append('  location             = var.managed_identity_location')
        lines.append('  identity {')
        lines.append('    type = "SystemAssigned"')
        lines.append('  }')
    lines.append('}')
    lines.append('')
    return "\n".join(lines)


def _role_assignments(ir):
    blocks = []
    for init in ir["initiatives"]:
        if not init["hasRemediation"]:
            continue
        ident = tf_ident(init["name"])
        for i, rid in enumerate(init["roleDefinitionIds"]):
            blocks.append("\n".join([
                f'resource "azurerm_role_assignment" "{ident}_{i}" {{',
                '  scope              = var.management_group_id',
                f'  role_definition_id = {hcl_str(rid)}',
                f'  principal_id       = azurerm_management_group_policy_assignment.{ident}.identity[0].principal_id',
                '}',
                '',
            ]))
    return "\n".join(blocks)


def _variables_tf():
    return "\n".join([
        'variable "management_group_id" {',
        '  type        = string',
        '  description = "Deployment root management group resource id."',
        '}',
        '',
        'variable "managed_identity_location" {',
        '  type        = string',
        '  default     = null',
        '  description = "Location for system-assigned identities (remediation)."',
        '}',
        '',
        'variable "tenant_id" {',
        '  type        = string',
        '  description = "Azure AD tenant id."',
        '}',
        '',
    ])


def _tfvars(ir, env):
    lines = [
        f'# tfvars for pacSelector "{env["selector"]}" (enforcement: {env["enforcement"]})',
        f'management_group_id       = {hcl_str(env["rootScope"])}',
        f'tenant_id                 = {hcl_str(env["tenantId"])}',
    ]
    if env.get("managedIdentityLocation"):
        lines.append(f'managed_identity_location = {hcl_str(env["managedIdentityLocation"])}')
    lines.append('')
    return "\n".join(lines)


_HEADER = "\n".join([
    "# Generated by the epac-builder (consumer). Do not hand-edit.",
    "terraform {",
    "  required_providers {",
    "    azurerm = {",
    '      source  = "hashicorp/azurerm"',
    '      version = "~> 3.0"',
    "    }",
    "  }",
    "}",
    "",
    'provider "azurerm" {',
    "  features {}",
    "  tenant_id = var.tenant_id",
    "}",
    "",
])
