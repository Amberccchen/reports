#!/usr/bin/env bash
# Build the encrypted site and publish it: this repo is public and GitHub Pages
# serves it at https://amberccchen.github.io/reports/. Only encrypted pages are committed.
#   REPORTS_KEY=... tools/deploy.sh [src_dir]
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${1:-$HOME/reports-src}"
: "${REPORTS_KEY:?set REPORTS_KEY}"
python3 -I "$REPO/tools/build.py" "$SRC" "$REPO"
cd "$REPO" && git add -A
if git diff --cached --quiet; then echo "site unchanged"; exit 0; fi
git commit -qm "${MSG:-Update reports}"
git -c credential.helper='!gh auth git-credential' push -q origin main
echo "published https://amberccchen.github.io/reports/"
