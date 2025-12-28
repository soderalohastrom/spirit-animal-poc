# /deps - Query file dependencies

Query what files import the target file and what it imports.

## Usage
```
/deps <file-path>
```

## Instructions

Run the dependency query tool:

```bash
bash .claude/tools/query-deps/query-deps.sh $ARGUMENTS
```

Report the results showing:
1. What files the target imports
2. What files import the target
3. Total importer count

If the dependency graph doesn't exist, instruct the user to run:
```bash
.claude/bin/dependency-scanner --path . --output .claude/dep-graph.toon
```
