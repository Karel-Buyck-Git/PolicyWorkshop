# Fluid Relay Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Fluid Relay should use customer-managed keys to encrypt data at rest | 46388f67-373c-4018-98d3-2b83172dd13a |  | Use customer-managed keys to manage the encryption at rest of your Fluid Relay server. By default, customer data is encrypted with service-managed keys, but CMKs are commonly required to meet regulatory compliance standards. Customer-managed keys enable the data to be encrypted with an Azure Key Vault key created and owned by you, with full control and responsibility, including rotation and management. Learn more at https://docs.microsoft.com/azure/azure-fluid-relay/concepts/customer-managed-keys. | Audit, Disabled | Audit | Audit | Fluid Relay | 1.0.0 | BuiltIn | Enterprise |
