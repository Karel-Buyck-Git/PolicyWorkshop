---
description: Add one well-formed row to actions/backlog.md — enforces the row shape, requires a source, and flags duplicates before inserting. Manual only.
argument-hint: "[what the item is; include a why/source if you have one]"
disable-model-invocation: true
---

Today: !`date +%Y-%m-%d`

Add a backlog item. $ARGUMENTS is a free-text description of the item (may include the effort
and source; if not, you'll infer or ask below).

1. Read `actions/backlog.md`. The items live in one markdown table with columns
   `# | Item | Effort | Status | Source`. Compute the next id = **(highest integer `#` in the
   table) + 1**. Only integer ids are auto-generated — sub-ids like `1a`/`1b` are hand-authored,
   never generated here. IDs are permanent references (session logs and `actions/reviews/` reviews cite them),
   and the table already tolerates non-sequential order, so **append the new row as the last row
   of the table** — do not renumber or reorder anything.

2. Resolve all five columns from $ARGUMENTS:
   - **Item** — the description. Keep the house style: a concrete, self-contained sentence (what +
     where + why it matters). Fine to be long, like the existing rows.
   - **Effort** — one of `low` / `medium` / `high`. Infer from the description; if genuinely
     unclear, ask rather than guess.
   - **Status** — defaults to `todo` (use `in-progress` only if $ARGUMENTS says work has started).
   - **Source** — **required**: where this came from / the why (e.g. `Karel, <today's date>`, a
     `actions/reviews/review-*.md` file, or "discovered building #N"). If $ARGUMENTS gives no source, **ask**
     for one — do not invent it.

3. **Duplicate guard.** Scan the existing `Item` cells. If a current row already covers this
   (same fix, same area), surface that row and ask whether to proceed, refine the existing row
   instead, or cancel — don't silently add a near-duplicate.

4. Write the row into the table (before the `## Notes` section). If there's rationale worth
   preserving beyond the one-line Item, add a short `## Notes` bullet referencing the new id.

5. Report the new id and the row as written. **Do not stage or commit anything** — that's the
   author's call (same as every other command here).
