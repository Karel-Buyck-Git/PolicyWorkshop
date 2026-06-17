# PaaS Baseline

- **_Minimal: Azure Foundational Governance & Security_**
  This tier serves as the entry-level baseline, establishing a secure, cost-efficient baseline using automated Azure Policy and Management Group hierarchies. It enforces essential governance "guardrails" such as naming convention and mandatory resource tagging to ensure environment consistency and accurate cost tracking. While optimized for low overhead, it applies the same rigorous Role-Based Access Control (RBAC) and identity standards as higher tiers to maintain a unified security posture. Enforcing standardized protocols, embedded resilience, and hardened cryptography across all resources.

- **_Standard: Azure Hardened Virtual Datacenter_**
  Designed for production workloads, this tier introduces enhanced operational resilience and network hardening. It mandates the use of high-availability services with guaranteed SLAs, explicitly excluding "Dev/Test" SKUs. Security is bolstered through comprehensive auditing, centralized logging, and advanced diagnostics, providing the visibility required for professional monitoring and rapid incident response.

- **_Premium: Azure Advanced Enterprise Isolation_**
  The highest tier provides a comprehensive, "Zero Trust" architecture designed for sensitive data and critical business applications. It moves beyond standard security by implementing full Private Link integration to eliminate public internet exposure. Introducing Conditional access and Privileged Identity Management. This level incorporates granular micro-segmentation, continuous verification, and advanced traffic inspection to meet the most demanding compliance and isolation requirements.

---

## Web & Container Services

| Service                  | Policy Description                                  | Policy ID                            | Effect     | Category | Notes                     | Tier     |
| ------------------------ | --------------------------------------------------- | ------------------------------------ | ---------- | -------- | ------------------------- | -------- |
| App Service              | Apps should only be accessible over HTTPS           | a4af4a39-4135-47fb-b175-47fbdf85311d | Audit/Deny | Built-in |                           | Minimal  |
| App Service              | Apps should use the latest TLS version              | f0e6e85b-9b9f-4a4b-b67b-f730d42f1b0b | Audit      | Built-in |                           | Minimal  |
| App Service              | Apps should use managed identity                    | 2b9ad585-36bc-4615-b300-fd4435808332 | Audit      | Built-in |                           | Minimal  |
| App Service              | Apps should require FTPS only                       | 4d24b6d4-5e53-4a4f-a7f4-618fa573ee4b | Audit      | Built-in |                           | Minimal  |
| Azure Functions          | Should only be accessible over HTTPS                | 6d555dd1-86f2-4f1c-8ed7-5abae7c6cbab | Audit/Deny | Built-in |                           | Minimal  |
| Azure Functions          | Should use the latest TLS version                   | f9d614c5-c173-4d56-95a7-b4437057d193 | Audit      | Built-in |                           | Minimal  |
| Azure Functions          | Should use managed identity                         | 0da106f2-4ca3-48e8-bc85-c638fe6aea8f | Audit      | Built-in |                           | Minimal  |
| Azure Functions          | Should require FTPS only                            | 399b2637-a50f-4f95-96f8-3a145476eb15 | Audit      | Built-in |                           | Minimal  |
| Container Apps           | Managed identity should be enabled                  | b874ab2d-72dd-47f1-8cb5-4a306478a4e7 | Audit      | Built-in |                           | Minimal  |
| Container Apps           | Should only be accessible over HTTPS                | 0e80e269-43a4-4ae9-b5bc-178126b8a5cb | Audit      | Built-in |                           | Minimal  |
| Container Apps           | Authentication should be enabled                    | 2b585559-a78e-4cc4-b1aa-fb169d2f6b96 | Audit      | Built-in |                           | Minimal  |
| Container Apps           | Environment should disable public network access    | d074ddf8-01a5-4b5e-a2b8-964aed452c0a | Audit      | Built-in |                           | Standard |
| Container Apps           | App environments should use network injection       | 8b346db6-85af-419b-8557-92cee2c0f9bb | Audit      | Built-in |                           | Premium  |
| Container Apps           | Should disable external network access              | 783ea2a8-b8fd-46be-896a-9ae79643a0b1 | Audit      | Built-in |                           | Premium  |
| Azure Spring Apps        | Should use network injection                        | af35e2a4-ef96-44e7-a9ae-853dd97032c4 | Audit      | Built-in | Limited built-in coverage | Standard |
| Azure Kubernetes Service | Clusters should have local auth disabled            | 993c2fcd-2b29-49d2-9eb0-df2c3a730c32 | Audit      | Built-in |                           | Minimal  |
| Azure Kubernetes Service | Clusters should be accessible only over HTTPS       | 1a5b4dca-0b6f-4cf5-907c-56316bc1bf3d | Audit      | Built-in |                           | Minimal  |
| Azure Kubernetes Service | Azure Policy Add-on should be installed and enabled | 0a15ec92-a229-4763-bb14-0ea34a568f8d | Audit      | Built-in |                           | Standard |
| Azure Batch              | Accounts should have local auth disabled            | 6f68b69f-05fe-49cd-b361-777ee9ca7e35 | Audit      | Built-in |                           | Minimal  |
| Azure Batch              | Resource logs in Batch accounts should be enabled   | 428256e6-1fac-4f48-a757-df34c2b3336d | Audit      | Built-in |                           | Standard |

