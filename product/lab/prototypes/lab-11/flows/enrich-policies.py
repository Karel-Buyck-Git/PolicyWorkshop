"""
enrich-policies.py

Phase 2 enrichment for lab-11:
  - Re-validates the Tier column in every category's policies.md using refined
    rules (encoding the corrections from the lab plan).
  - Generates a rationale section above the table, grounded in the policies
    actually present in each tier for that resource category.
  - Re-sorts rows by (tier, name) and rewrites the file.

The script is idempotent: re-running it produces the same output for the same
input. Run after extract-policies.py.

Usage:
    python enrich-policies.py [--out <folder>] [--hierarchy <file>]
"""

import argparse
import re
from pathlib import Path
from hierarchy import load_domain_map  # shared parser (single source)

# Defaults derive from this script's location (the lab root is two levels up),
# so the pipeline targets its own lab with no flags.
from _paths import LAB_ROOT, DEFINITIONS_DIR, HIERARCHY_FILE  # noqa: F401
DEFAULT_OUT = str(DEFINITIONS_DIR)
DEFAULT_HIERARCHY = str(HIERARCHY_FILE)


TIER_ORDER = {"Essential": 0, "Professional": 1, "Enterprise": 2}


# ---------------------------------------------------------------------------
# Refined tier classification
#
# Priority: Enterprise > Professional > Essential. First tier whose rule
# matches wins. Rules are tuned to the corrections called out in lab-09-plan:
#   - Defender/threat/vulnerability  -> Professional (someone must act)
#   - Auditing/logging as observability -> Professional
#   - Logging that feeds a diagnostic pipeline (Log Analytics / Event Hub /
#     diagnostic settings / resource logs) -> Enterprise
#   - Private endpoint / private link -> Enterprise (zero trust investment)
#   - Zone redundancy / availability zones -> Enterprise (99.99% SLA)
#   - Resiliency / backup / recovery -> Essential (baseline data protection)
# ---------------------------------------------------------------------------

ENTERPRISE_PATTERNS = [
    r"\bprivate endpoint\b",
    r"\bprivate link\b",
    r"\bprivate dns zone\b",
    r"\bcustomer[- ]managed key",
    r"\bcustomer managed key",
    r"\bcmk\b",
    r"\bbyok\b",
    r"\bdiagnostic setting",
    r"\bresource log",
    r"\bstream.*(log analytics|event hub|storage account)",
    r"\bsend.*(log analytics|event hub)",
    r"\blog analytics workspace",
    r"\bzone[- ]redundan",
    r"\bzone resilien",
    r"\bzoneredundant",
    r"\bavailability zone",
    r"\bregional outage",
    r"\bzone outage",
    r"\bsentinel\b",
    r"\bconfidential comput",
    r"\btrusted launch",
    r"\bsecure boot",
    r"\bvtpm\b",
    r"\bsovereignty\b",
    r"\bdata residency\b",
    r"\bregulatory\b",
    r"\bnis2\b",
    r"\biso 27001\b",
    r"\bcis benchmark\b",
    r"\bnist\b",
    r"\bcma_",
]

# Categories that, by definition, are entirely Enterprise tier regardless of
# the individual policy text. Only used when the category as a whole exists
# *for* a regulatory/governance purpose (so the per-row keyword rules cannot
# fairly classify them — every row is the same kind of control).
ENTERPRISE_ONLY_CATEGORIES = {
    "regulatory-compliance",   # NIST 800-53 / CMA attestations, terse descriptions
}

PROFESSIONAL_PATTERNS = [
    r"\bdefender\b",
    r"\bthreat protection\b",
    r"\badvanced threat",
    r"\bvulnerability\b",
    r"\bvulnerability assessment\b",
    r"\bmicrosoft cloud security benchmark",
    r"\bpublic network access\b",
    r"\bdisable public",
    r"\bpublic ip\b",
    r"\bpublic access\b",
    r"\bfirewall\b",
    r"\bvirtual network\b",
    r"\bvnet\b",
    r"\bservice endpoint\b",
    r"\bnetwork security group\b",
    r"\bnsg\b",
    r"\bnetwork acl",
    r"\bweb application firewall",
    r"\bwaf\b",
    r"\bprivileged identity management\b",
    r"\bpim\b",
    r"\bjust[- ]in[- ]time\b",
    r"\bjit\b",
    r"\bcors\b",
    r"\bauditing should be enabled\b",
    r"\baudit.*should be enabled\b",
    r"\bshould have.*audit",
    r"\bdiagnostic logs.*should be enabled\b",
    r"\blog.*should be enabled\b",
    r"\blogging should be enabled\b",
    r"\bremediat",
    r"\bshould.*monitor",
    r"\bcompliance scan",
    r"\bmalware\b",
]

