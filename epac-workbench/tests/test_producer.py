"""Producer phases 1-3, end to end against a tiny fixture source tree (#38 remainder).

The producer was the last thing in the repo with **no** automated coverage: CI exercises
only the consumer, so a producer regression stays green until someone regenerates the
catalogue — which is exactly how the 2026-07-23 stale-`createInitiatives` drift (#26)
survived a day, and why #43 and #8 exist.

**Hermetic on purpose.** The fixture ships its own 4-policy source tree *and* its own
hierarchy, so an edit to the authored taxonomy (`config/azure-domain-hierachy.md`) cannot
break these tests, and a failure here cannot be mistaken for a taxonomy change. The one
authored input still in play is `config/azure-category-abbreviation.md`, because
`shared/naming.py` reads it from a fixed path — see `test_shared.py` for its own coverage,
and backlog #55 for the trap that dependency creates.

The fixture's four policies are each chosen to exercise one path:

===================  ====================================================================
Tags                 required (no-default) parameter -> bubbles to an initiative parameter
Storage (CMK)        customer-managed key -> the authored rules must tier it Enterprise
Security Center      DeployIfNotExists + roleDefinitionIds -> remediating, gets .roles.json
Monitoring           category absent from the fixture hierarchy -> the `undefined` bucket
===================  ====================================================================

These are slower than the rest of the suite (~2s: they shell out to the three phase
scripts and write to a temp tree). They never touch the real `catalogue/`.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import _engine_path  # noqa: F401

ROOT = Path(_engine_path.ROOT)
FIXTURE = Path(_engine_path.FIXTURES) / "producer"
SOURCE = FIXTURE / "policy-source"
HIERARCHY = FIXTURE / "hierarchy.md"

EXTRACT = ROOT / "engine" / "catalogue_builder" / "extract_policies.py"
ENRICH = ROOT / "engine" / "catalogue_builder" / "enrich_policies.py"
CREATE = ROOT / "engine" / "catalogue_builder" / "create_initiatives.py"


def run(script, *args):
    """Run a producer phase, failing the test with its output if it exits non-zero."""
    proc = subprocess.run([sys.executable, str(script), *args],
                          cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise AssertionError(
            f"{Path(script).name} exited {proc.returncode}\n"
            f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}")
    return proc.stdout


class ProducerRun(unittest.TestCase):
    """Runs phases 1-3 once for the whole class; the phases are sequential by nature."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.mkdtemp(prefix="epac-producer-test-")
        cls.work = Path(cls._tmp)
        cls.defs = cls.work / "definitions"
        cls.initiatives = cls.work / "initiatives"
        cls.defs.mkdir(parents=True)

        cls.extract_out = run(EXTRACT, "--source", str(SOURCE), "--out", str(cls.defs),
                              "--hierarchy", str(HIERARCHY))
        cls.enrich_out = run(ENRICH, "--out", str(cls.defs), "--hierarchy", str(HIERARCHY))
        cls.create_out = run(CREATE, "--output", str(cls.defs),
                             "--initiatives", str(cls.initiatives),
                             "--source", str(SOURCE), "--version", "0000.00.00-test")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._tmp, ignore_errors=True)

    def table_rows(self, category_slug):
        """The data rows of a category's generated markdown table."""
        text = (self.defs / category_slug / "policies.md").read_text(encoding="utf-8")
        return [ln for ln in text.splitlines()
                if ln.startswith("| ") and not ln.startswith("| #")
                and set(ln) - set("|-: ")]

    def group(self, rel):
        return self.initiatives / rel


class TestPhase1Extract(ProducerRun):
    def test_one_markdown_file_per_category(self):
        for slug in ("tags", "storage", "security-center", "monitoring"):
            self.assertTrue((self.defs / slug / "policies.md").exists(), slug)

    def test_every_source_policy_appears_exactly_once(self):
        total = sum(len(self.table_rows(s))
                    for s in ("tags", "storage", "security-center", "monitoring"))
        self.assertEqual(total, len(list(SOURCE.rglob("*.json"))))

    def test_domain_comes_from_the_hierarchy(self):
        self.assertIn("| Demoland |", self.table_rows("tags")[0])
        self.assertIn("| Otherland |", self.table_rows("security-center")[0])

    def test_unmapped_category_falls_into_undefined(self):
        # Not an error: the catch-bucket is deliberate, and the consumer refuses to
        # assemble from it (catalogue.resolve raises on the undefined domain).
        self.assertIn("| undefined |", self.table_rows("monitoring")[0])

    def test_hardened_value_is_the_most_restrictive_allowed_effect(self):
        self.assertIn("| Deny |", self.table_rows("tags")[0])          # Audit/Deny/Disabled
        # Audit/Disabled only -> hardened can be no stronger than Audit.
        row = self.table_rows("monitoring")[0]
        self.assertNotIn("| Deny |", row)

    def test_required_parameters_are_flagged(self):
        # tagName has no default -> must be supplied at assignment.
        self.assertIn("| Yes |", self.table_rows("tags")[0])

    def test_managed_identity_is_flagged_for_remediating_policies(self):
        self.assertIn("| Yes |", self.table_rows("security-center")[0])


