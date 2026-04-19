Here's the expanded Security Baseline focused on PaaS, all IDs verified via [AzAdvertizer](https://www.azadvertizer.net):

---

**🔒 TLS 1.2 Minimum**

| Policy Name                                                    | Policy ID                              | Service     |
| -------------------------------------------------------------- | -------------------------------------- | ----------- |
| Storage accounts should have the specified minimum TLS version | `fe83a0eb-a853-422d-aac2-1bffd182c5d0` | Storage     |
| Azure SQL Database should be running TLS version 1.2 or newer  | `32e6bbec-16b6-44c2-be37-c5b672d103cf` | SQL         |
| App Service apps should use the latest TLS version             | `f0e6e85b-9b9f-4a4b-b67b-f730d42f1b0b` | App Service |

---

**🔑 Shared Key / SAS Token Hardening**

| Policy Name                                                | Policy ID                              | Effect     |
| ---------------------------------------------------------- | -------------------------------------- | ---------- |
| Storage accounts should prevent shared key access          | `8c6a50c6-9ffd-4ae7-986f-5fa6111f9a54` | Audit/Deny |
| Storage accounts should have SAS policies configured       | `bc1b984e-ddae-40cc-801a-050a030e4fbe` | Audit      |
| Storage SAS tokens should adhere to 7 day maximum validity | `7aa1c9d5-3d7e-4579-8117-d85e99211757` | Audit/Deny |

---

**🪪 Entra Authentication / Disable Local Auth**

| Policy Name                                                     | Policy ID                              | Service     |
| --------------------------------------------------------------- | -------------------------------------- | ----------- |
| An Azure AD administrator should be provisioned for SQL servers | `1f314764-cb73-4fc9-b863-8eca98ac36e9` | SQL         |
| Azure SQL should have Entra-only authentication enabled         | `abda6d70-9778-44e7-84a8-06713e6db027` | SQL DB      |
| Azure SQL Managed Instance — Entra-only authentication          | `78215662-041e-49ed-a9dd-5385911b3a1f` | SQL MI      |
| Cosmos DB accounts should have local authentication disabled    | `5450f5bd-9c72-4390-a9c4-a7aba4edfdd2` | Cosmos DB   |
| Service Bus namespaces — local auth disabled                    | `cfb11c26-f069-4c14-8e36-56c394dae5af` | Service Bus |
| Configure Event Hub namespaces to disable local authentication  | `57f35901-8389-40bb-ac49-3ba4f86d889d` | Event Hub   |

---

**🤖 Managed Identity**

| Policy Name                                  | Policy ID                              | Service     |
| -------------------------------------------- | -------------------------------------- | ----------- |
| App Service apps should use managed identity | `2b9ad585-36bc-4615-b300-fd4435808332` | App Service |
| Function apps should use managed identity    | `0da106f2-4ca3-48e8-bc85-c638fe6aea8f` | Functions   |

---

**📡 FTPS / Secure FTP**

| Policy Name                               | Policy ID                              | Service     |
| ----------------------------------------- | -------------------------------------- | ----------- |
| App Service apps should require FTPS only | `4d24b6d4-5e53-4a4f-a7f4-618fa573ee4b` | App Service |
| Function apps should require FTPS only    | `399b2637-a50f-4f95-96f8-3a145476eb15` | Functions   |

---

All of these are **Audit or Deny effect only** — no `deployIfNotExists`, so zero cost impact. A few things worth noting:

- The **Entra-only** SQL policies apply at creation time, so they work best combined with an Audit policy for existing servers
- **Shared key access disabled** on storage is powerful but can break legacy workloads — worth running in Audit mode first
- The **local auth disabled** policies for Service Bus, Event Hub, and Cosmos DB are great paired with managed identity policies above

Would you like me to export this full catalogue (both previous and new sections) into an Excel spreadsheet you can work from?

Sources:

- [AzAdvertizer — Azure Policy Reference](https://www.azadvertizer.net)
- [Azure/azure-policy GitHub Repository](https://github.com/Azure/azure-policy)
