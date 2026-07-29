"""Build a throwaway workbench so the producer can be driven end to end in a test.

``shared/paths.py`` derives every producer path from ``PROJECT_ROOT``, which is why phases
4–5 and the release driver had no coverage: they read fixed locations, and a test that
exercised them would have written to the **real** ``catalogue/``. ``EPAC_WORKBENCH_ROOT``
relocates that root; this module assembles a tree for it to point at.

The scratch workbench is a real workbench, not a mock:

* ``engine/`` and ``customer/manifests/`` are **copied verbatim** — the code under test is
  the code that ships;
* ``config/`` is copied with the **real** hierarchy, tier rules and abbreviation map, so
  classification and naming behave exactly as in production…
* …except ``definition-gens.md``, which is rewritten with every generator **disabled**. That
  is the documented "built-in-only catalogue" mode (see the runbook, phase 4): the overlays
  still register and the stamp is still finalized, but the 169-definition naming generator
  does not run, which keeps a rehearsal in the seconds rather than the minutes;
* the policy source is ``tests/fixtures/producer/policy-source`` — 4 policies — wired in
  through ``AZURE_POLICY_REPO``, the same override a developer uses locally;
* ``examples/contoso`` gets a **minimal** manifest selecting the one group those 4 policies
  actually produce, so the driver's re-pin and fixture-rebuild steps have something real to
  act on.

Nothing here touches the repository's own ``catalogue/``.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import _engine_path  # noqa: F401

ROOT = Path(_engine_path.ROOT)
FIXTURE = Path(_engine_path.FIXTURES) / "producer"
POLICY_SOURCE = FIXTURE / "policy-source"

# The 4 fixture policies land in Tags -> Management/Essential under the REAL hierarchy,
# which is the group the scratch contoso manifest selects.
REHEARSAL_GROUP = {"domain": "management", "category": "tags", "tier": "essential"}

def gens_md(enabled=()):
    """The generator allowlist, with only ``enabled`` families turned on.

    Default is all-off: the documented "built-in-only catalogue" mode (runbook, phase 4).
    Phase 4 then applies no overlays but still registers and finalizes the stamp — which is
    what a rehearsal wants, since the real naming generator emits 169 definitions and would
    dominate the runtime of a 4-policy workbench.

    Tests that need the *overlay* path enable ``dlw-az-tagging``: one definition, and it
    exercises the NewGroup + bubbled-``customerAbbreviation`` shape (#21) in the producer.
    """
    rows = [
        ("gen_dlw_naming_definitions", "dlw-az-naming", "NewGroup · management-esn-naming"),
        ("gen_dlw_tagging_definitions", "dlw-az-tagging", "NewGroup · management-esn-tagging"),
        ("gen_dlw_az_apim_definitions", "dlw-az-apim", "Enrich · integration-esn-apim"),
    ]
    body = "\n".join(
        f"| {module} | {family} | {placement} | {'yes' if family in enabled else 'no'} |"
        for module, family, placement in rows)
    return ("# Definition generators — TEST FIXTURE\n\n"
            "Rewritten per test. See tests/workbench.py::gens_md.\n\n"
            "| Module | Family | Placement | Enabled |\n|---|---|---|---|\n" + body + "\n")

MANIFEST = {
    "schemaVersion": 1,
    "customer": "rehearsal",
    "prefix": "rhs",
    "pacOwnerId": "11111111-2222-3333-4444-555555555555",
    "source": {
        "initiatives": "../../../catalogue/initiatives",
        "catalogueVersion": "REPLACED-BY-REPIN",
        "catalogueContentHash": "sha256:REPLACED-BY-REPIN",
    },
    "output": {"root": "../package", "flavours": ["json"]},
    "environments": [{
        "selector": "epac-dev",
        "tenantId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "deploymentRootScope": "/providers/Microsoft.Management/managementGroups/rhs-root",
        "managedIdentityLocation": "westeurope",
        "enforcement": "hardened",
        "logAnalyticsWorkspaceId": (
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-mon"
            "/providers/Microsoft.OperationalInsights/workspaces/rhs-law"),
    }],
    "allowedLocations": ["westeurope"],
    "notScopes": {},
    "selection": [dict(REHEARSAL_GROUP,
                       scope={"epac-dev": ["/providers/Microsoft.Management/managementGroups/rhs-lz"]})],
    # The fixture's Tags policy has a no-default parameter, which bubbles to the initiative
    # under this generated name -- so the manifest must bind it or the rebuild step fails
    # fast (which is how the rehearsal found this the first time it ran).
    "bindings": {"defaults": {"requireTagResourcesTagName": "costCenter"}, "overrides": {}},
    "effectOverrides": [],
    "exemptions": {},
    "metadata": {},
}


def _resolved_ref(source_dir: Path) -> str:
    """The commit `create_initiatives._git_ref` will stamp for this source directory."""
    out = subprocess.run(["git", "-C", str(source_dir), "rev-parse", "HEAD"],
                         capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def build(dest: Path, generators=()) -> Path:
    """Assemble a scratch workbench at ``dest`` and return it."""
    dest.mkdir(parents=True, exist_ok=True)

    shutil.copytree(ROOT / "engine", dest / "engine",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(ROOT / "config", dest / "config")
    (dest / "config" / "definition-gens.md").write_text(gens_md(generators), encoding="utf-8",
                                                        newline="\n")

    # The pin must name the commit the source actually resolves to -- the invariant
    # fetch_policy_source.py maintains in production by checking the pin out. Here the
    # fixture source sits inside this repo, so `git rev-parse` reports THIS repo's HEAD;
    # writing that into the pin reproduces the agreement rather than faking it, and keeps
    # the rehearsal's `builtInsRef` check meaningful instead of permanently red.
    pin = json.loads((dest / "config" / "policy-source.json").read_text(encoding="utf-8"))
    pin["commit"] = _resolved_ref(POLICY_SOURCE)
    (dest / "config" / "policy-source.json").write_text(
        json.dumps(pin, indent=2) + "\n", encoding="utf-8", newline="\n")

    (dest / "customer").mkdir()
    shutil.copytree(ROOT / "customer" / "manifests", dest / "customer" / "manifests")

    shutil.copy2(ROOT / "pyproject.toml", dest / "pyproject.toml")

    manifests = dest / "examples" / "contoso" / "manifests"
    manifests.mkdir(parents=True)
    (manifests / "manifest.example.jsonc").write_text(
        json.dumps(MANIFEST, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    # Phase 5 regenerates docs/epac-naming-convention.md and does not create the folder --
    # harmless in the real tree, where docs/ is committed, but the scratch one needs it.
    (dest / "docs").mkdir()
    (dest / "catalogue").mkdir()
    return dest


def env(dest: Path) -> dict:
    """The environment that points the engine at the scratch workbench."""
    e = dict(os.environ)
    e["EPAC_WORKBENCH_ROOT"] = str(dest)
    e["AZURE_POLICY_REPO"] = str(POLICY_SOURCE)
    e.pop("PYTHONPATH", None)
    return e


def run(dest: Path, argv, check=True):
    """Run an engine script inside the scratch workbench."""
    proc = subprocess.run([sys.executable, *argv], cwd=dest, env=env(dest),
                          capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise AssertionError(
            f"{' '.join(argv)} exited {proc.returncode}\n"
            f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}")
    return proc


def seed_catalogue(dest: Path, version: str):
    """Produce a first catalogue, so a release has a predecessor to diff against."""
    run(dest, ["engine/catalogue_builder/extract_policies.py"])
    run(dest, ["engine/catalogue_builder/enrich_policies.py"])
    run(dest, ["engine/catalogue_builder/create_initiatives.py", "--version", version])
    run(dest, ["engine/definition_gen/apply_overlays.py"])
    run(dest, ["engine/catalogue_builder/quality_control.py"])
    run(dest, ["engine/tools/catalogue_changelog.py", "--write"])   # baseline ledger entry
    return json.loads((dest / "catalogue" / "catalogue.json").read_text(encoding="utf-8"))
