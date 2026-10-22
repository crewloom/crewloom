#!/usr/bin/env bash
set -euo pipefail

# Crewloom Core Toolkit Release Automator
# Usage: ./scripts/release.sh <new_version_e.g._0.9.0>

if [ $# -lt 1 ]; then
  echo "Usage: $0 <version> (e.g. 0.9.0 or 1.0.0)"
  exit 1
fi

RAW_VERSION="${1#v}" # remove leading 'v' if provided
TAG_NAME="v$RAW_VERSION"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🔍 Validating repository status in $PROJECT_DIR..."
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "Current branch: $CURRENT_BRANCH"

# Update MANIFEST.json package_version if exists
if [ -f "documentation/MANIFEST.json" ]; then
  echo "📝 Updating documentation/MANIFEST.json to $RAW_VERSION..."
  sed -i '' "s/\"package_version\": \".*\"/\"package_version\": \"$RAW_VERSION\"/" documentation/MANIFEST.json
  git add documentation/MANIFEST.json
fi

# Commit release bump
echo "💾 Creating release commit..."
git commit -m "chore(release): $TAG_NAME" || echo "No changes to commit"

# Create annotated tag
echo "🏷️ Tagging $TAG_NAME..."
git tag -a "$TAG_NAME" -m "Release $TAG_NAME - Crewloom Toolkit"

# Push to origin
echo "⬆️ Pushing branch and tags to origin..."
git push origin "$CURRENT_BRANCH" --tags

# Create GitHub Release via gh CLI
if command -v gh >/dev/null 2>&1; then
  echo "📢 Publishing GitHub Release for $TAG_NAME..."
  gh release create "$TAG_NAME" \
    --title "Crewloom Toolkit $TAG_NAME" \
    --generate-notes \
    --repo crewloom/crewloom || echo "⚠️ GitHub release create failed or already exists"
fi

echo "✅ Successfully released $TAG_NAME for crewloom!"
