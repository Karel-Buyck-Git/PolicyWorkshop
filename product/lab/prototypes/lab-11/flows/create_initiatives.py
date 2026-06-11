"""
create_initiatives.py

Phase 3 for lab-11:
  - Recursively scans every `catalogue/definitions/**/*.md` file produced by the earlier phases.
  - Parses each policies.md markdown table, discovering column indices from the
    header row (no hard-coded positions), and the `## Tier rationale` section.
  - Groups every policy row by (Domain, Tier, Category) — each policy lands in
    exactly one group (tiers are treated as *exclusive*, not cumulative).
  - For each group writes four EPAC-ready artifacts to
    `catalogue/initiatives/<domain-slug>/<tier-slug>/<category-slug>/<prefix>-<domain>-<tier>-<category>.*`:
        .md               — the policy table (same columns as Phase 1/2) + tier rationale
        .policyset.json   — an EPAC policySetDefinition (initiative) with parameter
                            values sourced from the official Azure policy repo
        .assignment.json  — an EPAC assignment scaffold with mock tenant references
        .exemptions.json  — an EPAC exemptions template stub

Parameter values are sourced by joining each policy row (on its Policy ID) against
a parameter index built from the official built-in policy definitions. The enriched
markdown remains the taxonomy source of truth (tier / rationale); the repo remains the
parameter-schema source of truth.

Run after enrich_policies.py.

Usage:
    python flows/create_initiatives.py
    python flows/create_initiatives.py --prefix company --source "<repo>" --output <dir> --initiatives <dir>
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from paths import LAB_ROOT, DEFINITIONS_DIR, INITIATIVES_DIR, HIERARCHY_FILE  # noqa: F401
from hierarchy import load_domain_map
DEFAULT_OUTPUT = DEFINITIONS_DIR
DEFAULT_INITIATIVES = INITIATIVES_DIR
DEFAULT_SOURCE = (
    r"C:\GIT\Official Azure Policy\azure-policy\built-in-policies\policyDefinitions"
)
DEFAULT_PREFIX = "company"

VALID_TIERS = ("Essential", "Professional", "Enterprise")

# Canonical column layout (matches enrich_policies.py / extract_policies.py).
COLUMNS = [
    "#", "Policy", "Policy ID", "Tag", "Description",
    "Requires Parameters", "Requires Managed Identity",
    "Allowed Values", "Default Value", "Soft Value", "Hardened Value",
    "Category", "Domain", "Version", "Type", "Tier",
]

HEADER_LINE = (
    "| # | Policy | Policy ID | Tag | Description | Requires Parameters | Requires Managed Identity | "
    "Allowed Values | Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier |"
)
SEP_LINE = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"

_SEP_RE = re.compile(r"^\|[-:\s|]+\|$")
_RATIONALE_RE = re.compile(r"^\*\*(Essential|Professional|Enterprise)\*\*\s*(.*)$")

# Canonical casing for known effects (source allowedValues casing is inconsistent).
# Mirrors extract_policies.py; unknown effects pass through unchanged.
CANONICAL_EFFECT: dict[str, str] = {
    "denyaction": "DenyAction", "deny": "Deny", "modify": "Modify",
    "enforcesetting": "EnforceSetting", "mutate": "Mutate",
    "deployifnotexists": "DeployIfNotExists", "auditifnotexists": "AuditIfNotExists",
    "audit": "Audit", "append": "Append", "addtonetworkgroup": "AddToNetworkGroup",
    "manual": "Manual", "disabled": "Disabled",
}


def canonical_effect(value: str) -> str:
    """Return the canonically-cased form of an effect, or the input unchanged."""
    return CANONICAL_EFFECT.get((value or "").strip().lower(), value)


# Cells are pipe-separated; a literal pipe inside a value is escaped as ``\|``.
# Split only on *unescaped* pipes so policy names/descriptions containing a pipe
# (e.g. NIST control titles "… | Cryptographic Protection") stay in one cell —
# otherwise the columns shift and the real GUID lands in the wrong column,
# breaking the Policy-ID join. Cells are unescaped on read; md_escape re-escapes
# on write so the round-trip is stable.
_CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")


def split_cells(stripped: str) -> list[str]:
    inner = stripped.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.strip().replace("\\|", "|") for c in _CELL_SPLIT_RE.split(inner)]


def md_escape(value: str) -> str:
    return (value or "").replace("|", "\\|").replace("\n", " ")


# ---------------------------------------------------------------------------
# Slug / version helpers
# ---------------------------------------------------------------------------

def slugify(value: str) -> str:
    """Lowercase, replace any run of non-alphanumerics with a single hyphen."""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (value or "").lower())).strip("-")


# Filler words dropped when deriving a readable parameter name from a policy display name.
_PARAM_STOPWORDS = {
    "should", "have", "has", "the", "a", "an", "to", "of", "for", "and", "or", "its",
    "be", "is", "are", "in", "on", "with", "that", "this", "by", "as", "from", "their",
    "not", "use", "using", "specified", "must", "at", "within", "when", "than", "more",
    "only", "your", "which", "if", "it",
}


def policy_token(display_name: str, max_words: int = 6) -> str:
    """A short camelCase token from a policy display name (letters only, no fillers)."""
    all_words = re.findall(r"[A-Za-z]+", display_name)
    words = [w for w in all_words if w.lower() not in _PARAM_STOPWORDS][:max_words]
    words = words or all_words[:max_words]
    if not words:
        return "policy"
    out = words[0].lower()
    for w in words[1:]:
        out += w[0].upper() + w[1:].lower()
    return out


def _letters_suffix(n: int) -> str:
    """Excel-column-style letters for n>=1 (1->A, 26->Z, 27->AA). Letters only."""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(ord("A") + r) + s
    return s


def make_param_name(display_name: str, src_param: str, used: set[str]) -> str:
    """Build a unique, readable camelCase initiative-parameter name (letters only).

    Combines a token from the policy name with the source parameter name, e.g.
    ``certificatesMaximumValidityPeriodMaximumValidityInMonths``. When genuinely
    near-identical policies still collide (e.g. per-resource diagnostic policies),
    disambiguates with a trailing Excel-style letter sequence — never digits.
    """
    base = policy_token(display_name)
    param = re.sub(r"[^A-Za-z]", "", src_param) or "param"
    name = base + param[0].upper() + param[1:]
    candidate, n = name, 1
    while candidate in used:
        candidate = name + _letters_suffix(n)
        n += 1
    used.add(candidate)
    return candidate


def version_key(v: str) -> tuple:
    """Parse '1.2.1' or '1.0.0-preview' into a sortable tuple; higher = newer.

    Mirrors extract_policies.py so the parameter index keeps the same definition
    version the markdown was built from.
    """
    if not v:
        return (0, 0, 0, 0)
    is_prerelease = "-" in v
    main = v.split("-", 1)[0]
    parts: list[int] = []
    for p in main.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return (*parts[:3], 0 if is_prerelease else 1)


# ---------------------------------------------------------------------------
# Parameter index from the official policy repo
# ---------------------------------------------------------------------------

def build_param_index(source_dir: Path) -> dict[str, dict]:
    """Map Policy ID -> {parameters, resource_id, version}.

    Walks the official built-in policy definitions once (same walk
    extract_policies.py does). On duplicate ids the highest version wins so the
    schema matches the deduplicated markdown.
    """
    index: dict[str, dict] = {}
    for path in source_dir.rglob("*.json"):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        pid = raw.get("name", "")
        if not pid:
            continue
        props = raw.get("properties", {}) or {}
        version = (props.get("metadata") or {}).get("version", "")
        existing = index.get(pid)
        if existing is not None and version_key(existing["version"]) >= version_key(version):
            continue
        rule = props.get("policyRule") or {}
        details = (rule.get("then") or {}).get("details")
        # `then.details` is usually an object (DeployIfNotExists/AuditIfNotExists),
        # but some policies use an array form (e.g. Modify operations); only the
        # object form carries roleDefinitionIds.
        role_ids = details.get("roleDefinitionIds") or [] if isinstance(details, dict) else []
        index[pid] = {
            "parameters": props.get("parameters") or {},
            "resource_id": raw.get("id") or f"/providers/Microsoft.Authorization/policyDefinitions/{pid}",
            "version": version,
            "roleDefinitionIds": list(role_ids),
        }
    return index


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

def parse_table(path: Path) -> list[dict]:
    """Parse the markdown table in ``path`` and return a list of row dicts.

    Column names are discovered from the header row, then each row is re-keyed
    onto COLUMNS so downstream code stays uniform regardless of source layout.
    Returns [] when no table is found.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    header_cells: list[str] | None = None
    rows: list[dict] = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        if header_cells is None and "Policy ID" in stripped:
            header_cells = split_cells(stripped)
            in_table = True
            continue
        if _SEP_RE.match(stripped):
            continue
        if in_table and header_cells:
            cells = split_cells(stripped)
            if len(cells) < len(header_cells):
                cells.extend([""] * (len(header_cells) - len(cells)))
            raw_row = dict(zip(header_cells, cells[: len(header_cells)]))
            row = {col: raw_row.get(col, "") for col in COLUMNS}
            rows.append(row)
    return rows


