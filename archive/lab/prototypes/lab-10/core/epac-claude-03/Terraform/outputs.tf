output "custom_policy_definition_ids" {
  description = "IDs of the custom policy definitions."
  value = {
    deny_public_ip         = azurerm_policy_definition.deny_public_ip.id
    require_tag_owner      = azurerm_policy_definition.require_tag_owner.id
    restrict_nsg_rules     = azurerm_policy_definition.restrict_nsg_rules.id
    deploy_nsg_diagnostics = azurerm_policy_definition.deploy_nsg_diagnostics.id
  }
}

output "initiative_ids" {
  description = "IDs of the custom initiatives."
  value = {
    security_baseline = azurerm_policy_set_definition.security_baseline.id
    tagging           = azurerm_policy_set_definition.tagging.id
  }
}

output "assignment_principal_ids" {
  description = "Managed identity principal ids for remediation assignments."
  value = {
    mcsb              = azurerm_management_group_policy_assignment.mcsb.identity[0].principal_id
    security_baseline = azurerm_management_group_policy_assignment.security_baseline.identity[0].principal_id
    tagging           = azurerm_management_group_policy_assignment.tagging.identity[0].principal_id
  }
}
