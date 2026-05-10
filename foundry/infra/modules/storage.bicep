// Two storage accounts:
//   1. storageHub  — required default workspace storage for the Foundry hub.
//   2. storageData — separate account holding the policy catalog and outputs.
//                    Hierarchical namespace enabled so we can use ADLS paths.

param location string
param tags object
param storageHubName string
param storageDataName string

// -----------------------------------------------------------------------------
// Hub workspace storage
// -----------------------------------------------------------------------------
resource storageHub 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageHubName
  location: location
  tags: tags
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true   // Foundry hub still requires this today
    supportsHttpsTrafficOnly: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
}

// -----------------------------------------------------------------------------
// Data storage (policy catalog + outputs)
// -----------------------------------------------------------------------------
resource storageData 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageDataName
  location: location
  tags: tags
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    supportsHttpsTrafficOnly: true
    isHnsEnabled: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storageData
  name: 'default'
  properties: {
    deleteRetentionPolicy: { enabled: true, days: 7 }
    containerDeleteRetentionPolicy: { enabled: true, days: 7 }
  }
}

resource catalogContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'catalog'
  properties: { publicAccess: 'None' }
}

resource outputsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'outputs'
  properties: { publicAccess: 'None' }
}

resource flowsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'flows'
  properties: { publicAccess: 'None' }
}

output storageHubId          string = storageHub.id
output storageHubName        string = storageHub.name
output storageDataId         string = storageData.id
output storageDataName       string = storageData.name
output storageDataEndpoint   string = storageData.properties.primaryEndpoints.blob
