---
description: Reset epac-workbench/customer/ back to its clean empty-scaffold state, undoing everything the onboarding flow generated. Destructive — confirms first and stops on unexpected changes. Manual only.
disable-model-invocation: true
---

Run the **`/reset-customer-package`** command of the epac-builder-onboarding-agent skill. Its full
procedure lives in
[epac-workbench/skills/epac-builder-onboarding-agent/reset-customer-package.md](../../epac-workbench/skills/epac-builder-onboarding-agent/reset-customer-package.md)
— read that file now and follow it exactly.

Non-negotiables from that procedure:

- **Classify first, from git — not memory.** Use `git status --porcelain --ignored -- customer/`
  (run from `epac-workbench/`) to tell the tracked scaffold from generated artifacts.
- **Stop rather than guess.** If a tracked scaffold file was modified, or there's an untracked file
  you can't attribute to onboarding, do not delete anything — report it and ask the user to resolve.
- **Confirm before destroying.** The generated artifacts are not in git, so deletion is irreversible.
  Show the exact paths, say so, and require explicit confirmation (ask the user to name the customer).
- **Scope + boundary.** Remove only the classified generated artifacts (`customer/package/`, the
  `<customer>.manifest.jsonc` / `.input.json`, `customer/designs/<customer>-*`). Only ever touch
  `customer/`; never the engine, catalogue, schemas, or workflows.
- **Verify pristine after.** Re-run the status check; it must come back empty. Report the result.
