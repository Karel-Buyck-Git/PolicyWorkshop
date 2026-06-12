# Trusted Launch Policies

## Tier rationale

**Essential** — Baseline hygiene for Trusted Launch: the non-negotiable controls every deployment should enforce from day one. This tier delivers TLS / HTTPS enforcement preventing in-transit interception and tagging, SKU, and naming controls for cost and ownership accountability. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

**Professional** — No professional-tier policies are defined for Trusted Launch in the current built-in policy set.

**Enterprise** — No enterprise-tier policies are defined for Trusted Launch in the current built-in policy set.

| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Disks and OS image should support TrustedLaunch | b03bb370-5249-4ea4-9fce-2552e87e45fa |  | TrustedLaunch improves security of a Virtual Machine which requires OS Disk & OS Image to support it (Gen 2). To learn more about TrustedLaunch, visit https://aka.ms/trustedlaunch | No | No | Audit, Disabled | Audit | Audit | Audit | Trusted Launch | Compute | 1.0.0 | BuiltIn | Essential |
| 2 | Virtual Machine should have TrustedLaunch enabled | c95b54ad-0614-4633-ab29-104b01235cbf |  | Enable TrustedLaunch on Virtual Machine for enhanced security, use VM SKU (Gen 2) that supports TrustedLaunch. To learn more about TrustedLaunch, visit https://learn.microsoft.com/en-us/azure/virtual-machines/trusted-launch | No | No | Audit, Disabled | Audit | Audit | Audit | Trusted Launch | Compute | 1.0.0 | BuiltIn | Essential |
