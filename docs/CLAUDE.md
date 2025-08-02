
# Documentation Architecture Guide

**[CURRENT]** Comprehensive documentation system for MCP Task Orchestrator

⚠️ **File Size Compliant**: This file is kept under 450 lines for Claude Code stability

#
# Overview

The MCP Task Orchestrator implements a sophisticated, multi-layered documentation architecture designed to serve three distinct audiences while maintaining architectural consistency and cross-referential integrity.

#
## Documentation Philosophy

- **Multi-Audience Design**: Serves human users, LLM agents, and technical developers

- **Architecture Alignment**: Documentation structure mirrors the Clean Architecture implementation

- **Modular System**: Distributed CLAUDE.md ecosystem with standardized templates

- **Cross-Reference Network**: Comprehensive linking system for efficient navigation

- **Compliance First**: All files respect Claude Code's 500-line limit for stability

#
# Dual-Audience Architecture

#
## Primary Audience Separation

#
### `docs/users/` - Human-Oriented Documentation

**Target Audience**: End users, integrators, system administrators

**Content Focus**:

- Installation and setup guides

- Usage patterns and examples

- Troubleshooting and diagnostics

- Real-world implementation scenarios

- Quick-start and getting-started content

**Organization Pattern**:

```bash
docs/users/
├── quick-start/          
# Immediate onboarding
├── guides/               
# Comprehensive usage guides
├── reference/            
# API and command reference
└── troubleshooting/      
# Problem resolution
```text

#
### `docs/developers/` - Technical Implementation Documentation

**Target Audience**: Contributors, maintainers, system architects

**Content Focus**:

- Clean Architecture implementation details

- Contribution guidelines and workflows

- Technical architecture decisions

- Development patterns and practices

- Internal system design documentation

**Organization Pattern**:
```text
bash
docs/developers/
├── architecture/         
# System design and patterns
├── contributing/         
# Development workflows
├── planning/             
# Future development and roadmaps
└── integration/          
# System integration guides

```text

#
# CLAUDE.md Ecosystem

#
## Distributed CLAUDE.md System

The project maintains 6 specialized CLAUDE.md files, each serving specific development contexts:

#
### Core Files

1. **`/CLAUDE.md`** (219 lines) - Essential quick-reference and navigation hub

2. **`/CLAUDE-detailed.md`** (389 lines) - Comprehensive architecture and development practices

#
### Context-Specific Files

3. **`docs/developers/architecture/CLAUDE.md`** (186 lines) - Architecture documentation context

4. **`mcp_task_orchestrator/CLAUDE.md`** (91 lines) - Core package implementation guide

5. **`tests/CLAUDE.md`** (124 lines) - Testing infrastructure and validation

6. **`scripts/CLAUDE.md`** (79 lines) - Automation and utility scripts

7. **`PRPs/CLAUDE.md`** (138 lines) - PRP framework and development workflows

#
## CLAUDE.md Design Principles

#
### Template-Driven Consistency

All CLAUDE.md files follow standardized templates ensuring:

- Consistent structure and navigation patterns

- Standardized status tracking ([CURRENT], [NEEDS-UPDATE], [DEPRECATED])

- Uniform cross-reference systems

- Architecture layer identification

- Maintenance procedure documentation

#
### Claude Code Compliance

- **File Size Limit**: All files under 500 lines (target 300-400 lines)

- **Modular Design**: Complex content split across multiple files

- **Cross-Reference Network**: Comprehensive linking prevents information silos

- **Quick Navigation**: Essential information accessible within 2-3 clicks

#
# Clean Architecture Integration

#
## Documentation Layers Mirror Software Layers

The documentation architecture directly reflects the 4-layer Clean Architecture:

#
### Domain Layer Documentation

- Business logic and domain concepts in `docs/developers/architecture/`

- Entity and value object documentation

- Domain service explanations and usage patterns

#
### Application Layer Documentation

- Use case workflows and orchestration patterns

- DTO documentation and API contracts

- Service integration guides

#
### Infrastructure Layer Documentation

- Database implementation details

- MCP protocol adapters and handlers

- Monitoring and diagnostic system documentation

#
### Presentation Layer Documentation

- MCP server configuration and usage

- CLI interface documentation

- Client integration guides

#
## Architectural Decision Documentation

Following the Architecture Decision Record (ADR) pattern:

- Decision rationale and context

- Alternatives considered

- Implementation consequences

- Maintenance implications

#
# Modular Documentation Patterns

#
## Red Hat Modular Documentation Approach

Implemented using industry-standard modular documentation principles:

#
### Content Types

1. **Concept Documentation**: Explains what something is and why it matters

2. **Procedure Documentation**: Step-by-step task completion guides

3. **Reference Documentation**: API specifications and command references

4. **Troubleshooting Documentation**: Problem diagnosis and resolution

#
### Reusable Modules

- **Snippet Includes**: Common command patterns and code examples

- **Template Systems**: Standardized CLAUDE.md and documentation templates

- **Cross-Reference Modules**: Consistent navigation and linking patterns

- **Validation Modules**: Shared compliance and quality assurance content

#
## Information Architecture

#
### Progressive Disclosure

Documentation organized from general to specific:

1. **Overview Level**: High-level concepts and navigation

2. **Guide Level**: Detailed implementation guidance

