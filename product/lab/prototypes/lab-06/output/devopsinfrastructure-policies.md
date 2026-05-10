# DevOpsInfrastructure Policies

| # | Policy | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Microsoft Managed DevOps Pools should be provided with valid subnet resource in order to configure with own virtual network. | Preview | Disallows creating Pool resources if a valid subnet resource is not provided. | Audit, Deny, Disabled | Audit | Deny | DevOpsInfrastructure | 1.0.0-preview | BuiltIn | Professional |
