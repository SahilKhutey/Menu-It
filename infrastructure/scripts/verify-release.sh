#!/usr/bin/env bash
# ModularMenu — Release Manifest & Digest Validator (ARC-11 §18.1)
set -euo pipefail

MANIFEST_FILE="${1:-release-manifest.json}"

if [ ! -f "$MANIFEST_FILE" ]; then
    echo "ERROR: Release manifest not found: $MANIFEST_FILE"
    exit 1
fi

echo "=== Verifying Release Manifest: $MANIFEST_FILE ==="

python - <<'PY'
import json, sys, re

with open(sys.argv[1], 'r') as f:
    manifest = json.load(f)

assert manifest.get("product") == "ModularMenu", "Invalid product identifier"
assert "release" in manifest, "Missing release version"
assert "git_commit" in manifest, "Missing git_commit SHA"
assert "components" in manifest, "Missing components block"

components = manifest["components"]
for comp in ["frontend", "backend", "worker"]:
    assert comp in components, f"Missing component {comp}"
    digest = components[comp].get("digest", "")
    assert digest.startswith("sha256:"), f"Component {comp} digest is not a valid sha256: {digest}"

print(f"✓ Validated manifest for release: {manifest['release']} (Commit: {manifest['git_commit']})")
PY "$MANIFEST_FILE"

echo "=== Release Manifest Verified ==="
