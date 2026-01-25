#!/usr/bin/env bash
# Verify Claude Dev Tools installation
# Run: bash .claude/scripts/verify-install.sh

set -eo pipefail

CLAUDE_DIR=".claude"
PASS=0
FAIL=0
WARN=0

check() {
    local name="$1"
    local path="$2"
    local required="${3:-true}"

    if [ -e "$path" ]; then
        echo "  ✓ $name"
        PASS=$((PASS + 1))
    elif [ "$required" = "true" ]; then
        echo "  ✗ $name (missing: $path)"
        FAIL=$((FAIL + 1))
    else
        echo "  ⚠ $name (optional, not found)"
        WARN=$((WARN + 1))
    fi
}

check_exec() {
    local name="$1"
    local path="$2"

    if [ -x "$path" ]; then
        echo "  ✓ $name (executable)"
        PASS=$((PASS + 1))
    elif [ -f "$path" ]; then
        echo "  ⚠ $name (exists but not executable)"
        WARN=$((WARN + 1))
    else
        echo "  ✗ $name (missing: $path)"
        FAIL=$((FAIL + 1))
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Claude Dev Tools - Installation Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check base directory
if [ ! -d "$CLAUDE_DIR" ]; then
    echo "✗ .claude directory not found"
    echo "  Run the installer first"
    exit 1
fi
echo "✓ .claude directory exists"
echo ""

# Check directories
echo "Directories:"
check "bin" "$CLAUDE_DIR/bin"
check "tools" "$CLAUDE_DIR/tools"
check "lib" "$CLAUDE_DIR/lib"
check "scripts" "$CLAUDE_DIR/scripts"
check "hooks" "$CLAUDE_DIR/hooks"
check "commands" "$CLAUDE_DIR/commands" "false"
echo ""

# Check binaries
echo "Go Binaries:"
check_exec "dependency-scanner" "$CLAUDE_DIR/bin/dependency-scanner"
check_exec "progressive-reader" "$CLAUDE_DIR/bin/progressive-reader"
echo ""

# Check shell tools
echo "Shell Tools:"
check_exec "query-deps" "$CLAUDE_DIR/tools/query-deps/query-deps.sh"
check_exec "impact-analysis" "$CLAUDE_DIR/tools/impact-analysis/impact-analysis.sh"
check_exec "find-circular" "$CLAUDE_DIR/tools/find-circular/find-circular.sh"
check_exec "find-dead-code" "$CLAUDE_DIR/tools/find-dead-code/find-dead-code.sh"
echo ""

# Check lib
echo "Libraries:"
check_exec "toon-parser" "$CLAUDE_DIR/lib/toon-parser.sh"
echo ""

# Check scripts
echo "Scripts:"
check_exec "show-deps-tree" "$CLAUDE_DIR/scripts/show-deps-tree.sh"
check_exec "verify-install" "$CLAUDE_DIR/scripts/verify-install.sh"
echo ""

# Check hooks
echo "Hooks:"
check_exec "large-file-guard" "$CLAUDE_DIR/hooks/large-file-guard.sh"
echo ""

# Check slash commands
echo "Slash Commands:"
check "deps" "$CLAUDE_DIR/commands/deps.md" "false"
check "impact" "$CLAUDE_DIR/commands/impact.md" "false"
check "circular" "$CLAUDE_DIR/commands/circular.md" "false"
check "deadcode" "$CLAUDE_DIR/commands/deadcode.md" "false"
check "deps-tree" "$CLAUDE_DIR/commands/deps-tree.md" "false"
check "large-file" "$CLAUDE_DIR/commands/large-file.md" "false"
check "scan-deps" "$CLAUDE_DIR/commands/scan-deps.md" "false"
check "verify-tools" "$CLAUDE_DIR/commands/verify-tools.md" "false"
echo ""

# Check configuration
echo "Configuration:"
check "settings.local.json" "$CLAUDE_DIR/settings.local.json"
echo ""

# Check dependency graph
echo "Data Files:"
if [ -f "$CLAUDE_DIR/dep-graph.toon" ]; then
    FILE_COUNT=$(grep -c "^FILE:" "$CLAUDE_DIR/dep-graph.toon" 2>/dev/null || echo "0")
    echo "  ✓ dep-graph.toon ($FILE_COUNT files indexed)"
    PASS=$((PASS + 1))
else
    echo "  ⚠ dep-graph.toon (not built yet)"
    echo "    Run: .claude/bin/dependency-scanner --path . --output .claude/dep-graph.toon"
    WARN=$((WARN + 1))
fi
echo ""

# Test binary functionality
echo "Functional Tests:"
if [ -x "$CLAUDE_DIR/bin/dependency-scanner" ]; then
    if "$CLAUDE_DIR/bin/dependency-scanner" --version >/dev/null 2>&1; then
        echo "  ✓ dependency-scanner runs"
        PASS=$((PASS + 1))
    else
        echo "  ✗ dependency-scanner fails to run"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  - dependency-scanner (skipped, not installed)"
fi

if [ -x "$CLAUDE_DIR/bin/progressive-reader" ]; then
    if "$CLAUDE_DIR/bin/progressive-reader" --help >/dev/null 2>&1; then
        echo "  ✓ progressive-reader runs"
        PASS=$((PASS + 1))
    else
        echo "  ✗ progressive-reader fails to run"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  - progressive-reader (skipped, not installed)"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $FAIL -eq 0 ]; then
    echo "✅ Installation verified: $PASS passed, $WARN warnings"
    exit 0
else
    echo "❌ Installation incomplete: $PASS passed, $FAIL failed, $WARN warnings"
    exit 1
fi
