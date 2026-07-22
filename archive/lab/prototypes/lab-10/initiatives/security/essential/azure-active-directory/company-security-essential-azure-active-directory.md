# Company Security Essential — Azure Active Directory

## Tier rationale

**Essential** — Baseline hygiene for Microsoft Entra ID (Azure AD): the non-negotiable controls every deployment should enforce from day one. This tier delivers TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Active Directory Domain Services managed domains should use TLS 1.2 only mode | 3aa87b5a-7813-4b57-8a43-42dd9df5aaa7 |  | Use TLS 1.2 only mode for your managed domains. By default, Azure AD Domain Services enables the use of ciphers such as NTLM v1 and TLS v1. These ciphers may be required for some legacy applications, but are considered weak and can be disabled if you don't need them. When TLS 1.2 only mode is enabled, any client making a request that is not using TLS 1.2 will fail. Learn more at https://docs.microsoft.com/azure/active-directory-domain-services/secure-your-domain. | Audit, Deny, Disabled | Audit | Audit | Deny | Azure Active Directory | Security | 1.1.0 | BuiltIn | Essential | No | No |