ESSENTIAL_PATTERNS = [
    r"\bencryption at rest\b",
    r"\binfrastructure encryption\b",
    r"\bdouble encryption\b",
    r"\bservice[- ]managed key",
    r"\btls\b",
    r"\bhttps\b",
    r"\bsecure transfer\b",
    r"\btransport security\b",
    r"\bencrypt(ion|ed)?\b",
    r"\brbac\b",
    r"\brole[- ]based access",
    r"\bmanaged identity\b",
    r"\bsystem[- ]assigned identity",
    r"\buser[- ]assigned identity",
    r"\blocal authentication\b",
    r"\block.box\b",
    r"\bmfa\b",
    r"\bkey rotation\b",
    r"\bkey expiration\b",
    r"\bcertificate\b",
    r"\bbackup\b",
    r"\bsoft delete",
    r"\bpurge protection",
    r"\bgeo[- ]redundan",
    r"\brecovery (vault|service)",
    r"\bdeletion protection",
    r"\btag\b",
    r"\btagging\b",
    r"\bsku\b",
    r"\bnaming\b",
    r"\bquota\b",
    r"\bshared access\b",
    r"\bsas\b",
    r"\bexpir(e|y|ation)\b",
]

_ENT_RE  = re.compile("|".join(ENTERPRISE_PATTERNS), re.IGNORECASE)
_PRO_RE  = re.compile("|".join(PROFESSIONAL_PATTERNS), re.IGNORECASE)
_ESS_RE  = re.compile("|".join(ESSENTIAL_PATTERNS), re.IGNORECASE)


def classify(name: str, description: str) -> str:
    text = f"{name} {description}".lower()
    if _ENT_RE.search(text):
        return "Enterprise"
    if _PRO_RE.search(text):
        return "Professional"
    if _ESS_RE.search(text):
        return "Essential"
    return "Essential"


# ---------------------------------------------------------------------------
# Theme detection — what kinds of policies live in each tier for this category?
# ---------------------------------------------------------------------------

THEME_RULES = {
    "private_connectivity": r"private (endpoint|link|dns)",
    "diagnostic_pipeline":  r"diagnostic setting|resource log|log analytics|event hub|sentinel",
    "customer_managed_keys": r"customer[- ]managed key|\bcmk\b|\bbyok\b",
    "zone_redundancy":      r"zone[- ]redundan|availability zone",
    "confidential_compute": r"confidential|trusted launch|secure boot",
    "regulatory":           r"regulatory|nis2|iso 27001|cis benchmark|nist",
    "defender":             r"defender|threat protection|advanced threat",
    "vulnerability":        r"vulnerability",
    "network_hardening":    r"public network access|disable public|virtual network|service endpoint|firewall|nsg|waf",
    "identity_governance":  r"\bpim\b|privileged identity|just[- ]in[- ]time|\bjit\b",
    "observability_audit":  r"auditing should be enabled|audit.*should be enabled|log.*should be enabled|monitor",
    "remediation":          r"remediat",
    "encryption_at_rest":   r"encryption at rest|infrastructure encryption|double encryption|service[- ]managed key|encrypt",
    "transport_security":   r"\btls\b|https|secure transfer|transport security",
    "identity_access":      r"\brbac\b|role[- ]based access|managed identity|local authentication|\bmfa\b",
    "key_certificate":      r"key rotation|key expiration|certificate|expir",
    "backup_resiliency":    r"backup|soft delete|purge protection|geo[- ]redundan|recovery (vault|service)|deletion protection",
    "tagging_finops":       r"\btag\b|tagging|\bsku\b|naming|quota",
}

_THEME_RES = {k: re.compile(v, re.IGNORECASE) for k, v in THEME_RULES.items()}


def themes_for(policies: list[dict]) -> set[str]:
    """Return the set of theme keys present across these policies."""
    blob = " ".join(f"{p['name']} {p['description']}" for p in policies).lower()
    return {key for key, rx in _THEME_RES.items() if rx.search(blob)}


