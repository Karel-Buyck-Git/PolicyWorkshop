"""The ``--strict`` deploy-readiness gate.

Schema validation proves a manifest is well-formed; it cannot prove it is *filled in*.
An unedited ``<REPLACE: …>`` renders verbatim into the package and is rejected only by
Azure at deploy time — by which point the customer is watching. These tests pin both
halves of the gate: residual placeholders anywhere in the manifest, and any assignment
that fell back to the placeholder scope.
"""
import unittest

import _engine_path  # noqa: F401
import support

from epac_builder.strict import StrictGateError, residual_placeholders  # noqa: E402


class TestResidualPlaceholders(unittest.TestCase):
    def test_a_filled_manifest_with_real_scopes_is_clean(self):
        ir, m, _c = support.build(selection=[support.scoped(support.PLAIN)])
        self.assertEqual(residual_placeholders(m, ir), [])

    def test_unmapped_selection_is_caught_via_the_placeholder_scope(self):
        ir, m, _c = support.build(selection=[support.PLAIN])
        problems = residual_placeholders(m, ir)
        self.assertEqual(len(problems), 1)
        self.assertIn("placeholder scope", problems[0])
        self.assertIn("demo/essential/plain", problems[0])

    def test_unfilled_value_is_reported_with_its_path(self):
        ir, m, _c = support.build(selection=[support.scoped(support.PLAIN)])
        m["environments"][0]["managedIdentityLocation"] = "<REPLACE: location>"
        problems = residual_placeholders(m, ir)
        self.assertEqual(len(problems), 1)
        self.assertIn("$.environments[0].managedIdentityLocation", problems[0])

    def test_unfilled_dict_key_is_caught_not_just_values(self):
        ir, m, _c = support.build(selection=[support.scoped(support.PLAIN)])
        m["notScopes"] = {"<REPLACE: pacSelector>": ["/providers/x"]}
        problems = residual_placeholders(m, ir)
        self.assertTrue(any("unfilled key" in p for p in problems))

    def test_nested_binding_placeholder_is_caught(self):
        ir, m, _c = support.build(selection=[support.scoped(support.PLAIN)])
        m["bindings"]["defaults"]["demoTagName"] = "<REPLACE: demoTagName>"
        problems = residual_placeholders(m, ir)
        self.assertTrue(any("bindings.defaults.demoTagName" in p for p in problems))

    def test_every_problem_is_reported_not_just_the_first(self):
        ir, m, _c = support.build(selection=[support.PLAIN])       # placeholder scope
        m["prefix"] = "<REPLACE: prefix-slug>"                     # + an unfilled value
        self.assertEqual(len(residual_placeholders(m, ir)), 2)


class TestGateError(unittest.TestCase):
    def test_message_lists_every_problem_and_says_how_to_proceed(self):
        err = StrictGateError(["problem one", "problem two"])
        msg = str(err)
        self.assertIn("2 placeholder(s)", msg)
        self.assertIn("problem one", msg)
        self.assertIn("problem two", msg)
        self.assertIn("drop --strict", msg)
        self.assertEqual(err.problems, ["problem one", "problem two"])


if __name__ == "__main__":
    unittest.main()