def parse_rationale(path: Path) -> dict[str, str]:
    """Return {tier: paragraph} captured from the `## Tier rationale` section.

    Degrades to {} when the file has no rationale (e.g. a pre-enrichment run).
    Each tier paragraph in enrich_policies.py output is a single line starting
    with ``**<Tier>** — ...``.
    """
    result: dict[str, str] = {}
    in_section = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = stripped.lower() == "## tier rationale"
            continue
        if not in_section:
            continue
        if stripped.startswith("|"):  # table reached — rationale is done
            break
        m = _RATIONALE_RE.match(stripped)
        if m:
            result[m.group(1)] = stripped
    return result


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------

def normalize_domain(value: str) -> str:
    s = (value or "").strip()
    if not s or s.lower() == "undefined":
        return "undefined"
    return s


def normalize_tier(value: str) -> str:
    s = (value or "").strip().lower()
    for tier in VALID_TIERS:
        if s == tier.lower():
            return tier
    return "Essential"  # safe default, mirrors the classifier


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def md_row(row: dict, n: int) -> str:
    return (
        f"| {n} | {md_escape(row['Policy'])} | {row['Policy ID']} | {row['Tag']} | "
        f"{md_escape(row['Description'])} | {row['Requires Parameters']} | {row['Requires Managed Identity']} | "
        f"{row['Allowed Values']} | {row['Default Value']} | {row['Soft Value']} | {row['Hardened Value']} | "
        f"{row['Category']} | {row['Domain']} | {row['Version']} | {row['Type']} | {row['Tier']} |"
    )


