# /deadcode - Find unused files

Detect potentially unused files (dead code) in the codebase.

## Usage
```
/deadcode
```

## Instructions

Run the dead code finder:

```bash
bash .claude/tools/find-dead-code/find-dead-code.sh
```

Report the results:
1. List all files with zero importers
2. Exclude entry points (main files, index files, config files)
3. Group by directory for easier review
4. Suggest which files might be safe to delete

Note: Some files may be used dynamically or as entry points. Recommend manual verification before deletion.
