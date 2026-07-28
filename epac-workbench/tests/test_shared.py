"""Shared modules: naming limits, tier classification, hierarchy, release ledger.

These are imported by BOTH builders, so a regression here is the widest blast radius
in the repo: `naming` decides every technical name in the catalogue *and* in a
customer's package, and `changelog` is what #48's collision guard reads before a
release is allowed to stamp.
"""
import tempfile
import unittest
from pathlib import Path

import _engine_path  # noqa: F401

from shared import changelog, naming, paths  # noqa: E402
from shared.hierarchy import load_hierarchy  # noqa: E402
from shared.tiers import classify  # noqa: E402


class TestNaming(unittest.TestCase):
    def test_tier_codes(self):
        self.assertEqual(naming.tier_code("essential"), "esn")
        self.assertEqual(naming.tier_code("Professional"), "pro")
        self.assertEqual(naming.tier_code("ENTERPRISE"), "ent")

    def test_unknown_tier_is_rejected(self):
        with self.assertRaises(ValueError):
            naming.tier_code("platinum")

    def test_group_names_fit_the_azure_assignment_limit(self):
        # An assignment name over 24 chars is rejected by Azure at deploy, so the
        # catalogue can never emit one. 24 is the tightest limit in the whole system.
        built = naming.compose_name("management", "essential", "tags")
        self.assertEqual(built, "management-esn-tags")
        self.assertLessEqual(len(built), naming.ASSIGNMENT_NAME_MAX)

    def test_every_catalogue_name_is_within_limits(self):
        import json
        index = json.loads((Path(_engine_path.ROOT) / "catalogue" / "index.json")
                           .read_text(encoding="utf-8"))
        for group in index["groups"]:
            self.assertLessEqual(len(group["name"]), naming.ASSIGNMENT_NAME_MAX,
                                 f"group name too long for Azure: {group['name']}")

    def test_display_and_node_names_are_brand_neutral(self):
        display = naming.display_name("Management", "essential", "Tags")
        self.assertEqual(display, "Management Essential — Tags")
        self.assertLessEqual(len(display), naming.DISPLAY_NAME_MAX)
        self.assertEqual(naming.node_name("Management", "essential", "Tags"),
                         "/management/essential/tags/")

    def test_exemption_name_suffix(self):
        self.assertEqual(naming.exemption_name("management-esn-tags"), "management-esn-tags-ex")

    def test_unknown_category_names_the_file_to_fix(self):
        with self.assertRaises(KeyError) as ctx:
            naming.category_abbr("No Such Category At All")
        self.assertIn("azure-category-abbreviation", str(ctx.exception))


class TestTiers(unittest.TestCase):
    """Tier assignment comes from the authored keyword rules, not from code.

    Asserting the *documented* placements from the runbook's tier definitions, so a
    rule edit that silently re-tiers a whole class of policies fails here rather than
    surfacing as an unexplained catalogue diff.
    """

    def test_classification_returns_a_known_tier(self):
        tier = classify("Storage accounts should restrict network access", "", "Storage")
        self.assertIn(tier, ("Essential", "Professional", "Enterprise"))

    def test_customer_managed_keys_are_enterprise(self):
        # CMK implies ongoing key operations -> Enterprise, per the tier definitions.
        self.assertEqual(
            classify("Storage accounts should use customer-managed key for encryption",
                     "", "Storage"),
            "Enterprise")

    def test_defender_and_threat_protection_are_professional(self):
        self.assertEqual(
            classify("Microsoft Defender for Storage should be enabled", "", "Security"),
            "Professional")

    def test_private_connectivity_is_professional(self):
        self.assertEqual(
            classify("Storage accounts should use private link", "", "Storage"),
            "Professional")

    def test_the_default_is_the_least_restrictive_tier(self):
        # A policy matching no rule must land in Essential -- the safe default, since
        # Essential is included by every tier and so can never silently drop coverage.
        self.assertEqual(classify("zzz nothing matches this at all", "", "General"), "Essential")

    def test_classification_is_deterministic(self):
        args = ("Storage accounts should restrict network access", "", "Storage")
        self.assertEqual(classify(*args), classify(*args))


class TestHierarchy(unittest.TestCase):
    def test_authored_hierarchy_maps_domains_to_their_categories(self):
        mapping = load_hierarchy(paths.HIERARCHY_FILE)
        self.assertTrue(mapping)
        self.assertIn("Tags", mapping["Management"])

    def test_every_category_belongs_to_exactly_one_domain(self):
        # A category in two domains would make the catalogue's (domain, tier, category)
        # grouping ambiguous, and policies could land in two groups.
        seen = {}
        for domain, categories in load_hierarchy(paths.HIERARCHY_FILE).items():
            for category in categories:
                self.assertNotIn(category, seen,
                                 f"category {category!r} is in both {seen.get(category)!r} "
                                 f"and {domain!r}")
                seen[category] = domain


class TestReleaseLedger(unittest.TestCase):
    """#48: one version label can never mean two different catalogues."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "CHANGELOG.md"

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, body):
        self.path.write_text(body, encoding="utf-8", newline="\n")

    def test_missing_changelog_is_the_first_release_not_an_error(self):
        self.assertEqual(changelog.released_versions(self.path), {})
        self.assertIsNone(changelog.version_collision("2026.07.26", "sha256:abc", self.path))

    def test_released_versions_reads_label_and_hash(self):
        self._write("# Changelog\n\n## 2026.07.26\n\nCatalogue contentHash `sha256:aaa`.\n")
        self.assertEqual(changelog.released_versions(self.path), {"2026.07.26": "sha256:aaa"})

    def test_reusing_a_label_for_different_content_is_a_collision(self):
        self._write("# Changelog\n\n## 2026.07.26\n\nCatalogue contentHash `sha256:aaa`.\n")
        message = changelog.version_collision("2026.07.26", "sha256:bbb", self.path)
        self.assertIsNotNone(message)
        self.assertIn("would mean two different catalogues", message)
        self.assertIn("--version 2026.07.26.1", message)      # names the next free label

    def test_restamping_identical_content_is_not_a_collision(self):
        self._write("# Changelog\n\n## 2026.07.26\n\nCatalogue contentHash `sha256:aaa`.\n")
        self.assertIsNone(changelog.version_collision("2026.07.26", "sha256:aaa", self.path))

    def test_an_unrecorded_label_cannot_collide(self):
        # The blind spot #51 exists to close: a release that is never written to the
        # ledger is invisible here, so its label stays silently reusable.
        self._write("# Changelog\n\n## 2026.07.26\n\nCatalogue contentHash `sha256:aaa`.\n")
        self.assertIsNone(changelog.version_collision("2026.07.27", "sha256:bbb", self.path))

    def test_next_free_label_counts_up_rather_than_incrementing_a_date(self):
        # Incrementing the last component of 2026.07.25 would propose *tomorrow*.
        self.assertEqual(changelog.next_free_label("2026.07.25", {}), "2026.07.25.1")
        self.assertEqual(
            changelog.next_free_label("2026.07.25", {"2026.07.25.1": "x", "2026.07.25.2": "y"}),
            "2026.07.25.3")

    def test_entry_without_a_readable_hash_still_reports_reuse(self):
        self._write("# Changelog\n\n## 2026.07.26\n\nNo hash recorded here.\n")
        message = changelog.version_collision("2026.07.26", "sha256:bbb", self.path)
        self.assertIn("does not record", message)


if __name__ == "__main__":
    unittest.main()
