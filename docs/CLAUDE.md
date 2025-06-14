# Documentation Development - Claude Code Guide

<critical_file_size_warning>
⚠️ **CRITICAL: FILE SIZE LIMITS FOR CLAUDE CODE STABILITY** ⚠️

**Maximum File Size**: 500 lines (300-400 lines recommended)
**Risk**: Files exceeding 500 lines can cause Claude Code to crash

**Documentation Files in THIS Directory Exceeding Limits**:
- `examples/generic-task-usage-guide.md` (1172 lines) - CRITICAL
- `prompts/features/proposed/[RESEARCH]_mcp_tools_suite_expansion.md` (1065 lines) - CRITICAL
- `prompts/features/proposed/[RESEARCH]_bidirectional_persistence_system.md` (877 lines) - HIGH RISK
- `examples/migration-examples.md` (853 lines) - HIGH RISK
- `API_REFERENCE.md` (838 lines) - HIGH RISK
- Multiple other files 500-800 lines

**Documentation Refactoring Guidelines**:
1. Split large guides into topic-focused sections
2. Create subdirectories for multi-part documentation
3. Use index files for navigation
4. Keep individual doc files under 400 lines
5. Consider separate files for code examples
</critical_file_size_warning>

<documentation_context_analysis>
You are working within the multi-audience documentation system. Before proceeding with documentation work:

1. **Identify Target Audience**: Human users, LLM agents, or technical developers?
2. **Determine Documentation Type**: User guides, API docs, architecture decisions, or troubleshooting?
3. **Check Content Requirements**: Character limits for LLM docs, format standards, cross-references?
4. **Validate Current Structure**: How does this fit with existing documentation architecture?
5. **Consider Integration**: How will this documentation be discovered and used?
</documentation_context_analysis>

Documentation-specific guidance for the MCP Task Orchestrator project's comprehensive documentation system.

## Documentation Strategy Framework

<documentation_decision_framework>
**Choose Documentation Approach Based on Purpose**:

**Human-Readable Documentation** (`user-guide/`):
- **When**: End-user facing content, tutorials, getting started guides
- **Style**: Clear structure, progressive disclosure, practical examples
- **Length**: No strict limits, optimize for clarity and completeness
- **Format**: Descriptive headings, visual aids, step-by-step workflows

**LLM-Optimized Documentation** (`llm-agents/`):
- **When**: AI assistant integration, Claude Code contexts, tool documentation
- **Style**: Dense information, maximum utility per character
- **Length**: 1200-2000 characters per file (strict requirement)
- **Format**: Structured sections, consistent formatting, tool integration focus

**Architecture Documentation** (`architecture/`):
- **When**: Design decisions, technical specifications, system design
- **Style**: Decision records with context, alternatives, and consequences
- **Length**: Comprehensive but focused, document the "why" not just "what"
- **Format**: Problem/solution/rationale structure

**Decision Process**:
1. **Identify Primary Users**: Who will consume this documentation?
2. **Determine Access Pattern**: How will users discover and use this content?
3. **Assess Update Frequency**: How often will this need maintenance?
4. **Consider Integration Needs**: Does this link to other documentation?
</documentation_decision_framework>

## Documentation Architecture

**Multi-Audience Design**: This project serves both human users and LLM agents with specialized documentation.

### Audience-Specific Areas
- `user-guide/` - Human-readable guides and tutorials
- `llm-agents/` - AI-optimized documentation (1200-2000 chars)
- `architecture/` - System design and decision records
- `testing/` - Testing documentation and best practices
- `troubleshooting/` - Issue resolution guides
- `prompts/features/` - Feature lifecycle management

## Documentation Context Commands

### Core Documentation Tasks
```bash
# Comprehensive documentation status
cat INDEX.md

# Test documentation completeness
python ../tests/test_example_file_creation.py

# Validate cross-references
grep -r "docs/" . --include="*.md" | head -20

# Check documentation consistency
python ../scripts/diagnostics/check_status.py
```

