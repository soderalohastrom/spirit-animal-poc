# /impact - Impact analysis

Analyze what would break if a file is modified. Shows all direct and transitive dependents.

## Usage
```
/impact <file-path>
```

## Instructions

Run the impact analysis tool:

```bash
bash .claude/tools/impact-analysis/impact-analysis.sh $ARGUMENTS
```

Report the results showing:
1. Direct dependents (files that import this file)
2. Transitive dependents (files that depend on dependents)
3. Risk assessment based on the number of affected files

Provide recommendations if the impact is high (>10 files affected).
