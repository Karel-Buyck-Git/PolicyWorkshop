targetScope = 'managementGroup'

@description('Resource ids of the custom policy definitions to bundle.')
param denyPublicIpId string
param requireTagOwnerId string
param restrictNsgRulesId string
param deployNsgDiagnosticsId string

var inheritTagDefId = '/providers/Microsoft.Authorization/policyDefinitions/ea3f2387-9b95-492a-a190-fcdc54f7b070'

resource securityBaseline 'Microsoft.Authorization/policySetDefinitions@2023-04-01' = {
  name: 'security-baseline-initiative'
  properties: {
    displayName: 'Custom Security Baseline Initiative'
    policyType: 'Custom'
    description: 'Org controls layered on MCSB: no public IPs, restricted NSG rules, NSG diagnostics.'
    metadata: {
      version: '1.0.0'
      category: 'Security'
    }
    parameters: {
      denyPublicIpEffect: { type: 'String', allowedValues: [ 'Audit', 'Deny', 'Disabled' ], defaultValue: 'Deny' }
      restrictNsgEffect: { type: 'String', allowedValues: [ 'Audit', 'Deny', 'Disabled' ], defaultValue: 'Deny' }
      deniedNsgPorts: { type: 'Array', defaultValue: [ '22', '3389' ] }
      diagnosticsEffect: { type: 'String', allowedValues: [ 'DeployIfNotExists', 'AuditIfNotExists', 'Disabled' ], defaultValue: 'DeployIfNotExists' }
      logAnalytics: { type: 'String', metadata: { displayName: 'Log Analytics workspace resource id', strongType: 'oms', assignPermissions: true } }
    }
    policyDefinitions: [
      {
        policyDefinitionReferenceId: 'DenyPublicIp'
        policyDefinitionId: denyPublicIpId
        parameters: {
          effect: { value: '[parameters(\'denyPublicIpEffect\')]' }
        }
      }
      {
        policyDefinitionReferenceId: 'RestrictNsgRules'
        policyDefinitionId: restrictNsgRulesId
        parameters: {
          effect: { value: '[parameters(\'restrictNsgEffect\')]' }
          deniedPorts: { value: '[parameters(\'deniedNsgPorts\')]' }
        }
      }
      {
        policyDefinitionReferenceId: 'DeployNsgDiagnostics'
        policyDefinitionId: deployNsgDiagnosticsId
        parameters: {
          effect: { value: '[parameters(\'diagnosticsEffect\')]' }
          logAnalytics: { value: '[parameters(\'logAnalytics\')]' }
        }
      }
    ]
  }
}

resource tagging 'Microsoft.Authorization/policySetDefinitions@2023-04-01' = {
  name: 'tagging-initiative'
  properties: {
    displayName: 'Tagging Governance Initiative'
    policyType: 'Custom'
    description: 'Requires an Owner tag (custom) and inherits CostCenter from the RG (built-in Modify).'
    metadata: {
      version: '1.0.0'
      category: 'Governance'
    }
    parameters: {
      ownerTagEffect: { type: 'String', allowedValues: [ 'Audit', 'Deny', 'Disabled' ], defaultValue: 'Audit' }
      costCenterTagName: { type: 'String', defaultValue: 'CostCenter' }
    }
    policyDefinitions: [
      {
        policyDefinitionReferenceId: 'RequireOwnerTag'
        policyDefinitionId: requireTagOwnerId
        parameters: {
          tagName: { value: 'Owner' }
          effect: { value: '[parameters(\'ownerTagEffect\')]' }
        }
      }
      {
        policyDefinitionReferenceId: 'InheritCostCenterFromRg'
        policyDefinitionId: inheritTagDefId
        parameters: {
          tagName: { value: '[parameters(\'costCenterTagName\')]' }
        }
      }
    ]
  }
}

output securityBaselineId string = securityBaseline.id
output taggingId string = tagging.id
