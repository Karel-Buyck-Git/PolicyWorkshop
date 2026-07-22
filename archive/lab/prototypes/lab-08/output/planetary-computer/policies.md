# Planetary Computer Policies

## Tier rationaleHardened

**Essential** — Baseline hygiene for Planetary Computer: the non-negotiable controls every deployment should enforce from day one. This tier delivers RBAC and managed-identity controls eliminating shared credentials. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for Planetary Computer in the current built-in policy set.

**Enterprise** — No enterprise-tier policies are defined for Planetary Computer in the current built-in policy set.

| #   | Policy                                                                     | Policy ID                            | Tag | Description                                                                                                                                                                                 | Allowed Values        | Default Value | Hardened Value | Category           | Version | Type    | Tier      |
| --- | -------------------------------------------------------------------------- | ------------------------------------ | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- | ------------- | -------------- | ------------------ | ------- | ------- | --------- |
| 1   | Microsoft Planetary Computer Pro GeoCatalogs should use a managed identity | 9fac9537-cba6-480a-97dc-21a93c1aa055 |     | Assigning a managed identity to a Planetary Computer GeoCatalog lets it securely access source Storage accounts (Storage Blob Data Reader) for data ingestion without you managing secrets. | Audit, Deny, Disabled | Audit         | Deny           | Planetary Computer | 1.0.0   | BuiltIn | Essential |
