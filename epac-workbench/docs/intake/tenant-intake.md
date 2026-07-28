# Tenant intake sheet

Fill this in **in one pass** on the tenant. Every command below is **read-only** — nothing
here creates, changes or deletes an Azure resource, so it is safe to run before any change
approval is in place.

Each row names the manifest key the value feeds, so the manifest can be written straight
from the completed sheet with no second visit.

- **Customer / engagement:** `________________`
- **Collected by:** `________________`  **Date:** `________________`
- **Clearance / change reference:** `________________`

```bash
az login --tenant <tenant-domain-or-id>     # device code: add --use-device-code
az account set --subscription <sub-id>
```

---

## 1. Identity and scope

| # | Value | Command | Manifest key | Collected |
|---|---|---|---|---|
| 1.1 | **Tenant ID** | `az account show --query tenantId -o tsv` | `environments[].tenantId` | |
| 1.2 | **Tenant display name** | `az account show --query name -o tsv` | — (context) | |
| 1.3 | **Deployment root scope** — the *intermediate* MG EPAC will own | `az account management-group list -o table` | `environments[].deploymentRootScope` | |
| 1.4 | **Dev root scope** — a **separate** MG hierarchy for `epac-dev` | as above | `environments[].deploymentRootScope` (dev env) | |

> 🛑 **The single most consequential value on this sheet is 1.3.** EPAC is a desired-state
> engine: it owns its `deploymentRootScope` **and everything beneath it**. Point it at the
> **Tenant Root Group** and you have handed it the entire tenant.
>
> Two rules, both from the shipped `docs/azure/README.md` §2:
> - use an **intermediate** management group, never the Tenant Root Group;
> - `epac-dev` must **not** be nested inside the prod scope, or the two environments fight
>   over the same policy objects.
>
> Cross-check against `strategy` before deploying: the package defaults to the safe
> `ownedOnly` (#20), which touches only what it deploys. `full` lets EPAC **delete**
> pre-existing policy in that scope — correct for greenfield, destructive for brownfield.
> If the tenant has ALZ or hand-made policy, it is brownfield. See backlog #39.

**Record the full MG tree** — needed for [`hierarchy-file.md`](hierarchy-file.md):

```bash
# The whole hierarchy, management groups and subscriptions, as JSON:
az account management-group show --name <root-mg-id> --expand --recurse -o json > mg-tree.raw.json

# Quick human-readable check of what you just captured:
az account management-group show --name <root-mg-id> --expand --recurse \
  --query "displayName, children[].{name:displayName, type:type}" -o yaml
```

| # | Value | Command | Where it goes | Collected |
|---|---|---|---|---|
| 1.5 | **MG tree (raw)** | above | → `designs/<customer>-mgmt-groups.json` | |
| 1.6 | **Subscriptions + placement** | `az account list --query "[].{name:name,id:id,state:state}" -o table` | leaf nodes of the hierarchy file | |

---

## 2. Targeting

Which management group each selection is assigned at. **A selection with no target renders
a placeholder scope that Azure rejects** — deliberate, so the decision is forced rather
than defaulted (there is no silent fall-back to the root scope).

| # | Value | Notes | Manifest key | Collected |
|---|---|---|---|---|
| 2.1 | **MG name per selection** | e.g. api-management → the integration landing zone | `selection[].managementGroup` | |
| 2.2 | **Scope overrides** | only if a selection needs a raw scope id instead of an MG name | `selection[].scope` | |
| 2.3 | **notScopes** | MGs/subs to exclude — sandbox and test subscriptions usually belong here | `notScopes` | |

---

## 3. Regions and workspace

| # | Value | Command | Manifest key | Collected |
|---|---|---|---|---|
| 3.1 | **managedIdentityLocation** | `az account list-locations --query "[].name" -o tsv` | `environments[].managedIdentityLocation` | |
| 3.2 | **Allowed locations** | the regions policy will permit | `allowedLocations` | |
| 3.3 | **Log Analytics workspace id** | `az monitor log-analytics workspace list --query "[].{name:name,id:id,location:location}" -o table` | `environments[].logAnalyticsWorkspaceId` | |

> The workspace id must be the **full resource id**
> (`/subscriptions/…/resourceGroups/…/providers/Microsoft.OperationalInsights/workspaces/…`),
> not the workspace name or its GUID. Nothing validates its shape today (#33 open), so a
> wrong value here surfaces only at deploy.

---

## 4. Posture and naming

| # | Value | Options | Manifest key | Collected |
|---|---|---|---|---|
| 4.1 | **pacSelector per environment** | conventionally `epac-dev`, `tenant` | `environments[].selector` | |
| 4.2 | **enforcement** | `Audit` (report only) or `hardened` (baked effects, can Deny) | `environments[].enforcement` | |
| 4.3 | **desiredState strategy** | `ownedOnly` (brownfield, default) / `full` (greenfield) | `environments[].strategy` | |
| 4.4 | **prefix** | customer slug, lowercase, ≤24 chars — prepended to every policy set name | `prefix` | |
| 4.5 | **customerAbbreviation** | the naming anchor, **only if a naming/anchored initiative is selected** | `bindings.defaults` | |

> **Start `Audit` on a live tenant.** `hardened` bakes the restrictive effect, which for
> many policies is `Deny` — and a large share of those are **immutable at resource
> creation**, so in a brownfield tenant they cannot be remediated, only recreated (see
> backlog #47(b)). Audit first, read the compliance report, then harden deliberately.

---

## 5. Identities

Created, not collected — see [`oidc-checklist.md`](oidc-checklist.md). Record the results:

| # | Value | Secret name | Collected |
|---|---|---|---|
| 5.1 | Plan app registration client id | `PLAN_CLIENT_ID` | |
| 5.2 | Policy deploy app registration client id | `POLICY_CLIENT_ID` | |
| 5.3 | Roles deploy app registration client id | `ROLES_CLIENT_ID` | |
| 5.4 | Subscription id for the login context | `AZURE_SUBSCRIPTION_ID` | |

---

## 6. Before you leave the tenant

- [ ] 1.3 and 1.4 are **different** MG hierarchies, and 1.3 is **not** the Tenant Root Group
- [ ] The MG tree JSON captured at 1.5 includes subscriptions (`--recurse` was used)
- [ ] Every selection in the intended manifest has a target from 2.1 or 2.2
- [ ] The workspace id at 3.3 is a full resource id
- [ ] You know whether this tenant is **greenfield or brownfield** — it decides 4.3, and
      getting it wrong proposes deleting the customer's existing policy

---

## 7. Handling what you collected

The values above are **customer tenant identifiers**. Backlog **#28** is open precisely
because this repo's own guidance currently says to commit a filled manifest "for
provenance" — and a filled manifest carries the tenant GUID, the root MG id, the workspace
resource id and the `pacOwnerId`.

**Until #28 is decided, do not commit a completed sheet or a real customer manifest to a
public repo.** Keep them in the customer's own private deploy repo.