def render_markdown(display_name: str, rationale: str, rows: list[dict]) -> str:
    lines = [f"# {display_name}", ""]
    if rationale:
        lines += ["## Tier rationale", "", rationale, ""]
    lines += ["## Policies", "", HEADER_LINE, SEP_LINE]
    for i, r in enumerate(sorted(rows, key=lambda r: r["Policy"].lower()), start=1):
        lines.append(md_row(r, i))
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# EPAC JSON builders
# ---------------------------------------------------------------------------

def _mock_value(param_def: dict, init_name: str) -> object:
    """A clearly-marked placeholder for a required (no-default) parameter."""
    ptype = str(param_def.get("type", "String")).lower()
    placeholder = f"<REPLACE: {init_name}>"
    if ptype == "array":
        return [placeholder]
    return placeholder


def build_policyset(name, display_name, domain, tier, category, rows, param_index, description,
                    catalogue_version: str = ""):
    """Return (policyset_dict, required_params, roles_info).

    required_params maps each bubbled-up initiative parameter name to its source
    schema. roles_info captures remediation role IDs (baked from the repo at build
    time) so the Terraform/Bicep renderers never need the policy repo downstream.
    """
    policy_defs: list[dict] = []
    init_params: dict[str, dict] = {}
    required_params: dict[str, dict] = {}
    used_param_names: set[str] = set()
    role_union: set[str] = set()
    roles_by_policy: dict[str, list] = {}

    for i, r in enumerate(rows, start=1):
        pid = r["Policy ID"].strip()
        idx = param_index.get(pid)
        resource_id = (
            idx["resource_id"] if idx
            else f"/providers/Microsoft.Authorization/policyDefinitions/{pid}"
        )
        src_params = idx["parameters"] if idx else {}
        ref = pid or slugify(r["Policy"]) or f"policy-{i}"

        member_roles = (idx or {}).get("roleDefinitionIds") or []
        if member_roles:
            roles_by_policy[ref] = list(member_roles)
            role_union.update(member_roles)

        pd_params: dict[str, dict] = {}
        for pname, pdef in src_params.items():
            if pname.lower() == "effect":
                hardened = canonical_effect(r["Hardened Value"].strip())
                # Guard: never bake an inert 'Disabled' when the policy supports a
                # real effect (e.g. allowedValues ['enforceSetting','disabled']).
                if hardened == "Disabled":
                    allowed = pdef.get("allowedValues") or []
                    real = [a for a in allowed if str(a).strip().lower() != "disabled"]
                    if real:
                        default = pdef.get("defaultValue")
                        pick = default if default and str(default).strip().lower() != "disabled" else real[0]
                        hardened = canonical_effect(pick)
                if hardened:
                    pd_params["effect"] = {"value": hardened}
                continue
            if "defaultValue" in pdef:
                pd_params[pname] = {"value": pdef["defaultValue"]}
            else:
                init_name = make_param_name(r["Policy"], pname, used_param_names)
                schema = {
                    "type": pdef.get("type", "String"),
                    "metadata": pdef.get("metadata", {"displayName": pname}),
                }
                if "allowedValues" in pdef:
                    schema["allowedValues"] = pdef["allowedValues"]
                init_params[init_name] = schema       # no defaultValue => required
                required_params[init_name] = pdef
                pd_params[pname] = {"value": f"[parameters('{init_name}')]"}

        policy_def = {
            "policyDefinitionReferenceId": ref,
            "policyDefinitionId": resource_id,
            "groupNames": [tier],
            "metadata": {"policyName": r["Policy"]},
        }
        if pd_params:
            policy_def["parameters"] = pd_params
        policy_defs.append(policy_def)

    metadata = {"category": category, "domain": domain, "tier": tier}
    if catalogue_version:
        metadata["catalogueVersion"] = catalogue_version
    metadata["hasRemediation"] = bool(role_union)
    if role_union:
        metadata["roleDefinitionIds"] = sorted(role_union)

    policyset = {
        "name": name,
        "properties": {
            "displayName": display_name,
            "description": description,
            "policyType": "Custom",
            "metadata": metadata,
            "policyDefinitionGroups": [{"name": tier}],
            "parameters": init_params,
            "policyDefinitions": policy_defs,
        },
    }
    roles_info = {
        "name": name,
        "hasRemediation": bool(role_union),
        "roleDefinitionIds": sorted(role_union),
        "byPolicy": roles_by_policy,
    }
    return policyset, required_params, roles_info


