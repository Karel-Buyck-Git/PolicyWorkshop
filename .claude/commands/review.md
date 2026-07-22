---
description: Run a full state/functionality/readiness review of epac-workbench (or another path), save it to actions/reviews/, and reconcile findings into the backlog. Heavier than /continue — run periodically, not every session. Manual only.
argument-hint: "[path to review, default epac-workbench/]"
disable-model-invocation: true
---

Today: !`date +%m-%d-%y`

Explore the codebase at $ARGUMENTS — if that's empty, use `epac-workbench/`. It's
"epac builder", an engine that scaffolds Enterprise Policy as Code (EPAC) setups for
Azure customers.

Do the following:

1. Map the structure: entry points, core modules, dependencies, and how a user would
   actually invoke this to generate a scaffold.
2. Check for tests, CI config, and documentation (README, inline comments, TODOs).
3. Skim recent git history for signs of active vs. stalled development.

Then give an assessment covering:

- State: what's built vs. stubbed/incomplete
- Functionality: does the core scaffold-generation path actually work end-to-end?
- Readiness: could a real customer use this today? If not, list the top blockers,
  ranked by effort to fix.

Keep it to bullet points I can act on — no restating the code back to me.

Save the result to `actions/reviews/review-<today's date>.md` (use the date above, format
MM-DD-YY). Then open `actions/backlog.md` and reconcile: mark items this review
confirms are done, add rows for anything new, leave everything else as-is.
