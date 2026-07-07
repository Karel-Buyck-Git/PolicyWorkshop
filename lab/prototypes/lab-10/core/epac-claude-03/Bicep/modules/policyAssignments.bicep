targetScope = 'managementGroup'

@description('Default location for assignment managed identities (DINE/Modify).')
param location string

@description('Log Analytics workspace resource id for the NSG diagnostics DINE policy.')
param logAnalyticsWorkspaceId string

@description('Allowed regions.')
param allowedLocations array

@description('Sandbox management group id (short name) excluded from Allowed Locations.')
param sandboxManagementGroupId string

param enableNist bool
param enablePci bool
param pciPolicySetId string

param ownerTagEffect string
param costCenterTagName string

@description('Custom initiative ids passed from the policySetDefinitions module.')
param securityBaselineId string
param taggingId string

// Well-known built-in ids
var mcsbSetId = tenantResourceId('Microsoft.Authorization/policySetDefinitions', '1f3afdf9-d0c9-4c3d-847f-89da613e70a8')
var nistSetId = tenantResourceId('Microsoft.Authorization/policySetDefinitions', '179d1daa-458f-4e47-8086-2a68d0d6c38f')
var allowedLocDefId = tenantResourceId('Microsoft.Authorization/policyDefinitions', 'e56962a6-4747-49cd-b67b-bf8b01975c4c')

// Roles for remediation identities
var roleMonitoringContributor = tenantResourceId('Microsoft.Authorization/roleDefinitions', '749f88d5-cbae-40b8-bcfc-e573ddc772fa')
var roleLogAnalyticsContributor = tenantResourceId('Microsoft.Authorization/roleDefinitions', '92aaf0da-9dab-42b6-94a3-d43ce8d16293')
var roleTagContributor = tenantResourceId('Microsoft.Authorization/roleDefinitions', '4a9ae827-6dc8-4573-8ac7-8239d42aa03f')

var sandboxScope = tenantResourceId('Microsoft.Management/managementGroups', sandboxManagementGroupId)

// ---- Compliance: MCSB (always) ----
resource mcsb 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'mcsb'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    displayName: 'Microsoft Cloud Security Benchmark'
    description: 'MCSB compliance baseline.'
    policyDefinitionId: mcsbSetId
  }
}

// ---- Compliance: NIST (optional) ----
resource nist 'Microsoft.Authorization/policyAssignments@2024-04-01' = if (enableNist) {
  name: 'nist-800-53-r5'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    displayName: 'NIST SP 800-53 Rev. 5'
    description: 'NIST 800-53 R5 compliance baseline.'
    policyDefinitionId: nistSetId
  }
}

// ---- Compliance: PCI-DSS (optional, requires pciPolicySetId) ----
resource pci 'Microsoft.Authorization/policyAssignments@2024-04-01' = if (enablePci && !empty(pciPolicySetId)) {
  name: 'pci-dss'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    displayName: 'PCI DSS'
    description: 'PCI-DSS compliance baseline.'
    policyDefinitionId: pciPolicySetId
  }
}

// ---- Custom security baseline initiative ----
resource securityBaseline 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'sec-baseline'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    displayName: 'Security Baseline'
    description: 'Custom org security controls.'
    policyDefinitionId: securityBaselineId
    parameters: {
      denyPublicIpEffect: { value: 'Deny' }
      restrictNsgEffect: { value: 'Deny' }
      deniedNsgPorts: { value: [ '22', '3389' ] }
      diagnosticsEffect: { value: 'DeployIfNotExists' }
      logAnalytics: { value: logAnalyticsWorkspaceId }
    }
  }
}

// ---- Governance: Allowed locations (built-in), sandbox excluded ----
resource allowedLocations_assignment 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'allowed-locations'
  properties: {
    displayName: 'Allowed Locations'
    description: 'Restricts deployment regions.'
    policyDefinitionId: allowedLocDefId
    notScopes: [ sandboxScope ]
    parameters: {
      listOfAllowedLocations: { value: allowedLocations }
    }
  }
}

// ---- Governance: Tagging initiative ----
resource tagging 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'tagging-gov'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    displayName: 'Tagging Governance'
    description: 'Owner tag required; CostCenter inherited from RG.'
    policyDefinitionId: taggingId
    parameters: {
      ownerTagEffect: { value: ownerTagEffect }
      costCenterTagName: { value: costCenterTagName }
    }
  }
}

// ---- Role assignments for remediation identities ----
resource raSecBaselineMonitoring 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(managementGroup().id, 'sec-baseline', 'monitoring-contributor')
  properties: {
    roleDefinitionId: roleMonitoringContributor
    principalId: securityBaseline.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource raSecBaselineLaw 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(managementGroup().id, 'sec-baseline', 'log-analytics-contributor')
  properties: {
    roleDefinitionId: roleLogAnalyticsContributor
    principalId: securityBaseline.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource raTaggingTagContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(managementGroup().id, 'tagging-gov', 'tag-contributor')
  properties: {
    roleDefinitionId: roleTagContributor
    principalId: tagging.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// NOTE: MCSB/NIST contain many DINE/AINE policies. Add role assignments for their identities
// (mcsb.identity.principalId / nist.identity.principalId) when enabling remediation.

output allowedLocationsAssignmentId string = allowedLocations_assignment.id
