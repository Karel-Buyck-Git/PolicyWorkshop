# Claude Code Prompt — Phase 3: Create per-tier EPAC-ready initiatives

Paste this prompt into Claude Code (or use it as a slash command / task prompt).

---

You are working inside the repository at:
`C:\GIT\Karel Buyck Git Azure Policy Workshop\PolicyWorkshop\product\lab\prototypes\bal-10`

## Context

This lab has an agentic pipeline with two earlier phases:

- **Phase 1** — `flows/extract-policies.py` extracts Azure Policy definitions and writes one `policies.md` per Azure resource category into the `output/` folder.
- **Phase 2** — `flows/enrich-policies.py` deduplicates rows, validates tiers, and adds a `## Tier rationale` section to each `output/<category>/policies.md` file.

Every `policies.md` file is a Markdown document that contains a table with these exact columns:

```
| # | Policy | Policy ID | Tag | Description | Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |
```

The **Domain** column groups Azure resource categories into higher-level governance domains
(e.g. `Storage`, `Security`, `Compute`, `Networking`, `Management`, `undefined`). The **Tier**
column is one of `Essential`, `Professional`, `Enterprise`.

## Your task — `flows/create-initiatives.py` (Phase 3)

The script turns the enriched markdown into a **per-tier, per-category, EPAC-ready** structure.
The enriched markdown is the taxonomy source of truth (tier, rationale); the official policy repo
is the parameter-schema source of truth. The two are joined on **Policy ID**.

**Inputs (CLI args, with defaults)**

- `--output` (default `output/`) — enriched markdown to read.
- `--initiatives` (default `initiatives/`) — output root.
- `--source` (default the official built-in policy definitions repo) — parameter schema.
- `--prefix` (default `company`) — brand prefix for files and initiative names.

**Processing**

- Build a parameter index `Policy ID -> {parameters, resource_id}` from `--source` (highest version wins).
- Parse each `output/**/*.md` table (dynamic header discovery) and its `## Tier rationale` section.
- Group every row by `(Domain, Tier, Category)`. Tiers are **exclusive** — each policy lands in
  exactly one group. Empty/`undefined` domains collapse to `undefined`; tiers outside the three
  canonical values fall back to `Essential`.

**Output — four artifacts per group**, written to
`initiatives/<domain-slug>/<tier-slug>/<category-slug>/<prefix>-<domain>-<tier>-<category>.*`:

- `.md` — H1 title, the matching tier's rationale paragraph, then the full 16-column table
  (`#` restarts at 1, policies sorted by name).
- `.policyset.json` — an EPAC `policySetDefinition` (initiative):
  - each member entry carries `metadata.policyName` (the policy display name) so a reviewer doesn't
    have to cross-reference the GUID against the markdown;
  - `effect` set to the **hardened** literal from the table (canonically cased; never the inert
    `Disabled` when the policy supports a real effect);
  - policies whose effect is **hardcoded in the rule** (no `effect` parameter — ~1/4 of built-ins,
    e.g. DINE/Modify/Append) carry **no `parameters.effect` by design** — EPAC cannot override a
    non-parameterized effect;
  - other parameters **with** a repo default → that default value emitted inline;
  - other parameters **without** a default (required) → bubbled up to a top-level initiative
    parameter (no default, so it must be supplied at assignment) and referenced via
    `[parameters('<name>')]`. Names are readable camelCase, letters only, derived from the policy +
    parameter (e.g. `certificatesMaximumValidityPeriodMaximumValidityInMonths`).
- `.assignment.json` — an EPAC assignment scaffold: `policySetDefinitionName`, a mock
  `<REPLACE: ...>` value per required parameter, `scope`/`notScopes` placeholders, and
  `managedIdentityLocations` **only** when the group contains a Modify/DeployIfNotExists policy
  (`Requires Managed Identity = Yes`). The `description` states the group's prerequisites — how many
  parameter values must be supplied (and which), and whether a managed identity / remediation is needed.
- `.exemptions.json` — an EPAC exemptions template stub (one `Waiver` example with placeholders).

The target EPAC shapes follow `docs/azure-policy-assignment-requirements.html`
(§9.3 initiative assignment, §10.2.1 exemptions, §12.3–12.4 assignment scaffolds).

**Error handling**

- No table found in a file → warn and skip, do not abort.
- `output/` missing → exit with a clear error.
- `--source` missing → continue with a warning; JSON omits sourced parameters.
- Overwrite existing files without prompting.

## Verification steps

1. Ensure `output/` is populated (run Phase 1 then Phase 2 if needed).
2. Run `python flows/create-initiatives.py` from the bal-10 root; confirm the per-group summary.
3. Confirm the tree: `initiatives/<domain>/<tier>/<category>/<prefix>-<domain>-<tier>-<category>.{md,policyset.json,assignment.json,exemptions.json}`.
4. Validate every JSON parses (e.g. `ConvertFrom-Json` over all `*.json`).
5. Spot-check a `policyset.json`: each `policyDefinitionId` resolves to a real repo GUID, `effect`
   is the hardened literal, and a required parameter is bubbled to top-level `parameters`. The
   matching `assignment.json` carries `<REPLACE: ...>` mocks and includes `managedIdentityLocations`
   only when the group has a Modify/DINE policy.
6. Spot-check a `.md`: rationale paragraph present, 16-column table, `#` restarts at 1.
