# Azure Stack Edge Policies

## Tier rationale

**Essential** — Baseline hygiene for Azure Stack Edge: the non-negotiable controls every deployment should enforce from day one. This tier delivers encryption-at-rest with service-managed keys. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for Azure Stack Edge in the current built-in policy set.

**Enterprise** — No enterprise-tier policies are defined for Azure Stack Edge in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Stack Edge devices should use double-encryption | b4ac1030-89c5-4697-8e00-28b5ba6a8811 |  | To secure the data at rest on the device, ensure it's double-encrypted, the access to data is controlled, and once the device is deactivated, the data is securely erased off the data disks. Double encryption is the use of two layers of encryption: BitLocker XTS-AES 256-bit encryption on the data volumes and built-in encryption of the hard drives. Learn more in the security overview documentation for the specific Stack Edge device. | No | No | Audit, Audit, Deny, Deny, Disabled, Disabled | Audit | Audit | Deny | Azure Stack Edge | Compute | 1.1.0 | BuiltIn | Essential |
