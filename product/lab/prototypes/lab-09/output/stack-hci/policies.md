# Stack HCI Policies

## Tier rationale

**Essential** — Baseline hygiene for Azure Stack HCI: the non-negotiable controls every deployment should enforce from day one. This tier delivers encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — Active security posture for Azure Stack HCI: controls that produce signals an operations team must act on. This tier delivers Microsoft Defender plans surfacing threat signals. Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — No enterprise-tier policies are defined for Azure Stack HCI in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Stack HCI servers should meet Secured-core requirements | 5e6bf724-0154-49bc-985f-27b2e07e636b | Preview | Ensure that all Azure Stack HCI servers meet the Secured-core requirements. To enable the Secured-core server requirements: 1. From the Azure Stack HCI clusters page, go to Windows Admin Center and select Connect. 2. Go to the Security extension and select Secured-core. 3. Select any setting that is not enabled and click Enable. | Audit, Disabled, AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Stack HCI | Compute | 1.0.0-preview | BuiltIn | Essential |
| 2 | Azure Stack HCI systems should have encrypted volumes | ee8ca833-1583-4d24-837e-96c2af9488a4 | Preview | Use BitLocker to encrypt the OS and data volumes on Azure Stack HCI systems. | Audit, Disabled, AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Stack HCI | Compute | 1.0.0-preview | BuiltIn | Essential |
| 3 | Host and VM networking should be protected on Azure Stack HCI systems | 36f0d6bc-a253-4df8-b25b-c3a5023ff443 | Preview | Protect data on the Azure Stack HCI hosts network and on virtual machine network connections. | Audit, Disabled, AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Stack HCI | Compute | 1.0.0-preview | BuiltIn | Essential |
| 4 | Azure Stack HCI servers should have consistently enforced application control policies | dad3a6b9-4451-492f-a95c-69efc6f3fada | Preview | At a minimum, apply the Microsoft WDAC base policy in enforced mode on all Azure Stack HCI servers. Applied Windows Defender Application Control (WDAC) policies must be consistent across servers in the same cluster. | Audit, Disabled, AuditIfNotExists | AuditIfNotExists | AuditIfNotExists | Stack HCI | Compute | 1.0.0-preview | BuiltIn | Professional |
