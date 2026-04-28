# Professional

**_Professional: Azure Hardened Virtual Datacenter_**
  Designed for production workloads, this tier introduces enhanced operational resilience and network hardening. It mandates the use of high-availability services with guaranteed SLAs, explicitly excluding "Dev/Test" SKUs. Security is bolstered through comprehensive auditing, centralized logging, and advanced diagnostics, providing the visibility required for professional monitoring and rapid incident response.


- Security Posture Optimization: Establishes an enforceable production posture by standardizing secure configuration defaults and reducing drift. Uses Azure Policy initiatives (Audit/Deny/Modify/DeployIfNotExists where appropriate) at management-group scope to keep security outcomes consistent across subscriptions.
  - Examples (AzAdvertizer): Allowed locations (`e56962a6-4747-49cd-b67b-bf8b01975c4c`), Allowed resource types (`a08ec900-254a-4555-9bf5-e42af04b5c5c`), Require a tag and its value on resources (`1e30110a-5ceb-460c-a204-c1c3969c6d62`), Inherit a tag from the resource group (`cd3aa116-8754-49c9-a813-ad46512ece54`).

- Vulnerability management: Ensures vulnerability signals are collected and acted on by requiring supported security assessments and recommendations for in-scope services. Enforces configuration prerequisites via Azure Policy where possible, and relies on integrated security tooling for detection and prioritization.
  - Examples (AzAdvertizer): Transparent Data Encryption on SQL databases should be enabled (`17k78e20-9358-41c9-923c-fb736d382a12`), Auditing on SQL server should be enabled (`a6fb4358-5bf4-4ad7-ba82-2cd2f41ce5e9`), Key Vault secrets should have an expiration date (`98728c90-32c7-4049-8429-847dc0f4fe37`), Storage accounts should prevent shared key access (`8c6a50c6-9ffd-4ae7-986f-5fa6111f9a54`).

- Identity governance: Governs privileged access and role hygiene to support least privilege and controlled elevation. Uses Azure Policy to prevent risky authorization patterns on Azure resources, and aligns with tenant identity governance practices for administrative workflows.
  - Examples (AzAdvertizer): Audit usage of custom RBAC roles (`a451c1ef-c6ca-483d-87ed-f49761e3ffb5`), Accounts with owner permissions should be MFA enabled (`e3e008c3-56b9-4133-8fd7-d3347377402a`), Deprecated accounts should be removed from your subscription (`8d7e1fde-fe26-4b5f-8108-f8e432cbc2be`), An Azure AD administrator should be provisioned for SQL servers (`1f314764-cb73-4fc9-b863-8eca98ac36e9`).

- Network hardening: Reduces exposure by enforcing segmentation and secure connectivity patterns (for example, NSG association, restricted inbound access, and elimination of unnecessary public endpoints where enforceable). Policies are applied consistently to support production-grade network boundaries.
  - Examples (AzAdvertizer): Network interfaces should not have public IPs (`83a86a26-fd1f-447c-b59d-e51f44264114`), Subnets should be associated with a Network Security Group (`e71308d3-144b-4262-b144-efdc3cc90517`), Container Apps environment should disable public network access (`d074ddf8-01a5-4b5e-a2b8-964aed452c0a`), Azure AI Services — configure accounts to disable public network access (`47ba1dd7-28d9-4b07-a8d5-9813bed64e0c`).

- Forced token renewals: Implements session and access lifetime controls to reduce the impact of credential compromise and long-lived sessions. This is primarily enforced through tenant identity controls (for example, Conditional Access session policies) and monitored as part of the overall compliance posture.
  - Examples (AzAdvertizer, related identity guardrails): Accounts with owner permissions should be MFA enabled (`e3e008c3-56b9-4133-8fd7-d3347377402a`), Deprecated accounts should be removed from your subscription (`8d7e1fde-fe26-4b5f-8108-f8e432cbc2be`).

- Compliance reporting: Produces auditable evidence of control implementation using Azure Policy compliance results, standardized initiative structure, and exportable reporting. Enables continuous compliance views suitable for internal governance and external assurance.
  - Examples (AzAdvertizer): Allowed locations (`e56962a6-4747-49cd-b67b-bf8b01975c4c`), Allowed resource types (`a08ec900-254a-4555-9bf5-e42af04b5c5c`), Secure transfer to storage accounts should be enabled (`34c877ad-507e-4c82-993e-3452a6e0ad3c`), App Service apps should only be accessible over HTTPS (`a4af4a39-4135-47fb-b175-47fbdf85311d`).

- Auto remediation: Uses policy-driven remediation (Modify/DeployIfNotExists) and controlled remediation tasks to converge resources toward the intended configuration state. Balances automation with safe rollout patterns and exception handling.
  - Examples (AzAdvertizer): Inherit a tag from the resource group (Modify) (`cd3aa116-8754-49c9-a813-ad46512ece54`), Configure Event Hub namespaces to disable local authentication (Modify) (`57f35901-8389-40bb-ac49-3ba4f86d889d`), Configure to disable non-SSL ports (Modify) (`766f5de3-c6c0-4327-9f4d-042ab8ae846c`), Enable logging to Log Analytics (DeployIfNotExists) (`69e0da8f-ca50-479d-b1a8-33a31426c512`).

- Auditing & Observability: Requires centralized logging and diagnostics to enable professional monitoring, detection, and incident response. Enforces diagnostic settings and log destinations where supported, and audits coverage for services that cannot be auto-configured.
  - Examples (AzAdvertizer): Service Bus — resource logs should be enabled (`f8d36e2f-389b-4ee4-898d-21aeb69a0f45`), Event Hubs — resource logs should be enabled (`83a214f7-d01a-484b-91a9-ed54470c9a6a`), Logic Apps — resource logs should be enabled (`34f95f76-5386-4de7-b824-0d8478470c9d`), Azure Machine Learning — resource logs should be enabled (`afe0c3be-ba3b-4544-ba52-0c99672a8ad6`).

- Everything in Essential: Includes all Essential guardrails; Professional adds production-strength hardening, compliance evidence, and operational control depth.
  - Examples (AzAdvertizer): Network interfaces should not have public IPs (`83a86a26-fd1f-447c-b59d-e51f44264114`), Require a tag and its value on resources (`1e30110a-5ceb-460c-a204-c1c3969c6d62`), Secure transfer to storage accounts should be enabled (`34c877ad-507e-4c82-993e-3452a6e0ad3c`), Key Vault purge protection should be enabled (`0b60c0b2-2dc2-4e1c-b5c9-abbed971de53`).
