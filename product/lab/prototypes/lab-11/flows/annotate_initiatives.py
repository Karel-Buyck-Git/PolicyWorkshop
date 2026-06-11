"""
annotate_initiatives.py

Post-processor for the Phase 3 catalogue (does NOT re-run the producer flow).
Applies two in-place annotations to the already-generated initiative artifacts
under catalogue/initiatives/:

  1. Stamps an EPAC `$schema` URL (as the first key) onto every
     *.policyset.json, *.assignment.json and *.exemptions.json.
     *.roles.json is intentionally skipped — it is a lab-local helper artifact,
     not an EPAC-native file type, so it has no published schema.

  2. Inserts a `## Usage` section into every initiative *.md, positioned between
     the `## Tier rationale` section and the `## Policies` table. The section
     documents the IaC aspect of the sibling JSON artifacts (policyset,
     assignment, exemptions, roles).

The script is idempotent: re-running re-stamps the same schema and replaces an
existing `## Usage` section rather than duplicating it. It reads and writes only
the initiative artifacts; index.json / catalogue.json are left untouched.

Usage:
    python flows/annotate_initiatives.py
"""

import json
from pathlib import Path

from paths import INITIATIVES_DIR

# Canonical EPAC schema URLs (Azure/enterprise-azure-policy-as-code, Schemas/).
_EPAC_BASE = "https://raw.githubusercontent.com/Azure/enterprise-azure-policy-as-code/main/Schemas"
SCHEMA_BY_SUFFIX = {
    ".policyset.json":  f"{_EPAC_BASE}/policy-set-definition-schema.json",
    ".assignment.json": f"{_EPAC_BASE}/policy-assignment-schema.json",
    ".exemptions.json": f"{_EPAC_BASE}/policy-exemption-schema.json",
    # .roles.json deliberately omitted — no EPAC schema for this helper artifact.
}

USAGE_HEADING = "## Usage"
POLICIES_HEADING = "## Policies"


def double_suffix(path: Path) -> str:
    """Return the two-part suffix (e.g. '.policyset.json') or the single suffix."""
    if len(path.suffixes) >= 2:
        return "".join(path.suffixes[-2:])
    return path.suffix


def stamp_schema(path: Path, schema_url: str) -> bool:
    """Insert/refresh `$schema` as the first key. Returns True if the file changed."""
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("$schema") == schema_url and next(iter(obj)) == "$schema":
        return False
    rebuilt = {"$schema": schema_url}
    for k, v in obj.items():
        if k == "$schema":
            continue
        rebuilt[k] = v
    # Match create_initiatives.write_json formatting exactly (indent=2, trailing \n).
    path.write_text(json.dumps(rebuilt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def usage_block(base_name: str, has_roles: bool) -> list[str]:
    """The `## Usage` section lines for one initiative group."""
    roles_state = (
        "Present for this group" if has_roles
        else "Not present for this group (no Modify/DeployIfNotExists policy)"
    )
    return [
        USAGE_HEADING,
        "",
        "These artifacts are [EPAC](https://azure.github.io/enterprise-azure-policy-as-code/) "
        "(Enterprise Azure Policy as Code) definition files — deploy them as Infrastructure-as-Code "
        "via the EPAC pipeline (`Build-DeploymentPlans` → `Deploy-PolicyPlan` → `Deploy-RolesPlan`) "
        "or translate them to Terraform / Bicep. Each carries a `$schema` reference for editor "
        "validation.",
        "",
        "| Artifact | EPAC type | What to do with it |",
        "|---|---|---|",
        f"| `{base_name}.policyset.json` | `policySetDefinition` (initiative) | The set of built-in "
        "policies for this (domain, tier, category), hardened effect baked in and required parameters "
        "bubbled to top-level `parameters`. Place under your EPAC `policyDefinitions/` folder. |",
        f"| `{base_name}.assignment.json` | `policyAssignment` | Binds the initiative to a scope. "
        "Replace `<root-mg-id>`, `<pac-environment-selector>`, `<sub-id>` and every `<REPLACE: …>` "
        "parameter mock, then place under `policyAssignments/`. The `description` field states this "
        "group's prerequisites (required parameter count, managed identity). |",
        f"| `{base_name}.exemptions.json` | `policyExemption` | One `Waiver` stub. Set the scope and "
        "`policyDefinitionReferenceIds` for policies that do not apply, or remove the file. Place "
        "under `policyExemptions/`. |",
        f"| `{base_name}.roles.json` | role assignments (lab helper) | {roles_state}. Lists the "
        "`roleDefinitionIds` the assignment's managed identity needs for remediation. Not an "
        "EPAC-native file (no `$schema`) — consumed by the Terraform / Bicep renderers so they never "
        "need the policy repo downstream. |",
        "",
        "**Deployment order:** assign the initiative → (if a managed identity is required) grant the "
        "roles from `roles.json` at the assignment scope → run remediation tasks for the "
        "Modify/DeployIfNotExists policies.",
        "",
    ]


def insert_usage(path: Path, has_roles: bool) -> bool:
    """Insert/replace the `## Usage` section before `## Policies`. Returns True if changed."""
    lines = path.read_text(encoding="utf-8").splitlines()
    base_name = path.name[: -len(".md")]

    # Strip any existing Usage section (idempotent re-run) — from `## Usage` up to
    # (but not including) the next `## ` heading.
    if USAGE_HEADING in lines:
        start = lines.index(USAGE_HEADING)
        end = start + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        del lines[start:end]

    try:
        anchor = lines.index(POLICIES_HEADING)
    except ValueError:
        print(f"  [SKIP] {path}: no '{POLICIES_HEADING}' heading found")
        return False

    new_lines = lines[:anchor] + usage_block(base_name, has_roles) + lines[anchor:]
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return True


def main() -> None:
    root = Path(INITIATIVES_DIR)
    if not root.exists():
        raise SystemExit(f"ERROR: initiatives folder not found: {root}")

    json_changed = json_skipped = 0
    for path in sorted(root.rglob("*.json")):
        suffix = double_suffix(path)
        schema_url = SCHEMA_BY_SUFFIX.get(suffix)
        if not schema_url:          # .roles.json or anything else -> leave alone
            continue
        if stamp_schema(path, schema_url):
            json_changed += 1
        else:
            json_skipped += 1

    md_changed = 0
    for path in sorted(root.rglob("*.md")):
        has_roles = (path.parent / f"{path.name[:-len('.md')]}.roles.json").exists()
        if insert_usage(path, has_roles):
            md_changed += 1

    print(f"$schema stamped: {json_changed} json files ({json_skipped} already current)")
    print(f"## Usage inserted: {md_changed} markdown files")
    print("(.roles.json and catalogue manifests left untouched)")


if __name__ == "__main__":
    main()
