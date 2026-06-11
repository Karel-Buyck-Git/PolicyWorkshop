# Company Data Essential — HDInsight

## Tier rationale

**Essential** — Baseline hygiene for HDInsight: the non-negotiable controls every deployment should enforce from day one. This tier delivers encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure HDInsight clusters should use encryption at host to encrypt data at rest | 1fd32ebd-e4c3-4e13-a54a-d7422d4d95f6 |  | Enabling encryption at host helps protect and safeguard your data to meet your organizational security and compliance commitments. When you enable encryption at host, data stored on the VM host is encrypted at rest and flows encrypted to the Storage service. | Audit, Deny, Disabled | Audit | Audit | Deny | HDInsight | Data | 1.0.0 | BuiltIn | Essential | No | No |
| 2 | Azure HDInsight clusters should use encryption in transit to encrypt communication between Azure HDInsight cluster nodes | d9da03a1-f3c3-412a-9709-947156872263 |  | Data can be tampered with during transmission between Azure HDInsight cluster nodes. Enabling encryption in transit addresses problems of misuse and tampering during this transmission. | Audit, Deny, Disabled | Audit | Audit | Deny | HDInsight | Data | 1.0.0 | BuiltIn | Essential | No | No |
