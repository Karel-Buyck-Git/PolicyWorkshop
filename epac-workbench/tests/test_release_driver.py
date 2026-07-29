"""Release rehearsal — drive a whole catalogue release against a scratch workbench.

**This test exists so the release driver cannot rot.** A monthly tool gets ~12 real
executions a year while the engine underneath it changes weekly, so the driver would
otherwise be discovered broken on release day — the worst possible moment, and precisely
when hand-running becomes the fast path and the tool is abandoned. Here the happy path
runs on every push, against a 4-policy workbench, in seconds.

What the rehearsal covers that CI otherwise cannot: the **sequence**. The individual
battery commands (`verify.sh`, the MCP smoke test, the stamp check, the unit tests) are
already run directly by CI, so the rehearsal passes `--no-battery`; what nothing else
exercises is stage → bump → phases → stamp → changelog → re-pin → fixtures, in that order,
with the staging happening *before* phase 3 destroys what it stages.

Nothing here touches the repository's own `catalogue/` — `EPAC_WORKBENCH_ROOT` points the
whole producer at a temp tree (see `tests/workbench.py`).
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import _engine_path  # noqa: F401
import workbench

from tools.release_catalogue import STEPS  # noqa: E402

RUNBOOK = Path(_engine_path.ROOT).parent / ".claude" / "commands" / "catalogue-builder-run.md"
DRIVER = "engine/tools/release_catalogue.py"

PREVIOUS = "0000.00.01"
RELEASE = "0000.00.02"


class RehearsalCase(unittest.TestCase):
    """One full release, driven end to end, shared by the assertions below."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.mkdtemp(prefix="epac-rehearsal-")
        root = Path(cls._tmp)
        cls.wb = workbench.build(root / "wb")
        cls.stage = root / "prev"          # short path: MAX_PATH is a real constraint (#46)
        cls.before = workbench.seed_catalogue(cls.wb, PREVIOUS)

        cls.proc = subprocess.run(
            [sys.executable, DRIVER, "--version", RELEASE, "--yes",
             "--stage", str(cls.stage), "--no-fetch", "--no-battery", "--no-bump"],
            cwd=cls.wb, env=workbench.env(cls.wb), capture_output=True, text=True)
        cls.out = cls.proc.stdout + cls.proc.stderr

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._tmp, ignore_errors=True)

    def catalogue(self):
        return json.loads((self.wb / "catalogue" / "catalogue.json").read_text(encoding="utf-8"))


