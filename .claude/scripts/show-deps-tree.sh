#!/bin/bash
# Dependency Tree Visualization
# Shows file dependencies in tree format with colors

set -eo pipefail

FILE="${1:-}"
DEP_GRAPH="${DEP_GRAPH_FILE:-.claude/dep-graph.toon}"

if [ -z "$FILE" ]; then
  echo "Usage: show-deps-tree.sh <file-path>"
  exit 1
fi

if [ ! -f "$DEP_GRAPH" ]; then
  echo "Error: Dependency graph not found: $DEP_GRAPH"
  echo "Run: .claude/bin/dependency-scanner --path . --output .claude/dep-graph.toon"
  exit 1
fi

# Find lib directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/../lib/toon-parser.sh" ]; then
  source "$SCRIPT_DIR/../lib/toon-parser.sh"
elif [ -f ".claude/lib/toon-parser.sh" ]; then
  source ".claude/lib/toon-parser.sh"
else
  echo "Error: Cannot find toon-parser.sh"
  exit 1
fi

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
BLUE='\033[0;34m'
RESET='\033[0m'

echo ""
echo -e "${BLUE}${FILE}${RESET} dependency tree:"
echo ""

# Get imports for this file
IMPORTS=$(toon_get_imports "$DEP_GRAPH" "$FILE")

if [ -z "$IMPORTS" ]; then
  echo -e "${GRAY}  (no imports)${RESET}"
else
  echo "$IMPORTS" | while read -r import_file; do
    echo -e "  ${GREEN}├─→${RESET} ${import_file}"
  done
fi

echo ""

# Get files that import THIS file  
IMPORTERS=$(toon_get_importers "$DEP_GRAPH" "$FILE")
IMPORTER_COUNT=$(echo "$IMPORTERS" | grep -c . 2>/dev/null || echo "0")
IMPORTER_COUNT=${IMPORTER_COUNT//[^0-9]/}
IMPORTER_COUNT=${IMPORTER_COUNT:-0}

if [ "$IMPORTER_COUNT" -gt 0 ]; then
  echo -e "${YELLOW}Files depending on ${FILE}:${RESET} ${IMPORTER_COUNT}"
  echo ""
  
  echo "$IMPORTERS" | head -10 | while read -r importer; do
    echo -e "  ${RED}◀─┤${RESET} ${importer}"
  done
  
  [ "$IMPORTER_COUNT" -gt 10 ] && echo -e "  ${GRAY}... and $((IMPORTER_COUNT - 10)) more${RESET}"
fi

echo ""
