"""IR assembly: scopes, warnings, remediation, and the lineage stamp.

The warning paths matter most here. An unmapped selection must produce a placeholder
scope Azure will reject *loudly* — there is deliberately no fall-back to
``deploymentRootScope``, because silently widening a customer's blast radius to the
tenant root is the worst possible default.
"""
import unittest

import _engine_path  # noqa: F401
import support

from epac_builder.mgscopes import PLACEHOLDER_SCOPE, HierarchyError  # noqa: E402


class TestScopes(unittest.TestCase):
    def test_unmapped_selection_gets_a_placeholder_and_a_warning(self):
        ir, _m, _c = support.build(selection=[support.PLAIN])
        assignment = support.assignment_named(ir, "demo-esn-plain")
        self.assertEqual(assignment["scopes"]["epac-dev"], [PLACEHOLDER_SCOPE])
        self.assertTrue(any("placeholder scope" in w for w in ir["warnings"]))

    def test_placeholder_never_falls_back_to_the_deployment_root(self):
        ir, m, _c = support.build(selection=[support.PLAIN])
        root = m["environments"][0]["deploymentRootScope"]
        self.assertNotIn(root, support.assignment_named(ir, "demo-esn-plain")["scopes"]["epac-dev"])

    def test_explicit_scope_suppresses_the_warning(self):
        ir, _m, _c = support.build(selection=[support.scoped(support.PLAIN)])
        assignment = support.assignment_named(ir, "demo-esn-plain")
        self.assertEqual(assignment["scopes"]["epac-dev"],
                         ["/providers/Microsoft.Management/managementGroups/tst-lz"])
        self.assertEqual(ir["warnings"], [])

    def test_unknown_management_group_name_is_a_hard_error(self):
        from epac_builder.ir import build_ir
        m = support.manifest(selection=[dict(support.PLAIN, managementGroup="mg-does-not-exist")])
        cat = support.catalogue()
        groups = cat.resolve(m["selection"])
        with self.assertRaises(HierarchyError) as ctx:
            build_ir(m, cat, groups, mg_index={"mg-real": "/providers/x/mg-real"})
        self.assertIn("mg-does-not-exist", str(ctx.exception))

    def test_management_group_names_resolve_to_scope_ids(self):
        from epac_builder.ir import build_ir
        m = support.manifest(selection=[dict(support.PLAIN, managementGroup="mg-lz")])
        cat = support.catalogue()
        groups = cat.resolve(m["selection"])
        ir = build_ir(m, cat, groups,
                      mg_index={"mg-lz": "/providers/Microsoft.Management/managementGroups/mg-lz"})
        self.assertEqual(support.assignment_named(ir, "demo-esn-plain")["scopes"]["epac-dev"],
                         ["/providers/Microsoft.Management/managementGroups/mg-lz"])


class TestNaming(unittest.TestCase):
    def test_policyset_is_customer_prefixed_but_assignment_name_is_not(self):
        ir, _m, _c = support.build(selection=[support.scoped(support.PLAIN)])
        assignment = support.assignment_named(ir, "demo-esn-plain")
        self.assertEqual(assignment["initiative"], "tst-demo-esn-plain")
        # The assignment's own name stays brand-neutral: Azure caps it at 24 chars.
        self.assertEqual(assignment["assignmentName"], "demo-esn-plain")
        self.assertLessEqual(len(assignment["assignmentName"]), 24)

    def test_node_name_carries_the_customer_segment(self):
        ir, _m, _c = support.build(selection=[support.scoped(support.PLAIN)])
        self.assertEqual(support.assignment_named(ir, "demo-esn-plain")["nodeName"],
                         "/tst/demo/essential/plain/")


