# Backlog

Living list of action items for catalogue-builder / epac-builder. Sourced from reviews in
`actions/log/` and consumer feedback in `actions/feedback/`. Update at the start/end of every
session — see `actions/sessions/`.

Status: `todo` / `in-progress` / `done`

| # | Item | Effort | Status | Source |
|---|---|---|---|---|
| 1 | Test suite / CI on the builder (golden-fixture diff against `customer/package/`) | low | done (2026-07-03) | actions/log/review-07-03-26.md |
| 1a | Add `requirements.txt`/`pyproject.toml` marker (stdlib-only, but make it explicit) | low | done (2026-07-05) | actions/log/review-07-03-26.md |
| 1b | Drop committed `__pycache__`, add to `.gitignore` | low | done (2026-07-05) | actions/log/review-07-03-26.md |
| 2 | Manifest completion guardrail: `--strict`/pre-deploy gate that fails when any `<REPLACE:>` or placeholder-scope survives into output | medium | done (2026-07-06) | actions/log/review-07-03-26.md |
| 3 | Catalogue customer-clean: resolve/remove `undefined`-domain policies, drop `builtinpolicytest` so the catalogue can be regenerated reproducibly | high | done (2026-07-19) | actions/log/review-07-03-26.md |
| 4 | `customer/package/docs/*.svg` is stale vs. `customer/designs/*.svg` (byte-diff, same commit) — CI's golden-fixture diff excludes `docs/` because of this; resync so the exclusion can be dropped | low | done (2026-07-04) | discovered building CI, 2026-07-03 |
| 5 | Producer's `--source` default is hard-coded to a local clone path (`C:\GIT\Official Azure Policy\...`) — breaks for anyone but Karel running without `--source`. In `extract_policies.py` (`DEFAULT_SOURCE`, ~line 270; docstring line 17; argparse default line 292) and `create_initiatives.py` (`DEFAULT_SOURCE`, ~line 55; argparse default line 659). `--source` already exists as an override, so the fix is just: stop defaulting to a personal path — require `--source` explicitly (fail with a clear message) or read an env var (e.g. `AZURE_POLICY_REPO`), then update the two docstrings, `flows/catalogue_builder/README.md`, and `docs/az-taxonomy-pipeline.md`. Producer-only; doesn't touch the customer-facing epac-builder path | low | done (2026-07-03) | Karel, 2026-07-03 |
| 6 | Pinned-commit fetch for the official policy source: `config/policy-source.json` pin + `flows/tools/fetch_policy_source.py` (`--sync` / `--check`) materialising a gitignored `.policy-source/` cache; `official_policy_source()` defaults to it. Gives everyone one reproducible version (builds match committed `builtInsRef`). Kernel of the future daily-sync system | medium | done (2026-07-04) | Karel, 2026-07-04 |
| 7 | Daily-sync system: schedule `fetch_policy_source.py --sync` + `--check` (GitHub Action / cron) and wire the `--check` drift signal (exit 2) into a notification. Builds on #6 | medium | todo | discovered building #6, 2026-07-04 |
| 8 | Producer-side CI: now that the source is reproducible (#6), add a workflow that runs `fetch_policy_source.py` then regenerates the catalogue and diffs it (extend/complement `.github/workflows/contoso-epac-build.yml`, which currently only exercises the consumer/assembler) | medium | todo | discovered building #6, 2026-07-04 |
| 9 | Enable CI in GitHub: the workflow files exist but Actions has never run — push the repo/branch (`alpha/epac-builder/actions` is currently unpushed), enable Actions, and confirm `contoso epac build` (#11) plus any other workflows run green. Prereq for #7/#8/#11 actually executing anywhere | medium | done (2026-07-05) | Karel, 2026-07-04 |
| 10 | Customer-folder reshape: `customer/` is doing double duty as the worked `contoso` sample **and** the CI golden fixture, so a new user can't start from an empty scaffold. Move the sample (filled `manifest.example.jsonc`, `designs/contoso-*`, `package/`) to `catalogue-builder/examples/contoso/` via `git mv`; leave `customer/` holding only schemas + `manifest.template.jsonc` + `input.example.json` + READMEs; add `customer/NOTICE.md`, `customer/designs/README.md`, and a root `CLAUDE.md` so every session knows `customer/` is the user's empty working area and `examples/contoso/` is the sample. Repoint docs (`manifests/README.md`, `docs/az-taxonomy-pipeline.md`, `docs/epac-assembler-design.md`). See plan Parts B/D | high | done (2026-07-05) | Karel, 2026-07-04 |
| 11 | Contoso CI + native start-check: after #10, add `examples/contoso/verify.sh` (build + full-tree `diff -rq`, the pipeline logic living with the example) invoked by a thin `.github/workflows/contoso-epac-build.yml` (name `contoso epac build`; `paths:` on `flows/**` + `catalogue/**` + `examples/contoso/**` so it fires on either builder changing — GH Actions requires the YAML under `.github/workflows/`, so logic lives in the example, trigger lives at root); and make `epac-builder-start`'s health check build from the **current** `customer/` inputs (dynamic) rather than the frozen fixture, reporting "not configured" on an empty scaffold. Consumer/example half of CI — pairs with #8 (producer half). Depends on #10 | medium | done (2026-07-05) | Karel, 2026-07-04 |
| 13 | Terraform/Bicep renderers have **zero regression coverage**: CI (`test.yml`) builds only the default (json) flavour and diffs it; `render_terraform`+`hcl` and `render_bicep` are exercised by no test, so a silent regression in either ships undetected. Extend the golden fixture to a `--only json,terraform,bicep` build + full-tree `diff -rq` (commit the two extra flavour trees as fixtures, or fold into #11's `verify.sh`). Both flavours verified working by hand on 2026-07-05 — this is coverage, not a bug | low | done (2026-07-05) | actions/log/review-07-05-26.md |
| 12 | Convert `catalogue-builder/plan/catalogue-builder.md` (the 5-phase producer runbook) into a slash command `.claude/commands/catalogue-builder-run.md` — a single run command executing phases 1–5, mirroring `epac-builder-start.md`'s frontmatter (`description`, `disable-model-invocation: true`). Fix on the way: (a) replace all hard-coded absolute script paths (`C:\GIT\…\<script>.py` in Phases 1/3/4/5) with repo-relative `python flows/…` invocations; (b) rewrite Phase 1's "Authorized source folder" section (lines 52–59), which still names the personal `C:\GIT\Official Azure Policy\…` clone as the `--source` default — obsoleted by #5/#6; lead with `python flows/tools/fetch_policy_source.py --sync` + pinned-cache resolution (`flows/shared/paths.py::official_policy_source`) instead | medium | done (2026-07-05) | Karel, 2026-07-04 |
| 14 | **Contoso as the deployable reference customer** (real Azure tenant, end-to-end): today `contoso epac build` (#11/#13) only proves the assembler is **deterministic** (rebuild + byte-`diff`), NOT that the package is **deployable**. Establish contoso as the internal reference customer deployed against a real dev/sandbox tenant, adding the deployability layer the regression flow deliberately skips: (a) validate the generated EPAC/json package with the **EPAC PowerShell module** (`Build-DeploymentPlan` + `Deploy-*` in what-if), (b) prove the **generated GitHub / Azure DevOps pipeline** actually runs that plan/deploy (OIDC/service-principal auth), and optionally (c) `terraform validate/plan` + `az bicep build` for the other two flavours. Gives engineers a living, deployable reference — not just a byte-diff fixture. Needs a tenant + credentials; likely a separate opt-in workflow (secrets, not on every push). Distinct from the catalogue-upgrade path (#15) | high | in-progress (2026-07-07) | Karel, 2026-07-05 |
| 15 | **Customer-package lifecycle / catalogue-upgrade path**: the shared catalogue is versioned and bumped ~**monthly**; a customer package built + deployed at catalogue version X must be **re-generatable/migratable** to version Y without hand-editing — diff what changed between catalogue versions, re-assemble the customer's manifest against the new catalogue, and surface breaking changes (removed/renamed initiatives, new required params, role changes) for review before redeploy. Needed to keep already-implemented customer tenants current as the catalogue evolves. Use **contoso** as the test case (pairs with #14). Kernel of a future "customer package update" system; builds on the versioned catalogue (`catalogue.json` `version`/`contentHash`) and `lineage.json` provenance already emitted per package | high | todo | Karel, 2026-07-05 |
| 16 | **Consumer-onboarding skill** (`catalogue-builder/skills/epac-builder-onboarding-agent/`): a self-contained skill that walks a new engineer/developer/user through onboarding to EPAC Builder as a **consumer** — Explain (how the catalogue/EPAC builders fit, what the package contains) → Interview (collect every manifest input up front, no silent defaults; the concrete question set = `customer` + `selection` + one value per `<REPLACE:>` the `--input` expansion emits, incl. one per required policy param) → Generate (drive the real `assemble_scaffold.py` to fill `customer/` + render `customer/package/`) → Hand off. **Hard boundary: read-only on the engine** — only writes under `customer/`, never edits `flows/**`/`catalogue/**`/schemas/workflows, declines engine changes even if asked. Built 2026-07-05; SKILL.md + README shipped. Follow-ups: exercise it end-to-end against a fresh empty `customer/` (dry run) and reconcile with #14/#15 (deploy + upgrade layers it explicitly defers) | medium | done (2026-07-05) | Karel, 2026-07-05 |
| 17 | **Local MCP server (stdio)** over the builder working tree — expose the on-disk build/validate flows as MCP tools for conversational use: `validate_manifest`/`strict_check` (wrap `assemble_scaffold.py --check` / `--check --strict`; **highest value** — instant "every unfilled `<REPLACE:>` + every placeholder scope" feedback without shelling out), `assemble_scaffold` (full build → json/terraform/bicep + `report.md`/`lineage.json`), `expand_input` (tiny `input.json` → scaffolded manifest with `<REPLACE:>` seeded), `check_policy_source_drift` (`fetch_policy_source.py --check`), `diff_catalogues` (`catalogue_diff.py`), `generate_mg_hierarchy_svg` (plain-text mg-tree → SVG), and optionally the producer pipeline steps (extract/enrich/create-initiatives/apply-overlays/QC) as a **maintainer-only** surface. Anything that mutates a customer package or touches the filesystem lives here (one user, one working tree). **Caveat: decisions to settle before building — see Notes** (local/stdio has none of the HTTP hosting/auth/network/cost exposure) | medium | in-progress (2026-07-07) | Karel, 2026-07-06 |
| 19 | **Wire the MCP smoke test into CI**: `flows/mcp_server/test_server.sh` is green locally (5/5) but runs in **no** workflow — a silent regression in the stdio server or `validate_manifest` ships undetected (same untested-in-CI class as the old #13 renderer gap). Add a `bash flows/mcp_server/test_server.sh` step to `.github/workflows/contoso-epac-build.yml` (already fires on `flows/**`). Called out as a follow-up in #17's notes + the 2026-07-07 session log; promoting to its own row | low | done (2026-07-18) | actions/log/review-07-07-26.md |
| 18 | **HTTP MCP server (remote, read-only)** over the published catalogue artifact (`index.json` + `catalogue.json` + `initiatives/` + `definitions/` — a self-contained versioned artifact) — pure lookups exposable to consumers who never touch this repo (sales engineers, customers, other internal tools): `search_policies`/`lookup_policy_by_id` (keyword/GUID/resource-type → tier, category, effect, description), `get_initiative` (a domain/tier/category group's policy set, required params, usage guide), `explain_tier_rationale` (NIS2/ISO27001/CIS/NIST citation baked into `enrich_policies.py` output), `get_tier_description` (Essential/Professional/Enterprise product copy — good for a pre-sales chatbot), `get_catalogue_version` (version/hash/counts). No repo or filesystem access. **Caveat: MUST settle auth + hosting + network + recurring-cost decisions before building — see Notes** | high | todo | Karel, 2026-07-06 |
| 20 | **EPAC 11.x deploy-blocking renderer gaps (consumer what-if, Findings 1 & 3)**: `render_json.py` emits a package that passes the builder's **own** schema but is rejected by EPAC 11.4.7 at `Build-DeploymentPlans`. Two fixes. **(a)** `_write_global_settings` (render_json.py:50-68) emits **no `desiredState`** — add it **inside each `pacEnvironment`** with a **safe default `strategy:"ownedOnly"`** + `keepDfcSecurityAssignments:false`, and surface `strategy` (+ optional `excludedScopes`) as a **per-environment manifest field** (add to `environments[]` in `manifest.schema.json` **and** `manifest.input.schema.json`, thread through `_env` in `ir.py`, emit in the renderer) so greenfield can opt into `full` deliberately while brownfield stays safe by default. Brownfield safety is the sharp edge (Finding 3): where the field is optional EPAC defaults to destructive `full`, proposing deletion of a tenant's pre-existing ALZ/hand-made policy at/below root scope. **(b)** `_assignment` (render_json.py:80) emits flat `policySetDefinitionName`; EPAC 11.x expects `definitionEntry:{policySetName:…}` — convert (review terraform/bicep renderers for the same shape). Regenerating contoso fixtures required (byte-diff CI). First **real-tenant** validation feeding #14 | high | in-progress (2026-07-07) | actions/feedback/consumer-feedback-vandelabr-07-06-26.md |
| 21 | **Naming initiative hardcodes `customerAbbreviation:"dlw"` (consumer Finding 2)**: `management-esn-naming.policyset.json` bakes `{"value":"dlw"}` **162×** (only `effect` is a real initiative parameter), so the naming initiative audits every non-DLW customer (e.g. vandelabr) against a `dlw-*` anchor and can't be retargeted from the manifest. **Fix (parameterize from manifest):** promote `customerAbbreviation` to an initiative-level parameter (keep `defaultValue "dlw"` as safe fallback) bound from the existing manifest `prefix`. Producer/scaffold change — generalize `_bubbled_params` (scaffold.py:127-135), which special-cases only `effect`, to also bubble `customerAbbreviation` to `"[parameters('customerAbbreviation')]"` + add it to the initiative `parameters` block (~scaffold.py:212-227); `CUST_DEFAULT` at gen_dlw_naming_definitions.py:36 stays the default. Then **regenerate the catalogue** and wire the manifest binding (`bindings.defaults` / derive from `prefix`). Catalogue-regeneration fix, heavier than #20 | medium | todo | actions/feedback/consumer-feedback-vandelabr-07-06-26.md |
| 22 | **Producer catalogue assignment scaffolds use invalid top-level `policySetDefinitionName`**: the **188** `*.assignment.json` reference scaffolds under `catalogue/initiatives/**` all emit a top-level `policySetDefinitionName`; EPAC 11.x rejects that leaf shape (`each tree branch must define either a definitionEntry or a non-empty definitionEntryList`) and wants `definitionEntry:{policySetName,displayName}` — the same defect as #20(b) but in a **separate producer code path**. Emitters: `build_assignment` (create_initiatives.py:531) + `_new_group_assignment` (scaffold.py:245); keep `quality_control.py:183`'s reader consistent. Regenerate the catalogue after the fix. **Lower severity**: these scaffolds are **not** copied into customer packages (the assembler lifts only `nodeName`, ir.py:106), so they're reference/deployment-example artifacts — only a real problem if the catalogue scaffolds are meant to be directly EPAC-deployable. Producer task (`/catalogue-builder-run`) | low | todo | actions/feedback/consumer-feedback-demo-07-07-26.md |
| 23 | **Bundled package workflow isn't repo-root-discoverable**: `package.py` (`_epac_workflow`, package.py:43-131) writes `.github/workflows/{epac,terraform,bicep}.yml` **inside** the package dir with repo-root-relative paths (`DEFINITIONS: Definitions`, `paths: Definitions/**`). GitHub only discovers workflows at the **repo root**, and the paths assume the package *is* the repo root — so the bundled pipeline never fires when the package is dropped into an existing repo as a subfolder. Affects all three flavours. **Resolved by decision, not by code (Karel, 2026-07-20):** the package **is** the root of a dedicated customer deploy repo — this repo is never delivered to the customer, and the engineer building the package is expected to know where it lands. That makes the repo-root-relative paths *correct by contract*; no wrapper, no `DEFINITIONS` parameterization, no subfolder support. Fix was documentation: `_header` (package.py:266, shared by all three flavours) now states the rule at the top of every generated package README, so it travels with the artifact; `examples/contoso/README.md` gained a "Delivery boundary" section. Consumer's hand-written root `epac-demo.yml` was the workaround for the undocumented rule | medium | done (2026-07-20) | actions/feedback/consumer-feedback-demo-07-07-26.md |
| 24 | **Housekeeping: gitignore `Output/` + settle customer-package deploy location**: `customer/package/Output/` (EPAC plan artifact) is **not** gitignored (no `customer/.gitignore` exists) — a local `Build-DeploymentPlans` run would be committed; add an ignore rule. Separately decide whether a real deploy package belongs under `customer/` (diverges from the "empty scaffold; sample in `examples/contoso/`" convention) or as its own example / dedicated deploy repo. Note `*.manifest.jsonc` is already ignored (`customer/manifests/.gitignore:5-6`), so a committed demo carries `demo.input.json` + rendered `package/` but not its manifest — confirm that's acceptable | low | done (2026-07-09) | actions/feedback/consumer-feedback-demo-07-07-26.md |
| 25 | **Move the historical prototype tree `product/lab/` to the repo root (`lab/`)**: it's self-contained (`lab-01…lab-11`, incl. `lab-11`'s own private pipeline copy) with **no** ties into the active `catalogue-builder/`, so this is a clean `git mv product/lab lab`. Only **five** external doc lines reference the old path and need updating (`CLAUDE.md:4`, `AGENTS.md:19`, `foundry/README.md:3`, `foundry/architecture.md:5` + `:165`). No active-CI / `.gitignore` / `.claude/` entanglement; `product/` survives the move (keeps `descriptions/` + `developmentjourney/`, and `product/descriptions/` is referenced by `foundry/`). Optional tidy-up: ~54 stale internal absolute `C:\GIT\…\product\lab\…` paths baked into dead prototype scripts/plans would dangle after the move but nothing runs them | low | done (2026-07-07) | Karel, 2026-07-07 |
| 26 | **Producer Phase 3 (`create_initiatives.py`) is additive — no garbage collection of moved/removed groups**: the script writes `(domain,tier,category)` group dirs (`create_initiatives.py:723`, `mkdir(parents=True, exist_ok=True)`) but never prunes groups that move or disappear, so reclassifying a category (or any domain/tier/category change) leaves the old `initiatives/<olddomain>/…` dir orphaned on disk. **The orphan is silent but poisons the catalogue stamp**, because the two artifacts are derived from different universes: `index.json[groups]` is built from the *in-memory* record list parsed from the enriched markdown (`create_initiatives.py:620-638`), while `contentHash` is built by `rglob("*")` over `catalogue/` *on disk* (`apply_overlays.py:72-80`, call site `:145`). So a stale dir is invisible to `index.json`, to `catalogue.json` `counts`, and to every QC check — `quality_control.py`'s `unregistered-custom-group` (`:296-305`) is gated on `it.get("custom")`, so a stale **built-in** group dir is skipped outright, and there is no reverse `index.json[groups][*].dir` → disk check anywhere. Phase 5 passes green with a wrong `contentHash`, deterministically (so it never flaps), and `catalogue_diff.py:160` will later report drift between two semantically identical catalogues. Discovered doing #3: moving **11 categories** (17 policysets) out of `undefined` left stale `undefined/**` dirs (25 policysets on disk vs 8 in `index.json`); worked around by manually wiping `catalogue/initiatives/` before re-running Phases 3→4→5. **Fix — the pattern already exists in-tree**: `apply_overlays.py:120-128` does exactly this prune for `definitions/custom/<family>` ("so a disabled generator … leaves no orphaned definitions behind"); the same reasoning was simply never applied to `initiatives/`. Mirror it in `create_initiatives.py` (clear, or diff-and-prune, its output tree at the start of a run) so a regenerate is self-cleaning. Fix **before the next catalogue regeneration**. Producer task | low | todo | discovered building #3, 2026-07-19 |
| 27 | **Versioning & branching strategy — blocks Alpha exit** (decision spike, not code): **three things version independently and only one of them is stamped.** (a) *Catalogue artifact* — `catalogueVersion` (`2026.07.18`) + `contentHash`; works, and is the one thing enforced (`assemble_scaffold.py:107-111` fails the build on a mismatch). (b) *Taxonomy/hierarchy inputs* — `catalogue.json` `inputs.hierarchyHash` / `tierRulesHash` / `definitionGensHash`; the hashes move correctly but **nothing propagates them to consumers**. (c) *Engine (epac-builder itself)* — `pyproject.toml` is still `version = "0.0.0"`, so the `tools.*` hashes in `catalogue.json` are the only de-facto engine fingerprint. **Evidence this is already biting:** `hierarchyVersion` is **inert** — declared in `manifest.schema.json:53-55` as "Domain hierarchy snapshot id (lineage)", written by `expand.py:52` as the literal `<REPLACE: hierarchy-snapshot-id>`, and read by **no code at all**; #3 changed the hierarchy and moved `inputs.hierarchyHash`, yet `examples/contoso/manifests/manifest.example.jsonc:15` still pins `2026.06.21`, the only remaining `2026.06.21` string in the active tree. `lineage.json` — the provenance artifact that **ships to the customer** — records only `catalogueVersion`: not `contentHash`, not `builtInsRef`, not `hierarchyVersion`, not any engine version, so a customer holding an epac-package cannot tell which builder produced it or which upstream Azure Policy commit it came from. And `tools.extract` / `tools.createInitiatives` moved in `82dc38f`, a commit that changed **no** Python — absorbed from `da93bad`, which landed after the previous regeneration in `44ce852`; provenance moved for a reason the record can't explain, precisely because there's no engine version to pin against. **Open questions to settle:** does the hierarchy get its own version or inherit the catalogue's? Does a git branch map to a catalogue version, an engine version, or both? What single identifier does a customer quote in a support conversation? Recurring monthly upstream sync (`config/policy-source.json` pinned at `04989912`, fetched 2026-07-04) makes this recur. Split implementation rows off once the model is chosen | high | todo | actions/log/review-07-20-26.md |
| 28 | **Real customer manifests carry tenant identifiers into a public repo**: #24 dropped the `*.manifest.jsonc` ignore from `customer/manifests/.gitignore` and `customer/NOTICE.md` + `customer/manifests/README.md` now instruct users to commit the manifest "for provenance" — but an expanded `<customer>.manifest.jsonc` carries `tenantId`, `pacOwnerId`, `deploymentRootScope` (root management-group resource id) and `logAnalyticsWorkspaceId` (`expand.py:47-62`). In a public repo, a consumer following that guidance publishes their tenant GUID, root MG id and workspace resource id. The deploy-location decision itself (#24) was settled deliberately and stands; **this row is about *where* that rule applies** — decide whether real customer manifests belong in this public repo at all, or whether committable-provenance should hold only inside a customer's own private deploy repo. If they stay, name the exposed identifiers explicitly in `NOTICE.md`/`README.md` so the choice is informed | medium | todo | actions/log/review-07-20-26.md |
| 29 | **QC sample tables churn and lose domain coverage on any catalogue change**: `quality_control.py:73-83` `spread()` picks evenly spaced **indices** from a positionally ordered list, so inserting the 17 relocated policysets in #3 reshuffled every sample row rather than just the affected ones. Net effect in the regenerated `catalogue/naming-samples.md:104-116` and `docs/epac-naming-convention.md:101-113`: **Data** now appears twice (`data-ent-sql`, `data-pro-hapi`), **Security** dropped out entirely, and the `undefined-esn-ehc` row that illustrated the catch-bucket is gone — while `undefined` still holds 8 policysets. Both docs claim to show "a representative spread", and both are auto-generated, so the churn recurs on every catalogue change and pollutes the diff. Fix direction: sample **one per domain** (or otherwise key the selection to the taxonomy) instead of by list position | low | todo | actions/log/review-07-20-26.md |
| 30 | **MCP smoke test crashes with a traceback instead of a clean FAIL**: `flows/mcp_server/test_server.sh:55-95` indexes `resp[1]`…`resp[5]` directly, so a server that dies after `initialize` — or returns a JSON-RPC error object with no `"result"` — raises `KeyError: 2` and prints a bare Python traceback pointing at the test harness rather than the script's own `[test] FAIL: …` message. The script already defines `fail()` and already handles the non-JSON/protocol-contamination case, so this is an inconsistent gap rather than a design choice. Now CI-facing via #19 (`contoso-epac-build.yml:48`), where a legible failure message is the entire point. Fix: look the id up with `.get()` and `fail()` with "no response for id N" when absent | low | todo | actions/log/review-07-20-26.md |
| 31 | **Front end for package creation (mid/long-term product goal)**: today the only way to produce a customer epac-package is to clone this repo and drive `assemble_scaffold.py` — via the CLI, or conversationally through the onboarding skill (#16). That gates delivery on an engineer with a working tree, and it is the wrong shape for the delivery boundary settled in #23: **the customer never receives this repo, only the rendered package.** Goal: a proper front end where an engineer (and eventually a customer directly) fills the manifest inputs and gets a package out, without cloning anything. **Interaction model already proven by #16** — Explain → Interview (every input up front, no silent defaults, one question per `<REPLACE:>`) → Generate → Hand off; the front end is that flow with a real UI instead of a chat transcript, and the same hard boundary (read-only on the engine; only ever writes a package). **Read side already scoped as #18** — the HTTP MCP server over the published catalogue artifact is exactly the lookup API such a front end needs (search policies, get initiative, explain tier rationale), and was already framed for "consumers who never touch this repo". **Hard dependency on #27**: a front end that emits packages to people outside this repo is unshippable until the engine and catalogue carry real versions to stamp into `lineage.json` — otherwise nobody can answer "which builder produced this package?". Open questions: who hosts and authenticates it; does it render server-side or hand back a manifest for a pipeline to build; does the customer get the package as a repo, a zip, or a PR into their deploy repo. Decision spike before any build; sequence after #27 and #18 | high | todo | Karel, 2026-07-20 |

## Notes

- Item 1's CI workflow diffs everything the assembler actually computes
  (`Definitions/`, `lineage.json`, `report.md`, `README.md`, `.github/workflows/epac.yml`
  inside the generated package). As of #4 (done 2026-07-04) `docs/` is now included too —
  the SVG was already in sync, so the `-x docs` exclusion was dropped.
- Item 1b (done 2026-07-05) needed no code change: `.gitignore` already carried the Python
  bytecode section (`__pycache__/`, `*.py[cod]`, `*.pyo` — added in `15d14fa`, reinforced in
  `9cfe57e`) and nothing matching was tracked; the physical `__pycache__/` dirs on disk are
  already ignored. Item 1a shipped `catalogue-builder/pyproject.toml`, a declarative
  `[project]` marker with empty `dependencies` making the stdlib-only design explicit (no
  `[build-system]` — not a pip-installable package).
- Item 5 was split out of the review's original #3 ("decouple producer from hard-coded
  path") once the code was checked — it's a two-file default-value fix, not a curation
  task, so it's tracked and estimated separately from the catalogue-cleanup work.
- Item 9 (done 2026-07-05): the premises were stale. The branch was **already pushed and
  tracked** (`origin/alpha/epac-builder/actions`, up through `9cfe57e`) and **Actions was
  already enabled and had run green twice** (`09570bd`, `9cfe57e` on 2026-07-03). Pushed the
  3 pending commits (through `74907e4`); the resulting `epac-builder regression test` run
  passed (`success`). Confirmed via the public REST API (`/actions/runs`) — `gh` is not
  installed locally. The `contoso epac build` half of #9's ask stays N/A until #11 builds
  that workflow. Net effect: CI is live and green; #7/#8/#11 now have a working Actions
  environment to run in.
- Item 12 (done 2026-07-05): `git mv`'d the runbook `catalogue-builder/plan/catalogue-builder.md`
  → `.claude/commands/catalogue-builder-run.md` (the now-empty `plan/` dir is gone). Added the
  `epac-builder-start`-style frontmatter (`description` + `disable-model-invocation: true`) and a
  run preamble (all phases run from `catalogue-builder/`, stop on any non-zero script). Replaced the
  4 absolute `C:\GIT\…\<script>.py` paths (Phases 1/3/4/5) with repo-relative `python flows/…` fenced
  blocks; rewrote Phase 1's source section to lead with `fetch_policy_source.py --sync` + pinned-cache
  resolution (`config/policy-source.json` → `flows/shared/paths.py::official_policy_source`), dropping
  the personal-clone `--source` default. Also flattened the 3 `../`-relative markdown links (they
  pointed relative to the old `plan/` location) to plain catalogue-builder-relative inline paths.
- Item 10 (done 2026-07-05): `git mv`'d the worked sample to
  `catalogue-builder/examples/contoso/{manifests/,designs/,package/}` — layout **mirrors**
  `customer/` so `package.py` (`manifest.parents[1]/designs`) and the fixed-location schema
  loader need **no code change**; only the example manifest's `source.initiatives` gained one
  `../` for the extra depth. `customer/` now ships as an empty scaffold (schemas + template +
  `input.example.json` + READMEs + empty `designs/`); the `package/` there only appears on
  build. Added root `CLAUDE.md`, `customer/NOTICE.md`, `customer/designs/README.md`,
  `examples/contoso/README.md`. Repointed the worked-example references only (CI `test.yml`,
  `epac-builder-start` health check, `customer/manifests/README.md`, `epac-assembler-design.md`);
  the many *generic* `customer/package/` mentions (the template's default `output.root`) are
  still correct and were left. `az-taxonomy-pipeline.md` had no such references. Verified: the
  example rebuilds **byte-identical** to the committed fixture. Note the fixture files carry a
  new `manifestHash` (the example manifest changed), so `lineage.json`/`report.md` were
  regenerated. Consumer-side CI restructure (verify.sh + renamed workflow) + dynamic health
  check remain **#11**; for now `test.yml` and the health check just point at the new location.
- Review 2026-07-05 (`actions/log/review-07-05-26.md`) reconciled: confirmed #1/#1a/#1b/#4/#5/#6/#9/#10/#12
  done (re-ran the assembler; `examples/contoso` rebuilds byte-identical, all 3 flavours render).
  #2 (strict gate) and #3 (catalogue still ships `undefined` + `builtinpolicytest`) carry forward
  unchanged. One new row: #13 (Terraform/Bicep renderers uncovered by CI).
- Item 11 + 13 (done 2026-07-05, together): added `examples/contoso/verify.sh` — the pipeline
  logic living with the example. It rebuilds the worked sample for **every** flavour and diffs
  byte-for-byte: json → `examples/contoso/package/`, terraform → `examples/contoso/fixtures/terraform/`,
  bicep → `examples/contoso/fixtures/bicep/`. Chose **separate flavour fixtures** (over one 3-flavour
  sub-foldered `package/`) so the worked sample stays a realistic single-flavour json deploy; the two
  new trees are pure regression fixtures (that's #13's coverage — terraform/bicep were previously
  exercised by no test). New thin `.github/workflows/contoso-epac-build.yml` (name `contoso epac
  build`) just calls `bash examples/contoso/verify.sh`; `paths:` fires on `flows/**` + `catalogue/**`
  + `examples/contoso/**` + `customer/manifests/**` (shared schemas). **Deleted `test.yml`** — folded
  into the new workflow (verify.sh is a superset of its single-json diff). Made `epac-builder-start`'s
  health check **dynamic**: engine baseline via `verify.sh` (always), then customer-readiness on live
  `customer/` inputs (`--check` a filled manifest; report "empty scaffold — not configured" when only
  the template/placeholders exist). Repointed all *current-state* `test.yml` references (root
  `CLAUDE.md`, `examples/contoso/README.md`, `customer/NOTICE.md`, `pyproject.toml`, `actions/README.md`,
  backlog #8); historical session-log mentions left as-is. verify.sh passes green locally on all three
  flavours (fixtures confirmed deterministic across two builds).
- Review 2026-07-05 (end-of-day, second pass, `actions/log/review-07-05-26.md` rewritten): re-ran
  `examples/contoso/verify.sh` — all three flavours byte-identical (exit 0). Confirmed **#11 and #13
  done** (verify.sh now covers json+terraform+bicep; the morning review had raised #13 as the renderer
  coverage gap — closed same day) and **#16 done** (onboarding skill + `/epac-builder-onboard` +
  `/reset-customer-package` shipped). No status flips (all already marked done) and **no new rows** —
  every finding maps to an existing item. Re-confirmed **open**: #2 (scope-less/`<REPLACE:>`-param
  manifests still build with only a `[warn]`), #3 (`undefined`-domain refs still in `index.json`;
  `builtinpolicytest` still in `definitions/` + two `initiatives/undefined/*/` dirs), #14 (deployability
  never proven — CI is byte-diff only), #15 (no catalogue-upgrade path). #14/#15 are now the two
  highest-value open items.
- Item 2 (done 2026-07-06): added the `--strict` deploy-ready gate. New
  `flows/epac_builder/strict.py` (`residual_placeholders` + `StrictGateError`); `assemble()` gained a
  `strict=` param and the CLI a `--strict` flag, checked right after IR-build so **both `--check` and a
  full build honour it**. It fails listing every surviving `<REPLACE: …>` in the manifest (recursive
  walk — values *and* placeholder dict keys) **plus** any assignment that fell back to
  `PLACEHOLDER_SCOPE` (the previously warn-only no-managementGroup/scope case). The **schema build-gate
  still catches the four pattern-constrained placeholders first** (`prefix`, `tenantId`,
  `deploymentRootScope`, `enforcement`); `--strict`'s unique value is the *free-string* fields the
  schema structurally can't (`selector`, `managedIdentityLocation`, `logAnalyticsWorkspaceId`,
  `hierarchyVersion`, `allowedLocations`, `notScopes`, `bindings.defaults` param values, `metadata`) —
  verified it lists all 12 on a half-filled manifest. Default (non-strict) path **unchanged**
  (`verify.sh` still byte-identical on all 3 flavours). Wired the gate into the docs/flows that
  represent "deploy-ready": onboarding SKILL step 5 + `epac-builder-start` health check now run
  `--check --strict`; `customer/manifests/README.md` gained a strict pre-build check step. Added a
  **regression guard to `verify.sh`**: contoso's intentionally-unmapped `management/essential/tags`
  selection means `--check --strict` must exit non-zero — CI now asserts the gate fires. This is the
  guardrail the reverted template-GUID slip (2026-07-05) called for.
- Items 17–18 came from an **MCP-exposure brainstorm** (Karel + Claude, 2026-07-06) — **not** an
  `actions/log/` code review. Dividing line: anything that **mutates a customer package or touches the
  filesystem** → **local/stdio** (#17: one user, one working tree); a **pure lookup against the
  published, versioned catalogue** → **HTTP** (#18: multiple consumers, no repo access at all).
  **Before building any tool/resource in either item, the relevant decisions below MUST be
  discussed and decided first — do not assume or silently default them:**
  - **Authentication** — API key vs OAuth, single-tenant vs multi-customer access *(HTTP only)*
  - **HTTP hosting infrastructure & design** — where it runs, how the catalogue gets
    published/refreshed to it, single instance vs per-environment
  - **Network/firewall** — public endpoint vs VNet-restricted; who needs to reach it
  - **Recurring/operational cost vs one-time build effort, and who owns running it**

  These apply **mainly to #18 (HTTP)**; local/stdio #17 has none of the hosting/auth/network/
  recurring-cost exposure. The caveat lives inline in the row, so it travels with the item
  whenever the backlog is read — no separate reminder needed.
- Item 17 (in-progress 2026-07-07): first tool **`validate_manifest`** landed. New stdlib-only
  package `flows/mcp_server/` — a **hand-rolled** MCP stdio server (JSON-RPC 2.0 over
  newline-delimited stdin/stdout: `initialize`/`tools/list`/`tools/call`/`ping` + a tool registry),
  **no `mcp` PyPI SDK** (keeps `dependencies = []`). The one tool imports the engine (no shell-out)
  and returns **structured** JSON: `assemble(check=True, strict=…)` → `{valid, initiativesResolved,
  warnings, note}` on success, or `{valid:false, errors|strictProblems|error}` on failure. Design:
  a *validation failure* is a normal result (`isError:false`, `valid:false` + problem list);
  `isError:true` only for real tool failures (bad path, crash). **Read-only**: threaded a
  `write_back=True` default through `resolve_pac_owner_id`/`load_manifest`/`assemble` so the tool
  (`write_back=False`) never triggers the CLI's `pacOwnerId` write-back — surfaces a note instead.
  CLI defaults unchanged → `verify.sh` still byte-identical on all 3 flavours. Verified: smoke test
  `flows/mcp_server/test_server.sh` (5/5 — initialize, list, `--check` valid, strict gate fires on
  contoso's unmapped `tags`, bad-path error), no-mutation probe (invalid pacOwnerId left untouched),
  cwd-independent (paths resolve against the catalogue-builder root). Registered for Claude Code via
  root `.mcp.json`. **Remaining #17**: the other five local tools drop into `tools/` against the same
  registry; wire `test_server.sh` into `contoso-epac-build.yml` (kept standalone for the alpha).
- Review 2026-07-07 (`actions/log/review-07-07-26.md`) reconciled: re-ran `examples/contoso/verify.sh` (all
  3 flavours byte-identical + strict-gate regression, exit 0), the MCP smoke test (`test_server.sh`
  5/5), and `check_env.py` (exit 0). **Confirmed done:** #2 (strict gate — verified the `--strict`
  gate fires in CI on contoso's unmapped `tags`). **In-progress:** #17 (`validate_manifest` landed;
  five local tools remain). **Re-confirmed open:** #3 (`index.json` still carries 25 `undefined`
  refs; `builtinpolicytest` still in `definitions/` + two `initiatives/undefined/*/` dirs), plus
  #7/#8/#14/#15. With #2 closed, **#3 is now the top product blocker** and #14/#15 remain the two
  highest-value tenant-dependent items. One new row: **#19** (wire the MCP smoke test into CI —
  currently untested-in-CI). Watch item (no row): `.mcp.json` hard-codes `python`; `check_env.py`
  detects but can't fix the `python`/`python3` mismatch — first cross-machine approval will tell.
- Consumer feedback triage (2026-07-07): a consumer ran a real onboarding dry-run — customer
  `vandelabr` (`networking/essential/network` + `management/essential/tags` +
  `management/essential/naming`), built with `assemble_scaffold.py`, then EPAC
  `Build-DeploymentPlans` (what-if) on **EnterprisePolicyAsCode 11.4.7** against a demo tenant. The
  feedback log (`actions/feedback/consumer-feedback-vandelabr-07-06-26.md`) was cross-checked here and **all three
  findings confirmed against the code**: `_write_global_settings` (render_json.py:50-68) emits no
  `desiredState` and `strategy`/`ownedOnly`/`keepDfcSecurityAssignments`/`excludedScopes` exist nowhere
  in `flows/**`/`config/**`/schemas; `_assignment` (render_json.py:80) emits flat
  `policySetDefinitionName`; the naming policyset bakes `{"value":"dlw"}` **162×** (only `effect` is a
  real initiative param), origin `CUST_DEFAULT="dlw"` (gen_dlw_naming_definitions.py:36) +
  `_bubbled_params` special-casing only `effect` (scaffold.py:127-135). Split into two rows: **#20**
  (renderer, deploy-blocking; findings 1 & 3 share the same missing-`desiredState` root cause) and
  **#21** (naming producer). **#20 is the first validation of the builder's output against the real
  EPAC engine on a live tenant** — it partially exercises the long-open deployability gap (#14), and
  executing it must include **regenerating the contoso golden fixtures** (any `render_json.py` output
  change breaks the byte-diff CI). The consumer only hand-patched the generated package to complete the
  what-if; those patches are wiped on rebuild, so the durable fix belongs in the engine.
- Demo deploy exercise triage (2026-07-07, `actions/feedback/consumer-feedback-demo-07-07-26.md`): a consumer built a
  `demo`-prefix package (`management/essential/tags` + `naming`) on a company machine and, on the Azure
  **demo** tenant (`89ee4175-…`, `Demo` MG), **proved it deployable** — a live `Build-DeploymentPlans` on
  **EPAC 11.4.7** produced 169 defs + 2 sets + 2 assignments, all *New*, no role changes, and GitHub OIDC
  was wired (3 SPNs with roles at `Demo` MG + corrected federated creds). This **corroborates and advances**
  round 1: the consumer **implemented the #20 renderer fixes** (`desiredState.strategy="ownedOnly"` +
  `keepDfcSecurityAssignments:false`; top-level `policySetDefinitionName` → `definitionEntry.policySetName`)
  and confirmed they make EPAC accept the package. **Those fixes are uncommitted on `alpha/epac-builder/demo`
  (another device), not in this line** — so **#20 → in-progress** (remaining: land the diff here + regenerate
  contoso fixtures + decide manifest-driven vs hardcoded `desiredState`) and **#14 → in-progress** (first real
  deployability proof; caveats: vehicle was `demo` not `contoso`, the generated pipeline hasn't actually run,
  the MG is empty so nothing is evaluated yet, tf/bicep unvalidated). Three new rows split out from the log,
  all verified against the code here: **#22** (188 catalogue `*.assignment.json` scaffolds carry the same bad
  `policySetDefinitionName`, a separate producer path — but *not* copied into customer packages, so low
  severity), **#23** (bundled `package.py` workflow uses repo-root-relative paths and lives in a subfolder GH
  never scans → never runs), **#24** (`customer/package/Output/` not gitignored + customer-package location
  convention). Note the consumer's estimate of "≈98" catalogue scaffolds — actual count is **188**.
