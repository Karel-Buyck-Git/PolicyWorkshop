variable "management_group_id" {
  type        = string
  description = "Deployment root management group resource id."
}

variable "managed_identity_location" {
  type        = string
  default     = null
  description = "Location for system-assigned identities (remediation)."
}

variable "tenant_id" {
  type        = string
  description = "Azure AD tenant id."
}
