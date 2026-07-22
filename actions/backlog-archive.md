# Backlog — archive

Closed items moved out of `actions/backlog.md` to keep the working table lean. Rows are kept
**verbatim with their original `#`** — ids are permanent references (cited from `actions/reviews/` reviews and
`actions/sessions/`), so nothing here is ever renumbered or deleted. Grouped by the date they were
archived. Populated by `/backlog-archive`.

## Archived 2026-07-20

| # | Item | Effort | Status | Source |
|---|---|---|---|---|
| 1 | Test suite / CI on the builder (golden-fixture diff against `customer/package/`) | low | done (2026-07-03) | actions/reviews/review-07-03-26.md |
| 1a | Add `requirements.txt`/`pyproject.toml` marker (stdlib-only, but make it explicit) | low | done (2026-07-05) | actions/reviews/review-07-03-26.md |
| 1b | Drop committed `__pycache__`, add to `.gitignore` | low | done (2026-07-05) | actions/reviews/review-07-03-26.md |
| 2 | Manifest completion guardrail: `--strict`/pre-deploy gate that fails when any `<REPLACE:>` or placeholder-scope survives into output | medium | done (2026-07-06) | actions/reviews/review-07-03-26.md |
| 3 | Catalogue customer-clean: resolve/remove `undefined`-domain policies, drop `builtinpolicytest` so the catalogue can be regenerated reproducibly | high | done (2026-07-19) | actions/reviews/review-07-03-26.md |
| 4 | `customer/package/docs/*.svg` is stale vs. `customer/designs/*.svg` (byte-diff, same commit) — CI's golden-fixture diff excludes `docs/` because of this; resync so the exclusion can be dropped | low | done (2026-07-04) | discovered building CI, 2026-07-03 |
| 5 | Producer's `--source` default is hard-coded to a local clone path (`C:\GIT\Official Azure Policy\...`) — breaks for anyone but Karel running without `--source`. In `extract_policies.py` (`DEFAULT_SOURCE`, ~line 270; docstring line 17; argparse default line 292) and `create_initiatives.py` (`DEFAULT_SOURCE`, ~line 55; argparse default line 659). `--source` already exists as an override, so the fix is just: stop defaulting to a personal path — require `--source` explicitly (fail with a clear message) or read an env var (e.g. `AZURE_POLICY_REPO`), then update the two docstrings, `flows/catalogue_builder/README.md`, and `docs/az-taxonomy-pipeline.md`. Producer-only; doesn't touch the customer-facing epac-builder path | low | done (2026-07-03) | Karel, 2026-07-03 |
| 6 | Pinned-commit fetch for the official policy source: `config/policy-source.json` pin + `flows/tools/fetch_policy_source.py` (`--sync` / `--check`) materialising a gitignored `.policy-source/` cache; `official_policy_source()` defaults to it. Gives everyone one reproducible version (builds match committed `builtInsRef`). Kernel of the future daily-sync system | medium | done (2026-07-04) | Karel, 2026-07-04 |
| 9 | Enable CI in GitHub: the workflow files exist but Actions has never run — push the repo/branch (`alpha/epac-builder/actions` is currently unpushed), enable Actions, and confirm `contoso epac build` (#11) plus any other workflows run green. Prereq for #7/#8/#11 actually executing anywhere | medium | done (2026-07-05) | Karel, 2026-07-04 |
| 10 | Customer-folder reshape: `customer/` is doing double duty as the worked `contoso` sample **and** the CI golden fixture, so a new user can't start from an empty scaffold. Move the sample (filled `manifest.example.jsonc`, `designs/contoso-*`, `package/`) to `catalogue-builder/examples/contoso/` via `git mv`; leave `customer/` holding only schemas + `manifest.template.jsonc` + `input.example.json` + READMEs; add `customer/NOTICE.md`, `customer/designs/README.md`, and a root `CLAUDE.md` so every session knows `customer/` is the user's empty working area and `examples/contoso/` is the sample. Repoint docs (`manifests/README.md`, `docs/az-taxonomy-pipeline.md`, `docs/epac-assembler-design.md`). See plan Parts B/D | high | done (2026-07-05) | Karel, 2026-07-04 |
| 11 | Contoso CI + native start-check: after #10, add `examples/contoso/verify.sh` (build + full-tree `diff -rq`, the pipeline logic living with the example) invoked by a thin `.github/workflows/contoso-epac-build.yml` (name `contoso epac build`; `paths:` on `flows/**` + `catalogue/**` + `examples/contoso/**` so it fires on either builder changing — GH Actions requires the YAML under `.github/workflows/`, so logic lives in the example, trigger lives at root); and make `epac-builder-start`'s health check build from the **current** `customer/` inputs (dynamic) rather than the frozen fixture, reporting "not configured" on an empty scaffold. Consumer/example half of CI — pairs with #8 (producer half). Depends on #10 | medium | done (2026-07-05) | Karel, 2026-07-04 |
| 13 | Terraform/Bicep renderers have **zero regression coverage**: CI (`test.yml`) builds only the default (json) flavour and diffs it; `render_terraform`+`hcl` and `render_bicep` are exercised by no test, so a silent regression in either ships undetected. Extend the golden fixture to a `--only json,terraform,bicep` build + full-tree `diff -rq` (commit the two extra flavour trees as fixtures, or fold into #11's `verify.sh`). Both flavours verified working by hand on 2026-07-05 — this is coverage, not a bug | low | done (2026-07-05) | actions/reviews/review-07-05-26.md |
| 12 | Convert `catalogue-builder/plan/catalogue-builder.md` (the 5-phase producer runbook) into a slash command `.claude/commands/catalogue-builder-run.md` — a single run command executing phases 1–5, mirroring `epac-builder-start.md`'s frontmatter (`description`, `disable-model-invocation: true`). Fix on the way: (a) replace all hard-coded absolute script paths (`C:\GIT\…\<script>.py` in Phases 1/3/4/5) with repo-relative `python flows/…` invocations; (b) rewrite Phase 1's "Authorized source folder" section (lines 52–59), which still names the personal `C:\GIT\Official Azure Policy\…` clone as the `--source` default — obsoleted by #5/#6; lead with `python flows/tools/fetch_policy_source.py --sync` + pinned-cache resolution (`flows/shared/paths.py::official_policy_source`) instead | medium | done (2026-07-05) | Karel, 2026-07-04 |
| 16 | **Consumer-onboarding skill** (`catalogue-builder/skills/epac-builder-onboarding-agent/`): a self-contained skill that walks a new engineer/developer/user through onboarding to EPAC Builder as a **consumer** — Explain (how the catalogue/EPAC builders fit, what the package contains) → Interview (collect every manifest input up front, no silent defaults; the concrete question set = `customer` + `selection` + one value per `<REPLACE:>` the `--input` expansion emits, incl. one per required policy param) → Generate (drive the real `assemble_scaffold.py` to fill `customer/` + render `customer/package/`) → Hand off. **Hard boundary: read-only on the engine** — only writes under `customer/`, never edits `flows/**`/`catalogue/**`/schemas/workflows, declines engine changes even if asked. Built 2026-07-05; SKILL.md + README shipped. Follow-ups: exercise it end-to-end against a fresh empty `customer/` (dry run) and reconcile with #14/#15 (deploy + upgrade layers it explicitly defers) | medium | done (2026-07-05) | Karel, 2026-07-05 |
| 19 | **Wire the MCP smoke test into CI**: `flows/mcp_server/test_server.sh` is green locally (5/5) but runs in **no** workflow — a silent regression in the stdio server or `validate_manifest` ships undetected (same untested-in-CI class as the old #13 renderer gap). Add a `bash flows/mcp_server/test_server.sh` step to `.github/workflows/contoso-epac-build.yml` (already fires on `flows/**`). Called out as a follow-up in #17's notes + the 2026-07-07 session log; promoting to its own row | low | done (2026-07-18) | actions/reviews/review-07-07-26.md |
| 23 | **Bundled package workflow isn't repo-root-discoverable**: `package.py` (`_epac_workflow`, package.py:43-131) writes `.github/workflows/{epac,terraform,bicep}.yml` **inside** the package dir with repo-root-relative paths (`DEFINITIONS: Definitions`, `paths: Definitions/**`). GitHub only discovers workflows at the **repo root**, and the paths assume the package *is* the repo root — so the bundled pipeline never fires when the package is dropped into an existing repo as a subfolder. Affects all three flavours. **Resolved by decision, not by code (Karel, 2026-07-20):** the package **is** the root of a dedicated customer deploy repo — this repo is never delivered to the customer, and the engineer building the package is expected to know where it lands. That makes the repo-root-relative paths *correct by contract*; no wrapper, no `DEFINITIONS` parameterization, no subfolder support. Fix was documentation: `_header` (package.py:266, shared by all three flavours) now states the rule at the top of every generated package README, so it travels with the artifact; `examples/contoso/README.md` gained a "Delivery boundary" section. Consumer's hand-written root `epac-demo.yml` was the workaround for the undocumented rule | medium | done (2026-07-20) | actions/feedback/consumer-feedback-demo-07-07-26.md |
| 24 | **Housekeeping: gitignore `Output/` + settle customer-package deploy location**: `customer/package/Output/` (EPAC plan artifact) is **not** gitignored (no `customer/.gitignore` exists) — a local `Build-DeploymentPlans` run would be committed; add an ignore rule. Separately decide whether a real deploy package belongs under `customer/` (diverges from the "empty scaffold; sample in `examples/contoso/`" convention) or as its own example / dedicated deploy repo. Note `*.manifest.jsonc` is already ignored (`customer/manifests/.gitignore:5-6`), so a committed demo carries `demo.input.json` + rendered `package/` but not its manifest — confirm that's acceptable | low | done (2026-07-09) | actions/feedback/consumer-feedback-demo-07-07-26.md |
| 25 | **Move the historical prototype tree `product/lab/` to the repo root (`lab/`)**: it's self-contained (`lab-01…lab-11`, incl. `lab-11`'s own private pipeline copy) with **no** ties into the active `catalogue-builder/`, so this is a clean `git mv product/lab lab`. Only **five** external doc lines reference the old path and need updating (`CLAUDE.md:4`, `AGENTS.md:19`, `foundry/README.md:3`, `foundry/architecture.md:5` + `:165`). No active-CI / `.gitignore` / `.claude/` entanglement; `product/` survives the move (keeps `descriptions/` + `developmentjourney/`, and `product/descriptions/` is referenced by `foundry/`). Optional tidy-up: ~54 stale internal absolute `C:\GIT\…\product\lab\…` paths baked into dead prototype scripts/plans would dangle after the move but nothing runs them | low | done (2026-07-07) | Karel, 2026-07-07 |

### Completion notes (moved with their rows, in id order)

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
