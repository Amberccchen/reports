#!/usr/bin/env bash
# Build the encrypted site and publish ONLY the encrypted pages to the public
# user-site repo (Amberccchen.github.io), served at https://amberccchen.github.io/reports/.
# This repo (reports) stays private.
#   REPORTS_KEY=... tools/deploy.sh [src_dir] [public_clone]
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${1:-$HOME/reports-src}"
PUB="${2:-$HOME/reports-public}"
: "${REPORTS_KEY:?set REPORTS_KEY}"
python3 -I "$REPO/tools/build.py" "$SRC" "$REPO"
[ -d "$PUB/.git" ] || git clone -q https://github.com/Amberccchen/Amberccchen.github.io.git "$PUB"
rm -rf "$PUB/reports" && mkdir -p "$PUB/reports"
cp "$REPO/index.html" "$PUB/reports/" && cp -r "$REPO/r" "$PUB/reports/"
touch "$PUB/.nojekyll"
cd "$PUB" && git add -A
if git diff --cached --quiet; then echo "public site unchanged"; exit 0; fi
git commit -qm "Update reports"
git -c credential.helper='!gh auth git-credential' push -q origin main
echo "published https://amberccchen.github.io/reports/"