### Content Validation
```bash
# Check all markdown files for broken links
find . -name "*.md" -exec echo "=== {} ===" \; -exec head -5 {} \;

# Documentation structure analysis
tree -I "__pycache__|*.pyc" -L 3

# Content length validation for LLM docs
find llm-agents/ -name "*.md" -exec wc -c {} \;
```

## Writing Guidelines

### Human-Readable Documentation (`user-guide/`)
- **Clear structure**: Use descriptive headings and logical flow
- **Practical examples**: Include real-world usage scenarios
- **Progressive disclosure**: Start simple, build complexity
- **Visual aids**: Use code blocks, tables, and diagrams where helpful

### LLM-Optimized Documentation (`llm-agents/`)
- **Character limits**: 1200-2000 characters per file
- **Dense information**: Maximum utility per character
- **Clear structure**: Well-defined sections with consistent formatting
- **Tool integration**: Optimized for Claude Code and other MCP tools

### Architecture Documentation (`architecture/`)
- **Decision records**: Document why, not just what
- **Context preservation**: Include problem statement and alternatives
- **Future considerations**: Note potential changes and impacts
- **Diagrams**: Use text-based diagrams when possible

## Documentation Patterns

### Feature Documentation Workflow
1. **Research** → Analysis in `prompts/features/proposed/`
2. **Specification** → Detailed specs in `prompts/features/approved/`
3. **Implementation** → Progress tracking in `prompts/features/in-progress/`
4. **Documentation** → User guides and API docs
5. **Validation** → Testing and cross-reference verification

### Content Update Process
```bash
# 1. Update relevant documentation
# 2. Run documentation validation
python ../tests/validation_suite.py

# 3. Check cross-references
grep -r "$(basename $PWD)" ../README.md ../CLAUDE.md

# 4. Test with orchestrator
cd ..
python simple_test_runner.py
```

## Documentation Testing

### Automated Validation
- **Content testing**: `test_example_file_creation.py` validates documentation completeness
- **Cross-reference checking**: Automated link validation
- **Format validation**: Markdown syntax and structure checks
- **Length validation**: Character count verification for LLM docs

### Manual Quality Checks
- **Accuracy**: Verify all commands and examples work
- **Clarity**: Ensure concepts are clearly explained
- **Completeness**: Check coverage of all features and use cases
- **Consistency**: Maintain consistent style and terminology

## Integration with Development

### Documentation-Driven Development
- **Feature specs first**: Document features before implementation
- **API documentation**: Maintain alongside code changes
- **Testing documentation**: Update procedures with new test patterns
- **Troubleshooting**: Document known issues and solutions

### Orchestrator Integration
- **Multi-specialist approach**: Use documenter, reviewer, and tester specialists
- **Artifact storage**: Leverage artifact system for complex documentation projects
- **Context continuity**: Use directory-specific guidance for focused work

## Best Practices

### Content Organization
- **Logical hierarchy**: Organize content by user workflow
- **Cross-references**: Link related concepts and procedures
- **Maintenance**: Regular review and update cycles
- **Version control**: Track changes with descriptive commit messages

### Quality Standards
- **Technical accuracy**: All examples must be tested and working
- **Accessibility**: Clear language and good information architecture
- **Maintainability**: Structured for easy updates and extensions
- **User-focused**: Written from the user's perspective and needs

## Common Documentation Tasks

### Creating New Documentation
```bash
# Check existing structure
cat INDEX.md

# Create new document with proper header
echo "# New Document Title" > new-doc.md
echo "" >> new-doc.md
echo "Brief description..." >> new-doc.md

# Update index and cross-references
# Add to INDEX.md navigation
# Update related documents with links
```

### Updating Existing Documentation
```bash
# Check current content
head -20 existing-doc.md

# Verify impact of changes
grep -r "existing-doc" . --include="*.md"

# Update cross-references after changes
# Test all examples and commands
```

---

**Specialized Documentation**: This directory contains comprehensive, multi-audience documentation. Use orchestrator specialists for complex documentation projects.
