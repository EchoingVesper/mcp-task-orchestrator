# Claude Code Rules Structure Documentation

## Overview

The MCP Task Orchestrator project implements a comprehensive **Claude Code Rules Structure** that provides context-aware guidance for development work across different project areas. This system enables specialized development workflows through directory-specific guidance files.

## Architecture

### Core Components

**Main CLAUDE.md** (`/CLAUDE.md`)
- Universal project guidance and overview
- High-level commands and project structure
- Git workflow and repository management guidelines
- Integration with orchestrator tools and enhanced features

**Directory-Specific CLAUDE.md Files**
- Specialized guidance for specific development contexts
- Area-specific commands and best practices
- Integration patterns for each project domain
- Context-aware development workflows

## File Structure

```
mcp-task-orchestrator/
├── CLAUDE.md                           # Universal project guidance
├── docs/CLAUDE.md                      # Documentation development
├── tests/CLAUDE.md                     # Enhanced testing infrastructure
├── scripts/CLAUDE.md                   # System utilities and diagnostics
├── mcp_task_orchestrator/CLAUDE.md     # Core implementation
└── architecture/CLAUDE.md              # Architecture documentation
```

## Usage Patterns

### Universal Context (`cd project_root && claude`)
Access comprehensive project guidance:
- Project overview and version information
- System diagnostic commands
- Git workflow and repository management
- Enhanced testing and development server commands
- Architecture overview and troubleshooting

### Specialized Context (`cd <directory> && claude`)
Access area-specific guidance:
- **Documentation**: `cd docs && claude` for multi-audience documentation workflows
- **Testing**: `cd tests && claude` for enhanced testing procedures
- **Scripts**: `cd scripts && claude` for diagnostic and maintenance tools
- **Core**: `cd mcp_task_orchestrator && claude` for orchestrator development
- **Architecture**: `cd architecture && claude` for design documentation

## Directory-Specific Features

### Documentation Directory (`docs/CLAUDE.md`)
**Focus**: Multi-audience documentation development
- Documentation architecture guidance (user-guide, llm-agents, architecture areas)
- Content validation commands and testing procedures
- Writing guidelines for different audience types (human vs LLM-optimized)
- Feature documentation workflow patterns
- Quality standards and cross-reference management

**Key Commands**:
```bash
# Documentation status
cat INDEX.md

# Test documentation completeness
python ../tests/test_example_file_creation.py

# Validate cross-references
grep -r "docs/" . --include="*.md"
```

### Testing Directory (`tests/CLAUDE.md`)
**Focus**: Enhanced testing infrastructure
- Enhanced test runners (alternative to pytest)
- File-based output system guidance
- Resource management best practices
- Testing patterns with managed connections
- Integration with orchestrator testing specialists

**Key Commands**:
```bash
# Enhanced test runners (preferred)
python simple_test_runner.py
python test_validation_runner.py

# Resource management validation
python test_resource_cleanup.py

# Hang detection testing
python test_hang_detection.py
```

### Scripts Directory (`scripts/CLAUDE.md`)
**Focus**: System utilities and diagnostics
- Diagnostic command reference (health checks, verification, database analysis)
- Performance and troubleshooting utilities
- Installation and setup scripts
- Script development patterns and safety guidelines
- Maintenance coordination integration

**Key Commands**:
```bash
# System health checking
python diagnostics/check_status.py
python diagnostics/verify_tools.py
python diagnostics/diagnose_db.py
```

### Core Implementation Directory (`mcp_task_orchestrator/CLAUDE.md`)
**Focus**: Core orchestration engine development
- MCP server implementation patterns
- Async safety guidelines and database operations
- SQLAlchemy ORM usage patterns
- Orchestration logic and specialist assignment
- Error handling and recovery mechanisms

**Key Commands**:
```bash
# Run the MCP server
python -m mcp_task_orchestrator.server

# Database connectivity testing
python -c "from db.persistence import get_db_connection; get_db_connection()"
```

### Architecture Directory (`architecture/CLAUDE.md`)
**Focus**: Design decisions and technical records
- Architecture documentation patterns
- Decision record structure and guidelines
- Design analysis commands
- System integration documentation
- Component relationship analysis

**Key Commands**:
```bash
# Review current architecture
find . -name "*.md" -exec echo "=== {} ===" \; -exec head -10 {} \;

# Check decision records
grep -r "Decision:" . --include="*.md"
```

## Development Workflow Integration

### Context-Aware Development
The Claude Code Rules Structure enables context-aware development by providing specialized guidance based on the current working directory:

1. **Universal Context**: Start with main CLAUDE.md for project overview
2. **Specialized Context**: Navigate to specific directories for focused work
3. **Cross-Reference**: Files reference each other and main documentation
4. **Tool Integration**: Commands optimized for each directory's specific needs

### Orchestrator Integration
All directory-specific files integrate with the MCP Task Orchestrator system:
- **Specialist Assignment**: Each directory aligns with specific orchestrator specialists
- **Artifact Storage**: Compatible with the artifact storage system for complex work
- **Maintenance Coordination**: Integrates with maintenance coordinator tools
- **Enhanced Testing**: Leverages the project's enhanced testing infrastructure

## Maintenance Procedures

### File Maintenance
- **Regular Updates**: Update directory-specific files when project structure changes
- **Command Validation**: Verify all commands work correctly in their respective directories
- **Cross-Reference Checking**: Ensure links and references remain accurate
- **Consistency Maintenance**: Keep formatting and structure consistent across files

### Content Validation Process
```bash
# Test all directory-specific commands
cd docs && python ../tests/test_example_file_creation.py
cd tests && python simple_test_runner.py
cd scripts && python diagnostics/check_status.py
cd mcp_task_orchestrator && python -m mcp_task_orchestrator.server --test
cd architecture && find . -name "*.md" -exec head -5 {} \;
```

### Quality Assurance
- **Accuracy**: All commands and examples must be tested and working
- **Completeness**: Coverage of all major development patterns and use cases
- **Clarity**: Concepts clearly explained with practical examples
- **Consistency**: Consistent style and terminology across all files

## Best Practices

### Usage Recommendations
1. **Start Universal**: Begin with main CLAUDE.md for project context
2. **Navigate Specifically**: Use `cd <directory> && claude` for focused work
3. **Reference Cross-Files**: Leverage cross-references between files
4. **Validate Commands**: Test commands before relying on them in workflows

### Development Guidelines
- **Context-Specific Work**: Use appropriate directory for the type of work
- **Tool Integration**: Leverage directory-specific command optimizations
- **Orchestrator Usage**: Use orchestrator specialists aligned with directory focus
- **Documentation Maintenance**: Update files when making structural changes

### Integration Patterns
- **Multi-Directory Projects**: Use orchestrator for work spanning multiple areas
- **Specialist Assignment**: Align work with appropriate directory and specialist
- **Artifact Storage**: Leverage artifact system for complex, multi-context work
- **Enhanced Testing**: Use enhanced testing infrastructure for validation

## Troubleshooting

### Common Issues
- **Command Failures**: Verify working directory and path contexts
- **Missing Context**: Ensure you're in the correct directory for specialized guidance
- **Outdated Information**: Check file modification dates and update as needed
- **Cross-Reference Errors**: Validate links when project structure changes

### Resolution Steps
1. **Verify Context**: Confirm current working directory
2. **Check Updates**: Ensure files are current with project changes
3. **Test Commands**: Validate commands in clean environment
4. **Cross-Reference**: Check related files for consistency

---

**Maintenance**: This structure requires regular maintenance to stay current with project evolution. Update files when making structural changes to the project.
