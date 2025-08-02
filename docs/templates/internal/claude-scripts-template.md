
# CLAUDE.md

**[CURRENT]** Claude Code guidance for Scripts and Utilities in MCP Task Orchestrator

⚠️ **File Size Compliant**: This file is kept under 400 lines for Claude Code stability

#
# Status Header

- **Status**: [CURRENT]

- **Context**: Automation Scripts and Utility Tools

- **Architecture Layer**: Infrastructure (automation and operations)

#
# Context Analysis

#
## Directory Purpose

Automation scripts and utility tools for development, maintenance, deployment, and operational tasks.

#
## Scope

- Diagnostic and health check utilities

- Maintenance and cleanup automation

- Release and deployment scripts

- Development workflow automation

- Testing and validation utilities

#
## Architectural Role

Provides operational support for the Clean Architecture by:

- Automating infrastructure maintenance tasks

- Providing diagnostic tools for system health

- Supporting deployment and release workflows

- Enabling development productivity tools

#
# Core Commands

#
## Essential Script Operations

```bash

# Health check and system diagnostics

python scripts/diagnostics/health_check.py

# System maintenance and cleanup

python scripts/maintenance/cleanup_database.py
python scripts/maintenance/optimize_performance.py

# Release automation

python scripts/release/pypi_release_simple.py
python scripts/release/prepare_release.py

# Development utilities

python scripts/validation/validate_architecture.py
python scripts/setup/setup_development_environment.py

```text

#
## Diagnostic Tools

```text
bash

# Comprehensive system health check

python scripts/diagnostics/system_health.py

# Database diagnostics

python scripts/diagnostics/database_health.py

# MCP protocol testing

python scripts/diagnostics/test_mcp_protocol.py

# Performance monitoring

python scripts/diagnostics/performance_analysis.py

```text

#
## Maintenance Operations

```text
bash

# Database maintenance

python scripts/maintenance/migrate_database.py
python scripts/maintenance/backup_database.py
python scripts/maintenance/cleanup_old_data.py

# File system maintenance

python scripts/maintenance/cleanup_temp_files.py
python scripts/maintenance/organize_documentation.py

```text

#
# Directory Structure

```text
bash
scripts/
├── diagnostics/            
# System health and analysis tools
│   ├── health_check.py    
# Comprehensive health checks
│   ├── performance_monitor.py  
# Performance analysis
│   └── test_mcp_protocol.py    
# MCP protocol testing
├── maintenance/            
# System maintenance and cleanup
│   ├── cleanup_database.py     
# Database maintenance
│   ├── migrate_database.py     
# Database migrations
│   └── optimize_system.py      
# Performance optimization
├── release/               
# Release and deployment automation
│   ├── pypi_release_simple.py  
# PyPI publishing
│   ├── prepare_release.py      
# Release preparation
│   └── validate_release.py     
# Release validation
├── validation/            
# Architecture and code validation
│   ├── validate_architecture.py    
# Clean architecture validation
│   ├── check_dependencies.py       
# Dependency analysis
│   └── lint_all.py                
# Code quality checks
├── setup/                 
# Development environment setup
│   ├── setup_development.py    
# Dev environment setup
│   ├── install_dependencies.py 
# Dependency installation
│   └── configure_tools.py      
# Tool configuration
└── CLAUDE.md             
# This file

```text

#
# Development Patterns

#
## Creating New Scripts

1. Follow Clean Architecture principles - scripts interact through application layer

2. Use dependency injection container for service access

3. Implement proper error handling and logging

4. Add validation and dry-run capabilities

5. Include comprehensive help and documentation

#
## Script Organization