class TestPhase2Enrich(ProducerRun):
    def test_rationale_section_is_added_per_tier(self):
        text = (self.defs / "tags" / "policies.md").read_text(encoding="utf-8")
        self.assertIn("## Tier rationale", text)
        for tier in ("**Essential**", "**Professional**", "**Enterprise**"):
            self.assertIn(tier, text)

    def test_rationale_cites_a_compliance_framework(self):
        text = (self.defs / "tags" / "policies.md").read_text(encoding="utf-8")
        self.assertTrue(any(f in text for f in ("ISO 27001", "CIS", "NIS2", "NIST")))

    def test_customer_managed_keys_are_tiered_enterprise(self):
        self.assertIn("| Enterprise |", self.table_rows("storage")[0])

    def test_defender_is_tiered_professional(self):
        self.assertIn("| Professional |", self.table_rows("security-center")[0])

    def test_enrich_is_idempotent(self):
        before = (self.defs / "tags" / "policies.md").read_text(encoding="utf-8")
        run(ENRICH, "--out", str(self.defs), "--hierarchy", str(HIERARCHY))
        self.assertEqual((self.defs / "tags" / "policies.md").read_text(encoding="utf-8"),
                         before)


class TestPhase3Initiatives(ProducerRun):
    def test_one_group_per_domain_tier_category(self):
        self.assertTrue(self.group("demoland/essential/tags").is_dir())
        self.assertTrue(self.group("demoland/enterprise/storage").is_dir())
        self.assertTrue(self.group("otherland/professional/security-center").is_dir())
        self.assertTrue(self.group("undefined/essential/monitoring").is_dir())

    def test_group_names_follow_the_naming_contract(self):
        self.assertTrue((self.group("demoland/essential/tags")
                         / "demoland-esn-tags.policyset.json").exists())
        self.assertTrue((self.group("otherland/professional/security-center")
                         / "otherland-pro-asc.policyset.json").exists())

    def test_roles_json_only_for_remediating_groups(self):
        self.assertTrue((self.group("otherland/professional/security-center")
                         / "otherland-pro-asc.roles.json").exists())
        self.assertFalse((self.group("demoland/essential/tags")
                          / "demoland-esn-tags.roles.json").exists())

    def test_only_no_default_parameters_bubble_to_the_initiative(self):
        pset = json.loads((self.group("demoland/essential/tags")
                           / "demoland-esn-tags.policyset.json").read_text(encoding="utf-8"))
        params = pset["properties"]["parameters"]
        # tagName has no repo default -> it must be supplied at assignment, so it is
        # promoted to an initiative parameter under a readable camelCase name.
        self.assertEqual(sorted(params), ["requireTagResourcesTagName"])
        # effect has a default and is NOT bubbled for a built-in group: it is baked per
        # member as the hardened literal. (Only the definition_gen NewGroup path bubbles
        # effect -- see BUBBLED_TO_INITIATIVE in scaffold.py, covered by test_bind.)
        self.assertNotIn("effect", params)

    def test_member_effect_is_baked_as_the_hardened_literal(self):
        pset = json.loads((self.group("demoland/essential/tags")
                           / "demoland-esn-tags.policyset.json").read_text(encoding="utf-8"))
        member = pset["properties"]["policyDefinitions"][0]
        self.assertEqual(member["parameters"]["effect"]["value"], "Deny")
        # ...and the bubbled parameter is wired through to the member by reference.
        self.assertEqual(member["parameters"]["tagName"]["value"],
                         "[parameters('requireTagResourcesTagName')]")

    def test_assignment_uses_definition_entry_not_the_flat_key(self):
        # #22: EPAC 11.x rejects a top-level policySetDefinitionName outright.
        asg = json.loads((self.group("demoland/essential/tags")
                          / "demoland-esn-tags.assignment.json").read_text(encoding="utf-8"))
        self.assertEqual(asg["definitionEntry"]["policySetName"], "demoland-esn-tags")
        self.assertNotIn("policySetDefinitionName", asg)

    def test_assignment_scaffold_carries_replace_mocks_for_required_params(self):
        asg = json.loads((self.group("demoland/essential/tags")
                          / "demoland-esn-tags.assignment.json").read_text(encoding="utf-8"))
        self.assertTrue(any(str(v).startswith("<REPLACE:")
                            for v in (asg.get("parameters") or {}).values()))

    def test_managed_identity_locations_only_when_remediating(self):
        remed = json.loads((self.group("otherland/professional/security-center")
                            / "otherland-pro-asc.assignment.json").read_text(encoding="utf-8"))
        plain = json.loads((self.group("demoland/essential/tags")
                            / "demoland-esn-tags.assignment.json").read_text(encoding="utf-8"))
        self.assertIn("managedIdentityLocations", remed)
        self.assertNotIn("managedIdentityLocations", plain)

    def test_index_and_catalogue_stamps_are_written(self):
        index = json.loads((self.work / "index.json").read_text(encoding="utf-8"))
        catalogue = json.loads((self.work / "catalogue.json").read_text(encoding="utf-8"))
        self.assertEqual(index["catalogueVersion"], "0000.00.00-test")
        self.assertEqual(catalogue["catalogueVersion"], "0000.00.00-test")
        self.assertEqual(len(index["groups"]), 4)

    def test_content_hash_is_pending_until_phase_4_finalizes_it(self):
        catalogue = json.loads((self.work / "catalogue.json").read_text(encoding="utf-8"))
        self.assertEqual(catalogue["contentHash"], "sha256:pending")

    def test_every_group_in_the_index_exists_on_disk(self):
        # The reverse check #26 found missing: index.json is built from memory while
        # contentHash walks the disk, so the two universes can silently diverge.
        index = json.loads((self.work / "index.json").read_text(encoding="utf-8"))
        for group in index["groups"]:
            self.assertTrue((self.work / group["dir"]).is_dir(), group["dir"])

    def test_phase_3_self_cleans_a_stale_group(self):
        # #26: a (domain, tier, category) that moves or disappears must not leave an
        # orphan behind -- it is invisible to index.json but poisons contentHash.
        orphan = self.initiatives / "goneland" / "essential" / "ghost"
        orphan.mkdir(parents=True, exist_ok=True)
        (orphan / "goneland-esn-ghost.md").write_text("stale\n", encoding="utf-8", newline="\n")
        run(CREATE, "--output", str(self.defs), "--initiatives", str(self.initiatives),
            "--source", str(SOURCE), "--version", "0000.00.00-test")
        self.assertFalse(orphan.exists(), "phase 3 left an orphaned group directory behind")
        self.assertTrue(self.group("demoland/essential/tags").is_dir(),
                        "the self-clean must rebuild the real groups, not just delete")


