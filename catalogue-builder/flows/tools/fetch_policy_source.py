#!/usr/bin/env python3
"""Materialise the pinned official Azure Policy source into a local cache.

The producer (extract_policies.py / create_initiatives.py) reads ~5k policy JSON
files from a clone of github.com/Azure/azure-policy. To keep catalogues
reproducible, everyone should build against the SAME upstream commit rather than
whatever each person happens to have checked out. This tool reads the tracked pin
file (config/policy-source.json) and fetches exactly that commit into a gitignored
cache; the producer then resolves its --source default to the cache automatically
(see shared.paths.official_policy_source).

This is the reproducible-checkout kernel of the future daily-sync system: a
scheduler running `--sync` keeps the cache current, and `--check` reports when
upstream has moved past the pin (the drift signal a notifier would wrap).

Usage:
    python flows/tools/fetch_policy_source.py            # --sync (default)
    python flows/tools/fetch_policy_source.py --check     # report drift, no changes

Modes:
    --sync    Clone-if-absent (partial + sparse: only the pinned subdir), then
              fetch + checkout the pinned commit. Idempotent. Exits non-zero if the
              resulting HEAD does not match the pin.
    --check   git ls-remote the pinned branch and compare its HEAD to the pinned
              commit. Prints `up to date` or `DRIFT ...` and exits non-zero on drift.
              Never touches the cache.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # flows/ root
from shared.paths import POLICY_SOURCE_PIN, POLICY_SOURCE_CACHE  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def load_pin() -> dict:
    if not POLICY_SOURCE_PIN.exists():
        print(f"ERROR: pin file not found: {POLICY_SOURCE_PIN}")
        raise SystemExit(1)
    pin = json.loads(POLICY_SOURCE_PIN.read_text(encoding="utf-8"))
    for key in ("repo", "branch", "commit", "subdir"):
        if not pin.get(key):
            print(f"ERROR: pin file missing '{key}': {POLICY_SOURCE_PIN}")
            raise SystemExit(1)
    return pin


def git(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        print(f"ERROR: git {' '.join(args)}\n{result.stderr.strip()}")
        raise SystemExit(1)
    return result


def sync(pin: dict) -> None:
    cache = POLICY_SOURCE_CACHE
    repo, branch, commit, subdir = pin["repo"], pin["branch"], pin["commit"], pin["subdir"]

    if not (cache / ".git").exists():
        print(f"[fetch] cloning {repo} (partial + sparse: {subdir}) -> {cache}")
        cache.parent.mkdir(parents=True, exist_ok=True)
        git(["clone", "--filter=blob:none", "--no-checkout", "--branch", branch, repo, str(cache)])
        git(["sparse-checkout", "set", subdir], cwd=cache)

    # Ensure the pinned commit is present, then check it out. --filter keeps the
    # download to blobs under the sparse path only.
    print(f"[fetch] fetching {branch} and checking out {commit[:10]}")
    git(["fetch", "--filter=blob:none", "origin", branch], cwd=cache)
    git(["checkout", "--force", commit], cwd=cache)

    head = git(["rev-parse", "HEAD"], cwd=cache).stdout.strip()
    if head != commit:
        print(f"ERROR: checked-out HEAD {head[:10]} != pinned {commit[:10]}")
        raise SystemExit(1)

    src = cache / subdir
    count = sum(1 for _ in src.rglob("*.json")) if src.exists() else 0
    print(f"[fetch] OK — {src} at {head[:10]} ({count} JSON files)")


def check(pin: dict) -> None:
    repo, branch, commit = pin["repo"], pin["branch"], pin["commit"]
    out = git(["ls-remote", repo, f"refs/heads/{branch}"]).stdout.strip()
    if not out:
        print(f"ERROR: could not read remote {branch} of {repo}")
        raise SystemExit(1)
    remote = out.split()[0]
    if remote == commit:
        print(f"[check] up to date — pin {commit[:10]} == remote {branch} {remote[:10]}")
        return
    print(f"[check] DRIFT: pin {commit[:10]} != remote {branch} {remote[:10]} "
          f"(bump config/policy-source.json to re-sync)")
    raise SystemExit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch the pinned official Azure Policy source.")
    parser.add_argument("--check", action="store_true",
                        help="Report whether upstream has moved past the pin (no changes)")
    args = parser.parse_args()

    pin = load_pin()
    if args.check:
        check(pin)
    else:
        sync(pin)


if __name__ == "__main__":
    main()