# ---------------------------------------------------------------------------
# Rationale generation — category-aware, theme-aware
# ---------------------------------------------------------------------------

TIER_FRAMEWORKS = {
    "Essential":    "CIS Benchmarks, ISO 27001 Annex A.10 (cryptography) and A.12 (operations)",
    "Professional": "NIS2 Article 21 (detection & response), ISO 27001 A.12.4 (logging) and A.13 (network security)",
    "Enterprise":   "NIS2 Articles 21–23, ISO 27001 A.13.1.3 (network segregation) and A.18 (compliance), NIST SP 800-207 (Zero Trust)",
}

ESSENTIAL_THEME_PHRASES = {
    "identity_access":    "RBAC and managed-identity controls eliminating shared credentials",
    "transport_security": "TLS / HTTPS enforcement preventing in-transit interception",
    "encryption_at_rest": "encryption-at-rest with service-managed keys",
    "key_certificate":    "key and certificate lifecycle hygiene (rotation, expiration, validity)",
    "backup_resiliency":  "backup, soft-delete, and purge-protection guards against accidental or malicious data loss",
    "tagging_finops":     "tagging, SKU, and naming controls for cost and ownership accountability",
}

PROFESSIONAL_THEME_PHRASES = {
    "defender":           "Microsoft Defender plans surfacing threat signals",
    "vulnerability":      "vulnerability assessment scanning",
    "network_hardening":  "network hardening (public access disabled, VNet integration, firewall rules)",
    "identity_governance": "privileged identity management and just-in-time access",
    "observability_audit": "audit-log and monitoring controls that produce signals for ops teams",
    "remediation":        "auto-remediation deployments",
}

ENTERPRISE_THEME_PHRASES = {
    "private_connectivity":  "private endpoints and private link removing the public attack surface",
    "diagnostic_pipeline":   "diagnostic settings streaming to Log Analytics / Event Hub / Sentinel",
    "customer_managed_keys": "customer-managed keys (CMK / BYOK) for cryptographic sovereignty",
    "zone_redundancy":       "zone-redundant deployments backing the 99.99% SLA",
    "confidential_compute":  "confidential computing and trusted-launch attestation",
    "regulatory":            "direct mapping to regulatory framework controls",
}


# Friendly display names for category slugs that need a different label.
CATEGORY_PRETTY = {
    "api-management": "API Management",
    "app-service": "App Service",
    "azure-active-directory": "Microsoft Entra ID (Azure AD)",
    "azure-ai-services": "Azure AI Services",
    "azure-arc": "Azure Arc",
    "azure-data-explorer": "Azure Data Explorer",
    "azure-databricks": "Azure Databricks",
    "azure-load-testing": "Azure Load Testing",
    "azure-purview": "Microsoft Purview",
    "azure-stack-edge": "Azure Stack Edge",
    "azure-update-manager": "Azure Update Manager",
    "bot-service": "Bot Service",
    "container-apps": "Container Apps",
    "container-instance": "Container Instance",
    "container-instances": "Container Instances",
    "container-registry": "Container Registry",
    "cosmos-db": "Cosmos DB",
    "data-factory": "Data Factory",
    "data-lake": "Data Lake",
    "desktop-virtualization": "Azure Virtual Desktop",
    "event-grid": "Event Grid",
    "event-hub": "Event Hubs",
    "guest-configuration": "Guest Configuration",
    "health-bot": "Health Bot",
    "healthcare-apis": "Healthcare APIs",
    "internet-of-things": "Internet of Things",
    "key-vault": "Key Vault",
    "lab-services": "Lab Services",
    "logic-apps": "Logic Apps",
    "machine-learning": "Machine Learning",
    "managed-application": "Managed Application",
    "managed-grafana": "Managed Grafana",
    "managed-identity": "Managed Identity",
    "regulatory-compliance": "Regulatory Compliance",
    "security-center": "Defender for Cloud",
    "security-center---granular-pricing": "Defender for Cloud (Granular Pricing)",
    "service-bus": "Service Bus",
    "service-fabric": "Service Fabric",
    "signalr": "SignalR",
    "site-recovery": "Site Recovery",
    "sql-managed-instance": "SQL Managed Instance",
    "sql-server": "SQL Server",
    "stack-hci": "Azure Stack HCI",
    "stream-analytics": "Stream Analytics",
    "trusted-launch": "Trusted Launch",
    "vm-image-builder": "VM Image Builder",
    "web-pubsub": "Web PubSub",
}


