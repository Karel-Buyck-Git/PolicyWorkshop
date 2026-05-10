# Container Instances Policies

| # | Policy | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure diagnostics for container group to log analytics workspace |  | Appends the specified log analytics workspaceId and workspaceKey when any container group which is missing these fields is created or updated. Does not modify the fields of container groups created before this policy was applied until those resource groups are changed. | Append, Disabled | Append | Append | Container Instances | 1.0.0 | BuiltIn | Enterprise |
