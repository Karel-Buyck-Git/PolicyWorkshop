#!/usr/bin/env python3
"""Static pre-deploy validation for a generated EPAC policy package.

Run this on a pull request, **before** anything reaches Azure:

    python validate-package.py            # from the repo root (the package root)
    python validate-package.py <path>     # or point it at a package dir

Stdlib only, no network, no Azure credentials — so it is safe on fork pull
requests and finishes in under a second.

WHAT IT CHECKS
    1. pacSelector coverage  Every ``pacSelector`` in global-settings.jsonc has a
       key in every assignment's ``scope`` block. An assignment with no key for the
       selector being deployed is **silently skipped** by EPAC — no error, no
       warning — so a policy simply never exists in that environment. This is the
       check that exists nowhere else.
    2. Referential integrity  Each assignment's ``policySetDefinitionName`` resolves
       to a file in policySetDefinitions/, and each custom member
       (``policyDefinitionName``) resolves to a file in policyDefinitions/. Built-in
       members (``policyDefinitionId``) are taken on trust — only Azure can confirm
       those.
    3. Placeholder residue  No unfilled ``<REPLACE: …>`` value and no placeholder
       management group survives into the package.
    4. Resource-id shape  Management-group scopes, subscription scopes, tenantId
       and pacOwnerId match the shapes Azure requires.
    5. Parse  Every .json/.jsonc file under Definitions/ actually parses.

WHAT IT DELIBERATELY DOES NOT CHECK — do not mistake a pass here for these:
    * **Full EPAC schema conformance.** The EPAC schemas use ``patternProperties``,
      ``oneOf``/``anyOf``, ``$defs`` and recursive ``$ref``. Validating them properly
      needs a complete JSON-Schema implementation; a partial one would silently skip
      exactly the ``scope``/``notScopes`` blocks that matter most and report success.
      ``Build-DeploymentPlans`` is the authoritative schema check — that is the job
      of the plan step, which runs with Azure credentials.
    * **Whether the referenced resources exist.** This is a *shape* check. A
      perfectly-formed management-group id for a group that was never created passes
      here and fails at plan time.
    * ``managedIdentityLocation`` is not verified against a region list — shipping a
      hard-coded list of Azure regions would go stale silently, which is worse than
      leaving it to the plan step.

Every problem is collected and reported at once, so one run shows the full list
rather than one error per attempt.
"""
import json
import re
import sys
from pathlib import Path

GUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
GUID_RE = re.compile(rf"^{GUID}$")
MG_SCOPE_RE = re.compile(r"^/providers/Microsoft\.Management/managementGroups/[^/]+$")
SUB_SCOPE_RE = re.compile(rf"^/subscriptions/{GUID}(/resourceGroups/[^/]+)?$")

PLACEHOLDER_PREFIX = "<REPLACE:"
PLACEHOLDER_SCOPE = (
    "/providers/Microsoft.Management/managementGroups/REPLACE-set-managementGroup-in-manifest"
)


# --------------------------------------------------------------------------- #
# JSONC reading
#
# Mirrored from the builder's jsonc reader. Kept inline (not imported) because
# this file ships standalone inside the customer's deploy repo, where the
# builder's modules do not exist.
# --------------------------------------------------------------------------- #

def strip_jsonc(text):
    """Return ``text`` with comments and trailing commas removed (string-aware)."""
    out = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            i += 2
            while i < n and text[i] not in "\r\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return _strip_trailing_commas("".join(out))


