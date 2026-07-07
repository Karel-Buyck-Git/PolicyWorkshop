targetScope = 'managementGroup'

// Custom policy definitions deployed at the management group.

resource denyPublicIp 'Microsoft.Authorization/policyDefinitions@2023-04-01' = {
  name: 'deny-public-ip'
  properties: {
    displayName: 'Deny creation of Public IP addresses'
    policyType: 'Custom'
    mode: 'All'
    description: 'Prevents creation of Public IP resources to reduce internet-facing exposure.'
    metadata: {
      version: '1.0.0'
      category: 'Security'
    }
    parameters: {
      effect: {
        type: 'String'
        allowedValues: [ 'Audit', 'Deny', 'Disabled' ]
        defaultValue: 'Deny'
        metadata: { displayName: 'Effect' }
      }
    }
    policyRule: {
      if: {
        field: 'type'
        equals: 'Microsoft.Network/publicIPAddresses'
      }
      then: {
        effect: '[parameters(\'effect\')]'
      }
    }
  }
}

resource requireTagOwner 'Microsoft.Authorization/policyDefinitions@2023-04-01' = {
  name: 'require-tag-owner'
  properties: {
    displayName: 'Require \'Owner\' tag on resources'
    policyType: 'Custom'
    mode: 'Indexed'
    description: 'Enforces an Owner tag so every resource has an accountable owner.'
    metadata: {
      version: '1.0.0'
      category: 'Security'
    }
    parameters: {
      tagName: {
        type: 'String'
        defaultValue: 'Owner'
        metadata: { displayName: 'Tag Name' }
      }
      effect: {
        type: 'String'
        allowedValues: [ 'Audit', 'Deny', 'Disabled' ]
        defaultValue: 'Audit'
        metadata: { displayName: 'Effect' }
      }
    }
    policyRule: {
      if: {
        field: '[concat(\'tags[\', parameters(\'tagName\'), \']\')]'
        exists: 'false'
      }
      then: {
        effect: '[parameters(\'effect\')]'
      }
    }
  }
}

resource restrictNsgRules 'Microsoft.Authorization/policyDefinitions@2023-04-01' = {
  name: 'restrict-nsg-rules'
  properties: {
    displayName: 'Restrict permissive inbound NSG rules from the Internet'
    policyType: 'Custom'
    mode: 'All'
    description: 'Audits/denies NSG rules allowing inbound from any source on sensitive ports.'
    metadata: {
      version: '1.0.0'
      category: 'Network'
    }
    parameters: {
      deniedPorts: {
        type: 'Array'
        defaultValue: [ '22', '3389' ]
        metadata: { displayName: 'Denied destination ports' }
      }
      effect: {
        type: 'String'
        allowedValues: [ 'Audit', 'Deny', 'Disabled' ]
        defaultValue: 'Deny'
        metadata: { displayName: 'Effect' }
      }
    }
    policyRule: {
      if: {
        allOf: [
          { field: 'type', equals: 'Microsoft.Network/networkSecurityGroups/securityRules' }
          { field: 'Microsoft.Network/networkSecurityGroups/securityRules/access', equals: 'Allow' }
          { field: 'Microsoft.Network/networkSecurityGroups/securityRules/direction', equals: 'Inbound' }
          { field: 'Microsoft.Network/networkSecurityGroups/securityRules/sourceAddressPrefix', in: [ '*', 'Internet', '0.0.0.0/0' ] }
          { field: 'Microsoft.Network/networkSecurityGroups/securityRules/destinationPortRange', in: '[parameters(\'deniedPorts\')]' }
        ]
      }
      then: {
        effect: '[parameters(\'effect\')]'
      }
    }
  }
}

resource deployNsgDiagnostics 'Microsoft.Authorization/policyDefinitions@2023-04-01' = {
  name: 'deploy-diagnostic-settings-nsg'
  properties: {
    displayName: 'Deploy diagnostic settings for NSGs to Log Analytics'
    policyType: 'Custom'
    mode: 'All'
    description: 'DeployIfNotExists: streams NSG logs to Log Analytics. Validate apiVersion/log categories.'
    metadata: {
      version: '1.0.0'
      category: 'Monitoring'
    }
    parameters: {
      logAnalytics: {
        type: 'String'
        metadata: {
          displayName: 'Log Analytics workspace resource id'
          strongType: 'oms'
          assignPermissions: true
        }
      }
      effect: {
        type: 'String'
        allowedValues: [ 'DeployIfNotExists', 'AuditIfNotExists', 'Disabled' ]
        defaultValue: 'DeployIfNotExists'
        metadata: { displayName: 'Effect' }
      }
    }
    policyRule: {
      if: {
        field: 'type'
        equals: 'Microsoft.Network/networkSecurityGroups'
      }
      then: {
        effect: '[parameters(\'effect\')]'
        details: {
          type: 'Microsoft.Insights/diagnosticSettings'
          name: 'nsg-to-law'
          roleDefinitionIds: [
            '/providers/Microsoft.Authorization/roleDefinitions/749f88d5-cbae-40b8-bcfc-e573ddc772fa'
            '/providers/Microsoft.Authorization/roleDefinitions/92aaf0da-9dab-42b6-94a3-d43ce8d16293'
          ]
          existenceCondition: {
            allOf: [
              { field: 'Microsoft.Insights/diagnosticSettings/workspaceId', equals: '[parameters(\'logAnalytics\')]' }
            ]
          }
          deployment: {
            properties: {
              mode: 'incremental'
              parameters: {
                nsgName: { value: '[field(\'name\')]' }
                location: { value: '[field(\'location\')]' }
                logAnalytics: { value: '[parameters(\'logAnalytics\')]' }
              }
              template: {
                '$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#'
                contentVersion: '1.0.0.0'
                parameters: {
                  nsgName: { type: 'string' }
                  location: { type: 'string' }
                  logAnalytics: { type: 'string' }
                }
                resources: [
                  {
                    type: 'Microsoft.Network/networkSecurityGroups/providers/diagnosticSettings'
                    apiVersion: '2021-05-01-preview'
                    name: '[concat(parameters(\'nsgName\'), \'/Microsoft.Insights/nsg-to-law\')]'
                    location: '[parameters(\'location\')]'
                    properties: {
                      workspaceId: '[parameters(\'logAnalytics\')]'
                      logs: [
                        { category: 'NetworkSecurityGroupEvent', enabled: true }
                        { category: 'NetworkSecurityGroupRuleCounter', enabled: true }
                      ]
                    }
                  }
                ]
              }
            }
          }
        }
      }
    }
  }
}

output denyPublicIpId string = denyPublicIp.id
output requireTagOwnerId string = requireTagOwner.id
output restrictNsgRulesId string = restrictNsgRules.id
output deployNsgDiagnosticsId string = deployNsgDiagnostics.id
