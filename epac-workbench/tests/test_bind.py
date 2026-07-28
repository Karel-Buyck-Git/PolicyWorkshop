"""Parameter binding, the bubbled naming anchor (#44/#21), and effect posture.

``customerAbbreviation`` is the reason this file exists. #21 promoted it from a value
baked 162x into the naming policyset to an initiative-level parameter bound from the
manifest, and #44 recorded that **nothing in CI exercised that path** — the contoso
golden fixture selects two groups, neither of which declares it. These tests are that
coverage: unbound must fail fast, bound must reach the rendered assignment.
"""
import unittest

import _engine_path  # noqa: F401
import support

from epac_builder.bind import (  # noqa: E402
    BindError, apply_posture, bind_parameters, is_placeholder,
    required_param_keys, resolve_posture,
)


class TestRequiredParams(unittest.TestCase):
    def test_placeholder_detection_ignores_real_values(self):
        self.assertTrue(is_placeholder("<REPLACE: customerAbbreviation>"))
        self.assertTrue(is_placeholder("   <REPLACE: leading-whitespace>"))
        self.assertFalse(is_placeholder("contoso"))
        self.assertFalse(is_placeholder(None))
        self.assertFalse(is_placeholder(42))

    def test_anchor_group_declares_customer_abbreviation(self):
        art = support.artifacts(support.ANCHOR)
        self.assertEqual(required_param_keys(art["assignment"]), ["customerAbbreviation"])


class TestBubbledAnchor(unittest.TestCase):
    """#44: the #21 bubbled-parameter path, end to end."""

    def test_unbound_anchor_fails_fast(self):
        art = support.artifacts(support.ANCHOR)
        with self.assertRaises(BindError) as ctx:
            bind_parameters(art, {"defaults": {}, "overrides": {}})
        msg = str(ctx.exception)
        # The message has to name the key and where to put it, or it is not actionable.
        self.assertIn("customerAbbreviation", msg)
        self.assertIn("bindings.defaults", msg)

    def test_bound_anchor_reaches_the_assignment(self):
        art = support.artifacts(support.ANCHOR)
        bound = bind_parameters(art, {"defaults": {"customerAbbreviation": "ctso"},
                                      "overrides": {}})
        self.assertEqual(bound["customerAbbreviation"], "ctso")

    def test_bound_anchor_reaches_the_rendered_ir(self):
        ir, _m, _c = support.build(selection=[support.ANCHOR])
        assignment = support.assignment_named(ir, "demo-esn-anchor")
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment["boundParameters"]["customerAbbreviation"], "tst")
        # And the policyset still exposes it as an initiative-level parameter, rather
        # than the pre-#21 shape where the value was baked into every member.
        params = ir["initiatives"][0]["policyset"]["properties"]["parameters"]
        self.assertIn("customerAbbreviation", params)

    def test_per_group_override_beats_the_default(self):
        art = support.artifacts(support.ANCHOR)
        bound = bind_parameters(art, {
            "defaults": {"customerAbbreviation": "global"},
            "overrides": {"demo/anchor": {"customerAbbreviation": "specific"}},
        })
        self.assertEqual(bound["customerAbbreviation"], "specific")


class TestTypeChecking(unittest.TestCase):
    def test_wrong_type_is_rejected(self):
        art = support.artifacts(support.ANCHOR)
        with self.assertRaises(BindError) as ctx:
            bind_parameters(art, {"defaults": {"customerAbbreviation": 42}, "overrides": {}})
        self.assertIn("expects String", str(ctx.exception))

    def test_value_outside_allowed_values_is_rejected(self):
        art = support.artifacts(support.PLAIN)
        # effect carries allowedValues; force it through the binder as a non-placeholder.
        art["assignment"]["parameters"]["effect"] = "NotAnEffect"
        with self.assertRaises(BindError) as ctx:
            bind_parameters(art, {"defaults": support.DEFAULT_BINDINGS, "overrides": {}})
        self.assertIn("allowedValues", str(ctx.exception))

    def test_non_placeholder_values_pass_through_untouched(self):
        art = support.artifacts(support.PLAIN)
        art["assignment"]["parameters"]["demoTagName"] = "already-set"
        bound = bind_parameters(art, {"defaults": {}, "overrides": {}})
        self.assertEqual(bound["demoTagName"], "already-set")


class TestPosture(unittest.TestCase):
    def _environments(self, *enforcements):
        return [{"selector": f"env{i}", "enforcement": e}
                for i, e in enumerate(enforcements)]

    def test_selection_override_wins(self):
        posture, warn = resolve_posture({"name": "g"}, {"enforcement": "Audit"},
                                        self._environments("hardened"))
        self.assertEqual(posture, "Audit")
        self.assertIsNone(warn)

    def test_agreeing_environments_need_no_warning(self):
        posture, warn = resolve_posture({"name": "g"}, None,
                                        self._environments("hardened", "hardened"))
        self.assertEqual(posture, "hardened")
        self.assertIsNone(warn)

    def test_disagreeing_environments_pick_the_first_and_warn(self):
        posture, warn = resolve_posture({"name": "g"}, None,
                                        self._environments("Audit", "hardened"))
        self.assertEqual(posture, "Audit")        # deterministic: first environment
        self.assertIsNotNone(warn)
        self.assertIn("disagree", warn)

    def test_audit_posture_softens_only_parameterized_effects(self):
        art = support.artifacts(support.PLAIN)
        policyset = apply_posture(art["policyset"], "Audit", [])
        members = policyset["properties"]["policyDefinitions"]
        self.assertEqual(members[0]["parameters"]["effect"]["value"], "Audit")
        # The second member's effect is a literal, not a parameter reference — it is
        # still an 'effect' key, so posture reaches it too.
        self.assertEqual(members[1]["parameters"]["effect"]["value"], "Audit")

    def test_hardened_posture_leaves_baked_effects_alone(self):
        art = support.artifacts(support.PLAIN)
        policyset = apply_posture(art["policyset"], "hardened", [])
        members = policyset["properties"]["policyDefinitions"]
        self.assertEqual(members[0]["parameters"]["effect"]["value"], "[parameters('effect')]")
        self.assertEqual(members[1]["parameters"]["effect"]["value"], "Deny")

    def test_effect_override_is_applied_last(self):
        art = support.artifacts(support.PLAIN)
        policyset = apply_posture(
            art["policyset"], "Audit",
            [{"policyDefinitionReferenceId": "demo-builtin-two", "effect": "Disabled"}])
        members = policyset["properties"]["policyDefinitions"]
        self.assertEqual(members[0]["parameters"]["effect"]["value"], "Audit")
        self.assertEqual(members[1]["parameters"]["effect"]["value"], "Disabled")


if __name__ == "__main__":
    unittest.main()
