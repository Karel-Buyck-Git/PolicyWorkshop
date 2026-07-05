# `/reset-customer-package` — reset the customer working area to its pre-scaffold state

A command of the **epac-builder-onboarding-agent** skill. It undoes everything the onboarding
flow generated for a customer, restoring `catalogue-builder/customer/` to the clean **empty
scaffold** it was before any customer artifacts existed — ready to run onboarding again from
scratch.

It obeys the same **hard boundary** as the rest of the skill: it operates **only** under
`catalogue-builder/customer/` and never touches engine/catalogue/schema/workflow code. It also
never deletes the committed scaffold files themselves — only the generated per-customer artifacts.

Run everything from `catalogue-builder/`.

---

## What "pristine" means (the definition the reset restores)

The pre-scaffold state is exactly the **git-tracked** files under `customer/` — the committed empty
scaffold:

```
customer/NOTICE.md
customer/description.md
customer/designs/README.md
customer/manifests/.gitignore
customer/manifests/README.md
customer/manifests/input.example.json
customer/manifests/input.schema.json
customer/manifests/manifest.input.schema.json
customer/manifests/manifest.schema.json
customer/manifests/manifest.template.jsonc
```

Everything the onboarding flow adds is **not** in that set — it is untracked or gitignored:

| Generated artifact | Git state | Recoverable after delete? |
|---|---|---|
| `customer/package/**` (the whole rendered package) | untracked | ❌ not in git history |
| `customer/manifests/<customer>.input.json` | untracked | ❌ |
| `customer/manifests/<customer>.manifest.jsonc` (or `.manifest.json`) | **gitignored** | ❌ |
| `customer/designs/<customer>-mgmt-groups.json` / `…rich.svg` | untracked | ❌ |

So: **the tracked scaffold is safe and git-restorable; the generated artifacts are NOT in git and
deleting them is irreversible** unless the user committed or backed them up.

---

## Procedure

### Step 1 — Classify the current state (read-only; no deletion yet)

Determine what is pristine, what is generated, and whether anything is unexpected. Use git as the
source of truth — do **not** guess from memory of the session.

```
# Everything under customer/ that differs from the committed scaffold (tracked drift, untracked, ignored):
git status --porcelain --ignored -- customer/
```

Interpret each line:

- **Tracked file modified/deleted/renamed** (status like ` M`, `M `, ` D`, `R `, `AD`, etc. on one of
  the 10 scaffold files) → **unexpected.** The skill never edits the tracked scaffold, so this is a
  manual edit or corruption. **Go to Safe stop.**
- **`??` untracked** → candidate generated artifact. Check it matches an expected pattern (below).
- **`!!` ignored** → candidate generated artifact (the `*.manifest.jsonc` / `*.manifest.json`).

**Expected generated-artifact patterns** (the only things this command may remove):

- `customer/package/` (directory, any contents)
- `customer/manifests/*.manifest.jsonc`, `customer/manifests/*.manifest.json`
- `customer/manifests/*.input.json` **except** `input.example.json`
- `customer/designs/*` **except** `README.md` (e.g. `*-mgmt-groups.json`, `*-mgmt-groups.rich.svg`)

If **every** untracked/ignored entry matches one of these patterns, the working area is cleanly
attributable to onboarding → proceed to Step 2.

If there is **any** untracked/ignored file under `customer/` that does **not** match a pattern above
(someone dropped an unrelated file, or created something by hand) → **Go to Safe stop.** Do not
delete it and do not guess.

If there are **no** generated artifacts at all → tell the user the working area is already at the
pristine empty scaffold; nothing to reset. Stop.

### Step 2 — Warn and require explicit confirmation (before any deletion)

Present the exact removal plan as a concrete file/dir list (the classified set from Step 1 — show the
real paths, not patterns). Then state plainly:

- This is **destructive and irreversible**: the listed generated files are **not in git history**, so
  once deleted they cannot be recovered unless the user has their own backup or committed them.
- The committed scaffold files are **not** touched and remain git-restorable.
- After reset, `customer/` will be the clean empty scaffold, ready to onboard again.

Require **explicit** confirmation to proceed — ask the user to confirm by naming the customer (e.g.
"type the customer name to confirm reset of contoso"), not a bare yes. If they decline or hesitate,
stop and offer the non-destructive alternative (Step 4).

### Step 3 — Reset (only after confirmation)

Delete **only** the classified generated artifacts — the explicit paths shown in Step 2. Target them
directly; never blanket-`git clean` and never delete a tracked scaffold file. For example:

```
rm -rf customer/package
rm -f  customer/manifests/<customer>.input.json
rm -f  customer/manifests/<customer>.manifest.jsonc   # and any *.manifest.json
rm -f  customer/designs/<customer>-mgmt-groups.json customer/designs/<customer>-mgmt-groups.rich.svg
```

Then **verify** the working area is back to pristine — this must come back empty:

```
git status --porcelain --ignored -- customer/
```

If it is not empty, stop and report what remains rather than deleting further.

### Step 4 — Report

Confirm what was removed, that the tracked scaffold is intact, and that `customer/` is a clean
starting point. Point the user at the onboarding flow (`SKILL.md`) to begin again.

**Non-destructive alternative (offer if the user is unsure):** instead of deleting, they can *keep* a
copy — commit the generated artifacts on a throwaway branch, or rename the folder
(`customer/package` → `customer/package.bak-<date>`) — then reset. Recommend this if the package might
still be needed.

---

## Safe stop (when state doesn't match expectations)

Do **not** delete anything. Tell the user exactly what was found and why the command is stopping, e.g.:

> Reset stopped — the `customer/` working area isn't in a state I can safely reset. I found changes I
> can't attribute to the onboarding flow:
> - modified tracked scaffold file(s): `customer/manifests/manifest.template.jsonc`
> - unrecognised untracked file(s): `customer/notes.txt`
>
> The onboarding skill only ever creates generated artifacts (package/, `<customer>.manifest.jsonc`,
> `<customer>.input.json`, the design files) and never edits the committed scaffold — so these look
> like manual changes. Please resolve them yourself: restore tracked files with
> `git checkout -- <path>`, and move/remove the unrelated files. Then re-run `/reset-customer-package`.

This "stop rather than guess" behaviour is the point — it protects hand edits and anything the command
can't prove it created.
