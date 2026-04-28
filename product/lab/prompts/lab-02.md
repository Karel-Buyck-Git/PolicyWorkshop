`I'm creating a hierarchy of policies, using essential, professional and enterprise as initiatives. Here is the essential description`

Description

## Essential

**_Foundational Governance & Security_**
  This tier serves as the entry-level baseline, establishing a secure, cost-efficient baseline using automated Azure Policy and Management Group hierarchies. It enforces essential governance "guardrails" such as naming convention and mandatory resource tagging to ensure environment consistency and accurate cost tracking. While optimized for low overhead, it applies the same rigorous Role-Based Access Control (RBAC) and identity standards as higher tiers to maintain a unified security posture. Enforcing standardized protocols, embedded resilience, and hardened cryptography across all resources.

- Read this file for context, C:\Git\Karel-Buyck-Git Policy Workshop\PolicyWorkshop\product\descriptions\essential\description.md

- Create a new file in folder C:\Git\Karel-Buyck-Git Policy Workshop\PolicyWorkshop\product\lab\prototypes\essential, called "lab-concept-essential-catalogue.md"

- Using the context and azadvertiser.net, create a list of policies as a table, example 

| Service                  | Policy Description                                  | Policy ID                            | Effect     | Category | Notes                     | Tier     |
| ------------------------ | --------------------------------------------------- | ------------------------------------ | ---------- | -------- | ------------------------- | -------- |
| App Service              | Apps should only be accessible over HTTPS           | a4af4a39-4135-47fb-b175-47fbdf85311d | Audit/Deny | Built-in |                           | Essential|
