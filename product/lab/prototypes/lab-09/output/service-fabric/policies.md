# Service Fabric Policies

## Tier rationale

**Essential** — Baseline hygiene for Service Fabric: the non-negotiable controls every deployment should enforce from day one. This tier delivers encryption-at-rest with service-managed keys and key and certificate lifecycle hygiene (rotation, expiration, validity). Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for Service Fabric in the current built-in policy set.

**Enterprise** — No enterprise-tier policies are defined for Service Fabric in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Service Fabric clusters should have the ClusterProtectionLevel property set to EncryptAndSign | 617c02be-7f02-4efd-8836-3180d47b6c68 |  | Service Fabric provides three levels of protection (None, Sign and EncryptAndSign) for node-to-node communication using a primary cluster certificate. Set the protection level to ensure that all node-to-node messages are encrypted and digitally signed | Audit, Deny, Disabled | Audit | Deny | Service Fabric | Compute | 1.1.0 | BuiltIn | Essential |
| 2 | Service Fabric clusters should only use Azure Active Directory for client authentication | b54ed75b-3e1a-44ac-a333-05ba39b99ff0 |  | Audit usage of client authentication only via Azure Active Directory in Service Fabric | Audit, Deny, Disabled | Audit | Deny | Service Fabric | Compute | 1.1.0 | BuiltIn | Essential |
