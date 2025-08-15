# Temporary Testing Directory

This directory contains temporary test scripts and artifacts that are created during development and testing processes.

## Purpose

This directory serves as a managed temporary space for:
- One-time fix scripts (`fix_*.py`)
- Test compatibility scripts
- Temporary hook testing scripts  
- Development debugging scripts
- Short-term testing artifacts

## Lifecycle Management

### Automatic Cleanup
Files in this directory are subject to automated cleanup via the lifecycle management system:

```bash
# Run cleanup manually
python scripts/lifecycle/automated_cleanup_manager.py --dry-run

# Apply cleanup
python scripts/lifecycle/automated_cleanup_manager.py
```

### Retention Policy
- **Fix scripts**: Cleaned after 7 days
- **Test scripts**: Cleaned after 7 days  
- **Debug artifacts**: Cleaned after 7 days
- **Hook test scripts**: Cleaned after use

## Guidelines for Contributors

### When to Use This Directory
- Creating temporary fix scripts during debugging
- Testing one-off solutions before implementing properly
- Validating hook functionality
- Short-term compatibility testing

### When NOT to Use This Directory
- Production scripts (use `scripts/` subdirectories)
- Permanent test suites (use `tests/`)
- Documentation (use `docs/`)
- Long-term artifacts (use `docs/archives/`)

### Best Practices
1. **Prefix files appropriately**: `fix_`, `test_`, `debug_`, etc.
2. **Include dates in filenames**: `fix_auth_20250813.py`
3. **Clean up manually when done**: Don't rely only on automation
4. **Document purpose**: Add comments explaining what the script does
5. **Use descriptive names**: Avoid generic names like `temp.py`

## File Organization

```
temporary/
├── README.md                    # This file
├── fix_*.py                    # Temporary fix scripts  
├── test_*.py                   # Temporary test scripts
├── debug_*.py                  # Debug utility scripts
├── validate_*.py               # Validation scripts
└── *hooks*.sh                  # Hook testing scripts
```

## Integration with Git Workflow

This directory and its contents are managed by `.gitignore` patterns to prevent accidental commits of temporary files:

```gitignore
# In project root .gitignore
scripts/testing/temporary/*.py
scripts/testing/temporary/*.sh
scripts/testing/temporary/*.json
scripts/testing/temporary/*.log
```

Exception: This README.md is tracked to document the system.

## Monitoring and Alerts

The Claude Code hooks system will remind contributors about cleanup:
- Weekly reminders about files older than 7 days
- Alerts when this directory contains >10 files
- Integration with project maintenance schedules

## Archive Process

When temporary files need to be preserved:
1. **Working scripts**: Move to appropriate `scripts/` subdirectory
2. **Test artifacts**: Move to `docs/archives/test-artifacts/`
3. **Historical scripts**: Move to `docs/archives/historical/development-scripts/`

## Related Documentation

- [Automated Cleanup Manager](../lifecycle/automated_cleanup_manager.py)
- [Project Lifecycle Documentation](../../docs/archives/README.md) 
- [Claude Code Integration Guidelines](../../CLAUDE.md)

Last Updated: 2025-08-13 (Phase 4 Documentation Ecosystem Modernization)