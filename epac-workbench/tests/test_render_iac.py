"""Terraform and Bicep renderer shape, plus the HCL emitter.

These two flavours have no validator and no PR gate of their own (#33/#34 open), and
CI only ever byte-diffs them — so a break shows up as "some file differs" with no
indication of which renderer or which construct. These tests localize that.

The HCL escaping tests are the sharp edge: a policy displayName containing a quote or
a backslash that reaches ``main.tf`` unescaped produces a config that does not parse,
and nothing upstream of Terraform itself would catch it.
"""
import tempfile
import unittest
from pathlib import Path

import _engine_path  # noqa: F401
import support

from epac_builder import render_bicep, render_terraform  # noqa: E402
from epac_builder.hcl import hcl_str, hcl_value, tf_ident  # noqa: E402


class TestHclEmitter(unittest.TestCase):
    def test_quotes_and_backslashes_are_escaped(self):
        self.assertEqual(hcl_str('say "hi"'), '"say \\"hi\\""')
        self.assertEqual(hcl_str("back\\slash"), '"back\\\\slash"')

    def test_newlines_do_not_break_out_of_the_literal(self):
        self.assertEqual(hcl_str("two\nlines"), '"two\\nlines"')

    def test_scalars_render_as_hcl_not_python(self):
        self.assertEqual(hcl_value(True), "true")
        self.assertEqual(hcl_value(False), "false")
        self.assertEqual(hcl_value(None), "null")
        self.assertEqual(hcl_value(7), "7")

    def test_empty_collections_stay_inline(self):
        self.assertEqual(hcl_value([]), "[]")
        self.assertEqual(hcl_value({}), "{}")

    def test_scalar_lists_stay_on_one_line(self):
        self.assertEqual(hcl_value(["a", "b"]), '["a", "b"]')

    def test_objects_use_quoted_keys_and_preserve_order(self):
        rendered = hcl_value({"zebra": 1, "alpha": 2})
        self.assertIn('"zebra" = 1', rendered)
        self.assertLess(rendered.index("zebra"), rendered.index("alpha"))

    def test_identifiers_are_terraform_safe(self):
        self.assertEqual(tf_ident("tst-demo-esn-plain"), "tst-demo-esn-plain")
        self.assertEqual(tf_ident("has spaces/and.dots"), "has_spaces_and_dots")


class IacCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.pkg = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


class TestTerraform(IacCase):
    def render(self, selection):
        ir, _m, _c = support.build(selection=selection)
        render_terraform.render(ir, self.pkg)
        return ir

    def test_emits_the_expected_file_set(self):
        self.render([support.scoped(support.PLAIN)])
        self.assertTrue((self.pkg / "main.tf").exists())
        self.assertTrue((self.pkg / "variables.tf").exists())
        self.assertTrue((self.pkg / "environments" / "epac-dev.tfvars").exists())

    def test_one_tfvars_per_environment(self):
        m = support.manifest(selection=[support.scoped(support.PLAIN)])
        second = dict(m["environments"][0], selector="epac-prod")
        m["environments"].append(second)
        from epac_builder.ir import build_ir
        cat = support.catalogue()
        render_terraform.render(build_ir(m, cat, cat.resolve(m["selection"])), self.pkg)
        self.assertTrue((self.pkg / "environments" / "epac-dev.tfvars").exists())
        self.assertTrue((self.pkg / "environments" / "epac-prod.tfvars").exists())

    def test_policy_set_and_assignment_reach_main_tf(self):
        self.render([support.scoped(support.PLAIN)])
        main = (self.pkg / "main.tf").read_text(encoding="utf-8")
        self.assertIn("tst-demo-esn-plain", main)
        self.assertIn("jsonencode(", main)

    def test_custom_definition_is_emitted_for_the_anchor_group(self):
        self.render([support.scoped(support.ANCHOR)])
        main = (self.pkg / "main.tf").read_text(encoding="utf-8")
        self.assertIn("demo-anchored-naming", main)
        self.assertIn("tst", main)          # the bound anchor value reaches terraform too

    def test_output_is_deterministic(self):
        ir = self.render([support.scoped(support.PLAIN)])
        before = (self.pkg / "main.tf").read_bytes()
        render_terraform.render(ir, self.pkg)
        self.assertEqual((self.pkg / "main.tf").read_bytes(), before)


class TestBicep(IacCase):
    def render(self, selection):
        ir, _m, _c = support.build(selection=selection)
        render_bicep.render(ir, self.pkg)
        return ir

    def test_emits_the_expected_file_set(self):
        self.render([support.scoped(support.PLAIN)])
        self.assertTrue((self.pkg / "main.bicep").exists())
        self.assertTrue((self.pkg / "main.parameters.epac-dev.json").exists())
        self.assertTrue((self.pkg / "policies" / "tst-demo-esn-plain.policyset.json").exists())

    def test_policyset_json_excludes_members_which_main_bicep_builds_inline(self):
        self.render([support.scoped(support.PLAIN)])
        meta = support.read_json(self.pkg / "policies" / "tst-demo-esn-plain.policyset.json")
        self.assertNotIn("policyDefinitions", meta)
        self.assertIn("displayName", meta)

    def test_bound_parameters_go_to_a_params_file(self):
        self.render([support.scoped(support.ANCHOR)])
        params = support.read_json(self.pkg / "policies" / "tst-demo-esn-anchor.params.json")
        self.assertEqual(params["customerAbbreviation"], {"value": "tst"})

    def test_custom_definition_body_is_shipped(self):
        self.render([support.scoped(support.ANCHOR)])
        self.assertTrue((self.pkg / "policies" / "demo-anchored-naming.definition.json").exists())

    def test_output_is_deterministic(self):
        ir = self.render([support.scoped(support.PLAIN)])
        before = (self.pkg / "main.bicep").read_bytes()
        render_bicep.render(ir, self.pkg)
        self.assertEqual((self.pkg / "main.bicep").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
