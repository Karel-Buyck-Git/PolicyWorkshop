targetScope = 'managementGroup'

metadata majorVersion = '1'
metadata minorVersion = '0'

resource policy 'Microsoft.Authorization/policyDefinitions@2025-03-01' = {
  name: 'Require naming for resource groups'
  properties: {
    displayName: 'Require naming for resource groups'
    policyType: 'Custom'
    mode: 'All'
    metadata: {
      category: 'Naming convention'
      version: '1.0.0'
    }
    parameters: {
      resourceAbbreviation: {
        type: 'String'
        defaultValue: 'rg'
        metadata: {
          displayName: 'Resource group type abbreviation'
          description: 'A short name for the resource group type abbreviation'
        }
      }
      excludedResourceGroupPattern: {
        type: 'Array'
        defaultValue: [
          'AzureBackupRG_*'
          'NetworkWatcherRG'
          'synapseworkspace-managedrg-*'
          'mrg-cisco-meraki-*'
        ]
        metadata: {
          displayName: 'Array of excluded resource groups'
          description: 'This array contains all excluded RGs from this policy. Wild card patterns is supported. Example: \'rg-*, rg-abc-*\''
        }
      }
      effect: {
        type: 'String'
        allowedValues: [
          'Audit'
          'Deny'
          'Disabled'
        ]
        defaultValue: 'Audit'
        metadata: {
          displayName: 'Effect'
          description: 'The effect of the policy (Deny, Audit or Disabled)'
        }
      }
    }
    policyRule: {
      if: {
        allOf: [
          {
            field: 'type'
            equals: 'Microsoft.Resources/subscriptions/resourceGroups'
          }
          {
            count: {
              value: '[parameters(\'excludedResourceGroupPattern\')]'
              name: 'pattern'
              where: {
                field: 'name'
                like: '[current(\'pattern\')]'
              }
            }
            equals: 0
          }
          {
            count: {
              value: [
                '[concat(\'...-\',parameters(\'resourceAbbreviation\'),\'-..-...-..-###\')]'
                '[concat(\'...-\',parameters(\'resourceAbbreviation\'),\'-..-...-...-###\')]'
                '[concat(\'...-\',parameters(\'resourceAbbreviation\'),\'-...-...-..-###\')]'
                '[concat(\'...-\',parameters(\'resourceAbbreviation\'),\'-...-...-...-###\')]'
                '[concat(\'...-\',parameters(\'resourceAbbreviation\'),\'-....-...-..-###\')]'
                '[concat(\'...-\',parameters(\'resourceAbbreviation\'),\'-....-...-...-###\')]'
                '[concat(\'....-\',parameters(\'resourceAbbreviation\'),\'-..-...-..-###\')]'
                '[concat(\'....-\',parameters(\'resourceAbbreviation\'),\'-..-...-...-###\')]'
                '[concat(\'....-\',parameters(\'resourceAbbreviation\'),\'-...-...-..-###\')]'
                '[concat(\'....-\',parameters(\'resourceAbbreviation\'),\'-...-...-...-###\')]'
                '[concat(\'....-\',parameters(\'resourceAbbreviation\'),\'-....-...-..-###\')]'
                '[concat(\'....-\',parameters(\'resourceAbbreviation\'),\'-....-...-...-###\')]'
              ]
              name: 'pattern'
              where: {
                field: 'name'
                match: '[current(\'pattern\')]'
              }
            }
            equals: 0
          }
        ]
      }
      then: {
        effect: '[parameters(\'effect\')]'
      }
    }
  }
}

output id string = policy.id
output name string = policy.name
output policy object = policy
