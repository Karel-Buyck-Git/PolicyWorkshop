#!/usr/bin/env bash
#
# Contoso golden-fixture regression — the epac-builder determinism contract.
#
# Rebuilds the worked sample for EVERY renderer flavour and diffs the result
# byte-for-byte against the committed trees:
#
#   json      -> examples/contoso/package             (the worked sample)
#   terraform -> examples/contoso/fixtures/terraform
#   bicep     -> examples/contoso/fixtures/bicep
#
# Then asserts the --strict deploy-ready gate FIRES: the contoso manifest intentionally leaves
# one selection unmapped, so `--check --strict` must reject it (regression guard for the gate).
#
# The pipeline logic lives here, with the example; .github/workflows/contoso-epac-build.yml
# is a thin trigger that just calls this. Runnable from anywhere (it locates its own
# catalogue-builder/ root). To ACCEPT an intended change, rebuild the relevant fixture in
# place (e.g. `--only terraform --out examples/contoso/fixtures/terraform`) and commit the diff.
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CB="$(cd "$HERE/../.." && pwd)"   # catalogue-builder/
cd "$CB"

MANIFEST="examples/contoso/manifests/manifest.example.jsonc"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

build_and_diff() {
  flavour="$1"; fixture="$2"
  echo "[verify] build flavour=$flavour"
  python flows/epac_builder/assemble_scaffold.py \
    --manifest "$MANIFEST" --only "$flavour" --out "$WORK/$flavour"
  echo "[verify] diff -rq  $WORK/$flavour  <->  $fixture"
  diff -rq "$WORK/$flavour" "$fixture"
}

build_and_diff json      examples/contoso/package
build_and_diff terraform examples/contoso/fixtures/terraform
build_and_diff bicep     examples/contoso/fixtures/bicep

# Deploy-ready gate (--strict) must FIRE on this manifest: contoso intentionally leaves the
# management/essential/tags selection unmapped -> placeholder scope, so --strict has to reject
# it (exit != 0). Guards the gate against silently passing an incomplete manifest.
echo "[verify] strict-gate regression: expect --check --strict to FAIL on the unmapped selection"
if python flows/epac_builder/assemble_scaffold.py --manifest "$MANIFEST" --check --strict >/dev/null 2>&1; then
  echo "[verify] FAIL: --strict passed a manifest with a placeholder scope (gate is broken)" >&2
  exit 1
fi
echo "[verify] strict-gate fired as expected"

echo "[verify] OK — json, terraform and bicep all byte-identical to committed fixtures; strict gate fires"
