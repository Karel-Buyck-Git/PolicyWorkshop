# Bicep — Azure Policy governance (parity with the EPAC/JSON scaffold)

Implements the same governance as `../Json` (EPAC), natively in Bicep, deployed at the
management group scope with `az deployment mg`.

## Layout

```
Bicep/
├── main.bicep                       # targetScope managementGroup; orchestrates modules
├── main.parameters.dev.json
├── main.parameters.tenant01.json
├── modules/
│   ├── policyDefinitions.bicep      # 4 custom policies
│   ├── policySetDefinitions.bicep   # security-baseline + tagging initiatives
│   ├── policyAssignments.bicep      # MCSB (+NIST/+PCI), custom baseline, allowed-locations, tagging + role assignments
│   └── policyExemptions.bicep       # sample sandbox waiver (deployed to sandbox MG)
└── pipelines/
    ├── AzureDevOps/azure-pipelines.yml
    └── GitHubActions/bicep-cd.yml
```

## Mapping to the EPAC scaffold

| EPAC concept | Bicep equivalent |
|---|---|
| pacEnvironment / deploymentRootScope | `--management-group-id` + a parameters file |
| policyDefinitions/* | `Microsoft.Authorization/policyDefinitions` |
| policySetDefinitions/* | `Microsoft.Authorization/policySetDefinitions` |
| policyAssignments/* | `Microsoft.Authorization/policyAssignments` |
| policyExemptions/* | `Microsoft.Authorization/policyExemptions` |
| EPAC auto role assignments | explicit `Microsoft.Authorization/roleAssignments` |
| Build/Deploy plans | `az deployment mg what-if` / `create` |

## Run

```bash
az login --tenant <tenantId>

# dev first (target the dev MG)
az deployment mg what-if \
  --management-group-id epac-dev-contoso --location westeurope \
  --template-file main.bicep --parameters @main.parameters.dev.json

az deployment mg create \
  --management-group-id epac-dev-contoso --location westeurope \
  --template-file main.bicep --parameters @main.parameters.dev.json

# then tenant01 (target the intermediate root MG; gate behind approval in CI/CD)
az deployment mg create \
  --management-group-id contoso --location westeurope \
  --template-file main.bicep --parameters @main.parameters.tenant01.json
```

`--location` is the location for the deployment metadata (and default MI location); the policy
resources themselves are scoped to the management group.

## Edit before running

- `logAnalyticsWorkspaceId`, `sandboxManagementGroupId` per parameters file
- the `--management-group-id` you target (dev vs tenant root)
- `enablePci` + `pciPolicySetId` if enabling PCI

## Caveats vs EPAC

- **Role assignments are not auto-calculated.** Roles for the custom DINE and the tagging Modify
  are included; add role assignments for MCSB/NIST identities when enabling remediation.
- A Bicep deployment is additive/idempotent for what it declares; it does **not** delete
  out-of-band policy the way EPAC's desired-state engine does.
- The DINE diagnostic template is illustrative — validate apiVersion/log categories.
- Bicep escapes ARM policy expressions with `\'...\'` (e.g. `[parameters(\'effect\')]`).