---

## Data & Storage

| Service                    | Policy Description                                                | Policy ID                            | Effect     | Category | Notes                                                     |
| -------------------------- | ----------------------------------------------------------------- | ------------------------------------ | ---------- | -------- | --------------------------------------------------------- |
| Azure SQL Database         | Should be running TLS 1.2 or newer                                | 32e6bbec-16b6-44c2-be37-c5b672d103cf | Audit      | Built-in |                                                           |
| Azure SQL Database         | Entra admin should be provisioned for SQL servers                 | 1f314764-cb73-4fc9-b863-8eca98ac36e9 | Audit      | Built-in |                                                           |
| Azure SQL Database         | Transparent Data Encryption should be enabled                     | 17k78e20-9358-41c9-923c-fb736d382a12 | Audit      | Built-in | Verify ID on AzAdvertizer                                 |
| Azure SQL Database         | Auditing on SQL server should be enabled                          | a6fb4358-5bf4-4ad7-ba82-2cd2f41ce5e9 | Audit      | Built-in |                                                           |
| Azure SQL Database         | Entra-only authentication during creation                         | abda6d70-9778-44e7-84a8-06713e6db027 | Audit      | Built-in | Applies at resource creation time                         |
| Azure SQL Managed Instance | Entra-only authentication during creation                         | 78215662-041e-49ed-a9dd-5385911b3a1f | Audit      | Built-in | Applies at resource creation time                         |
| Azure SQL Managed Instance | Entra-only authentication should be enabled                       | 0c28c3fb-c244-42d5-a9bf-f35f2999577b | Audit      | Built-in |                                                           |
| Azure SQL Managed Instance | Should disable public network access                              | 9dfea752-dd46-4766-aed1-c355fa93fb91 | Audit      | Built-in |                                                           |
| Azure SQL Managed Instance | Minimum TLS version should be 1.2                                 | a8793640-60f7-487c-b5c3-1d37215905c4 | Audit      | Built-in |                                                           |
| Storage Accounts           | Secure transfer to storage accounts should be enabled             | 34c877ad-507e-4c82-993e-3452a6e0ad3c | Audit/Deny | Built-in |                                                           |
| Storage Accounts           | Minimum TLS version should be enforced                            | fe83a0eb-a853-422d-aac2-1bffd182c5d0 | Audit      | Built-in | Default param: TLS1_2                                     |
| Storage Accounts           | Should prevent shared key access                                  | 8c6a50c6-9ffd-4ae7-986f-5fa6111f9a54 | Audit/Deny | Built-in | May break legacy workloads – run Audit first              |
| Storage Accounts           | Should have SAS expiry policy configured                          | bc1b984e-ddae-40cc-801a-050a030e4fbe | Audit      | Built-in |                                                           |
| Storage Accounts           | SAS tokens should adhere to 7-day max validity                    | 7aa1c9d5-3d7e-4579-8117-d85e99211757 | Audit/Deny | Built-in |                                                           |
| Azure Cosmos DB            | Should disable local authentication                               | 5450f5bd-9c72-4390-a9c4-a7aba4edfdd2 | Audit/Deny | Built-in |                                                           |
| Azure Cosmos DB            | Key-based metadata write access should be disabled                | 4750c32b-89c0-46af-bfcb-2e4541a818d5 | Audit      | Built-in |                                                           |
| Azure Cosmos DB            | Accounts should have firewall rules                               | 862e97cf-49fc-4a5c-9de4-40d4e2e7c8eb | Audit      | Built-in |                                                           |
| Azure Cosmos DB            | Throughput should be limited                                      | 0b7ef78e-a035-4f23-b9bd-aff122a1b1cf | Audit      | Built-in | Requires max throughput parameter                         |
| PostgreSQL Flexible Server | Entra-only authentication should be enabled                       | 7c90f6d1-f79a-4c1c-b44a-4a655d4774f0 | Deny       | Built-in |                                                           |
| PostgreSQL Flexible Server | Entra administrator should be provisioned                         | ce39a96d-bf09-4b60-8c32-e85d52abea0f | Audit      | Built-in |                                                           |
| PostgreSQL Flexible Server | Enforce SSL connection should be enabled                          | c29c38cb-74a7-4505-9a06-e588ab86620a | Audit      | Built-in |                                                           |
| PostgreSQL Flexible Server | Should run TLS 1.2 or newer                                       | a43d5475-c569-45ce-a268-28fa79f4e87a | Audit      | Built-in |                                                           |
| PostgreSQL Flexible Server | Public network access should be disabled                          | 5e1de0e3-42cb-4ebc-a86d-61d0c619ca48 | Audit      | Built-in |                                                           |
| MySQL Flexible Server      | Entra-only authentication should be enabled                       | 40e85574-ef33-47e8-a854-7a65c7500560 | Audit      | Built-in |                                                           |
| MySQL Flexible Server      | Entra administrator should be provisioned                         | 146412e9-005c-472b-9e48-c87b72ac229e | Audit      | Built-in |                                                           |
| MySQL Flexible Server      | Require Secure Transport should be enabled                        | 49e6f04d-fbc3-4ac3-9e84-6ae0eb5db024 | Audit      | Built-in |                                                           |
| MySQL Flexible Server      | Public network access should be disabled                          | c9299215-ae47-4f50-9c54-8a392f68a052 | Audit      | Built-in |                                                           |
| Azure Database for MariaDB | Public network access should be disabled                          | fdccbe47-f3e3-4213-ad5d-ea459b2fa077 | Audit      | Built-in | Legacy service – limited policy coverage                  |
| Azure Synapse Analytics    | Entra-only authentication during workspace creation               | 2158ddbe-fefa-408e-b43f-d4faef8ff3b8 | Audit      | Built-in | Applies at resource creation time                         |
| Azure Synapse Analytics    | Entra-only authentication should be enabled                       | 6ea81a52-5ca7-4575-9669-eaa910b7edf8 | Audit      | Built-in |                                                           |
| Azure Synapse Analytics    | Dedicated SQL pools should enable encryption                      | cfaf0007-99c7-4b01-b36b-4048872ac978 | Audit      | Built-in |                                                           |
| Azure Synapse Analytics    | SQL Server TLS should be 1.2 or newer                             | cb3738a6-82a2-4a18-b87b-15217b9deff4 | Audit      | Built-in |                                                           |
| Azure Synapse Analytics    | IP firewall rules should be removed                               | 56fd377d-098c-4f02-8406-81eb055902b8 | Audit      | Built-in |                                                           |
| Azure Synapse Analytics    | Should disable public network access                              | 38d8df46-cf4e-4073-8e03-48c24b29de0d | Audit      | Built-in |                                                           |
| Azure Synapse Analytics    | Managed private endpoints should only connect to approved tenants | 3a003702-13d2-4679-941b-937e58c443f0 | Audit      | Built-in |                                                           |
| Azure Data Explorer        | Disk encryption should be enabled                                 | f4b53539-8df9-40e4-86c6-6b607703bd4e | Audit      | Built-in |                                                           |
| Azure Data Explorer        | Double encryption should be enabled                               | ec068d99-e9c7-401f-8cef-5bdde4e6ccf1 | Audit      | Built-in |                                                           |
| Azure Data Explorer        | Public network access should be disabled                          | 43bc7be6-5e69-4b0d-a2bb-e815557ca673 | Audit      | Built-in |                                                           |
| Azure Databricks           | Clusters should disable public IP                                 | 51c1490f-3319-459c-bbbc-7f391bbed753 | Audit      | Built-in |                                                           |
| Azure Databricks           | Workspaces should disable public network access                   | 0e7849de-b939-4c50-ab48-fc6b0f5eeba2 | Audit      | Built-in |                                                           |
| Azure Databricks           | Workspaces should be in a virtual network                         | 9c25c9e4-ee12-4882-afd2-11fb9d87893f | Audit      | Built-in |                                                           |
| Azure Databricks           | Deny non-Premium SKU                                              | Deny-Databricks-Sku                  | Deny       | ALZ      | ALZ community policy – deploy via EPAC Definitions folder |