def pretty_category(slug: str, fallback_title: str) -> str:
    if slug in CATEGORY_PRETTY:
        return CATEGORY_PRETTY[slug]
    return fallback_title


def join_phrases(phrases: list[str]) -> str:
    """Join 1-N phrases with commas and an Oxford 'and'."""
    if not phrases:
        return ""
    if len(phrases) == 1:
        return phrases[0]
    if len(phrases) == 2:
        return f"{phrases[0]} and {phrases[1]}"
    return ", ".join(phrases[:-1]) + f", and {phrases[-1]}"


def rationale_for_tier(
    tier: str,
    category_label: str,
    policies: list[dict],
) -> str:
    if not policies:
        return (
            f"**{tier}** — No {tier.lower()}-tier policies are defined for "
            f"{category_label} in the current built-in policy set."
        )

    present = themes_for(policies)

    if tier == "Essential":
        phrase_map = ESSENTIAL_THEME_PHRASES
        intro = (
            f"**Essential** — Baseline hygiene for {category_label}: the "
            f"non-negotiable controls every deployment should enforce from day one."
        )
        default_protection = (
            "credential theft, unencrypted data exposure, and accidental data loss"
        )
    elif tier == "Professional":
        phrase_map = PROFESSIONAL_THEME_PHRASES
        intro = (
            f"**Professional** — Active security posture for {category_label}: "
            f"controls that produce signals an operations team must act on."
        )
        default_protection = (
            "unauthorized network exposure, exploitable vulnerabilities, "
            "and undetected privilege misuse"
        )
    else:  # Enterprise
        phrase_map = ENTERPRISE_THEME_PHRASES
        intro = (
            f"**Enterprise** — Zero-trust and regulatory alignment for "
            f"{category_label}: controls that require infrastructure investment "
            f"or map directly to compliance frameworks."
        )
        default_protection = (
            "lateral movement, sovereign-data exfiltration, and audit gaps "
            "in regulated workloads"
        )

    matched_phrases = [phrase_map[t] for t in phrase_map if t in present]

    if matched_phrases:
        body = (
            f"This tier delivers {join_phrases(matched_phrases)}. "
            f"Together these policies protect against {default_protection}."
        )
    else:
        body = (
            f"This tier protects against {default_protection} for "
            f"{category_label} workloads."
        )

    frameworks = f"Maps to {TIER_FRAMEWORKS[tier]}."

    return f"{intro} {body} {frameworks}"