def assignment_description(rows, required_params) -> str:
    """A scaffold description that states the assignment prerequisites for this set:
    required parameter values, managed identity / remediation, or neither."""
    n = len(rows)
    parts = [f"Deployment scaffold for {n} polic{'ies' if n != 1 else 'y'}."]

    req = list(required_params)
    if req:
        shown = ", ".join(req[:6]) + (", …" if len(req) > 6 else "")
        parts.append(
            f"{len(req)} parameter value{'s' if len(req) != 1 else ''} must be supplied at "
            f"assignment (shown as <REPLACE: …> mocks): {shown}."
        )
    else:
        parts.append(
            "No parameter values are required (effects are baked; other parameters use defaults)."
        )

    mi = sum(1 for r in rows if r["Requires Managed Identity"].strip().lower() == "yes")
    if mi:
        parts.append(
            f"A managed identity is required: {mi} Modify/DeployIfNotExists "
            f"polic{'ies' if mi != 1 else 'y'} {'need' if mi != 1 else 'needs'} remediation roles — "
            f"assign the identity at scope and run remediation tasks after deployment."
        )
    else:
        parts.append("No managed identity is required (no Modify/DeployIfNotExists policies).")

    parts.append(
        "Replace all mock references (<root-mg-id>, <pac-environment-selector>, <sub-id>, "
        "<REPLACE: …>) before deploying."
    )
    return " ".join(parts)


