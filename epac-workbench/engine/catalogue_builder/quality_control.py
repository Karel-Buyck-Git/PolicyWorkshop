"""Quality control output — producer step ⑤.

The final, repeatable gate of the Catalogue Builder pipeline. After Phases 1-3 have (re)built
the catalogue, this script:

  1. Reads the on-disk catalogue (custom definitions, built-in ``policies.md`` tables,
     initiatives and assignments).
  2. Runs a validation pass over the artifacts (missing display names, duplicate
     technical names, empty initiatives, orphan assignments, members without a
     readable policyName).
  3. Regenerates two documentation artifacts from live catalogue data:
       - ``catalogue/naming-samples.md``      (samples + name<->displayName pairs)
       - ``docs/epac-naming-convention.md``   (explanatory naming guide)
  4. Writes a machine-readable report at ``catalogue/quality-control.json``.

It is deterministic/idempotent: re-running on an unchanged catalogue produces
byte-identical output apart from the ``generatedAt`` timestamp. It exits non-zero
when any ``error``-level finding is present, so the plan step can "report and stop"
like the earlier phases.

Reuses the shared helpers rather than reinventing them:
  - ``shared.paths``    -> all catalogue/docs path constants
  - ``shared.mdtable``  -> the header-discovering ``parse_table``
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/ root

from shared.paths import (  # noqa: E402
    CATALOGUE_DIR,
    DEFINITIONS_DIR,
    INITIATIVES_DIR,
    CATALOGUE_FILE,
    INDEX_FILE,
    DOCS_DIR,
    NAMING_SAMPLES_FILE,
    EPAC_NAMING_DOC,
    QC_REPORT_FILE,
)
from shared.mdtable import parse_table  # noqa: E402  reuse shared helper
from shared.naming import (  # noqa: E402
    ASSIGNMENT_NAME_MAX, DEFINITION_NAME_MAX, DISPLAY_NAME_MAX, DESCRIPTION_MAX,
)

GUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------

def md_escape(text: str) -> str:
    """Make a string safe to drop into a single markdown table cell."""
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Build a GitHub-flavoured markdown table from already-stringified cells."""
    head = "| " + " | ".join(headers) + " |"
    sep = "|" + "|".join(["---"] * len(headers)) + "|"
    body = ["| " + " | ".join(md_escape(c) for c in r) + " |" for r in rows]
    return "\n".join([head, sep, *body])


def spread(seq: list, k: int) -> list:
    """Pick up to ``k`` evenly spaced items from ``seq`` (deterministic).

    Stable across runs, but **not** across catalogue changes: the picks are list
    *positions*, so inserting anything shifts every later row. Prefer ``spread_by``
    for any list with a taxonomy key (#29); this remains for lists that have none.
    """
    n = len(seq)
    if n <= k:
        return list(seq)
    idx = sorted({round(i * (n - 1) / (k - 1)) for i in range(k)})
    return [seq[i] for i in idx]


def spread_by(seq: list, k: int, key) -> list:
    """Pick up to ``k`` items, spread across the distinct values of ``key`` (#29).

    Positional ``spread`` had two failure modes in the sample tables, both visible in
    the #3 regeneration: it reshuffled **every** row when 17 policysets were inserted
    (churn that pollutes the diff of an auto-generated file), and it sampled the same
    domain twice while dropping others entirely — in a table that claims to show "a
    representative spread".

    Keying the selection to the taxonomy fixes both. Round-robin over the sorted key
    values takes one item per group before any group gets a second, so the sample
    covers as many distinct groups as it has slots; and because a group's own order is
    preserved, an inserted item only changes the sample if it lands ahead of the
    current pick **within its own group**. Everything else stays put.
    """
    groups: dict = {}
    for item in seq:
        groups.setdefault(key(item), []).append(item)
    picked: list = []
    depth = 0
    while len(picked) < k:
        exhausted = True
        for value in sorted(groups):
            members = groups[value]
            if depth < len(members):
                picked.append(members[depth])
                exhausted = False
                if len(picked) == k:
                    return picked
        if exhausted:
            break
        depth += 1
    return picked


