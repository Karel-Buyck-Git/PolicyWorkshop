"""Turn a rendered flavour folder into a self-contained, deployable package.

Each flavour render (epac/terraform/bicep) writes its IaC content into the package
dir; ``finalize`` then makes that dir a ready-to-commit repo by adding the flavour's
GitHub Actions pipeline, the management-group hierarchy diagram under ``docs/``, and a
deploy ``README.md``. Provenance (``lineage.json`` + ``report.md``) is written by the
caller (``report.write_reports``) into the same dir, so the package stands alone.
"""
import shutil
from pathlib import Path

from epac_builder.writeutil import write_text


def finalize(ir, pkg_dir, flavour, manifest_path, log=print):
    pkg_dir = Path(pkg_dir)
    customer = ir["identity"]["customer"]
    selectors = [e["selector"] for e in ir["environments"]]

    # hierarchy diagram(s) -> docs/
    designs = Path(manifest_path).resolve().parents[1] / "designs"
    copied = []
    for variant in ("rich", "minimal"):
        svg = designs / f"{customer}-mgmt-groups.{variant}.svg"
        if svg.is_file():
            (pkg_dir / "docs").mkdir(parents=True, exist_ok=True)
            shutil.copy2(svg, pkg_dir / "docs" / svg.name)
            copied.append(svg.name)
    if not copied:
        log(f"[package] note: no {customer}-mgmt-groups.*.svg in {designs} (skipped docs/)")

    wf_name, wf_fn = _WORKFLOWS[flavour]
    write_text(pkg_dir / ".github" / "workflows" / wf_name, wf_fn(ir, selectors))

    # PR gate (epac flavour only for now — terraform/bicep have no equivalent yet).
    # The validator is emitted verbatim from its single source next to this module, so
    # the shipped copy can never drift from the one we develop against; the contoso
    # golden-fixture byte-diff proves that on every build.
    if flavour == "json":
        write_text(pkg_dir / ".github" / "workflows" / "epac-validate.yml",
                   _epac_validate_workflow(ir, selectors))
        write_text(pkg_dir / "validate-package.py", _validator_source())

    write_text(pkg_dir / "README.md", _READMES[flavour](customer, ir, selectors, copied))
    return pkg_dir


def _validator_source():
    """The static package validator, read from its source of truth in this package."""
    return (Path(__file__).parent / "pkgvalidate.py").read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# GitHub Actions pipelines (starters; OIDC federated login)
# --------------------------------------------------------------------------- #


