"""Producer phases 4 and 5 — overlays, the finalize gate, and the release guard.

These were the last uncovered producer phases (#38's named remainder). They read fixed
paths, which is exactly why they had no tests: exercising them meant writing to the real
`catalogue/`. `EPAC_WORKBENCH_ROOT` relocates the workbench, so they can now run against a
4-policy scratch tree instead.

The two things most worth pinning here are **states the pipeline must refuse**, not states
it must produce:

* phase 4 refuses to finalize a version label the ledger already released for *different*
  content (#48) — and leaves the stamp `pending`, so a refused build cannot be mistaken for
  a good one;
* phase 5 refuses a catalogue phase 4 never finalized — the `catalogue-not-finalized` gate,
  which is what stops a `pending` stamp reaching a consumer.
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import _engine_path  # noqa: F401
import workbench

APPLY_OVERLAYS = ["engine/definition_gen/apply_overlays.py"]
QUALITY_CONTROL = ["engine/catalogue_builder/quality_control.py"]
VERSION = "0000.00.01"


class WorkbenchCase(unittest.TestCase):
    generators = ()

    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="epac-finalize-")
        self.wb = workbench.build(Path(self._tmp) / "wb", generators=self.generators)

    def tearDown(self):
        shutil.rmtree(self._tmp, ignore_errors=True)

    def phases_1_to_3(self, version=VERSION):
        workbench.run(self.wb, ["engine/catalogue_builder/extract_policies.py"])
        workbench.run(self.wb, ["engine/catalogue_builder/enrich_policies.py"])
        workbench.run(self.wb, ["engine/catalogue_builder/create_initiatives.py",
                                "--version", version])

    def catalogue(self):
        return json.loads((self.wb / "catalogue" / "catalogue.json").read_text(encoding="utf-8"))

    def index(self):
        return json.loads((self.wb / "catalogue" / "index.json").read_text(encoding="utf-8"))


class TestPhase4BuiltInOnly(WorkbenchCase):
    """Every generator disabled — the documented built-in-only mode."""

    def test_it_finalizes_the_stamp_even_with_nothing_to_apply(self):
        self.phases_1_to_3()
        self.assertEqual(self.catalogue()["contentHash"], "sha256:pending")
        workbench.run(self.wb, APPLY_OVERLAYS)
        catalogue = self.catalogue()
        self.assertNotEqual(catalogue["contentHash"], "sha256:pending")
        self.assertTrue(catalogue["contentHash"].startswith("sha256:"))

    def test_it_adds_its_own_provenance_stamps(self):
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS)
        catalogue = self.catalogue()
        self.assertIn("definitionGensHash", catalogue["inputs"])
        self.assertIn("applyOverlays", catalogue["tools"])

    def test_it_registers_no_custom_groups(self):
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS)
        self.assertFalse([g for g in self.index()["groups"] if g.get("custom")])


class TestPhase4Overlays(WorkbenchCase):
    """One real generator enabled — the NewGroup overlay path."""

    generators = ("dlw-az-tagging",)

    def test_a_new_group_is_created_and_registered(self):
        self.phases_1_to_3()
        before = len(self.index()["groups"])
        workbench.run(self.wb, APPLY_OVERLAYS)

        groups = self.index()["groups"]
        self.assertEqual(len(groups), before + 1)
        custom = [g for g in groups if g.get("custom")]
        self.assertEqual(len(custom), 1)
        # Registered AND on disk: index.json is built in memory while contentHash walks the
        # disk, so the two universes disagreeing is the #26 class of bug. (`dir` is relative
        # to the catalogue root, not the workbench root.)
        self.assertTrue((self.wb / "catalogue" / custom[0]["dir"]).is_dir())

    def test_the_custom_definition_body_is_shipped(self):
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS)
        bodies = list((self.wb / "catalogue" / "definitions" / "custom").rglob("*.json"))
        self.assertTrue(bodies, "an enabled generator must emit its definition bodies")

    def test_the_overlay_group_carries_its_assignment_scaffold(self):
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS)
        custom = [g for g in self.index()["groups"] if g.get("custom")][0]
        group_dir = self.wb / "catalogue" / custom["dir"]
        assignment = json.loads(
            (group_dir / f"{custom['name']}.assignment.json").read_text(encoding="utf-8"))
        # #22: the scaffold must use definitionEntry, never the flat key EPAC 11.x rejects.
        self.assertEqual(assignment["definitionEntry"]["policySetName"], custom["name"])
        self.assertNotIn("policySetDefinitionName", assignment)


class TestPhase4VersionGuard(WorkbenchCase):
    """#48: one label can never come to mean two different catalogues."""

    def _release_then_tamper(self):
        """Publish VERSION, then rewrite the ledger so it claims a different hash for it."""
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS)
        workbench.run(self.wb, ["engine/tools/catalogue_changelog.py", "--write"])
        changelog = self.wb / "catalogue" / "CHANGELOG.md"
        text = changelog.read_text(encoding="utf-8")
        real = self.catalogue()["contentHash"]
        changelog.write_text(text.replace(real, "sha256:" + "0" * 64),
                             encoding="utf-8", newline="\n")

    def test_reusing_a_label_for_different_content_is_refused(self):
        self._release_then_tamper()
        self.phases_1_to_3()                     # resets the stamp to pending
        proc = workbench.run(self.wb, APPLY_OVERLAYS, check=False)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("already released", (proc.stdout + proc.stderr).lower())

    def test_a_refused_build_is_left_unfinalized(self):
        # The important half: a refused run must not leave something that looks finalized.
        self._release_then_tamper()
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS, check=False)
        self.assertEqual(self.catalogue()["contentHash"], "sha256:pending")

    def test_allow_version_reuse_overrides_it(self):
        self._release_then_tamper()
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS + ["--allow-version-reuse"])
        self.assertNotEqual(self.catalogue()["contentHash"], "sha256:pending")

    def test_restamping_identical_content_is_not_a_collision(self):
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS)
        workbench.run(self.wb, ["engine/tools/catalogue_changelog.py", "--write"])
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS)   # idempotent re-run: must succeed
        self.assertNotEqual(self.catalogue()["contentHash"], "sha256:pending")