def build_rationale_section(
    category_label: str,
    by_tier: dict[str, list[dict]],
) -> str:
    parts = [
        "## Tier rationale",
        "",
        rationale_for_tier("Essential",    category_label, by_tier.get("Essential", [])),
        "",
        rationale_for_tier("Professional", category_label, by_tier.get("Professional", [])),
        "",
        rationale_for_tier("Enterprise",   category_label, by_tier.get("Enterprise", [])),
        "",
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Markdown parsing / writing
# ---------------------------------------------------------------------------

# Expected columns in order; matches what extract-policies.py emits.
COLUMNS = [
    "#", "Policy", "Policy ID", "Tag", "Description",
    "Allowed Values", "Default Value", "Soft Value", "Hardened Value",
    "Category", "Domain", "Version", "Type", "Tier", "Requires Parameters", "Requires Managed Identity",
]

HEADER_LINE = (
    "| # | Policy | Policy ID | Tag | Description | Allowed Values | "
    "Default Value | Soft Value | Hardened Value | Category | Domain | Version | Type | Tier | Requires Parameters | Requires Managed Identity |"
)
SEP_LINE = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"


def parse_table(path: Path) -> tuple[str, list[dict]]:
    """Return (title, list of row dicts). Skip header + separator lines.

    Tolerates both the legacy 12-column layout (no Domain) and the current
    13-column layout. For legacy files, Domain is left empty and will be
    re-derived from Category in process_file.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    title = ""
    rows: list[dict] = []

    header_cells: list[str] | None = None
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()
            continue
        if stripped.startswith("|") and "Policy ID" in stripped:
            header_cells = [c.strip() for c in stripped.strip("|").split("|")]
            in_table = True
            continue
        if in_table and re.match(r"^\|[-: |]+\|$", stripped):
            continue
        if in_table and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            # Map cells to their header names (legacy vs current), then re-key
            # onto the canonical COLUMNS list so downstream code stays uniform.
            schema = header_cells if header_cells else COLUMNS
            if len(cells) < len(schema):
                cells.extend([""] * (len(schema) - len(cells)))
            raw_row = dict(zip(schema, cells[: len(schema)]))
            row = {col: raw_row.get(col, "") for col in COLUMNS}
            rows.append(row)

    return title, rows


def md_row(row: dict, n: int) -> str:
    return (
        f"| {n} | {row['Policy']} | {row['Policy ID']} | {row['Tag']} | "
        f"{row['Description']} | {row['Allowed Values']} | {row['Default Value']} | "
        f"{row['Soft Value']} | {row['Hardened Value']} | {row['Category']} | "
        f"{row['Domain']} | {row['Version']} | {row['Type']} | {row['Tier']} | "
        f"{row['Requires Parameters']} | {row['Requires Managed Identity']} |"
    )


def write_enriched(path: Path, title: str, rows: list[dict], rationale: str) -> None:
    out = [
        f"# {title}",
        "",
        rationale,
        HEADER_LINE,
        SEP_LINE,
    ]
    out.extend(md_row(r, i) for i, r in enumerate(rows, start=1))
    out.append("")
    path.write_text("\n".join(out), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def process_file(path: Path, domain_map: dict[str, str]) -> dict:
    title, rows = parse_table(path)
    slug = path.parent.name
    force_enterprise = slug in ENTERPRISE_ONLY_CATEGORIES

    # Re-classify tier + (re-)derive Domain from Category
    changed = 0
    for r in rows:
        new_tier = "Enterprise" if force_enterprise else classify(r["Policy"], r["Description"])
        if new_tier != r["Tier"]:
            changed += 1
            r["Tier"] = new_tier
        r["Domain"] = domain_map.get(r["Category"], "undefined")

    # Group by tier for rationale
    by_tier: dict[str, list[dict]] = {"Essential": [], "Professional": [], "Enterprise": []}
    for r in rows:
        by_tier.setdefault(r["Tier"], []).append(
            {"name": r["Policy"], "description": r["Description"]}
        )

    # Sort rows by tier then name
    rows.sort(key=lambda r: (TIER_ORDER.get(r["Tier"], 99), r["Policy"].lower()))

    # Build rationale
    slug = path.parent.name
    category_label = pretty_category(slug, title.replace(" Policies", ""))
    rationale = build_rationale_section(category_label, by_tier)

    write_enriched(path, title, rows, rationale)

    return {
        "file": path,
        "row_count": len(rows),
        "tier_changes": changed,
        "tier_counts": {t: len(v) for t, v in by_tier.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich lab-11 policies.md files.")
    parser.add_argument("--out",       default=DEFAULT_OUT,       help="Output folder")
    parser.add_argument("--hierarchy", default=DEFAULT_HIERARCHY, help="Domain-hierarchy markdown file")
    args = parser.parse_args()

    out_dir = Path(args.out)
    hierarchy_path = Path(args.hierarchy)
    if not hierarchy_path.exists():
        print(f"ERROR: hierarchy file not found: {hierarchy_path}")
        raise SystemExit(1)
    domain_map = load_domain_map(hierarchy_path)
    print(f"Loaded domain map: {len(domain_map)} categories from {hierarchy_path.name}")

    files = sorted(out_dir.rglob("policies.md"))
    print(f"Found {len(files)} policies.md files under {out_dir}")

    total_rows = 0
    total_changes = 0
    for f in files:
        result = process_file(f, domain_map)
        total_rows += result["row_count"]
        total_changes += result["tier_changes"]
        rel = f.relative_to(out_dir)
        tc = result["tier_counts"]
        print(
            f"  {result['row_count']:>4} rows ({result['tier_changes']:>3} re-tiered) "
            f"E={tc['Essential']:>3} P={tc['Professional']:>3} N={tc['Enterprise']:>3}  ->  {rel}"
        )

    print(f"\nDone. {total_rows} rows processed, {total_changes} tier corrections applied.")


if __name__ == "__main__":
    main()
