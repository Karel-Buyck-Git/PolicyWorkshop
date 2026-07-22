# tenant01 environment (production-managed intermediate root)
environment                 = "tenant01"
management_group_id         = "contoso"
sandbox_management_group_id = "contoso-sandbox"
location                    = "westeurope"
allowed_locations           = ["westeurope", "northeurope"]
log_analytics_workspace_id  = "/subscriptions/REPLACE-PROD-SUB/resourceGroups/rg-logs/providers/Microsoft.OperationalInsights/workspaces/law-contoso"

owner_tag_effect     = "Audit"
cost_center_tag_name = "CostCenter"

enable_nist             = true
enable_pci              = false
pci_policy_set_id       = "" # e.g. /providers/Microsoft.Authorization/policySetDefinitions/<pci-dss-id>
create_sample_exemption = true
