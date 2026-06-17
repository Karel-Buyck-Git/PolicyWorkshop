# Enterprise

**_Enterprise: Azure Advanced Enterprise Isolation_**
  The highest tier provides a comprehensive, "Zero Trust" architecture designed for sensitive data and critical business applications. It moves beyond standard security by implementing full Private Link integration to eliminate public internet exposure. Introducing Conditional access and Privileged Identity Management. This level incorporates granular micro-segmentation, continuous verification, and advanced traffic inspection to meet the most demanding compliance and isolation requirements.

* Secure Governance
* Zero trust
* Data Sovereignty
* Workload lifecycle management
* High availability (99,99% SLA)
* Regulatory framework alignment (NIS2, ISO 27001, CIS)
* Everything in Professional

# Description

**_Enterprise: Azure Advanced Enterprise Isolation_**
Enterprise is the highest tier and is built around Zero Trust principles for sensitive data and business-critical workloads. It eliminates public network exposure through mandatory Private Link integration, enforces continuous verification of identities and devices, and applies granular micro-segmentation across the network and data planes. Controls are implemented as policy-as-code with Deny and DeployIfNotExists effects at management-group scope, paired with strict exemption governance, so that regulatory and isolation requirements are demonstrably and continuously enforced.

- **_Secure Governance_**: Establishes the most stringent governance posture by combining management-group-scoped Azure Policy initiatives with strict exemption workflows, signed policy-as-code releases, and continuous compliance attestation. Guardrails are predominantly Deny/DeployIfNotExists to remove drift, and changes to the policy estate themselves are tightly controlled and auditable.
  - Examples (AzAdvertizer):
    - Audit usage of custom RBAC roles (`a451c1ef-c6ca-483d-87ed-f49761e3ffb5`)
    - Azure subscriptions should have a log profile for Activity Log (`7796937f-307b-4598-941c-67d3a05ebfe7`)
    - Management ports of virtual machines should be protected with just-in-time network access control (`b0f33259-77d7-4c9e-aac6-3aabcfae693c`)
    - Allowed locations for resource groups (`e765b5de-1225-4ba3-bd56-1ac6695af988`)

- **_Zero Trust_**: Enforces "never trust, always verify" across identity, network, and workload boundaries. Public endpoints are eliminated in favor of Private Link and private DNS; conditional access and Privileged Identity Management (PIM) govern administrative paths; and east-west traffic is inspected and segmented at the workload level.
  - Private Link & private endpoints: Mandates private connectivity for data and management planes, disabling public network access on supported services.
    - Examples (AzAdvertizer):
      - Storage accounts should disable public network access (`b2982f36-99f2-4db5-8eff-283140c09693`)
      - Azure Key Vault should disable public network access (`405c5871-3e91-4644-8a63-58e19d68ff5b`)
      - Azure Cosmos DB should disable public network access (`797b37f7-06b8-444c-b1ad-fc62d82a8acf`)
      - Azure SQL Database should have public network access disabled (`1b8ca024-1d5c-4dec-8995-b1a932b41780`)
      - Azure AI Services — configure accounts to disable public network access (`47ba1dd7-28d9-4b07-a8d5-9813bed64e0c`)
      - Configure private DNS zones for private endpoints (`a1817ec0-a368-432a-8057-8371e17ac6ee`)

  - Conditional access & PIM: Enforces step-up authentication, risk-based access, and just-in-time elevation for privileged Azure roles, aligned with tenant identity governance.
    - Examples (AzAdvertizer, related guardrails on the Azure resource plane):
      - Accounts with owner permissions should be MFA enabled (`e3e008c3-56b9-4133-8fd7-d3347377402a`)
      - Accounts with write permissions should be MFA enabled (`931e118d-50a1-4457-a5e4-78550e086c52`)
      - Deprecated accounts with owner permissions should be removed from your subscription (`ebb62a0c-3560-49e1-89ed-27e074e9f8ad`)
      - Management ports of virtual machines should be protected with just-in-time network access control (`b0f33259-77d7-4c9e-aac6-3aabcfae693c`)

  - Micro-segmentation & traffic inspection: Applies fine-grained network segmentation, forced tunneling through inspection appliances (Azure Firewall / NVA), and DDoS protection on perimeter networks.
    - Examples (AzAdvertizer):
      - All Internet traffic should be routed via your deployed Azure Firewall (`fc5e4038-4584-4632-8c85-c0448d374b2c`)
      - Subnets should be associated with a Network Security Group (`e71308d3-144b-4262-b144-efdc3cc90517`)
      - Virtual networks should be protected by Azure DDoS Protection Standard (`a7aca53f-2ed4-4466-a25e-0b45ade68efd`)
      - Network interfaces should not have public IPs (`83a86a26-fd1f-447c-b59d-e51f44264114`)

