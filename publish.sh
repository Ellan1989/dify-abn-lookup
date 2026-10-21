#!/usr/bin/env bash
# Publish the ABN Lookup plugin to the Dify Marketplace.
#
# Prerequisites (already satisfied on this machine):
#   - gh CLI logged in as Ellan1989
#   - Plugin packaged at abn_lookup-0.0.1.difypkg, validator-clean
#   - Source repo committed at ./
#
# What this script does:
#   1. Create the public source repo Ellan1989/dify-abn-lookup and push
#      (required by the marketplace submission: a public source repository).
#   2. Fork langgenius/dify-plugins (skipped if fork already exists).
#   3. Copy the .difypkg into ellan1989/abn_lookup/ on a new branch.
#   4. Open a pull request against langgenius/dify-plugins:main.
#
# After the PR is merged by the Dify team, the marketplace page URL will be:
#   https://marketplace.dify.ai/plugin/ellan1989/abn_lookup
set -euo pipefail

GH_USER="Ellan1989"
PLUGIN_DIR_NAME="ellan1989/abn_lookup"
PKG="abn_lookup-0.0.1.difypkg"
BRANCH="add-abn_lookup-0.0.1"
ROOT="$(cd "$(dirname "$0")" && pwd)"

cd "$ROOT"

echo "==> [1/4] Creating public source repo ${GH_USER}/dify-abn-lookup (if missing)..."
if gh repo view "${GH_USER}/dify-abn-lookup" >/dev/null 2>&1; then
  echo "    repo already exists, pushing latest commit"
  git push -u "https://github.com/${GH_USER}/dify-abn-lookup.git" HEAD:main 2>/dev/null || \
    git remote add origin "https://github.com/${GH_USER}/dify-abn-lookup.git" && \
    git push -u origin main
else
  gh repo create "${GH_USER}/dify-abn-lookup" --public --source . --push
fi

echo "==> [2/4] Forking langgenius/dify-plugins (if missing)..."
if ! gh repo view "${GH_USER}/dify-plugins" >/dev/null 2>&1; then
  gh repo fork langgenius/dify-plugins --clone=false
  sleep 5
fi

echo "==> [3/4] Preparing submission branch..."
WORK="$(mktemp -d)/dify-plugins"
gh repo clone "${GH_USER}/dify-plugins" "$WORK" -- --depth 5
cd "$WORK"
git checkout -b "$BRANCH"
# sync with upstream main to avoid stale-base review churn
git remote add upstream https://github.com/langgenius/dify-plugins.git 2>/dev/null || true
git fetch upstream main --depth 5 && git merge --ff-only upstream/main 2>/dev/null || true
mkdir -p "$PLUGIN_DIR_NAME"
cp "$ROOT/$PKG" "$PLUGIN_DIR_NAME/"
git add "$PLUGIN_DIR_NAME"
git -c user.name="$GH_USER" -c user.email="${GH_USER}@users.noreply.github.com" \
  commit -m "feat: add ABN Lookup 0.0.1 tool plugin"
git push -u origin "$BRANCH"

echo "==> [4/4] Opening PR..."
gh pr create \
  --repo langgenius/dify-plugins \
  --base main \
  --head "${GH_USER}:${BRANCH}" \
  --title "feat: add ABN Lookup 0.0.1 tool plugin" \
  --body-file "$ROOT/PR_DESCRIPTION.md"

echo
echo "Done. PR opened. After merge, your marketplace URL will be:"
echo "  https://marketplace.dify.ai/plugin/ellan1989/abn_lookup"
