# Company Data Essential — SQL Server

## Tier rationale

**Essential** — Baseline hygiene for SQL Server: the non-negotiable controls every deployment should enforce from day one. This tier delivers TLS / HTTPS enforcement preventing in-transit interception. Together these policies protect against credential theft, unencrypted data exposure, and accidental data loss. Maps to CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations).

## Policies

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Arc-enabled Servers with SQL Server extension installed to enable or disable SQL best practices assessment. | f36de009-cacb-47b3-b936-9c4c9120d064 |  | Enable or disable SQL best practices assessment on the SQL server instances on your Arc-enabled servers to evaluate best practices. Learn more at https://aka.ms/azureArcBestPracticesAssessment. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | SQL Server | Data | 1.0.1 | BuiltIn | Essential | Yes | Yes |
| 2 | Enable system-assigned identity to SQL VM | 7148a409-0d59-4baa-925b-b3aae486a14e | Preview | Enable system-assigned identity at scale to SQL virtual machines. You need to assign this policy at subscription level. Assign at resource group level will not work as expected. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | SQL Server | Data | 1.0.0-preview | BuiltIn | Essential | No | Yes |
| 3 | Subscribe eligible Arc-enabled SQL Servers instances to Extended Security Updates. | f692cc79-76fb-4c61-8861-467e454ac6f8 |  | Subscribe eligible Arc-enabled SQL Servers instances with License Type set to Paid or PAYG to Extended Security Updates. More on extended security updates https://go.microsoft.com/fwlink/?linkid=2239401. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | DeployIfNotExists | SQL Server | Data | 1.0.0 | BuiltIn | Essential | Yes | Yes |
