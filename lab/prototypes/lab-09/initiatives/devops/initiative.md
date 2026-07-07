# DevOps Initiative

## Azure Load Testing

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure load testing resource should use customer-managed keys to encrypt data at rest | 65c4f833-1f2e-426c-8780-f6d7593bed7a |  | Use customer-managed keys(CMK) to manage the encryption at rest for your Azure Load Testing resource. By default the encryptio is done using Service managed keys, customer-managed keys enable the data to be encrypted with an Azure Key Vault key created and owned by you. You have full control and responsibility for the key lifecycle, including rotation and management. Learn more at https://docs.microsoft.com/azure/load-testing/how-to-configure-customer-managed-keys?tabs=portal. | Audit, Deny, Disabled | Audit | Deny | Azure Load Testing | DevOps | 1.0.0 | BuiltIn | Enterprise |
| 2 | Load tests using Azure Load Testing should be run only against private endpoints from within a virtual network. | d855fd7a-9be5-4d84-8b75-28d41aadc158 | Preview | Azure Load Testing engine instances should use virtual network injection for the following purposes: 1. Isolate Azure Load Testing engines to a virtual network. 2. Enable Azure Load Testing engines to interact with systems in either on premises data centers or Azure service in other virtual networks. 3. Empower customers to control inbound and outbound network communications for Azure Load Testing engines. | Audit, Deny, Disabled | Audit | Deny | Azure Load Testing | DevOps | 1.0.0-preview | BuiltIn | Professional |

## Custom Provider

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Deploy associations for a custom provider | c15c281f-ea5c-44cd-90b8-fc3c14d13f0c |  | Deploys an association resource that associates selected resource types to the specified custom provider. This policy deployment does not support nested resource types. | deployIfNotExists | deployIfNotExists | deployIfNotExists | Custom Provider | DevOps | 1.0.0 | BuiltIn | Essential |

## DevCenter

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Microsoft Dev Box Pools should not use Microsoft Hosted Networks. | ece3c79b-2caf-470d-a5f5-66470c4fc649 | Preview | Disallows the use of Microsoft Hosted Networks when creating Pool resources. | Audit, Deny, Disabled | Audit | Deny | DevCenter | DevOps | 1.0.0-preview | BuiltIn | Essential |

## DevOpsInfrastructure

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Microsoft Managed DevOps Pools should be provided with valid subnet resource in order to configure with own virtual network. | 0d6d79a8-8406-4e87-814d-2dcd83b2c355 | Preview | Disallows creating Pool resources if a valid subnet resource is not provided. | Audit, Deny, Disabled | Audit | Deny | DevOpsInfrastructure | DevOps | 1.0.0-preview | BuiltIn | Professional |
