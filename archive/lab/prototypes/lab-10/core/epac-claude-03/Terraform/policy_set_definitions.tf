# Custom initiatives (policy set definitions).

resource "azurerm_policy_set_definition" "security_baseline" {
  name                = "security-baseline-initiative"
  policy_type         = "Custom"
  display_name        = "Custom Security Baseline Initiative"
  description         = "Org controls layered on MCSB: no public IPs, restricted NSG rules, NSG diagnostics."
  management_group_id = local.mg_scope_id
  metadata            = jsonencode({ version = "1.0.0", category = "Security" })

  parameters = jsonencode({
    denyPublicIpEffect = { type = "String", allowedValues = ["Audit", "Deny", "Disabled"], defaultValue = "Deny" }
    restrictNsgEffect  = { type = "String", allowedValues = ["Audit", "Deny", "Disabled"], defaultValue = "Deny" }
    deniedNsgPorts     = { type = "Array", defaultValue = ["22", "3389"] }
    diagnosticsEffect  = { type = "String", allowedValues = ["DeployIfNotExists", "AuditIfNotExists", "Disabled"], defaultValue = "DeployIfNotExists" }
    logAnalytics       = { type = "String", metadata = { displayName = "Log Analytics workspace resource id", strongType = "oms", assignPermissions = true } }
  })

  policy_definition_reference {
    policy_definition_id = azurerm_policy_definition.deny_public_ip.id
    reference_id         = "DenyPublicIp"
    parameter_values     = jsonencode({ effect = { value = "[parameters('denyPublicIpEffect')]" } })
  }

  policy_definition_reference {
    policy_definition_id = azurerm_policy_definition.restrict_nsg_rules.id
    reference_id         = "RestrictNsgRules"
    parameter_values = jsonencode({
      effect      = { value = "[parameters('restrictNsgEffect')]" }
      deniedPorts = { value = "[parameters('deniedNsgPorts')]" }
    })
  }

  policy_definition_reference {
    policy_definition_id = azurerm_policy_definition.deploy_nsg_diagnostics.id
    reference_id         = "DeployNsgDiagnostics"
    parameter_values = jsonencode({
      effect       = { value = "[parameters('diagnosticsEffect')]" }
      logAnalytics = { value = "[parameters('logAnalytics')]" }
    })
  }
}

resource "azurerm_policy_set_definition" "tagging" {
  name                = "tagging-initiative"
  policy_type         = "Custom"
  display_name        = "Tagging Governance Initiative"
  description         = "Requires an Owner tag (custom) and inherits CostCenter from the RG (built-in Modify)."
  management_group_id = local.mg_scope_id
  metadata            = jsonencode({ version = "1.0.0", category = "Governance" })

  parameters = jsonencode({
    ownerTagEffect    = { type = "String", allowedValues = ["Audit", "Deny", "Disabled"], defaultValue = "Audit" }
    costCenterTagName = { type = "String", defaultValue = "CostCenter" }
  })

  policy_definition_reference {
    policy_definition_id = azurerm_policy_definition.require_tag_owner.id
    reference_id         = "RequireOwnerTag"
    parameter_values = jsonencode({
      tagName = { value = "Owner" }
      effect  = { value = "[parameters('ownerTagEffect')]" }
    })
  }

  policy_definition_reference {
    policy_definition_id = local.builtin.inherit_tag_def
    reference_id         = "InheritCostCenterFromRg"
    parameter_values     = jsonencode({ tagName = { value = "[parameters('costCenterTagName')]" } })
  }
}