class TestRemediation(unittest.TestCase):
    def test_remediating_group_requires_an_identity_and_emits_role_assignments(self):
        ir, _m, _c = support.build(selection=[support.scoped(support.REMEDIATING)])
        assignment = support.assignment_named(ir, "demo-pro-remed")
        self.assertTrue(assignment["managedIdentity"]["required"])
        self.assertEqual(len(ir["roleAssignments"]), 1)
        self.assertEqual(ir["roleAssignments"][0]["scope"],
                         "/providers/Microsoft.Management/managementGroups/tst-lz")

    def test_non_remediating_group_emits_none(self):
        ir, _m, _c = support.build(selection=[support.scoped(support.PLAIN)])
        self.assertFalse(support.assignment_named(ir, "demo-esn-plain")
                         ["managedIdentity"]["required"])
        self.assertEqual(ir["roleAssignments"], [])

    def test_description_mentions_remediation_only_when_it_applies(self):
        ir, _m, _c = support.build(
            selection=[support.scoped(support.PLAIN), support.scoped(support.REMEDIATING)])
        self.assertNotIn("managed identity",
                         support.assignment_named(ir, "demo-esn-plain")["description"])
        self.assertIn("managed identity",
                      support.assignment_named(ir, "demo-pro-remed")["description"])


class TestDefinitionsAndLineage(unittest.TestCase):
    def test_custom_definitions_referenced_by_name_are_collected(self):
        ir, _m, _c = support.build(selection=[support.scoped(support.ANCHOR)])
        self.assertEqual([d["name"] for d in ir["definitions"]], ["demo-anchored-naming"])

    def test_builtin_only_selection_ships_no_definitions(self):
        ir, _m, _c = support.build(selection=[support.scoped(support.PLAIN)])
        self.assertEqual(ir["definitions"], [])

    def test_missing_custom_definition_is_a_hard_error(self):
        from epac_builder.catalogue import ResolveError
        from epac_builder.ir import build_ir
        m = support.manifest(selection=[support.scoped(support.ANCHOR)])
        cat = support.catalogue()
        groups = cat.resolve(m["selection"])
        cat.load_definition("demo-anchored-naming")      # prime the lazy index
        cat._def_paths = {}                              # simulate a definition gone missing
        with self.assertRaises(ResolveError) as ctx:
            build_ir(m, cat, groups)
        self.assertIn("would not deploy", str(ctx.exception))

    def test_lineage_carries_full_catalogue_provenance(self):
        ir, _m, _c = support.build(selection=[support.scoped(support.PLAIN)])
        lineage = ir["lineage"]
        # #27: a package must be able to answer "which catalogue + which upstream made me?"
        for key in ("manifestHash", "catalogueVersion", "catalogueContentHash",
                    "builtInsRef", "hierarchyHash"):
            self.assertIn(key, lineage)
        self.assertEqual(len(lineage["groups"]), 1)

    def test_manifest_hash_is_stable_and_content_sensitive(self):
        from epac_builder.ir import manifest_hash
        a = support.manifest()
        b = support.manifest()
        self.assertEqual(manifest_hash(a), manifest_hash(b))
        b["prefix"] = "other"
        self.assertNotEqual(manifest_hash(a), manifest_hash(b))


class TestEnvironments(unittest.TestCase):
    def test_desired_state_defaults_to_the_safe_strategy(self):
        # #20 Finding 3: where the field is optional EPAC defaults to destructive 'full',
        # which proposes deleting a brownfield tenant's pre-existing policy.
        ir, _m, _c = support.build(selection=[support.scoped(support.PLAIN)])
        self.assertEqual(ir["environments"][0]["strategy"], "ownedOnly")

    def test_explicit_strategy_is_honoured(self):
        m = support.manifest(selection=[support.scoped(support.PLAIN)])
        m["environments"][0]["strategy"] = "full"
        from epac_builder.ir import build_ir
        cat = support.catalogue()
        ir = build_ir(m, cat, cat.resolve(m["selection"]))
        self.assertEqual(ir["environments"][0]["strategy"], "full")


if __name__ == "__main__":
    unittest.main()
