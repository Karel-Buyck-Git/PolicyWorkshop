# cloud-adoption-framework — CAF governance skill

A Claude skill that gives **governance-focused Cloud Adoption Framework guidance** — landing-zone readiness plus the Govern, Secure, and Manage methodologies. It serves architects and governance leads who need the methodology and design reasoning (the *what, why, and where*), and live-fetches the official CAF docs, citing them in every answer.

It is the design counterpart to the **`epac`** skill: CAF decides what to govern and why; `epac` implements it as Azure Policy.

## Tiers (governance-leaning slice of CAF)

| Tier | CAF methodology |
|---|---|
| 1 — Ready | Landing zones, design areas, Azure environment setup |
| 2 — Govern | The 5-step cycle: team → assess risks → document policies → enforce → monitor |
| 3 — Secure | Posture modernization, incident readiness, CIA triad, Zero Trust / Defender |
| 4 — Manage | Operations baseline, business commitments, monitoring, protect & recover |

Strategy/Plan/Adopt are out of primary scope (pointers in `references/source-map.md`).

## The boundary with `epac`

This skill stops at design intent. When an answer needs Azure Policy JSON or an EPAC pipeline, it hands off to the `epac` skill. Install both so the hand-off works — together they cover governance end to end: *decide → enforce*.

## Try it (test environment)

1. Build: `pwsh ./build.ps1` (or `./build.sh`) → `dist/cloud-adoption-framework.skill`.
2. Install it in your Claude client (alongside `epac`).
3. Ask something real, e.g. *"How do we stand up cloud governance from scratch?"* or *"Walk me through the CAF Ready design areas for a new environment."*

## Share with colleagues

Send the built `dist/cloud-adoption-framework.skill` — they install it directly. (A `.skill` is just a zip with `SKILL.md` at its root.)

## Develop it

See `CONTRIBUTING.md` for the git + agile workflow (trunk-based branches, prompt-based tests in `evals/`, review-the-behaviour PRs, release on `caf-v*` tags). CI for both Azure DevOps and GitHub Actions builds the `.skill` on a tag.

## Where it sits

One of the sibling skills under `azure-cloud-solutions/` (alongside `epac-claude-01`, and the planned `alz-management` / `alz-networking`). When you're ready, these can be grouped into an `azure-cloud-solutions` plugin so they install together.
