# Claude Dev Tools

Dependency analysis and large file tools.

## Slash Commands

| Command | Description |
|---------|-------------|
| `/deps <file>` | What imports this file? |
| `/impact <file>` | What breaks if I change this? |
| `/circular` | Find circular dependencies |
| `/deadcode` | Find unused files |
| `/deps-tree <file>` | Visualize dependency tree |
| `/large-file <file>` | Read large file progressively |
| `/scan-deps` | Rebuild dependency graph |
| `/verify-tools` | Verify installation |

## Large Files (>50KB)

The PreToolUse hook blocks Read on files over 50KB. Use `/large-file` or:

```bash
.claude/bin/progressive-reader --path <file> --list    # See structure
.claude/bin/progressive-reader --path <file> --chunk N  # Read chunk
```

## Rebuild Dependency Graph

```bash
.claude/bin/dependency-scanner --path . --output .claude/dep-graph.toon
```