---

## Integration

| Service              | Policy Description                                 | Policy ID                            | Effect     | Category | Notes                                          |
| -------------------- | -------------------------------------------------- | ------------------------------------ | ---------- | -------- | ---------------------------------------------- |
| Azure Service Bus    | Should disable local authentication                | cfb11c26-f069-4c14-8e36-56c394dae5af | Audit/Deny | Built-in |                                                |
| Azure Service Bus    | Root management access rule should not be used     | a1817ec0-a368-432a-8057-8371e17ac6ee | Audit      | Built-in |                                                |
| Azure Service Bus    | Resource logs should be enabled                    | f8d36e2f-389b-4ee4-898d-21aeb69a0f45 | Audit      | Built-in |                                                |
| Azure Event Hubs     | Should disable local authentication                | 57f35901-8389-40bb-ac49-3ba4f86d889d | Modify     | Built-in | Requires managed identity on policy assignment |
| Azure Event Hubs     | Instance-level auth rules should be defined        | f4826e5f-6a27-407c-ae3e-9582eb39891d | Audit      | Built-in |                                                |
| Azure Event Hubs     | Resource logs should be enabled                    | 83a214f7-d01a-484b-91a9-ed54470c9a6a | Audit      | Built-in |                                                |
| Azure Event Grid     | Domains – local auth should be disabled            | 8bfadddb-ee1c-4639-8911-a38cb8e0b3bd | Audit      | Built-in |                                                |
| Azure Event Grid     | Configure domains to disable local auth            | 1c8144d9-746a-4501-b08c-093c8d29ad04 | Modify     | Built-in | Requires managed identity on policy assignment |
| Azure Event Grid     | Topics – local auth should be disabled             | ae9fb87f-8a17-4428-94a4-8135d431055c | Audit      | Built-in |                                                |
| Azure Logic Apps     | Resource logs should be enabled                    | 34f95f76-5386-4de7-b824-0d8478470c9d | Audit      | Built-in |                                                |
| Azure Data Factory   | Linked services should use managed identity auth   | f78ccdb4-7bf4-4106-8647-270491d2978a | Audit      | Built-in |                                                |
| Azure Data Factory   | Linked services should use Key Vault for secrets   | 127ef6d7-242f-43b3-9eef-947faf1725d0 | Audit      | Built-in |                                                |
| Azure Data Factory   | Public network access should be disabled           | 1cf164be-6819-4a50-b8fa-4bcaa4f98fb6 | Audit      | Built-in |                                                |
| Azure API Management | Backend calls should be authenticated              | c15dcc82-b93c-4dcb-9332-fbf121685b54 | Audit      | Built-in |                                                |
| Azure API Management | Username/password auth should be disabled          | 1b0d74ac-4b43-4c39-a15f-594385adc38d | Modify     | Built-in | Requires managed identity on policy assignment |
| Azure API Management | Public service config endpoints should be disabled | df73bd95-24da-4a4f-96b9-4e8b94b402bd | Audit      | Built-in |                                                |

