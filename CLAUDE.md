# MCP Task Orchestrator - Claude Code Development Guide

<critical_file_size_warning>
⚠️ **CRITICAL: FILE SIZE LIMITS FOR CLAUDE CODE STABILITY** ⚠️

**Maximum File Size**: 500 lines (300-400 lines recommended)
**Risk**: Files exceeding 500 lines can cause Claude Code to crash or become unresponsive

**Current Status**: Multiple files in this codebase exceed safe limits:
- `generic_repository.py` (1180 lines) - CRITICAL
- `task_lifecycle.py` (1132 lines) - CRITICAL  
- `server.py` (764 lines) - HIGH RISK
- See full analysis in `.task_orchestrator/artifacts/researcher_3629b7/`

**Best Practices**:
1. Keep all files under 500 lines (ideally 300-400)
2. Split large files into focused modules
3. Use subdirectories for logical grouping
4. Maintain clear module interfaces
5. Update imports after refactoring

**If Working with Large Files**:
- Consider reading specific sections with offset/limit
- Refactor before making major changes
- Use the Task Orchestrator to plan modularization
</critical_file_size_warning>

<context_analysis>
You are working with the MCP Task Orchestrator project, a production-ready Python-based MCP server with advanced orchestration capabilities. Before taking any action, analyze the current situation:

1. What type of development task are you being asked to perform?
2. Which project area(s) will be affected?
3. What is the current git status and any recent changes?
4. Are there any critical system health indicators to check first?
</context_analysis>

## Project Overview

**Version**: 1.4.1 (stable, production-ready)  
**Architecture**: Python-based MCP server with SQLite persistence and enhanced features  
**Location**: `E:\My Work\Programming\MCP Servers\mcp-task-orchestrator`

<key_capabilities>
- **Task Orchestration**: Intelligent breakdown with specialized AI roles
- **Artifact Storage**: Context limit prevention for complex workflows
- **Maintenance Coordination**: Automated task lifecycle management
- **Enhanced Testing**: Advanced infrastructure with alternative runners
- **Feature Management**: 8 approved features with implementation roadmap
</key_capabilities>

## Pre-Development System Check

<reasoning_framework>
Before making any changes, follow this systematic approach:

1. **Health Assessment**: Run diagnostic check to understand current system state
2. **Git Status Review**: Ensure repository is clean and up-to-date
3. **Context Selection**: Choose appropriate directory context for your task
4. **Resource Validation**: Verify system resources and dependencies
</reasoning_framework>

### Critical System Diagnostics
```bash
# Step 1: Comprehensive health check (ALWAYS run first)
python scripts/diagnostics/check_status.py

# Step 2: Installation verification if issues found
python scripts/diagnostics/verify_tools.py

# Step 3: Database optimization for performance issues
python scripts/diagnostics/diagnose_db.py
```
<example_diagnostic_workflow>
**Scenario**: Starting a new development session

**Input**: "I want to add a new feature to the orchestrator"

**Reasoning Process**:
1. Check system health: `python scripts/diagnostics/check_status.py`
2. Review git status: `git status && git pull origin main`
3. Identify affected components: Core orchestrator? Database? Testing?
4. Choose context: `cd mcp_task_orchestrator` for core changes
5. Validate prerequisites: Dependencies, database schema, test status

**Output**: Ready to proceed with guided development in appropriate context
</example_diagnostic_workflow>

## Enhanced Development Workflows

<workflow_selection>
Choose your development context based on the task type:

**Universal Project Tasks** → Stay in root directory
- Project-wide changes, documentation updates, git operations
- Cross-component integration, release management

**Core Implementation** → `cd mcp_task_orchestrator && claude`
- Orchestrator logic, database operations, MCP protocol
- Performance optimization, new API endpoints

**Testing Development** → `cd tests && claude`
- Test infrastructure, validation suites, resource management
- Test debugging, performance benchmarking

