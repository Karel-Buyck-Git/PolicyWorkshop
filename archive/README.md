# Archive — retired trees and why they were archived

This folder holds **historical / superseded** trees kept for reference only. Nothing here is
active: it is **not** imported by the engine, **not** exercised by CI, and must not be wired back
into the build. Don't hand-edit it. When something is archived, add a row to the log below and a
short "why" section — so the reasoning travels with the code, not just in a commit message.

| Tree | Archived | Why (one line) | Salvage / see |
|---|---|---|---|
| [`foundry/`](foundry/) | 2026-07-22 | Azure AI Foundry LLM taxonomy pipeline — its premise (tier classification needs an LLM) is superseded by the deterministic engine; never deployed | infra/ingestion design → backlog **#37**; reasoning in `actions/backlog.md` notes + `actions/sessions/2026-07-22.md` |
| [`lab/`](lab/) | 2026-07-22 | Claude Code prototype labs (`lab-01`…`lab-11`) — the original agentic-loop approach to building the taxonomy; superseded by `epac-workbench/engine` | prototype history only; the move itself is backlog **#25** (archived) |
| [`web-dev-best-practices-workspace/`](web-dev-best-practices-workspace/) | 2026-07-23 | Eval/benchmark workspace for the `web-dev-best-practices` skill — `with_skill`/`without_skill` output pairs + gradings; authoring output, not the runnable skill | the live skill moved to `.claude/skills/web-dev-best-practices/`; kept here as provenance of the skill's measured value |

## `foundry/` — Azure AI Foundry prompt-flow architecture

**What it was.** The "production-grade" plan to build the policy taxonomy on Azure AI Foundry: a
Prompt Flow DAG of Python nodes wrapped around **two LLM nodes** (`classify_tier`,
`align_descriptions`, calling Claude via Foundry Models-as-a-Service), plus Bicep infra (AI Foundry
hub + project, dual storage, Key Vault, App Insights, Log Analytics, a user-assigned managed
identity + RBAC) and a documented-but-never-built ingestion job (nightly clone of `Azure/azure-policy`
→ normalize → storage). See `foundry/architecture.md`.

**Why archived.** Its founding premise — *"~95% is deterministic; only tier classification and
description alignment need an LLM"* — no longer holds. The current `epac-workbench/engine` classifies
tiers **deterministically** from `config/tier-rules.yaml` (`shared/tiers.py`), with no LLM in the
path, so the AI Foundry hub / Claude-MaaS / prompt-flow DAG that foundry is built around isn't needed.
It was never deployed (2 commits ever; the ingestion job + `seed_catalog.py` were explicitly "not
here yet").

**What still has value (don't rebuild from scratch).** `foundry/infra/` Bicep (managed identity +
storage + monitoring + RBAC) and `architecture.md`/`README.md` §"Catalog ingestion" (the "nightly
`Azure/azure-policy` clone on a timer, not local" pattern — Azure Functions timer vs Container Apps
Job) are **prior art for the recurring cloud catalogue-update platform**. That work is captured as
backlog **#37** — and is far lighter than foundry now, because the deterministic producer needs no AI
Foundry hub and no LLM.

## `lab/` — Claude Code prototype labs

**What it was.** The original prototyping surface (`lab-01`…`lab-11`, including `lab-11`'s own private
pipeline copy) — the early agentic-loop approach to building the policy taxonomy with Claude Code.

**Why archived.** Self-contained prototype history with no ties into the active engine; superseded by
the deterministic `epac-workbench/engine`. Kept for reference (how the approach evolved) but not part
of any build. The earlier move `product/lab/` → root `lab/` is backlog **#25** (archived); the move
into `archive/` happened 2026-07-22.

## `web-dev-best-practices-workspace/` — skill eval/benchmark workspace

**What it was.** The authoring + benchmarking workspace for the general `web-dev-best-practices` skill:
`iteration-1/` with paired `with_skill` / `without_skill` code outputs across three evals (a user
table, an orders route, a login hook), each with a `grading.json`, plus `benchmark.json`/`benchmark.md`
and a rendered `eval-review-iteration-1.html`. It measures how much the skill improves generated code.

**Why archived.** It is **authoring output, not the runnable skill** — the live skill (`SKILL.md` +
`evals/`) was promoted to `.claude/skills/web-dev-best-practices/` (2026-07-23), where Claude Code
auto-discovers it for the whole team ahead of the front-end work (**#31**). The workspace has no place
in that auto-discovery path but is worth keeping as **provenance of the skill's measured value** (the
with/without-skill deltas), so it lives here rather than being deleted. It arrived in this repo as
stray stashed material under a top-level `tools/` folder, unrelated to the Azure Policy / EPAC engine.
