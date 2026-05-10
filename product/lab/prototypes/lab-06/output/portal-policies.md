# Portal Policies

| # | Policy | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Shared dashboards should not have markdown tiles with inline content |  | Disallow creating a shared dashboard that has inline content in markdown tiles and enforce that the content should be stored as a markdown file that's hosted online. If you use inline content in the markdown tile, you cannot manage encryption of the content. By configuring your own storage, you can encrypt, double encrypt and even bring your own keys. Enabling this policy restricts users to use 2020-09-01-preview or above version of shared dashboards REST API. | Audit, Deny, Disabled | Audit | Deny | Portal | 1.1.0 | BuiltIn | Essential |
