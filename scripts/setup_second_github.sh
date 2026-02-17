#!/bin/bash
# Generate a second SSH key for the priceoffreedom GitHub account
# and configure SSH to use it automatically
set -e

KEY_PATH="$HOME/.ssh/id_ed25519_priceoffreedom"

echo "=== Generating new SSH key for priceoffreedom ==="
if [ -f "$KEY_PATH" ]; then
    echo "Key already exists at $KEY_PATH, skipping generation."
else
    ssh-keygen -t ed25519 -C "priceoffreedom@github" -f "$KEY_PATH" -N ""
fi

echo ""
echo "=== Configuring SSH to use separate keys per account ==="

# Back up existing config
if [ -f "$HOME/.ssh/config" ]; then
    cp "$HOME/.ssh/config" "$HOME/.ssh/config.bak"
    echo "Backed up existing SSH config to ~/.ssh/config.bak"
fi

# Check if the config already has the priceoffreedom entry
if grep -q "github-priceoffreedom" "$HOME/.ssh/config" 2>/dev/null; then
    echo "SSH config already has github-priceoffreedom entry, skipping."
else
    cat >> "$HOME/.ssh/config" << 'EOF'

# Default GitHub account (mrbell-dev)
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519

# Second GitHub account (priceoffreedom)
Host github-priceoffreedom
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_priceoffreedom
EOF
    echo "Added SSH config entries."
fi

echo ""
echo "=== Uploading key to priceoffreedom account ==="
echo "Make sure 'priceoffreedom' is the active gh account first."
echo ""

# Switch to priceoffreedom account
gh auth switch --user priceoffreedom 2>/dev/null || true

# Upload the new key
gh ssh-key add "$KEY_PATH.pub" --title "priceoffreedom-key"

echo ""
echo "=== Done! ==="
echo ""
echo "To clone/push repos for priceoffreedom, use:"
echo "  git clone git@github-priceoffreedom:priceoffreedom/repo-name.git"
echo ""
echo "To clone/push repos for mrbell-dev, use the normal:"
echo "  git clone git@github.com:mrbell-dev/repo-name.git"
echo ""
echo "Your new public key:"
cat "$KEY_PATH.pub"
