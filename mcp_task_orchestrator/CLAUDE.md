# Core Implementation - Claude Code Guide

<critical_file_size_warning>
⚠️ **CRITICAL: FILE SIZE LIMITS FOR CLAUDE CODE STABILITY** ⚠️

**Maximum File Size**: 500 lines (300-400 lines recommended)
**Risk**: Files exceeding 500 lines can cause Claude Code to crash

**Files in THIS Directory Exceeding Limits**:
- `db/generic_repository.py` (1180 lines) - CRITICAL - Needs immediate refactoring
- `orchestrator/task_lifecycle.py` (1132 lines) - CRITICAL - Needs immediate refactoring
- `orchestrator/generic_models.py` (786 lines) - HIGH RISK
- `server.py` (764 lines) - HIGH RISK
- `orchestrator/maintenance.py` (735 lines) - HIGH RISK
- `staging/manager.py` (711 lines) - HIGH RISK
- Multiple other files 500-700 lines

**Refactoring Priority**: Start with CRITICAL files before making changes
</critical_file_size_warning>

<implementation_context_analysis>
You are working within the core MCP Task Orchestrator implementation package. Before making any changes:

1. **Analyze Impact Scope**: Which components will be affected by your changes?
2. **Check Dependencies**: Are other modules dependent on what you're modifying?
3. **Validate Current State**: Is the orchestrator currently running or being tested?
4. **Consider Async Safety**: Will your changes introduce race conditions or resource leaks?
</implementation_context_analysis>

## Core Architecture Overview

**Orchestration Engine**: Core MCP server with SQLite persistence, async operations, and enhanced features.

<package_architecture>
```
mcp_task_orchestrator/
├── orchestrator/           # Core orchestration logic and state management
├── db/                     # Database persistence layer
├── testing/                # Enhanced testing infrastructure
├── monitoring/             # Diagnostics and health monitoring
└── config/                 # Configuration management
```
</package_architecture>

## Development Decision Framework

<implementation_reasoning>
When implementing new features or fixing issues, follow this systematic approach:

1. **Identify Component**: Which package area contains the relevant logic?
2. **Check Interfaces**: What are the existing API contracts and dependencies?
3. **Plan Changes**: How will modifications affect other components?
4. **Design Async Safety**: How to prevent race conditions and resource leaks?
5. **Test Strategy**: What testing approach will validate the changes?
</implementation_reasoning>

## Core Development Commands

<development_workflow>
**Server Operations**:
```bash
# Primary server launch (recommended)
python -m mcp_task_orchestrator.server

# Alternative launcher with enhanced features
python server.py

# Development mode with debugging
python -m mcp_task_orchestrator.server --debug
```

**Component Testing**:
```bash
# Test enhanced handlers integration
python -c "from enhanced_handlers import *; test_handlers()"

# Validate database persistence layer
python -c "from persistence import *; validate_persistence()"
```
</development_workflow>