3. **Reference Level**: Comprehensive technical specifications

4. **Troubleshooting Level**: Problem-specific resolution guidance

#
### Context-Aware Navigation

- **Breadcrumb Systems**: Clear hierarchical navigation

- **Related Content**: Contextually relevant cross-references

- **Task-Oriented Linking**: Navigation optimized for specific workflows

- **Audience-Specific Paths**: Different entry points for different user types

#
# Status Tag System

#
## Documentation Lifecycle Management

All documentation uses standardized status tags:

#
### Status Classifications

- **[CURRENT]**: Up-to-date and actively maintained

- **[NEEDS-UPDATE]**: Requires revision due to system changes

- **[DEPRECATED]**: Legacy content maintained for reference

- **[DRAFT]**: Work-in-progress content

- **[ARCHIVED]**: Historical content moved to archives

#
### Maintenance Workflows

- **Regular Review Cycles**: Quarterly status validation

- **Change-Driven Updates**: Documentation updates triggered by code changes

- **Community Feedback Integration**: User-reported documentation issues

- **Automated Validation**: Scripts validate documentation consistency

#
# Navigation Enhancement System

#
## Cross-Reference Network

#
### Systematic Linking Architecture

Every CLAUDE.md file maintains bidirectional references:

- **Hierarchical Links**: Parent-child documentation relationships

- **Contextual Links**: Related content in different directories

- **Workflow Links**: Task-oriented navigation paths

- **Reference Links**: Quick access to specifications and APIs

#
### Navigation Patterns

```text
markdown

## Cross-References

#
## Related CLAUDE.md Files

- **Main Guide**: [CLAUDE.md](../CLAUDE.md) - Essential quick-reference

- **Detailed Guide**: [CLAUDE-detailed.md](../CLAUDE-detailed.md) - Comprehensive architecture

- **Documentation Architecture**: [docs/CLAUDE.md](../docs/CLAUDE.md) - Complete documentation system

#
## Related Documentation

- [Specific Technical Documentation]

- [Workflow-Specific Guides]

- [API References]

```text

#
# Maintenance and Automation

#
## Automated Validation System

#
### Documentation Compliance Checking

```text
bash

# Validate all CLAUDE.md files

python scripts/validation/validate_claude_md.py

# Check cross-reference accuracy

python scripts/validation/check_cross_references.py

# Validate file size compliance

python scripts/validation/check_file_sizes.py

# Status tag validation

python scripts/validation/check_status_tags.py
```text

#
### Quality Assurance Automation

- **Markdownlint Integration**: Automated markdown quality checking

- **Link Validation**: Broken link detection and reporting

- **Template Compliance**: Validation against standardized templates

- **Content Freshness**: Detection of outdated content based on system changes

#
## Update Procedures

#
### Documentation Update Workflows

1. **Code Change Integration**: Documentation updates triggered by code changes

2. **Template Evolution**: System-wide template updates with version control

3. **Cross-Reference Maintenance**: Automated link validation and correction

4. **Status Tag Management**: Regular review and status tag updates

#
### Maintenance Responsibilities

- **Core Team**: Overall architecture and template maintenance

- **Contributors**: Context-specific CLAUDE.md updates

- **Automated Systems**: Compliance validation and link checking

- **Community**: Feedback and improvement suggestions

#
# Usage Guidelines

#
## For Contributors

#
### Creating New CLAUDE.md Files

1. Use appropriate template from `docs/templates/`

2. Follow file size guidelines (under 400 lines)

3. Implement proper cross-reference network

4. Validate against template compliance requirements

5. Update navigation systems in related files

#
### Updating Existing Documentation

1. Check current status tag and update if necessary

2. Maintain cross-reference accuracy

3. Follow established architectural patterns

4. Validate against quality standards

5. Update maintenance notes

#
## For Users

#
### Efficient Documentation Navigation

1. **Start with Main CLAUDE.md**: Essential commands and quick navigation

2. **Use Context-Specific Guides**: Directory-specific CLAUDE.md files for detailed guidance

3. **Follow Cross-References**: Leverage linking system for related content

4. **Check Status Tags**: Ensure you're using current documentation

#
### Getting Help

- **Quick Reference**: Main CLAUDE.md for immediate needs

- **Comprehensive Guidance**: CLAUDE-detailed.md for complete implementation details

- **Context-Specific Help**: Directory-specific CLAUDE.md files

- **Troubleshooting**: Dedicated troubleshooting documentation in docs/users/

#
# Future Evolution

#
## Planned Enhancements

- **Interactive Documentation**: Enhanced navigation with dynamic cross-references

- **Search Integration**: Full-text search across all documentation

- **Version Control Integration**: Documentation versioning aligned with code releases

- **Community Contribution Tools**: Enhanced tools for community-driven documentation improvements

#
## Architectural Roadmap

- **Microservice Documentation**: Support for distributed system documentation

- **API Documentation Generation**: Automated API documentation from code

- **Testing Documentation Integration**: Enhanced integration between code and documentation testing

- **Internationalization Support**: Multi-language documentation architecture

---

📋 **This documentation architecture guide provides the foundation for the complete CLAUDE.md ecosystem. See [CLAUDE.md](../CLAUDE.md) for essential commands and individual directory CLAUDE.md files for context-specific guidance.**
