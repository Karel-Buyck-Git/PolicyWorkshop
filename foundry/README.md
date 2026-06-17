# Policy Taxonomy on Azure AI Foundry

Production-grade port of the Claude Code lab flow (`product/lab/prompts/lab-XX/`)
to Azure AI Foundry. Read [`architecture.md`](./architecture.md) first — it
explains the design decisions, the resource shape, and the Claude Code → Foundry
migration mapping.

## Repository layout

```
foundry/
├── architecture.md                  Design rationale, DAG, mappings
├── README.md                        This file
├── infra/                           Bicep for the Azure resources
│   ├── main.bicep
│   ├── main.bicepparam
│   ├── deploy.sh
│   └── modules/
│       ├── monitoring.bicep
│       ├── storage.bicep
│       ├── identity.bicep
│       ├── foundry-hub.bicep
│       └── rbac.bicep
└── flows/
    └── policy-taxonomy/             Prompt Flow DAG
        ├── flow.dag.yaml
        ├── requirements.txt
        ├── _storage.py              Auth + blob I/O helpers
        ├── resolve_resource.py      Python node
        ├── extract_fields.py        Python node
        ├── classify_tier.py         LLM node (Claude on Foundry MaaS)
        ├── align_descriptions.py    LLM node (optional, Claude)
        ├── render_markdown.py       Python node
        ├── verify.py                Python node
        ├── prompts/
        │   └── classify_tier.jinja2
        ├── data/
        │   ├── tier_rules.md
        │   ├── table_template.md
        │   └── descriptions/
        │       ├── essential.md
        │       ├── professional.md
        │       └── enterprise.md
        └── inputs/
            └── resources.csv        Batch run input
```

## Prerequisites

- Azure CLI 2.60+ logged into the target subscription (`az login`)
- Bicep CLI (`az bicep install`)
- Python 3.11+ for local flow testing
- An empty resource group in the target subscription
- Quota for Claude Sonnet (or your preferred model) in your region

## Step 1 — Deploy infrastructure

```powershell
# 1. Edit infra/main.bicepparam — set ownerObjectId to your AAD user/SP object id
$ownerId = (az ad signed-in-user show --query id -o tsv)

# 2. Deploy
cd infra
bash deploy.sh <your-resource-group>
```

The deployment provisions: Foundry hub + project, dual storage (workspace +
data), Key Vault, App Insights, Log Analytics, and a user-assigned managed
identity with Storage Blob Data Contributor on the data account.

Capture the outputs:

```text
hubName
projectName
projectEndpoint
storageDataEndpoint
uamiClientId
appInsightsConnStr
```

## Step 2 — Deploy Claude as a serverless model

The Bicep does not provision the model deployment because the model catalog
selection is rarely worth templating. From the Foundry portal:

1. Open the Foundry project in the portal.
2. **Models + endpoints** → **Deploy model** → pick `Claude Sonnet 4.6` (or
   the latest available Claude on Foundry).
3. Deployment type: **Serverless API** (Models as a Service).
4. Name the deployment `claude-sonnet-4-6` (matches the default in
   `classify_tier.py`).
5. Repeat for any additional model you want for `align_descriptions`.

The endpoint URL takes the shape
`https://<project>.<region>.models.ai.azure.com`. Note both that and the
deployment name for Step 4.

## Step 3 — Provision the policy-catalog ingestion job

This is where the daily git pull lives. Two options (both out of scope for
this Bicep — pick one and provision separately):

**Option A — Azure Functions, timer trigger (recommended)**
- Python timer trigger, daily at 03:00 UTC.
- `git clone --depth 1 https://github.com/Azure/azure-policy.git`
- Walk `built-in-policies/policyDefinitions/`.
- For each JSON, build a row with: `policy_id, folder, display_name, description, effect, allowed_values, is_deprecated, is_preview, file_hash`.
- Write `catalog/index/catalog.parquet` and `catalog/index/folders.parquet` to
  the **data** storage account (the one ending in `dat...`).

**Option B — Container Apps Job, cron schedule**
- Containerised Python script doing the same thing.
- Cleaner if you prefer not to run a Functions plan in this RG.

