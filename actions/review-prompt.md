# Reusable review prompt

If you're using Claude Code in this repo, just run `/review` — it's the same prompt as
a slash command (`.claude/commands/review.md`), with the date and backlog reconciliation
already wired in.

This file is the portable fallback: copy it into a fresh session (Claude Code, claude.ai,
or otherwise) to re-run a full state/functionality/readiness review of catalogue-builder.
Re-run periodically — before merging a feature branch to `main`, or every few sessions.
Save the output to `log/review-<MM-DD-YY>.md`, then reconcile findings into
`actions/backlog.md`.

---

Explore the codebase at catalogue-builder/. It's "epac builder" — an engine that scaffolds
Enterprise Policy as Code (EPAC) setups for Azure customers.

Do the following:

1. Map the structure: entry points, core modules, dependencies, and how a user
   would actually invoke this to generate a scaffold.
2. Check for tests, CI config, and documentation (README, inline comments, TODOs).
3. Skim recent git history for signs of active vs. stalled development.

Then give me an assessment covering:

- State: what's built vs. stubbed/incomplete
- Functionality: does the core scaffold-generation path actually work end-to-end?
- Readiness: could a real customer use this today? If not, list the top 3
  blockers, ranked by effort to fix.

Keep the assessment to bullet points I can act on — no restating the code back to me.

Save the output to `log/review-<MM-DD-YY>.md`.