- Item 24 (done 2026-07-09): two parts, both settled with Karel. **(a) gitignore** — added a
  repo-root rule `**/package/Output/` (not a `customer/`-only ignore): EPAC's
  `Build-DeploymentPlans -OutputFolder Output` writes `<package>/Output/` on any local plan run,
  so this covers `customer/package/Output/` **and** `examples/contoso/package/Output/` (a local
  plan there would otherwise break the golden-fixture byte-diff). Verified via `git check-ignore`:
  both package `Output/` dirs ignored; the contoso fixture files and lab's lowercase `output/`
  untouched. **(b) deploy-location decision** — Karel chose: a real (non-sample) deploy package
  **may be committed under `customer/`** (customer/ still *ships* empty; contoso stays the
  `examples/` fixture), **and** its manifest must be committed for provenance. So **dropped** the
  blanket `*.manifest.jsonc`/`*.manifest.json` ignore in `customer/manifests/.gitignore` — it
  singled the manifest out from its already-committable siblings (`input.json`, rendered
  `package/`); now all three commit together. Scratch `--check` manifests just show as untracked.
  Reconciled the docs that claimed the manifest is gitignored / customer/ is strictly empty:
  `customer/manifests/README.md` (the note + flow diagram), `customer/NOTICE.md` (new "Committing
  a real deploy package here" section), root `CLAUDE.md` (customer/ blurb). Docs + gitignore only —
  no engine/renderer change, so `verify.sh`/byte-diff CI unaffected.
- Item 19 (done 2026-07-18): added an **MCP stdio server smoke test** step to
  `.github/workflows/contoso-epac-build.yml` — `bash flows/mcp_server/test_server.sh`, right after
  the `verify.sh` flavour-diff step (same `working-directory: catalogue-builder`; `python` on PATH
  via `setup-python@v5`). No `paths:` change needed — the workflow already fires on `flows/**`,
  which covers `flows/mcp_server/**`. Updated the workflow header comment to mention the new step.
  Verified the script green locally (5/5). Closes the untested-in-CI gap #17's notes + the
  2026-07-07 session log flagged; the MCP server now regresses loudly.
- Item 3 (done 2026-07-19): kept the `undefined` domain as a deliberate **catch bucket** (its
  mechanism + consumer hard-exclude unchanged, per Karel) and **reclassified the 11 categories (17
  policysets) that genuinely belong to a real domain** by moving their lines in
  `config/azure-domain-hierachy.md`:
  → **Security** (Privileged Identity Management, VirtualEnclaves), **Integration** (Internet of
  Things, Maps), **Compute** (Azure Edge Hardware Center, Azure Stack Edge), **Data** (API for
  FHIR, Healthcare APIs, Health Data Services workspace, Health Deidentification Service, Planetary
  Computer). `BuiltInPolicyTest`, `audit`, `Mission`, `MissionPlatforms` stay parked in undefined.
  Regenerated the catalogue via the producer (Phases 3→4→5) — `undefined/` shrank **25 → 8**
  policysets; 72 files relocated; `index.json` `domainMap`, `catalogue.json` `contentHash`, 11
  `definitions/*/policies.md` Domain columns, and the QC docs updated. Catalogue **version bumped
  2026.06.21 → 2026.07.18** (expected: any catalogue change bumps the version); re-pinned contoso's
  `manifest.example.jsonc` `catalogueVersion` to match and **regenerated all 3 contoso fixtures**.
  Verified: QC 188/188 (0 errors), `verify.sh` green (json/tf/bicep byte-identical + strict gate),
  MCP smoke test 5/5; every modified initiative file differs only by the `catalogueVersion` stamp
  (0 content drift). Hit the **Phase-3 orphan bug** (create_initiatives is additive) — worked around
  with a clean `initiatives/` wipe before regenerating; logged as new row **#26**. Also fixed a
  runbook drift found here: `catalogue-builder-run.md` documented `fetch_policy_source.py --sync`,
  but `--sync` is not a defined flag (sync is the argparse default) — the command as written exits
  non-zero and would halt a fresh `/catalogue-builder-run` at Phase 1 before syncing the source.
- Items 27–30 (opened 2026-07-20): from a `/code-review` pass over the 2026-07-19 session's five
  commits (`d0d0cef`..`adb5427`). **The reclassification itself verified clean** — all 72 files moved
  symmetrically, `index.json` consistent with disk (188 groups, no duplicate names/dirs, no orphans
  either direction), relocated initiatives internally coherent (`name` / `displayName` /
  `policySetDefinitionName` / exemption `policyAssignmentId` all renamed together). What the review
  surfaced instead was a **provenance-and-versioning gap** (**#27**, the one that blocks Alpha exit:
  `hierarchyVersion` is a lineage field nothing writes and nothing reads, and `lineage.json` ships to
  the customer carrying only `catalogueVersion`), plus **#28** (the #24 commit-the-manifest rule
  publishes tenant identifiers in a public repo — the deploy-location decision stands, the question is
  *where* the rule applies), **#29** (auto-generated QC sample tables churn and lost a whole domain),
  and **#30** (the newly-CI-facing MCP smoke test crashes instead of failing legibly).
