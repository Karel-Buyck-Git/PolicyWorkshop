targetScope = 'managementGroup'

// Deploy with: az deployment mg create --management-group-id <id> --location <loc> \
//   --template-file main.bicep --parameters @main.parameters.tenant01.json

@description('Logical environment name (epac-dev | tenant01) - naming/metadata only.')
param environment string

@description('Default location for assignment managed identities (DINE/Modify).')
param location string = 'westeurope'

@description('Log Analytics workspace resource id for the NSG diagnostics DINE policy.')
param logAnalyticsWorkspaceId string

@description('Allowed regions.')
param allowedLocations array = [ 'westeurope', 'northeurope' ]

@description('Sandbox management group id (short name), excluded from Allowed Locations.')
param sandboxManagementGroupId string

@description('Assign built-in NIST 800-53 R5 initiative.')
param enableNist bool = true

@description('Assign a PCI-DSS initiative. Requires pciPolicySetId.')
param enablePci bool = false

@description('Built-in PCI-DSS policy set definition id (verify for your cloud).')
param pciPolicySetId string = ''

param ownerTagEffect string = 'Audit'
param costCenterTagName string = 'CostCenter'

@description('Create the sample sandbox waiver exemption.')
param createSampleExemption bool = false

// 1) Custom policy definitions
module definitions 'modules/policyDefinitions.bicep' = {
  name: 'policyDefinitions-${environment}'
}

// 2) Custom initiatives
module sets 'modules/policySetDefinitions.bicep' = {
  name: 'policySetDefinitions-${environment}'
  params: {
    denyPublicIpId: definitions.outputs.denyPublicIpId
    requireTagOwnerId: definitions.outputs.requireTagOwnerId
    restrictNsgRulesId: definitions.outputs.restrictNsgRulesId
    deployNsgDiagnosticsId: definitions.outputs.deployNsgDiagnosticsId
  }
}

// 3) Assignments (+ remediation role assignments)
module assignments 'modules/policyAssignments.bicep' = {
  name: 'policyAssignments-${environment}'
  params: {
    location: location
    logAnalyticsWorkspaceId: logAnalyticsWorkspaceId
    allowedLocations: allowedLocations
    sandboxManagementGroupId: sandboxManagementGroupId
    enableNist: enableNist
    enablePci: enablePci
    pciPolicySetId: pciPolicySetId
    ownerTagEffect: ownerTagEffect
    costCenterTagName: costCenterTagName
    securityBaselineId: sets.outputs.securityBaselineId
    taggingId: sets.outputs.taggingId
  }
}

// 4) Sample exemption, deployed at the sandbox MG scope
module exemption 'modules/policyExemptions.bicep' = if (createSampleExemption) {
  name: 'policyExemptions-${environment}'
  scope: managementGroup(sandboxManagementGroupId)
  params: {
    policyAssignmentId: assignments.outputs.allowedLocationsAssignmentId
  }
}
