#!/usr/bin/env python3
"""Catalogue release driver — runs Phase 6 of `/catalogue-builder-run` (#51 follow-on).

Phase 6 is a nine-step sequence with two traps that bite *silently* if you get the order
wrong, and it was run by hand for every release up to and including `2026.07.28`. Writing
it down fixed "invoked from memory"; this fixes "nine steps a tired person can skip".

    python engine/tools/release_catalogue.py --version 2026.07.28          # plan only
    python engine/tools/release_catalogue.py --version 2026.07.28 --yes    # actually run
    python engine/tools/release_catalogue.py --version 2026.07.28 --yes --from 3

What it will NOT do, on purpose:

* **commit, tag or push.** `release.py --apply --tag` is one command and belongs to a human
  who has read the diff. The driver prints exactly what to run.
* **write the changelog's human paragraph.** The tool attributes the driver and counts the
  deltas; only a person can say *why* the release happened, and every entry so far has
  needed one. The driver stops and asks for it.

Both traps are handled rather than documented:

* **Staging before the wipe** — phase 3 `shutil.rmtree`s `catalogue/initiatives/`, so the
  previous catalogue must be copied *first* or the changelog diff has nothing to compare
  against. The driver stages before it runs anything.
* **`MAX_PATH`** — the staged copy must sit at a short root or `catalogue_diff` refuses to
  read it (#46). The driver measures the deepest resulting path and fails *before* the
  pipeline starts rather than after the wipe.

Stdlib only.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/ root

from shared.paths import (  # noqa: E402
    PROJECT_ROOT, CATALOGUE_DIR, CATALOGUE_FILE, MANIFESTS_DIR,
)

WINDOWS_MAX_PATH = 260
DEFAULT_STAGE = Path("C:/tmp/cat-prev") if os.name == "nt" else Path("/tmp/cat-prev")

CONTOSO_MANIFEST = PROJECT_ROOT / "examples" / "contoso" / "manifests" / "manifest.example.jsonc"
FIXTURES = [
    ("json", PROJECT_ROOT / "examples" / "contoso" / "package"),
    ("terraform", PROJECT_ROOT / "examples" / "contoso" / "fixtures" / "terraform"),
    ("bicep", PROJECT_ROOT / "examples" / "contoso" / "fixtures" / "bicep"),
]

PHASES = {
    1: ("fetch + extract", [
        ["engine/tools/fetch_policy_source.py"],
        ["engine/catalogue_builder/extract_policies.py"],
    ]),
    2: ("enrich", [["engine/catalogue_builder/enrich_policies.py"]]),
    3: ("create initiatives", [["engine/catalogue_builder/create_initiatives.py"]]),   # + --version
    4: ("apply overlays", [["engine/definition_gen/apply_overlays.py"]]),
    5: ("quality control", [["engine/catalogue_builder/quality_control.py"]]),
}


class ReleaseError(Exception):
    """A precondition failed, or a step did. Always raised *before* damage where possible."""


def run(argv, why):
    print(f"\n$ python {' '.join(argv)}")
    proc = subprocess.run([sys.executable, *argv], cwd=PROJECT_ROOT)
    if proc.returncode != 0:
        raise ReleaseError(f"{why} failed (exit {proc.returncode}) — stopping. "
                           f"Fix it and re-run with --from to resume.")


def run_shell(argv, why):
    print(f"\n$ {' '.join(argv)}")
    proc = subprocess.run(argv, cwd=PROJECT_ROOT)
    if proc.returncode != 0:
        raise ReleaseError(f"{why} failed (exit {proc.returncode}).")


def stage_previous(stage_root, force):
    """Copy the current catalogue somewhere short, BEFORE phase 3 deletes half of it."""
    if not CATALOGUE_DIR.is_dir():
        raise ReleaseError(f"no catalogue at {CATALOGUE_DIR} to stage")
    if stage_root.exists():
        if not force:
            raise ReleaseError(
                f"staging path already exists: {stage_root}\n"
                f"It is probably a previous release's copy. Remove it, or pass --force to "
                f"overwrite — but check first: once phase 3 has run, this copy is the ONLY "
                f"record of the catalogue you are diffing against.")
        shutil.rmtree(stage_root)

    # Measure before copying: the deepest path the copy WILL create. #46 -- a staged tree
    # over MAX_PATH reads as unreadable, and the tool then refuses to diff (correctly, but
    # after phase 3 has already wiped the original).
    deepest = max((len(str(stage_root / p.relative_to(CATALOGUE_DIR)))
                   for p in CATALOGUE_DIR.rglob("*")), default=len(str(stage_root)))
    if os.name == "nt" and deepest >= WINDOWS_MAX_PATH:
        raise ReleaseError(
            f"staging at {stage_root} would produce paths up to {deepest} chars, over the "
            f"{WINDOWS_MAX_PATH}-char Windows limit. catalogue_diff would refuse to read it "
            f"(#46) — and it would refuse AFTER phase 3 had wiped the original. "
            f"Pass --stage with a shorter root (e.g. C:\\tmp\\c).")

    stage_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(CATALOGUE_DIR, stage_root)
    prev = json.loads((stage_root / "catalogue.json").read_text(encoding="utf-8"))
    print(f"[stage] {CATALOGUE_DIR.name} -> {stage_root}  "
          f"(version {prev.get('catalogueVersion')}, deepest path {deepest} chars)")
    return prev


def check_version_free(version, stage_root):
    """Refuse a label the ledger already released for different content (#48), early."""
    from shared.changelog import released_versions, next_free_label
    released = released_versions(PROJECT_ROOT / "catalogue" / "CHANGELOG.md")
    if version in released:
        raise ReleaseError(
            f"version label '{version}' is already recorded in CHANGELOG.md. Phase 4 would "
            f"refuse it unless the content is byte-identical. Use "
            f"--version {next_free_label(version, released)} — or, if you are deliberately "
            f"amending a release that never left this machine, run the phases by hand with "
            f"apply_overlays.py --allow-version-reuse.")


def repin_contoso():
    """Both pins move on every release: the label AND the precise contentHash (#48)."""
    import re
    cat = json.loads(CATALOGUE_FILE.read_text(encoding="utf-8"))
    text = CONTOSO_MANIFEST.read_text(encoding="utf-8")
    text, n1 = re.subn(r'("catalogueVersion":\s*)"[^"]+"',
                       r'\1"%s"' % cat["catalogueVersion"], text, count=1)
    text, n2 = re.subn(r'("catalogueContentHash":\s*)"[^"]+"',
                       r'\1"%s"' % cat["contentHash"], text, count=1)
    if not n1:
        raise ReleaseError(f"could not find catalogueVersion in {CONTOSO_MANIFEST}")
    if not n2:
        print("[repin] WARNING: no catalogueContentHash pin found — the manifest pins by "
              "label alone, which two same-day releases share (#48).")
    CONTOSO_MANIFEST.write_text(text, encoding="utf-8", newline="\n")
    print(f"[repin] contoso -> {cat['catalogueVersion']} / {cat['contentHash'][:23]}…")


def rebuild_fixtures():
    for flavour, out in FIXTURES:
        run(["engine/epac_builder/assemble_scaffold.py", "--manifest", str(CONTOSO_MANIFEST),
             "--only", flavour, "--out", str(out)], f"rebuilding the {flavour} fixture")


def battery():
    run_shell(["bash", "examples/contoso/verify.sh"], "verify.sh")
    run_shell(["bash", "engine/mcp_server/test_server.sh"], "the MCP smoke test")
    run(["engine/tools/check_catalogue_stamp.py"], "the catalogue stamp check")
    run(["-m", "unittest", "discover", "-s", "tests", "-t", "tests"], "the unit tests")


def plan(args, stage_root):
    print(f"""
Catalogue release plan — version {args.version}
{'=' * 60}
  0. stage {CATALOGUE_DIR} -> {stage_root}   (BEFORE phase 3 wipes initiatives/)
     refuse early if the label is already in CHANGELOG.md, or MAX_PATH would bite
  1. engine bump: release.py --apply        {'(skipped: --no-bump)' if args.no_bump else '(before regenerating!)'}
  2. phases {args.from_phase}-5
  3. check_catalogue_stamp.py
  4. catalogue_changelog.py --old {stage_root} --write
  5. re-pin contoso (catalogueVersion AND catalogueContentHash)
  6. rebuild json / terraform / bicep fixtures
  7. battery: verify.sh, MCP smoke, stamp check, unit tests

Then YOU: write the changelog's human paragraph, read the diff, commit,
          `release.py --apply --tag`, push the branch and the tag.

Nothing has been changed. Re-run with --yes to execute.
""".rstrip())


def main(argv=None):
    ap = argparse.ArgumentParser(description="Drive a catalogue release (Phase 6 of the runbook).")
    ap.add_argument("--version", required=True, help="catalogue version label, e.g. 2026.07.28")
    ap.add_argument("--yes", action="store_true", help="actually run (default: print the plan)")
    ap.add_argument("--stage", type=Path, default=DEFAULT_STAGE,
                    help=f"where to stage the previous catalogue (default: {DEFAULT_STAGE})")
    ap.add_argument("--from", dest="from_phase", type=int, default=1, choices=[1, 2, 3, 4, 5],
                    help="resume from this phase (see the runbook's which-phase table)")
    ap.add_argument("--no-bump", action="store_true",
                    help="skip the engine version bump (use when release.py proposes none)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing staging path")
    args = ap.parse_args(argv)

    stage_root = args.stage.resolve()
    if not args.yes:
        plan(args, stage_root)
        return 0

    try:
        check_version_free(args.version, stage_root)
        stage_previous(stage_root, args.force)

        if not args.no_bump:
            # BEFORE the regeneration: producedByEngine is stamped during phases 3-4, so a
            # bump applied afterwards leaves the catalogue naming the previous engine (#53).
            run(["engine/tools/release.py", "--apply"], "the engine version bump")

        for phase in range(args.from_phase, 6):
            label, scripts = PHASES[phase]
            print(f"\n=== Phase {phase} — {label} ===")
            for script in scripts:
                extra = ["--version", args.version] if phase == 3 else []
                run(script + extra, f"phase {phase} ({label})")

        run(["engine/tools/check_catalogue_stamp.py"], "the catalogue stamp check")
        run(["engine/tools/catalogue_changelog.py", "--old", str(stage_root), "--write"],
            "writing the changelog entry")
        repin_contoso()
        rebuild_fixtures()
        battery()
    except ReleaseError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 2

    print(f"""
{'=' * 60}
Release {args.version} is built, recorded and verified. THREE THINGS LEFT, all yours:

  1. Write the "why this release happened" paragraph into catalogue/CHANGELOG.md.
     The tool attributed the driver and counted the deltas; it cannot say why.
     Say what a consumer pinned to the previous version has to do.
  2. Read the diff. `git diff --stat` — a policy-level change you did not expect
     is the signal to stop.
  3. Commit, then:  python engine/tools/release.py --apply --tag
                    git push origin <branch> && git push origin v<x.y.z>

The staged previous catalogue is still at {stage_root} — keep it until the
changelog entry is committed, then delete it.
""".rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
