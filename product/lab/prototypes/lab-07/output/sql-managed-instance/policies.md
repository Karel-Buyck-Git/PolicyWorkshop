# SQL Managed Instance Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Customer managed key encryption must be used as part of CMK Encryption for Arc SQL managed instances. | 413923f0-ff16-41ae-8583-90c5c5d9fa8f |  | As a part of CMK encryption, Customer managed key encryption must be used. Learn more at https://aka.ms/EnableTDEArcSQLMI. | Audit, Disabled | Audit | Audit | SQL Managed Instance | 1.0.0 | BuiltIn | Essential |
| 2 | TLS protocol 1.2 must be used for Arc SQL managed instances. | bb3c7464-033e-41ee-81dc-480fde675b20 |  | As a part of network settings, Microsoft recommends allowing only TLS 1.2 for TLS protocols in SQL Servers. Learn more on network settings for SQL Server at https://aka.ms/TlsSettingsSQLServer. | Audit, Disabled | Audit | Audit | SQL Managed Instance | 1.0.0 | BuiltIn | Essential |
| 3 | Transparent Data Encryption must be enabled for Arc SQL managed instances. | 6599ab01-29bc-4852-a6f5-de9e2151714a |  | Enable transparent data encryption (TDE) at-rest on an Azure Arc-enabled SQL Managed Instance. Learn more at https://aka.ms/EnableTDEArcSQLMI. | Audit, Disabled | Audit | Audit | SQL Managed Instance | 1.0.0 | BuiltIn | Essential |