def _epac_workflow(ir, selectors):
    default = selectors[0] if selectors else "epac-dev"
    tpl = r"""# Enterprise Policy as Code (EPAC) — deploy this policy package.
# Three-phase flow with least-privilege identities:
#   plan (Reader) -> deploy-policy (Resource Policy Contributor) -> deploy-roles (RBAC Administrator)
name: EPAC deploy

on:
  workflow_dispatch:
    inputs:
      pacEnvironment:
        description: pacSelector to target
        default: "__DEF__"
  push:
    branches: [ main ]
    paths: [ "Definitions/**" ]

permissions:
  id-token: write
  contents: read

# EPAC reconciles a whole deploymentRootScope and deletes what is not in code, so two
# runs against the same pacEnvironment must never overlap. Queue instead of cancelling:
# cancelling mid-deploy would leave the scope half-reconciled.
concurrency:
  group: epac-deploy-${{ github.event.inputs.pacEnvironment || '__DEF__' }}
  cancel-in-progress: false

env:
  DEFINITIONS: Definitions
  OUTPUT: Output
  PAC_ENVIRONMENT: ${{ github.event.inputs.pacEnvironment || '__DEF__' }}

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install EPAC
        shell: pwsh
        run: Install-Module EnterprisePolicyAsCode -Force -Scope CurrentUser
      - name: Azure login (Reader)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.PLAN_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Build deployment plans
        shell: pwsh
        run: Build-DeploymentPlans -PacEnvironmentSelector "$env:PAC_ENVIRONMENT" -DefinitionsRootFolder "$env:DEFINITIONS" -OutputFolder "$env:OUTPUT"
      - uses: actions/upload-artifact@v4
        with: { name: epac-plans, path: Output }

  deploy-policy:
    needs: plan
    runs-on: ubuntu-latest
    environment: epac-policy
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { name: epac-plans, path: Output }
      - name: Install EPAC
        shell: pwsh
        run: Install-Module EnterprisePolicyAsCode -Force -Scope CurrentUser
      - name: Azure login (Resource Policy Contributor)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.POLICY_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Deploy policy plan
        shell: pwsh
        run: Deploy-PolicyPlan -PacEnvironmentSelector "$env:PAC_ENVIRONMENT" -DefinitionsRootFolder "$env:DEFINITIONS" -InputFolder "$env:OUTPUT"

  deploy-roles:
    needs: deploy-policy
    runs-on: ubuntu-latest
    environment: epac-roles
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { name: epac-plans, path: Output }
      - name: Install EPAC
        shell: pwsh
        run: Install-Module EnterprisePolicyAsCode -Force -Scope CurrentUser
      - name: Azure login (RBAC Administrator)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.ROLES_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Deploy roles plan
        shell: pwsh
        run: Deploy-RolesPlan -PacEnvironmentSelector "$env:PAC_ENVIRONMENT" -DefinitionsRootFolder "$env:DEFINITIONS" -InputFolder "$env:OUTPUT"
"""
    return tpl.replace("__DEF__", default)


def _epac_validate_workflow(ir, selectors):
    default = selectors[0] if selectors else "epac-dev"
    tpl = r"""# Pull-request gate for this policy package — NOTHING is deployed here.
#   validate : static checks (no Azure, no secrets) — runs on every PR, forks included
#   plan     : real what-if via Build-DeploymentPlans, Reader identity, same-repo PRs only
name: EPAC validate

on:
  pull_request:
    paths: [ "Definitions/**", "validate-package.py" ]

permissions:
  contents: read

env:
  DEFINITIONS: Definitions
  OUTPUT: Output
  PAC_ENVIRONMENT: "__DEF__"

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      # Shape, reference and pacSelector-coverage checks. Catches an assignment that
      # would be silently skipped for a pacEnvironment, which no other step detects.
      - name: Static package validation
        run: python validate-package.py .

  plan:
    needs: validate
    # A pull request from a fork receives no secrets, so OIDC federation cannot work.
    # Skip (rather than fail) those, and never switch this to pull_request_target —
    # that would run untrusted code with write permissions and secrets.
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - name: Install EPAC
        shell: pwsh
        run: Install-Module EnterprisePolicyAsCode -Force -Scope CurrentUser
      # Reader only. No Deploy-* cmdlet may appear in this workflow.
      - name: Azure login (Reader)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.PLAN_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Build deployment plan (what-if only)
        shell: pwsh
        run: Build-DeploymentPlans -PacEnvironmentSelector "$env:PAC_ENVIRONMENT" -DefinitionsRootFolder "$env:DEFINITIONS" -OutputFolder "$env:OUTPUT"
      - uses: actions/upload-artifact@v4
        with: { name: epac-plan-pr, path: Output }
"""
    return tpl.replace("__DEF__", default)


def _terraform_workflow(ir, selectors):
    default = selectors[0] if selectors else "epac-dev"
    tpl = r"""# Terraform (azurerm) policy deploy.
name: Terraform deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        description: tfvars environment (selector)
        default: "__DEF__"
  push:
    branches: [ main ]
    paths: [ "**.tf", "environments/**" ]

permissions:
  id-token: write
  contents: read

env:
  ARM_USE_OIDC: "true"
  ARM_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
  ARM_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
  ARM_CLIENT_ID: ${{ secrets.TF_CLIENT_ID }}
  TFVARS: environments/${{ github.event.inputs.environment || '__DEF__' }}.tfvars

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.TF_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - run: terraform plan -var-file="$TFVARS" -out tfplan
      - uses: actions/upload-artifact@v4
        with: { name: tfplan, path: tfplan }

  apply:
    needs: plan
    runs-on: ubuntu-latest
    environment: terraform-apply
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { name: tfplan, path: . }
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.TF_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - run: terraform apply tfplan
"""
    return tpl.replace("__DEF__", default)


