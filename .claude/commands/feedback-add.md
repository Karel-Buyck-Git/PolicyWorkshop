---
description: Capture a consumer feedback log in actions/feedback/ after a real consumer exercise (onboarding dry-run, demo build, tenant deploy), then reconcile findings into the backlog. Manual only.
argument-hint: "[who the consumer was + what they did; e.g. 'vandelabr tried a real onboarding']"
disable-model-invocation: true
---

Today: !`date +%m-%d-%y`

Capture feedback from a **real consumer exercise** — someone (not the maintainer) actually drove
epac-builder against a real goal, and hit real friction. $ARGUMENTS describes who and what.

This is not a code review (`/review` does that, into `actions/log/`). The value of a feedback log is
that it records what *actually happened to a real user* — their commands, their errors, their
workarounds — so findings can be traced back to lived evidence rather than inspection.

1. **Resolve the target file.** `actions/feedback/consumer-feedback-<who>-<MM-DD-YY>.md`, using the
   date above. `<who>` is the consumer/tenant/exercise slug (e.g. `demo`, `vandelabr`) — take it
   from $ARGUMENTS, and **ask** if it isn't clear. Do not invent one.

   **If that file already exists, do not overwrite it.** Offer to append a new dated section to the
   existing file instead, or to pick a different slug. (A same-date collision silently clobbering
   the earlier file is exactly what bit `/review` — see `actions/sessions/2026-07-05.md:232`.)

2. **Gather the content.** Ask for whatever $ARGUMENTS doesn't already give you — don't guess at
   facts a consumer reported. At minimum: the goal, what they ran, what broke or surprised them,
   what they worked around, and where they ended up.

3. **Write the file** in the house shape (see `actions/feedback/consumer-feedback-demo-07-07-26.md`):

   - `# <Name> — Session Feedback Log` heading
   - **Date** / **Goal** / **Status** bold fields
   - a **Reference values** table when the exercise involved concrete config (customer/prefix,
     `pacOwnerId`, tenant, root scope, pacSelector, enforcement, region, policy selection, repo,
     branch) — this is what makes the log reusable when someone picks the work up elsewhere
   - then numbered **Finding** sections: what happened, why it matters, and the file/line evidence
     where known

   **Redaction check before writing:** these logs routinely carry tenant GUIDs, management-group
   ids, service-principal client ids and workspace resource ids. This repo is public. Flag any
   value that looks like a live secret (client *secrets*, connection strings, tokens) and leave it
   out — identifiers are the consumer's call, secrets are never written. See backlog **#28**, which
   tracks this exact exposure question.

4. **Reconcile into `actions/backlog.md`.** For each finding worth tracking, add a row using the
   `/backlog-add` shape (`# | Item | Effort | Status | Source`), with **Source =** the new
   `actions/feedback/…` path. Append rows at the end of the table — never renumber or reorder.
   Apply the same duplicate guard `/backlog-add` uses: if a row already covers it, surface that row
   and ask rather than adding a near-duplicate.

5. **Report** the file written and the backlog ids added. **Do not stage or commit anything** —
   that's the author's call, same as every other command here.
