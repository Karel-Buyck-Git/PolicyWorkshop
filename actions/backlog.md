# Backlog

Living list of action items for catalogue-builder / epac-builder. Sourced from reviews in
`log/`. Update at the start/end of every session — see `actions/sessions/`.

Status: `todo` / `in-progress` / `done`

| # | Item | Effort | Status | Source |
|---|---|---|---|---|
| 1 | Test suite / CI on the builder (golden-fixture diff against `customer/package/`) | low | done (2026-07-03) | log/review-07-03-26.md |
| 1a | Add `requirements.txt`/`pyproject.toml` marker (stdlib-only, but make it explicit) | low | done (2026-07-05) | log/review-07-03-26.md |
| 1b | Drop committed `__pycache__`, add to `.gitignore` | low | done (2026-07-05) | log/review-07-03-26.md |
| 2 | Manifest completion guardrail: `--strict`/pre-deploy gate that fails when any `<REPLACE:>` or placeholder-scope survives into output | medium | todo | log/review-07-03-26.md |
| 3 | Catalogue customer-clean: resolve/remove `undefined`-domain policies, drop `builtinpolicytest` so the catalogue can be regenerated reproducibly | high | todo | log/review-07-03-26.md |
| 4 | `customer/package/docs/*.svg` is stale vs. `customer/designs/*.svg` (byte-diff, same commit) — CI's golden-fixture diff excludes `docs/` because of this; resync so the exclusion can be dropped | low | done (2026-07-04) | discovered building CI, 2026-07-03 |
| 5 | Producer's `--source` default is hard-coded to a local clone path (`C:\GIT\Official Azure Policy\...`) — breaks for anyone but Karel running without `--source`. In `extract_policies.py` (`DEFAULT_SOURCE`, ~line 270; docstring line 17; argparse default line 292) and `create_initiatives.py` (`DEFAULT_SOURCE`, ~line 55; argparse default line 659). `--source` already exists as an override, so the fix is just: stop defaulting to a personal path — require `--source` explicitly (fail with a clear message) or read an env var (e.g. `AZURE_POLICY_REPO`), then update the two docstrings, `flows/catalogue_builder/README.md`, and `docs/az-taxonomy-pipeline.md`. Producer-only; doesn't touch the customer-facing epac-builder path | low | done (2026-07-03) | Karel, 2026-07-03 |
| 6 | Pinned-commit fetch for the official policy source: `config/policy-source.json` pin + `flows/tools/fetch_policy_source.py` (`--sync` / `--check`) materialising a gitignored `.policy-source/` cache; `official_policy_source()` defaults to it. Gives everyone one reproducible version (builds match committed `builtInsRef`). Kernel of the future daily-sync system | medium | done (2026-07-04) | Karel, 2026-07-04 |
| 7 | Daily-sync system: schedule `fetch_policy_source.py --sync` + `--check` (GitHub Action / cron) and wire the `--check` drift signal (exit 2) into a notification. Builds on #6 | medium | todo | discovered building #6, 2026-07-04 |
| 8 | Producer-side CI: now that the source is reproducible (#6), add a workflow that runs `fetch_policy_source.py` then regenerates the catalogue and diffs it (extend/complement `.github/workflows/contoso-epac-build.yml`, which currently only exercises the consumer/assembler) | medium | todo | discovered building #6, 2026-07-04 |
| 9 | Enable CI in GitHub: the workflow files exist but Actions has never run — push the repo/branch (`alpha/epac-builder/actions` is currently unpushed), enable Actions, and confirm `contoso epac build` (#11) plus any other workflows run green. Prereq for #7/#8/#11 actually executing anywhere | medium | done (2026-07-05) | Karel, 2026-07-04 |
| 10 | Customer-folder reshape: `customer/` is doing double duty as the worked `contoso` sample **and** the CI golden fixture, so a new user can't start from an empty scaffold. Move the sample (filled `manifest.example.jsonc`, `designs/contoso-*`, `package/`) to `catalogue-builder/examples/contoso/` via `git mv`; leave `customer/` holding only schemas + `manifest.template.jsonc` + `input.example.json` + READMEs; add `customer/NOTICE.md`, `customer/designs/README.md`, and a root `CLAUDE.md` so every session knows `customer/` is the user's empty working area and `examples/contoso/` is the sample. Repoint docs (`manifests/README.md`, `docs/az-taxonomy-pipeline.md`, `docs/epac-assembler-design.md`). See plan Parts B/D | high | done (2026-07-05) | Karel, 2026-07-04 |
| 11 | Contoso CI + native start-check: after #10, add `examples/contoso/verify.sh` (build + full-tree `diff -rq`, the pipeline logic living with the example) invoked by a thin `.github/workflows/contoso-epac-build.yml` (name `contoso epac build`; `paths:` on `flows/**` + `catalogue/**` + `examples/contoso/**` so it fires on either builder changing — GH Actions requires the YAML under `.github/workflows/`, so logic lives in the example, trigger lives at root); and make `epac-builder-start`'s health check build from the **current** `customer/` inputs (dynamic) rather than the frozen fixture, reporting "not configured" on an empty scaffold. Consumer/example half of CI — pairs with #8 (producer half). Depends on #10 | medium | done (2026-07-05) | Karel, 2026-07-04 |
| 13 | Terraform/Bicep renderers have **zero regression coverage**: CI (`test.yml`) builds only the default (json) flavour and diffs it; `render_terraform`+`hcl` and `render_bicep` are exercised by no test, so a silent regression in either ships undetected. Extend the golden fixture to a `--only json,terraform,bicep` build + full-tree `diff -rq` (commit the two extra flavour trees as fixtures, or fold into #11's `verify.sh`). Both flavours verified working by hand on 2026-07-05 — this is coverage, not a bug | low | done (2026-07-05) | log/review-07-05-26.md |
| 12 | Convert `catalogue-builder/plan/catalogue-builder.md` (the 5-phase producer runbook) into a slash command `.claude/commands/catalogue-builder-run.md` — a single run command executing phases 1–5, mirroring `epac-builder-start.md`'s frontmatter (`description`, `disable-model-invocation: true`). Fix on the way: (a) replace all hard-coded absolute script paths (`C:\GIT\…\<script>.py` in Phases 1/3/4/5) with repo-relative `python flows/…` invocations; (b) rewrite Phase 1's "Authorized source folder" section (lines 52–59), which still names the personal `C:\GIT\Official Azure Policy\…` clone as the `--source` default — obsoleted by #5/#6; lead with `python flows/tools/fetch_policy_source.py --sync` + pinned-cache resolution (`flows/shared/paths.py::official_policy_source`) instead | medium | done (2026-07-05) | Karel, 2026-07-04 |
| 14 | **Contoso as the deployable reference customer** (real Azure tenant, end-to-end): today `contoso epac build` (#11/#13) only proves the assembler is **deterministic** (rebuild + byte-`diff`), NOT that the package is **deployable**. Establish contoso as the internal reference customer deployed against a real dev/sandbox tenant, adding the deployability layer the regression flow deliberately skips: (a) validate the generated EPAC/json package with the **EPAC PowerShell module** (`Build-DeploymentPlan` + `Deploy-*` in what-if), (b) prove the **generated GitHub / Azure DevOps pipeline** actually runs that plan/deploy (OIDC/service-principal auth), and optionally (c) `terraform validate/plan` + `az bicep build` for the other two flavours. Gives engineers a living, deployable reference — not just a byte-diff fixture. Needs a tenant + credentials; likely a separate opt-in workflow (secrets, not on every push). Distinct from the catalogue-upgrade path (#15) | high | todo | Karel, 2026-07-05 |
| 15 | **Customer-package lifecycle / catalogue-upgrade path**: the shared catalogue is versioned and bumped ~**monthly**; a customer package built + deployed at catalogue version X must be **re-generatable/migratable** to version Y without hand-editing — diff what changed between catalogue versions, re-assemble the customer's manifest against the new catalogue, and surface breaking changes (removed/renamed initiatives, new required params, role changes) for review before redeploy. Needed to keep already-implemented customer tenants current as the catalogue evolves. Use **contoso** as the test case (pairs with #14). Kernel of a future "customer package update" system; builds on the versioned catalogue (`catalogue.json` `version`/`contentHash`) and `lineage.json` provenance already emitted per package | high | todo | Karel, 2026-07-05 |

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
- Review 2026-07-05 (`log/review-07-05-26.md`) reconciled: confirmed #1/#1a/#1b/#4/#5/#6/#9/#10/#12
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
- Re-run `actions/review-prompt.md` periodically; reconcile new findings into this table.
