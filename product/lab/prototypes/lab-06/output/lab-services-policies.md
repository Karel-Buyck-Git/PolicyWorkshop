# Lab Services Policies

| # | Policy | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lab Services should enable all options for auto shutdown |  | This policy provides helps with cost management by enforcing all automatic shutdown options are enabled for a lab. | Audit, Deny, Disabled | Audit | Deny | Lab Services | 1.1.0 | BuiltIn | Essential |
| 2 | Lab Services should not allow template virtual machines for labs |  | This policy prevents creation and customization of a template virtual machines for labs managed through Lab Services. | Audit, Deny, Disabled | Audit | Deny | Lab Services | 1.1.0 | BuiltIn | Essential |
| 3 | Lab Services should require non-admin user for labs |  | This policy requires non-admin user accounts to be created for the labs managed through lab-services. | Audit, Deny, Disabled | Audit | Deny | Lab Services | 1.1.0 | BuiltIn | Essential |
| 4 | Lab Services should restrict allowed virtual machine SKU sizes |  | This policy enables you to restrict certain Compute VM SKUs for labs managed through Lab Services. This will restrict certain virtual machine sizes. | Audit, Deny, Disabled | Audit | Deny | Lab Services | 1.1.0 | BuiltIn | Essential |
