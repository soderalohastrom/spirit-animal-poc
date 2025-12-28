# /scan-deps - Rebuild dependency graph

Rebuild the dependency graph for the current project.

## Usage
```
/scan-deps [path]
```

## Instructions

Run the dependency scanner:

```bash
.claude/bin/dependency-scanner --path ${ARGUMENTS:-.} --output .claude/dep-graph.toon
```

Report the results:
1. Number of files scanned
2. Languages detected
3. Circular dependencies found (if any)
4. Dead code detected (if any)
5. Time taken

**When to rebuild:**
- After pulling new code from git
- After adding/removing files
- After changing import statements
- If dependency queries seem stale
