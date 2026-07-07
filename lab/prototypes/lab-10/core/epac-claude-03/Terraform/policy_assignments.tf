# Policy assignments at the deployment root management group.
# DINE/Modify assignments use a system-assigned identity + location, plus role assignments below.

# ---- Compliance: MCSB (always) ----
resource "azurerm_management_group_policy_assignment" "mcsb" {
  name                 = "mcsb"
  display_name         = "Microsoft Cloud Security Benchmark"
  description          = "MCSB compliance baseline."
  management_group_id  = local.mg_scope_id
  policy_definition_id = local.builtin.mcsb_set
  location             = var.location

  identity {
    type = "SystemAssigned"
  }
}

# ---- Compliance: NIST 800-53 R5 (optional) ----
resource "azurerm_management_group_policy_assignment" "nist" {
  count                = var.enable_nist ? 1 : 0
  name                 = "nist-800-53-r5"
  display_name         = "NIST SP 800-53 Rev. 5"
  description          = "NIST 800-53 R5 compliance baseline."
  management_group_id  = local.mg_scope_id
  policy_definition_id = local.builtin.nist_set
  location             = var.location

  identity {
    type = "SystemAssigned"
  }
}

# ---- Compliance: PCI-DSS (optional, requires pci_policy_set_id) ----
resource "azurerm_management_group_policy_assignment" "pci" {
  count                = var.enable_pci && var.pci_policy_set_id != "" ? 1 : 0
  name                 = "pci-dss"
  display_name         = "PCI DSS"
  description          = "PCI-DSS compliance baseline."
  management_group_id  = local.mg_scope_id
  policy_definition_id = var.pci_policy_set_id
  location             = var.location

  identity {
    type = "SystemAssigned"
  }
}

# ---- Custom security baseline initiative ----
resource "azurerm_management_group_policy_assignment" "security_baseline" {
  name                 = "sec-baseline"
  display_name         = "Security Baseline"
  description          = "Custom org security controls."
  management_group_id  = local.mg_scope_id
  policy_definition_id = azurerm_policy_set_definition.security_baseline.id
  location             = var.location

  parameters = jsonencode({
    denyPublicIpEffect = { value = "Deny" }
    restrictNsgEffect  = { value = "Deny" }
    deniedNsgPorts     = { value = ["22", "3389"] }
    diagnosticsEffect  = { value = "DeployIfNotExists" }
    logAnalytics       = { value = var.log_analytics_workspace_id }
  })

  identity {
    type = "SystemAssigned"
  }
}

# ---- Governance: Allowed locations (built-in), sandbox excluded ----
resource "azurerm_management_group_policy_assignment" "allowed_locations" {
  name                 = "allowed-locations"
  display_name         = "Allowed Locations"
  description          = "Restricts deployment regions."
  management_group_id  = local.mg_scope_id
  policy_definition_id = local.builtin.allowed_loc_def
  not_scopes           = [local.sandbox_scope]

  parameters = jsonencode({
    listOfAllowedLocations = { value = var.allowed_locations }
  })
}

# ---- Governance: Tagging initiative ----
resource "azurerm_management_group_policy_assignment" "tagging" {
  name                 = "tagging-gov"
  display_name         = "Tagging Governance"
  description          = "Owner tag required; CostCenter inherited from RG."
  management_group_id  = local.mg_scope_id
  policy_definition_id = azurerm_policy_set_definition.tagging.id
  location             = var.location

  parameters = jsonencode({
    ownerTagEffect    = { value = var.owner_tag_effect }
    costCenterTagName = { value = var.cost_center_tag_name }
  })

  identity {
    type = "SystemAssigned"
  }
}

# ---- Role assignments for remediation identities ----
# Terraform does not auto-calculate these (EPAC does). Assign the roles the policies need.

# Custom security baseline DINE -> Monitoring + Log Analytics Contributor
resource "azurerm_role_assignment" "sec_baseline_monitoring" {
  scope              = local.mg_scope_id
  role_definition_id = local.builtin.role_monitoring_contributor
  principal_id       = azurerm_management_group_policy_assignment.security_baseline.identity[0].principal_id
}

resource "azurerm_role_assignment" "sec_baseline_law" {
  scope              = local.mg_scope_id
  role_definition_id = local.builtin.role_log_analytics_contributor
  principal_id       = azurerm_management_group_policy_assignment.security_baseline.identity[0].principal_id
}

# Tagging Modify -> Tag Contributor
resource "azurerm_role_assignment" "tagging_tag_contributor" {
  scope              = local.mg_scope_id
  role_definition_id = local.builtin.role_tag_contributor
  principal_id       = azurerm_management_group_policy_assignment.tagging.identity[0].principal_id
}

# NOTE: MCSB and NIST contain many DINE/AINE policies. For full remediation you must assign the
# roles each surfaced policy requires to mcsb / nist[0].identity[0].principal_id. Start with Audit,
# then add role assignments as you enable remediation. EPAC computes these automatically.
