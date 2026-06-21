# epac — Azure Policy & Landing Zone skill

A Claude skill that helps Azure team members **set up, author, deploy, and operate Azure Policy in landing zones**, with the CAF/architecture background needed to do it correctly. It layers knowledge in tiers and live-fetches the official sources (Azure Policy repo, EPAC docs, Cloud Adoption Framework), citing them in every answer.

## Tiers

| Tier | Covers |
|---|---|
| 1 — Foundations | Azure scope model, management groups, RBAC vs Policy, how evaluation works |
| 2 — CAF / ALZ | Landing-zone hierarchy, design areas, guardrail placement, ALZ baseline |
| 3 — Networking & management guardrails | Regions/tags, NSG, public IP, Application Gateway/WAF, diagnostics, Defender |
| 4 — EPAC deployment & ops | Repo layout, desired state, plan→deploy flow, ALZ sync, CI/CD, remediation |

Tiers are reference files loaded on demand — a focused EPAC question doesn't drag in the foundations, and a design question doesn't pull deployment mechanics.

## Try it (test environment)

1. Build the skill: `pwsh ./build.ps1` (or `./build.sh`) → produces `dist/epac.skill`.
2. Install `dist/epac.skill` in your Claude client.
3. Ask something real, e.g. *"Propose the MG hierarchy for a new landing zone and tell me which guardrails go at Corp vs Online,"* or *"Walk me through deploying this deny policy with EPAC from epac-dev to tenant01."*

## Share with colleagues

Send them the built `dist/epac.skill` file — they install it directly, nothing to unpack. (A `.skill` is just a zip with `SKILL.md` at its root; rename to `.zip` to inspect.)

## Develop it

See `CONTRIBUTING.md` for the git + agile workflow (trunk-based branches, prompt-based tests in `evals/`, review-the-behaviour PRs, release on tag). CI for both Azure DevOps (`azure-pipelines.yml`) and GitHub Actions (`.github/workflows/build.yml`) builds the `.skill` on a version tag.

## Growth path

When a tier outgrows a reference file or gains a distinct audience, promote it to its own skill under the `azure-cloud-solutions` plugin — reference files and skills share nearly the same structure, so it's a copy, not a rewrite.
