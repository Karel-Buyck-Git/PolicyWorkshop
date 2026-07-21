# Azure & Entra prerequisites

What must exist in **Azure** and **Microsoft Entra** before this policy package can deploy. This is
the prerequisites companion to `docs/github/README.md` (which wires up the CI/CD) and the top-level
`README.md` (which lists the secrets and identities by name).

> This guide travels with the package and is written for the **EPAC (json)** flavour — the
> `plan → deploy-policy → deploy-roles` pipeline with three least-privilege identities.

---

## 1. Collect these up front

Gather every value below **before** you touch the pipeline — they seed `global-settings.jsonc` and
the deploy repo's secrets.

| Value | What it is | Where it goes |
| --- | --- | --- |
| **Tenant ID** | your Microsoft Entra tenant (directory) id | `pacEnvironments[].tenantId`; secret `AZURE_TENANT_ID` |
| **Subscription ID** | any subscription in the tenant, for the login context | secret `AZURE_SUBSCRIPTION_ID` |
| **Root management group id** | the intermediate root MG EPAC will own (prod) | `deploymentRootScope` of the `tenant` pacEnvironment |
| **Dev management group id** | a separate MG hierarchy for safe testing | `deploymentRootScope` of the `epac-dev` pacEnvironment |
| **managedIdentityLocation** | an Azure region (e.g. `westeurope`) for remediation identities | `pacEnvironments[].managedIdentityLocation` |
| **pacOwnerId** | the GUID stamping everything this instance owns | already set in this package's `global-settings.jsonc` |
| **Three client IDs** | the CI/CD app registrations (see §4) | secrets `PLAN_CLIENT_ID`, `POLICY_CLIENT_ID`, `ROLES_CLIENT_ID` |

---

## 2. Management groups & scope

EPAC is a **desired-state** engine: it owns its `deploymentRootScope` and **everything beneath it**,
and it **deletes** policy objects in that scope that are not in this repo. Scope it deliberately.

- **Use an intermediate root management group** as the `tenant` scope — **never the Tenant Root
  Group** (avoids tenant-wide lockout and keeps flexibility).
- **Use a separate MG hierarchy for `epac-dev`.** It must **not** be nested inside the `tenant`
  scope, or the two environments will fight over the same policy objects. Mirror your prod structure
  so tests are representative.
- Subscriptions live under management groups; individual assignments in this package may also target
  subscriptions or resource groups. The **management-group diagram in this `docs/` folder** shows the
  hierarchy this package was built for.

To create management groups you (the operator) need **Management Group Contributor** at the parent.

---

## 3. Subscriptions

- You need **at least one subscription** in the tenant. EPAC operates at management-group scope, but
  `azure/login` still needs a subscription context — that is what `AZURE_SUBSCRIPTION_ID` provides.
- **Remediation identities** for `DeployIfNotExists` / `Modify` policies are created by EPAC in the
  **`managedIdentityLocation`** region. Pick a region your tenant allows.
- No policy content is billed to a subscription; **remediation tasks that create or modify resources
  incur that resource's normal cost** (see §6).

---

## 4. Microsoft Entra — identities

CI/CD authenticates with **three app registrations** (service principals), one per pipeline phase,
following least privilege and separation of duties. Prefer **workload identity federation (OIDC)** so
there are **no client secrets** to store or rotate — the federated-credential subjects are covered in
`docs/github/README.md §4`.

| App registration | Purpose |
| --- | --- |
| plan | read-only, builds the what-if plan |
| policy | applies policy definitions / initiatives / assignments |
| roles | applies the RBAC role assignments remediation identities need |

To create app registrations and federated credentials you need permission to register applications in
Entra (the **Application Developer** role, or an Entra admin who does it for you).

---

## 5. Azure RBAC roles

Assign each CI/CD identity the **least-privilege** role at (or above) your `deploymentRootScope`, so
it covers all child scopes:

| Identity | Azure role | Why |
| --- | --- | --- |
| plan | **Reader** | `Build-DeploymentPlans` only reads; it never changes anything |
| policy | **Resource Policy Contributor** | `Deploy-PolicyPlan` creates/updates/deletes policy objects |
| roles | **Role Based Access Control Administrator** | `Deploy-RolesPlan` grants remediation identities their roles |

Notes:

- Keep the **policy** and **roles** identities separate in production so the privileged RBAC identity
  is isolated. In a dev-only setup you may collapse them into one (it still needs both roles).
- If you use **user-assigned** managed identities for remediation, the roles identity also needs
  **Managed Identity Operator** where those identities live.
- **You (the operator)** need **Owner** or **User Access Administrator** at the root MG to create the
  role assignments above, plus **Resource Policy Contributor** for any manual policy work.
- Consider RBAC **conditions** so the roles identity cannot grant `Owner` / `User Access
  Administrator`.

---

## 6. Licensing & cost

- **Azure Policy is free.** Definitions, initiatives, assignments, and compliance evaluation carry no
  license or charge.
- **Microsoft Entra:** app registrations, service principals, and **workload identity federation** are
  available on **all** Entra tiers — **no P1/P2 required**. (Only optional hardening like Conditional
  Access *targeting workload identities* needs the premium Microsoft Entra Workload ID add-on; this
  package does not require it.)
- **Guest / Machine Configuration policies** (in-guest audit, e.g. "audit settings inside a VM"):
  Azure Machine Configuration is **free for Azure VMs**; **Arc-enabled servers may incur a per-server
  charge**. Relevant only if your selected initiatives include guest-configuration policies.
- **Defender for Cloud regulatory compliance:** the policy assignments are free, but viewing framework
  compliance in Defender for Cloud's regulatory-compliance dashboard may require an enabled Defender
  plan.
- **Remediation** (`DeployIfNotExists` / `Modify`) creates or changes real resources — those follow
  **normal Azure resource pricing**.

> Azure and Entra pricing/tiers change — confirm current details in the Azure Pricing docs before you
> rely on a cost assumption.

---

## 7. Verify before you deploy

- [ ] `az login` succeeds against the tenant, and `az account set` works for the subscription
- [ ] the **root** and **epac-dev** management groups exist and you can read them
- [ ] the three app registrations exist, each with a **federated credential** and the role from §5
- [ ] `global-settings.jsonc` `pacEnvironments` match your tenant id, MG ids and region
- [ ] the deploy repo has secrets `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`,
      `PLAN_CLIENT_ID`, `POLICY_CLIENT_ID`, `ROLES_CLIENT_ID`

## References

- Azure Policy overview: <https://learn.microsoft.com/azure/governance/policy/overview>
- Azure built-in roles: <https://learn.microsoft.com/azure/role-based-access-control/built-in-roles>
- EPAC — App registrations & service principals: <https://azure.github.io/enterprise-azure-policy-as-code/ci-cd-app-registrations/>
- Azure Machine Configuration (pricing/coverage): <https://learn.microsoft.com/azure/governance/machine-configuration/overview>
