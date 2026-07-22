# Lab Services Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lab Services should enable all options for auto shutdown | a6e9cf2d-7d76-440e-b795-8da246bd3aab |  | This policy provides helps with cost management by enforcing all automatic shutdown options are enabled for a lab. | Audit, Deny, Disabled | Audit | Deny | Lab Services | 1.1.0 | BuiltIn | Essential |
| 2 | Lab Services should not allow template virtual machines for labs | e8a5a3eb-1ab6-4657-a701-7ae432cf14e1 |  | This policy prevents creation and customization of a template virtual machines for labs managed through Lab Services. | Audit, Deny, Disabled | Audit | Deny | Lab Services | 1.1.0 | BuiltIn | Essential |
| 3 | Lab Services should require non-admin user for labs | 0fd9915e-cab3-4f24-b200-6e20e1aa276a |  | This policy requires non-admin user accounts to be created for the labs managed through lab-services. | Audit, Deny, Disabled | Audit | Deny | Lab Services | 1.1.0 | BuiltIn | Essential |
| 4 | Lab Services should restrict allowed virtual machine SKU sizes | 3e13d504-9083-4912-b935-39a085db2249 |  | This policy enables you to restrict certain Compute VM SKUs for labs managed through Lab Services. This will restrict certain virtual machine sizes. | Audit, Deny, Disabled | Audit | Deny | Lab Services | 1.1.0 | BuiltIn | Essential |
