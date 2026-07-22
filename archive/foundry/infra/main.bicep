// =============================================================================
// Policy Taxonomy — AI Foundry infrastructure
//
// Deploys: Foundry hub + project, dual storage (workspace + data),
//          Key Vault, Application Insights, Log Analytics, UAMI, RBAC.
//
// Claude (Sonnet/Opus) MaaS deployments are created post-deploy from the
// Foundry model catalog — see ../README.md.
// =============================================================================

targetScope = 'resourceGroup'

@description('Short prefix used for resource names. Lowercase letters/numbers, 3-10 chars.')
@minLength(3)
@maxLength(10)
param namePrefix string = 'polcytax'

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Object ID of the user/service principal that should own the hub for portal access.')
param ownerObjectId string

@description('Tags applied to every resource.')
param tags object = {
  workload: 'policy-taxonomy'
  environment: 'dev'
}

// -----------------------------------------------------------------------------
// Naming
// -----------------------------------------------------------------------------
var suffix = uniqueString(resourceGroup().id, namePrefix)
var names = {
  hub:           '${namePrefix}-hub-${suffix}'
  project:       '${namePrefix}-proj-${suffix}'
  storageHub:    toLower('${namePrefix}hub${take(suffix, 8)}')
  storageData:   toLower('${namePrefix}dat${take(suffix, 8)}')
  keyVault:      '${namePrefix}-kv-${take(suffix, 6)}'
  appInsights:   '${namePrefix}-appi-${suffix}'
  logAnalytics:  '${namePrefix}-log-${suffix}'
  uami:          '${namePrefix}-uami-${suffix}'
}

// -----------------------------------------------------------------------------
// Modules
// -----------------------------------------------------------------------------
module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  params: {
    location:           location
    tags:               tags
    logAnalyticsName:   names.logAnalytics
    appInsightsName:    names.appInsights
  }
}

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    location:               location
    tags:                   tags
    storageHubName:         names.storageHub
    storageDataName:        names.storageData
  }
}

module identity 'modules/identity.bicep' = {
  name: 'identity'
  params: {
    location:   location
    tags:       tags
    uamiName:   names.uami
  }
}

module foundry 'modules/foundry-hub.bicep' = {
  name: 'foundry'
  params: {
    location:               location
    tags:                   tags
    hubName:                names.hub
    projectName:            names.project
    keyVaultName:           names.keyVault
    storageAccountId:       storage.outputs.storageHubId
    appInsightsId:          monitoring.outputs.appInsightsId
    uamiId:                 identity.outputs.uamiId
    uamiPrincipalId:        identity.outputs.uamiPrincipalId
    ownerObjectId:          ownerObjectId
  }
}

module rbac 'modules/rbac.bicep' = {
  name: 'rbac'
  params: {
    storageDataAccountName: storage.outputs.storageDataName
    uamiPrincipalId:        identity.outputs.uamiPrincipalId
  }
  dependsOn: [
    storage
    identity
  ]
}

// -----------------------------------------------------------------------------
// Outputs
// -----------------------------------------------------------------------------
output hubName             string = foundry.outputs.hubName
output projectName         string = foundry.outputs.projectName
output projectEndpoint     string = foundry.outputs.projectEndpoint
output storageDataEndpoint string = storage.outputs.storageDataEndpoint
output uamiClientId        string = identity.outputs.uamiClientId
output appInsightsConnStr  string = monitoring.outputs.appInsightsConnStr
