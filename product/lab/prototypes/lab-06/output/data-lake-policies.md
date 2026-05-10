# Data Lake Policies

| # | Policy | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Resource logs in Azure Data Lake Store should be enabled |  | Audit enabling of resource logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | Data Lake | 5.0.0 | BuiltIn | Enterprise |
| 2 | Resource logs in Data Lake Analytics should be enabled |  | Audit enabling of resource logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | Data Lake | 5.0.0 | BuiltIn | Enterprise |
| 3 | Require encryption on Data Lake Store accounts |  | This policy ensures encryption is enabled on all Data Lake Store accounts | deny | deny | deny | Data Lake | 1.0.0 | BuiltIn | Essential |
