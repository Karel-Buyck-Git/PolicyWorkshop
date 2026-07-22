"""JSON / EPAC renderer: IR -> an EPAC ``Definitions`` tree at the package root.

Layout written under the package dir (``pkg_dir``):

    Definitions/
      global-settings.jsonc                 (pacEnvironments + pacOwnerId)
      policyDefinitions/<name>.json          (custom member policies referenced by name)
      policySetDefinitions/<name>.json       (customer-prefixed, posture-applied policyset)
      policyAssignments/<name>.json          (bound assignment, real scopes)
      policyExemptions/<selector>/<name>.json

The deploy README + pipeline + provenance are added by the packaging step (package.py).
Effects are already baked per-group in the IR's policyset copy, so assignments carry
no effect ``overrides``. Output is deterministic (stable order, trailing newline).
"""
from pathlib import Path

from epac_builder.writeutil import write_json

SCHEMA = "https://raw.githubusercontent.com/Azure/enterprise-azure-policy-as-code/main/Schemas"


def render(ir, pkg_dir):
    """Write the EPAC Definitions tree at the package root (``pkg_dir``).

    The deploy README + pipeline + provenance are added by the packaging step, so
    this renderer emits only the EPAC ``Definitions/`` content.
    """
    defs = Path(pkg_dir) / "Definitions"
    _write_global_settings(ir, defs / "global-settings.jsonc")

    for defn in ir["definitions"]:
        write_json(defs / "policyDefinitions" / f"{defn['name']}.json", defn)

    for init in ir["initiatives"]:
        write_json(defs / "policySetDefinitions" / f"{init['name']}.json", init["policyset"])

    for asg in ir["assignments"]:
        write_json(defs / "policyAssignments" / f"{asg['assignmentName']}.json", _assignment(ir, asg))

    for ex in ir["exemptions"]:
        write_json(
            defs / "policyExemptions" / ex["selector"] / f"{ex['name']}.json",
            _exemption(ex),
        )

    return Path(pkg_dir)


def _write_global_settings(ir, path):
    envs = []
    for e in ir["environments"]:
        entry = {
            "pacSelector": e["selector"],
            "cloud": "AzureCloud",
            "tenantId": e["tenantId"],
            "deploymentRootScope": e["rootScope"],
        }
        if e.get("managedIdentityLocation"):
            entry["managedIdentityLocation"] = e["managedIdentityLocation"]
        if e.get("notScopes"):
            entry["globalNotScopes"] = e["notScopes"]
        # desiredState is EPAC's reconciliation strategy for this environment. Without it EPAC
        # 11.x defaults to the destructive "full" — proposing to delete any pre-existing policy
        # at/below the root scope. We emit a SAFE default ("ownedOnly": touch only what this
        # package owns) so a brownfield tenant is never at risk; greenfield opts into "full"
        # deliberately via the manifest's environments[].strategy. See ir.py:_env.
        desired = {
            "strategy": e.get("strategy") or "ownedOnly",
            "keepDfcSecurityAssignments": False,
        }
        if e.get("excludedScopes"):
            desired["excludedScopes"] = e["excludedScopes"]
        entry["desiredState"] = desired
        envs.append(entry)
    write_json(path, {
        "$schema": f"{SCHEMA}/global-settings-schema.json",
        "pacOwnerId": ir["identity"]["pacOwnerId"],
        "pacEnvironments": envs,
    })


def _assignment(ir, asg):
    out = {
        "$schema": f"{SCHEMA}/policy-assignment-schema.json",
        "nodeName": asg["nodeName"],
        "assignment": {
            "name": asg["assignmentName"],
            "displayName": asg["displayName"],
            "description": asg["description"],
        },
        # EPAC 11.x rejects a flat top-level policySetDefinitionName ("each tree branch must
        # define either a definitionEntry or a non-empty definitionEntryList"); it wants the
        # policy set named inside definitionEntry. See pkgvalidate.check_references, which reads
        # this shape.
        "definitionEntry": {"policySetName": asg["initiative"]},
        "parameters": asg["boundParameters"],
        "scope": asg["scopes"],
        "notScopes": asg["notScopes"] or [],
    }
    if asg["managedIdentity"]["required"]:
        out["managedIdentityLocations"] = _mi_locations(ir, asg)
    return out


def _mi_locations(ir, asg):
    """EPAC managedIdentityLocations: {location: [scopes]} from each env's location."""
    by_loc = {}
    loc_of = {e["selector"]: e.get("managedIdentityLocation") for e in ir["environments"]}
    for selector, scopes in asg["scopes"].items():
        loc = loc_of.get(selector)
        if loc:
            by_loc.setdefault(loc, [])
            for s in scopes:
                if s not in by_loc[loc]:
                    by_loc[loc].append(s)
    return by_loc


def _exemption(ex):
    out = {
        "name": ex["name"],
        "displayName": ex.get("displayName", ex["name"]),
        "exemptionCategory": ex["category"],
        "scope": ex["scopes"][0] if len(ex["scopes"]) == 1 else ex["scopes"],
    }
    if ex.get("expiresOn"):
        out["expiresOn"] = ex["expiresOn"]
    if ex.get("policyDefinitionReferenceId"):
        out["policyDefinitionReferenceIds"] = [ex["policyDefinitionReferenceId"]]
    return out
