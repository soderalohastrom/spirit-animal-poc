#!/bin/bash
# Large File Guard - Blocks Read on files >50KB, suggests progressive-reader
# Part of Claude Dev Tools

set -eo pipefail

# Read JSON from stdin (Claude Code hook protocol)
INPUT_JSON=$(cat)

# Extract tool name
TOOL_NAME=$(echo "$INPUT_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_name', ''))" 2>/dev/null || echo "")

# Only check Read tool
[ "$TOOL_NAME" != "Read" ] && exit 0

# Extract file path
FILE_PATH=$(echo "$INPUT_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('file_path', ''))" 2>/dev/null || echo "")

# Skip if no path or file doesn't exist
[ -z "$FILE_PATH" ] && exit 0
[ ! -f "$FILE_PATH" ] && exit 0

# Skip images and binary files
FILE_EXT="${FILE_PATH##*.}"
case "${FILE_EXT,,}" in
  jpg|jpeg|png|gif|webp|svg|bmp|ico|pdf|ipynb)
    exit 0
    ;;
esac

# Get file size (macOS and Linux compatible)
FILE_SIZE=$(stat -f%z "$FILE_PATH" 2>/dev/null || stat -c%s "$FILE_PATH" 2>/dev/null || echo "0")

# Block if over 50KB (51200 bytes)
if [ "$FILE_SIZE" -gt 51200 ]; then
  FILE_SIZE_KB=$((FILE_SIZE / 1024))
  echo "{\"decision\": \"block\", \"reason\": \"File ${FILE_SIZE_KB}KB exceeds 50KB limit. Use progressive-reader: .claude/bin/progressive-reader --path $FILE_PATH --list\"}"
fi

exit 0
