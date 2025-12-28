# /deps-tree - Visualize dependency tree

Show an ASCII tree visualization of a file's dependencies.

## Usage
```
/deps-tree <file-path>
```

## Instructions

Run the dependency tree visualizer:

```bash
bash .claude/scripts/show-deps-tree.sh $ARGUMENTS
```

Display the tree showing:
1. The target file as the root
2. Its imports as children
3. Recursive imports up to 3 levels deep
4. Indicators for circular references if detected

This helps visualize the dependency graph for a specific file.
