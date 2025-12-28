# /large-file - Read large files progressively

Read large files (>50KB) efficiently using progressive-reader.

## Usage
```
/large-file <file-path> [chunk-number]
```

## Instructions

If no chunk number is provided, first list the file structure:

```bash
.claude/bin/progressive-reader --path $ARGUMENTS --list
```

This shows:
- File size and detected language
- Functions/classes/methods found
- Available chunks with line ranges

If a chunk number is provided:

```bash
.claude/bin/progressive-reader --path <file-path> --chunk <chunk-number>
```

Guide the user through reading the file progressively, suggesting which chunks are most relevant to their task.

**Token savings**: Progressive reading typically saves 75-97% of tokens compared to reading the full file.