---

## Security

| Service         | Policy Description                              | Policy ID                            | Effect     | Category | Notes                                               |
| --------------- | ----------------------------------------------- | ------------------------------------ | ---------- | -------- | --------------------------------------------------- |
| Azure Key Vault | Keys should have an expiration date             | 152b15f7-8e1f-4c1f-ab71-8c010ba5dbc0 | Audit      | Built-in |                                                     |
| Azure Key Vault | Secrets should have an expiration date          | 98728c90-32c7-4049-8429-847dc0f4fe37 | Audit      | Built-in | Enforce secret rotation                             |
| Azure Key Vault | Should have soft delete enabled                 | 1e66c121-a66a-4b1f-9b83-0fd99bf0fc2d | Audit      | Built-in | Soft delete is default on new vaults; audits legacy |
| Azure Key Vault | Should have purge (deletion) protection enabled | 0b60c0b2-2dc2-4e1c-b5c9-abbed971de53 | Audit/Deny | Built-in |                                                     |

---

## Containers

| Service                  | Policy Description                           | Policy ID                            | Effect     | Category | Notes |
| ------------------------ | -------------------------------------------- | ------------------------------------ | ---------- | -------- | ----- |
| Azure Container Registry | Local admin account should be disabled       | dc921057-6b28-4fbe-9b83-f7bec05db6c2 | Audit/Deny | Built-in |       |
| Azure Container Registry | Anonymous authentication should be disabled  | 9f2dea28-e834-476c-99c5-3507b4728395 | Audit/Deny | Built-in |       |
| Azure Container Registry | Should not allow unrestricted network access | d0793b48-0edc-4296-a390-4c75d1bdfd71 | Audit      | Built-in |       |

