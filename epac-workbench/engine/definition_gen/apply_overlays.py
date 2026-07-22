"""Producer step — run the definition_gen overlays and register customs into the catalogue.

Runs **after** `create_initiatives.py` (built-in groups + `index.json` exist) and **before**
`quality_control.py`. For each generator it calls `scaffold.apply(gen.build())`, then updates the
catalogue manifests so the customs become part of the contract:

- **NewGroup** overlays are added to `index.json[groups]` (with `custom: true`);
- **Enrich** overlays bump their target group's `policyCount` and set `hasCustomMembers: true`;
- `catalogue.json` is re-stamped (`counts.groups`, `generatedAt`, `contentHash`).

    python engine/definition_gen/apply_overlays.py
"""
import hashlib
import importlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/ root
from shared.paths import (  # noqa: E402
    CATALOGUE_DIR, DEFINITIONS_DIR, INDEX_FILE, CATALOGUE_FILE, DEFINITION_GENS_FILE)
from definition_gen import scaffold  # noqa: E402

VALID_TIERS = ["Essential", "Professional", "Enterprise"]
_ENABLED = {"yes", "true", "y", "x", "✓"}


def load_generators():
    """Read the authored allowlist (config/definition-gens.md) and import the enabled modules.

    The registry of *which* generators contribute to the catalogue lives in config, not code —
    only rows with Enabled=yes are imported and run, in listed order.
    """
    if not DEFINITION_GENS_FILE.exists():
        raise SystemExit(f"ERROR: generator registry not found: {DEFINITION_GENS_FILE}")
    gens, header = [], None
    for line in DEFINITION_GENS_FILE.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= set("-: "):          # separator row
            continue
        row = dict(zip(header, cells))
        if row.get("enabled", "").lower() not in _ENABLED:
            continue
        name = row.get("module", "")
        if not name:
            continue
        try:
            mod = importlib.import_module(f"definition_gen.{name}")
        except ImportError as e:
            raise SystemExit(f"ERROR: {DEFINITION_GENS_FILE.name} lists '{name}' but it can't be "
                             f"imported as definition_gen.{name}: {e}")
        if not hasattr(mod, "build"):
            raise SystemExit(f"ERROR: generator '{name}' has no build() function.")
        gens.append((name, mod))
    return gens   # may be empty — that's a valid built-in-only build (apply-overlays still finalizes)


def _sha256_file(path):
    p = Path(path)
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else ""


def _content_hash(root, exclude):
    h = hashlib.sha256()
    for p in sorted(Path(root).rglob("*")):
        if not p.is_file() or p.name in exclude:
            continue
        rel = str(p.relative_to(root)).replace("\\", "/")
        h.update(rel.encode("utf-8")); h.update(b"\x00")
        h.update(p.read_bytes()); h.update(b"\x00")
    return "sha256:" + h.hexdigest()


def _write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    if not INDEX_FILE.exists():
        print("ERROR: index.json not found — run create_initiatives.py first.", file=sys.stderr)
        raise SystemExit(1)

    index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    version = index.get("catalogueVersion", "")
    groups = index["groups"]
    by_name = {g["name"]: g for g in groups}

    generators = load_generators()
    applied = []
    applied_families = set()
    for _name, gen in generators:
        overlay = gen.build()
        applied_families.add(overlay.family)
        result = scaffold.apply(overlay, version=version)
        applied.append(result)
        if result["kind"] == "new":
            rec = result["record"]
            if rec["name"] in by_name:                      # idempotent: replace existing record
                groups[groups.index(by_name[rec["name"]])] = rec
            else:
                groups.append(rec)
            by_name[rec["name"]] = rec
        else:  # enrich
            rec = by_name.get(result["target_name"])
            if rec is None:
                print(f"ERROR: enrich target '{result['target_name']}' is not in index.json.", file=sys.stderr)
                raise SystemExit(1)
            rec["policyCount"] = result["member_count"]     # actual count -> idempotent
            rec["hasCustomMembers"] = True

    # Prune custom-definition families whose generator is no longer enabled, so a disabled
    # generator (or a fully built-in-only build) leaves no orphaned definitions behind.
    pruned = []
    custom_root = DEFINITIONS_DIR / "custom"
    if custom_root.exists():
        for fam in sorted(custom_root.iterdir()):
            if fam.is_dir() and fam.name not in applied_families:
                shutil.rmtree(fam)
                pruned.append(fam.name)

    groups.sort(key=lambda r: (r["domain"].lower(), VALID_TIERS.index(r["tier"]), r["category"].lower()))
    index["groups"] = groups
    _write(INDEX_FILE, index)

    # Authoritative stamp (Phase ④ finalize): create_initiatives left contentHash 'pending';
    # apply_overlays writes the one true hash over the whole catalogue (built-in + custom) and
    # fingerprints the custom layer so drift detection (catalogue_diff) sees generator changes.
    catalogue = json.loads(CATALOGUE_FILE.read_text(encoding="utf-8"))
    catalogue.setdefault("counts", {})["groups"] = len(groups)
    catalogue.setdefault("inputs", {})["definitionGensHash"] = _sha256_file(DEFINITION_GENS_FILE)
    catalogue.setdefault("tools", {})["applyOverlays"] = _sha256_file(Path(__file__))
    catalogue["generatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # Fingerprint the *substantive* catalogue (definitions + initiatives + index.json), not the
    # version stamp itself nor the timestamped QC reports — so the hash is deterministic and
    # reflects content, not when QC last ran.
    catalogue["contentHash"] = _content_hash(
        CATALOGUE_DIR, exclude={"catalogue.json", "quality-control.json", "naming-samples.md"})
    _write(CATALOGUE_FILE, catalogue)

    new = [r for r in applied if r["kind"] == "new"]
    enr = [r for r in applied if r["kind"] == "enrich"]
    print(f"[apply-overlays] {len(applied)} overlay(s): {len(new)} new group(s), {len(enr)} enriched "
          f"— {len(groups)} catalogue groups, catalogue finalized")
    for r in new:
        print(f"  + new group   {r['name']} ({r['record']['policyCount']} policies)")
    for r in enr:
        print(f"  ~ enriched    {r['target_name']} (+{len(r['added'])} custom member(s))")
    if pruned:
        print(f"  - pruned disabled families: {', '.join(pruned)}")


if __name__ == "__main__":
    main()
