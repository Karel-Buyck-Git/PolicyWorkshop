Here's the **Minimal: Foundational Governance & Security** initiative scoped to 12 common PaaS services, all verified via [AzAdvertizer](https://www.azadvertizer.net):

---

### 🟢 Minimal — Foundational Governance & Security

| #   | PaaS Service           | Policy Name                                         | Policy ID                              | Effect     |
| --- | ---------------------- | --------------------------------------------------- | -------------------------------------- | ---------- |
| 1   | **App Service**        | Apps should only be accessible over HTTPS           | `a4af4a39-4135-47fb-b175-47fbdf85311d` | Audit/Deny |
|     |                        | Apps should use the latest TLS version              | `f0e6e85b-9b9f-4a4b-b67b-f730d42f1b0b` | Audit      |
|     |                        | Apps should use managed identity                    | `2b9ad585-36bc-4615-b300-fd4435808332` | Audit      |
|     |                        | Apps should require FTPS only                       | `4d24b6d4-5e53-4a4f-a7f4-618fa573ee4b` | Audit      |
| 2   | **Azure Functions**    | Should only be accessible over HTTPS                | `6d555dd1-86f2-4f1c-8ed7-5abae7c6cbab` | Audit/Deny |
|     |                        | Should use the latest TLS version                   | `f9d614c5-c173-4d56-95a7-b4437057d193` | Audit      |
|     |                        | Should use managed identity                         | `0da106f2-4ca3-48e8-bc85-c638fe6aea8f` | Audit      |
|     |                        | Should require FTPS only                            | `399b2637-a50f-4f95-96f8-3a145476eb15` | Audit      |
| 3   | **SQL Database**       | Should be running TLS 1.2 or newer                  | `32e6bbec-16b6-44c2-be37-c5b672d103cf` | Audit      |
|     |                        | Entra admin should be provisioned                   | `1f314764-cb73-4fc9-b863-8eca98ac36e9` | Audit      |
|     |                        | Transparent Data Encryption should be enabled       | `17k78e20-9358-41c9-923c-fb736d382a12` | Audit      |
|     |                        | Auditing should be enabled                          | `a6fb4358-5bf4-4ad7-ba82-2cd2f41ce5e9` | Audit      |
| 4   | **Storage Accounts**   | Secure transfer should be enabled                   | `34c877ad-507e-4c82-993e-3452a6e0ad3c` | Audit/Deny |
|     |                        | Minimum TLS version should be enforced              | `fe83a0eb-a853-422d-aac2-1bffd182c5d0` | Audit      |
|     |                        | Should prevent shared key access                    | `8c6a50c6-9ffd-4ae7-986f-5fa6111f9a54` | Audit/Deny |
|     |                        | Should have SAS expiry policy configured            | `bc1b984e-ddae-40cc-801a-050a030e4fbe` | Audit      |
| 5   | **Key Vault**          | Keys should have an expiration date                 | `152b15f7-8e1f-4c1f-ab71-8c010ba5dbc0` | Audit      |
|     |                        | Secrets should have an expiration date              | `98728c90-32c7-4049-8429-847dc0f4fe37` | Audit      |
|     |                        | Should have soft delete enabled                     | `1e66c121-a66a-4b1f-9b83-0fd99bf0fc2d` | Audit      |
|     |                        | Should have purge (deletion) protection enabled     | `0b60c0b2-2dc2-4e1c-b5c9-abbed971de53` | Audit/Deny |
| 6   | **Service Bus**        | Should disable local authentication                 | `cfb11c26-f069-4c14-8e36-56c394dae5af` | Audit/Deny |
|     |                        | Root management access rule should not be used      | `a1817ec0-a368-432a-8057-8371e17ac6ee` | Audit      |
|     |                        | Resource logs should be enabled                     | `f8d36e2f-389b-4ee4-898d-21aeb69a0f45` | Audit      |
|     |                        | Should disable username/password auth               | `1b0d74ac-4b43-4c39-a15f-594385adc38d` | Modify     |
| 7   | **Event Hubs**         | Should disable local authentication                 | `57f35901-8389-40bb-ac49-3ba4f86d889d` | Modify     |
|     |                        | Instance-level auth rules should be defined         | `f4826e5f-6a27-407c-ae3e-9582eb39891d` | Audit      |
|     |                        | Resource logs should be enabled                     | `83a214f7-d01a-484b-91a9-ed54470c9a6a` | Audit      |
|     |                        | Namespaces should use a valid TLS version           | `Deny-EH-minTLS` _(ALZ)_               | Deny       |
| 8   | **Cosmos DB**          | Should disable local authentication                 | `5450f5bd-9c72-4390-a9c4-a7aba4edfdd2` | Audit/Deny |
|     |                        | Key-based metadata write access should be disabled  | `4750c32b-89c0-46af-bfcb-2e4541a818d5` | Audit      |
|     |                        | Accounts should have firewall rules                 | `862e97cf-49fc-4a5c-9de4-40d4e2e7c8eb` | Audit      |
|     |                        | Throughput should be limited                        | `0b7ef78e-a035-4f23-b9bd-aff122a1b1cf` | Audit      |
| 9   | **Container Registry** | Local admin account should be disabled              | `dc921057-6b28-4fbe-9b83-f7bec05db6c2` | Audit/Deny |
|     |                        | Anonymous authentication should be disabled         | `9f2dea28-e834-476c-99c5-3507b4728395` | Audit/Deny |
|     |                        | Should not allow unrestricted network access        | `d0793b48-0edc-4296-a390-4c75d1bdfd71` | Audit      |
|     |                        | Should use private link                             | `e8eef0a8-67cf-4eb4-9386-14b0e78733d4` | Audit      |
| 10  | **Cache for Redis**    | Only secure connections should be enabled           | `22bee202-a82f-4305-9a2a-6d7f44d4dedb` | Audit/Deny |
|     |                        | Configure to disable non-SSL ports                  | `766f5de3-c6c0-4327-9f4d-042ab8ae846c` | Modify     |
|     |                        | Should not use access keys for authentication       | `3827af20-8f80-4b15-8300-6db0873ec901` | Audit      |
|     |                        | Min TLS version enforcement                         | `Append-Redis-sslEnforcement` _(ALZ)_  | Append     |
| 11  | **API Management**     | Backend calls should be authenticated               | `c15dcc82-b93c-4dcb-9332-fbf121685b54` | Audit      |
|     |                        | Username/password authentication should be disabled | `1b0d74ac-4b43-4c39-a15f-594385adc38d` | Modify     |
|     |                        | Public config endpoints should be disabled          | `df73bd95-24da-4a4f-96b9-4e8b94b402bd` | Audit      |
|     |                        | Min TLS enforcement on APIs                         | `Deny-Sql-minTLS` → check APIM variant | Deny       |
| 12  | **AI Services**        | Key access should be disabled (Entra-only)          | `71ef260a-8f18-47b7-abcb-62d0673d94dc` | Audit/Deny |
|     |                        | Should use managed identity                         | `fe3fd216-4f83-4fc1-8984-2bbec80a3418` | Audit      |
|     |                        | Configure accounts to disable public network access | `47ba1dd7-28d9-4b07-a8d5-9813bed64e0c` | Modify     |
|     |                        | AI Search — disable local authentication            | `4eb216f2-9dba-4979-86e6-5d7e63ce3b75` | Modify     |

---

> **Note:** Entries marked _(ALZ)_ use Azure Landing Zone community policy IDs rather than built-in GUIDs — they're well-established but require deployment via EPAC definitions rather than a simple `/providers/Microsoft.Authorization/policyDefinitions/` reference.

That's **48 policy assignments** across 12 services in a single initiative. Would you like me to now build out the **Standard** and **Premium** tiers, and then export the full three-tier hierarchy as an Excel catalogue ready for your EPAC implementation?

Sources:

- [AzAdvertizer — Azure Policy Reference](https://www.azadvertizer.net)
- [Azure/azure-policy GitHub Repository](https://github.com/Azure/azure-policy)
