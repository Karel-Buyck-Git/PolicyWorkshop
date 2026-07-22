# `gen-dlw-naming-definitions` DLW naming-convention policy generator

> A generator in [`definition_gen/`](README.md). Script: `gen_dlw_naming_definitions.py` ·
> output family: `dlw-az-naming`. This is the full manual; the package
> [README](README.md) explains how generators fit together.

This tool generates the **Azure Policy definitions** that audit/deny Azure resources
whose names don't follow the DLW landing-zone naming convention. It is the policy-side
mirror of the deployment-side Bicep function [`getResourceName.bicep`](https://github.com/DLW-INT-MSPE-Bicep-Framework/bicep-framework/blob/main/0-shared/function/getResourceName/getResourceName.bicep) v1.5 by MSPE. Their Bicep module _builds_ compliant names; these policies _enforce_ them.

- **Script:** `gen_dlw_naming_definitions.py`
- **Outputs:**
  - `catalogue/definitions/custom/dlw-az-naming/naming-*.json` one EPAC
    policyDefinition per Azure resource type (existing `naming-*.json` are overwritten;
  - `catalogue/initiatives/management/essential/naming/management-esn-naming.*`
    a `naming` **initiative** that bundles every definition above, using the same
    artifact set, JSON shapes and brand-neutral within-limit asset naming
    (`engine/shared/naming.py`) the built-in producer (`engine/catalogue_builder/create_initiatives.py`)
    emits per group. (The *policy rule* / naming convention the policies enforce is unchanged.)

## Product, purpose & deployment

**Product.** `gen-dlw-naming-definitions` is DLW's authoring tool for **Azure naming
governance as code**. It turns the deployment-time naming convention (the dlw MSPE
`getResourceName.bicep` module) into _enforceable_ Azure Policy: a complete set of custom
policy **definitions** (one per resource type) plus a single **`naming` initiative** that
bundles them. One command keeps the policy side in lock-step with the convention.

**Purpose.** Where `getResourceName.bicep` _builds_ compliant names at deploy time, these
policies _verify_ them at the platform so resources that are created outside the module
(portal, scripts, other IaC) are still caught.

> ⚠️ **Everything ships as `Audit`. Enforcement is a per-customer decision made at the
> customer.**
> Every generated definition **and** the initiative's top-level `effect` parameter default
> to **`Audit`** non-compliant names are reported, nothing is blocked. This is
> deliberate: the artifacts in this repo are safe to deploy as-is. When the policies are
> rolled out to a customer tenant and you want to _enforce_ the convention, change the
> effect to **`Deny`** (or `Disabled` to switch a control off) **at assignment time in the
> customer environment** override the initiative's `effect` parameter on the EPAC
> assignment. **Do not** bake `Deny` into the generated artifacts here; the repo stays
> Audit-by-default.

**Parameter values** (all have safe defaults; override per assignment / per customer):

| Parameter              | Where                                         | Allowed values              | Default     | Notes                                                                                                                                                      |
| ---------------------- | --------------------------------------------- | --------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `effect`               | initiative (one top-level) + every definition | `Audit`, `Deny`, `Disabled` | **`Audit`** | The initiative wires every member's `effect` to its single top-level `effect`, so one value tunes the whole set. Set to `Deny` at the customer to enforce. |
| `customerAbbreviation` | definitions (`default`/`compact` kinds)       | string                      | `dlw`       | Org prefix that anchors the name check.                                                                                                                    |
| `excludedNamePattern`  | every definition                              | array (wildcards)           | `[]`        | Carve-outs; resource groups ship with platform-managed exclusions (`NetworkWatcherRG`, `AzureBackupRG_*`, …).                                              |

**Deployment.** Definitions and the initiative deploy **together** via EPAC (the initiative
references definitions by `policyDefinitionName`, so both must be present in the EPAC
`Definitions/` tree). Assign the initiative at a management-group scope; leave `effect` at
`Audit` to observe, then flip it to `Deny` per customer when ready to enforce.

## The naming convention

The source of truth is `getResourceName.bicep` (v1.5). That module is not hand-authored
here it **derives from the `dlw` MSPE (Managed Services Platform Engineering) unit via
the Bicep Framework**, which is where the convention and the resource-type abbreviation
map are owned and maintained. This generator simply mirrors that module's logic onto the
policy side; when the MSPE unit updates the convention or abbreviations, sync the changes
into the `MODULE` map in `gen_dlw_naming_definitions.py` and re-run.

Its main pattern is:

```
{customerAbbreviation}-{resourceTypeAbbreviation}-{service}-{environmentName}-{locationAbbreviation}-[{role}]-{instanceNumber}
```

| Segment                    | Meaning                                       | Example             |
| -------------------------- | --------------------------------------------- | ------------------- |
| `customerAbbreviation`     | Org/customer prefix                           | `dlw`               |
| `resourceTypeAbbreviation` | Per-type abbreviation (`vnet`, `kv`, `st`, …) | `vnet`              |
| `service`                  | Workload/service (resource-group scope)       | `shared`            |
| `environmentName`          | Environment                                   | `dev`, `tst`, `prd` |
| `locationAbbreviation`     | Region                                        | `we`, `ne`          |
| `role` _(optional)_        | Role/purpose (VM, NSG, route table)           | `app`               |
| `instanceNumber`           | Instance counter                              | `001`               |

Example default name: **`dlw-vnet-shared-prd-we-001`**.

### Special cases (taken verbatim from the Bicep function)

Some resource types deviate, mostly to satisfy Azure name rules:

| Resource type(s)                                     | Form                                                                 | Example                         |
| ---------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------- |
| Storage account, Container registry, Fabric capacity | **compact, no hyphens** `{cust}{abbr}{service}{env}{loc}{instance}`  | `dlwstsharedprdwe001`           |
| Virtual machine                                      | **compact** `{service}{env}{loc}{role}{instance}` (no customer/abbr) | `sharedprdweapp001`             |
| OS disk / data disk / NIC                            | `{virtualMachineName}-{abbr}-{instance}`                             | `sharedprdweapp001-osdisk-001`  |
| Snapshot                                             | `{diskName}-snap-{instance}`                                         | `…-osdisk-001-snap-001`         |
| Subnet                                               | `{subnetFunction}Subnet`                                             | `appSubnet`                     |
| VNet peering                                         | `peer-{source}-with-{dest}`                                          | `peer-hub-with-spoke`           |
| Private endpoint                                     | `{attachedResource}-pep-{loc}-{subResource}-{instance}`              | `dlw-kv-…-pep-we-vault-001`     |
| NSG / Route table                                    | default form **plus** a `subnetFunction` / `purpose` segment         | `dlw-nsg-shared-prd-we-app-001` |

## How the policies validate names (and why they're "anchor" checks)

Azure Policy can't do general regular expressions. The two relevant operators are:

- **`like`** wildcard match, but **only one `*`** is allowed.
- **`match` / `matchInsensitively`** `#` = digit, `?` = letter, `.` = any char, but
  **fixed width** (no "one-or-more").

A 6–7 segment convention with free-text segments (`service`, `role`, …) therefore can't
be matched end-to-end. Instead each policy validates the **deterministic anchor** of the
name and flags anything that doesn't match. Per template kind:

| `checkKind`       | Condition that makes a resource **non-compliant**                                      |
| ----------------- | -------------------------------------------------------------------------------------- |
| `default`         | name is **not** `like` `{customerAbbreviation}-{abbr}-*`                               |
| `compact`         | name is **not** `like` `{customerAbbreviation}{abbr}*`                                 |
| `peering`         | name is **not** `like` `peer-*`                                                        |
| `subnet`          | name is **not** `like` `*Subnet`                                                       |
| `parentToken`     | name does **not** `contains` the `-{abbr}-` token (e.g. `-osdisk-`, `-disk-`, `-nic-`) |
| `privateEndpoint` | name does **not** `contains` `-pep-`                                                   |
| `vmCompact`       | name `contains` `-` (VM names must be compact)                                         |

This validates the customer prefix + correct resource-type abbreviation in the right
position the highest-value, false-positive-free part of the convention. The segments
_after_ the anchor (service/env/location/instance) are **not** enforced, by design,
because the operators can't express them precisely. `match`-style fixed-width masks were
considered and rejected (they'd reject any valid name whose segment lengths differ).

Every definition also carries:

- a `customerAbbreviation` parameter (default `dlw`) used to build the anchor,
- an `excludedNamePattern` array parameter (platform-managed carve-outs; resource groups
  ship with `AzureBackupRG_*`, `NetworkWatcherRG`, etc.),
- an `effect` parameter (`Audit` / `Deny` / `Disabled`, default `Audit`).

## Where the data comes from

1. **Base list (`ROWS`)** the full [CAF resource-abbreviations](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-abbreviations)
   table: resource → ARM provider type → abbreviation, used to enumerate every
   policeable Azure resource type and its category.
2. **Customer overrides (`MODULE`)** the ~70 types defined in `getResourceName.bicep`.
   For these, the script **replaces** the CAF abbreviation with the customer's
   abbreviation and applies the correct special-case `checkKind`. The Bicep module is
   the source of truth; the CAF page only fills the long tail of types the module
   doesn't mention (those get the `default` anchor with their CAF abbreviation).

Where several abbreviations map to one ARM type, the anchor accepts all of them
(e.g. `Microsoft.Web/sites` → `dlw-func-*` **or** `dlw-app-*`).

## CAF vs dlw MSPE naming syntax

The official CAF guidance and the dlw MSPE convention share the _components_ (type
abbreviation, workload, environment, region, instance) but order and assemble them
differently. The patterns:

```
CAF (recommended):   {resourceTypeAbbreviation}-{workload}-{environment}-{region}-{instance}
dlw MSPE:            {customerAbbreviation}-{resourceTypeAbbreviation}-{service}-{environmentName}-{locationAbbreviation}-[{role}]-{instanceNumber}
```

### Key syntax differences

1. **Leading token** CAF starts with the _resource-type_ abbreviation; dlw starts with
   the _customer_ abbreviation (`dlw`), then the resource type.
2. **Customer prefix** dlw mandates the `dlw` org prefix as segment 1; CAF treats
   business-unit/org as optional and never leads with it.
3. **Explicit `role` segment** dlw adds an optional role/purpose segment before the
   instance for some types (VM `role`, NSG `subnetFunction`, route table `purpose`); CAF
   folds that into the single workload token.
4. **Region length** dlw uses 2-letter codes (`we`, `ne`); CAF examples use longer
   region tokens (`westeurope`, `weu`).
5. **Environment tokens** dlw uses `dev` / `tst` / `prd`; CAF examples use
   `dev` / `test` / `prod`.
6. **Derived / special forms** dlw prescribes specific shapes CAF leaves open:
   compact VM names _without_ customer+type prefix, child names derived from the parent
   (`{parent}-{abbr}-{instance}` for disks/NIC/snapshot), `{subnetFunction}Subnet` for
   subnets, and `peer-{source}-with-{dest}` for peerings.

### Side-by-side examples

| Resource                    | CAF-style example                    | dlw MSPE example                   |
| --------------------------- | ------------------------------------ | ---------------------------------- |
| Resource group              | `rg-navigator-prod-westeurope-001`   | `dlw-rg-shared-prd-we-001`         |
| Virtual network             | `vnet-navigator-prod-westeurope-001` | `dlw-vnet-shared-prd-we-001`       |
| Subnet                      | `snet-navigator-prod-westeurope-001` | `appSubnet`                        |
| Storage account _(compact)_ | `stnavigatorprodweu001`              | `dlwstsharedprdwe001`              |
| Public IP address           | `pip-navigator-prod-westeurope-001`  | `dlw-pip-we-001`                   |
| Network security group      | `nsg-navigator-prod-westeurope-001`  | `dlw-nsg-shared-prd-we-app-001`    |
| Route table                 | `rt-navigator-prod-westeurope-001`   | `dlw-rt-shared-prd-we-spoke-001`   |
| Virtual machine _(compact)_ | `vmnavprod001`                       | `sharedprdweapp001`                |
| OS disk                     | `osdisk-navigator-001`               | `sharedprdweapp001-osdisk-001`     |
| Private endpoint            | `pep-navigator-prod-westeurope-001`  | `dlw-kv-shared-…-pep-we-vault-001` |
| VNet peering                | `peer-hub-spoke`                     | `peer-hub-with-spoke`              |

> CAF examples are illustrative of the recommended component order; the abbreviations
> themselves are compared in the next section.

## CAF vs getResourceName abbreviation comparison

The table below compares, for every resource type the `getResourceName.bicep` module
covers, the **CAF** abbreviation (left) against the **getResourceName** abbreviation
(right). `getResourceName` wins where they differ it is the source of truth for the
policies. Where one ARM type carries several CAF abbreviations (e.g. CognitiveServices
kinds, internal/external load balancer), all are listed; the module collapses them to
the single abbreviation it actually emits.

> Reflects the current `MODULE` map in `gen_dlw_naming_definitions.py`. Re-derive it from
> `ROWS` (CAF) and `MODULE` (getResourceName) after editing either. `Microsoft.Web/connections`
> (`apic`) and `Microsoft.OperationsManagement/solutions` (`oms`) are **not** on the CAF
> page the module is their only source.

**66 module-covered types 10 differ, 56 identical.**

| Azure resource                         | ARM type                                                   | CAF abbreviation                                                             | getResourceName abbreviation | Status      |
| -------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------- | ----------- |
| API connection                         | `Microsoft.Web/connections`                                | `apic`                                                                       | `apic`                       | same        |
| API management service instance        | `Microsoft.ApiManagement/service`                          | `apim`                                                                       | `apim`                       | same        |
| App Service plan                       | `Microsoft.Web/serverFarms`                                | `asp`                                                                        | `asp`                        | same        |
| Application Insights                   | `Microsoft.Insights/components`                            | `appi`                                                                       | `appi`                       | same        |
| Automation account                     | `Microsoft.Automation/automationAccounts`                  | `aa`                                                                         | `aa`                         | same        |
| Azure Bastion                          | `Microsoft.Network/bastionHosts`                           | `bas`                                                                        | `bas`                        | same        |
| Azure Data Factory                     | `Microsoft.DataFactory/factories`                          | `adf`                                                                        | `adf`                        | same        |
| Azure Databricks Access Connector      | `Microsoft.Databricks/workspaces/accessConnectors`         | `dbac`                                                                       | `dbrcon`                     | **differs** |
| Azure Databricks workspace             | `Microsoft.Databricks/workspaces`                          | `dbw`                                                                        | `dbw`                        | same        |
| Azure Monitor action group             | `Microsoft.Insights/actionGroups`                          | `ag`                                                                         | `ag`                         | same        |
| Azure Monitor data collection rule     | `Microsoft.Insights/dataCollectionRules`                   | `dcr`                                                                        | `dcr`                        | same        |
| Azure SQL database                     | `Microsoft.Sql/servers/databases`                          | `sqldb`                                                                      | `sqldb`                      | same        |
| Azure SQL Database server              | `Microsoft.Sql/servers`                                    | `sql`                                                                        | `sql`                        | same        |
| Connections                            | `Microsoft.Network/connections`                            | `con`                                                                        | `vcn`                        | **differs** |
| Container apps                         | `Microsoft.App/containerApps`                              | `ca`                                                                         | `ca`                         | same        |
| Container apps environment             | `Microsoft.App/managedEnvironments`                        | `cae`                                                                        | `cae`                        | same        |
| Container apps job                     | `Microsoft.App/jobs`                                       | `caj`                                                                        | `caj`                        | same        |
| Container registry                     | `Microsoft.ContainerRegistry/registries`                   | `cr`                                                                         | `cr`                         | same        |
| Data Lake Store account                | `Microsoft.DataLakeStore/accounts`                         | `dls`                                                                        | `dl`                         | **differs** |
| DNS forwarding ruleset                 | `Microsoft.Network/dnsForwardingRulesets`                  | `dnsfrs`                                                                     | `dnsfr`                      | **differs** |
| DNS private resolver                   | `Microsoft.Network/dnsResolvers`                           | `dnspr`                                                                      | `dnspr`                      | same        |
| DNS private resolver inbound endpoint  | `Microsoft.Network/dnsResolvers/inboundEndpoints`          | `in`                                                                         | `in`                         | same        |
| DNS private resolver outbound endpoint | `Microsoft.Network/dnsResolvers/outboundEndpoints`         | `out`                                                                        | `out`                        | same        |
| Event Grid domain                      | `Microsoft.EventGrid/domains`                              | `evgd`                                                                       | `evgd`                       | same        |
| Event Grid namespace                   | `Microsoft.EventGrid/namespaces`                           | `evgns`                                                                      | `evgns`                      | same        |
| Event Grid subscriptions               | `Microsoft.EventGrid/eventSubscriptions`                   | `evgs`                                                                       | `evgs`                       | same        |
| Event Grid system topic                | `Microsoft.EventGrid/systemTopics`                         | `egst`                                                                       | `egst`                       | same        |
| Event Grid topic                       | `Microsoft.EventGrid/domains/topics`                       | `evgt`                                                                       | `evgt`                       | same        |
| Event hub                              | `Microsoft.EventHub/namespaces/eventHubs`                  | `evh`                                                                        | `evh`                        | same        |
| Event Hubs namespace                   | `Microsoft.EventHub/namespaces`                            | `evhns`                                                                      | `evhns`                      | same        |
| ExpressRoute gateway                   | `Microsoft.Network/virtualNetworkGateways`                 | `ergw, vgw`                                                                  | `ergw`                       | **differs** |
| Fabric Capacity                        | `Microsoft.Fabric/capacities`                              | `fc`                                                                         | `fc`                         | same        |
| Firewall                               | `Microsoft.Network/azureFirewalls`                         | `afw`                                                                        | `afw`                        | same        |
| Firewall policy                        | `Microsoft.Network/firewallPolicies`                       | `afwp, waf`                                                                  | `afwp`                       | **differs** |
| Foundry Tools                          | `Microsoft.CognitiveServices/accounts`                     | `ais, aif, oai, cv, cm, cs, cstv, cstvt, di, face, hi, ir, lang, spch, trsl` | `aif`                        | **differs** |
| Function app                           | `Microsoft.Web/sites`                                      | `func, app`                                                                  | `func, app`                  | same        |
| Key vault                              | `Microsoft.KeyVault/vaults`                                | `kv`                                                                         | `kv`                         | same        |
| Load balancer                          | `Microsoft.Network/loadBalancers`                          | `lbi, lbe`                                                                   | `lbi, lbe`                   | same        |
| Load balancer rule                     | `Microsoft.Network/loadBalancers/inboundNatRules`          | `rule`                                                                       | `rule`                       | same        |
| Log Analytics query packs              | `Microsoft.OperationalInsights/querypacks`                 | `pack`                                                                       | `pack`                       | same        |
| Log Analytics workspace                | `Microsoft.OperationalInsights/workspaces`                 | `log`                                                                        | `log`                        | same        |
| Logic app                              | `Microsoft.Logic/workflows`                                | `logic`                                                                      | `logic`                      | same        |
| Managed disk                           | `Microsoft.Compute/disks`                                  | `osdisk, disk`                                                               | `osdisk, disk`               | same        |
| Managed identity                       | `Microsoft.ManagedIdentity/userAssignedIdentities`         | `id`                                                                         | `id`                         | same        |
| NAT gateway                            | `Microsoft.Network/natGateways`                            | `ng`                                                                         | `ng`                         | same        |
| Network interface                      | `Microsoft.Network/networkInterfaces`                      | `nic`                                                                        | `nic`                        | same        |
| Network security group                 | `Microsoft.Network/networkSecurityGroups`                  | `nsg`                                                                        | `nsg`                        | same        |
| Operations Management solution         | `Microsoft.OperationsManagement/solutions`                 | `oms`                                                                        | `oms`                        | same        |
| Private endpoint                       | `Microsoft.Network/privateEndpoints`                       | `pep`                                                                        | `pep`                        | same        |
| Public IP address                      | `Microsoft.Network/publicIPAddresses`                      | `pip`                                                                        | `pip`                        | same        |
| Recovery Services vault                | `Microsoft.RecoveryServices/vaults`                        | `rsv`                                                                        | `rsv`                        | same        |
| Resource group                         | `Microsoft.Resources/subscriptions/resourceGroups`         | `rg`                                                                         | `rg`                         | same        |
| Route server                           | `Microsoft.Network/virtualHubs`                            | `rtserv, vhub`                                                               | `vhub`                       | **differs** |
| Route table                            | `Microsoft.Network/routeTables`                            | `rt`                                                                         | `rt`                         | same        |
| Service Bus namespace                  | `Microsoft.ServiceBus/namespaces`                          | `sbns`                                                                       | `sbns`                       | same        |
| Service Bus queue                      | `Microsoft.ServiceBus/namespaces/queues`                   | `sbq`                                                                        | `sbq`                        | same        |
| Service Bus topic                      | `Microsoft.ServiceBus/namespaces/topics`                   | `sbt`                                                                        | `sbt`                        | same        |
| Service Bus topic subscription         | `Microsoft.ServiceBus/namespaces/topics/subscriptions`     | `sbts`                                                                       | `sbts`                       | same        |
| Snapshot                               | `Microsoft.Compute/snapshots`                              | `snap`                                                                       | `snap`                       | same        |
| Virtual machine                        | `Microsoft.Compute/virtualMachines`                        | `vm`                                                                         | `vm`                         | same        |
| Virtual network                        | `Microsoft.Network/virtualNetworks`                        | `vnet`                                                                       | `vnet`                       | same        |
| Virtual network peering                | `Microsoft.Network/virtualNetworks/virtualNetworkPeerings` | `peer`                                                                       | `peer`                       | same        |
| Virtual network subnet                 | `Microsoft.Network/virtualNetworks/subnets`                | `snet`                                                                       | `subnet`                     | **differs** |
| Virtual WAN                            | `Microsoft.Network/virtualWans`                            | `vwan`                                                                       | `vwan`                       | same        |
| VM storage account                     | `Microsoft.Storage/storageAccounts`                        | `stvm, st`                                                                   | `st`                         | **differs** |
| VPN Gateway                            | `Microsoft.Network/vpnGateways`                            | `vpng`                                                                       | `vpng`                       | same        |

## The `naming` initiative

After writing the definitions, the script bundles them into a single initiative under
`catalogue/initiatives/management/essential/naming/`, mirroring the artifact set the
built-in producer emits per `(domain, tier, category)` group:

| Artifact                                              | Notes                                                                                                                                                     |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `management-esn-naming.policyset.json`  | `policySetDefinition`; one member per `naming-*` definition, referenced by **`policyDefinitionName`** (custom, in-repo) with `groupNames: ["Essential"]`. |
| `management-esn-naming.assignment.json` | `policyAssignment` scaffold with `<root-mg-id>` / `<pac-environment-selector>` mocks.                                                                     |
| `management-esn-naming.exemptions.json` | One `Waiver` exemption stub.                                                                                                                              |
| `management-esn-naming.md`              | Tier rationale + Usage guide + the full member table.                                                                                                     |

No `.roles.json` is written naming policies are Audit/Deny only (no
Modify/DeployIfNotExists), exactly as the producer omits it for non-remediating groups.

**Effect handling:** unlike the built-in flow (which _bakes_ a hardened effect literal
per member), this initiative **bubbles a single top-level `effect` parameter**
(default `Audit`) and wires every member's `effect` to it so the whole set is tuned
from one value at assignment. Each member's other parameters (`customerAbbreviation`,
`excludedNamePattern`) are emitted inline with their definition defaults.

Placement constants live at the top of the script (`INIT_DOMAIN`, `INIT_TIER`,
`INIT_CATEGORY`, `INIT_CAT_ABBR`, `INIT_NAME`, `INIT_DIR`). The EPAC asset names
(`INIT_NAME` = `management-esn-naming`, displayName, nodeName, exemption name) are built by the
shared, brand-neutral, within-limit convention in `engine/shared/naming.py` — identical to the
built-in producer. The `catalogueVersion` stamped into the policyset is read from
`catalogue/catalogue.json` when present, else today's UTC date.

> Note: the script does **not** update the catalogue manifests
> (`catalogue/index.json` / `catalogue/catalogue.json`) those are owned by
> `engine/catalogue_builder/create_initiatives.py`, which would overwrite them on its next run.

## What it does when you run it

```bash
python engine/definition_gen/gen_dlw_naming_definitions.py
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
