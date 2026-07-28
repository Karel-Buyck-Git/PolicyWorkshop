"""Selection resolution: tier roll-up, ``*`` expansion, and the fail-fast messages.

Every error path here is one a consumer hits while authoring a manifest, so the
assertions are about the *message* as much as the exception — a resolve failure that
does not name the available alternatives sends the author back to the catalogue tree.
"""
import unittest

import _engine_path  # noqa: F401
import support

from epac_builder.catalogue import ResolveError, tier_rollup  # noqa: E402


class TestTierRollup(unittest.TestCase):
    def test_tiers_are_cumulative(self):
        self.assertEqual(tier_rollup("essential"), ["essential"])
        self.assertEqual(tier_rollup("professional"), ["essential", "professional"])
        self.assertEqual(tier_rollup("enterprise"),
                         ["essential", "professional", "enterprise"])


class TestResolve(unittest.TestCase):
    def setUp(self):
        self.cat = support.catalogue()

    def test_exact_selection_picks_one_group(self):
        groups = self.cat.resolve([support.PLAIN])
        self.assertEqual([g["name"] for g in groups], ["demo-esn-plain"])

    def test_professional_rolls_up_essential(self):
        groups = self.cat.resolve([{"domain": "demo", "category": "*", "tier": "professional"}])
        names = sorted(g["name"] for g in groups)
        self.assertEqual(names, ["demo-esn-anchor", "demo-esn-plain", "demo-pro-remed"])

    def test_star_at_essential_excludes_higher_tiers(self):
        groups = self.cat.resolve([{"domain": "demo", "category": "*", "tier": "essential"}])
        names = sorted(g["name"] for g in groups)
        self.assertEqual(names, ["demo-esn-anchor", "demo-esn-plain"])

    def test_duplicate_selections_dedupe(self):
        groups = self.cat.resolve([support.PLAIN, support.PLAIN])
        self.assertEqual(len(groups), 1)

    def test_unknown_domain_lists_the_available_ones(self):
        with self.assertRaises(ResolveError) as ctx:
            self.cat.resolve([{"domain": "nope", "category": "plain", "tier": "essential"}])
        self.assertIn("Available domains", str(ctx.exception))

    def test_unknown_category_lists_the_available_ones(self):
        with self.assertRaises(ResolveError) as ctx:
            self.cat.resolve([{"domain": "demo", "category": "nope", "tier": "essential"}])
        msg = str(ctx.exception)
        self.assertIn("categories available", msg)
        self.assertIn("plain", msg)

    def test_undefined_domain_is_never_consumable(self):
        with self.assertRaises(ResolveError) as ctx:
            self.cat.resolve([{"domain": "undefined", "category": "x", "tier": "essential"}])
        self.assertIn("must be given a real domain", str(ctx.exception))

    def test_missing_index_is_a_clear_error(self):
        from epac_builder.catalogue import Catalogue
        with self.assertRaises(ResolveError) as ctx:
            Catalogue(_engine_path.FIXTURES)      # a real dir, but no index.json in it
        self.assertIn("catalogue index not found", str(ctx.exception))


class TestArtifacts(unittest.TestCase):
    def setUp(self):
        self.cat = support.catalogue()

    def test_roles_are_optional_but_policyset_is_not(self):
        plain = self.cat.resolve([support.PLAIN])[0]
        remed = self.cat.resolve([support.REMEDIATING])[0]
        self.assertIsNone(self.cat.load_artifacts(plain)["roles"])
        self.assertIsNotNone(self.cat.load_artifacts(remed)["roles"])

    def test_custom_definition_bodies_load_by_name(self):
        body = self.cat.load_definition("demo-anchored-naming")
        self.assertIsNotNone(body)
        self.assertEqual(body["name"], "demo-anchored-naming")
        self.assertIsNone(self.cat.load_definition("no-such-definition"))

    def test_provenance_reads_catalogue_json(self):
        prov = self.cat.provenance()
        self.assertTrue(prov["catalogueContentHash"].startswith("sha256:"))
        self.assertTrue(prov["builtInsRef"].startswith("git:"))


if __name__ == "__main__":
    unittest.main()
