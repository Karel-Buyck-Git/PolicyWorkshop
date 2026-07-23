# Backlog

Living list of action items for catalogue-builder / epac-builder. Sourced from reviews in
`actions/reviews/` and consumer feedback in `actions/feedback/`. Update at the start/end of every
session — see `actions/sessions/`.

Status: `todo` / `in-progress` / `done`

| # | Item | Effort | Status | Source |
|---|---|---|---|---|
| 7 | Daily-sync system: schedule `fetch_policy_source.py --sync` + `--check` (GitHub Action / cron) and wire the `--check` drift signal (exit 2) into a notification. Builds on #6 | medium | todo | discovered building #6, 2026-07-04 |
| 8 | Producer-side CI: now that the source is reproducible (#6), add a workflow that runs `fetch_policy_source.py` then regenerates the catalogue and diffs it (extend/complement `.github/workflows/contoso-epac-build.yml`, which currently only exercises the consumer/assembler) | medium | todo | discovered building #6, 2026-07-04 |
| 14 | **Contoso as the deployable reference customer** (real Azure tenant, end-to-end): today `contoso epac build` (#11/#13) only proves the assembler is **deterministic** (rebuild + byte-`diff`), NOT that the package is **deployable**. Establish contoso as the internal reference customer deployed against a real dev/sandbox tenant, adding the deployability layer the regression flow deliberately skips: (a) validate the generated EPAC/json package with the **EPAC PowerShell module** (`Build-DeploymentPlan` + `Deploy-*` in what-if), (b) prove the **generated GitHub Actions pipeline** actually runs that plan/deploy (OIDC auth) — scoped to GitHub because that is the only platform the generator emits; the Azure DevOps half is **#32**, and #14 is not blocked on it — and optionally (c) `terraform validate/plan` + `az bicep build` for the other two flavours. Gives engineers a living, deployable reference — not just a byte-diff fixture. Needs a tenant + credentials; likely a separate opt-in workflow (secrets, not on every push). Distinct from the catalogue-upgrade path (#15) | high | in-progress (2026-07-07) | Karel, 2026-07-05 |
| 15 | **Customer-package lifecycle / catalogue-upgrade path**: the shared catalogue is versioned and bumped ~**monthly**; a customer package built + deployed at catalogue version X must be **re-generatable/migratable** to version Y without hand-editing — diff what changed between catalogue versions, re-assemble the customer's manifest against the new catalogue, and surface breaking changes (removed/renamed initiatives, new required params, role changes) for review before redeploy. Needed to keep already-implemented customer tenants current as the catalogue evolves. Use **contoso** as the test case (pairs with #14). Kernel of a future "customer package update" system; builds on the versioned catalogue (`catalogue.json` `version`/`contentHash`) and `lineage.json` provenance already emitted per package | high | todo | Karel, 2026-07-05 |
| 17 | **Local MCP server (stdio)** over the builder working tree — expose the on-disk build/validate flows as MCP tools for conversational use: `validate_manifest`/`strict_check` (wrap `assemble_scaffold.py --check` / `--check --strict`; **highest value** — instant "every unfilled `<REPLACE:>` + every placeholder scope" feedback without shelling out), `assemble_scaffold` (full build → json/terraform/bicep + `report.md`/`lineage.json`), `expand_input` (tiny `input.json` → scaffolded manifest with `<REPLACE:>` seeded), `check_policy_source_drift` (`fetch_policy_source.py --check`), `diff_catalogues` (`catalogue_diff.py`), `generate_mg_hierarchy_svg` (plain-text mg-tree → SVG), and optionally the producer pipeline steps (extract/enrich/create-initiatives/apply-overlays/QC) as a **maintainer-only** surface. Anything that mutates a customer package or touches the filesystem lives here (one user, one working tree). **Caveat: decisions to settle before building — see Notes** (local/stdio has none of the HTTP hosting/auth/network/cost exposure) | medium | in-progress (2026-07-07) | Karel, 2026-07-06 |
| 18 | **HTTP MCP server (remote, read-only)** over the published catalogue artifact (`index.json` + `catalogue.json` + `initiatives/` + `definitions/` — a self-contained versioned artifact) — pure lookups exposable to consumers who never touch this repo (sales engineers, customers, other internal tools): `search_policies`/`lookup_policy_by_id` (keyword/GUID/resource-type → tier, category, effect, description), `get_initiative` (a domain/tier/category group's policy set, required params, usage guide), `explain_tier_rationale` (NIS2/ISO27001/CIS/NIST citation baked into `enrich_policies.py` output), `get_tier_description` (Essential/Professional/Enterprise product copy — good for a pre-sales chatbot), `get_catalogue_version` (version/hash/counts). No repo or filesystem access. **Caveat: MUST settle auth + hosting + network + recurring-cost decisions before building — see Notes** | high | todo | Karel, 2026-07-06 |
| 20 | **EPAC 11.x deploy-blocking renderer gaps (consumer what-if, Findings 1 & 3)**: `render_json.py` emits a package that passes the builder's **own** schema but is rejected by EPAC 11.4.7 at `Build-DeploymentPlans`. Two fixes. **(a)** `_write_global_settings` (render_json.py:50-68) emits **no `desiredState`** — add it **inside each `pacEnvironment`** with a **safe default `strategy:"ownedOnly"`** + `keepDfcSecurityAssignments:false`, and surface `strategy` (+ optional `excludedScopes`) as a **per-environment manifest field** (add to `environments[]` in `manifest.schema.json` **and** `manifest.input.schema.json`, thread through `_env` in `ir.py`, emit in the renderer) so greenfield can opt into `full` deliberately while brownfield stays safe by default. Brownfield safety is the sharp edge (Finding 3): where the field is optional EPAC defaults to destructive `full`, proposing deletion of a tenant's pre-existing ALZ/hand-made policy at/below root scope. **(b)** `_assignment` (render_json.py:80) emits flat `policySetDefinitionName`; EPAC 11.x expects `definitionEntry:{policySetName:…}` — convert (review terraform/bicep renderers for the same shape). Regenerating contoso fixtures required (byte-diff CI). First **real-tenant** validation feeding #14. **Landed 2026-07-22** (both (a) and (b), json only — tf/bicep emit native `azurerm`/ARM resources and have no `desiredState`/`policySetName` concept) | high | done (2026-07-22) | actions/feedback/consumer-feedback-vandelabr-07-06-26.md |
| 21 | **Naming initiative hardcodes `customerAbbreviation:"dlw"` (consumer Finding 2)**: `management-esn-naming.policyset.json` bakes `{"value":"dlw"}` **162×** (only `effect` is a real initiative parameter), so the naming initiative audits every non-DLW customer (e.g. vandelabr) against a `dlw-*` anchor and can't be retargeted from the manifest. **Fix (parameterize from manifest):** promote `customerAbbreviation` to an initiative-level parameter (keep `defaultValue "dlw"` as safe fallback) bound from the existing manifest `prefix`. Producer/scaffold change — generalize `_bubbled_params` (scaffold.py:127-135), which special-cases only `effect`, to also bubble `customerAbbreviation` to `"[parameters('customerAbbreviation')]"` + add it to the initiative `parameters` block (~scaffold.py:212-227); `CUST_DEFAULT` at gen_dlw_naming_definitions.py:36 stays the default. Then **regenerate the catalogue** and wire the manifest binding (`bindings.defaults` / derive from `prefix`). Catalogue-regeneration fix, heavier than #20 | medium | todo | actions/feedback/consumer-feedback-vandelabr-07-06-26.md |
| 22 | **Producer catalogue assignment scaffolds use invalid top-level `policySetDefinitionName`**: the **188** `*.assignment.json` reference scaffolds under `catalogue/initiatives/**` all emit a top-level `policySetDefinitionName`; EPAC 11.x rejects that leaf shape (`each tree branch must define either a definitionEntry or a non-empty definitionEntryList`) and wants `definitionEntry:{policySetName,displayName}` — the same defect as #20(b) but in a **separate producer code path**. Emitters: `build_assignment` (create_initiatives.py:531) + `_new_group_assignment` (scaffold.py:245); keep `quality_control.py:183`'s reader consistent. Regenerate the catalogue after the fix. **Lower severity**: these scaffolds are **not** copied into customer packages (the assembler lifts only `nodeName`, ir.py:106), so they're reference/deployment-example artifacts — only a real problem if the catalogue scaffolds are meant to be directly EPAC-deployable. Producer task (`/catalogue-builder-run`) | low | todo | actions/feedback/consumer-feedback-demo-07-07-26.md |
| 26 | **Producer Phase 3 (`create_initiatives.py`) is additive — no garbage collection of moved/removed groups**: the script writes `(domain,tier,category)` group dirs (`create_initiatives.py:723`, `mkdir(parents=True, exist_ok=True)`) but never prunes groups that move or disappear, so reclassifying a category (or any domain/tier/category change) leaves the old `initiatives/<olddomain>/…` dir orphaned on disk. **The orphan is silent but poisons the catalogue stamp**, because the two artifacts are derived from different universes: `index.json[groups]` is built from the *in-memory* record list parsed from the enriched markdown (`create_initiatives.py:620-638`), while `contentHash` is built by `rglob("*")` over `catalogue/` *on disk* (`apply_overlays.py:72-80`, call site `:145`). So a stale dir is invisible to `index.json`, to `catalogue.json` `counts`, and to every QC check — `quality_control.py`'s `unregistered-custom-group` (`:296-305`) is gated on `it.get("custom")`, so a stale **built-in** group dir is skipped outright, and there is no reverse `index.json[groups][*].dir` → disk check anywhere. Phase 5 passes green with a wrong `contentHash`, deterministically (so it never flaps), and `catalogue_diff.py:160` will later report drift between two semantically identical catalogues. Discovered doing #3: moving **11 categories** (17 policysets) out of `undefined` left stale `undefined/**` dirs (25 policysets on disk vs 8 in `index.json`); worked around by manually wiping `catalogue/initiatives/` before re-running Phases 3→4→5. **Fix — the pattern already exists in-tree**: `apply_overlays.py:120-128` does exactly this prune for `definitions/custom/<family>` ("so a disabled generator … leaves no orphaned definitions behind"); the same reasoning was simply never applied to `initiatives/`. Mirror it in `create_initiatives.py` (clear, or diff-and-prune, its output tree at the start of a run) so a regenerate is self-cleaning. Fix **before the next catalogue regeneration**. Producer task | low | todo | discovered building #3, 2026-07-19 |
| 27 | **Versioning & branching strategy — blocks Alpha exit** (decision spike, not code): **three things version independently and only one of them is stamped.** (a) *Catalogue artifact* — `catalogueVersion` (`2026.07.18`) + `contentHash`; works, and is the one thing enforced (`assemble_scaffold.py:107-111` fails the build on a mismatch). (b) *Taxonomy/hierarchy inputs* — `catalogue.json` `inputs.hierarchyHash` / `tierRulesHash` / `definitionGensHash`; the hashes move correctly but **nothing propagates them to consumers**. (c) *Engine (epac-builder itself)* — `pyproject.toml` is still `version = "0.0.0"`, so the `tools.*` hashes in `catalogue.json` are the only de-facto engine fingerprint. **Evidence this is already biting:** `hierarchyVersion` is **inert** — declared in `manifest.schema.json:53-55` as "Domain hierarchy snapshot id (lineage)", written by `expand.py:52` as the literal `<REPLACE: hierarchy-snapshot-id>`, and read by **no code at all**; #3 changed the hierarchy and moved `inputs.hierarchyHash`, yet `examples/contoso/manifests/manifest.example.jsonc:15` still pins `2026.06.21`, the only remaining `2026.06.21` string in the active tree. `lineage.json` — the provenance artifact that **ships to the customer** — records only `catalogueVersion`: not `contentHash`, not `builtInsRef`, not `hierarchyVersion`, not any engine version, so a customer holding an epac-package cannot tell which builder produced it or which upstream Azure Policy commit it came from. And `tools.extract` / `tools.createInitiatives` moved in `82dc38f`, a commit that changed **no** Python — absorbed from `da93bad`, which landed after the previous regeneration in `44ce852`; provenance moved for a reason the record can't explain, precisely because there's no engine version to pin against. **Open questions to settle:** does the hierarchy get its own version or inherit the catalogue's? Does a git branch map to a catalogue version, an engine version, or both? What single identifier does a customer quote in a support conversation? Recurring monthly upstream sync (`config/policy-source.json` pinned at `04989912`, fetched 2026-07-04) makes this recur. Split implementation rows off once the model is chosen | high | todo | actions/reviews/review-07-20-26.md |
| 28 | **Real customer manifests carry tenant identifiers into a public repo**: #24 dropped the `*.manifest.jsonc` ignore from `customer/manifests/.gitignore` and `customer/NOTICE.md` + `customer/manifests/README.md` now instruct users to commit the manifest "for provenance" — but an expanded `<customer>.manifest.jsonc` carries `tenantId`, `pacOwnerId`, `deploymentRootScope` (root management-group resource id) and `logAnalyticsWorkspaceId` (`expand.py:47-62`). In a public repo, a consumer following that guidance publishes their tenant GUID, root MG id and workspace resource id. The deploy-location decision itself (#24) was settled deliberately and stands; **this row is about *where* that rule applies** — decide whether real customer manifests belong in this public repo at all, or whether committable-provenance should hold only inside a customer's own private deploy repo. If they stay, name the exposed identifiers explicitly in `NOTICE.md`/`README.md` so the choice is informed | medium | todo | actions/reviews/review-07-20-26.md |
| 29 | **QC sample tables churn and lose domain coverage on any catalogue change**: `quality_control.py:73-83` `spread()` picks evenly spaced **indices** from a positionally ordered list, so inserting the 17 relocated policysets in #3 reshuffled every sample row rather than just the affected ones. Net effect in the regenerated `catalogue/naming-samples.md:104-116` and `docs/epac-naming-convention.md:101-113`: **Data** now appears twice (`data-ent-sql`, `data-pro-hapi`), **Security** dropped out entirely, and the `undefined-esn-ehc` row that illustrated the catch-bucket is gone — while `undefined` still holds 8 policysets. Both docs claim to show "a representative spread", and both are auto-generated, so the churn recurs on every catalogue change and pollutes the diff. Fix direction: sample **one per domain** (or otherwise key the selection to the taxonomy) instead of by list position | low | todo | actions/reviews/review-07-20-26.md |
| 30 | **MCP smoke test crashes with a traceback instead of a clean FAIL**: `engine/mcp_server/test_server.sh:55-95` indexes `resp[1]`…`resp[5]` directly, so a server that dies after `initialize` — or returns a JSON-RPC error object with no `"result"` — raises `KeyError: 2` and prints a bare Python traceback pointing at the test harness rather than the script's own `[test] FAIL: …` message. The script already defines `fail()` and already handles the non-JSON/protocol-contamination case, so this is an inconsistent gap rather than a design choice. Now CI-facing via #19 (`contoso-epac-build.yml:48`), where a legible failure message is the entire point. Fix: look the id up with `.get()` and `fail()` with "no response for id N" when absent | low | todo | actions/reviews/review-07-20-26.md |
| 31 | **Front end for package creation (mid/long-term product goal)**: today the only way to produce a customer epac-package is to clone this repo and drive `assemble_scaffold.py` — via the CLI, or conversationally through the onboarding skill (#16). That gates delivery on an engineer with a working tree, and it is the wrong shape for the delivery boundary settled in #23: **the customer never receives this repo, only the rendered package.** Goal: a proper front end where an engineer (and eventually a customer directly) fills the manifest inputs and gets a package out, without cloning anything. **Interaction model already proven by #16** — Explain → Interview (every input up front, no silent defaults, one question per `<REPLACE:>`) → Generate → Hand off; the front end is that flow with a real UI instead of a chat transcript, and the same hard boundary (read-only on the engine; only ever writes a package). **Read side already scoped as #18** — the HTTP MCP server over the published catalogue artifact is exactly the lookup API such a front end needs (search policies, get initiative, explain tier rationale), and was already framed for "consumers who never touch this repo". **Hard dependency on #27**: a front end that emits packages to people outside this repo is unshippable until the engine and catalogue carry real versions to stamp into `lineage.json` — otherwise nobody can answer "which builder produced this package?". Open questions: who hosts and authenticates it; does it render server-side or hand back a manifest for a pipeline to build; does the customer get the package as a repo, a zip, or a PR into their deploy repo. Decision spike before any build; sequence after #27 and #18 | high | todo | Karel, 2026-07-20 |
| 32 | **Azure DevOps as a deploy platform target**: `package.py` emits GitHub Actions only (`_WORKFLOWS`, package.py:247 -> `.github/workflows/{epac,terraform,bicep}.yml`), but ADO is a stated goal — `docs/scaffold-deployment-guide.md` covers "GitHub Actions **and Azure DevOps**" (whole §14) and #14 assumed a generated ADO pipeline that no code produces. **Salvaged from the retired `automation/` tree (deleted 2026-07-20, originals at `755a774^`)** — the three things worth keeping: (a) **`Build-DeploymentPlans -DevOpsType "ado"`**, the flag that makes EPAC emit ADO-flavoured plan output (the one piece of real knowledge in that tree); (b) task shape `AzurePowerShell@5` with `azureSubscription: <service connection>` + `ScriptType: InlineScript` + `pwsh: true`; (c) artifact syntax `- publish: $(PAC_OUTPUT_FOLDER)` / `- download: current` (vs GitHub's `upload-artifact`/`download-artifact`). **Modelling question to settle first:** ADO is a **platform** axis, not a renderer flavour, so it does not slot cleanly into the existing `{json, terraform, bicep}` key space — decide between a `platform` field on the manifest vs a `json-ado` flavour key, *then* add `_ado_workflow()` beside `_epac_workflow` (package.py:43). **Must not repeat the retired tree's defects**: it had no `Deploy-RolesPlan` stage (so DINE/Modify remediation identities never got their roles), no `trigger:` block, no approval gates, and a dangling `template:` path. Prefer ADO **workload-identity federation** over the service-connection secret those templates used — `scaffold-deployment-guide.md:388-392` already documents the federated path. Regenerating contoso fixtures required (byte-diff CI) | medium | todo | Karel, 2026-07-20 |
| 33 | **PR validation gate in the generated package (Tier-1 static done; Tier-2/flavours open)**: shipped 2026-07-20 — the generated json package now carries `validate-package.py` (stdlib, no Azure, no creds) + a `.github/workflows/epac-validate.yml` PR gate, and `epac.yml` gained a `concurrency:` guard so two runs can't reconcile one `deploymentRootScope` at once. **Tier 1** (static, every PR incl. forks): parse, placeholder residue, resource-id shape, policyset/custom-policy referential integrity, and **pacSelector coverage** — an assignment with no `scope` key for a declared pacSelector is silently skipped by EPAC, caught nowhere else. **Tier 2** (plan/what-if via `Build-DeploymentPlans`, Reader identity, guarded to same-repo PRs so fork PRs skip rather than fail) overlaps #14's deployability goal. The validator is emitted verbatim from its source (`engine/epac_builder/pkgvalidate.py`) so it can't drift; the byte-diff CI proves it. **Deliberately NOT done, open follow-ups:** (a) full EPAC-schema conformance is left to `Build-DeploymentPlans` — our stdlib `validate.py` can't parse the EPAC schemas' `patternProperties`/`oneOf`/recursive `$ref` and would pass them while skipping `scope`/`notScopes`; (b) terraform & bicep packages get **no** validator/PR gate yet — json only; (c) `managedIdentityLocation` region and `logAnalyticsWorkspaceId` shape are unvalidated (no stale region allow-list shipped on purpose) | medium | in-progress (2026-07-20) | Karel, 2026-07-20 |
| 34 | **Engineer deploy-repo setup guide, shipped inside the package (GitHub done; ADO + tf/bicep open)**: the generated `README.md` only *names* the CI/CD prerequisites (5 secrets, 2 environments, 3 OIDC identities); there was no guidance on standing up the *platform* around a package — runners, environment protection rules, GitHub **licensing** (required reviewers on an environment need a paid plan on a private repo), OIDC federated-credential subjects, branch protection. The general `docs/scaffold-deployment-guide.md` is EPAC-concept-oriented and, per the #23 delivery boundary, **never ships to the customer** — only the rendered package does. **Shipped 2026-07-21 (GitHub + Azure/Entra, json slice):** two plane-1 guides emitted **verbatim** (same source-of-truth pattern as `pkgvalidate.py`) into every json package — `engine/epac_builder/github_setup.md` → `docs/github/README.md` (`_github_setup_doc()`) and `engine/epac_builder/azure_requirements.md` → `docs/azure/README.md` (`_azure_requirements_doc()`, covers subscriptions, management-group scope, Entra app registrations, RBAC roles, and Azure/Entra licensing/cost); the top-level README links to both; byte-diff CI proves them. **Open follow-ups:** (a) **Azure DevOps** equivalent — blocked on #32 (no ADO pipeline is generated yet), and the guide's identity/service-connection half only makes sense once `_ado_workflow()` exists; (b) **terraform & bicep** flavour guides (their identity/secret model differs — single `TF_/BICEP_CLIENT_ID`, `terraform-apply`/`bicep-apply` environments); (c) **day-2 ops** (remediation runs, catalogue-upgrade redeploys — ties to #15); (d) consider whether the customer-specific values (customer name, pacOwnerId, selectors) should be templated into the guide rather than kept generic + cross-referenced to the README. Docs + generator hand-off; complements #32 (ADO *workflows*) and #14 (deployability) | medium | in-progress (2026-07-21) | Karel, 2026-07-21 |
| 35 | **Documentation-architecture convention — high-level inline + central engine-docs library**: adopt a repo-wide rule that large explanatory content does not live inline in code. **Two documentation planes, kept explicitly apart:** (1) *customer/package docs* — product content emitted into the rendered package and delivered (e.g. `engine/epac_builder/github_setup.md` → `package/docs/github/README.md`); correctly a standalone `.md` template, not inline code; (2) *engine/maintainer docs* — how the builders work (`package.py`, the assembler, the producer), which never ship to a customer. **The rule:** (a) inline docstrings/comments stay high-level (what + why, a few lines) and end with a `See: docs/<x>.md` pointer when a deeper doc exists — no multi-page explanation inside code (`package.py`'s 8-line module docstring is the target size); (b) detailed engine/maintainer docs live centrally under `epac-workbench/docs/` (already home to `epac-assembler-design.md`, `az-taxonomy-pipeline.md`, `scaffold-deployment-guide.md`…) with a new `docs/README.md` **index** mapping each engine / script / command → its doc; (c) label the two planes so a customer guide is never inlined into code and a maintainer doc is never shipped to a customer. **Light cleanup in scope:** sweep the engine for over-long inline explanation blocks to trim + link, and reconcile the plane-1/plane-2 boundary — notably the overlap between the shipped `github_setup.md` (plane 1) and the builder-side `scaffold-deployment-guide.md` (plane 2). **Open questions to settle at pickup:** library location (`epac-workbench/docs/` recommended vs a new root-level `docs/` straddling the historical `archive/` trees); whether the cleanup sweep ships in this story or a follow-up; where the rule itself is written down (root `CLAUDE.md` vs a `docs/README.md` preamble) | medium | todo | Karel, 2026-07-21 |
| 36 | **Folder-naming realignment — `flows/` → `engine/`, top-level `catalogue-builder/` → whole-system name**: "catalogue-builder" is overloaded three ways — the top-level folder, the producer component `flows/catalogue_builder/`, and the `/catalogue-builder-run` command — so the whole-system folder claims the producer's name while `epac_builder` (consumer) is equally central. Meanwhile the docs already use **"engine"** with a precise meaning (`flows/**`: "read-only on the engine", "the engine is stdlib-only Python"), and the top folder also holds non-engine trees (`catalogue/` contract, `customer/` writable workspace, `config/`, `docs/`, `examples/`, `core/`, `skills/`). **Fix:** (a) rename `flows/` → `engine/`, aligning the folder with the established term; (b) rename top-level `catalogue-builder/` to a whole-system name — candidates: `workbench/` (fits the PolicyWorkshop metaphor), `epac-workbench/`, `policy-forge/`; avoid anything containing "builder". End state: `workbench/engine/catalogue_builder` (producer) vs `workbench/engine/epac_builder` (consumer) — each name does one job. **Sweep required:** Python import paths (`flows.epac_builder` → `engine.epac_builder`, incl. `flows/shared/paths.py`), root `README.md`/`CLAUDE.md`/`AGENTS.md`, `.mcp.json` (server command path), `.claude/commands/*`, `.github/workflows/contoso-epac-build.yml`, `examples/contoso/verify.sh`, all relative doc links, and regenerate anything that embeds paths; verify with `verify.sh` (all 3 flavours byte-identical) + MCP smoke test. Do it **before Alpha exit** — cheapest while alpha, and lands cleanly alongside the versioning decision (#27) | medium | done (2026-07-22) | Karel + Claude naming discussion, 2026-07-22 |
| 37 | **Cloud platform for the monthly catalogue-update automation (not local)**: the recurring Azure-policy-retrieval → catalogue-regeneration must run on Microsoft-hosted compute, **not a user's local device**. Productionize the currently-local pipeline — `fetch_policy_source.py --sync/--check` (**#7**, drift) + producer Phases 1–5 + a regenerate-and-diff (**#8**) — as a **scheduled runner** that publishes a new versioned catalogue plus a drift signal, on the ~monthly upstream cadence (`config/policy-source.json`, pinned `04989912`). **Key simplification vs. the retired design:** the engine is now deterministic stdlib-only (tier classification = `config/tier-rules.yaml` keyword rules, no LLM), so this needs **none** of `archive/foundry/`'s AI Foundry hub / Claude-MaaS / prompt-flow DAG — just a timer-triggered runner of the existing producer. **Salvage from `archive/foundry/` (prior art, don't rebuild from scratch):** `infra/` Bicep (user-assigned managed identity + storage + monitoring + RBAC modules) and `architecture.md`/`README.md` §ingestion (the "nightly clone `Azure/azure-policy` → normalize → storage" pattern, Azure Functions timer vs Container Apps Job). **Decisions to settle at pickup:** (a) **platform target** — GitHub Actions `schedule:` (already the CI platform, OIDC to Azure, simplest) **vs** Azure-native (Functions timer / Container Apps Job + managed identity, reuses foundry/infra) — *left open deliberately*; (b) where the regenerated catalogue lands (PR back to this repo vs. publish as the #18 read-only artifact); (c) how the run bumps `catalogueVersion` + surfaces breaking changes (ties **#27** versioning, **#15** upgrade path). Builds on / absorbs **#7** + **#8** | high | todo | Karel + Claude foundry-archival discussion, 2026-07-22 |
| 38 | **Engine unit-test layer — the only coverage today is coarse-grained**: end-to-end regression is strong (`examples/contoso/verify.sh` byte-diffs all 3 flavours + asserts the `--strict` gate; the Tier-1 validator has 7 negative tests per #33; the MCP server has a 5-assertion smoke test), but there is **no module-level test** for `expand`, `bind`, `build_ir`, the three renderers, or the producer phases individually. A break in any of those surfaces only as a global byte-diff failure with no localization, and a producer-phase regression isn't exercised in CI at all (the workflow is consumer-only). Add stdlib tests (keep `dependencies = []`) covering: manifest expand/bind edge cases, IR warning paths, per-renderer output shape, and the producer phases against a tiny fixture catalogue. Complements the golden-fixture regression rather than replacing it. Medium, ongoing | medium | todo | actions/reviews/review-07-22-26.md |
| 40 | **Compliance-benchmark coverage report for generated EPAC packages**: compare a generated customer package against a public Azure Policy compliance benchmark (CIS Microsoft Azure Foundations, ISO 27001, Microsoft Cloud Security Benchmark / MCSB, NIS2) and emit a **coverage + gap report** — which benchmark controls the package's assigned policies satisfy, which are unmet — so an engineer can reassure the customer with evidence, not just the tier prose. Anchors on the existing framework citations (`enrich_policies.py:83-87` `TIER_FRAMEWORKS`), which are today **narrative-only at tier level** with no per-policy control mapping. Azure ships each benchmark as a built-in **regulatory-compliance initiative** (policySetDefinition), so the control set is a public, versioned source of truth. **Open questions at pickup:** (a) map against Azure's built-in initiative membership vs. the framework's own control catalogue; (b) where the report lives — a plane-1 doc emitted **into** the package (per #23) vs. a maintainer/QC artifact; (c) which benchmarks to support first (MCSB is the Defender-for-Cloud default; CIS is the most-asked-for in sales). Ties #18 (tier-rationale lookups), #14 (deployability proof), #31 (front end could surface coverage). Replaces the empty `benchmarks/` scaffold folder (deleted 2026-07-23, untracked) whose four subfolder names — CIS / ISO 27001 / MCSB / NIS — seeded this idea | medium | todo | Karel, 2026-07-23 |
| 39 | **Field-type selection (greenfield / brownfield / bluefield) drives the deploy posture**: give the epac-builder user one high-level choice — is the target a **greenfield** environment (no pre-existing policy), a **brownfield** one (established, with pre-existing ALZ/hand-made policy that must not be disturbed), or a **bluefield** one (a hybrid: an existing estate being brought under EPAC management, partially owned) — instead of making them reason about EPAC's raw `desiredState.strategy`. Builds directly on **#20**, which just landed per-environment `strategy` (`full`/`ownedOnly`) + `excludedScopes` in the manifest + json renderer. **The mapping is the open question to settle when taken up:** greenfield → `strategy:"full"` (EPAC owns the scope; may delete unmanaged policy — safe because there is none); brownfield → `strategy:"ownedOnly"` (touch only what this package deploys — today's safe default); **bluefield → undecided** — likely `ownedOnly` during onboarding then a staged move toward `full` with `excludedScopes` carving out the not-yet-managed scopes, or `full` + `excludedScopes` from day one. **When the story is taken up, review exactly how the selection reflects in package creation and what it means in code vs. config:** does it become a top-level manifest field (e.g. `deploymentPosture`/`fieldType`) that *derives* the per-environment `strategy` (vs. today's explicit per-env `strategy`); is it per-environment (dev greenfield + prod brownfield is a real combo) or whole-package; does it also drive `keepDfcSecurityAssignments` / `excludedScopes` / enforcement defaults; and where the choice is made — the onboarding interview (**#16**) and any future front end (**#31**). Regenerating contoso fixtures required if the emitted `desiredState` shape changes. Ties #20 (mechanism), #16/#31 (where the choice is made), #14 (deployability proof per posture) | medium | todo | Karel, 2026-07-22 |

## Notes

- Review 2026-07-05 (`actions/reviews/review-07-05-26.md`) reconciled: confirmed #1/#1a/#1b/#4/#5/#6/#9/#10/#12
  done (re-ran the assembler; `examples/contoso` rebuilds byte-identical, all 3 flavours render).
  #2 (strict gate) and #3 (catalogue still ships `undefined` + `builtinpolicytest`) carry forward
  unchanged. One new row: #13 (Terraform/Bicep renderers uncovered by CI).
- Review 2026-07-05 (end-of-day, second pass, `actions/reviews/review-07-05-26.md` rewritten): re-ran
  `examples/contoso/verify.sh` — all three flavours byte-identical (exit 0). Confirmed **#11 and #13
  done** (verify.sh now covers json+terraform+bicep; the morning review had raised #13 as the renderer
  coverage gap — closed same day) and **#16 done** (onboarding skill + `/epac-builder-onboard` +
  `/reset-customer-package` shipped). No status flips (all already marked done) and **no new rows** —
  every finding maps to an existing item. Re-confirmed **open**: #2 (scope-less/`<REPLACE:>`-param
  manifests still build with only a `[warn]`), #3 (`undefined`-domain refs still in `index.json`;
  `builtinpolicytest` still in `definitions/` + two `initiatives/undefined/*/` dirs), #14 (deployability
  never proven — CI is byte-diff only), #15 (no catalogue-upgrade path). #14/#15 are now the two
  highest-value open items.
- Items 17–18 came from an **MCP-exposure brainstorm** (Karel + Claude, 2026-07-06) — **not** an
  `actions/reviews/` code review. Dividing line: anything that **mutates a customer package or touches the
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
- Review 2026-07-07 (`actions/reviews/review-07-07-26.md`) reconciled: re-ran `examples/contoso/verify.sh` (all
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
  `sessions/`, `reviews/`, `feedback/`) or the docs is dated 2026-07-19 or later; it was hit at runtime
  mid-session. The *prior* written position
  was the opposite and stronger claim — `flows/catalogue_builder/README.md:9` said each producer step
  "is idempotent", and `actions/reviews/review-07-07-26.md:60` called #3 "Data curation, **not a code fix**". Row
  #26 disproved both. Qualified the README claim and added the Phase-3 caveat to
  `.claude/commands/catalogue-builder-run.md` on 2026-07-20 so the trap is visible in the runbook the
  phase is actually executed from (it was recorded only in the session log + backlog before).
- Doc corrections applied 2026-07-20 alongside the above: the `contoso-epac-build.yml` header credited
  `verify.sh` with running the MCP smoke test (the *workflow* runs it, as a separate step); and
  "reclassified the **17 categories**" was wrong in three places — the enumerated list has **11**
  categories, 17 is the **policyset** count (undefined shrank 25 → 8), since several categories span
  two or three tiers.
- Item 31 (opened 2026-07-20): the **front end** is a mid/long-term product goal Karel has been
  carrying that had **no row at all** — worth recording that the gap was real, not just unwritten.
  The nearest existing items each stop short: #16 (done) is the interaction model but runs as a chat
  against a local clone; #17 is maintainer-facing stdio MCP over the working tree; #18 is a
  **read-only** catalogue lookup API — already framed for "consumers who never touch this repo",
  which is the same delivery-boundary instinct as #23, just applied to reads. None of them let
  someone *produce* a package without cloning. Sequenced after **#27** (a front end that emits
  packages to people outside this repo cannot ship until `lineage.json` can answer "which builder
  produced this?") and **#18** (its read side).
- **Retired the top-level `automation/` tree (2026-07-20)** — prompted by Karel asking whether it had
  become redundant once every rendered package started shipping its own pipeline. It had. Evidence
  before deleting: **4 files, 2,472 bytes**, of which `pipelines/epac-deploy.yml` was **0 bytes** and
  `pipelines/epac-build.yml` referenced `templates/buildDeploymentPlan.yml` **three times — a path
  that exists nowhere in the repo**, so it could never have run as committed (it also had no
  `trigger:` block). **Zero inbound references** anywhere outside the tree itself. One commit ever
  touched it — `755a774` (2026-06-28 "cleanup"), a **pure rename** from `epac/` with 0 insertions /
  0 deletions — so the content was frozen at 2026-05-23 and predates the whole catalogue-builder
  architecture. The generated `_epac_workflow` is a functional **superset**: same module and cmdlets,
  plus OIDC instead of a stored service-connection credential, three least-privilege identities
  instead of one, environment approval gates, real triggers, and a `Deploy-RolesPlan` stage the old
  templates never had (without which DINE/Modify remediation identities never receive their roles).
  Deleted with `git rm`; `755a774^` preserves the originals if ever wanted.
- Item 32 (opened 2026-07-20): opened **before** deleting `automation/`, because the tree held exactly
  one thing the generator cannot produce — the **Azure DevOps** platform target, and specifically the
  `Build-DeploymentPlans -DevOpsType "ado"` flag. That mattered more than the tree's condition
  suggested: ADO is already a **stated goal** (`docs/scaffold-deployment-guide.md` covers "GitHub
  Actions **and** Azure DevOps", whole §14), and **#14 asserted a "generated GitHub / Azure DevOps
  pipeline"** that no code produces — corrected the same day to name GitHub only and point at #32, so
  #14 is not blocked on a pipeline that does not exist. Note for whoever picks #32 up: ADO is a
  **platform** axis, not a renderer flavour, so it does not slot cleanly into the existing
  `{json, terraform, bicep}` key space — settle that modelling question before writing
  `_ado_workflow()`.
- Item 33 (2026-07-20): Karel wanted a **code-validation gate on the PR, before anything deploys**.
  Built as two tiers, both emitted **into** the package (per #23, the package is where the customer's
  PR happens; this repo is never delivered). **Tier 1** `validate-package.py` — a standalone,
  stdlib-only, credential-free script — is emitted **verbatim from its source of truth**
  `flows/epac_builder/pkgvalidate.py` (`package.py` reads and re-writes it), so the shipped copy can
  never drift and the contoso byte-diff CI proves it every run. Its headline check is **pacSelector
  coverage**: an assignment with no `scope` key for a declared pacEnvironment is *silently skipped* by
  EPAC — no error anywhere — so a policy just never exists in that environment; nothing else catches
  this. **Tier 2** is a plan-only what-if on the PR (`epac-validate.yml`), Reader identity, guarded by
  `if: …head.repo.full_name == github.repository` so **fork PRs skip rather than fail** (no secrets on
  a fork; and never `pull_request_target`, which would run untrusted code with write + secrets). Also
  added the `concurrency:` guard to `epac.yml` (queue, don't cancel — cancelling mid-reconcile leaves
  the root scope half-applied). **Key design call:** did *not* reuse the builder's stdlib
  `validate.py` for EPAC-schema conformance — the EPAC schemas use `patternProperties` / `oneOf` /
  recursive `$ref` that it doesn't implement and silently skips, so it would pass a file while
  ignoring the `scope`/`notScopes` blocks that matter most. Full schema conformance stays
  `Build-DeploymentPlans`' job (Tier 2). Validator proven with a positive test (repaired package
  passes) + 7 negative tests (coverage gap, dangling policyset ref, `<REPLACE:>`, malformed scope,
  bad GUID, unparseable file, missing custom-policy def) — each asserts the *specific* message.
  **Note the fixture interaction:** the shipped contoso package's own validator *fails* on the
  contoso package, because that fixture deliberately leaves `management/essential/tags` unmapped to
  exercise the `--strict` regression (verify.sh:44). That is correct — the fixture is a golden test
  artifact, never deployed — and it doubles as independent confirmation the validator agrees with
  `--strict`. **Left open (in the row):** terraform/bicep get no gate yet (json only);
  `managedIdentityLocation`/`logAnalyticsWorkspaceId` unvalidated on purpose.
  **Follow-up (2026-07-20):** Karel noticed the editor flagging `secrets.*` ("Context access might be
  invalid") and `environment:` values ("Value '…' is not valid") in the generated workflows — those
  are VS Code GitHub-Actions hints for customer-provided secrets/environments absent in the builder
  repo, not errors. Added a `_provisioning_note()` helper (`package.py`) that emits a short comment
  block naming each workflow's secrets/environments, pointing at `README.md`, and saying the hints
  clear once the deploy repo is set up. Applied to all four generated workflows (epac, terraform,
  bicep, epac-validate's plan job). Comment-only — `verify.sh` byte-diff still green.
- Item 34 (opened + GitHub slice shipped 2026-07-21): prompted by Karel noticing the generated
  package README has "little to no information on how to set up GitHub or DevOps to run the CI/CD",
  then extended the same session to the Azure/Entra prerequisites (`docs/azure/README.md`).
  Decision (via AskUserQuestion): the guide **ships inside the package** (`package/docs/github/`) and
  is **emitted by the generator** (not a standalone builder-repo doc), because per #23 the customer
  only ever receives the rendered package. Implemented with the existing verbatim-emit pattern:
  new source `flows/epac_builder/github_setup.md` → `_github_setup_doc()` reads it → `finalize`
  writes it to `docs/github/README.md` **json-flavour only** (gated with the `validate-package.py`
  block, since the guide is written around the epac 3-identity flow). Top-level `_epac_readme` Layout
  + a pointer line now reference it. Guide covers: repo-as-root, GitHub plan/licensing (the sharp
  edge — environment required-reviewers need a paid plan on a private repo), runners (hosted vs
  self-hosted), OIDC federated-credential **subjects** per job/environment, environments, branch
  protection + the PR gate, first-deploy order, a checklist, and a mermaid identity→role→job diagram
  (house style: a visual, GitHub-native so it needs no SVG asset). Self-contained — links only to
  official Azure/GitHub docs, never back into this repo. Regenerated the contoso json fixture; only
  `package/README.md` changed + `package/docs/github/README.md` added; `verify.sh` green (all 3
  flavours byte-identical + strict gate), MCP smoke 5/5. Note the working-tree EOL: `write_text`
  emits CRLF on Windows while the `.md` source is LF, but `core.autocrlf=true` normalises both to LF
  in the index (same as `validate-package.py`, `i/lf w/crlf`), so the Linux-CI byte-diff holds.
- Item 35 (opened 2026-07-21): came directly out of the #34 review — Karel saw the two in-repo
  copies of the GitHub guide (`github_setup.md` source + the contoso fixture render) and pushed back
  on the idea of inlining a ~200-line explanation into `package.py`. Resolved by naming **two
  documentation planes**: customer/package docs (emitted, delivered — `github_setup.md` is correctly
  a standalone template, **left as-is**) vs engine/maintainer docs (never shipped). The general rule —
  high-level inline + `See: docs/…` reference, detail in a central `catalogue-builder/docs/` library
  with an index — is captured as this story rather than refactored now. Ties to #34 (the plane-1
  example) and overlaps the builder-side `scaffold-deployment-guide.md` (plane-2), which the story
  should reconcile. No engine/fixture change was made under this row.
- Item 36 (done 2026-07-22): executed the two renames on `alpha/epac-builder/folder-realign` —
  `catalogue-builder/` → **`epac-workbench/`** (chosen over `workbench/`/`policy-forge/` for being
  self-describing against the `epac_builder` component) and `flows/` → **`engine/`**. End state:
  `epac-workbench/engine/catalogue_builder` (producer) · `epac-workbench/engine/epac_builder` (consumer).
  **Confirmed no code breaks:** every module derives its root relatively (`parents[N]`,
  `dirname(dirname(__file__))`) and imports siblings by bare package name — no dotted `flows.` import,
  no literal `"flows"`/`"catalogue-builder"` path join, and the rename preserves depth. Two `git mv`
  (history preserved) + string sweeps. **Sweep discipline:** replaced only *path* refs — `\bflows/`
  (word boundary, so `.github/workflows/` is untouched) → `engine/`, and `catalogue-builder/`
  (trailing slash = path) → `epac-workbench/`; **kept** producer-component prose (`/catalogue-builder-run`
  command ×25, "catalogue-builder (producer)" ×4, `pyproject.toml name = "catalogue-builder"`). **Catalogue
  regen** was surgical: swept the engine `.py`/`.md` provenance strings, then re-ran Phases 3→4→5 from the
  on-disk `.policy-source` cache with `--version 2026.07.18` (pinned so the rename stays semantically
  neutral — default would have bumped to today). Verified the catalogue diff is *exactly* the rename:
  file-count parity 1121↔1121 (no #26 orphans), **189 initiative `.md` differ only by the `flows/`→`engine/`
  provenance line (0 non-provenance diffs)**, `catalogue.json` changed only in `generatedAt` + the four
  tool-file hashes + `contentHash`, and **no `.policyset.json`/`.assignment.json` changed**. **Verified:**
  `verify.sh` green (json/terraform/bicep byte-identical to committed fixtures + strict gate fires — so the
  package output is unaffected, no fixture regen needed), MCP smoke 5/5, `check_env.py` exit 0, final
  full-tree grep = 0 stray path refs. **Follow-up (settled 2026-07-22):** `pyproject.toml`
  `name` bumped `catalogue-builder` → `epac-workbench` (+ header comment) — the whole-system project
  identifier; nothing functional reads it (not hashed into the catalogue), so no regen. **Note:** the
  running Claude Code MCP server still points at the old `.mcp.json` path until an MCP reload/restart.
- Item 37 (opened 2026-07-22): came out of archiving `foundry/`. Foundry was the **Azure AI Foundry
  prompt-flow** architecture — an LLM-based taxonomy pipeline (two Claude-MaaS nodes) + Bicep infra,
  built on the premise "tier classification needs an LLM". That premise is **superseded** (the engine now
  classifies deterministically from `config/tier-rules.yaml`), and it was never deployed — so it was
  archived, not kept. **#37 preserves the one piece with forward value:** foundry's `infra/` Bicep (UAMI +
  storage + monitoring + RBAC) and its documented ingestion job (nightly `Azure/azure-policy` clone on a
  timer) are prior art for the recurring cloud catalogue-update automation. Crucially the platform is
  **much lighter than foundry** now — no AI Foundry hub / no LLM — because the producer is deterministic
  stdlib Python. #37 is the cloud/platform productionization of #7 (drift-sync) + #8 (regenerate-and-diff);
  platform target (GitHub Actions vs Azure-native) left open per Karel.
- Review 2026-07-22 (`actions/reviews/review-07-22-26.md`) reconciled: a full state check (not a diff
  review) on `alpha/epac-builder/folder-realign`. Verified the core path works end-to-end today —
  `verify.sh` green (all 3 flavours byte-identical + strict gate fires), MCP smoke 5/5, `check_env`
  exit 0, and **remote CI success** on this branch. **#36 confirmed done** (folder realign — no stray
  path refs, package output unaffected). **No status flips** — every open row re-confirmed open. One
  new row: **#38** (engine unit-test layer — golden-fixture regression is strong but coarse, no
  module-level tests, producer phases untested in CI). **Sharpest finding, no new row:** the json
  renderer on *this* branch is still EPAC-rejected because the **#20** fixes were **never committed to
  this repo** — verified no branch tip carries them (every `render_json.py` emits flat
  `policySetDefinitionName`; there is no `alpha/epac-builder/demo` branch); they existed only as a
  manual patch in a consumer's working tree on another device. Landing #20 is the smallest-effort /
  highest-value unblock (generate
  works; deploy-unmodified does not until #20 lands). Ranked blockers in the review: #20 (low) → #26
  (low) → #21 (medium) → #27 (decision spike) → #14 (tenant) → #38 (ongoing).
- Item 20 (done 2026-07-22): landed both renderer fixes that made EPAC 11.4.7 reject the generated
  json package, closing the "generates vs. deploys" gap the 07-22 review named as the top blocker.
  **(a)** `render_json._write_global_settings` now emits `desiredState` inside each `pacEnvironment`
  with a **brownfield-safe default** (`strategy:"ownedOnly"`, `keepDfcSecurityAssignments:false`) — so
  EPAC no longer defaults to the destructive `full` that would propose deleting a tenant's
  pre-existing policy; `strategy` (+ optional `excludedScopes`) is now a per-environment manifest
  field (both schemas) threaded through `ir._env`. **(b)** `render_json._assignment` emits
  `definitionEntry.policySetName` instead of flat top-level `policySetDefinitionName`. **Crucial
  side-fix:** `pkgvalidate.check_references` was reading only `policySetDefinitionName` and *skipping*
  `definitionEntry` shapes — left unchanged, the shipped `validate-package.py` would have silently
  stopped checking assignment→policyset integrity; it now reads both. **Scope finding:** json-only —
  the terraform/bicep renderers emit native `azurerm`/`Microsoft.Authorization` resources with no
  `desiredState`/`policySetName` concept, so #20(b)'s "review tf/bicep for the same shape" resolves to
  "they don't share it." **Verified:** `verify.sh` green (all 3 flavours byte-identical after
  regenerating the contoso json fixture — global-settings + 2 assignments + the validator copy + strict
  gate fires), MCP smoke 5/5, and two targeted validator probes (good package resolves the new shape
  with no false error; a broken `policySetName` is still caught). **Note the provenance correction:**
  these fixes were **never committed to this repo** before now — verified no branch tip carried them;
  they had existed only as a consumer's local hand-patch on another device (see review-07-22-26.md).
  contoso deliberately stays on the `ownedOnly` default, proving the safe path is the zero-config one.
- Item 39 (opened 2026-07-22): came straight out of shipping #20. #20 exposed EPAC's raw
  `strategy` (`full`/`ownedOnly`) as a manifest field, but a user shouldn't have to reason in EPAC
  reconciliation terms — they know whether their environment is **greenfield** (new), **brownfield**
  (established, don't disturb), or **bluefield** (existing estate being brought under management). #39
  is the higher-level selection that maps onto #20's mechanism. greenfield→`full`, brownfield→
  `ownedOnly` are clear; **bluefield is the one to think hard about** (staged `ownedOnly`→`full` with
  `excludedScopes`, vs. `full`+`excludedScopes` from the start). Per Karel: **when the story is taken
  up, review how the selection reflects in package creation and what it means in code vs. config** —
  top-level field deriving per-env `strategy` vs. explicit per-env; per-environment vs. whole-package;
  and where the choice surfaces (#16 onboarding, #31 front end).
- Re-run `actions/review-prompt.md` periodically; reconcile new findings into this table.
