#!/usr/bin/env bash
# One-time: gh auth login   (then run this script)
set -euo pipefail
cd "$(dirname "$0")"
REPO="${1:-veehainc-links}"
gh auth status >/dev/null
USER=$(gh api user -q .login)
[ -d .git ] || git init -q -b main
git add -A && git commit -qm "Update link-in-bio $(date -I)" || true
gh repo view "$USER/$REPO" >/dev/null 2>&1 || gh repo create "$REPO" --public --source=. --remote=origin --push
git push -q origin main
gh api -X POST "repos/$USER/$REPO/pages" -f 'source[branch]=main' -f 'source[path]=/' >/dev/null 2>&1 || true
echo "https://$USER.github.io/$REPO/"
