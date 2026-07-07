# Policy Taxonomy — Azure AI Foundry Architecture

## Goals

Migrate the Claude Code lab flow (`lab/prompts/lab-XX/`) to a production-grade pipeline on Azure AI Foundry. Keep Claude Code for prototyping new prompts, rules, and table shapes. Move repeatable, scaled batch generation to Foundry.

## Design principle

The current Claude Code labs treat the entire flow as one agentic loop. ~95% of the work — folder resolution, JSON parsing, schema extraction, deprecation filtering, markdown rendering, structural verification — is deterministic and does not need an LLM. Only **tier classification** and **optional description alignment** require Claude.

The Foundry design therefore is a directed acyclic graph (DAG) of mostly-Python nodes with two LLM nodes inside it. This is what eliminates the slowness and context blow-up.

## Component layout

```
                    ┌─────────────────────────────────────────────┐
                    │           Azure Resource Group              │
                    │                                             │
  GitHub: Azure/    │   ┌─────────────────────┐                   │
  azure-policy ─────┼──▶│ AI Foundry GitOps   │                   │
                    │   │ (daily git pull)    │                   │
                    │   └──────────┬──────────┘                   │
                    │              │ writes JSON tree             │
                    │              ▼                              │
                    │   ┌─────────────────────┐                   │
                    │   │  Storage Account    │                   │
                    │   │  ├─ catalog/raw/    │ (mirrored repo)   │
                    │   │  ├─ catalog/index/  │ (catalog.parquet) │
                    │   │  └─ outputs/        │ (taxonomy md)     │
                    │   └──────────┬──────────┘                   │
                    │              │                              │
                    │              ▼                              │
                    │   ┌─────────────────────┐                   │
                    │   │  AI Foundry Project │                   │
                    │   │  ┌──────────────┐   │                   │
                    │   │  │ Prompt Flow  │   │                   │
                    │   │  │   DAG        │───┼──▶ Claude (MaaS)  │
                    │   │  └──────────────┘   │                   │
                    │   └─────────────────────┘                   │
                    │                                             │
                    └─────────────────────────────────────────────┘
```

## Resources to provision

| Resource | Purpose | SKU |
|---|---|---|
| Azure AI Foundry hub | Workspace shell, shared connections, identity | n/a |
| Azure AI Foundry project | Where the flow + Claude deployment live | n/a |
| Storage account (hub) | Default workspace storage | StorageV2, LRS |
| Storage account (data) | Policy catalog + outputs | StorageV2, LRS, hierarchical namespace |
| Key Vault | Secrets, Foundry connection store | Standard |
| Application Insights | Flow tracing | n/a |
| Log Analytics workspace | App Insights backing | PerGB2018 |
| User-assigned managed identity | Flow → Storage RBAC, MaaS auth | n/a |

The Claude (Sonnet/Opus) serverless deployment is created post-Bicep against the Foundry model catalog — see `README.md`.

## Data store choice — Blob over AI Search

| Option | Cost / mo (idle) | Fit for this workload |
|---|---|---|
| **Blob + Parquet (chosen)** | ~$0.50 | Strong. ~3K rows, read-heavy, Pandas-friendly |
| Azure AI Search Basic | ~$75 | Overkill until cross-resource semantic queries land |
| Cosmos DB (serverless) | ~$1–5 | Workable; more moving parts than needed |

**Add AI Search later** if you reach: (a) free-text search across all policies needed by the flow ("show me anything mentioning private endpoint"), or (b) embeddings-based fuzzy resource name resolution for resources the rule table doesn't cover. Until then, Pandas + `rapidfuzz` does the job in a Python node.

## Catalog ingestion (out of scope for Bicep, in scope for this doc)

Foundry now supports git-backed source control on flows and prompts directly, but **not** for arbitrary external repos as a data source. Two options:

1. **Recommended — Azure Functions timer trigger**: nightly Python function clones `Azure/azure-policy`, walks `built-in-policies/policyDefinitions/`, normalizes each policy to a row, writes:
   - `catalog/raw/{folder}/{file}.json` (mirror, optional, useful for audit)
   - `catalog/index/catalog.parquet` (one row per policy: folder, displayName, description, effect, allowedValues, isDeprecated, isPreview, fileHash)
   - `catalog/index/folders.parquet` (folder names + counts, for resolution)

2. **Container Apps Job + cron** if you'd rather not run Functions in this RG.

Either way, the flow consumes only the Parquet indexes — never the raw JSONs. This is what made `lab-05`'s "Phase 0 extraction" work; we just formalize it.