def build_assignment(name, display_name, prefix, domain, tier, category, rows, required_params):
    node = f"/{prefix}/{slugify(domain)}/{slugify(tier)}/{slugify(category)}/"
    assignment = {
        "nodeName": node,
        "assignment": {
            "name": name,
            "displayName": display_name,
            "description": assignment_description(rows, required_params),
        },
        "policySetDefinitionName": name,
        "parameters": {
            init_name: _mock_value(pdef, init_name)
            for init_name, pdef in required_params.items()
        },
    }
    needs_identity = any(r["Requires Managed Identity"].strip().lower() == "yes" for r in rows)
    if needs_identity:
        assignment["managedIdentityLocations"] = {
            "westeurope": ["/providers/Microsoft.Management/managementGroups/<root-mg-id>"]
        }
    assignment["scope"] = {
        "<pac-environment-selector>": ["/providers/Microsoft.Management/managementGroups/<root-mg-id>"]
    }
    assignment["notScopes"] = []
    return assignment


def build_exemptions(name, prefix, domain, tier, category):
    node = f"/{prefix}/{slugify(domain)}/{slugify(tier)}/{slugify(category)}/exemptions/"
    return {
        "nodeName": node,
        "exemptions": [
            {
                "name": f"{name}-example-exemption",
                "displayName": "Example exemption — replace or remove",
                "description": "Template stub. Set the scope/assignment id and the "
                               "policyDefinitionReferenceIds for policies that do not apply.",
                "exemptionCategory": "Waiver",
                "policyAssignmentId": (
                    "/providers/Microsoft.Management/managementGroups/<root-mg-id>"
                    f"/providers/Microsoft.Authorization/policyAssignments/{name}"
                ),
                "policyDefinitionReferenceIds": ["<policy-reference-id>"],
                "scope": "/subscriptions/<sub-id>",
            }
        ],
    }


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Catalogue manifests (version stamp + group index) — the consumer contract
# ---------------------------------------------------------------------------

def _sha256_file(path: Path) -> str:
    p = Path(path)
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else ""


def _content_hash(root: Path, exclude: set[str]) -> str:
    h = hashlib.sha256()
    for p in sorted(Path(root).rglob("*")):
        if not p.is_file() or p.name in exclude:
            continue
        rel = str(p.relative_to(root)).replace("\\", "/")
        h.update(rel.encode("utf-8")); h.update(b"\x00")
        h.update(p.read_bytes()); h.update(b"\x00")
    return "sha256:" + h.hexdigest()


