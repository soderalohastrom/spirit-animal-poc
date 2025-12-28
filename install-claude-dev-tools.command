#!/bin/bash
# Claude Dev Tools - Double-Click Installer
# Copy this file to your project root and double-click to install

# Change to the directory where this script is located
cd "$(dirname "$0")"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Installing Claude Dev Tools"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Project: $(pwd)"
echo ""

# Run the remote install
curl -fsSL https://raw.githubusercontent.com/soderalohastrom/claude-dev-tools/master/install | bash

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Installation complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "You can now delete this installer file."
echo ""
echo "Press any key to close..."
read -n 1
