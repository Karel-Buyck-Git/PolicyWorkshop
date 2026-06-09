# epac-dev environment (isolated dev copy of the hierarchy)
environment                 = "epac-dev"
management_group_id         = "epac-dev-contoso"
sandbox_management_group_id = "epac-dev-contoso-sandbox"
location                    = "westeurope"
allowed_locations           = ["westeurope", "northeurope"]
log_analytics_workspace_id  = "/subscriptions/REPLACE-DEV-SUB/resourceGroups/rg-logs/providers/Microsoft.OperationalInsights/workspaces/law-epac-dev"

owner_tag_effect     = "Audit"
cost_center_tag_name = "CostCenter"

enable_nist             = true
enable_pci              = false
pci_policy_set_id       = ""
create_sample_exemption = false
