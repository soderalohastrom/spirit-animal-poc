#!/usr/bin/env bash
# Impact analysis - shows the impact of changing a file

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

if [ $# -lt 1 ]; then
    echo "Usage: $0 <file-path> [graph-file]"
    echo ""
    echo "Analyze the impact of changing a file"
    exit 1
fi

TARGET_FILE="$1"
[ $# -ge 2 ] && GRAPH_FILE="$2"

if [ ! -f "$GRAPH_FILE" ]; then
    echo "Error: Graph file not found: $GRAPH_FILE"
    echo "Run: .claude/bin/dependency-scanner --path . --output .claude/dep-graph.toon"
    exit 1
fi

if ! toon_file_exists "$GRAPH_FILE" "$TARGET_FILE"; then
    echo "Error: File not found in dependency graph: $TARGET_FILE"
    exit 1
fi

get_recursive_importers() {
    local file="$1"
    local graph="$2"
    local visited="$3"

    echo "$visited" | grep -q "^$file$" && return
    visited="$visited"$'\n'"$file"

    local importers
    importers=$(toon_get_importers "$graph" "$file" 2>/dev/null || true)

    if [ -n "$importers" ]; then
        echo "$importers"
        while IFS= read -r importer; do
            [ -n "$importer" ] && get_recursive_importers "$importer" "$graph" "$visited"
        done <<< "$importers"
    fi
}

echo "Impact Analysis for: $TARGET_FILE"
echo ""

DIRECT_IMPORTERS=$(toon_get_importers "$GRAPH_FILE" "$TARGET_FILE")
DIRECT_COUNT=$(toon_count_importers "$GRAPH_FILE" "$TARGET_FILE")

echo "Direct impact:"
if [ "$DIRECT_COUNT" -eq 0 ]; then
    echo "  (none - no files import this)"
else
    echo "$DIRECT_IMPORTERS" | while IFS= read -r importer; do
        echo "  - $importer"
    done
fi
echo ""

echo "Recursive impact:"
ALL_IMPORTERS=$(get_recursive_importers "$TARGET_FILE" "$GRAPH_FILE" "")
if [ -z "$ALL_IMPORTERS" ]; then
    echo "  (none)"
    TOTAL_IMPACT=0
else
    UNIQUE_IMPORTERS=$(echo "$ALL_IMPORTERS" | sort -u | grep -v "^$TARGET_FILE$" || true)
    if [ -z "$UNIQUE_IMPORTERS" ]; then
        echo "  (none)"
        TOTAL_IMPACT=0
    else
        echo "$UNIQUE_IMPORTERS" | while IFS= read -r importer; do
            echo "  - $importer"
        done
        TOTAL_IMPACT=$(echo "$UNIQUE_IMPORTERS" | wc -l | tr -d ' ')
    fi
fi
echo ""
echo "Total files affected: ${TOTAL_IMPACT:-0}"
