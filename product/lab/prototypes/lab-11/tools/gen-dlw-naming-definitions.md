# `gen-dlw-naming-definitions` — DLW naming-convention policy generator

This tool generates the **Azure Policy definitions** that audit/deny Azure resources
whose names don't follow the DLW landing-zone naming convention. It is the policy-side
mirror of the deployment-side Bicep function [`getResourceName.bicep`](../catalogue/definitions/custom/dlw-az-naming/) —
the Bicep *builds* compliant names; these policies *enforce* them.

- **Script:** `gen-dlw-naming-definitions.py`
- **Outputs:**
  - `catalogue/definitions/custom/dlw-az-naming/naming-*.json` — one EPAC
    policyDefinition per Azure resource type (existing `naming-*.json` are overwritten;
    `sampleNaming.bicep` and `getResourceName.bicep` are left untouched).
  - `catalogue/initiatives/management/essential/naming/company-management-essential-naming.*`
    — a `naming` **initiative** that bundles every definition above, using the same
    artifact set and JSON shapes the built-in producer (`flows/create_initiatives.py`)
    emits per group.

## The naming convention

The source of truth is `getResourceName.bicep` (v1.5). Its main pattern is:

```
{customerAbbreviation}-{resourceTypeAbbreviation}-{service}-{environmentName}-{locationAbbreviation}-[{role}]-{instanceNumber}
```

| Segment | Meaning | Example |
|---|---|---|
| `customerAbbreviation` | Org/customer prefix | `dlw` |
| `resourceTypeAbbreviation` | Per-type abbreviation (`vnet`, `kv`, `st`, …) | `vnet` |
| `service` | Workload/service (resource-group scope) | `shared` |
| `environmentName` | Environment | `dev`, `tst`, `prd` |
| `locationAbbreviation` | Region | `we`, `ne` |
| `role` *(optional)* | Role/purpose (VM, NSG, route table) | `app` |
| `instanceNumber` | Instance counter | `001` |

Example default name: **`dlw-vnet-shared-prd-we-001`**.

### Special cases (taken verbatim from the Bicep function)

Some resource types deviate, mostly to satisfy Azure name rules:

| Resource type(s) | Form | Example |
|---|---|---|
| Storage account, Container registry, Fabric capacity | **compact, no hyphens** `{cust}{abbr}{service}{env}{loc}{instance}` | `dlwstsharedprdwe001` |
| Virtual machine | **compact** `{service}{env}{loc}{role}{instance}` (no customer/abbr) | `sharedprdweapp001` |
| OS disk / data disk / NIC | `{virtualMachineName}-{abbr}-{instance}` | `sharedprdweapp001-osdisk-001` |
| Snapshot | `{diskName}-snap-{instance}` | `…-osdisk-001-snap-001` |
| Subnet | `{subnetFunction}Subnet` | `appSubnet` |
| VNet peering | `peer-{source}-with-{dest}` | `peer-hub-with-spoke` |
| Private endpoint | `{attachedResource}-pep-{loc}-{subResource}-{instance}` | `dlw-kv-…-pep-we-vault-001` |
| NSG / Route table | default form **plus** a `subnetFunction` / `purpose` segment | `dlw-nsg-shared-prd-we-app-001` |

## How the policies validate names (and why they're "anchor" checks)

Azure Policy can't do general regular expressions. The two relevant operators are:

- **`like`** — wildcard match, but **only one `*`** is allowed.
- **`match` / `matchInsensitively`** — `#` = digit, `?` = letter, `.` = any char, but
  **fixed width** (no "one-or-more").

A 6–7 segment convention with free-text segments (`service`, `role`, …) therefore can't
be matched end-to-end. Instead each policy validates the **deterministic anchor** of the
name and flags anything that doesn't match. Per template kind:

| `checkKind` | Condition that makes a resource **non-compliant** |
|---|---|
| `default` | name is **not** `like` `{customerAbbreviation}-{abbr}-*` |
| `compact` | name is **not** `like` `{customerAbbreviation}{abbr}*` |
| `peering` | name is **not** `like` `peer-*` |
| `subnet` | name is **not** `like` `*Subnet` |
| `parentToken` | name does **not** `contains` the `-{abbr}-` token (e.g. `-osdisk-`, `-disk-`, `-nic-`) |
| `privateEndpoint` | name does **not** `contains` `-pep-` |
| `vmCompact` | name `contains` `-` (VM names must be compact) |

