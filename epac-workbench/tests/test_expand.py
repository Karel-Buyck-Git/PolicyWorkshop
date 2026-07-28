"""``input.json`` -> manifest expansion, against the REAL catalogue and schemas.

Unlike the rest of the suite this module deliberately uses the shipped catalogue:
``expand()`` loads ``customer/manifests/input.schema.json`` relative to the catalogue
directory, and the point of these tests is partly that the *shipped schemas* still
accept what the *shipped code* generates. That pairing is what broke in #42 — the
onboarding path emitted a key ``manifest.schema.json`` rejects, and nothing noticed.

The selection is read out of ``index.json`` at runtime rather than hardcoded, so a
catalogue release cannot invalidate these tests.
"""
import json
import unittest
from pathlib import Path

import _engine_path  # noqa: F401

from epac_builder import validate  # noqa: E402
from epac_builder.catalogue import Catalogue  # noqa: E402
from epac_builder.expand import expand, parse_selection  # noqa: E402

ROOT = Path(_engine_path.ROOT)
CATALOGUE = ROOT / "catalogue"
MANIFESTS = ROOT / "customer" / "manifests"


def _a_real_selection(catalogue, count=1):
    """`<domain>/<tier>/<category>` strings for the first consumable groups."""
    out = []
    for (dom, tier, cat) in sorted(catalogue.by_triple):
        if dom == "undefined":
            continue
        out.append(f"{dom}/{tier}/{cat}")
        if len(out) == count:
            break
    return out


class ExpandCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = Catalogue(CATALOGUE)
        cls.selection = _a_real_selection(cls.catalogue, 2)

    def expand(self, **overrides):
        data = {"customer": "testco", "selection": list(self.selection), "parameters": {}}
        data.update(overrides)
        return expand(data, self.catalogue)


class TestSelectionParsing(unittest.TestCase):
    def test_selection_strings_split_domain_tier_category(self):
        self.assertEqual(parse_selection(["management/essential/tags"]),
                         [{"domain": "management", "category": "tags", "tier": "essential"}])


class TestExpandedShape(ExpandCase):
    def test_result_validates_against_the_shipped_structure_schema(self):
        schema = json.loads((MANIFESTS / "manifest.input.schema.json").read_text(encoding="utf-8"))
        validate.validate(self.expand(), schema, "expanded manifest")   # raises on failure

    def test_catalogue_is_pinned_precisely_not_just_by_label(self):
        # #48: the version label is a UTC date two same-day releases share; the
        # contentHash is the pin that can tell them apart, and it must be the DEFAULT.
        source = self.expand()["source"]
        self.assertEqual(source["catalogueVersion"], self.catalogue.version)
        self.assertTrue(source["catalogueContentHash"].startswith("sha256:"))

    def test_retired_hierarchy_version_is_not_emitted(self):
        # 27c retired it; #42 was the onboarding path still asking for it, which
        # manifest.schema.json (additionalProperties: false) then rejected.
        self.assertNotIn("hierarchyVersion", self.expand()["source"])

    def test_unknown_values_are_seeded_as_replace_placeholders(self):
        manifest = self.expand()
        self.assertTrue(manifest["prefix"].startswith("<REPLACE:"))
        self.assertTrue(manifest["environments"][0]["tenantId"].startswith("<REPLACE:"))

    def test_required_parameters_become_bindable_placeholders(self):
        manifest = self.expand()
        for key, value in manifest["bindings"]["defaults"].items():
            self.assertEqual(value, f"<REPLACE: {key}>",
                             f"binding '{key}' should be seeded as its own placeholder")

    def test_supplied_parameters_are_used_instead_of_placeholders(self):
        manifest = self.expand()
        keys = list(manifest["bindings"]["defaults"])
        if not keys:
            self.skipTest("the sampled groups declare no required parameters")
        supplied = {keys[0]: "already-known"}
        self.assertEqual(self.expand(parameters=supplied)["bindings"]["defaults"][keys[0]],
                         "already-known")

    def test_selection_round_trips(self):
        manifest = self.expand()
        self.assertEqual(len(manifest["selection"]), len(self.selection))

    def test_bad_input_is_rejected_by_the_input_schema(self):
        with self.assertRaises(validate.ValidationError) as ctx:
            expand({"customer": "testco", "parameters": {}}, self.catalogue)   # no selection
        self.assertIn("selection", str(ctx.exception))


class TestStrictGateOnAFreshManifest(ExpandCase):
    def test_a_freshly_expanded_manifest_is_not_deploy_ready(self):
        # The whole point of the expansion is that a human still has to fill it in;
        # --strict must refuse it until they have.
        from epac_builder.strict import residual_placeholders
        problems = residual_placeholders(self.expand(), {"assignments": []})
        self.assertTrue(problems)


if __name__ == "__main__":
    unittest.main()