- **_Data Sovereignty_**: Guarantees that data residency, encryption, and key custody requirements are continuously enforced. Restricts deployments to approved sovereign regions, mandates customer-managed keys (CMK) for data-at-rest, and ensures key material is held in dedicated HSM-backed Key Vaults.
  - Examples (AzAdvertizer):
    - Allowed locations (`e56962a6-4747-49cd-b67b-bf8b01975c4c`)
    - Allowed locations for resource groups (`e765b5de-1225-4ba3-bd56-1ac6695af988`)
    - Storage accounts should use customer-managed key for encryption (`6fac406b-40ca-413b-bf8e-0bf964659c25`)
    - Azure Cosmos DB accounts should use customer-managed keys to encrypt data at rest (`1f905d99-2ab7-462c-a6b0-f709acca6c8f`)
    - Azure Machine Learning workspaces should be encrypted with a customer-managed key (`ba769a63-b8cc-4b2d-abf6-ac33c7204be8`)
    - Key vaults should have deletion protection enabled (`0b60c0b2-2dc2-4e1c-b5c9-abbed971de53`)
    - Azure Key Vault Managed HSM should have purge protection enabled (`c39ba22d-4428-4149-b981-70acb31fc383`)

- **_Workload lifecycle management_**: Governs the full lifecycle of regulated workloads from landing-zone provisioning through decommissioning, using policy-as-code, signed artifacts, and controlled promotion across environments. Drift is continuously detected and remediated, and decommissioning is policy-enforced so that residual resources, identities, and data stores cannot persist outside their approved lifecycle.
  - Examples (AzAdvertizer):
    - Deploy — Configure diagnostic settings for Azure Key Vault to Log Analytics workspace (`951af2fa-529b-416e-ab6e-066fd85ac459`)
    - Configure backup on virtual machines with a given tag to an existing recovery services vault in the same location (`345fa903-145c-4fe1-8bcd-93ec2adccde8`)
    - Resource groups should have a tag and its value (`96670d01-0a4d-4649-9c89-2d3abc0a5025`)
    - Inherit a tag from the resource group (`cd3aa116-8754-49c9-a813-ad46512ece54`)

- **_High availability (99.99% SLA)_**: Enforces availability targets aligned to a 99.99% SLA by mandating zone-redundant or multi-region topologies, geo-redundant storage, and platform-managed failover for supported services. Non-HA SKUs and single-zone deployments are blocked for in-scope workloads.
  - Examples (AzAdvertizer):
    - Storage accounts should be zone redundant (`23a8f9ec-8e0e-4205-8c70-d56b6c95dab2`)
    - Azure SQL Database should have zone-redundant configuration (`70f2cee4-7d7e-4f50-9135-87a87b6ec7e6`)
    - Cosmos DB account should have multiple write regions (`44c5a1f9-7ec3-4f17-9bf6-c1ff4e96aa05`)
    - Azure Backup should be enabled for Virtual Machines (`013e242c-8828-4970-87b3-ab247555486d`)
    - Geo-redundant backup should be enabled for Azure Database for PostgreSQL (`48af4db5-9b8b-401c-8e74-076be876a430`)

- **_Regulatory framework alignment (NIS2, ISO 27001, CIS)_**: Maps controls to NIS2, ISO/IEC 27001, and CIS benchmarks using built-in regulatory compliance initiatives, supplemented by tier-specific custom policies. Compliance state is continuously reported and exported for internal and external assurance, with evidence traceable back to specific policy assignments.
  - Examples (AzAdvertizer — built-in regulatory initiatives):
    - ISO 27001:2013 initiative (`89c6cddc-1c73-4ac1-b19c-54d1a15a42f2`)
    - CIS Microsoft Azure Foundations Benchmark v2.0.0 (`06f19060-9e68-4070-92ca-f15cc126059e`)
    - NIST SP 800-53 Rev. 5 (`179d1daa-458f-4e47-8086-2a68d0d6c38f`)
    - Microsoft cloud security benchmark (`1f3afdf9-d0c9-4c3d-847f-89da613e70a8`)

- **_Everything in Professional_**: Includes all Essential and Professional guardrails; Enterprise adds Zero Trust enforcement, sovereign data controls, regulated-workload lifecycle governance, and the highest availability requirements.
  - Examples (AzAdvertizer):
    - Storage accounts should disable public network access (`b2982f36-99f2-4db5-8eff-283140c09693`)
    - All Internet traffic should be routed via your deployed Azure Firewall (`fc5e4038-4584-4632-8c85-c0448d374b2c`)
    - Storage accounts should use customer-managed key for encryption (`6fac406b-40ca-413b-bf8e-0bf964659c25`)
    - Virtual networks should be protected by Azure DDoS Protection Standard (`a7aca53f-2ed4-4466-a25e-0b45ade68efd`)
    - Azure Key Vault Managed HSM should have purge protection enabled (`c39ba22d-4428-4149-b981-70acb31fc383`)
