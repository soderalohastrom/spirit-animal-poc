# /verify-tools - Verify installation

Verify that Claude Dev Tools is properly installed.

## Usage
```
/verify-tools
```

## Instructions

Run the verification script:

```bash
bash .claude/scripts/verify-install.sh
```

This checks:
1. All required directories exist
2. Go binaries are built and executable
3. Shell tools are present and executable
4. Hooks are configured
5. Dependency graph exists (optional)
6. Binaries can execute successfully

If any checks fail, provide guidance on how to fix the installation.
