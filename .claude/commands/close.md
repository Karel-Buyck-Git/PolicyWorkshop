---
description: Close out a work session cleanly — writes the session log, reconciles anything finished into the backlog, and checks git status before you walk away. Manual only.
argument-hint: "[optional: anything you want called out in the log]"
disable-model-invocation: true
---

Today: !`date +%Y-%m-%d`

Close out this session:

1. Write `actions/sessions/<today's date>.md` (filename format `YYYY-MM-DD.md`,
   matching the existing files) with three sections:
   - **Done** — what actually changed this session
   - **Next** — what's still open, in priority order
   - **Open questions** — anything unresolved the next session (you or a colleague)
     needs to know
   If $ARGUMENTS is non-empty, make sure it's reflected somewhere in the log.
   If a log for today already exists, extend it rather than overwriting.

2. If anything worked on this session maps to a row in `actions/backlog.md`, update its
   status (`todo` → `in-progress` → `done`) to match reality. This is a light touch-up,
   not a full audit — that's what `/review` is for.

3. Run `git status --short` and report:
   - Any `__pycache__`/`.pyc` paths staged or modified (shouldn't happen now that
     `.gitignore` covers it — flag it if it does, something's off)
   - Everything else uncommitted, just listed. Don't stage or commit anything yourself.

4. Give a one-paragraph summary of the session and confirm the log file was written.
