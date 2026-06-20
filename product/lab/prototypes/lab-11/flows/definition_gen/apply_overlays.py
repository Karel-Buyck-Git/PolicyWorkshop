"""Producer step — run the definition_gen overlays and register customs into the catalogue.

Runs **after** `create_initiatives.py` (built-in groups + `index.json` exist) and **before**
`quality_control.py`. For each generator it calls `scaffold.apply(gen.build())`, then updates the
catalogue manifests so the customs become part of the contract:

- **NewGroup** overlays are added to `index.json[groups]` (with `custom: true`);
- **Enrich** overlays bump their target group's `policyCount` and set `hasCustomMembers: true`;
- `catalogue.json` is re-stamped (`counts.groups`, `generatedAt`, `contentHash`).

    python flows/definition_gen/apply_overlays.py
"""
import hashlib
import importlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # flows/ root
from shared.paths import CATALOGUE_DIR, INDEX_FILE, CATALOGUE_FILE, DEFINITION_GENS_FILE  # noqa: E402
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
    if not gens:
        raise SystemExit(f"ERROR: no enabled generators in {DEFINITION_GENS_FILE.name}.")
    return gens


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
    for _name, gen in generators:
        result = scaffold.apply(gen.build(), version=version)
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

    groups.sort(key=lambda r: (r["domain"].lower(), VALID_TIERS.index(r["tier"]), r["category"].lower()))
    index["groups"] = groups
    _write(INDEX_FILE, index)

    catalogue = json.loads(CATALOGUE_FILE.read_text(encoding="utf-8"))
    catalogue.setdefault("counts", {})["groups"] = len(groups)
    catalogue["generatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    catalogue["contentHash"] = _content_hash(CATALOGUE_DIR, exclude={"catalogue.json"})
    _write(CATALOGUE_FILE, catalogue)

    new = [r for r in applied if r["kind"] == "new"]
    enr = [r for r in applied if r["kind"] == "enrich"]
    print(f"[apply-overlays] {len(applied)} overlay(s): {len(new)} new group(s), {len(enr)} enriched "
          f"— {len(groups)} catalogue groups, manifests re-stamped")
    for r in new:
        print(f"  + new group   {r['name']} ({r['record']['policyCount']} policies)")
    for r in enr:
        print(f"  ~ enriched    {r['target_name']} (+{len(r['added'])} custom member(s))")


if __name__ == "__main__":
    main()
