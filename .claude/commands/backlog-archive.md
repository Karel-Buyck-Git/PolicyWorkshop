---
description: Move done rows out of actions/backlog.md into actions/backlog-archive.md — keeps the working table lean without losing the audit trail or breaking id references. Manual only.
argument-hint: "[optional: specific ids to archive, e.g. 2 11 17; default = all done rows]"
disable-model-invocation: true
---

Today: !`date +%Y-%m-%d`

Archive closed backlog items. $ARGUMENTS (optional) is a list of ids to archive; if empty,
archive **every row whose Status is `done`**.

1. Read `actions/backlog.md`. Select the rows to move: the ids in $ARGUMENTS, or — if $ARGUMENTS
   is empty — all rows with Status `done`. If nothing matches, say so and stop.

2. Read (or create) `actions/backlog-archive.md`. If creating it, start with the standard header
   (see below). Under a `## Archived <today's date>` heading, append each selected row
   **verbatim** — same five columns, **same original `#`**. This is the audit trail; the ids stay
   permanent because `actions/log/` reviews and `actions/sessions/` cite them.

3. For each archived row, also move its **dedicated completion note** if one exists — the
   `## Notes` bullets that begin `Item N (done …)` / `Item N …` and speak only to that row — into
   the archive directly under its row. **Leave cross-cutting notes in `backlog.md`**: review-
   reconciliation entries, the local-vs-HTTP dividing-line note, the "re-run review-prompt" bullet,
   and anything referencing still-open items. When a note is ambiguous, **keep it in `backlog.md`**
   and call it out in the report.

4. Remove the archived rows (and their moved notes) from `actions/backlog.md`. **Do not renumber**
   — neither the archived ids nor the remaining ones. Reordering the surviving rows is fine only if
   it changes no id.

5. Report: which ids moved, which notes moved vs. stayed, and confirm no `done` rows remain in
   `backlog.md` (unless $ARGUMENTS deliberately limited the set). Sanity-check that no row or note
   was dropped or duplicated across the two files. **Do not stage or commit anything.**

---

If `actions/backlog-archive.md` doesn't exist yet, create it with this header, then the first
`## Archived <date>` section:

```
# Backlog — archive

Closed items moved out of `actions/backlog.md` to keep the working table lean. Rows are kept
**verbatim with their original `#`** — ids are permanent references (cited from `actions/log/` reviews and
`actions/sessions/`), so nothing here is ever renumbered or deleted. Grouped by the date they were
archived. Populated by `/backlog-archive`.

| # | Item | Effort | Status | Source |
|---|---|---|---|---|
```

(Use one table per `## Archived <date>` section, or a single running table — match whatever the
file already does on subsequent runs.)
