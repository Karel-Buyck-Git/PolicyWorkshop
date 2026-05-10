# Data Lake Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Resource logs in Azure Data Lake Store should be enabled | 057ef27e-665e-4328-8ea3-04b3122bd9fb |  | Audit enabling of resource logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | Data Lake | 5.0.0 | BuiltIn | Enterprise |
| 2 | Resource logs in Data Lake Analytics should be enabled | c95c74d9-38fe-4f0d-af86-0c7d626a315c |  | Audit enabling of resource logs. This enables you to recreate activity trails to use for investigation purposes; when a security incident occurs or when your network is compromised | AuditIfNotExists, Disabled | AuditIfNotExists | AuditIfNotExists | Data Lake | 5.0.0 | BuiltIn | Enterprise |
| 3 | Require encryption on Data Lake Store accounts | a7ff3161-0087-490a-9ad9-ad6217f4f43a |  | This policy ensures encryption is enabled on all Data Lake Store accounts | deny | deny | deny | Data Lake | 1.0.0 | BuiltIn | Essential |
