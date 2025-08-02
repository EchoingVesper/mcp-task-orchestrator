
# CLAUDE.md

**[CURRENT]** Claude Code guidance for Architecture Documentation in MCP Task Orchestrator

⚠️ **File Size Compliant**: This file is kept under 400 lines for Claude Code stability

#
# Status Header

- **Status**: [CURRENT]

- **Last Updated**: 2025-01-08

- **Context**: Architecture Documentation and Design Decisions

- **Architecture Layer**: Documentation (cross-cutting architectural concerns)

#
# Context Analysis

#
## Directory Purpose

Comprehensive architecture documentation covering Clean Architecture implementation, design decisions, and system structure.

#
## Scope

- Clean Architecture design patterns and implementation guides

- Database schema documentation and enhancements

- System component architecture and interactions

- Design decision documentation and rationale

- Architectural pattern explanations and usage

#
## Architectural Role

Provides architectural guidance for the Clean Architecture implementation:

- Documents design decisions and their rationale

- Explains architectural patterns and their application

- Guides implementation across all system layers

- Ensures consistency in architectural approaches

#
# Critical File Size Warning

⚠️ **CRITICAL: FILE SIZE LIMITS FOR CLAUDE CODE STABILITY** ⚠️

**Maximum File Size**: 500 lines (300-400 lines recommended)
**Risk**: Files exceeding 500 lines can cause Claude Code to crash

**Architecture Files in THIS Directory Exceeding Limits**:

- `database-schema-enhancements.md` (694 lines) - HIGH RISK

- `nested-task-architecture.md` (554 lines) - MEDIUM RISK

**Architecture Documentation Best Practices**:

1. Split large architecture docs by component or layer

2. Use separate files for diagrams and detailed specs

3. Create overview files that link to detailed docs

4. Keep decision records concise (under 300 lines)

5. Use appendices for lengthy technical details

#
# Core Commands

#
## Architecture Validation

```bash

# Validate clean architecture compliance

python scripts/validation/validate_architecture.py

# Check architectural dependencies

python scripts/validation/check_dependencies.py --architecture

# Analyze file size compliance

python scripts/validation/check_file_sizes.py docs/developers/architecture/

# Validate documentation structure

python scripts/validation/validate_documentation.py

```text

#
## Architecture Analysis

```text
bash

# Generate architecture overview

python tools/diagnostics/architecture_analysis.py

# Analyze layer dependencies

python tools/diagnostics/dependency_analysis.py --layers

# Check design pattern compliance

python tools/diagnostics/pattern_analysis.py

# Validate database schema

python tools/diagnostics/schema_analysis.py

```text

#
## Documentation Maintenance

```text
bash

# Update architecture documentation

python scripts/maintenance/update_architecture_docs.py

# Validate cross-references

python scripts/validation/check_architecture_links.py

# Generate architecture diagrams

python scripts/documentation/generate_diagrams.py

```text

#
# Directory Structure

```text
bash
docs/developers/architecture/
├── overview.md                              
# High-level architecture overview
├── clean-architecture-guide.md             
# Clean Architecture implementation
├── database-schema-enhancements.md         
# Database design (694 lines - needs splitting)
├── nested-task-architecture.md             
# Task system design (554 lines - needs splitting)
├── generic-task-implementation-guide.md    
# Generic task patterns
├── decision-documentation-framework.md     
# ADR framework
├── tool-naming-conventions.md              
# Tool naming standards
├── workspace-paradigm-implementation-guide.md  
# Workspace patterns
├── operations/
│   └── reboot-operations.md               
# System restart architecture
└── CLAUDE.md                              
# This file

```text

#
# Development Patterns

#
## Creating Architecture Documentation

1. Follow Architecture Decision Record (ADR) format for decisions

2. Include context, problem statement, and solution rationale

3. Document alternatives considered and trade-offs

4. Maintain file size under 500 lines (split if necessary)

5. Include implementation examples and patterns

