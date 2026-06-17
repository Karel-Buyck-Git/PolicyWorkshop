# Company undefined Professional — Health Deidentification Service

## Tier rationale

**Professional** — Active security posture for Health Deidentification Service: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure Health Data Services de-identification service should disable public network access | c5f34731-7ab9-42ff-922d-ef4920068b74 |  | Disabling public network access improves security by ensuring that the resource isn't exposed on the public internet. You can limit exposure of your resources by creating private endpoints instead. | Audit, Disabled | Audit | Audit | Audit | Health Deidentification Service | undefined | 1.0.0 | BuiltIn | Professional | No | No |