def _bicep_workflow(ir, selectors):
    default = selectors[0] if selectors else "epac-dev"
    env0 = ir["environments"][0] if ir["environments"] else {}
    mg_id = (env0.get("rootScope") or "").rsplit("/", 1)[-1] or "REPLACE-management-group-id"
    location = env0.get("managedIdentityLocation") or "westeurope"
    tpl = r"""# Bicep policy deploy (management-group scope).
name: Bicep deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        description: parameters environment (selector)
        default: "__DEF__"
      managementGroupId:
        description: target management group id
        default: "__MG__"
      location:
        description: deployment location
        default: "__LOC__"

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: bicep-apply
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.BICEP_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Deploy at management group scope
        uses: azure/cli@v2
        with:
          inlineScript: |
            env="${{ github.event.inputs.environment || '__DEF__' }}"
            az deployment mg create \
              --name "${{ github.run_id }}" \
              --management-group-id "${{ github.event.inputs.managementGroupId || '__MG__' }}" \
              --location "${{ github.event.inputs.location || '__LOC__' }}" \
              --template-file main.bicep \
              --parameters "@main.parameters.$env.json"
"""
    return tpl.replace("__DEF__", default).replace("__MG__", mg_id).replace("__LOC__", location)


_WORKFLOWS = {
    "json": ("epac.yml", _epac_workflow),
    "terraform": ("terraform.yml", _terraform_workflow),
    "bicep": ("bicep.yml", _bicep_workflow),
}


# --------------------------------------------------------------------------- #
# READMEs
# --------------------------------------------------------------------------- #

PLACEHOLDER_NOTE = (
    "Any assignment scoped to "
    "`/providers/Microsoft.Management/managementGroups/REPLACE-set-managementGroup-in-manifest` "
    "had no target management group — set `managementGroup` on that selection in the manifest and "
    "re-build, or remove the selection. Azure rejects this placeholder."
)


def _header(customer, ir, kind):
    return [
        f"# {customer} — {kind} policy package",
        "",
        f"Catalogue version `{ir['catalogueVersion']}` · pacOwnerId `{ir['identity']['pacOwnerId']}`.",
        "",
        "Generated by the epac-builder. **The contents of this folder are the root of a dedicated",
        "deploy repo** — publish them at the *top level* of their own repository, not as a subfolder",
        "of an existing one: GitHub only discovers workflows at the repo root, and the bundled",
        "pipeline resolves `Definitions/` from there. **Do not hand-edit the generated files — re-run",
        "the builder from the manifest instead.**",
        "",
    ]


