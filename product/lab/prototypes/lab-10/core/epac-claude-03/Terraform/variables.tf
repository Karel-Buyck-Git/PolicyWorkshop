variable "tenant_id" {
  type        = string
  description = "Entra tenant id (optional; usually supplied via ARM_TENANT_ID)."
  default     = ""
}

variable "subscription_id" {
  type        = string
  description = "A subscription id for the provider context (optional; ARM_SUBSCRIPTION_ID)."
  default     = ""
}

variable "environment" {
  type        = string
  description = "Logical EPAC-style environment name (epac-dev | tenant01). Used for naming/metadata only."
}

variable "management_group_id" {
  type        = string
  description = "Deployment root management group id (short name, e.g. 'contoso' or 'epac-dev-contoso')."
}

variable "sandbox_management_group_id" {
  type        = string
  description = "Sandbox management group id, excluded from Allowed Locations and used by the sample exemption."
}

variable "location" {
  type        = string
  description = "Default location for policy assignment managed identities (DINE/Modify)."
  default     = "westeurope"
}

variable "allowed_locations" {
  type        = list(string)
  description = "Regions resources may be deployed to."
  default     = ["westeurope", "northeurope"]
}

variable "log_analytics_workspace_id" {
  type        = string
  description = "Resource id of the Log Analytics workspace for the NSG diagnostics DINE policy."
}

variable "owner_tag_effect" {
  type    = string
  default = "Audit"
}

variable "cost_center_tag_name" {
  type    = string
  default = "CostCenter"
}

variable "enable_nist" {
  type        = bool
  description = "Assign the built-in NIST SP 800-53 R5 initiative."
  default     = true
}

variable "enable_pci" {
  type        = bool
  description = "Assign a PCI-DSS initiative. Requires pci_policy_set_id."
  default     = false
}

variable "pci_policy_set_id" {
  type        = string
  description = "Built-in PCI-DSS policy set definition id (verify for your cloud)."
  default     = ""
}

variable "create_sample_exemption" {
  type        = bool
  description = "Create the sample sandbox waiver exemption."
  default     = false
}

# Well-known built-in ids (stable)
locals {
  builtin = {
    mcsb_set        = "/providers/Microsoft.Authorization/policySetDefinitions/1f3afdf9-d0c9-4c3d-847f-89da613e70a8"
    nist_set        = "/providers/Microsoft.Authorization/policySetDefinitions/179d1daa-458f-4e47-8086-2a68d0d6c38f"
    allowed_loc_def = "/providers/Microsoft.Authorization/policyDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c"
    inherit_tag_def = "/providers/Microsoft.Authorization/policyDefinitions/ea3f2387-9b95-492a-a190-fcdc54f7b070"
    # Roles used for remediation identities
    role_log_analytics_contributor = "/providers/Microsoft.Authorization/roleDefinitions/92aaf0da-9dab-42b6-94a3-d43ce8d16293"
    role_monitoring_contributor    = "/providers/Microsoft.Authorization/roleDefinitions/749f88d5-cbae-40b8-bcfc-e573ddc772fa"
    role_tag_contributor           = "/providers/Microsoft.Authorization/roleDefinitions/4a9ae827-6dc8-4573-8ac7-8239d42aa03f"
  }
  mg_scope_id   = "/providers/Microsoft.Management/managementGroups/${var.management_group_id}"
  sandbox_scope = "/providers/Microsoft.Management/managementGroups/${var.sandbox_management_group_id}"
}
