// User-assigned managed identity used by Prompt Flow runs to read the data
// storage and call MaaS endpoints.

param location string
param tags object
param uamiName string

resource uami 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: uamiName
  location: location
  tags: tags
}

output uamiId          string = uami.id
output uamiPrincipalId string = uami.properties.principalId
output uamiClientId    string = uami.properties.clientId
