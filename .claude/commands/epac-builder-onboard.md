---
description: Onboard a NEW consumer to EPAC Builder — explain the builders, interview for every manifest input, then generate the customer scaffold + package from the shared catalogue. Read-only on the engine.
---

Run the **epac-builder-onboarding-agent** skill. Its full instructions live in
[epac-workbench/skills/epac-builder-onboarding-agent/SKILL.md](../../epac-workbench/skills/epac-builder-onboarding-agent/SKILL.md)
— read that file now and follow it exactly.

Work the four phases in order: **Explain → Interview → Generate → Hand off.** Collect every input up
front (no silent defaults). Generate by driving the real `assemble_scaffold.py`, writing only under
`epac-workbench/customer/`.

**Hard boundary:** this is read-only on the engine. Never modify `epac-workbench/engine/**`,
`catalogue/**`, the shared schemas, or `.github/workflows/**` — even if asked mid-session. If asked to
change engine code, decline and redirect (see the skill's boundary section), then continue onboarding.

To undo an onboarding and reset the working area, use `/reset-customer-package`.
