# Health Deidentification Service Policies

| # | Policy | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Health Data Services de-identification service should disable public network access |  | Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can limit exposure of your resources by creating private endpoints instead. | Audit, Disabled | Audit | Audit | Health Deidentification Service | 1.0.0 | BuiltIn | Enterprise |
| 2 | Azure Health Data Services de-identification service should use private link |  | Azure Health Data Services de-identification service should have at least one approved private endpoint connection. Clients in a virtual network can securely access resources that have private endpoint connections through private links. | Audit, Disabled | Audit | Audit | Health Deidentification Service | 1.0.0 | BuiltIn | Enterprise |
