# EPAC Implementation Plan (hydration-style scaffold)

This scaffold mirrors what `Install-HydrationEpac` produces, pre-built so you can fill in
placeholders and deploy fast. It assumes a Cloud Adoption Framework v3 (CAFv3) management
group layout and the standard two-EPAC-environment model.

## Target model

| EPAC environment (pacSelector) | deploymentRootScope | Purpose |
|---|---|---|
| `tenant01` | `contoso` (intermediate root MG) | production-managed hierarchy |
| `epac-dev` | `epac-dev-contoso` (a copy of the hierarchy) | isolated testing |

CAFv3 management group hierarchy each environment expects:

```
contoso (intermediate root)            epac-dev-contoso (dev copy)
├── contoso-platform                   ├── epac-dev-contoso-platform
│   ├── contoso-connectivity           │   ├── ...
│   ├── contoso-identity
│   └── contoso-management
├── contoso-landingzones               ├── epac-dev-contoso-landingzones
│   ├── contoso-corp
│   └── contoso-online
├── contoso-decommissioned
└── contoso-sandbox
```

## Implementation phases

1. **Prerequisites** — PowerShell 7.4+, Az module, `EnterprisePolicyAsCode` module, Owner/Contributor + Mgmt Group Contributor for setup. (`git` only needed if you regenerate from the real StarterKit.)
2. **Fill placeholders** — `global-settings.jsonc` (`pacOwnerId`, `tenantId`, root scopes, MI location), then the MG IDs / workspace IDs / subscription IDs across assignment and exemption files. Every placeholder is prefixed `REPLACE-`.
3. **Create the dev hierarchy** — either let the real Hydration Kit build the `epac-dev` MG copy, or create the MGs listed above manually.
4. **Plan & deploy to `epac-dev` first**:
   ```powershell
   Build-DeploymentPlans -PacEnvironmentSelector "epac-dev" -DefinitionsRootFolder ./Definitions -OutputFolder ./Output
   Deploy-PolicyPlan     -PacEnvironmentSelector "epac-dev" -DefinitionsRootFolder ./Definitions -InputFolder ./Output
   Deploy-RolesPlan      -PacEnvironmentSelector "epac-dev" -DefinitionsRootFolder ./Definitions -InputFolder ./Output
   ```
5. **Review the plan, then promote to `tenant01`** (gate behind CI/CD approval).
6. **Wire CI/CD** — service principals (Reader / Resource Policy Contributor / RBAC Administrator), OIDC federated credentials, then the pipelines in `pipelines/`.
7. **Operationalize** — remediation tasks for DINE/Modify, generate documentation, manage exemptions.

## What's pre-loaded (mimicking hydration choices)

- **Always:** Microsoft Cloud Security Benchmark (MCSB) assignment at the root scope.
- **Optional frameworks (included, set to Audit):** NIST SP 800-53 Rev. 5. PCI-DSS stub (verify the policy set ID before enabling).
- **Governance starters:** Allowed Locations, tag governance (require Owner tag + inherit CostCenter).
- **Custom policy examples:** deny public IP, restrict NSG rules, deploy NSG diagnostics (DINE).
- **Exemptions:** managed per environment (empty dev, one sample waiver in tenant01).
- **CI/CD:** StarterKit-style pipelines for Azure DevOps and GitHub Actions.

## Decisions to confirm (the questions the real installer asks)

- pacOwnerId: generate a GUID and keep it forever.
- Deploy CAFv3 MG structure? prefix/suffix for MG names?
- Main pacSelector name (here: `tenant01`).
- epac-dev parent MG + naming prefix/suffix.
- Managed identity location (here: `westeurope`).
- Which compliance frameworks beyond MCSB.
- CI/CD platform + module vs script execution.
