"""Environment doctor — is this machine set up to run the catalogue-builder tooling?

    python engine/tools/check_env.py

Pure stdlib, standalone (imports nothing from the repo) and deliberately written in
old-Python-compatible syntax, so it still runs — and reports "too old" — on a 3.8/3.9
interpreter. It checks the toolchain a *contributor* needs and prints a friendly fix for
anything missing, instead of letting a script die later with a raw `set -euo pipefail` error.

It does NOT check deploy-time prerequisites (PowerShell, Az, the EPAC module) — those live
in docs/scaffold-deployment-guide.md and only matter once you push a package to Azure.

Exit: 0 all good · 1 a per-flow tool is missing (bash/diff/git, or `python` for MCP) ·
2 the Python interpreter is too old (the one hard requirement).
"""
import platform
import shutil
import sys

MIN_PYTHON = (3, 10)

OK, WARN, FAIL = "ok", "warn", "FAIL"


def _is_windows():
    return platform.system() == "Windows"


def _check_python_version():
    v = sys.version_info
    detail = "%d.%d.%d  (%s)" % (v.major, v.minor, v.micro, sys.executable)
    if (v.major, v.minor) >= MIN_PYTHON:
        return ("Python interpreter", OK, detail, None)
    fix = "need Python >= %d.%d — install a newer Python and re-run with it" % MIN_PYTHON
    return ("Python interpreter", FAIL, detail, fix)


def _check_on_path(exe, needed_for, windows_fix=None, level_if_missing=WARN):
    found = shutil.which(exe)
    if found:
        return (exe, OK, found, None)
    fix = windows_fix if (windows_fix and _is_windows()) else ("install %s (needed for %s)" % (exe, needed_for))
    return (exe, level_if_missing, "not found on PATH  (needed for %s)" % needed_for, fix)


GITBASH = "on Windows, install Git for Windows - its Git Bash bundles bash + diff"


def collect():
    results = [_check_python_version()]

    # .mcp.json launches the server via bare `python`; a machine with only `python3`
    # would fail to start it even though the interpreter version is fine.
    results.append(_check_on_path(
        "python", "the MCP server in .mcp.json (which calls `python`)",
        windows_fix="`python` should be on PATH from the official installer; "
                    "if only `python3` exists, add a `python` alias or adjust .mcp.json"))

    results.append(_check_on_path("bash", "examples/contoso/verify.sh + the health check",
                                  windows_fix=GITBASH))
    results.append(_check_on_path("diff", "verify.sh byte-for-byte fixture diffs",
                                  windows_fix=GITBASH))
    results.append(_check_on_path("git", "the /reset-customer-package flow and normal work"))
    return results


def main():
    print("catalogue-builder environment check  (%s)\n" % platform.platform())

    results = collect()
    mark = {OK: "  [ok]  ", WARN: "  [warn]", FAIL: "  [FAIL]"}
    for name, status, detail, fix in results:
        print("%s %-8s %s" % (mark[status], name, detail))
        if fix:
            print("           -> %s" % fix)

    print("")
    has_fail = any(r[1] == FAIL for r in results)
    has_warn = any(r[1] == WARN for r in results)
    if has_fail:
        print("Not ready: fix the [FAIL] above (the Python version is the one hard requirement).")
        return 2
    if has_warn:
        print("Mostly ready: the [warn] tools are missing - the flows that need them won't run "
              "until you install them. Everything else is good.")
        return 1
    print("All good - you can run the builder tooling. Next: `python engine/tools/fetch_policy_source.py` "
          "then `/epac-builder-start`, or `/epac-builder-onboard` to build your own package.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