class TestRehearsalSucceeds(RehearsalCase):
    def test_the_driver_completes(self):
        self.assertEqual(self.proc.returncode, 0,
                         f"driver failed:\n{self.out}")

    def test_it_staged_the_previous_catalogue_before_wiping_it(self):
        # The staged copy must be the PREVIOUS release, not the new one -- proof that
        # staging happened before phase 3's rmtree rather than after.
        staged = json.loads((self.stage / "catalogue.json").read_text(encoding="utf-8"))
        self.assertEqual(staged["catalogueVersion"], PREVIOUS)
        self.assertEqual(staged["contentHash"], self.before["contentHash"])

    def test_it_produced_the_new_catalogue(self):
        self.assertEqual(self.catalogue()["catalogueVersion"], RELEASE)

    def test_it_finalized_the_stamp(self):
        # 'pending' would mean phase 4 never ran -- the state phase 5 exists to reject.
        self.assertNotEqual(self.catalogue()["contentHash"], "sha256:pending")

    def test_it_recorded_the_release_in_the_ledger(self):
        # The step whose absence makes #48's collision guard blind (#51).
        changelog = (self.wb / "catalogue" / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## {RELEASE}", changelog)
        self.assertIn(f"## {PREVIOUS}", changelog, "the previous entry must survive")

    def test_it_repinned_contoso_on_both_pins(self):
        manifest = json.loads(
            (self.wb / "examples" / "contoso" / "manifests" / "manifest.example.jsonc")
            .read_text(encoding="utf-8"))
        self.assertEqual(manifest["source"]["catalogueVersion"], RELEASE)
        self.assertEqual(manifest["source"]["catalogueContentHash"],
                         self.catalogue()["contentHash"])

    def test_it_rebuilt_the_package(self):
        pkg = self.wb / "examples" / "contoso" / "package"
        self.assertTrue((pkg / "Definitions" / "global-settings.jsonc").exists())
        lineage = json.loads((pkg / "lineage.json").read_text(encoding="utf-8"))
        self.assertEqual(lineage["catalogueVersion"], RELEASE)

    def test_it_says_what_the_human_still_owes(self):
        # The driver deliberately stops short of the changelog paragraph, the diff read,
        # and the commit/tag. If that message ever disappears, those get forgotten.
        for owed in ("paragraph", "diff", "--apply --tag"):
            self.assertIn(owed, self.out)

    def test_skipping_the_battery_is_reported_loudly(self):
        self.assertIn("BATTERY SKIPPED", self.out)
        self.assertIn("NOT VERIFIED", self.out)


class TestRehearsalRefusals(unittest.TestCase):
    """The three guards, each of which must fire BEFORE anything is modified."""

    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="epac-rehearsal-guard-")
        root = Path(self._tmp)
        self.wb = workbench.build(root / "wb")
        self.stage = root / "prev"
        self.before = workbench.seed_catalogue(self.wb, PREVIOUS)

    def tearDown(self):
        shutil.rmtree(self._tmp, ignore_errors=True)

    def drive(self, *extra):
        return subprocess.run(
            [sys.executable, DRIVER, "--version", RELEASE, "--yes", "--stage", str(self.stage),
             "--no-fetch", "--no-battery", "--no-bump", *extra],
            cwd=self.wb, env=workbench.env(self.wb), capture_output=True, text=True)

    def assert_catalogue_untouched(self):
        now = json.loads((self.wb / "catalogue" / "catalogue.json").read_text(encoding="utf-8"))
        self.assertEqual(now["catalogueVersion"], PREVIOUS)
        self.assertEqual(now["contentHash"], self.before["contentHash"])

    def test_a_released_label_is_refused_before_any_work(self):
        proc = subprocess.run(
            [sys.executable, DRIVER, "--version", PREVIOUS, "--yes", "--stage", str(self.stage),
             "--no-fetch", "--no-battery", "--no-bump"],
            cwd=self.wb, env=workbench.env(self.wb), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("already recorded in CHANGELOG.md", proc.stdout + proc.stderr)
        self.assertFalse(self.stage.exists(), "it must refuse before staging anything")
        self.assert_catalogue_untouched()

    def test_an_existing_staging_path_is_refused(self):
        self.stage.mkdir(parents=True)
        proc = self.drive()
        self.assertEqual(proc.returncode, 2)
        self.assertIn("staging path already exists", proc.stdout + proc.stderr)
        self.assert_catalogue_untouched()

    def test_force_overwrites_an_existing_staging_path(self):
        self.stage.mkdir(parents=True)
        (self.stage / "stale.txt").write_text("junk\n", encoding="utf-8", newline="\n")
        proc = self.drive("--force")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertFalse((self.stage / "stale.txt").exists())


class TestPlanModeChangesNothing(unittest.TestCase):
    def test_plan_mode_touches_nothing(self):
        tmp = tempfile.mkdtemp(prefix="epac-rehearsal-plan-")
        try:
            wb = workbench.build(Path(tmp) / "wb")
            before = workbench.seed_catalogue(wb, PREVIOUS)
            stage = Path(tmp) / "prev"
            proc = subprocess.run(
                [sys.executable, DRIVER, "--version", RELEASE, "--stage", str(stage)],
                cwd=wb, env=workbench.env(wb), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0)
            self.assertIn("Nothing has been changed", proc.stdout)
            self.assertFalse(stage.exists())
            after = json.loads((wb / "catalogue" / "catalogue.json").read_text(encoding="utf-8"))
            self.assertEqual(after["contentHash"], before["contentHash"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestRunbookAndDriverAgree(unittest.TestCase):
    """Anti-drift: the release sequence now exists in two places.

    Writing the procedure down fixed "invoked from memory" (#51); scripting it fixed "nine
    steps a tired person can skip". The cost of both is that the runbook prose and the
    driver's code are two descriptions of one sequence, and nothing stops them diverging —
    the same failure mode one level up. So the driver's step list is the authority for
    *sequence*, the runbook keeps the *why* and the traps, and this test refuses to let a
    step exist in one and not the other.
    """

    def setUp(self):
        self.runbook = RUNBOOK.read_text(encoding="utf-8")

    def test_every_driver_step_is_documented_in_the_runbook(self):
        text = self.runbook.lower()
        for name, _what, marker in STEPS:
            self.assertIn(marker.lower(), text,
                          f"driver step '{name}' has no counterpart in the runbook "
                          f"(looked for {marker!r}) — the procedure and the tool have diverged. "
                          f"Fix whichever one is wrong; do not just change the marker.")

    def test_the_runbook_points_at_the_driver(self):
        self.assertIn("release_catalogue.py", self.runbook)

    def test_the_runbook_states_the_no_hand_finishing_rule(self):
        # The policy that keeps the tool alive: a failed run is a bug in the driver, not a
        # licence to finish the release by hand.
        self.assertIn("fix the driver", self.runbook.lower())


if __name__ == "__main__":
    unittest.main()
