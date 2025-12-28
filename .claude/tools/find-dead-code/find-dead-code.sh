#!/usr/bin/env bash
# Find potentially dead/unused code

set -eo pipefail

# Find lib directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/../../lib/toon-parser.sh" ]; then
  LIB_DIR="$SCRIPT_DIR/../../lib"
elif [ -f "$SCRIPT_DIR/../lib/toon-parser.sh" ]; then
  LIB_DIR="$SCRIPT_DIR/../lib"
else
  echo "Error: Cannot find toon-parser.sh"
  exit 1
fi

source "$LIB_DIR/toon-parser.sh"

GRAPH_FILE="${DEP_GRAPH_FILE:-.claude/dep-graph.toon}"
[ $# -ge 1 ] && GRAPH_FILE="$1"

if [ ! -f "$GRAPH_FILE" ]; then
    echo "Error: Graph file not found: $GRAPH_FILE"
    echo "Run: .claude/bin/dependency-scanner --path . --output .claude/dep-graph.toon"
    exit 1
fi

DEADCODE=$(toon_get_deadcode "$GRAPH_FILE")

if [ -z "$DEADCODE" ]; then
    echo "✓ No potentially unused files found"
    exit 0
fi

DEAD_COUNT=$(echo "$DEADCODE" | wc -l | tr -d ' ')

echo "Found $DEAD_COUNT potentially unused file(s):"
echo ""

echo "$DEADCODE" | while IFS= read -r file; do
    echo "  - $file"
done

echo ""
echo "Note: These files have no importers. Verify before deleting."
