# DevOpsInfrastructure Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Microsoft Managed DevOps Pools should be provided with valid subnet resource in order to configure with own virtual network. | 0d6d79a8-8406-4e87-814d-2dcd83b2c355 | Preview | Disallows creating Pool resources if a valid subnet resource is not provided. | Audit, Deny, Disabled | Audit | Deny | DevOpsInfrastructure | 1.0.0-preview | BuiltIn | Professional |
