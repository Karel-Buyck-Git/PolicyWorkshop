// Azure AI Foundry hub + project (Microsoft.MachineLearningServices/workspaces).
//
// NOTE: Foundry has a newer "Microsoft.CognitiveServices/accounts (kind=AIServices)
// + projects" pattern that is becoming the recommended path. This template uses
// the more widely documented hub/project pattern, which remains fully supported
// and works with Prompt Flow today. If you'd prefer the newer pattern, the
// project node and Claude MaaS deployment paths change but the rest of the
// architecture stays identical.

param location string
param tags object
param hubName string
param projectName string
param keyVaultName string
param storageAccountId string
param appInsightsId string
param uamiId string
param uamiPrincipalId string
param ownerObjectId string

// -----------------------------------------------------------------------------
// Key Vault (required by hub)
// -----------------------------------------------------------------------------
resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: { name: 'standard', family: 'A' }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enabledForDeployment: false
    enabledForTemplateDeployment: false
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    publicNetworkAccess: 'Enabled'
  }
}

// -----------------------------------------------------------------------------
// Foundry hub
// -----------------------------------------------------------------------------
resource hub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: hubName
  location: location
  tags: tags
  kind: 'Hub'
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${uamiId}': {}
    }
  }
  properties: {
    friendlyName: 'Policy Taxonomy Hub'
    description: 'Hub for the Azure Policy taxonomy production flow.'
    storageAccount: storageAccountId
    keyVault: kv.id
    applicationInsights: appInsightsId
    publicNetworkAccess: 'Enabled'
    hbiWorkspace: false
  }
}

// -----------------------------------------------------------------------------
// Foundry project (child workspace, kind=Project, references the hub)
// -----------------------------------------------------------------------------
resource project 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: projectName
  location: location
  tags: tags
  kind: 'Project'
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${uamiId}': {}
    }
  }
  properties: {
    friendlyName: 'Policy Taxonomy Project'
    description: 'Production flow for Azure Policy tier classification.'
    hubResourceId: hub.id
    publicNetworkAccess: 'Enabled'
  }
}

// -----------------------------------------------------------------------------
// RBAC: hub owner + UAMI gets AzureML Data Scientist on the project
// -----------------------------------------------------------------------------
var roles = {
  azureMLDataScientist: 'f6c7c914-8db3-469d-8ca1-694a8f32e121'
  contributor:          'b24988ac-6180-42a0-ab88-20f7382dd24c'
}

resource ownerHub 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: hub
  name: guid(hub.id, ownerObjectId, 'contributor')
  properties: {
    principalId: ownerObjectId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.contributor)
    principalType: 'User'
  }
}

resource uamiOnProject 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: project
  name: guid(project.id, uamiPrincipalId, 'mlds')
  properties: {
    principalId: uamiPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.azureMLDataScientist)
    principalType: 'ServicePrincipal'
  }
}

output hubName         string = hub.name
output projectName     string = project.name
output projectEndpoint string = 'https://${location}.api.azureml.ms/discovery/workspaces/${project.name}'