Either way the contract for the flow is the same: two Parquet files at
`catalog/index/*.parquet` on the data storage account. Until the job runs,
populate them manually from your local clone:

```bash
python tools/seed_catalog.py \
  --source "C:/GIT/Official Azure Policy/azure-policy/built-in-policies/policyDefinitions" \
  --account-url https://<datastorageaccount>.blob.core.windows.net
```

(`tools/seed_catalog.py` is the next file to write — pair it with the
ingestion function so they share the normalization logic.)

## Step 4 — Run the flow locally

```powershell
cd flows/policy-taxonomy
python -m venv .venv
.venv/Scripts/Activate.ps1
pip install -r requirements.txt

# Auth: log in once. azure-identity will pick up the CLI token.
az login

# Tell the flow where the data storage account lives and which model to use.
$env:STORAGE_ACCOUNT_URL  = "https://<datastorageaccount>.blob.core.windows.net"
$env:AZURE_AI_INFERENCE_ENDPOINT   = "https://<project>.<region>.models.ai.azure.com"
$env:AZURE_AI_INFERENCE_DEPLOYMENT = "claude-sonnet-4-6"

# Single-resource test
pf flow test --flow . `
  --inputs resource_name="App Service" tier_set="essential,professional,enterprise"
```

The rendered markdown lands in `_out/` locally. Verify output with:

```powershell
Get-Content _out/appservice-policies.md
```

## Step 5 — Run the flow as a batch in Foundry

Once local runs succeed, push the flow to the Foundry project and run it over
the input CSV.

```powershell
cd flows/policy-taxonomy

# Authenticate to your Foundry workspace
az ml workspace show -n <projectName> -g <rg>

# Submit a batch run over inputs/resources.csv
pf run create --flow . --data inputs/resources.csv --stream
```

Each row in the CSV produces one markdown file in the data storage account at
`outputs/<resource-slug>-policies.md`. Fan-out is handled by Prompt Flow —
parallelism is set on the run object (`--worker-count`).

## Step 6 — Wire up scheduled runs (optional)

If you want the taxonomy to refresh after every daily catalog ingest, set up
an Azure Logic App or Azure Function to trigger the Foundry batch run on the
storage event for `catalog/index/catalog.parquet`. The Foundry SDK has a
`pfclient.runs.create_or_update` method that takes the same flow + data CSV.

## Coexistence with the Claude Code labs

| Workflow | Surface |
|---|---|
| Drafting a new tier rule | Claude Code, edit `data/tier_rules.md` in this folder, run lab-style |
| Adding a new resource | Update `inputs/resources.csv`; the flow handles the rest |
| Tweaking the markdown shape | Edit `data/table_template.md`; both labs and flow consume it |
| Validating tier accuracy | Both — Claude Code for spot-checks, flow's `verify.py` for assertions |

The Parquet catalog produced by the ingestion job is the source of truth for
both surfaces. You can mount the data storage account in your dev box and
point Claude Code at it directly.

## Troubleshooting

- **`AZURE_AI_INFERENCE_ENDPOINT must be set`** — export both env vars (Step 4).
- **`No folder match for resource '<name>'`** — add an entry to
  `KNOWN_MAPPINGS` in `resolve_resource.py`, or use the exact folder name from
  the catalog.
- **`Catalog parquet missing required columns`** — the ingestion job needs to
  re-run with the latest schema. Check column list in `extract_fields.py`.
- **`Verification: 'private endpoint' wording but tier=Essential`** — Claude
  drifted from the rules. Either add a clarifying example to
  `data/tier_rules.md` and re-run, or hand-correct the row.

## What is intentionally not here yet

- **`tools/seed_catalog.py`** and the Functions/Container Apps Job source for
  the ingestion. These should share normalization logic — once you pick A or B
  I'll add the matching scaffold.
- **AI Search** — see `architecture.md` for when to add it.
- **Cost tracking** — App Insights ingests the run telemetry; a workbook on
  Log Analytics is a follow-up.
- **CI/CD** — `flow.dag.yaml` is a stable artifact suitable for GitOps; an
  Azure DevOps or GitHub Actions pipeline that runs `pf flow test` on PR is
  the next reasonable step.
