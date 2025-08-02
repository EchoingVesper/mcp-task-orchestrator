
# CLAUDE.md

**[CURRENT]** Claude Code guidance for PRP Framework in MCP Task Orchestrator

⚠️ **File Size Compliant**: This file is kept under 400 lines for Claude Code stability

#
# Status Header

- **Status**: [CURRENT]

- **Last Updated**: 2025-01-08

- **Context**: PRP (Product Requirement Prompt) Framework

- **Architecture Layer**: Presentation (development workflow automation)

#
# Context Analysis

#
## Directory Purpose

**Enhanced PRP (Product Requirement Prompt) Framework** - a systematic context engineering system for creating and executing comprehensive product requirements that enable AI agents to ship production-ready, secure code on the first pass using proven context engineering principles.

#
## Scope

- **Enhanced PRP Templates**: Security-first, prescriptive templates with context engineering

- **AI Documentation System**: Comprehensive ai_docs/ with MCP, database, and security patterns

- **Multi-Stage Validation Framework**: 5-stage validation with security and performance gates

- **Context Engineering Methodology**: Systematic approach to context gathering and organization

- **Security-First Design**: Integrated security considerations throughout all templates and validation

- **Reusable Patterns**: Common implementation patterns for async, database, and MCP development

#
## Architectural Role

Provides enhanced development workflow automation for the Clean Architecture by:

- **Context Engineering**: Systematic context gathering for superior AI code generation

- **Security-First Development**: Integrated security validation throughout the development lifecycle  

- **Multi-Stage Validation**: Comprehensive quality gates from syntax to production readiness

- **Prescriptive Implementation**: Detailed guidance with specific file paths and code patterns

- **Pattern Reusability**: Systematic documentation of proven implementation patterns

#
# Core Commands

#
## PRP Development Operations

```bash

# Create new PRP from template

claude prp create --template comprehensive

# Execute existing PRP

claude prp execute comprehensive-claude-md-ecosystem-overhaul

# Validate PRP structure

claude prp validate --file comprehensive-claude-md-ecosystem-overhaul.md

# Generate PRP summary

claude prp summarize --status completed

```text

#
## Template Operations

```text
bash

# List available PRP templates

claude template list

# Create custom template

claude template create --name custom-feature-template

# Validate template structure

claude template validate --template comprehensive-template.md

```text

#
## Integration Commands

```text
bash

# Integrate with MCP Task Orchestrator

claude orchestrator initialize --prp-mode

# Execute PRP with task orchestration

claude orchestrator execute --prp comprehensive-claude-md-ecosystem-overhaul

# Validate PRP completion

claude orchestrator validate --prp-status

```text

#
# Enhanced Directory Structure

```text
bash
PRPs/
├── ai_docs/                        
# ENHANCED: Systematic AI documentation
│   ├── mcp-protocol-patterns.md    
# MCP server implementation patterns
│   ├── database-integration-patterns.md 
# Async database patterns with SQLite
│   ├── security-patterns.md        
# Security validation and protection patterns
│   └── context-engineering-guide.md 
# Context engineering methodology
├── templates/                      
# ENHANCED: Security-first templates
│   ├── prp_base.md                
# Enhanced base template with security
│   ├── prp_base_enhanced.md       
# Prescriptive template with context engineering
│   ├── prp_base_typescript.md     
# TypeScript template
│   └── [other specialized templates]
├── validation/                     
# NEW: Multi-stage validation framework
│   ├── validation-framework.md    
# 5-stage validation methodology
│   └── security-validation.md     
# Security-specific validation procedures
├── patterns/                       
# NEW: Reusable implementation patterns
│   ├── async-patterns.md          
# Common async/await patterns
│   ├── database-patterns.md       
# Database integration patterns
│   └── mcp-tool-patterns.md       
# MCP tool implementation patterns
├── completed/                      
# Successfully implemented PRPs
├── examples/                       
# Example PRPs and implementations
└── CLAUDE.md                      
# This file

```text

#
# Context Engineering Principles

#
## "Context is King" Methodology

**Enhanced PRPs implement systematic context engineering for superior AI code generation:**

- **Comprehensive Context**: Include ALL necessary documentation, examples, patterns, and gotchas

- **Security-First Design**: Integrate security considerations throughout, not as afterthoughts  

- **Prescriptive Implementation**: Specify exact file paths, line numbers, and method signatures

- **Multi-Stage Validation**: Comprehensive validation gates with specific commands and expected outputs

- **Pattern Documentation**: Systematic documentation of reusable implementation patterns

#
## Context Engineering Commands

```text
bash

# Validate context completeness

python scripts/validate_context_completeness.py --prp your-prp.md

# Generate context summary

python scripts/generate_context_summary.py --prp your-prp.md

# Check security integration

python scripts/check_security_integration.py --prp your-prp.md

# Validate cross-references

python scripts/validate_cross_references.py --directory PRPs/

```text

#
## Enhanced Validation Framework

```text
bash

# Stage 1: Syntax & Security

ruff check . --fix && mypy src/ && bandit -r src/ && safety check

# Stage 2: Unit Testing with Security Focus  

pytest tests/unit/ -v --cov=src --cov-fail-under=80 -m security

# Stage 3: Integration & Database Testing

pytest tests/integration/ -v && python scripts/validate_database_schema.py

# Stage 4: Security & Performance Validation

python scripts/security_audit.py && python scripts/performance_benchmark.py

# Stage 5: Production Readiness Validation

python scripts/e2e_validation.py && python scripts/production_readiness_check.py

```text