class TestDeterminism(ProducerRun):
    def test_rerunning_the_pipeline_reproduces_the_same_bytes(self):
        # The producer's whole provenance story (#27) rests on this: same inputs, same
        # output, so a moved contentHash means a real change and not a rebuild.
        second = Path(tempfile.mkdtemp(prefix="epac-producer-test2-"))
        try:
            defs2 = second / "definitions"
            defs2.mkdir(parents=True)
            run(EXTRACT, "--source", str(SOURCE), "--out", str(defs2),
                "--hierarchy", str(HIERARCHY))
            run(ENRICH, "--out", str(defs2), "--hierarchy", str(HIERARCHY))
            run(CREATE, "--output", str(defs2), "--initiatives", str(second / "initiatives"),
                "--source", str(SOURCE), "--version", "0000.00.00-test")

            for rel in ("demoland/essential/tags/demoland-esn-tags.policyset.json",
                        "otherland/professional/security-center/otherland-pro-asc.roles.json"):
                self.assertEqual((second / "initiatives" / rel).read_bytes(),
                                 (self.initiatives / rel).read_bytes(), rel)
            self.assertEqual((defs2 / "tags" / "policies.md").read_bytes(),
                             (self.defs / "tags" / "policies.md").read_bytes())
        finally:
            shutil.rmtree(second, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
