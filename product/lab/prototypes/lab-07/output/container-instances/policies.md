# Container Instances Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure diagnostics for container group to log analytics workspace | 21c469fa-a887-4363-88a9-60bfd6911a15 |  | Appends the specified log analytics workspaceId and workspaceKey when any container group which is missing these fields is created or updated. Does not modify the fields of container groups created before this policy was applied until those resource groups are changed. | Append, Disabled | Append | Append | Container Instances | 1.0.0 | BuiltIn | Enterprise |
