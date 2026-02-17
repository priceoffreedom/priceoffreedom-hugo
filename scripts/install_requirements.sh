#!/bin/bash
# Install Hugo (extended) and Go for the Price of Freedom Hugo site
set -e

echo "=== Installing Go ==="
sudo snap install go --classic

echo ""
echo "=== Installing Hugo Extended ==="
# Hugo extended is needed for SCSS/SASS support used by most themes
sudo snap install hugo

echo ""
echo "=== Verifying installations ==="
echo "Go:   $(go version)"
echo "Hugo: $(hugo version)"

echo ""
echo "=== Adding second GitHub account (priceoffreedom) ==="
gh auth login --hostname github.com

echo ""
echo "Done! Run 'gh auth status' to verify both accounts."
