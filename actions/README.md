# actions/ — continuous-improvement loop

How work on catalogue-builder / epac-builder gets planned and tracked across sessions
and contributors.

## The loop

1. **Start of session** — run `/epac-builder-start` (Claude Code slash command). It
   health-checks the engine (the same diff CI runs) then reads `backlog.md` and the
   latest `sessions/` file for instant orientation. No need to re-derive project state
   from scratch, and you find out immediately if something's broken before you start.
2. **Work an item** from the backlog (or something new that comes up). Run `/continue`
   any time mid-session (or later the same day) if you need the same orientation again
   without the health check. **Grooming:** new items enter consistently via `/backlog-add`
   (enforces the row shape + a source, flags duplicates); closed items leave the working
   table via `/backlog-archive` (moves `done` rows to `backlog-archive.md`, ids preserved).
3. **End of session** — run `/close`. Writes `sessions/<date>.md` (what changed, what's
   next, open questions), reconciles anything finished into `backlog.md`, and checks
   `git status` (including a `__pycache__` sanity check) before you walk away.
4. **Periodically** (before merging a feature branch to `main`, or every few sessions)
   run `/review` — re-runs the full audit against the codebase, saves the dated output
   to `actions/log/`, and reconciles findings into `backlog.md` — close finished items, add new
   ones. Heavier than the other two; not a daily command.
5. **After a real consumer exercise** — someone other than the maintainer drove the builder
   against a real goal — run `/feedback-add`. Writes a dated log to `actions/feedback/` (what
   they ran, what broke, what they worked around) and reconciles findings into `backlog.md`.
   Kept separate from `log/` on purpose: reviews are *inspection*, feedback is *lived evidence*.

### Slash commands

| Command | When | What it does |
|---|---|---|
| `/epac-builder-start` | Start of every day | Health check (golden-fixture diff) + orientation (backlog + last session) |
| `/continue` | Any time you need a reminder | Orientation only, no health check |
| `/close` | End of every session | Writes the session log, reconciles finished items into the backlog, checks `git status` |
| `/review` | Periodically (pre-merge, weekly) | Full state/functionality/readiness audit, saved to `log/` and reconciled into the backlog |
| `/feedback-add` | After a real consumer exercise | Writes a dated consumer feedback log to `feedback/`, reconciles findings into the backlog |
| `/backlog-add` | When a new item comes up | Adds one well-formed backlog row (shape + required source, duplicate guard) |
| `/backlog-archive` | When the table gets long | Moves `done` rows (and their completion notes) to `backlog-archive.md`; ids never renumbered |

Defined in `.claude/commands/` — plain markdown, so they're easy to read or tweak
directly. If you're not using Claude Code, `review-prompt.md` has the same review
prompt in copy-paste form.

## Before committing

- **No `__pycache__`.** It keeps sneaking into commits (34 `.pyc` files are already
  tracked under `catalogue-builder/` as of 2026-07-03 — there's no `.gitignore` yet).
  Run `git status` before committing and make sure no `__pycache__/` paths are staged.
  One-time cleanup + a real `.gitignore` fix is tracked as backlog #1b.

## Automated safety net

`.github/workflows/contoso-epac-build.yml` (the `contoso epac build` check) runs on every
push/PR touching the engine (`flows/**`), the catalogue, the example, or the shared schemas.
It calls `examples/contoso/verify.sh`, which rebuilds the worked sample for every renderer
flavour (json, terraform, bicep) and diffs each byte-for-byte against the committed fixtures.
Any drift in the assembler's output fails the build. This runs regardless of whether the loop
above is followed — it's the floor, not the plan.

## Files

| File | Purpose |
|---|---|
| `backlog.md` | Prioritized, status-tracked action items (the working table) |
| `backlog-archive.md` | Closed items moved out of `backlog.md`, kept verbatim with original ids |
| `sessions/` | One file per work session — what happened, what's next |
| `log/` | Dated `/review` audits — periodic inspection of the codebase (`review-<MM-DD-YY>.md`) |
| `feedback/` | Dated consumer feedback logs — what a real user hit driving the builder (`consumer-feedback-<who>-<MM-DD-YY>.md`) |
| `review-prompt.md` | Reusable prompt to re-run a full state/functionality/readiness review |

## Why plain markdown

Everything here is git-tracked markdown — readable and editable with or without Claude
Code, so a colleague can pick up state without adopting any particular tool.
