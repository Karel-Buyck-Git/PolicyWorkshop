# EPAC Builder — requirements & delivery status

The founding **functional requirements** for the EPAC Builder, mapped to what the system actually does
today. It began as the original project brief (May 2026) and its AI-assisted "Dynamic Policy Engine"
proposal; this doc keeps the durable requirements and drops the parts that were superseded, so it stays
*true* rather than aspirational.

- For the **why and the arc**, see [`../developmentjourney/description.md`](../developmentjourney/description.md).
- For the **authoritative technical design**, see the engine-docs library:
  [`epac-assembler-design.md`](../../epac-workbench/docs/epac-assembler-design.md),
  [`az-taxonomy-pipeline.md`](../../epac-workbench/docs/az-taxonomy-pipeline.md),
  [`azure-policy-source-schema.md`](../../epac-workbench/docs/azure-policy-source-schema.md).
- For the **tracked open work**, see [`../../actions/backlog.md`](../../actions/backlog.md).

**Status legend:** ✅ Shipped · ⏳ Partial · 🔀 Reframed · 🔭 Roadmap · ❌ Superseded

---

## 1. Source & ingestion

| Requirement | Status | Where it landed |
|---|---|---|
| Use Microsoft's official Azure Policy repo as the source | ✅ | Source pinned in `config/policy-source.json`; fetched by `fetch_policy_source.py` |
| Pull the source **daily** / keep it current automatically | 🔭 | Local `--sync` exists; a *scheduled* cloud job is **#37** (builds on **#7/#8**) |
| Track changes/deltas from the last pull via commit history | ⏳ | `fetch_policy_source.py --check` emits a drift signal; wiring it to a notification is **#7** |
| Filter the source (drop deprecated/invalid definitions) | ✅ | `extract_policies.py` — see [`azure-policy-source-schema.md`](../../epac-workbench/docs/azure-policy-source-schema.md) for the `[Deprecated]`/`[Preview]`/`policyType` rules |

## 2. Taxonomy & enrichment

| Requirement | Status | Where it landed |
|---|---|---|
| Tiered taxonomy — **Essential / Professional / Enterprise** | ✅ | `config/tier-rules.yaml` + `shared/tiers.py`; deterministic keyword rules, no LLM |
| Enrich policies with `domain`, `initiative`, and default-value metadata by tier | ✅ | `enrich_policies.py` → catalogue records |
| Select policies by an array of resource names / features (job parameters) | 🔀 | Reframed — the consumer **manifest** selects domain/tier/category groups; the producer extracts all built-ins once into the shared catalogue |
| Store Initiative products for EPAC, shared across the whole team | ✅ | Versioned shared catalogue under `catalogue/initiatives/**` |

## 3. Packaging & output

| Requirement | Status | Where it landed |
|---|---|---|
| Produce a deployable **EPAC** configuration per selected tier | ✅ | `assemble_scaffold.py` renders a full package |
| Render output from templates | 🚀 Surpassed | Output is a deployable package in **three flavours** (native EPAC/JSON, Terraform, Bicep) — plus CI/CD pipelines, a package validator, and setup guides — not a Markdown table |
| Full traceability of a package back to its source | ⏳ | `lineage.json` records `catalogueVersion`; end-to-end provenance (engine + hierarchy + source commit) is the **#27** gap |

## 4. Guardrails

| Requirement | Status | Where it landed |
|---|---|---|
| Execution guardrails for access/edits; dry-run before publish | ✅ | `--check` / `--strict`; the engine is read-only and only ever writes a package |
| Human approval before anything deploys | ✅ | The generated PR validation gate (**#33**) + environment approvals in the emitted pipelines |
| Error handling | ✅ | Validation surfaces unfilled `<REPLACE:>` inputs, placeholder scopes, and referential-integrity breaks |

## 5. Product surface

| Requirement | Status | Where it landed |
|---|---|---|
| EPAC offering accessible **per API**, by tier | 🔭 | Read-only catalogue service — **#18** |
| Auto-update with human interactive approvals | ⏳ | Human approval shipped (above); automated update cadence is **#37** |
| UI for business | 🔭 | Front end — **#31** |
| UI for engineering | 🔭 | Front end — **#31** |
| API for read functions | 🔭 | **#18** |
| Self-service lifecycle (pull → update → publish definitions/initiatives) | 🔭 | Catalogue-upgrade path **#15** + scheduled automation **#37** |
| Reporting tool | 🔭 | Compliance-benchmark coverage reporting — **#40** |

## Superseded — recorded so the intent isn't re-litigated

The original proposal assumed a **language model in the runtime loop** (chunking, summarisation, and
state kept solely to manage LLM context; success metrics like "60% faster" and "zero context-limit
errors"). That premise is gone: the engine is deterministic, stdlib-only Python with **no LLM at run
time** — so those constraints and metrics no longer apply. The specific shape it proposed (the
"Dynamic Policy Engine" name, a `/governance-engine` folder layout, Jinja2 templating, `classify.md`
prompt files) was not adopted; the built system is `epac-workbench/engine/` (producer + consumer). The
LLM's real role turned out to be **helping build the engine**, not running inside it.
