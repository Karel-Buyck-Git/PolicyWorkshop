#!/usr/bin/env bash
# Deploy the policy-taxonomy infrastructure into the current resource group.
#
# Usage:
#   az login
#   az account set --subscription "<sub>"
#   az group create --name <rg> --location westeurope
#   ./deploy.sh <rg>
set -euo pipefail

RG="${1:?Usage: deploy.sh <resource-group>}"
PARAM_FILE="${2:-main.bicepparam}"

cd "$(dirname "$0")"

echo "Validating Bicep..."
az bicep build --file main.bicep > /dev/null

echo "Deploying to resource group: $RG"
az deployment group create \
  --resource-group "$RG" \
  --template-file main.bicep \
  --parameters "$PARAM_FILE" \
  --query "properties.outputs"