#
## Architecture Review Process

1. Review architectural decisions against clean architecture principles

2. Validate layer separation and dependency direction

3. Ensure documentation accuracy and completeness

4. Check for compliance with established patterns

5. Update cross-references and related documentation

#
## Documentation Organization

- **Overview Files**: High-level summaries linking to detailed docs

- **Component Files**: Specific architectural components and patterns

- **Decision Files**: Architecture Decision Records (ADRs)

- **Implementation Files**: Detailed implementation guidance

- **Pattern Files**: Reusable architectural patterns

#
# Integration Points

#
## Clean Architecture Integration

- **Domain Layer**: Document business logic and entity design

- **Application Layer**: Document use case orchestration patterns

- **Infrastructure Layer**: Document implementation patterns and adapters

- **Presentation Layer**: Document interface design and protocols

#
## Documentation Architecture Integration

- Links to main documentation architecture guide

- Cross-references with implementation-specific CLAUDE.md files

- Integration with testing documentation for validation

- Coordination with operational documentation in scripts/

#
## Design Decision Integration

- Architecture Decision Records (ADRs) document major decisions

- Decision documentation framework ensures consistency

- Integration with implementation guides for practical application

- Cross-referencing with related architectural concerns

#
# Troubleshooting

#
## Common Issues

- **File Size Violations**: Split large files into focused components

- **Broken Cross-References**: Validate links when restructuring documentation

- **Outdated Patterns**: Regular review against current implementation

- **Inconsistent Terminology**: Maintain architectural vocabulary consistency

#
## Debugging Architecture Issues

```text
bash

# Check architectural compliance

python tools/diagnostics/architecture_compliance.py

# Validate design patterns

python tools/diagnostics/pattern_validation.py

# Analyze dependency violations

python tools/diagnostics/dependency_violations.py

# Check documentation consistency

python scripts/validation/documentation_consistency.py
```text

#
## Performance Considerations

- Keep documentation files under 500 lines for Claude Code stability

- Use overview files with links for large architectural topics

- Organize by architectural layer and component for clarity

- Maintain clear separation between different architectural concerns

#
# Cross-References

#
## Related CLAUDE.md Files

- **Main Guide**: [CLAUDE.md](../../../CLAUDE.md) - Essential quick-reference

- **Detailed Guide**: [CLAUDE-detailed.md](../../../CLAUDE-detailed.md) - Comprehensive architecture

- **Documentation Architecture**: [docs/CLAUDE.md](../../CLAUDE.md) - Complete documentation system

- **Core Package**: [mcp_task_orchestrator/CLAUDE.md](../../../mcp_task_orchestrator/CLAUDE.md) - Implementation details

- **Testing Guide**: [tests/CLAUDE.md](../../../tests/CLAUDE.md) - Architecture validation testing

#
## Related Documentation

- [Clean Architecture Guide](./clean-architecture-guide.md) - Implementation patterns

- [Database Schema Documentation](./database-schema-enhancements.md) - Data architecture

- [Generic Task Implementation](./generic-task-implementation-guide.md) - Task system architecture

- [Decision Documentation Framework](./decision-documentation-framework.md) - ADR guidelines

#
# Maintenance Notes

#
## Update Procedures

- Review architecture documentation quarterly for accuracy

- Update when significant architectural changes are made

- Validate cross-references when restructuring files

- Ensure file size compliance when adding content

#
## Validation Requirements

- All architectural decisions must be documented with rationale

- Implementation guides must align with actual system implementation

- Cross-references must be accurate and current

- File sizes must comply with Claude Code limitations

#
## Dependencies

- Clean Architecture implementation in core package

- Design decision framework for consistency

- Documentation architecture for integration

- Implementation guides for practical application

---

📋 **This architecture documentation guides Clean Architecture implementation. See [CLAUDE.md](../../../CLAUDE.md) for essential commands and [docs/CLAUDE.md](../../CLAUDE.md) for complete documentation architecture.**