class TestPhase5QualityControl(WorkbenchCase):
    def test_it_refuses_a_catalogue_phase_4_never_finalized(self):
        self.phases_1_to_3()                     # stamp is still 'pending'
        proc = workbench.run(self.wb, QUALITY_CONTROL, check=False)
        self.assertNotEqual(proc.returncode, 0,
                            "QC must reject a pending catalogue — that is the finalize gate")
        report = json.loads(
            (self.wb / "catalogue" / "quality-control.json").read_text(encoding="utf-8"))
        codes = [f["code"] for f in report["findings"] if f["severity"] == "error"]
        self.assertIn("catalogue-not-finalized", codes)

    def test_an_error_finding_is_printed_rather_than_crashing_the_run(self):
        # Regression guard: finding messages name phases with circled digits, which a
        # Windows cp1252 console cannot encode -- printing one used to raise
        # UnicodeEncodeError and bury the finding under a traceback.
        self.phases_1_to_3()
        proc = workbench.run(self.wb, QUALITY_CONTROL, check=False)
        combined = proc.stdout + proc.stderr
        self.assertNotIn("UnicodeEncodeError", combined)
        self.assertIn("catalogue-not-finalized", combined)

    def test_it_regenerates_its_three_artifacts(self):
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS)
        workbench.run(self.wb, QUALITY_CONTROL)
        self.assertTrue((self.wb / "catalogue" / "naming-samples.md").exists())
        self.assertTrue((self.wb / "catalogue" / "quality-control.json").exists())
        self.assertTrue((self.wb / "docs" / "epac-naming-convention.md").exists())

    def test_a_clean_catalogue_produces_no_error_findings(self):
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS)
        workbench.run(self.wb, QUALITY_CONTROL)
        report = json.loads(
            (self.wb / "catalogue" / "quality-control.json").read_text(encoding="utf-8"))
        errors = [f for f in report["findings"] if f["severity"] == "error"]
        self.assertEqual(errors, [], f"unexpected error-level findings: {errors}")

    def test_check_only_reports_without_rewriting(self):
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS)
        workbench.run(self.wb, QUALITY_CONTROL)
        samples = self.wb / "catalogue" / "naming-samples.md"
        samples.write_text("sentinel\n", encoding="utf-8", newline="\n")
        workbench.run(self.wb, QUALITY_CONTROL + ["--check-only"])
        self.assertEqual(samples.read_text(encoding="utf-8"), "sentinel\n")

    def test_output_is_deterministic_apart_from_the_timestamp(self):
        self.phases_1_to_3()
        workbench.run(self.wb, APPLY_OVERLAYS)
        workbench.run(self.wb, QUALITY_CONTROL)
        first = (self.wb / "catalogue" / "naming-samples.md").read_bytes()
        workbench.run(self.wb, QUALITY_CONTROL)
        self.assertEqual((self.wb / "catalogue" / "naming-samples.md").read_bytes(), first)


if __name__ == "__main__":
    unittest.main()
