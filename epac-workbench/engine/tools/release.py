#!/usr/bin/env python3
"""Auto-SemVer release helper — semantic version, automatically derived (#27).

The engine version is SemVer, but the *number is not hand-picked*: it is computed
from the Conventional-Commit prefixes on the commits since the last ``v*`` git tag,
which this repo already writes:

    feat!: / BREAKING CHANGE:  -> major   (0.3.1 -> 1.0.0)
    feat:                      -> minor   (0.3.1 -> 0.4.0)
    fix: / perf:               -> patch   (0.3.1 -> 0.3.2)
    docs/chore/refactor/test/… -> no release-worthy change on their own

The only judgement a human makes is *"is this breaking?"* — encoded as the ``!``
you already type in the commit. git tags stay the human-facing release markers;
``engine/shared/version.py`` + ``pyproject.toml`` are kept in lockstep so the
stamped artifacts (catalogue.json, lineage.json) are byte-reproducible.

Usage:
    python engine/tools/release.py                # dry-run: analyse + print proposal
    python engine/tools/release.py --apply        # write version.py + pyproject.toml
    python engine/tools/release.py --apply --tag   # also create the annotated v<x.y.z> tag

Stdlib only; no third-party release tooling (keeps ``dependencies = []``).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # epac-workbench/
VERSION_PY = ROOT / "engine" / "shared" / "version.py"
PYPROJECT = ROOT / "pyproject.toml"

# Conventional-Commit subject: type(scope)!: description
_CC = re.compile(r"^(?P<type>\w+)(?:\([^)]*\))?(?P<bang>!)?:", re.IGNORECASE)
_MINOR = {"feat"}
_PATCH = {"fix", "perf"}


def _git(*args):
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def _current_version():
    m = re.search(r'__version__\s*=\s*"([^"]+)"', VERSION_PY.read_text(encoding="utf-8"))
    if not m:
        sys.exit(f"could not read __version__ from {VERSION_PY}")
    return m.group(1)


def _latest_tag():
    tags = [t for t in _git("tag", "--list", "v*").splitlines() if re.fullmatch(r"v\d+\.\d+\.\d+", t)]
    tags.sort(key=lambda t: tuple(int(n) for n in t[1:].split(".")))
    return tags[-1] if tags else None


def _classify(subjects, bodies):
    """Return the bump level implied by the commits: 'major' | 'minor' | 'patch' | None."""
    level = None
    rank = {"patch": 1, "minor": 2, "major": 3}
    def bump(l):
        nonlocal level
        if level is None or rank[l] > rank[level]:
            level = l
    for subj in subjects:
        m = _CC.match(subj)
        if not m:
            continue
        if m.group("bang"):
            bump("major")
        elif m.group("type").lower() in _MINOR:
            bump("minor")
        elif m.group("type").lower() in _PATCH:
            bump("patch")
    if any("BREAKING CHANGE" in b for b in bodies):
        bump("major")
    return level


def _next(version, level):
    major, minor, patch = (int(n) for n in version.split("."))
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def _write_version(new):
    # newline="\n" (#52): rewriting these two files must change the version line and
    # nothing else — without it, a bump run on Windows re-writes the whole file as CRLF.
    VERSION_PY.write_text(
        re.sub(r'__version__\s*=\s*"[^"]+"', f'__version__ = "{new}"',
               VERSION_PY.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    PYPROJECT.write_text(
        re.sub(r'^version\s*=\s*"[^"]+"', f'version = "{new}"',
               PYPROJECT.read_text(encoding="utf-8"), count=1, flags=re.MULTILINE),
        encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser(description="Auto-SemVer release helper (#27).")
    ap.add_argument("--apply", action="store_true", help="write version.py + pyproject.toml")
    ap.add_argument("--tag", action="store_true", help="also create the annotated v<x.y.z> git tag")
    args = ap.parse_args()

    current = _current_version()
    tag = _latest_tag()

    if tag is None:
        print(f"No v* tag yet. Current version.py = {current}.")
        print(f"Proposal: establish the baseline tag v{current} at HEAD.")
        new = current
    else:
        base = tag[1:]
        rng = f"{tag}..HEAD"
        subjects = [s for s in _git("log", rng, "--format=%s").splitlines() if s]
        bodies = _git("log", rng, "--format=%b").split("\n\n")
        if not subjects:
            print(f"No commits since {tag}. Nothing to release.")
            return
        level = _classify(subjects, bodies)
        if level is None:
            print(f"{len(subjects)} commit(s) since {tag}, none release-worthy "
                  f"(no feat/fix/perf/!). No version bump.")
            return
        new = _next(base, level)
        print(f"{len(subjects)} commit(s) since {tag}: bump = {level.upper()}  ({base} -> {new})")

    if not args.apply:
        print("\n(dry-run — re-run with --apply to write version.py + pyproject.toml, "
              "--apply --tag to also commit the bump and create the git tag.)")
        return

    _write_version(new)
    print(f"Wrote {new} to version.py + pyproject.toml.")
    if not args.tag:
        print("Next: commit these two files, then tag that commit — or re-run with --apply --tag.")
        return

    # --tag: the tag must land on a commit that CONTAINS this version bump. Commit the two
    # version files first (if the write changed them), so `git describe` at the tag reports `new`.
    changed = _git("status", "--porcelain", str(VERSION_PY), str(PYPROJECT))
    if changed:
        subprocess.run(["git", "add", str(VERSION_PY), str(PYPROJECT)], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", f"chore(release): v{new}"], cwd=ROOT, check=True)
        print(f"Committed the v{new} bump.")
    else:
        print(f"version.py/pyproject already at {new} (baseline) — tagging HEAD.")
    r = subprocess.run(["git", "tag", "-a", f"v{new}", "-m", f"Release v{new}"], cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"git tag v{new} failed (does it already exist?).")
    print(f"Created annotated tag v{new}. Publish with: git push origin v{new} (and push the branch).")


if __name__ == "__main__":
    main()
