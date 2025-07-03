# Scripts - Automation and Utilities

## Script Categories

### Core Operations
- **`diagnostics/`** - Health checks and system analysis
- **`maintenance/`** - Database cleanup and optimization  
- **`testing/`** - Test runners and validation tools
- **`release/`** - PyPI publishing and release automation

### Key Scripts
- **`diagnostics/health_check.py`** - Comprehensive system diagnostics
- **`maintenance/cleanup_database.py`** - Database optimization
- **`release/pypi_release_simple.py`** - Automated PyPI publishing

## Execution Guidelines

### Diagnostic Workflow
1. **`diagnostics/check_status.py`** - Always run first for system overview
2. **`diagnostics/diagnose_db.py`** - Database-specific issues
3. **`diagnostics/verify_tools.py`** - Dependency validation

### Safety Protocol
- Run health checks before major operations
- Backup data before destructive operations  
- Test scripts in isolated environments first
- Use dry-run modes where available

## Integration Notes
- Scripts work with both legacy and Clean Architecture systems
- Use dependency injection when available
- Maintain backward compatibility during transition

## File Size Limits
Keep scripts under 300-400 lines for Claude Code compatibility.