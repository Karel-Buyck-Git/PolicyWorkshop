# Contributing to the `epac` skill

This skill helps Azure team members set up, author, deploy, and operate Azure Policy in landing zones. It is plain Markdown, so it fits git and an agile loop unusually well — readable diffs, fast reviews, trivial builds. The one difference from normal code: **our tests are prompts, not unit tests**.

## What's in here

```
epac/
├── SKILL.md                     # router + tier sequencing (the skill's "brain")
├── references/                  # the tiers + cross-cutting knowledge (loaded on demand)
│   ├── foundations.md           # Tier 1 — Azure scope / MG / RBAC / evaluation
│   ├── caf-alz-architecture.md  # Tier 2 — landing-zone design & guardrail placement
│   ├── networking-guardrails.md # Tier 3 — guardrail patterns (NSG, public IP, App Gw/WAF…)
│   ├── epac-operations.md       # Tier 4 — EPAC deploy & ops
│   ├── policy-authoring.md      # cross-cutting — JSON, effects, aliases, debugging
│   ├── docs-and-runbooks.md     # cross-cutting — Markdown deliverable templates
│   └── source-map.md            # live-fetch index: which URL to fetch for which question
├── evals/evals.json             # the prompt suite = our regression tests
├── build.ps1 / build.sh         # package SKILL.md + references → dist/epac.skill
├── azure-pipelines.yml          # CI: build .skill on tag (Azure DevOps)
└── .github/workflows/build.yml  # CI: build .skill on tag (GitHub Actions)
```

Only `SKILL.md` + `references/` ship in the `.skill`. The build scripts exclude everything else, so dev tooling never reaches users.

## The design rules (keep the skill good)

- **Live-fetch, don't snapshot.** The reference files capture *how to think* and *where to look* (`source-map.md`), not copies of Microsoft docs that rot. If you're tempted to paste a built-in policy's full JSON, add a fetch pointer instead.
- **Cite sources.** Every Azure-specific claim should be traceable to a fetched URL.
- **Tiers are reference files, not separate skills.** Progressive disclosure loads only the tier a task needs. Add depth by enriching a tier file; only split a tier into its own skill (under the `azure-cloud-solutions` plugin) once it outgrows a reference file or gets a distinct audience.
- **Keep SKILL.md lean** (ideally < 500 lines). Push detail down into references.
- **Explain the *why*.** Prefer reasoning over rigid MUST/NEVER rules — the model follows intent better than edicts.

## Branching & PR flow (trunk-based, small batches)

1. `main` is always shippable — it is the `.skill` colleagues have installed.
2. Branch per change, scoped small: `feat/app-gateway-waf`, `fix/dine-remediation-debug`, `docs/onboarding`.
3. Open a PR. **Review behaviour, not just the diff** — the reviewer runs the affected prompt(s) from `evals/` with the branch's skill and judges the *output*. A wording change that reads fine can still make Claude behave worse.
4. Merge fast, keep batches small.

## Backlog = prompts

Frame work as user stories in the team's own voice: *"When I ask <X>, I get <Y>."* Each story becomes (a) a prompt in `evals/evals.json` and (b) the reference content that makes the skill answer it well. When someone reports a weak answer, add that prompt — it becomes a permanent regression test.

## Definition of done

- The affected `evals/` prompt(s) produce good output when run with the skill.
- New Azure facts have fetch pointers / citations, not hard-coded snapshots.
- `SKILL.md` still routes correctly and stays lean.
- `build.ps1` (or `build.sh`) runs clean and the `.skill` contains only `SKILL.md` + `references/`.

## Build & test locally

```powershell
# Windows
pwsh ./build.ps1            # produces dist/epac.skill
```
```bash
# macOS / Linux / WSL
./build.sh                  # produces dist/epac.skill
```

Then install `dist/epac.skill` in your Claude client and run a few `evals/` prompts by hand. For a structured review of many prompts at once, use the skill-creator tooling to batch-run `evals/evals.json` and generate a side-by-side review page.

## Versioning & release

- Bump the version when behaviour changes meaningfully (semver). Track it in the tag and, once you promote this to a plugin, in `plugin.json`.
- Tag releases: `git tag v1.1.0 && git push --tags`. CI builds `epac.skill` and publishes it as the release artifact.
- "Everyone's on v1.1.0" is your reference point when collecting test-environment feedback.

## Cadence & ownership

Run a short loop (a one-week iteration is plenty). Name one **skill owner** who merges and curates so `SKILL.md` stays coherent and the content doesn't bloat. Install in the test environment → colleagues hit real tasks → gaps become new `evals/` prompts → next iteration.
