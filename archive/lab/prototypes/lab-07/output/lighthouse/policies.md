# Lighthouse Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Allow managing tenant ids to onboard through Azure Lighthouse | 7a8a51a3-ad87-4def-96f3-65a1839242b6 |  | Restricting Azure Lighthouse delegations to specific managing tenants increases security by limiting those who can manage your Azure resources. | deny | deny | deny | Lighthouse | 1.0.1 | BuiltIn | Essential |
| 2 | Audit delegation of scopes to a managing tenant | 76bed37b-484f-430f-a009-fd7592dff818 |  | Audit delegation of scopes to a managing tenant via Azure Lighthouse. | Audit, Disabled | Audit | Audit | Lighthouse | 1.0.0 | BuiltIn | Professional |
