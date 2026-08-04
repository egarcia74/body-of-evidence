#!/bin/bash
# Body of Evidence — Repository Initialization Script
# Double-click this file to run it in Terminal

REPO="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
echo "Initializing Body of Evidence repository at: $REPO"

cd "$REPO" || exit 1

# Remove stale lock file if present
rm -f .git/index.lock

# Configure git identity for this repo
git config user.email "boe@body-of-evidence.org"
git config user.name "Body of Evidence"

# Stage everything
git add -A

# Commit
git commit -m "feat: bootstrap Body of Evidence v0.1 — founding repository scaffold"

echo ""
echo "Done. Commit hash:"
git log --oneline -1

echo ""
echo "You can close this window."
read -p "Press Enter to close..."