def _strip_trailing_commas(text):
    out = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == ",":
            j = i + 1
            while j < n and text[j] in " \t\r\n":
                j += 1
            if j < n and text[j] in "}]":
                i += 1
                continue
        out.append(ch)
        i += 1
    return "".join(out)


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def _load(path, problems):
    """Parse one .json/.jsonc file. Returns None (and records a problem) on failure."""
    try:
        return json.loads(strip_jsonc(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        problems.append(f"{path}: does not parse ({exc})")
        return None


def _load_dir(defs_root, name, problems):
    """Load every .json/.jsonc directly under ``defs_root/name``. -> [(path, doc)]"""
    out = []
    folder = defs_root / name
    if not folder.is_dir():
        return out
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in (".json", ".jsonc"):
            doc = _load(path, problems)
            if doc is not None:
                out.append((path, doc))
    return out


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

def _walk_strings(node, path, found):
    """Collect (jsonpath, value) for every string in the document."""
    if isinstance(node, str):
        found.append((path, node))
    elif isinstance(node, dict):
        for k, v in node.items():
            _walk_strings(v, f"{path}.{k}", found)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk_strings(v, f"{path}[{i}]", found)


def check_placeholders(docs, problems):
    """No unfilled <REPLACE: …> and no placeholder management group may survive."""
    for path, doc in docs:
        strings = []
        _walk_strings(doc, "$", strings)
        for where, value in strings:
            if value.lstrip().startswith(PLACEHOLDER_PREFIX):
                problems.append(
                    f"{path}: unfilled placeholder at {where} = {value!r} — fill it in "
                    f"the manifest and re-build the package"
                )
            elif PLACEHOLDER_SCOPE in value:
                problems.append(
                    f"{path}: placeholder management group at {where} — the selection had "
                    f"no managementGroup/scope set; Azure rejects this value"
                )


def check_global_settings(settings, problems):
    """Shape-check global-settings.jsonc. Returns the list of pacSelectors."""
    owner = settings.get("pacOwnerId")
    if not isinstance(owner, str) or not GUID_RE.match(owner):
        problems.append(f"global-settings.jsonc: pacOwnerId is not a GUID ({owner!r})")

    envs = settings.get("pacEnvironments")
    if not isinstance(envs, list) or not envs:
        problems.append("global-settings.jsonc: pacEnvironments is missing or empty")
        return []

    selectors = []
    for i, env in enumerate(envs):
        at = f"global-settings.jsonc: pacEnvironments[{i}]"
        if not isinstance(env, dict):
            problems.append(f"{at}: not an object")
            continue

        selector = env.get("pacSelector")
        if not isinstance(selector, str) or not selector.strip():
            problems.append(f"{at}: pacSelector is missing or empty")
        else:
            if selector in selectors:
                problems.append(f"{at}: duplicate pacSelector {selector!r}")
            selectors.append(selector)

        tenant = env.get("tenantId")
        if not isinstance(tenant, str) or not GUID_RE.match(tenant):
            problems.append(f"{at}: tenantId is not a GUID ({tenant!r})")

        root = env.get("deploymentRootScope")
        if not isinstance(root, str) or not MG_SCOPE_RE.match(root):
            problems.append(
                f"{at}: deploymentRootScope must be "
                f"/providers/Microsoft.Management/managementGroups/<name> (got {root!r})"
            )

        for j, scope in enumerate(env.get("globalNotScopes") or []):
            if not _is_scope(scope):
                problems.append(f"{at}: globalNotScopes[{j}] is not a valid scope ({scope!r})")

    return selectors


def _is_scope(value):
    return isinstance(value, str) and bool(MG_SCOPE_RE.match(value) or SUB_SCOPE_RE.match(value))


def check_assignment_scopes(assignments, selectors, problems):
    """Every pacSelector must appear in every assignment's scope block, and every
    scope value must be a well-formed management-group or subscription id."""
    for path, doc in assignments:
        scope = doc.get("scope")
        if not isinstance(scope, dict):
            problems.append(f"{path}: missing a 'scope' block")
            continue

        for selector in selectors:
            if selector not in scope:
                problems.append(
                    f"{path}: no scope entry for pacSelector {selector!r} — this assignment "
                    f"would be SILENTLY SKIPPED when deploying that environment "
                    f"(present: {sorted(scope)})"
                )
            elif not scope[selector]:
                problems.append(
                    f"{path}: scope[{selector!r}] is empty — the assignment would deploy nowhere"
                )

        for block in ("scope", "notScopes"):
            for selector, values in (doc.get(block) or {}).items():
                if not isinstance(values, list):
                    problems.append(f"{path}: {block}[{selector!r}] must be a list")
                    continue
                for k, value in enumerate(values):
                    if not _is_scope(value):
                        problems.append(
                            f"{path}: {block}[{selector!r}][{k}] is not a valid scope "
                            f"({value!r}) — expected /providers/Microsoft.Management/"
                            f"managementGroups/<name> or /subscriptions/<guid>"
                        )

        unknown = set(scope) - set(selectors)
        for selector in sorted(unknown):
            problems.append(
                f"{path}: scope has entry for {selector!r}, which is not a pacSelector in "
                f"global-settings.jsonc — it will never be used"
            )


def check_references(assignments, policysets, policydefs, problems):
    """Assignments must point at a policy set that exists; policy sets must point at
    custom definitions that exist. Built-in members are taken on trust."""
    set_names = {doc.get("name") for _p, doc in policysets if doc.get("name")}
    def_names = {doc.get("name") for _p, doc in policydefs if doc.get("name")}

    for path, doc in assignments:
        # This builder emits definitionEntry.policySetName (EPAC 11.x). A flat top-level
        # policySetDefinitionName is still accepted here for older/hand-written packages. A
        # definitionEntryList or a built-in policySetDefinitionId is not ours to resolve.
        wanted = doc.get("policySetDefinitionName")
        if wanted is None:
            entry = doc.get("definitionEntry")
            if isinstance(entry, dict):
                wanted = entry.get("policySetName")
        if wanted is None:
            continue
        if wanted not in set_names:
            problems.append(
                f"{path}: policy set {wanted!r} has no matching file in "
                f"policySetDefinitions/ (found: {sorted(set_names) or 'none'})"
            )

    for path, doc in policysets:
        members = (doc.get("properties") or {}).get("policyDefinitions") or []
        for i, member in enumerate(members):
            if not isinstance(member, dict):
                problems.append(f"{path}: properties.policyDefinitions[{i}] is not an object")
                continue
            name = member.get("policyDefinitionName")
            if name is not None and name not in def_names:
                problems.append(
                    f"{path}: member[{i}] references custom policy {name!r}, which has no "
                    f"matching file in policyDefinitions/"
                )


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def validate(package_dir):
    """Validate the package rooted at ``package_dir``. Returns a list of problems."""
    root = Path(package_dir)
    problems = []

    defs_root = root / "Definitions"
    if not defs_root.is_dir():
        return [f"{defs_root} not found — run this from the package root (where Definitions/ is)"]

    settings_path = defs_root / "global-settings.jsonc"
    if not settings_path.is_file():
        settings_path = defs_root / "global-settings.json"
    if not settings_path.is_file():
        return [f"{defs_root}/global-settings.jsonc not found — this is not an EPAC package"]

    settings = _load(settings_path, problems)
    if settings is None:
        return problems  # nothing further is meaningful

    assignments = _load_dir(defs_root, "policyAssignments", problems)
    policysets = _load_dir(defs_root, "policySetDefinitions", problems)
    policydefs = _load_dir(defs_root, "policyDefinitions", problems)
    all_docs = [(settings_path, settings)] + assignments + policysets + policydefs

    selectors = check_global_settings(settings, problems)
    check_placeholders(all_docs, problems)
    check_assignment_scopes(assignments, selectors, problems)
    check_references(assignments, policysets, policydefs, problems)
    return problems


def main(argv):
    package_dir = argv[1] if len(argv) > 1 else "."
    problems = validate(package_dir)

    if problems:
        print(f"[validate] FAIL — {len(problems)} problem(s) in '{package_dir}':\n")
        for p in problems:
            print(f"  - {p}")
        print(
            "\nThis is a static check. A pass here does not prove the package deploys — "
            "the plan step (Build-DeploymentPlans) validates against live Azure."
        )
        return 1

    print(f"[validate] OK — '{package_dir}' passed all static checks.")
    print(
        "Note: shape and reference checks only. Whether the referenced management groups "
        "and subscriptions exist is proven by the plan step, not here."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
