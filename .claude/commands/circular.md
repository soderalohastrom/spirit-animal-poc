# /circular - Find circular dependencies

Detect circular import chains in the codebase.

## Usage
```
/circular
```

## Instructions

Run the circular dependency finder:

```bash
bash .claude/tools/find-circular/find-circular.sh
```

Report the results:
1. List all circular dependency chains found
2. For each chain, explain the cycle (A -> B -> C -> A)
3. Suggest which dependency to break to resolve the cycle

If no circular dependencies are found, confirm the codebase is clean.