**Documentation Work** → `cd docs && claude`
- Multi-audience documentation, API docs, user guides
- Architecture decisions, troubleshooting guides

**System Administration** → `cd scripts && claude`
- Diagnostic tools, maintenance scripts, deployment
- Database migrations, system health monitoring
</workflow_selection>

### Enhanced Testing Infrastructure
<testing_strategy>
**Preferred Approach**: Use enhanced test runners for reliability

**Primary Runners** (Use these first):
```bash
# Enhanced test runner with improved reliability
python simple_test_runner.py

# Comprehensive validation with detailed output
python test_validation_runner.py

# Resource management validation (prevents warnings)
python tests/test_resource_cleanup.py
```

**Traditional Fallback** (If enhanced runners fail):
```bash
# Standard pytest (may have truncation issues)
python -m pytest tests/ -v
```

**Reasoning**: Enhanced runners prevent output truncation, include hang detection, and provide better resource management than standard pytest.
</testing_strategy>

## Legal Protection Documentation Standards

<legal_liability_protection>
⚠️ **CRITICAL: DOCUMENTATION LEGAL RISK MANAGEMENT** ⚠️

**Legal Liability Score**: Current project documents score **7.5/10 HIGH RISK** for potential legal exposure in commercial environments.

**Problem**: Documentation contains warranty language that could trigger lawsuits if tools fail in high-stakes commercial environments where significant financial losses occur.

**Required Standards for ALL Documentation**:

### Prohibited Language (NEVER USE):
- **Absolute Claims**: "always", "never fails", "guaranteed", "100%", "eliminates", "prevents"
- **Completeness Warranties**: "complete reference", "comprehensive coverage", "total solution"
- **Performance Guarantees**: "optimal performance", "seamless integration", "robust handling"
- **Reliability Assertions**: "production-ready", "enterprise-grade" (without qualification)
- **Specification Compliance**: "follows all standards", "fully compliant" (without version/scope)

### Required Protective Language:
- **Qualifiers**: "designed to", "intended for", "typical conditions", "under normal use"
- **Scope Limitations**: "available features", "current implementation", "documented capabilities"
- **Conditional Performance**: "when properly configured", "in supported environments"
- **Version-Specific**: "as of version X.Y.Z", "subject to change"

### Mandatory Disclaimers for Documentation Categories:

**API Documentation**: "This documentation describes available functionality as implemented. Performance and compatibility may vary based on environment and usage patterns."

**User Guides**: "This software is provided 'as is' without warranties. Users should evaluate suitability for their specific use cases."

**Technical Specifications**: "Specifications subject to change. Verify current behavior through testing in your environment."

**Installation/Setup**: "Installation success depends on system configuration. Troubleshooting may be required for specific environments."
</legal_liability_protection>

### Documentation Writing Framework

<safe_documentation_patterns>
**Before Writing ANY Documentation**:

1. **Legal Risk Check**: Does this create warranties, guarantees, or absolute claims?
2. **Scope Definition**: Are we clearly limiting what we promise?
3. **User Context**: Could this be used in high-stakes commercial environments?
4. **Failure Scenarios**: What happens if this claim proves false?

**Safe Language Patterns**:
```
❌ RISKY: "This system prevents data loss"
✅ SAFE: "This system is designed to reduce risk of data loss"

❌ RISKY: "Complete API reference covering all features"  
✅ SAFE: "API reference for available features in version X.Y.Z"

❌ RISKY: "Guaranteed seamless integration"
✅ SAFE: "Designed for integration with supported MCP clients"

❌ RISKY: "Production-ready, enterprise-grade solution"
✅ SAFE: "Suitable for development and testing environments"
```

**Documentation Review Checklist**:
- [ ] No absolute language ("always", "never", "guaranteed")
- [ ] No unqualified performance claims
- [ ] Scope clearly defined and limited
- [ ] Appropriate disclaimers included
- [ ] Version/environment context provided
- [ ] Failure scenarios acknowledged where relevant
</safe_documentation_patterns>