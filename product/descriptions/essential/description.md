# Essential

**_Foundational Governance & Security_**
  This tier serves as the entry-level baseline, establishing a secure, cost-efficient baseline using automated Azure Policy and Management Group hierarchies. It enforces essential governance "guardrails" such as naming convention and mandatory resource tagging to ensure environment consistency and accurate cost tracking. While optimized for low overhead, it applies the same rigorous Role-Based Access Control (RBAC) and identity standards as higher tiers to maintain a unified security posture. Enforcing standardized protocols, embedded resilience, and hardened cryptography across all resources.


* Secure Baseline Enforcement
* CAF Architecture Alignment,
      Standardized Resource Naming,
      Resource Hierarchy
* Identity & Access
* FinOps,
      SKU Governance,
      Quota & Capacity Planning
* Automated Software Delivery, (CI/CD pipeline)
* Resiliency & data protection

# Description

**_Foundational Governance & Security_**
Essential is the foundational governance and security tier. It establishes a consistent landing-zone baseline using Management Groups and Azure Policy initiatives, prioritizing enforceable guardrails with low operational overhead. Controls are typically implemented with Audit, Deny, and Modify effects at management-group scope, with a defined exemption/exception path for legitimate deviations. Identity and RBAC standards align with higher tiers so teams can adopt Essential broadly and upgrade later without rework.

- **_Secure Baseline Enforcement_**: Establishes a minimum security posture across subscriptions by auditing and blocking high-risk configurations (for example, insecure transport, weak encryption defaults, and exposed endpoints where enforceable). Emphasizes secure-by-default settings that are broadly compatible with common workloads.
  - Examples (AzAdvertizer):
    - Secure transfer to storage accounts should be enabled (`34c877ad-507e-4c82-993e-3452a6e0ad3c`)
    - App Service apps should only be accessible over HTTPS (`a4af4a39-4135-47fb-b175-47fbdf85311d`)
    - Storage accounts should have the specified minimum TLS version (`fe83a0eb-a853-422d-aac2-1bffd182c5d0`)
    - Transparent Data Encryption on SQL databases should be enabled (`17k78e20-9358-41c9-923c-fb736d382a12`)
    - Configure Event Hub namespaces to disable local authentication (`57f35901-8389-40bb-ac49-3ba4f86d889d`)
    - Configure to disable non-SSL ports (`766f5de3-c6c0-4327-9f4d-042ab8ae846c`)

- **_CAF Architecture Alignment_**: Standardizes how resources are organized and governed to support consistent operations, delegation, and reporting.
  - Standardized Resource Naming: Enforces naming conventions (deny where feasible; otherwise audit) to improve discoverability, operational handoffs, and automated reporting.
    - Examples (AzAdvertizer):
      - Require a tag and its value on resources (`1e30110a-5ceb-460c-a204-c1c3969c6d62`)
      - Inherit a tag from the resource group (`cd3aa116-8754-49c9-a813-ad46512ece54`)

  - Resource Hierarchy: Applies a consistent Management Group / subscription / resource group hierarchy and placement rules (for example, allowed locations and resource types) to keep governance predictable at scale.
    - Examples (AzAdvertizer):
      - Allowed locations (`e56962a6-4747-49cd-b67b-bf8b01975c4c`)
      - Allowed resource types (`a08ec900-254a-4555-9bf5-e42af04b5c5c`)

- **_Identity & Access_**: Applies baseline identity and access controls aligned to least privilege, including RBAC hygiene and authentication expectations (for example, MFA readiness and avoidance of risky role patterns). Promotes managed identities for supported services to reduce credential sprawl.
  - Examples (AzAdvertizer):
    - Audit usage of custom RBAC roles (`a451c1ef-c6ca-483d-87ed-f49761e3ffb5`)
    - Accounts with owner permissions should be MFA enabled (`e3e008c3-56b9-4133-8fd7-d3347377402a`)
    - Deprecated accounts should be removed from your subscription (`8d7e1fde-fe26-4b5f-8108-f8e432cbc2be`)
    - App Service apps should use managed identity (`2b9ad585-36bc-4615-b300-fd4435808332`)

- **_FinOps_**: Implements guardrails that improve cost transparency and prevent common cost overruns without slowing down delivery.
  - SKU Governance: Restricts service SKUs and tiers to an approved set to keep spend predictable and ensure supportable, production-appropriate choices.
    - Examples (AzAdvertizer):
      - Allowed resource types (`a08ec900-254a-4555-9bf5-e42af04b5c5c`)
      - Azure Databricks — deny non-Premium SKU (ALZ community policy) (`Deny-Databricks-Sku`)

  - Quota & Capacity Planning: Surfaces quota and capacity risks early through governance checks and standard request/exemption processes, reducing deployment friction and last-minute escalations.
    - Examples (AzAdvertizer):
      - Azure Cosmos DB — Throughput should be limited (`0b7ef78e-a035-4f23-b9bd-aff122a1b1cf`)
      - Storage SAS tokens should adhere to 7 day maximum validity (`7aa1c9d5-3d7e-4579-8117-d85e99211757`)

- **_Automated Software Delivery (CI/CD pipeline)_**: Establishes policy-as-code practices using EPAC (Enterprise Policy as Code), where policy definitions, initiatives, and assignments are stored as a Git-tracked desired state. Changes flow through pull requests for review and produce a clear version history; pipelines promote the same artifacts across environments and reconcile assignments to detect and correct drift.

- **_Resiliency & data protection_**: Sets baseline requirements for durability and recovery (for example, backup/retention expectations and protective features like soft delete where applicable), and audits configurations that materially reduce availability or recoverability.
  - Examples (AzAdvertizer):
    - Key Vault should have soft delete enabled (`1e66c121-a66a-4b1f-9b83-0fd99bf0fc2d`)
    - Key Vault should have purge (deletion) protection enabled (`0b60c0b2-2dc2-4e1c-b5c9-abbed971de53`)
    - Key Vault secrets should have an expiration date (`98728c90-32c7-4049-8429-847dc0f4fe37`)
    - Auditing on SQL server should be enabled (`a6fb4358-5bf4-4ad7-ba82-2cd2f41ce5e9`)

