# Scripts and Utilities - Claude Code Guide

<critical_file_size_warning>
⚠️ **CRITICAL: FILE SIZE LIMITS FOR CLAUDE CODE STABILITY** ⚠️

**Maximum File Size**: 500 lines (300-400 lines recommended)
**Risk**: Files exceeding 500 lines can cause Claude Code to crash

**Script Files Status**:
- Most scripts in this directory are within safe limits
- Note: Some archived scripts may exceed limits but are not actively used

**Best Practices for Scripts**:
1. Keep utility scripts focused and single-purpose
2. Split complex scripts into modules
3. Use configuration files instead of hardcoding
4. Aim for scripts under 300 lines
</critical_file_size_warning>

<scripts_context_analysis>
You are working with diagnostic and maintenance tools. Before executing any scripts:

1. **Assess System State**: What is the current health and status of the system?
2. **Understand Script Purpose**: Diagnostic, maintenance, deployment, or migration?
3. **Check Prerequisites**: Are there dependencies or requirements to validate first?
4. **Evaluate Impact**: Will this script modify data, system state, or configuration?
5. **Plan Recovery**: Do you have rollback options if something goes wrong?
</scripts_context_analysis>

Scripts and utilities guidance for the MCP Task Orchestrator's diagnostic and maintenance tools.

## Scripts Architecture

**System Tools**: Comprehensive diagnostic, maintenance, and deployment utilities.

### Key Script Categories
- `diagnostics/` - System health checking and validation tools
- `maintenance/` - Database and task lifecycle management
- `deployment/` - Installation and configuration scripts
- `migrations/` - Database schema and data migration utilities

## Script Execution Decision Framework

<diagnostic_strategy_reasoning>
**Choose the Right Diagnostic Approach**:

**System Health Issues**:
- **First Step**: `python diagnostics/check_status.py` - Comprehensive overview
- **Database Problems**: `python diagnostics/diagnose_db.py` - Database-specific analysis
- **Installation Issues**: `python diagnostics/verify_tools.py` - Dependency validation
- **Performance Problems**: `python diagnose_timeout.py` - Timeout investigation

**Maintenance Operations**:
- **Database Migrations**: `python migrate_to_persistence.py` - Schema updates
- **System Cleanup**: Use orchestrator maintenance coordinator tools
- **Test Validation**: `python run_tests_alternative.py` - Alternative test execution

**Execution Safety Protocol**:
1. **Health Check First**: Always run `check_status.py` before major operations
2. **Backup Data**: Ensure data safety before destructive operations
3. **Validate Prerequisites**: Check dependencies and system requirements
4. **Monitor Execution**: Watch for errors and unexpected behavior
5. **Verify Results**: Confirm operations completed successfully

**Decision Process**:
1. **Identify Problem Type**: System health, performance, data, or configuration?
2. **Assess Urgency**: Emergency fix or routine maintenance?
3. **Choose Appropriate Tool**: Diagnostic vs maintenance vs migration script?
4. **Plan Execution**: Prerequisites, backup, execution, validation steps?
</diagnostic_strategy_reasoning>

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
