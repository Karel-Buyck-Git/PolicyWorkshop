# Company Storage Professional — ElasticSan

## Tier rationale

**Professional** — Active security posture for ElasticSan: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ElasticSan should disable public network access | 6a92fe1f-0b86-44ae-843d-2db3d2b571ae |  | Disable public network access for your ElasticSan so that it's not accessible over the public internet. This can reduce data leakage risks. | Audit, Deny, Disabled | Audit | Audit | Deny | ElasticSan | Storage | 1.0.0 | BuiltIn | Professional | No | No |
