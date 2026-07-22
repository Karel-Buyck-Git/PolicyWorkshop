# Contributing to the `cloud-adoption-framework` skill

This skill provides governance-focused Cloud Adoption Framework guidance (Ready + Govern/Secure/Manage). It is plain Markdown, so it fits git and an agile loop well — readable diffs, fast reviews, trivial builds. Our tests are **prompts**, not unit tests.

## What's in here

```
cloud-adoption-framework/
├── SKILL.md                       # router + tier sequencing + the boundary with `epac`
├── references/
│   ├── ready-landing-zones.md     # Tier 1 — Ready: design areas & landing zones
│   ├── govern.md                  # Tier 2 — Govern: the 5-step governance cycle
│   ├── secure.md                  # Tier 3 — Secure: posture, incident, CIA, sustain
│   ├── manage.md                  # Tier 4 — Manage: operations baseline & resilience
│   ├── deliverables.md            # Markdown templates for governance artifacts
│   └── source-map.md              # live-fetch index: which CAF URL for which question
├── evals/evals.json               # the prompt suite = our regression tests
├── build.ps1 / build.sh           # package SKILL.md + references → dist/cloud-adoption-framework.skill
├── azure-pipelines.yml            # CI: build .skill on a caf-v* tag (Azure DevOps)
└── .github/workflows/build.yml    # CI: build .skill on a caf-v* tag (GitHub Actions)
```

Only `SKILL.md` + `references/` ship in the `.skill`; the build scripts exclude everything else.

## Design rules

- **Live-fetch, don't snapshot.** Reference files capture *how to think* and *where to look* (`source-map.md`), not copies of CAF pages that rot. CAF gets reorganized — pointers age better than prose.
- **Stay on the CAF side of the boundary.** This skill is methodology and design (*what/why/where*). The moment an answer needs Azure Policy code or an EPAC deployment, hand off to the **`epac`** skill. Don't duplicate policy mechanics here.
- **Tie controls to risks.** CAF governance derives policy statements from assessed risks — keep that discipline in the content.
- **Cite CAF sources** for every methodology claim.
- **Keep SKILL.md lean** (< 500 lines); push detail into references.
- **Explain the *why*** rather than issuing rigid rules.

## Branching & PR flow (trunk-based, small batches)

1. `main` is always shippable — it is the `.skill` colleagues have installed.
2. Branch per change, scoped small: `feat/secure-zero-trust`, `fix/govern-raci`, `docs/ops-baseline`.
3. Open a PR. **Review behaviour, not just the diff** — run the affected `evals/` prompt(s) with the branch's skill and judge the *output*, including whether the `epac` hand-off fires correctly.
4. Merge fast, keep batches small.

## Backlog = prompts

Frame work as user stories: *"When I ask <X>, I get <Y>."* Each becomes (a) a prompt in `evals/evals.json` and (b) the reference content that answers it well. Weak answers reported in the test environment become new prompts — permanent regression tests. Pay special attention to **boundary prompts** (evals 5 and 10) that check the skill routes implementation work to `epac` instead of doing it here.

## Definition of done

- The affected `evals/` prompt(s) produce good output with the skill.
- Implementation requests are handed to `epac`, not answered with policy code here.
- CAF claims have fetch pointers / citations, not hard-coded snapshots.
- `SKILL.md` still routes correctly and stays lean.
- `build.ps1`/`build.sh` runs clean; the `.skill` contains only `SKILL.md` + `references/`.

## Build & test locally

```powershell
pwsh ./build.ps1            # → dist/cloud-adoption-framework.skill
```
```bash
./build.sh                  # → dist/cloud-adoption-framework.skill
```

Install the `.skill` in your Claude client and run a few `evals/` prompts. Install the `epac` skill alongside it to test the hand-off between the two.

## Versioning & release

- Bump the version on meaningful changes (semver). Track in the tag (and in `plugin.json` once these skills are promoted to the `azure-cloud-solutions` plugin).
- Tag releases with the `caf-` prefix so this skill's tags don't collide with `epac`'s in the same repo: `git tag caf-v1.1.0 && git push --tags`. CI builds and publishes the `.skill`.

## Cadence & ownership

Short loop (one-week iterations). Name a **skill owner** who merges and curates so `SKILL.md` stays coherent and the `epac` boundary stays clean. Install in the test environment → real tasks → gaps become new `evals/` prompts → next iteration.
