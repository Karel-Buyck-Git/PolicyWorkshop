#!/usr/bin/env python3
"""Is the committed catalogue still the one this engine produces? (#43)

    python engine/tools/check_catalogue_stamp.py

#27 made the catalogue's provenance stamps **reproducible** — `engine/shared/hashing.py`
newline-normalizes before hashing, so a hash depends on file content and nothing else. That
turns "has the catalogue drifted from the engine?" into a question answerable in seconds
**without regenerating anything**: recompute every fingerprint `catalogue.json` claims and
compare.

The drift this catches really happens: on 2026-07-23 a producer fix (#26) changed
`create_initiatives.py` without a catalogue regeneration, so the committed
`tools.createInitiatives` hash described a file that no longer existed — for a full day,
with every check green. Nothing in the repo could see it.

**This is not #8.** #8 re-runs the producer and diffs the whole catalogue, which is the only
way to catch a change in what the tools *produce*. This checks that the stamp still describes
the tools and inputs on disk — the cheap slice, meant to run on every push.

Exit: 0 in sync (notes are informational) · 1 drift · 2 the catalogue can't be read.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/ root
from shared.hashing import sha256_file, content_hash  # noqa: E402
from shared.version import __version__ as ENGINE_VERSION  # noqa: E402
from shared.paths import (  # noqa: E402
    CATALOGUE_DIR, CATALOGUE_FILE, CONFIG_DIR, HIERARCHY_FILE, TIER_RULES_FILE,
    DEFINITION_GENS_FILE, PROJECT_ROOT,
)

CATALOGUE_BUILDER_DIR = PROJECT_ROOT / "engine" / "catalogue_builder"
APPLY_OVERLAYS_FILE = PROJECT_ROOT / "engine" / "definition_gen" / "apply_overlays.py"
POLICY_SOURCE_PIN = CONFIG_DIR / "policy-source.json"

# Which stamp key fingerprints which file. Mirrors the two producer stamp sites —
# create_initiatives.write_catalogue_manifests() and the apply_overlays finalize block.
# `builtInsRef` is deliberately absent: it is an upstream git ref, not a file hash, and is
# checked separately against the pin. Any key the producer adds later and this table misses
# is reported as uncovered rather than silently skipped (see _check_coverage).
FILE_STAMPS = {
    "inputs.hierarchyHash": HIERARCHY_FILE,
    "inputs.tierRulesHash": TIER_RULES_FILE,
    "inputs.definitionGensHash": DEFINITION_GENS_FILE,
    "tools.extract": CATALOGUE_BUILDER_DIR / "extract_policies.py",
    "tools.enrich": CATALOGUE_BUILDER_DIR / "enrich_policies.py",
    "tools.createInitiatives": CATALOGUE_BUILDER_DIR / "create_initiatives.py",
    "tools.applyOverlays": APPLY_OVERLAYS_FILE,
}

# Must match the exclude set in apply_overlays.py's finalize block: files that either carry
# the hash (circular) or are timestamped. A mismatch here would make every run report drift,
# so it fails loudly rather than subtly — see the contentHash comparison below.
CONTENT_HASH_EXCLUDE = {"catalogue.json", "quality-control.json", "naming-samples.md", "CHANGELOG.md"}

OK, DRIFT, NOTE = "ok", "DRIFT", "note"


def _dotted(obj, key):
    for part in key.split("."):
        if not isinstance(obj, dict) or part not in obj:
            return None
        obj = obj[part]
    return obj


def _check_coverage(catalogue):
    """Every fingerprint the catalogue carries must be one this checker knows how to verify.

    Without this, a producer that starts stamping a new input would silently gain an
    unverified hash — the check would keep passing while covering less than it claims.
    """
    known = set(FILE_STAMPS) | {"inputs.builtInsRef"}
    stamped = {f"{section}.{k}"
               for section in ("inputs", "tools")
               for k in (catalogue.get(section) or {})}
    return sorted(stamped - known)


def main() -> int:
    if not CATALOGUE_FILE.exists():
        print(f"ERROR: no catalogue stamp at {CATALOGUE_FILE} — has the producer ever run?")
        return 2
    try:
        catalogue = json.loads(CATALOGUE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: {CATALOGUE_FILE} is not valid JSON: {exc}")
        return 2

    rows = []   # (level, label, detail)

    uncovered = _check_coverage(catalogue)
    for key in uncovered:
        rows.append((DRIFT, key, "stamped by the producer but unknown to this checker — "
                                 "add it to FILE_STAMPS in check_catalogue_stamp.py"))

    for key, path in FILE_STAMPS.items():
        stored = _dotted(catalogue, key)
        if stored is None:
            rows.append((DRIFT, key, "missing from catalogue.json — the stamp is incomplete"))
            continue
        actual = sha256_file(path)
        if not actual:
            rows.append((DRIFT, key, f"the file it fingerprints is gone: {path}"))
        elif actual != stored:
            rows.append((DRIFT, key, f"{path.name} changed since the catalogue was built\n"
                                     f"          stamped {stored}\n          on disk  {actual}"))
        else:
            rows.append((OK, key, path.name))

    # builtInsRef: not a file hash but the upstream commit the catalogue was extracted from.
    # It must still be the commit config/policy-source.json pins, or the catalogue describes
    # a source no one can reproduce.
    stored_ref = _dotted(catalogue, "inputs.builtInsRef")
    if POLICY_SOURCE_PIN.exists() and stored_ref:
        pinned = (json.loads(POLICY_SOURCE_PIN.read_text(encoding="utf-8")) or {}).get("commit")
        if pinned and stored_ref != f"git:{pinned}":
            rows.append((DRIFT, "inputs.builtInsRef",
                         f"catalogue built from {stored_ref}, but policy-source.json pins git:{pinned}"))
        elif pinned:
            rows.append((OK, "inputs.builtInsRef", stored_ref))

    stored_content = catalogue.get("contentHash")
    actual_content = content_hash(CATALOGUE_DIR, exclude=CONTENT_HASH_EXCLUDE)
    if stored_content != actual_content:
        rows.append((DRIFT, "contentHash",
                     "the catalogue on disk is not the catalogue that was stamped\n"
                     f"          stamped {stored_content}\n          on disk  {actual_content}\n"
                     "          (if only the exclude set moved, reconcile CONTENT_HASH_EXCLUDE "
                     "here with apply_overlays.py)"))
    else:
        rows.append((OK, "contentHash", f"{len(list(CATALOGUE_DIR.rglob('*')))} paths under catalogue/"))

    # Informational only. A catalogue produced by an older engine is accurate provenance, not
    # drift — it only matters if something the catalogue *depends on* changed, which the hashes
    # above already cover.
    produced_by = catalogue.get("producedByEngine")
    if produced_by and produced_by != ENGINE_VERSION:
        rows.append((NOTE, "producedByEngine",
                     f"catalogue built by engine {produced_by}, this engine is {ENGINE_VERSION} — "
                     "fine unless a producer input above also moved"))

    width = max(len(label) for _, label, _ in rows)
    for level, label, detail in rows:
        mark = {OK: "  ok  ", DRIFT: " DRIFT", NOTE: " note "}[level]
        print(f"[{mark}] {label.ljust(width)}  {detail}")

    drifted = [r for r in rows if r[0] == DRIFT]
    print()
    if drifted:
        print(f"FAIL: {len(drifted)} stamp(s) drifted — catalogue {catalogue.get('catalogueVersion')} "
              f"no longer describes the engine on disk.")
        print("Fix: re-run the producer (/catalogue-builder-run, phases 1-5) and commit the "
              "regenerated catalogue/, so the stamp matches the tools that produced it.")
        return 1
    print(f"OK: catalogue {catalogue.get('catalogueVersion')} is in sync with the engine "
          f"({len(rows)} stamp(s) verified).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
