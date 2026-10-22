#!/usr/bin/env bash
set -euo pipefail

# Publish a verified stable release. Prepare its changelog entry before invocation.

if [ $# -lt 1 ]; then
  echo "Usage: $0 <version> (e.g. 0.9.0 or 1.0.0)"
  exit 1
fi

RAW_VERSION="${1#v}"
if [[ ! "$RAW_VERSION" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
  echo "Expected a stable semantic version (for example 0.9.0)." >&2
  exit 1
fi
TAG_NAME="v$RAW_VERSION"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$CURRENT_BRANCH" == HEAD || -n "$(git status --porcelain)" ]]; then
  echo "Release requires a branch with a clean working tree and index." >&2
  exit 1
fi
if git rev-parse -q --verify "refs/tags/$TAG_NAME" >/dev/null; then
  echo "Release tag already exists: $TAG_NAME" >&2
  exit 1
fi
command -v gh >/dev/null
python3 -c 'import build' || { echo 'Install the Python build frontend before releasing.' >&2; exit 1; }

python3 - "$RAW_VERSION" <<'PY'
import json
from pathlib import Path
import re
import sys

version = sys.argv[1]
path = Path('pyproject.toml')
source = path.read_text(encoding='utf-8')
old = re.search(r'^version = "([0-9]+\.[0-9]+\.[0-9]+)"$', source, re.M)
if old is None or tuple(map(int, version.split('.'))) <= tuple(map(int, old[1].split('.'))):
    raise SystemExit('Release version must exceed the current package version')
if not re.search(r'^## ' + re.escape(version) + r' — ', Path('CHANGELOG.md').read_text(encoding='utf-8'), re.M):
    raise SystemExit('Prepare the target version entry in CHANGELOG.md before release')
path.write_text(source[:old.start(1)] + version + source[old.end(1):], encoding='utf-8')
manifest_path = Path('documentation/MANIFEST.json')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['package_version'] = version
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
PY
python3 scripts/check_repository.py --write-manifest
python3 scripts/check_repository.py
python3 -m build

git add pyproject.toml documentation/MANIFEST.json
git commit -m "chore(release): $TAG_NAME"

# Create annotated tag
echo "🏷️ Tagging $TAG_NAME..."
git tag -a "$TAG_NAME" -m "Release $TAG_NAME - Crewloom Toolkit"

# Push to origin
echo "⬆️ Pushing branch and tags to origin..."
git push origin "HEAD:refs/heads/$CURRENT_BRANCH" "refs/tags/$TAG_NAME"

# Create GitHub Release via gh CLI
gh release create "$TAG_NAME" --verify-tag \
  --title "Crewloom Core $TAG_NAME" --generate-notes

echo "✅ Successfully released $TAG_NAME for crewloom!"