def _git_ref(source_dir: Path) -> str:
    try:
        out = subprocess.run(["git", "-C", str(source_dir), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            return "git:" + out.stdout.strip()
    except Exception:
        pass
    p = Path(source_dir)
    if p.exists():
        return "snapshot:" + datetime.utcfromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
    return "unavailable"


def write_catalogue_manifests(catalogue_root, records, version, source_dir,
                              group_count, file_count) -> None:
    """Write the two consumer-facing manifests at the catalogue root:
    index.json (groups + domain map) and catalogue.json (version + fingerprint)."""
    catalogue_root = Path(catalogue_root)
    catalogue_root.mkdir(parents=True, exist_ok=True)
    flows_dir = Path(__file__).resolve().parent
    domain_map = load_domain_map(HIERARCHY_FILE) if Path(HIERARCHY_FILE).exists() else {}

    index = {
        "catalogueVersion": version,
        "tiers": list(VALID_TIERS),
        "domainMap": domain_map,   # category -> domain, from the ONE authored hierarchy
        "groups": sorted(
            records,
            key=lambda r: (r["domain"].lower(), VALID_TIERS.index(r["tier"]), r["category"].lower()),
        ),
    }
    write_json(catalogue_root / "index.json", index)

    catalogue = {
        "catalogueVersion": version,
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "inputs": {
            "builtInsRef": _git_ref(source_dir),
            "hierarchyHash": _sha256_file(HIERARCHY_FILE),
            "tierRulesHash": _sha256_file(flows_dir / "enrich_policies.py"),
        },
        "counts": {"groups": group_count, "files": file_count},
        "tools": {
            "extract": _sha256_file(flows_dir / "extract_policies.py"),
            "enrich": _sha256_file(flows_dir / "enrich_policies.py"),
            "createInitiatives": _sha256_file(flows_dir / "create_initiatives.py"),
        },
        # fingerprint over the whole catalogue except catalogue.json itself
        "contentHash": _content_hash(catalogue_root, exclude={"catalogue.json"}),
    }
    write_json(catalogue_root / "catalogue.json", catalogue)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 3 — build per-tier EPAC-ready initiatives.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Enriched markdown folder to read")
    parser.add_argument("--initiatives", default=str(DEFAULT_INITIATIVES), help="Output root for initiatives")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Official policy repo (parameter schema)")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX, help="Brand prefix for files and initiative names")
    parser.add_argument("--version", default=datetime.now(timezone.utc).strftime("%Y.%m.%d"),
                        help="Catalogue version label (default: today's UTC date)")
    args = parser.parse_args()
    catalogue_version = args.version

    output_dir = Path(args.output)
    initiatives_dir = Path(args.initiatives)
    catalogue_root = initiatives_dir.parent
    source_dir = Path(args.source)
    prefix = args.prefix

    if not output_dir.exists():
        print(f"ERROR: definitions catalogue folder not found: {output_dir}", file=sys.stderr)
        raise SystemExit(1)

    if source_dir.exists():
        param_index = build_param_index(source_dir)
        print(f"[Phase 3] Parameter index: {len(param_index)} policy definitions from {source_dir}")
    else:
        param_index = {}
        print(f"[Phase 3] WARNING: source repo not found ({source_dir}); "
              f"JSON will omit sourced parameters.")

    md_files = [p for p in output_dir.rglob("*.md") if "initiatives" not in p.parts]

    # Group rows by (domain, tier, category); collect rationale per (category, tier).
    by_group: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    rationale_by_cat: dict[str, dict[str, str]] = {}
    for path in sorted(md_files):
        rows = parse_table(path)
        if not rows:
            print(f"[Phase 3] WARNING: no table found, skipping {path}")
            continue
        rationale = parse_rationale(path)
        for r in rows:
            domain = normalize_domain(r.get("Domain", ""))
            tier = normalize_tier(r.get("Tier", ""))
            category = r.get("Category", "").strip() or "Uncategorized"
            r["Domain"], r["Tier"], r["Category"] = domain, tier, category
            by_group[(domain, tier, category)].append(r)
            rationale_by_cat.setdefault(category, rationale)

    index_records: list[dict] = []
    file_count = 0
    for (domain, tier, category) in sorted(by_group, key=lambda k: (k[0].lower(), VALID_TIERS.index(k[1]), k[2].lower())):
        rows = by_group[(domain, tier, category)]
        name = f"{prefix}-{slugify(domain)}-{slugify(tier)}-{slugify(category)}"
        display_name = f"{prefix.capitalize()} {domain} {tier} — {category}"
        rationale_text = rationale_by_cat.get(category, {}).get(tier, "")
        description = rationale_text or f"{display_name}: {len(rows)} built-in policies."

        group_dir = initiatives_dir / slugify(domain) / slugify(tier) / slugify(category)
        group_dir.mkdir(parents=True, exist_ok=True)

        (group_dir / f"{name}.md").write_text(
            render_markdown(display_name, rationale_text, rows), encoding="utf-8"
        )
        policyset, required_params, roles_info = build_policyset(
            name, display_name, domain, tier, category, rows, param_index, description,
            catalogue_version,
        )
        write_json(group_dir / f"{name}.policyset.json", policyset)
        if roles_info["hasRemediation"]:
            write_json(group_dir / f"{name}.roles.json", roles_info)
            file_count += 1
        index_records.append({
            "domain": domain, "tier": tier, "category": category, "name": name,
            "dir": str(group_dir.relative_to(catalogue_root)).replace("\\", "/"),
            "policyCount": len(rows),
            "hasRemediation": roles_info["hasRemediation"],
        })
        write_json(
            group_dir / f"{name}.assignment.json",
            build_assignment(name, display_name, prefix, domain, tier, category, rows, required_params),
        )
        write_json(
            group_dir / f"{name}.exemptions.json",
            build_exemptions(name, prefix, domain, tier, category),
        )
        file_count += 4
        print(f"[Phase 3] {slugify(domain)}/{slugify(tier)}/{slugify(category)}: "
              f"{len(rows)} policies -> 1 md + 3 json")

    write_catalogue_manifests(
        catalogue_root, index_records, catalogue_version, source_dir, len(by_group), file_count
    )
    print(f"\n[Phase 3] Done. {len(by_group)} groups, {file_count} files written to {initiatives_dir}")
    print(f"[Phase 3] Catalogue stamped: version {catalogue_version} "
          f"(index.json + catalogue.json at {catalogue_root})")


if __name__ == "__main__":
    main()