This validates the customer prefix + correct resource-type abbreviation in the right
position — the highest-value, false-positive-free part of the convention. The segments
*after* the anchor (service/env/location/instance) are **not** enforced, by design,
because the operators can't express them precisely. `match`-style fixed-width masks were
considered and rejected (they'd reject any valid name whose segment lengths differ).

Every definition also carries:
- a `customerAbbreviation` parameter (default `dlw`) used to build the anchor,
- an `excludedNamePattern` array parameter (platform-managed carve-outs; resource groups
  ship with `AzureBackupRG_*`, `NetworkWatcherRG`, etc.),
- an `effect` parameter (`Audit` / `Deny` / `Disabled`, default `Audit`).

## Where the data comes from

1. **Base list (`ROWS`)** — the full [CAF resource-abbreviations](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-abbreviations)
   table: resource → ARM provider type → abbreviation, used to enumerate every
   policeable Azure resource type and its category.
2. **Customer overrides (`MODULE`)** — the ~70 types defined in `getResourceName.bicep`.
   For these, the script **replaces** the CAF abbreviation with the customer's
   abbreviation and applies the correct special-case `checkKind`. The Bicep module is
   the source of truth; the CAF page only fills the long tail of types the module
   doesn't mention (those get the `default` anchor with their CAF abbreviation).

Where several abbreviations map to one ARM type, the anchor accepts all of them
(e.g. `Microsoft.Web/sites` → `dlw-func-*` **or** `dlw-app-*`).

## The `naming` initiative

After writing the definitions, the script bundles them into a single initiative under
`catalogue/initiatives/management/essential/naming/`, mirroring the artifact set the
built-in producer emits per `(domain, tier, category)` group:

| Artifact | Notes |
|---|---|
| `company-management-essential-naming.policyset.json` | `policySetDefinition`; one member per `naming-*` definition, referenced by **`policyDefinitionName`** (custom, in-repo) with `groupNames: ["Essential"]`. |
| `company-management-essential-naming.assignment.json` | `policyAssignment` scaffold with `<root-mg-id>` / `<pac-environment-selector>` mocks. |
| `company-management-essential-naming.exemptions.json` | One `Waiver` exemption stub. |
| `company-management-essential-naming.md` | Tier rationale + Usage guide + the full member table. |

No `.roles.json` is written — naming policies are Audit/Deny only (no
Modify/DeployIfNotExists), exactly as the producer omits it for non-remediating groups.

**Effect handling:** unlike the built-in flow (which *bakes* a hardened effect literal
per member), this initiative **bubbles a single top-level `effect` parameter**
(default `Audit`) and wires every member's `effect` to it — so the whole set is tuned
from one value at assignment. Each member's other parameters (`customerAbbreviation`,
`excludedNamePattern`) are emitted inline with their definition defaults.

Placement constants live at the top of the script (`PREFIX`, `INIT_DOMAIN`, `INIT_TIER`,
`INIT_CATEGORY`, `INIT_NAME`, `INIT_DIR`). The `catalogueVersion` stamped into the
policyset is read from `catalogue/catalogue.json` when present, else today's UTC date.

> Note: the script does **not** update the catalogue manifests
> (`catalogue/index.json` / `catalogue/catalogue.json`) — those are owned by
> `flows/create_initiatives.py`, which would overwrite them on its next run.

## What it does when you run it

```bash
python tools/gen-dlw-naming-definitions.py
```

1. Builds the type → {abbreviations, category} map from `ROWS`, normalising provider
   casing and collapsing duplicate types.
2. Deletes the existing `naming-*.json` files in `dlw-az-naming/` (full regenerate).
3. For each ARM type, resolves abbreviations + `checkKind` (MODULE override else CAF
   default) and writes one EPAC `policyDefinition` JSON with the anchor rule above.
4. Bundles all definitions into the `naming` initiative artifacts described above.
5. Prints a summary: total types, files written, module-aligned vs CAF-default,
   a breakdown by `checkKind`, and the initiative name / member count / version.

## Updating the convention

- **Change an abbreviation or a special case** → edit the `MODULE` map (keep it in sync
  with `getResourceName.bicep`) and re-run.
- **Add a brand-new resource type the module starts emitting** → add it to `MODULE`
  (and to `ROWS` if it isn't on the CAF page), then re-run.
- **Change the customer prefix** → it's a per-definition parameter; override
  `customerAbbreviation` at assignment time, or change `CUST_DEFAULT` and re-run.

## Deploying

The definitions and the `naming` initiative are deployed together via EPAC (the
initiative references the definitions by `policyDefinitionName`, so both must be present
in the EPAC `Definitions/` tree). Assign the initiative at a management-group scope; set
the `effect` parameter to `Deny` when you're ready to enforce rather than audit.
