targetScope = 'managementGroup'

// Deployed (via main.bicep) scoped to the sandbox management group.

@description('Policy assignment id to exempt (the Allowed Locations assignment).')
param policyAssignmentId string

resource sandboxWaiver 'Microsoft.Authorization/policyExemptions@2022-07-01-preview' = {
  name: 'sandbox-allowed-locations-waiver'
  properties: {
    displayName: 'Sandbox waiver - Allowed Locations'
    description: 'Temporary waiver for the sandbox MG during a regional PoC.'
    policyAssignmentId: policyAssignmentId
    exemptionCategory: 'Waiver'
    expiresOn: '2026-12-31T00:00:00Z'
  }
}
