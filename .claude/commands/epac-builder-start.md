---
description: Daily start-of-session ritual for catalogue-builder — health-checks the engine, then orients on the backlog and last session. Run this first each day. Manual only.
disable-model-invocation: true
---

## 1. Health check

Two parts: prove the **engine** is sound (against the golden fixture), then check the
**customer's** live inputs (dynamic — the empty scaffold reports "not configured", it is
not an error). Run everything from `catalogue-builder/`.

**Engine baseline (always).** Run the same regression check CI (`contoso epac build`) runs,
locally — it rebuilds the worked sample for every flavour and diffs byte-for-byte:

\`\`\`
cd catalogue-builder
bash examples/contoso/verify.sh
\`\`\`

Report pass/fail. If it fails, show the diff and **stop here** — don't start new work on a
broken engine; fixing it is the top priority instead.

**Customer readiness (dynamic).** Now check the user's own working area, `customer/`. Look
in `customer/manifests/` for a real, filled manifest — a `*.jsonc` that is **not**
`manifest.template.jsonc` and has **no surviving `<REPLACE:` placeholders**:

- **If one exists**, validate it against the engine (validates + reports, writes nothing):

  \`\`\`
  python flows/epac_builder/assemble_scaffold.py --manifest customer/manifests/<name>.jsonc --check
  \`\`\`

  Report pass/fail (and surface any placeholder-scope or `<REPLACE:>` warnings).

- **If none exists** (only the template is present, or every manifest still carries
  `<REPLACE:>` placeholders), report: **"customer/ is an empty scaffold — not configured
  yet."** This is the expected state on a fresh clone; it is not a failure, and there is
  nothing to build.

## 2. Orient

If the health check passed, read `actions/backlog.md` and the most recent file in
`actions/sessions/` (dated `YYYY-MM-DD.md`, take the latest). Summarize briefly:

- Where things left off, from that session log's "Next" section
- The top 2-3 open backlog items (status `todo`), lowest effort first, unless
  something is explicitly blocking

Ask which one I want to work on, or propose the highest-priority item if I don't say.
Don't start making changes yet.
