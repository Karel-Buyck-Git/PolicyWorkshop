"""JSON/EPAC renderer output shape.

Two assertions here are not style preferences — they are the defects a real tenant's
``Build-DeploymentPlans`` rejected (#20), found by a consumer and not by us:

* **desiredState** must be present per ``pacEnvironment`` and default to ``ownedOnly``.
  Where the field is absent EPAC 11.x defaults to ``full``, which proposes **deleting**
  a brownfield tenant's pre-existing ALZ/hand-made policy at or below the root scope.
* **definitionEntry.policySetName** — a flat top-level ``policySetDefinitionName`` is
  rejected outright ("each tree branch must define either a definitionEntry or a
  non-empty definitionEntryList").
"""
import tempfile
import unittest
from pathlib import Path

import _engine_path  # noqa: F401
import support

from epac_builder import render_json  # noqa: E402


class RendererCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.pkg = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def render(self, selection=None, **kw):
        ir, _m, _c = support.build(selection=selection, **kw)
        render_json.render(ir, self.pkg)
        return ir

    @property
    def defs(self):
        return self.pkg / "Definitions"


class TestGlobalSettings(RendererCase):
    def test_desired_state_is_emitted_per_environment_and_defaults_safe(self):
        self.render(selection=[support.scoped(support.PLAIN)])
        settings = support.read_json(self.defs / "global-settings.jsonc")
        env = settings["pacEnvironments"][0]
        self.assertIn("desiredState", env)                      # #20 Finding 1
        self.assertEqual(env["desiredState"]["strategy"], "ownedOnly")   # #20 Finding 3
        self.assertIs(env["desiredState"]["keepDfcSecurityAssignments"], False)

    def test_pac_owner_id_and_tenant_reach_global_settings(self):
        ir = self.render(selection=[support.scoped(support.PLAIN)])
        settings = support.read_json(self.defs / "global-settings.jsonc")
        self.assertEqual(settings["pacOwnerId"], ir["identity"]["pacOwnerId"])
        self.assertEqual(settings["pacEnvironments"][0]["deploymentRootScope"],
                         ir["environments"][0]["rootScope"])

    def test_not_scopes_become_global_not_scopes_only_when_set(self):
        self.render(selection=[support.scoped(support.PLAIN)])
        self.assertNotIn("globalNotScopes",
                         support.read_json(self.defs / "global-settings.jsonc")["pacEnvironments"][0])

        m = support.manifest(selection=[support.scoped(support.PLAIN)],
                             notScopes={"epac-dev": ["/providers/Microsoft.Management/managementGroups/sandbox"]})
        from epac_builder.ir import build_ir
        cat = support.catalogue()
        render_json.render(build_ir(m, cat, cat.resolve(m["selection"])), self.pkg)
        env = support.read_json(self.defs / "global-settings.jsonc")["pacEnvironments"][0]
        self.assertEqual(env["globalNotScopes"],
                         ["/providers/Microsoft.Management/managementGroups/sandbox"])


class TestAssignments(RendererCase):
    def test_definition_entry_shape_not_the_flat_key(self):
        self.render(selection=[support.scoped(support.PLAIN)])
        asg = support.read_json(self.defs / "policyAssignments" / "demo-esn-plain.json")
        self.assertEqual(asg["definitionEntry"]["policySetName"], "tst-demo-esn-plain")  # #20(b)
        self.assertNotIn("policySetDefinitionName", asg)

    def test_bound_parameters_are_rendered_verbatim(self):
        self.render(selection=[support.scoped(support.ANCHOR)])
        asg = support.read_json(self.defs / "policyAssignments" / "demo-esn-anchor.json")
        self.assertEqual(asg["parameters"]["customerAbbreviation"], "tst")

    def test_managed_identity_locations_only_for_remediating_groups(self):
        self.render(selection=[support.scoped(support.PLAIN), support.scoped(support.REMEDIATING)])
        plain = support.read_json(self.defs / "policyAssignments" / "demo-esn-plain.json")
        remed = support.read_json(self.defs / "policyAssignments" / "demo-pro-remed.json")
        self.assertNotIn("managedIdentityLocations", plain)
        self.assertEqual(remed["managedIdentityLocations"],
                         {"westeurope": ["/providers/Microsoft.Management/managementGroups/tst-lz"]})

    def test_every_assignment_declares_a_scope_for_each_selector(self):
        # pacSelector coverage: an assignment with no scope for a declared selector is
        # silently SKIPPED by EPAC, and is caught nowhere else (#33 Tier-1).
        ir = self.render(selection=[support.scoped(support.PLAIN)])
        asg = support.read_json(self.defs / "policyAssignments" / "demo-esn-plain.json")
        for env in ir["environments"]:
            self.assertIn(env["selector"], asg["scope"])


class TestDefinitionsTree(RendererCase):
    def test_custom_definition_bodies_are_shipped(self):
        self.render(selection=[support.scoped(support.ANCHOR)])
        body = support.read_json(self.defs / "policyDefinitions" / "demo-anchored-naming.json")
        self.assertEqual(body["properties"]["policyType"], "Custom")

    def test_policyset_is_written_under_its_customer_scoped_name(self):
        self.render(selection=[support.scoped(support.PLAIN)])
        self.assertTrue((self.defs / "policySetDefinitions" / "tst-demo-esn-plain.json").exists())

    def test_no_definitions_dir_entries_for_builtin_only_selections(self):
        self.render(selection=[support.scoped(support.PLAIN)])
        self.assertFalse((self.defs / "policyDefinitions").exists())

    def test_output_is_deterministic(self):
        first = self.render(selection=[support.scoped(support.PLAIN)])
        before = (self.defs / "policySetDefinitions" / "tst-demo-esn-plain.json").read_bytes()
        render_json.render(first, self.pkg)
        after = (self.defs / "policySetDefinitions" / "tst-demo-esn-plain.json").read_bytes()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