---

## Cache

| Service               | Policy Description                            | Policy ID                            | Effect     | Category | Notes                                          |
| --------------------- | --------------------------------------------- | ------------------------------------ | ---------- | -------- | ---------------------------------------------- |
| Azure Cache for Redis | Only secure connections should be enabled     | 22bee202-a82f-4305-9a2a-6d7f44d4dedb | Audit/Deny | Built-in |                                                |
| Azure Cache for Redis | Configure to disable non-SSL ports            | 766f5de3-c6c0-4327-9f4d-042ab8ae846c | Modify     | Built-in | Requires managed identity on policy assignment |
| Azure Cache for Redis | Should not use access keys for authentication | 3827af20-8f80-4b15-8300-6db0873ec901 | Audit      | Built-in |                                                |

---

## AI & Machine Learning

| Service                | Policy Description                                   | Policy ID                            | Effect           | Category | Notes                                          |
| ---------------------- | ---------------------------------------------------- | ------------------------------------ | ---------------- | -------- | ---------------------------------------------- |
| Azure AI Services      | Key access should be disabled (Entra-only)           | 71ef260a-8f18-47b7-abcb-62d0673d94dc | Audit/Deny       | Built-in | Disables local key-based authentication        |
| Azure AI Services      | Should use managed identity                          | fe3fd216-4f83-4fc1-8984-2bbec80a3418 | Audit            | Built-in |                                                |
| Azure AI Search        | Disable local authentication                         | 4eb216f2-9dba-4979-86e6-5d7e63ce3b75 | Modify           | Built-in | Requires managed identity on policy assignment |
| Azure AI Search        | Should disable public network access                 | ee980b6d-0eca-4501-8d54-f6290fd512c3 | Audit            | Built-in |                                                |
| Azure Machine Learning | Workspaces should disable public network access      | 438c38d2-3772-465a-a9cc-7a6666a275ce | Audit            | Built-in |                                                |
| Azure Machine Learning | Computes should have local auth disabled             | e96a9a5f-07ca-471b-9bc5-6a0f33cbd68f | Audit            | Built-in |                                                |
| Azure Machine Learning | Configure Computes to disable local auth             | a6f9a2d0-cff7-4855-83ad-4cd750666512 | Modify           | Built-in | Requires managed identity on policy assignment |
| Azure Machine Learning | Workspaces should use user-assigned managed identity | 5f0c7d88-c7de-45b8-ac49-db49e72eaa78 | Audit            | Built-in |                                                |
| Azure Machine Learning | Resource logs should be enabled                      | afe0c3be-ba3b-4544-ba52-0c99672a8ad6 | AuditIfNotExists | Built-in |                                                |