- On **#26**, checked specifically whether the additive/no-GC behaviour had been settled deliberately
  earlier: **it had not.** Every mention of orphans/wiping/GC anywhere in `actions/` (backlog,
  `sessions/`, `log/`, `feedback/`) or the docs is dated 2026-07-19 or later; it was hit at runtime
  mid-session. The *prior* written position
  was the opposite and stronger claim — `flows/catalogue_builder/README.md:9` said each producer step
  "is idempotent", and `actions/log/review-07-07-26.md:60` called #3 "Data curation, **not a code fix**". Row
  #26 disproved both. Qualified the README claim and added the Phase-3 caveat to
  `.claude/commands/catalogue-builder-run.md` on 2026-07-20 so the trap is visible in the runbook the
  phase is actually executed from (it was recorded only in the session log + backlog before).
- Doc corrections applied 2026-07-20 alongside the above: the `contoso-epac-build.yml` header credited
  `verify.sh` with running the MCP smoke test (the *workflow* runs it, as a separate step); and
  "reclassified the **17 categories**" was wrong in three places — the enumerated list has **11**
  categories, 17 is the **policyset** count (undefined shrank 25 → 8), since several categories span
  two or three tiers.
- Item 23 (done 2026-07-20) — **closed by decision, not by code.** Karel: the engineers building an
  epac-package are expected to know where it lands on the customer side, and **it is never the
  intention to ship this repo to the customer** — only the rendered `package/` crosses, published at
  the *top level* of a dedicated customer deploy repo. That makes the bundled workflow's
  repo-root-relative paths (`DEFINITIONS: Definitions`, `paths: Definitions/**`) **correct by
  contract**, so the competing options in the original row — a root-level wrapper, or parameterizing
  `DEFINITIONS` + the `paths:` filter for a subfolder deploy — are explicitly **not** being built.
  The real defect was that the rule was tacit: the generated package README said only "Commit this
  folder to your DevOps/GitHub repo", which reads as "drop it in as a subfolder" — exactly the case
  where GitHub never discovers the workflow, and exactly what drove the demo consumer to hand-write a
  root `epac-demo.yml`. Fixed in the **generator** so the instruction travels with the artifact:
  `_header` (package.py:266) is shared by all three flavours, so one edit covers epac/terraform/bicep.
  Added a "Delivery boundary" section to `examples/contoso/README.md`. Regenerated all three contoso
  trees; the only diff is the three package READMEs (byte-diff CI confirms nothing else moved).
- Item 31 (opened 2026-07-20): the **front end** is a mid/long-term product goal Karel has been
  carrying that had **no row at all** — worth recording that the gap was real, not just unwritten.
  The nearest existing items each stop short: #16 (done) is the interaction model but runs as a chat
  against a local clone; #17 is maintainer-facing stdio MCP over the working tree; #18 is a
  **read-only** catalogue lookup API — already framed for "consumers who never touch this repo",
  which is the same delivery-boundary instinct as #23, just applied to reads. None of them let
  someone *produce* a package without cloning. Sequenced after **#27** (a front end that emits
  packages to people outside this repo cannot ship until `lineage.json` can answer "which builder
  produced this?") and **#18** (its read side).
- Re-run `actions/review-prompt.md` periodically; reconcile new findings into this table.
