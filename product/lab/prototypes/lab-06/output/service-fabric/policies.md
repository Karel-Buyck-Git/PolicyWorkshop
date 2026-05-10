# Service Fabric Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Service Fabric clusters should only use Azure Active Directory for client authentication | b54ed75b-3e1a-44ac-a333-05ba39b99ff0 |  | Audit usage of client authentication only via Azure Active Directory in Service Fabric | Audit, Deny, Disabled | Audit | Deny | Service Fabric | 1.1.0 | BuiltIn | Enterprise |
| 2 | Service Fabric clusters should have the ClusterProtectionLevel property set to EncryptAndSign | 617c02be-7f02-4efd-8836-3180d47b6c68 |  | Service Fabric provides three levels of protection (None, Sign and EncryptAndSign) for node-to-node communication using a primary cluster certificate. Set the protection level to ensure that all node-to-node messages are encrypted and digitally signed | Audit, Deny, Disabled | Audit | Deny | Service Fabric | 1.1.0 | BuiltIn | Essential |
