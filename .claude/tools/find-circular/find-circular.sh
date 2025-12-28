#!/usr/bin/env bash
# Find circular dependencies

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

CIRCULAR=$(toon_get_circular "$GRAPH_FILE")

if [ -z "$CIRCULAR" ]; then
    echo "✓ No circular dependencies found"
    exit 0
fi

CYCLE_COUNT=$(echo "$CIRCULAR" | wc -l | tr -d ' ')

echo "Found $CYCLE_COUNT circular dependency cycle(s):"
echo ""

INDEX=1
echo "$CIRCULAR" | while IFS= read -r cycle; do
    echo "Cycle $INDEX:"
    echo "  $cycle"
    echo ""
    INDEX=$((INDEX + 1))
done