#
# Development Patterns

#
## Creating New PRPs

1. Start with appropriate template from `PRPs/templates/`

2. Include comprehensive problem statement and context

3. Define clear success criteria and validation gates

4. Specify implementation approach and technical requirements

5. Add cross-references to related documentation and PRPs

#
## PRP Execution Workflow

1. **Analysis Phase**: Understand requirements and existing codebase

2. **Planning Phase**: Break down into manageable implementation steps

3. **Implementation Phase**: Follow clean architecture principles

4. **Testing Phase**: Validate against specified success criteria

5. **Completion Phase**: Move to completed/ folder with summary

#
## Validation-First Design

- All PRPs must include executable validation gates

- Success criteria must be measurable and testable

- Implementation must follow clean architecture principles

- Documentation must be updated as part of completion criteria

#
# Integration Points

#
## MCP Tool Integration

- PRPs integrate with MCP Task Orchestrator tools for execution

- Task orchestration provides systematic implementation approach

- Specialist roles can be assigned for complex PRPs

- Progress tracking through orchestrator status systems

#
## Clean Architecture Integration

- **Presentation Layer**: PRPs define user-facing requirements

- **Application Layer**: PRP execution workflows as use cases

- **Infrastructure Layer**: Template system and validation frameworks

- **Domain Layer**: Core PRP concepts and business logic

#
## Template System Integration

- Standardized PRP templates ensure consistency

- Template validation prevents structural issues

- Reusable components for common PRP patterns

- Integration with documentation architecture

#
# Core PRP Concepts

#
## PRP Framework Philosophy

**"PRP = PRD + curated codebase intelligence + agent/runbook"**

- **PRD (Product Requirements Document)**: Traditional requirement specification

- **Codebase Intelligence**: Deep understanding of existing architecture and patterns

- **Agent/Runbook**: Executable workflow for AI-driven implementation

#
## Command-Driven System

- **28+ pre-configured Claude Code commands** in `.claude/commands/`

- Commands organized by function:
  - `PRPs/` - PRP creation and execution workflows
  - `development/` - Core development utilities
  - `code-quality/` - Review and refactoring commands
  - `rapid-development/experimental/` - Parallel PRP creation
  - `git-operations/` - Conflict resolution and smart git operations

#
## Template-Based Methodology

- **PRP Templates** follow structured format with validation loops

- **Context-Rich Approach**: Every PRP includes comprehensive documentation, examples, and gotchas

- **Validation-First Design**: Each PRP contains executable validation gates

#
# Troubleshooting

#
## Common Issues

- **Template Validation Errors**: Check template structure and required sections

- **Incomplete Success Criteria**: Ensure all validation gates are clearly defined

- **Integration Failures**: Verify MCP Task Orchestrator compatibility

- **Documentation Inconsistencies**: Maintain cross-reference accuracy

#
## Debugging PRPs

```text
bash

# Validate PRP structure

claude prp validate --detailed --file prp-name.md

# Check completion criteria

claude prp status --validation-gates --file prp-name.md

# Verify integration

claude orchestrator health-check --prp-integration

# Review execution logs

claude prp logs --file prp-name.md --detailed
```text

#
## Performance Considerations

- Keep PRPs focused and manageable in scope

- Use incremental validation gates for large PRPs

- Maintain clear separation between analysis and implementation

- Document dependencies and prerequisites clearly

#
# Cross-References

#
## Related CLAUDE.md Files

- **Main Guide**: [CLAUDE.md](../CLAUDE.md) - Essential quick-reference

- **Detailed Guide**: [CLAUDE-detailed.md](../CLAUDE-detailed.md) - Comprehensive architecture

- **Documentation Architecture**: [docs/CLAUDE.md](../docs/CLAUDE.md) - Complete documentation system

- **Core Package**: [mcp_task_orchestrator/CLAUDE.md](../mcp_task_orchestrator/CLAUDE.md) - Implementation details

- **Testing Guide**: [tests/CLAUDE.md](../tests/CLAUDE.md) - Testing validation patterns

#
## Related Documentation

- [PRP Templates](./templates/) - Standardized PRP creation templates

- [Validation Workflows](../docs/developers/contributing/testing/TESTING_GUIDELINES.md) - PRP validation framework

- [AI Documentation](./ai_docs/) - Curated context for AI-driven development

#
# Maintenance Notes

#
## Update Procedures

- Update templates when new PRP patterns emerge

- Maintain validation gate consistency across all PRPs

- Keep AI documentation current with latest practices

- Review completed PRPs for pattern extraction

#
## Validation Requirements

- All PRPs must pass template validation

- Success criteria must be measurable and testable

- Integration with MCP Task Orchestrator must be verified

- Documentation cross-references must be accurate

#
## Dependencies

- Claude Code command system for PRP execution

- MCP Task Orchestrator for systematic implementation

- Template validation framework for quality assurance

- Documentation architecture for context integration

---

📋 **This PRP framework enables AI-driven development with the MCP Task Orchestrator. See [CLAUDE.md](../CLAUDE.md) for essential commands and [docs/CLAUDE.md](../docs/CLAUDE.md) for complete documentation architecture.**
