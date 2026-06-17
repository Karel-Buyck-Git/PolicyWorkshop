#!/usr/bin/env bash
# Packages the cloud-adoption-framework skill into dist/cloud-adoption-framework.skill
# (a zip with SKILL.md at the root). Only SKILL.md + references/ are included; the dev
# harness is excluded so it never ships to users.
#
# Usage: ./build.sh
set -euo pipefail

SKILL_NAME="cloud-adoption-framework"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST="$ROOT/dist"
STAGING="$(mktemp -d)"
trap 'rm -rf "$STAGING"' EXIT

INCLUDE=("SKILL.md" "references")

echo "Building $SKILL_NAME skill..."

for item in "${INCLUDE[@]}"; do
  if [[ ! -e "$ROOT/$item" ]]; then
    echo "ERROR: required skill item not found: $item" >&2
    exit 1
  fi
  cp -r "$ROOT/$item" "$STAGING/"
done

if ! grep -qE "^name:[[:space:]]*$SKILL_NAME([[:space:]]|$)" "$STAGING/SKILL.md"; then
  echo "ERROR: SKILL.md frontmatter must declare 'name: $SKILL_NAME'" >&2
  exit 1
fi

mkdir -p "$DIST"
rm -f "$DIST/$SKILL_NAME.skill"
( cd "$STAGING" && zip -r -q "$DIST/$SKILL_NAME.skill" . )

echo "Built: $DIST/$SKILL_NAME.skill"
