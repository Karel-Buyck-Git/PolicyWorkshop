# Essential — Policy Catalogue (Lab Concept)

This catalogue supports the **Essential** initiative by listing a baseline set of **Azure Built-in** Azure Policy definitions (GUID policy IDs) aligned to the Essential description.

All policy IDs in the table are intended to be looked up and validated on AzAdvertizer using:
`https://www.azadvertizer.net/azpolicyadvertizer/<policyId>.html`

**Sources**
- AzAdvertizer policy reference: https://www.azadvertizer.net/

> Notes
> - This catalogue intentionally excludes ALZ/community/custom policies with non-GUID IDs (for example, `Deny-*`, `Append-*`) to satisfy “no local policy IDs”.
> - Some **Modify** policies require a managed identity on the policy assignment.

| Service | Policy Description | Policy ID | Effect | Category | Notes | Tier |
| --- | --- | --- | --- | --- | --- | --- |
| AI Services | Key access should be disabled (Entra-only) | 71ef260a-8f18-47b7-abcb-62d0673d94dc | Audit/Deny | Built-in |  | Essential |
| AI Services | Should use managed identity | fe3fd216-4f83-4fc1-8984-2bbec80a3418 | Audit | Built-in |  | Essential |
| AI Services | Configure accounts to disable public network access | 47ba1dd7-28d9-4b07-a8d5-9813bed64e0c | Modify | Built-in | Requires managed identity on assignment | Essential |
| AI Services | AI Search — disable local authentication | 4eb216f2-9dba-4979-86e6-5d7e63ce3b75 | Modify | Built-in | Requires managed identity on assignment | Essential |
| API Management | Backend calls should be authenticated | c15dcc82-b93c-4dcb-9332-fbf121685b54 | Audit | Built-in |  | Essential |
| API Management | Username/password authentication should be disabled | 1b0d74ac-4b43-4c39-a15f-594385adc38d | Modify | Built-in | Requires managed identity on assignment | Essential |
| API Management | Public config endpoints should be disabled | df73bd95-24da-4a4f-96b9-4e8b94b402bd | Audit | Built-in |  | Essential |
| App Service | Apps should only be accessible over HTTPS | a4af4a39-4135-47fb-b175-47fbdf85311d | Audit/Deny | Built-in |  | Essential |
| App Service | Apps should require FTPS only | 4d24b6d4-5e53-4a4f-a7f4-618fa573ee4b | Audit | Built-in |  | Essential |
| App Service | Apps should use managed identity | 2b9ad585-36bc-4615-b300-fd4435808332 | Audit | Built-in |  | Essential |
| App Service | Apps should use the latest TLS version | f0e6e85b-9b9f-4a4b-b67b-f730d42f1b0b | Audit | Built-in |  | Essential |
| Azure Functions | Should only be accessible over HTTPS | 6d555dd1-86f2-4f1c-8ed7-5abae7c6cbab | Audit/Deny | Built-in |  | Essential |
| Azure Functions | Should require FTPS only | 399b2637-a50f-4f95-96f8-3a145476eb15 | Audit | Built-in |  | Essential |
| Azure Functions | Should use managed identity | 0da106f2-4ca3-48e8-bc85-c638fe6aea8f | Audit | Built-in |  | Essential |
| Azure Functions | Should use the latest TLS version | f9d614c5-c173-4d56-95a7-b4437057d193 | Audit | Built-in |  | Essential |
| Cache for Redis | Configure to disable non-SSL ports | 766f5de3-c6c0-4327-9f4d-042ab8ae846c | Modify | Built-in | Requires managed identity on assignment | Essential |
| Cache for Redis | Only secure connections should be enabled | 22bee202-a82f-4305-9a2a-6d7f44d4dedb | Audit/Deny | Built-in |  | Essential |
| Cache for Redis | Should not use access keys for authentication | 3827af20-8f80-4b15-8300-6db0873ec901 | Audit | Built-in |  | Essential |
| Compute | Audit VMs that do not use managed disks | 06a78e20-9358-41c9-923c-fb736d382a4d | Audit | Built-in |  | Essential |
| Container Registry | Anonymous authentication should be disabled | 9f2dea28-e834-476c-99c5-3507b4728395 | Audit/Deny | Built-in |  | Essential |
| Container Registry | Local admin account should be disabled | dc921057-6b28-4fbe-9b83-f7bec05db6c2 | Audit/Deny | Built-in |  | Essential |
| Container Registry | Should not allow unrestricted network access | d0793b48-0edc-4296-a390-4c75d1bdfd71 | Audit | Built-in |  | Essential |
| Container Registry | Should use private link | e8eef0a8-67cf-4eb4-9386-14b0e78733d4 | Audit | Built-in |  | Essential |
| Cosmos DB | Accounts should have firewall rules | 862e97cf-49fc-4a5c-9de4-40d4e2e7c8eb | Audit | Built-in |  | Essential |
| Cosmos DB | Key-based metadata write access should be disabled | 4750c32b-89c0-46af-bfcb-2e4541a818d5 | Audit | Built-in |  | Essential |
| Cosmos DB | Should disable local authentication | 5450f5bd-9c72-4390-a9c4-a7aba4edfdd2 | Audit/Deny | Built-in |  | Essential |
| Cosmos DB | Throughput should be limited | 0b7ef78e-a035-4f23-b9bd-aff122a1b1cf | Audit | Built-in | Requires max throughput parameter | Essential |
| Event Hubs | Instance-level auth rules should be defined | f4826e5f-6a27-407c-ae3e-9582eb39891d | Audit | Built-in |  | Essential |
| Event Hubs | Resource logs should be enabled | 83a214f7-d01a-484b-91a9-ed54470c9a6a | Audit | Built-in |  | Essential |
| Event Hubs | Should disable local authentication | 57f35901-8389-40bb-ac49-3ba4f86d889d | Modify | Built-in | Requires managed identity on assignment | Essential |
| Identity & Access | Accounts with owner permissions should be MFA enabled | e3e008c3-56b9-4133-8fd7-d3347377402a | Audit | Built-in |  | Essential |
| Identity & Access | Audit usage of custom RBAC roles | a451c1ef-c6ca-483d-87ed-f49761e3ffb5 | Audit | Built-in |  | Essential |
| Identity & Access | Deprecated accounts should be removed from your subscription | 8d7e1fde-fe26-4b5f-8108-f8e432cbc2be | Audit | Built-in |  | Essential |
| Key Vault | Keys should have an expiration date | 152b15f7-8e1f-4c1f-ab71-8c010ba5dbc0 | Audit | Built-in |  | Essential |
| Key Vault | Secrets should have an expiration date | 98728c90-32c7-4049-8429-847dc0f4fe37 | Audit | Built-in |  | Essential |
| Key Vault | Should have purge (deletion) protection enabled | 0b60c0b2-2dc2-4e1c-b5c9-abbed971de53 | Audit/Deny | Built-in |  | Essential |
| Key Vault | Should have soft delete enabled | 1e66c121-a66a-4b1f-9b83-0fd99bf0fc2d | Audit | Built-in |  | Essential |
| Networking | Network interfaces should not have public IPs | 83a86a26-fd1f-447c-b59d-e51f44264114 | Deny | Built-in |  | Essential |
| Networking | Subnets should be associated with a Network Security Group | e71308d3-144b-4262-b144-efdc3cc90517 | Audit | Built-in |  | Essential |
| Resource Governance | Allowed locations | e56962a6-4747-49cd-b67b-bf8b01975c4c | Deny | Built-in |  | Essential |
| Resource Governance | Allowed resource types | a08ec900-254a-4555-9bf5-e42af04b5c5c | Deny | Built-in |  | Essential |
| Resource Governance | Inherit a tag from the resource group | cd3aa116-8754-49c9-a813-ad46512ece54 | Modify | Built-in | Requires managed identity on assignment | Essential |
| Resource Governance | Require a tag and its value on resources | 1e30110a-5ceb-460c-a204-c1c3969c6d62 | Deny | Built-in |  | Essential |
| SQL Database | Auditing should be enabled | a6fb4358-5bf4-4ad7-ba82-2cd2f41ce5e9 | Audit | Built-in |  | Essential |
| SQL Database | Entra admin should be provisioned | 1f314764-cb73-4fc9-b863-8eca98ac36e9 | Audit | Built-in |  | Essential |
| SQL Database | Should be running TLS 1.2 or newer | 32e6bbec-16b6-44c2-be37-c5b672d103cf | Audit | Built-in |  | Essential |
| SQL Database | Transparent Data Encryption should be enabled | 17k78e20-9358-41c9-923c-fb736d382a12 | Audit | Built-in |  | Essential |
| Service Bus | Resource logs should be enabled | f8d36e2f-389b-4ee4-898d-21aeb69a0f45 | Audit | Built-in |  | Essential |
| Service Bus | Root management access rule should not be used | a1817ec0-a368-432a-8057-8371e17ac6ee | Audit | Built-in |  | Essential |
| Service Bus | Should disable local authentication | cfb11c26-f069-4c14-8e36-56c394dae5af | Audit/Deny | Built-in |  | Essential |
| Service Bus | Should disable username/password auth | 1b0d74ac-4b43-4c39-a15f-594385adc38d | Modify | Built-in | Requires managed identity on assignment | Essential |
| Storage Accounts | Minimum TLS version should be enforced | fe83a0eb-a853-422d-aac2-1bffd182c5d0 | Audit | Built-in | Default param often TLS1_2 | Essential |
| Storage Accounts | Secure transfer should be enabled | 34c877ad-507e-4c82-993e-3452a6e0ad3c | Audit/Deny | Built-in |  | Essential |
| Storage Accounts | Should have SAS expiry policy configured | bc1b984e-ddae-40cc-801a-050a030e4fbe | Audit | Built-in |  | Essential |
| Storage Accounts | Storage SAS tokens should adhere to 7 day maximum validity | 7aa1c9d5-3d7e-4579-8117-d85e99211757 | Audit/Deny | Built-in |  | Essential |
| Storage Accounts | Should prevent shared key access | 8c6a50c6-9ffd-4ae7-986f-5fa6111f9a54 | Audit/Deny | Built-in | Consider starting in Audit to avoid breaking legacy workloads | Essential |