## The flow (Prompt Flow DAG)

```
              ┌────────────────────┐
              │ inputs:            │
              │  resource_name     │
              │  tier_set          │
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐         Python — fuzzy match
              │ resolve_resource   │         resource_name → folder
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐         Python — read parquet,
              │ extract_fields     │         drop deprecated/preview
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐         Claude (MaaS)
              │ classify_tier      │         batched 20 rows / call
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐         Claude (MaaS), optional
              │ align_descriptions │         only if pitch source matches
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐         Python — Jinja → markdown
              │ render_markdown    │
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐         Python — assertions, fail
              │ verify             │         the row on violation
              └──────────┬─────────┘
                         │
                         ▼
              ┌────────────────────┐
              │ output: blob URL   │
              └────────────────────┘
```

Each node is in `flows/policy-taxonomy/`. The flow runs locally (`pf flow test`) or in Foundry (batch run over a CSV of resource names).

## Where Claude is called and how

Foundry serves Claude through Models-as-a-Service (MaaS) endpoints. The flow nodes call those endpoints with the **Azure AI Inference SDK** (`azure-ai-inference`), authenticating with the user-assigned managed identity. There is no agent loop / threads / tools — the DAG is the orchestration. Each LLM call is a single message with a Jinja-rendered prompt and a structured-output JSON schema response.

### Batched classification

Rather than one call per policy (slow, expensive) or one call per resource (long context, lossy), `classify_tier` chunks the policy list into batches of ~20 and asks Claude for a JSON list of `{policy_id, tier, rationale}`. This keeps each call <2K input tokens and parallelizes naturally over batches inside one resource.

## Verification — split between deterministic and qualitative

| Check | Today (Claude Code) | Foundry |
|---|---|---|
| No `[Deprecated]` rows | LLM re-reads file | `verify.py` assertion |
| Every row has tier+effect | LLM checks | `verify.py` assertion |
| No duplicate display names | LLM checks | `verify.py` assertion |
| Policy ID exists in source | LLM spot-checks 3 rows | `verify.py` checks 100% |
| Columns match template | LLM checks | `verify.py` regex |
| Tier rule consistency ("private endpoint → Enterprise") | LLM judgment | Optional second LLM pass on the rendered table only |

`verify.py` failing fails the row in batch mode — it does not silently produce a broken file.

## Mapping from Claude Code labs to Foundry

| Claude Code artifact | Foundry equivalent |
|---|---|
| `lab-XX-plan.md` (system prompt) | Split: rule text → `data/tier_rules.md`, JSON schema → `data/source_schema.md`, prompt → `prompts/classify_tier.jinja2` |
| `table-template.md` | `data/table_template.md` (Jinja-rendered by `render_markdown.py`) |
| `azure-technologies.md` | Input CSV for batch runs |
| `policy-paths.md` | Replaced by `resolve_resource.py` + `folders.parquet` |
| `descriptions/{tier}/description.md` | `data/descriptions/{tier}.md`, loaded by `align_descriptions.py` |
| `Phase 0 — Extraction` | The nightly ingestion job |
| Self-verification | `verify.py` + optional LLM check |
| Escalation rules | Row-level failure with reason column in batch output |

## Coexistence with Claude Code

Claude Code stays in `lab/prompts/lab-XX/` for **prototyping**:
- Trying new tier rules
- Drafting new resource categories
- One-off investigations

When a prompt stabilizes, port the relevant section to `flows/policy-taxonomy/data/` or `prompts/` and run it at scale through the flow. The Parquet catalog produced by the ingestion job can also be downloaded and used by Claude Code locally — same source of truth for both surfaces.

## Costs, rough order of magnitude

For one full sweep of ~80 resources × ~30 policies/resource = ~2,400 policies:

- Classification: ~120 Claude calls × ~1.5K input + 0.5K output tokens
- Description alignment (optional, ~30% of rows): ~720 calls × ~1K tokens
- Storage / Foundry idle: ~$1/day

The dominant cost is Claude tokens. Batching keeps it low. A full sweep should be in the low single digits of dollars.

## Open questions (to revisit)

1. Do you want both Sonnet and Opus deployed (Sonnet for classification, Opus for description alignment)? Cheaper to use Sonnet for both initially.
2. Output destination — blob only, or also commit to a downstream Git repo (e.g. EPAC definitions)?
3. Should we cache the classification result keyed by policy `fileHash` to skip re-classifying unchanged policies on subsequent runs? (Recommended; trivial Python cache against blob.)