# ---------------------------------------------------------------------------
# Catalogue readers
# ---------------------------------------------------------------------------

def load_custom_definitions() -> list[dict]:
    """All custom policy definitions under definitions/custom/**.json (sorted by name)."""
    out: list[dict] = []
    custom_dir = DEFINITIONS_DIR / "custom"
    for path in sorted(custom_dir.rglob("*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            out.append({"name": path.stem, "displayName": "", "_path": path, "_unreadable": True})
            continue
        props = raw.get("properties") or {}
        meta = props.get("metadata") or {}
        abbr = meta.get("abbreviations") or []
        out.append({
            "name": raw.get("name") or path.stem,
            "displayName": props.get("displayName") or "",
            "description": props.get("description") or "",
            "resourceType": meta.get("resourceType") or "",
            "abbr": abbr[0] if abbr else "",
            "checkKind": meta.get("checkKind") or "",
            "conventionExample": meta.get("conventionExample") or "",
            "family": path.parent.name,            # dlw-az-naming / dlw-az-tagging / ...
            "_path": path,
            "_unreadable": False,
        })
    out.sort(key=lambda d: d["name"])
    return out


def load_builtin_policies() -> list[dict]:
    """Built-in policy rows from every definitions/<category>/policies.md (sorted, deduped)."""
    seen: set[str] = set()
    rows: list[dict] = []
    for md in sorted(DEFINITIONS_DIR.glob("*/policies.md")):
        for row in parse_table(md):
            if (row.get("Type") or "").strip().lower() != "builtin":
                continue
            pid = (row.get("Policy ID") or "").strip()
            name = (row.get("Policy") or "").strip()
            if not pid or pid in seen:
                continue
            seen.add(pid)
            rows.append({"id": pid, "displayName": name,
                         "category": (row.get("Category") or "").strip()})
    rows.sort(key=lambda r: r["displayName"].lower())
    return rows


def _domain_of(path: Path) -> str:
    """The taxonomy domain an artifact lives in — ``initiatives/<domain>/<tier>/<category>/``.

    Read from the path rather than the artifact: every group artifact has one, including
    the ones that fail to parse, so sampling by domain (#29) never loses a row.
    """
    try:
        return path.relative_to(INITIATIVES_DIR).parts[0]
    except (ValueError, IndexError):
        return "(unknown)"


def load_initiatives() -> tuple[list[dict], list[dict], list[dict]]:
    """Return (initiatives, assignments, members) read from initiatives/**."""
    initiatives: list[dict] = []
    members: list[dict] = []
    for path in sorted(INITIATIVES_DIR.rglob("*.policyset.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            initiatives.append({"name": path.stem, "displayName": "", "domain": _domain_of(path),
                                "_path": path, "_unreadable": True, "memberCount": 0})
            continue
        props = raw.get("properties") or {}
        defs = props.get("policyDefinitions") or []
        initiatives.append({
            "name": raw.get("name") or path.stem,
            "displayName": props.get("displayName") or "",
            "description": props.get("description") or "",
            "memberCount": len(defs),
            "custom": bool((props.get("metadata") or {}).get("custom")),
            "domain": _domain_of(path),
            "_path": path,
            "_unreadable": False,
        })
        for m in defs:
            ref = m.get("policyDefinitionReferenceId") or m.get("policyDefinitionName") or ""
            members.append({
                "ref": ref,
                "policyName": (m.get("metadata") or {}).get("policyName") or "",
                "kind": "Built-in" if GUID_RE.match(ref or "") else "Custom",
                "initiative": raw.get("name") or path.stem,
                "_path": path,
            })

    assignments: list[dict] = []
    for path in sorted(INITIATIVES_DIR.rglob("*.assignment.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            assignments.append({"name": path.stem, "displayName": "", "policySet": "",
                                "domain": _domain_of(path), "_path": path, "_unreadable": True})
            continue
        a = raw.get("assignment") or {}
        assignments.append({
            "name": a.get("name") or path.stem,
            "displayName": a.get("displayName") or "",
            "description": a.get("description") or "",
            # definitionEntry.policySetName is the shape the producer emits (#22); the flat
            # policySetDefinitionName is still read so the referential-integrity check below
            # keeps working on a catalogue generated before that fix.
            "policySet": ((raw.get("definitionEntry") or {}).get("policySetName")
                          or raw.get("policySetDefinitionName") or ""),
            "domain": _domain_of(path),
            "_path": path,
            "_unreadable": False,
        })
    return initiatives, assignments, members


def load_exemptions() -> list[dict]:
    """Return exemption stubs (name + path) read from initiatives/**/*.exemptions.json."""
    out: list[dict] = []
    for path in sorted(INITIATIVES_DIR.rglob("*.exemptions.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for ex in raw.get("exemptions") or []:
            out.append({"name": ex.get("name") or "", "_path": path})
    return out


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(CATALOGUE_DIR.parent)).replace("\\", "/")
    except ValueError:
        return str(path)


def validate(custom: list[dict], builtins: list[dict], initiatives: list[dict],
             assignments: list[dict], members: list[dict],
             exemptions: list[dict] | None = None) -> list[dict]:
    """Run the QC checks and return a list of findings (severity/code/message/file)."""
    findings: list[dict] = []

    def add(severity: str, code: str, message: str, path: Path | None = None):
        findings.append({"severity": severity, "code": code, "message": message,
                         "file": _rel(path) if path else ""})

    # finalize gate: apply_overlays (Phase ④) must have stamped the catalogue ---
    try:
        _content_hash = json.loads(CATALOGUE_FILE.read_text(encoding="utf-8")).get("contentHash", "")
    except (OSError, json.JSONDecodeError):
        _content_hash = ""
    if _content_hash == "sha256:pending":
        add("error", "catalogue-not-finalized",
            "catalogue.json contentHash is 'pending' — run apply_overlays.py (Phase ④) to apply "
            "custom overlays and stamp the catalogue before quality-control", CATALOGUE_FILE)

    # missing display names ---------------------------------------------------
    for d in custom:
        if d["_unreadable"]:
            add("error", "unreadable-definition", f"Custom definition '{d['name']}' did not parse", d["_path"])
        elif not d["displayName"].strip():
            add("error", "missing-displayname", f"Custom definition '{d['name']}' has no displayName", d["_path"])
    for it in initiatives:
        if it["_unreadable"]:
            add("error", "unreadable-initiative", f"Initiative '{it['name']}' did not parse", it["_path"])
            continue
        if not it["displayName"].strip():
            add("error", "missing-displayname", f"Initiative '{it['name']}' has no displayName", it["_path"])
        if it["memberCount"] == 0:
            add("error", "empty-initiative", f"Initiative '{it['name']}' has zero member policies", it["_path"])
    for a in assignments:
        if not a["_unreadable"] and not a["displayName"].strip():
            add("error", "missing-displayname", f"Assignment '{a['name']}' has no displayName", a["_path"])

    # Azure hard limits (docs/epac-arm-hard-limits.md) ------------------------
    def check_limits(kind, items, name_max):
        for x in items:
            if x.get("_unreadable"):
                continue
            nm = x.get("name", "")
            if len(nm) > name_max:
                add("error", "name-too-long",
                    f"{kind} name '{nm}' is {len(nm)} chars (Azure max {name_max})", x.get("_path"))
            dn = x.get("displayName", "")
            if len(dn) > DISPLAY_NAME_MAX:
                add("error", "displayname-too-long",
                    f"{kind} '{nm}' displayName is {len(dn)} chars (max {DISPLAY_NAME_MAX})", x.get("_path"))
            desc = x.get("description", "")
            if len(desc) > DESCRIPTION_MAX:
                add("error", "description-too-long",
                    f"{kind} '{nm}' description is {len(desc)} chars (max {DESCRIPTION_MAX})", x.get("_path"))

    check_limits("definition", custom, DEFINITION_NAME_MAX)
    check_limits("initiative", initiatives, DEFINITION_NAME_MAX)
    check_limits("assignment", assignments, ASSIGNMENT_NAME_MAX)  # the strict 24-char cap
    for ex in (exemptions or []):
        if len(ex["name"]) > DEFINITION_NAME_MAX:
            add("error", "name-too-long",
                f"exemption name '{ex['name']}' is {len(ex['name'])} chars (max {DEFINITION_NAME_MAX})",
                ex.get("_path"))

    # brand-neutral catalogue (no 'company' / brand token) --------------------
    for kind, items in (("initiative", initiatives), ("assignment", assignments)):
        for x in items:
            if x.get("_unreadable"):
                continue
            if re.search(r"(?i)\bcompany\b", f"{x.get('name','')} {x.get('displayName','')}"):
                add("error", "brand-leak",
                    f"{kind} '{x['name']}' still carries a 'company' brand token", x.get("_path"))

    # governance: definition_gen overlays ------------------------------------
    member_refs = {m["ref"] for m in members}
    for d in custom:
        if not d["_unreadable"] and d["name"] not in member_refs:
            add("error", "orphan-custom-definition",
                f"Custom definition '{d['name']}' is not a member of any initiative "
                f"(no overlay references it)", d["_path"])

    try:
        index_names = {g["name"] for g in json.loads(INDEX_FILE.read_text(encoding="utf-8")).get("groups", [])}
    except (OSError, json.JSONDecodeError):
        index_names = None
    if index_names is not None:
        for it in initiatives:
            if it.get("custom") and it["name"] not in index_names:
                add("error", "unregistered-custom-group",
                    f"Custom overlay '{it['name']}' is not registered in index.json "
                    f"(run apply_overlays.py)", it["_path"])

    gen_dir = Path(__file__).resolve().parent.parent / "definition_gen"
    for gen in sorted(gen_dir.glob("gen_*.py")):
        if not gen.with_suffix(".md").exists():
            add("error", "missing-generator-doc",
                f"Generator '{gen.name}' has no companion '{gen.stem}.md'", gen)

    # duplicate technical names ----------------------------------------------
    for label, items, severity in (("definition", custom, "warning"),
                                   ("initiative", initiatives, "warning"),
                                   ("assignment", assignments, "error")):
        counts: dict[str, int] = {}
        for x in items:
            counts[x["name"]] = counts.get(x["name"], 0) + 1
        for name, c in sorted(counts.items()):
            if c > 1:
                add(severity, "duplicate-name", f"{label} name '{name}' appears {c} times")

    # orphan assignments ------------------------------------------------------
    initiative_names = {it["name"] for it in initiatives}
    for a in assignments:
        if a["policySet"] and a["policySet"] not in initiative_names:
            add("error", "orphan-assignment",
                f"Assignment '{a['name']}' references missing policy set '{a['policySet']}'", a["_path"])

    # members without a readable name ----------------------------------------
    missing_member = sum(1 for m in members if not m["policyName"].strip())
    if missing_member:
        add("warning", "member-without-policyname",
            f"{missing_member} initiative member(s) have no metadata.policyName (GUID only in the portal)")

    # coverage (info) ---------------------------------------------------------
    add("info", "naming-coverage",
        f"{len(custom)} custom definitions (readable slugs), {len(builtins)} built-in policies (GUID ids), "
        f"{len(initiatives)} initiatives, {len(assignments)} assignments")

    return findings


# ---------------------------------------------------------------------------
# Table builders (live data)
# ---------------------------------------------------------------------------

def naming_defs(custom: list[dict]) -> list[dict]:
    return [d for d in custom if d["family"] == "dlw-az-naming" and not d["_unreadable"]]


def t_sample_result_names(custom: list[dict]) -> str:
    rows = [d for d in naming_defs(custom) if d["checkKind"] == "default" and d["conventionExample"]]
    # One example per Azure resource provider (Microsoft.Storage/…, Microsoft.Network/…),
    # so the sample spans providers instead of a positional slice of one (#29).
    return md_table(
        ["Resource type", "Abbr", "Example name (`conventionExample`)"],
        [[f"`{d['resourceType']}`", f"`{d['abbr']}`", f"`{d['conventionExample']}`"]
         for d in spread_by(rows, 7, lambda d: (d["resourceType"] or "").split("/")[0])],
    )


def t_checkkind_distribution(custom: list[dict]) -> str:
    defs = naming_defs(custom)
    counts: dict[str, int] = {}
    example: dict[str, str] = {}
    for d in defs:
        ck = d["checkKind"] or "(unset)"
        counts[ck] = counts.get(ck, 0) + 1
        if ck not in example and d["conventionExample"]:
            example[ck] = d["conventionExample"]
    order = sorted(counts, key=lambda k: (-counts[k], k))
    return md_table(
        ["`checkKind`", "Count", "Example name"],
        [[f"`{ck}`", str(counts[ck]), f"`{example.get(ck, '—')}`"] for ck in order],
    )


def t_pairs(items: list[tuple[str, str]], headers: list[str], code_left: bool = True) -> str:
    rows = [[f"`{a}`" if code_left else a, b] for a, b in items]
    return md_table(headers, rows)


def t_custom_pairs(custom: list[dict]) -> str:
    # Keyed on the generator family (naming / tagging / apim) so each is represented.
    items = [(d["name"], d["displayName"])
             for d in spread_by([c for c in custom if not c["_unreadable"]], 11,
                                lambda d: d["family"] or "")]
    return t_pairs(items, ["Technical `name`", "`displayName`"])


def t_builtin_pairs(builtins: list[dict]) -> str:
    items = [(b["id"], b["displayName"])
             for b in spread_by(builtins, 8, lambda b: b["category"] or "")]
    return t_pairs(items, ["Technical `name` (GUID)", "`displayName`"])


def t_initiative_pairs(initiatives: list[dict]) -> str:
    # The table #29 was raised on: positional sampling showed Data twice and dropped
    # Security entirely. Sized to the taxonomy — exactly one row per domain, so "a
    # representative spread" is literally true and no domain can fall off the end.
    readable = [i for i in initiatives if not i["_unreadable"]]
    items = [(it["name"], it["displayName"])
             for it in spread_by(readable, len({i["domain"] for i in readable}),
                                 lambda i: i["domain"])]
    return t_pairs(items, ["Technical `name`", "`displayName`"])


def t_assignment_pairs(assignments: list[dict]) -> str:
    items = [(a["name"], a["displayName"])
             for a in spread_by([a for a in assignments if not a["_unreadable"]], 4,
                                lambda a: a["domain"])]
    return t_pairs(items, ["`assignment.name`", "`assignment.displayName`"])


def t_member_pairs(members: list[dict]) -> str:
    custom = [m for m in members if m["kind"] == "Custom" and m["policyName"]]
    builtin = [m for m in members if m["kind"] == "Built-in" and m["policyName"]]
    picked = spread(custom, 2) + spread(builtin, 3)
    rows = [[f"`{m['ref']}`", m["policyName"], m["kind"]] for m in picked]
    return md_table(["Member reference id", "`metadata.policyName` (displayName)", "Kind"], rows)


def t_findings(findings: list[dict]) -> str:
    if not findings:
        return "_No findings._"
    order = {"error": 0, "warning": 1, "info": 2}
    rows = [[f["severity"], f"`{f['code']}`", f["message"], f["file"] or "—"]
            for f in sorted(findings, key=lambda x: (order.get(x["severity"], 9), x["code"]))]
    return md_table(["Severity", "Code", "Message", "File"], rows)


# ---------------------------------------------------------------------------
# Document templates (curated prose + injected live tables)
# ---------------------------------------------------------------------------

def render_naming_samples(ctx: dict) -> str:
    return f"""# Catalogue Builder EPAC Catalogue — Naming Result Samples

> **Auto-generated by `engine/catalogue_builder/quality_control.py` (producer step ⑤).** Do not edit by hand —
> rerun the quality-control step. Catalogue version **{ctx['version']}**, generated {ctx['generatedAt']}.

A tour of what the Catalogue Builder catalogue produces, with samples pulled live from the files on
disk. Focus is the **custom naming definitions** and the **initiatives** that bundle them,
plus the assignment scaffolding around them.

All artifacts carry the EPAC `$schema` reference and follow the convention generated by
`engine/definition_gen/gen_dlw_naming_definitions.py` from the DLW `getResourceName.bicep` module (v1.5).
Customer/org prefix is **`dlw`**.

---

## 1. Naming convention — the result names

Every custom naming policy validates a single **deterministic anchor** at the front of the
resource name (`customer + resource abbreviation`), because Azure Policy `like` allows only
one wildcard. The general shape:

```
dlw-<abbr>-<service>-<env>-<loc>-<instance>
└┬┘ └─┬─┘ └────────────┬───────────────────┘
 │    │                └ free segments (NOT validated — only the anchor is)
 │    └ CAF resource abbreviation (e.g. kv, rg, apim, st)
 └ customerAbbreviation parameter (bound per customer; raw-catalogue fallback "org")
```

A concrete instance once the placeholders are filled, e.g. a prod Key Vault for the
"payments" service in West Europe: **`dlw-kv-payments-prod-weu-001`**.

### Sample result names by resource type

{ctx['sample_names']}

### The check is not always hyphenated

The generator emits different `checkKind`s depending on what Azure allows for that resource's
name. Distribution across the custom naming definitions:

{ctx['checkkinds']}

> Storage accounts and VMs disallow hyphens, so those policies check "the name has no `-`" /
> "starts with `dlwst`" rather than the standard dashed anchor.

---

## 2. The two identifiers — name vs displayName

Every artifact carries two identifiers: the technical **`name`** (in the JSON / resource ID)
and the **`displayName`** (what the Azure Portal lists render). The pairs below are laid out
side-by-side for a portal-style scan.

> **Aesthetic contrast:** custom artifacts use readable slugs (`naming-keyvault-vaults`),
> while built-in policies surface as raw **GUIDs** — only their `displayName` reads cleanly.

### A. Custom policy definitions — slug ↔ displayName

{ctx['custom_pairs']}

### B. Built-in policy definitions — GUID ↔ displayName

Built-ins live in the catalogue only as `definitions/<category>/policies.md` rows (no JSON);
Azure references them by GUID.

{ctx['builtin_pairs']}

> For built-ins the technical id is an opaque GUID — only the `displayName` is human-readable.

### C. Initiatives (policy sets) — name ↔ displayName

{ctx['initiative_pairs']}

> Pattern: `<domain>-<tier>-<abbr>` ↔ `<Domain> <Tier> — <Category>` (brand-neutral; tier code
> `esn`/`pro`/`ent`; the category abbreviation is authored in `config/azure-category-abbreviation.md`).

### D. Assignments — name ↔ displayName

The assignment's `name` / `displayName` mirror its initiative.

{ctx['assignment_pairs']}

### E. Initiative members — reference id ↔ member displayName

How members read inside an initiative — custom (slug) vs built-in (GUID) in one view:

{ctx['member_pairs']}

---

## 3. Deployment recap

1. Deploy the custom `naming-*` definitions (members referenced by `policyDefinitionName`).
2. Deploy the initiative (policy set).
3. Apply the assignment (replace the `<…>` placeholders).
4. Optionally fill or remove the exemption stub.
5. Ships as **`Audit`** — set the initiative's `effect` to **`Deny`** at the customer to enforce.

---

## Quality control report

{ctx['summary_line']}

{ctx['findings']}
"""


def render_epac_naming_doc(ctx: dict) -> str:
    return f"""# Catalogue Builder Catalogue — Naming, Identifiers & How They Render in Azure

> **Auto-generated by `engine/catalogue_builder/quality_control.py` (producer step ⑤).** Do not edit by hand —
> rerun the quality-control step. Catalogue version **{ctx['version']}**, generated {ctx['generatedAt']}.

An explanatory guide to **what the Catalogue Builder EPAC catalogue produces** and, in particular, **how
the two identifiers on every artifact — the technical `name` and the `displayName` — appear in
the Azure Portal**. Written for a naming / aesthetics review: it pairs the machine name with the
human-facing name so you can judge how each artifact reads in the portal.

The worked samples that back this guide live in
[`catalogue/naming-samples.md`](../catalogue/naming-samples.md). The producer that generates the
artifacts is documented in [`az-taxonomy-pipeline.md`](./az-taxonomy-pipeline.md), and the
deployment mechanics in [`scaffold-deployment-guide.md`](./scaffold-deployment-guide.md).

---

## 1. The two identifiers Azure tracks

Every policy definition, initiative (policy set) and assignment carries **two** names, and Azure
surfaces them in different places:

| Identifier | Where it lives in the JSON | Where Azure shows it |
|---|---|---|
| Technical **`name`** | top-level `name` (definitions/initiatives), `assignment.name` | Resource ID / URL, the "Definition ID", raw JSON |
| **`displayName`** | `properties.displayName`, `assignment.displayName` | Policy blade **lists** (Definitions, Assignments, Compliance) |

In day-to-day portal use a reviewer sees the **`displayName`**. The technical `name` only
appears when you open the definition's ID or inspect the JSON. Inside an initiative, each member
policy row is rendered by its `displayName` too (the initiative stores a copy of that text in
each member's `metadata.policyName`).

---

## 2. Custom vs built-in — the key aesthetic contrast

The single most important thing a naming review will notice:

- **Custom policies** (the `dlw-az-naming` and `dlw-az-tagging` definitions) use **readable
  slugs** for their technical `name` — e.g. `naming-keyvault-vaults`.
- **Built-in policies** are referenced by an **opaque GUID** — e.g.
  `cccc23c7-8427-4f53-ad12-b6a63eb452b3`. Only their `displayName` is human-readable.

So in any list that mixes the two, the *display names* read consistently, but the *technical
ids* do not — half are friendly slugs, half are GUIDs. That is inherent to Azure (you cannot
rename a built-in's id), not a defect in the catalogue.

---

## 3. Naming convention for custom resources

The custom `naming-*` policies validate a single **deterministic anchor** at the front of a
resource name (`customer + resource abbreviation`):

```
dlw-<abbr>-<service>-<env>-<loc>-<instance>
```

A filled-in example — a prod Key Vault for the "payments" service in West Europe:
**`dlw-kv-payments-prod-weu-001`**. Not every resource uses the dashed form: storage accounts
and VMs disallow hyphens, so those policies check a *compact* name instead. See
[`naming-samples.md`](../catalogue/naming-samples.md) for the full check-kind breakdown.

---

## 4. Name ↔ displayName, by artifact type

Representative pairs pulled live from the catalogue.

### Custom policy definitions — slug ↔ displayName

{ctx['custom_pairs']}

### Built-in policy definitions — GUID ↔ displayName

{ctx['builtin_pairs']}

### Initiatives (policy sets) — name ↔ displayName

{ctx['initiative_pairs']}

Pattern: `<domain>-<tier>-<abbr>` ↔ `<Domain> <Tier> — <Category>`. Names are **brand-neutral**
(no `company`) and within the Azure hard limits (assignment `name` ≤ 24 chars — see
`epac-arm-hard-limits.md`). Tier code: `esn`/`pro`/`ent`. The category abbreviation is authored
in `config/azure-category-abbreviation.md` (CAF-aligned where the category is a resource type).

### Assignments — name ↔ displayName

{ctx['assignment_pairs']}

### Initiative members — reference id ↔ member displayName

{ctx['member_pairs']}

---

## 5. What to look for in a naming / aesthetics review

- **Display names** — consistency of tone, casing and length across definitions, initiatives and
  assignments (these are the user-facing strings). Watch for casing slips.
- **Initiative / assignment titles** — they follow `<Domain> <Tier> — <Category>` (brand-neutral);
  confirm the em-dash and capitalisation are uniform.
- **Technical names** — custom slugs are predictable (`naming-<provider>-<resource>`); built-in
  ids are GUIDs and cannot be changed.

---

## Quality control report

{ctx['summary_line']}

{ctx['findings']}

## See also

- [`catalogue/naming-samples.md`](../catalogue/naming-samples.md) — fuller worked samples of each artifact.
- [`az-taxonomy-pipeline.md`](./az-taxonomy-pipeline.md) — the producer pipeline that generates the catalogue.
- [`scaffold-deployment-guide.md`](./scaffold-deployment-guide.md) — standing up EPAC and deploying these artifacts.
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 5 — quality-control docs + validation report.")
    parser.add_argument("--catalogue", default=str(CATALOGUE_DIR), help="Catalogue root to read")
    parser.add_argument("--docs", default=str(DOCS_DIR), help="Docs output folder")
    parser.add_argument("--version", default=datetime.now(timezone.utc).strftime("%Y.%m.%d"),
                        help="Fallback version label when catalogue.json is absent")
    parser.add_argument("--check-only", action="store_true",
                        help="Run validation + report only; do not rewrite the docs")
    args = parser.parse_args()

    # Version stamp from the catalogue manifest, falling back to --version.
    version, _ = args.version, None
    if CATALOGUE_FILE.exists():
        try:
            cat = json.loads(CATALOGUE_FILE.read_text(encoding="utf-8"))
            version = cat.get("catalogueVersion") or version
        except (json.JSONDecodeError, OSError):
            pass
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Collect catalogue data.
    custom = load_custom_definitions()
    builtins = load_builtin_policies()
    initiatives, assignments, members = load_initiatives()
    exemptions = load_exemptions()

    # Validate.
    findings = validate(custom, builtins, initiatives, assignments, members, exemptions)
    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warning")
    summary_line = (f"**{len(custom)}** custom defs · **{len(builtins)}** built-ins · "
                    f"**{len(initiatives)}** initiatives · **{len(assignments)}** assignments — "
                    f"**{len(findings)}** findings (**{errors}** errors, **{warnings}** warnings).")

    # Shared render context.
    ctx = {
        "version": version,
        "generatedAt": generated_at,
        "sample_names": t_sample_result_names(custom),
        "checkkinds": t_checkkind_distribution(custom),
        "custom_pairs": t_custom_pairs(custom),
        "builtin_pairs": t_builtin_pairs(builtins),
        "initiative_pairs": t_initiative_pairs(initiatives),
        "assignment_pairs": t_assignment_pairs(assignments),
        "member_pairs": t_member_pairs(members),
        "findings": t_findings(findings),
        "summary_line": summary_line,
    }

    report = {
        "catalogueVersion": version,
        "generatedAt": generated_at,
        "counts": {
            "customDefinitions": len(custom),
            "builtinPolicies": len(builtins),
            "initiatives": len(initiatives),
            "assignments": len(assignments),
            "members": len(members),
            "errors": errors,
            "warnings": warnings,
        },
        "findings": [{k: v for k, v in f.items()} for f in findings],
    }

    if args.check_only:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        # newline="\n" everywhere (#52): the engine writes LF on every host, so a
        # regenerated artifact is byte-identical whoever ran the producer.
        NAMING_SAMPLES_FILE.write_text(render_naming_samples(ctx), encoding="utf-8", newline="\n")
        EPAC_NAMING_DOC.write_text(render_epac_naming_doc(ctx), encoding="utf-8", newline="\n")
        QC_REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                  encoding="utf-8", newline="\n")
        print(f"Wrote {NAMING_SAMPLES_FILE.name}, {EPAC_NAMING_DOC.name}, {QC_REPORT_FILE.name}")

    print(f"QC: {summary_line.replace('**', '')}")
    for f in findings:
        if f["severity"] == "error":
            print(f"  ERROR [{f['code']}] {f['message']}")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
