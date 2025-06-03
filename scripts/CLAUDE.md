# Scripts and Utilities - Claude Code Guide

Scripts and utilities guidance for the MCP Task Orchestrator's diagnostic and maintenance tools.

## Scripts Architecture

**System Tools**: Comprehensive diagnostic, maintenance, and deployment utilities.

### Key Script Categories
- `diagnostics/` - System health checking and validation tools
- `maintenance/` - Database and task lifecycle management
- `deployment/` - Installation and configuration scripts
- `migrations/` - Database schema and data migration utilities

## Diagnostic Commands

### System Health Checking
```bash
# Comprehensive health check (run first for any issues)
python diagnostics/check_status.py

# Installation verification
python diagnostics/verify_tools.py

# Database optimization and analysis
python diagnostics/diagnose_db.py
```

### Performance and Troubleshooting
```bash
# Timeout investigation
python diagnose_timeout.py

# Migration validation
python run_migration_test.py

# Alternative test execution
python run_tests_alternative.py
```

### Installation and Setup
```bash
# Windows installation
./install.ps1

# Unix/Linux installation
./install.sh

# Database migration
python migrate_to_persistence.py
```

## Script Development Patterns

### Diagnostic Script Structure
- **Health Checks**: Comprehensive system state validation
- **Error Reporting**: Clear, actionable error messages
- **Repair Suggestions**: Automated fix recommendations
- **Logging**: Detailed execution traces for troubleshooting

### Maintenance Script Guidelines
- **Safety First**: Backup data before destructive operations
- **Validation**: Verify system state before and after operations
- **Recovery**: Provide rollback mechanisms for critical changes
- **Documentation**: Clear usage instructions and examples

### Integration with Orchestrator
- **Maintenance Coordinator**: Use orchestrator tools for complex maintenance
- **Artifact Storage**: Store maintenance results as artifacts
- **Context Continuity**: Leverage directory-specific guidance for focused work

---

**System Utilities**: This directory contains diagnostic and maintenance tools. Always run health checks before major operations.
