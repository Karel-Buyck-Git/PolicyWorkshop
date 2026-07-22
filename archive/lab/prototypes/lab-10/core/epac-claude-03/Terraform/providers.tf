terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }
  }

  # Remote state (recommended). Configure and uncomment for CI/CD.
  # backend "azurerm" {
  #   resource_group_name  = "rg-tfstate"
  #   storage_account_name = "sttfstateepac"
  #   container_name       = "tfstate"
  #   key                  = "epac-policy.tfstate"
  # }
}

provider "azurerm" {
  features {}

  # Authentication is taken from the environment (ARM_* / az login / OIDC in CI).
  # tenant_id / subscription_id can also be supplied via variables if preferred.
  tenant_id       = var.tenant_id != "" ? var.tenant_id : null
  subscription_id = var.subscription_id != "" ? var.subscription_id : null
}
