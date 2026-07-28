"""Shared helpers for the engine unit tests.

Builds manifests against ``tests/fixtures/mini-catalogue`` — a hand-authored,
few-KB catalogue with three groups:

===========================  ===========================================================
``demo/essential/plain``     two built-in members, one required parameter, no remediation
``demo/essential/anchor``    the **#21 shape**: a custom member whose naming anchor is a
                             bubbled initiative-level ``customerAbbreviation`` parameter,
                             with a matching ``<REPLACE: …>`` mock in its assignment
``demo/professional/remed``  a DeployIfNotExists member with ``.roles.json``
===========================  ===========================================================

Why a fixture catalogue rather than the real one (#44): the real naming initiative is
169 members / 111 KB, so covering the anchor path through the golden fixtures would
commit ~330 KB across the three flavour trees and re-churn it on every catalogue
release — and a break would still surface as a global byte-diff with no localization.
The fixture pins no catalogue version (``source`` requires only ``initiatives``), so a
real catalogue release never invalidates these tests.
"""
import copy
import json

import _engine_path  # noqa: F401  (sys.path bootstrap)

from epac_builder.catalogue import Catalogue  # noqa: E402

MINI_CATALOGUE = _engine_path.MINI_CATALOGUE

PLAIN = {"domain": "demo", "category": "plain", "tier": "essential"}
ANCHOR = {"domain": "demo", "category": "anchor", "tier": "essential"}
REMEDIATING = {"domain": "demo", "category": "remediating", "tier": "professional"}

_BASE_MANIFEST = {
    "schemaVersion": 1,
    "customer": "testco",
    "prefix": "tst",
    "pacOwnerId": "11111111-2222-3333-4444-555555555555",
    "source": {"initiatives": "initiatives"},
    "output": {"root": "package", "flavours": ["json"]},
    "environments": [
        {
            "selector": "epac-dev",
            "tenantId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "deploymentRootScope": "/providers/Microsoft.Management/managementGroups/tst-root",
            "managedIdentityLocation": "westeurope",
            "enforcement": "hardened",
            "logAnalyticsWorkspaceId": (
                "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-mon"
                "/providers/Microsoft.OperationalInsights/workspaces/tst-law"
            ),
        }
    ],
    "allowedLocations": ["westeurope"],
    "notScopes": {},
    "selection": [],
    "bindings": {"defaults": {}, "overrides": {}},
    "effectOverrides": [],
    "exemptions": {},
    "metadata": {},
}

# Every required parameter the fixture groups declare, so the default manifest binds cleanly.
DEFAULT_BINDINGS = {
    "demoTagName": "costCenter",
    "customerAbbreviation": "tst",
}


def catalogue():
    """A ``Catalogue`` over the mini fixture."""
    return Catalogue(MINI_CATALOGUE)


def manifest(selection=None, bindings=None, **overrides):
    """A valid manifest over the mini catalogue, with targeted overrides.

    ``bindings`` replaces ``bindings.defaults`` wholesale (pass ``{}`` to prove the
    fail-fast path); omit it to get every parameter the fixture needs.
    """
    m = copy.deepcopy(_BASE_MANIFEST)
    m["selection"] = copy.deepcopy(selection if selection is not None else [PLAIN])
    m["bindings"]["defaults"] = dict(DEFAULT_BINDINGS if bindings is None else bindings)
    for key, value in overrides.items():
        m[key] = value
    return m


def scoped(selection_item, scope="/providers/Microsoft.Management/managementGroups/tst-lz",
           selector="epac-dev"):
    """A copy of a selection item with an explicit per-selector scope (no placeholder)."""
    item = dict(selection_item)
    item["scope"] = {selector: [scope]}
    return item


def build(selection=None, bindings=None, **overrides):
    """Resolve + build the IR in one step. Returns ``(ir, manifest, catalogue)``."""
    from epac_builder.ir import build_ir

    m = manifest(selection=selection, bindings=bindings, **overrides)
    cat = catalogue()
    groups = cat.resolve(m["selection"])
    return build_ir(m, cat, groups), m, cat


def artifacts(selection_item):
    """Load one group's catalogue artifacts (the dict ``bind_parameters`` consumes)."""
    cat = catalogue()
    group = cat.resolve([selection_item])[0]
    return cat.load_artifacts(group)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def assignment_named(ir, name):
    """The IR assignment whose ``assignmentName`` matches, or ``None``."""
    for a in ir["assignments"]:
        if a["assignmentName"] == name:
            return a
    return None
