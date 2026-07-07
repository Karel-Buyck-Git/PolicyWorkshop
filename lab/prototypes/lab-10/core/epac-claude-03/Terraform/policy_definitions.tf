# Custom policy definitions, created at the deployment root management group.

resource "azurerm_policy_definition" "deny_public_ip" {
  name                  = "deny-public-ip"
  policy_type           = "Custom"
  mode                  = "All"
  display_name          = "Deny creation of Public IP addresses"
  description           = "Prevents creation of Public IP resources to reduce internet-facing exposure."
  management_group_id   = local.mg_scope_id
  metadata              = jsonencode({ version = "1.0.0", category = "Security" })
  policy_rule           = file("${path.module}/policies/deny-public-ip.json")
  parameters = jsonencode({
    effect = {
      type          = "String"
      allowedValues = ["Audit", "Deny", "Disabled"]
      defaultValue  = "Deny"
      metadata      = { displayName = "Effect" }
    }
  })
}

resource "azurerm_policy_definition" "require_tag_owner" {
  name                = "require-tag-owner"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "Require 'Owner' tag on resources"
  description         = "Enforces an 'Owner' tag so every resource has an accountable owner."
  management_group_id = local.mg_scope_id
  metadata            = jsonencode({ version = "1.0.0", category = "Security" })
  policy_rule         = file("${path.module}/policies/require-tag-owner.json")
  parameters = jsonencode({
    tagName = { type = "String", defaultValue = "Owner", metadata = { displayName = "Tag Name" } }
    effect  = { type = "String", allowedValues = ["Audit", "Deny", "Disabled"], defaultValue = "Audit", metadata = { displayName = "Effect" } }
  })
}

resource "azurerm_policy_definition" "restrict_nsg_rules" {
  name                = "restrict-nsg-rules"
  policy_type         = "Custom"
  mode                = "All"
  display_name        = "Restrict permissive inbound NSG rules from the Internet"
  description         = "Audits/denies NSG rules allowing inbound from any source on sensitive ports."
  management_group_id = local.mg_scope_id
  metadata            = jsonencode({ version = "1.0.0", category = "Network" })
  policy_rule         = file("${path.module}/policies/restrict-nsg-rules.json")
  parameters = jsonencode({
    deniedPorts = { type = "Array", defaultValue = ["22", "3389"], metadata = { displayName = "Denied destination ports" } }
    effect      = { type = "String", allowedValues = ["Audit", "Deny", "Disabled"], defaultValue = "Deny", metadata = { displayName = "Effect" } }
  })
}

resource "azurerm_policy_definition" "deploy_nsg_diagnostics" {
  name                = "deploy-diagnostic-settings-nsg"
  policy_type         = "Custom"
  mode                = "All"
  display_name        = "Deploy diagnostic settings for NSGs to Log Analytics"
  description         = "DeployIfNotExists: streams NSG logs to Log Analytics. Validate apiVersion/log categories."
  management_group_id = local.mg_scope_id
  metadata            = jsonencode({ version = "1.0.0", category = "Monitoring" })
  policy_rule         = file("${path.module}/policies/deploy-diagnostic-settings.json")
  parameters = jsonencode({
    logAnalytics = { type = "String", metadata = { displayName = "Log Analytics workspace resource id", strongType = "oms", assignPermissions = true } }
    effect       = { type = "String", allowedValues = ["DeployIfNotExists", "AuditIfNotExists", "Disabled"], defaultValue = "DeployIfNotExists", metadata = { displayName = "Effect" } }
  })
}