---

## IoT

| Service           | Policy Description                               | Policy ID                            | Effect           | Category | Notes                                          |
| ----------------- | ------------------------------------------------ | ------------------------------------ | ---------------- | -------- | ---------------------------------------------- |
| Azure IoT Hub     | Should have local auth disabled for Service APIs | 672d56b3-23a7-4a3c-a233-b77ed7777518 | Audit            | Built-in |                                                |
| Azure IoT Hub     | Configure to disable local authentication        | 9f8ba900-a70f-486e-9ffc-faf907305376 | Modify           | Built-in | Requires managed identity on policy assignment |
| Azure IoT Hub     | Resource logs should be enabled                  | 383856f8-de7f-44a2-81fc-e5135b5c2aa4 | AuditIfNotExists | Built-in |                                                |
| Azure IoT Central | Should use private link                          | 9ace2dbc-4b71-48b6-b2a7-428b0b2e3944 | Audit            | Built-in | Limited built-in coverage for IoT Central      |

---

## Developer Tools

| Service                      | Policy Description                              | Policy ID                            | Effect            | Category | Notes                                                   |
| ---------------------------- | ----------------------------------------------- | ------------------------------------ | ----------------- | -------- | ------------------------------------------------------- |
| Azure App Configuration      | Disable local authentication methods            | 72bc14af-4ab8-43af-b4e4-38e7983f9a1f | Modify            | Built-in | Requires managed identity on policy assignment          |
| Azure App Configuration      | Local authentication methods should be disabled | b08ab3ca-1062-4db3-8803-eec9cae605d6 | Audit             | Built-in |                                                         |
| Azure SignalR Service        | Configure to disable local authentication       | 702133e5-5ec5-4f90-9638-c78e22f13b39 | Modify            | Built-in | Requires managed identity on policy assignment          |
| Azure SignalR Service        | Should have local auth methods disabled         | f70eecba-335d-4bbc-81d5-5b17b03d498f | Audit             | Built-in |                                                         |
| Azure SignalR Service        | Should disable public network access            | 21a9766a-82a5-4747-abb5-650b6dbba6d0 | Audit             | Built-in |                                                         |
| Azure Web PubSub             | Configure to disable local authentication       | 17f9d984-90c8-43dd-b7a6-76cb694815c1 | Modify            | Built-in | Requires managed identity on policy assignment          |
| Azure Communication Services | Should use a managed identity                   | bcff6755-335b-484d-b435-d1161db39cdc | Audit             | Built-in |                                                         |
| Azure Notification Hubs      | Enable logging to Log Analytics                 | 69e0da8f-ca50-479d-b1a8-33a31426c512 | DeployIfNotExists | Built-in | Requires managed identity; limited coverage for service |

---

## Data Management

| Service           | Policy Description                                         | Policy ID                            | Effect | Category | Notes                                           |
| ----------------- | ---------------------------------------------------------- | ------------------------------------ | ------ | -------- | ----------------------------------------------- |
| Microsoft Purview | Accounts should use private link                           | 9259053b-ddb8-40ab-842a-0aef19d0ade4 | Audit  | Built-in |                                                 |
| Azure Maps        | Public network access should be disabled                   | a46d869a-f759-4404-8289-7737e7a1f79e | Audit  | Built-in | Limited built-in policy coverage for Azure Maps |
| Azure Maps        | CORS should not allow every resource to access map account | 50553764-7777-43cf-bf12-8647e0b9ba01 | Audit  | Built-in | Limited built-in policy coverage for Azure Maps |

---

## Monitoring

| Service                       | Policy Description                                       | Policy ID                            | Effect | Category | Notes                                          |
| ----------------------------- | -------------------------------------------------------- | ------------------------------------ | ------ | -------- | ---------------------------------------------- |
| Azure Monitor / Log Analytics | Configure Log Analytics to disable public network access | d3ba9c42-9dd5-441a-957c-274031c750c0 | Modify | Built-in | Requires managed identity on policy assignment |
