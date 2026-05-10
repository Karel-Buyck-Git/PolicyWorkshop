// Grant the UAMI Storage Blob Data Contributor on the data storage account
// so flow runs can read catalog/* and write outputs/*.

param storageDataAccountName string
param uamiPrincipalId string

resource storageData 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageDataAccountName
}

var blobDataContributor = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'

resource uamiBlobAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageData
  name: guid(storageData.id, uamiPrincipalId, blobDataContributor)
  properties: {
    principalId: uamiPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', blobDataContributor)
    principalType: 'ServicePrincipal'
  }
}