def _epac_readme(customer, ir, selectors, svgs):
    diagram = f"![Management groups](docs/{svgs[0]})\n\n" if svgs else ""
    lines = _header(customer, ir, "EPAC") + [
        "## Layout",
        "",
        "```",
        "Definitions/                  # EPAC definitions root",
        "  global-settings.jsonc       # pacEnvironments + pacOwnerId",
        "  policySetDefinitions/       # the customer initiatives",
        "  policyAssignments/          # assignments, scoped to your management groups",
        "  policyExemptions/           # (if any)",
        ".github/workflows/epac.yml    # plan -> deploy-policy -> deploy-roles (push/dispatch)",
        ".github/workflows/epac-validate.yml  # PR gate: static checks + what-if plan",
        "validate-package.py           # the static checks; run it locally too",
        "docs/  README.md  lineage.json  report.md",
        "```",
        "",
        "## Check before you commit",
        "",
        "```",
        "python validate-package.py .",
        "```",
        "",
        "Runs offline (no Azure, no credentials): confirms every file parses, that each "
        "assignment has a `scope` entry for **every** `pacSelector` in `global-settings.jsonc` "
        "— an assignment missing one is silently skipped for that environment — that policy set "
        "and custom policy references resolve, and that scope/GUID values are well formed. "
        "The same script runs automatically on every pull request. It is a *static* check: "
        "whether the referenced management groups actually exist is proven by the plan step.",
        "",
        diagram + "## Before you deploy",
        "",
        "1. **Fill placeholders.** Search `Definitions/` for `<REPLACE:` and resolve every one.",
        f"2. **Check scopes.** {PLACEHOLDER_NOTE}",
        "3. **Create three OIDC identities** (least privilege): plan → **Reader**, deploy-policy → "
        "**Resource Policy Contributor**, deploy-roles → **Role Based Access Control Administrator**.",
        "4. **Secrets:** `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `PLAN_CLIENT_ID`, "
        "`POLICY_CLIENT_ID`, `ROLES_CLIENT_ID`.",
        "5. **Environments** `epac-policy`, `epac-roles` with required reviewers to gate the deploys.",
        "",
        f"## Deploy ({', '.join(selectors)})",
        "",
        "Run the **EPAC deploy** workflow (`workflow_dispatch`): "
        "`Build-DeploymentPlans -> Deploy-PolicyPlan -> Deploy-RolesPlan`. See `report.md`.",
        "",
    ]
    return "\n".join(lines)


def _terraform_readme(customer, ir, selectors, svgs):
    diagram = f"![Management groups](docs/{svgs[0]})\n\n" if svgs else ""
    lines = _header(customer, ir, "Terraform") + [
        "## Layout",
        "",
        "```",
        "main.tf  variables.tf          # azurerm policy set definitions + assignments + roles",
        "environments/<selector>.tfvars # per-environment inputs",
        ".github/workflows/terraform.yml",
        "docs/  README.md  lineage.json  report.md",
        "```",
        "",
        diagram + "## Deploy",
        "",
        f"1. {PLACEHOLDER_NOTE}",
        "2. Create an OIDC identity with **Resource Policy Contributor** (and **RBAC Administrator** "
        "if assignments include DINE/Modify role assignments).",
        "3. **Secrets:** `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `TF_CLIENT_ID`.",
        f"4. Run the **Terraform deploy** workflow (`plan -> apply`) for an environment "
        f"({', '.join(selectors)}); it uses `-var-file=environments/<selector>.tfvars`.",
        "",
    ]
    return "\n".join(lines)


def _bicep_readme(customer, ir, selectors, svgs):
    diagram = f"![Management groups](docs/{svgs[0]})\n\n" if svgs else ""
    lines = _header(customer, ir, "Bicep") + [
        "## Layout",
        "",
        "```",
        "main.bicep                     # policySetDefinitions + assignments + role assignments",
        "policies/                      # policyset properties + bound params (loadJsonContent)",
        "main.parameters.<selector>.json",
        ".github/workflows/bicep.yml",
        "docs/  README.md  lineage.json  report.md",
        "```",
        "",
        diagram + "## Deploy",
        "",
        f"1. {PLACEHOLDER_NOTE}",
        "2. Create an OIDC identity with **Resource Policy Contributor** (+ **RBAC Administrator** for "
        "role assignments).",
        "3. **Secrets:** `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `BICEP_CLIENT_ID`.",
        f"4. Run the **Bicep deploy** workflow (`workflow_dispatch`) for an environment "
        f"({', '.join(selectors)}); it runs `az deployment mg create` with "
        "`main.parameters.<selector>.json`.",
        "",
    ]
    return "\n".join(lines)


_READMES = {
    "json": _epac_readme,
    "terraform": _terraform_readme,
    "bicep": _bicep_readme,
}
