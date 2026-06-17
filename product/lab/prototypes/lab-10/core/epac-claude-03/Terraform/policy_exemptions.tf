# Sample exemption: waive Allowed Locations on the sandbox MG (gated by create_sample_exemption).
resource "azurerm_management_group_policy_exemption" "sandbox_waiver" {
  count                = var.create_sample_exemption ? 1 : 0
  name                 = "sandbox-allowed-locations-waiver"
  display_name         = "Sandbox waiver - Allowed Locations"
  description          = "Temporary waiver for the sandbox MG during a regional PoC."
  management_group_id  = local.sandbox_scope
  policy_assignment_id = azurerm_management_group_policy_assignment.allowed_locations.id
  exemption_category   = "Waiver"
  expires_on           = "2026-12-31T00:00:00Z"
}
