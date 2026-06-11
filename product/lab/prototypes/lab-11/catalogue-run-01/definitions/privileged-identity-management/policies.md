# Privileged Identity Management Policies

## Tier rationale

**Essential** — No essential-tier policies are defined for Privileged Identity Management in the current built-in policy set.

**Professional** — Active security posture for Privileged Identity Management: controls that produce signals an operations team must act on. This tier delivers privileged identity management and just-in-time access. Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

**Enterprise** — No enterprise-tier policies are defined for Privileged Identity Management in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure role assignment management should be restricted to Microsoft Entra Privileged Identity Management | 25237d14-4a47-4cb6-bc7c-8bbdd4671f31 |  | Ensures all Azure role assignments are made via Microsoft Entra PIM or explicitly approved apps; others are denied by default. Admins can allow exceptions for specific roles, users, or groups (e.g., break‑glass access). Existing role assignments are unaffected. Ensure your tenant has the required PIM licensing before enabling this policy; otherwise, access may be unintentionally blocked. | Audit, Deny, Disabled | Deny | Audit | Deny | Privileged Identity Management | undefined | 1.0.0 | BuiltIn | Professional | No | No |
