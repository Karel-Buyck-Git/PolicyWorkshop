# Company Data Professional — HDInsight

## Tier rationale

**Professional** — Active security posture for HDInsight: controls that produce signals an operations team must act on. This tier delivers network hardening (public access disabled, VNet integration, firewall rules). Together these policies protect against unauthorized network exposure, exploitable vulnerabilities, and undetected privilege misuse. Maps to NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Azure HDInsight clusters should be injected into a virtual network | b0ab5b05-1c98-40f7-bb9e-dc568e41b501 |  | Injecting Azure HDInsight clusters in a virtual network unlocks advanced HDInsight networking and security features and provides you with control over your network security configuration. | Audit, Disabled, Deny | Audit | Audit | Deny | HDInsight | Data | 1.0.0 | BuiltIn | Professional | No | No |
