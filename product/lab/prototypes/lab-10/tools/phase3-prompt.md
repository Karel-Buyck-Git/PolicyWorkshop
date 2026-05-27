# Claude Code Prompt — Phase 3: Create Initiatives by Domain

Paste this prompt into Claude Code (or use it as a slash command / task prompt).

---

You are working inside the repository at:
`C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop\product\lab\prototypes\lab-09`

## Context

This lab has an agentic pipeline with two existing phases:

- **Phase 1** — `flows/extract-policies.py` extracts Azure Policy definitions and writes one `policies.md` per Azure resource category into the `output/` folder.
- **Phase 2** — `flows/enrich-policies.py` deduplicates rows, validates tiers, and adds tier-rationale sections to each `output/<category>/policies.md` file.

Every `policies.md` file is a Markdown document that contains a table with these exact columns:

```
| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
```

The **Domain** column groups Azure resource categories into higher-level governance domains (e.g. `Storage`, `Security`, `Compute`, `Network`, `Data`, `undefined`, etc.).

## Your task

### 1. Write `flows/create-initiatives.py`

Create a Python 3 script at `flows/create-initiatives.py` that implements **Phase 3**:

**Input**
- Recursively scan every `output/**/*.md` file (skip any file whose path contains `initiatives`).
- Parse the Markdown table in each file. A row belongs to the table if it starts with `|` and is not a separator line (`|---|`).
- Extract the header row to identify column indices dynamically (do not hard-code column positions).

**Processing**
- Group all parsed rows by their **Domain** column value.
- Rows whose Domain is empty, whitespace-only, or equals `undefined` should be grouped under the domain name `undefined`.
- Preserve all columns exactly as they appear in the source files — do not drop or reorder columns.
- Within each domain group, sort rows by **Category** (alphabetically), then by Policy name within each category.
- Renumber the `#` column sequentially (1, 2, 3 …) **per category section** — each category restarts at 1.

**Output**
- Write one Markdown file per domain to `initiatives/<domain-slug>/initiative.md` — directly under the lab root, **not** under `output/`.
  - `<domain-slug>` is the domain name lowercased, spaces replaced with hyphens (e.g. `Storage` → `storage`, `Azure Active Directory` → `azure-active-directory`).
- Each initiative file is divided into **one section per Category**. The section heading is the category name. Within each section there is a full Markdown table with the standard columns. The overall file structure must be:

```markdown
# <Domain> Initiative

## <Category A>

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ... |
| 2 | ... |

## <Category B>

| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ... |
```

- Categories within a file are ordered alphabetically.
- Create parent directories as needed.
- Print a summary to stdout: one line per initiative file written, e.g.:
  `[Phase 3] Written: initiatives/storage/initiative.md  (61 policies across 3 categories)`

**Error handling**
- If a `policies.md` file cannot be parsed (no table found), print a warning and skip it — do not abort.
- If the `output/` directory does not exist, exit with a clear error message.
- If the `initiatives/` output directory already exists, overwrite existing files without prompting.

**Style requirements**
- Use only Python standard library modules (`pathlib`, `re`, `collections`, `sys`).
- No external dependencies.
- Add a module-level docstring explaining what the script does.
- Use `pathlib.Path` throughout (no `os.path`).
- Define a `main()` function and guard execution with `if __name__ == "__main__": main()`.

### 2. Update `plan/lab-09-plan.md`

Append a **Phase 3** section to `plan/lab-09-plan.md` immediately after the existing Phase 2 section, and update the **Done when** section to include the Phase 3 completion criterion. Use the same tone and heading style as the existing phases. The new section should read:

```markdown
## Phase 3 — Create initiatives by domain

Run the following script:
"C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop\product\lab\prototypes\lab-09\flows\create-initiatives.py"

- If the script exits with an error, report the error message and stop.
- If it completes successfully, note how many initiative files were written and proceed.

The script reads all enriched `policies.md` files from the `output/` folder, groups every
policy row by its **Domain** column value, and writes one consolidated initiative file per
domain to `initiatives/<domain-slug>/initiative.md` (directly under the lab root).

Each initiative file is divided into one section per Category (alphabetically ordered). Each
section heading is the category name followed by a Markdown table with the standard columns.
The `#` column restarts at 1 for each category section.

Review the generated initiative files and verify:
- Every policy from the source files appears in exactly one initiative.
- The row counts in the script's stdout summary match the number of rows in each file.
- Policies with Domain `undefined` are collected into `initiatives/undefined/initiative.md`
  and flagged for manual domain assignment in a follow-up task.
```

And update the **Done when** section to add:

```
All initiative files have been generated under `initiatives/` — one per domain, divided into
per-category sections — and verified for completeness and correctness.
```

## Verification steps after writing the code

1. Run `python flows/create-initiatives.py` from the lab-09 root.
2. Confirm that `initiatives/` (at the lab root) contains one subfolder per domain.
3. Spot-check `initiatives/storage/initiative.md`:
   - It should contain a `## Storage` section (or whichever categories exist in that domain).
   - The `#` column should restart at 1 in each category section.
   - Total policy count should match all Storage-domain rows across all source files.
4. Confirm no policies are duplicated across initiative files (each Policy ID should appear in exactly one initiative).
5. Confirm that within each section the `#` column is sequential with no gaps.
