# BuiltInPolicyTest Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Append a tag and its value to resources - This built-in is created for versioning test. | 125b7269-7ec9-47bf-8beb-8865b61c2c95 | Preview | Appends the specified tag and value when any resource which is missing this tag is created or updated. Does not modify the tags of resources created before this policy was applied until those resources are changed. Does not apply to resource groups. New 'modify' effect policies are available that support remediation of tags on existing resources (see https://aka.ms/modifydoc). | Append, Disabled | Append | Append | BuiltInPolicyTest | 1.0.0-preview | BuiltIn | Essential |
| 2 | Requires resources to not have a specific tag. This is a versioning test built-in. | 36fd7371-8eb7-4321-9c30-a7100022d048 |  | Denies the creation of a resource that contains the given tag. Does not apply to resource groups. | Audit, Deny, Disabled | Audit | Deny | BuiltInPolicyTest | 2.0.1 | BuiltIn | Essential |
