# SQL Server Policies

| # | Policy | Tag | Description | Allowed Values | Default Value | MVP Value | Category | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Configure Arc-enabled Servers with SQL Server extension installed to enable or disable SQL best practices assessment. |  | Enable or disable SQL best practices assessment on the SQL server instances on your Arc-enabled servers to evaluate best practices. Learn more at https://aka.ms/azureArcBestPracticesAssessment. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | SQL Server | 1.0.1 | BuiltIn | Essential |
| 2 | Enable system-assigned identity to SQL VM | Preview | Enable system-assigned identity at scale to SQL virtual machines. You need to assign this policy at subscription level. Assign at resource group level will not work as expected. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | SQL Server | 1.0.0-preview | BuiltIn | Essential |
| 3 | Subscribe eligible Arc-enabled SQL Servers instances to Extended Security Updates. |  | Subscribe eligible Arc-enabled SQL Servers instances with License Type set to Paid or PAYG to Extended Security Updates. More on extended security updates https://go.microsoft.com/fwlink/?linkid=2239401. | DeployIfNotExists, Disabled | DeployIfNotExists | DeployIfNotExists | SQL Server | 1.0.0 | BuiltIn | Essential |