- **diagnostics/**: Read-only analysis and monitoring tools

- **maintenance/**: Operational tasks that modify system state

- **release/**: Deployment and publishing automation

- **validation/**: Code quality and architecture validation

- **setup/**: Environment configuration and initialization

#
## Best Practices

- Use argparse for command-line interface consistency

- Implement proper logging with configurable levels

- Add dry-run mode for destructive operations

- Include progress indicators for long-running operations

- Validate inputs and provide clear error messages

#
# Integration Points

#
## MCP Tool Integration

- Scripts can use MCP Task Orchestrator tools for automation

- Diagnostic scripts validate MCP protocol implementation

- Maintenance scripts can orchestrate complex workflows

- Release scripts integrate with MCP tool validation

#
## Clean Architecture Integration

- Scripts access system through application layer use cases

- Diagnostic tools validate architectural compliance

- Maintenance scripts respect domain boundaries

- All scripts use dependency injection for service access

#
## Database Integration

- Maintenance scripts handle database migrations and cleanup

- Diagnostic scripts monitor database health and performance

- Backup scripts ensure data preservation

- Migration scripts handle schema evolution

#
# Troubleshooting

#
## Common Issues

- **Permission Errors**: Ensure scripts have proper file system permissions

- **Import Errors**: Check Python path and dependency installation

- **Database Lock**: Scripts may conflict with running server - stop server first

- **Configuration Issues**: Verify environment variables and configuration files

#
## Debugging Scripts

```text
bash

# Run script with verbose logging

python script_name.py --verbose

# Dry-run mode for destructive operations

python script_name.py --dry-run

# Debug mode with detailed output

python script_name.py --debug

# Check script dependencies

python scripts/validation/check_dependencies.py
```text

#
## Performance Considerations

- Use file-based output for scripts producing large amounts of data

- Implement progress indicators for user feedback

- Use batch operations for database modifications

- Include timeout handling for external service calls

#
# Cross-References

#
## Related CLAUDE.md Files

- **Main Guide**: [CLAUDE.md](../CLAUDE.md) - Essential quick-reference

- **Detailed Guide**: [CLAUDE-detailed.md](../CLAUDE-detailed.md) - Comprehensive architecture

- **Documentation Architecture**: [docs/CLAUDE.md](../docs/CLAUDE.md) - Complete documentation system

- **Core Package**: [mcp_task_orchestrator/CLAUDE.md](../mcp_task_orchestrator/CLAUDE.md) - Implementation details

- **Testing Guide**: [tests/CLAUDE.md](../tests/CLAUDE.md) - Testing infrastructure

#
## Related Documentation

- [Release Automation Guide](../docs/developers/contributing/PYPI_RELEASE_AUTOMATION.md)

- [Maintenance Procedures](../docs/users/troubleshooting/maintenance-operations.md)

- [Diagnostic Tools Guide](../docs/users/troubleshooting/diagnostic-tools.md)

#
# Quality Checklist

- [ ] File size under 400 lines for Claude Code stability

- [ ] Status header current and accurate

- [ ] All script categories properly documented

- [ ] Directory structure reflects current organization

- [ ] Commands tested and functional

- [ ] Cross-references accurate and up-to-date

- [ ] Development patterns reflect current best practices

- [ ] Script organization categories clearly defined

- [ ] Integration points completely documented

- [ ] Troubleshooting addresses real script issues

- [ ] Accessibility guidelines followed (proper heading hierarchy)

- [ ] Code blocks specify language (bash, python, yaml, etc.)

- [ ] Related documentation links verified

#
# Maintenance Notes

#
## Update Procedures

- Add new scripts following established directory structure

- Update script documentation when functionality changes

- Maintain consistency in command-line interface patterns

- Test scripts in development environment before deployment

#
## Validation Requirements

- All scripts must have proper error handling

- Destructive operations must have dry-run mode

- Scripts must validate inputs and provide clear error messages

- Database operations must use proper transaction management

- **Template Compliance**: Must pass `python scripts/validation/validate_template_compliance.py`

- **Cross-Reference Accuracy**: Must pass `python scripts/validation/validate_cross_references.py`

- **Style Guide Compliance**: Must follow [Style Guide](../style-guide.md) standards

- **Script Standards**: Follow established command-line interface patterns

#
## Dependencies

- Scripts depend on core package for business logic access

- Diagnostic scripts require monitoring and health check infrastructure

- Release scripts depend on PyPI configuration and credentials

- Maintenance scripts require appropriate system permissions

#
# Accessibility Notes

- **Heading Hierarchy**: Always follow proper H1 → H2 → H3 structure

- **Screen Reader Compatibility**: Use descriptive link text and alt text

- **Language Specification**: All code blocks must specify language

- **Consistent Navigation**: Cross-references enable logical navigation paths

- **Script Documentation**: Clear command descriptions and examples

---

📋 **These scripts provide operational support for the Clean Architecture system. See [CLAUDE.md](../CLAUDE.md) for essential commands, [Style Guide](../style-guide.md) for writing standards, and [CLAUDE-detailed.md](../CLAUDE-detailed.md) for comprehensive operational guidance.**
