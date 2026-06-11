# Company Compute Essential — Stack HCI

## Tier rationale

**Essential** — Baseline hygiene for Azure Stack HCI: the non-negotiable controls every deployment should enforce from day one. This tier delivers encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Stack HCI servers should meet Secured-core requirements | 5e6bf724-0154-49bc-985f-27b2e07e636b | Preview | Ensure that all Azure Stack HCI servers meet the Secured-core requirements. To enable the Secured-core server requirements: 1. From the Azure Stack HCI clusters page, go to Windows Admin Center and select Connect. 2. Go to the Security extension and select Secured-core. 3. Select any setting that is not enabled and click Enable. | Audit, Disabled, AuditIfNotExists | AuditIfNotExists | Audit | AuditIfNotExists | Stack HCI | Compute | 1.0.0-preview | BuiltIn | Essential | No | No |
| 2 | Azure Stack HCI systems should have encrypted volumes | ee8ca833-1583-4d24-837e-96c2af9488a4 | Preview | Use BitLocker to encrypt the OS and data volumes on Azure Stack HCI systems. | Audit, Disabled, AuditIfNotExists | AuditIfNotExists | Audit | AuditIfNotExists | Stack HCI | Compute | 1.0.0-preview | BuiltIn | Essential | No | No |
| 3 | Host and VM networking should be protected on Azure Stack HCI systems | 36f0d6bc-a253-4df8-b25b-c3a5023ff443 | Preview | Protect data on the Azure Stack HCI hosts network and on virtual machine network connections. | Audit, Disabled, AuditIfNotExists | AuditIfNotExists | Audit | AuditIfNotExists | Stack HCI | Compute | 1.0.0-preview | BuiltIn | Essential | No | No |
