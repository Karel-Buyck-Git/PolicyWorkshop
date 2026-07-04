---
description: Daily start-of-session ritual for catalogue-builder — health-checks the engine, then orients on the backlog and last session. Run this first each day. Manual only.
disable-model-invocation: true
---

## 1. Health check

Run the same regression check `.github/workflows/test.yml` runs, locally, so you know
the baseline is good before changing anything:

\`\`\`
cd catalogue-builder
python flows/epac_builder/assemble_scaffold.py --manifest customer/manifests/manifest.example.jsonc --out /tmp/epac-health-check
diff -rq /tmp/epac-health-check customer/package
\`\`\`

Report pass/fail. If it fails,
show the diff and stop here — don't start new work on a broken baseline; that's the
top priority instead.

## 2. Orient

If the health check passed, read `actions/backlog.md` and the most recent file in
`actions/sessions/` (dated `YYYY-MM-DD.md`, take the latest). Summarize briefly:

- Where things left off, from that session log's "Next" section
- The top 2-3 open backlog items (status `todo`), lowest effort first, unless
  something is explicitly blocking

Ask which one I want to work on, or propose the highest-priority item if I don't say.
Don't start making changes yet.
