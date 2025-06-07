# In-Context Server Reboot - Claude Code Development Guide

<worktree_context>
**Worktree Purpose**: In-Context Server Reboot Mechanism Implementation
**Branch**: feature/in-context-server-reboot
**Task ID**: task_2f047d36
**Priority**: CRITICAL - Development Velocity Blocker  
**Timeline**: 3 days implementation
</worktree_context>

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

<worktree_focus>
- **Graceful Shutdown**: State serialization and task suspension
- **Connection Preservation**: MCP client connection maintenance during reboot
- **State Restoration**: Seamless server restart with preserved state
- **Reboot Coordination**: Safe reboot triggers and confirmation mechanisms
- **Integration Support**: Coordination with migration system for automatic reboots
</worktree_focus>

## Active Task Status

**Current Subtasks** (ready to execute):
1. **architect_9e06a9**: Design server state serialization and graceful shutdown (6 hours)
2. **implementer_a8b5f3**: Implement graceful shutdown and state preservation (8 hours)
3. **implementer_dd2297**: Implement restart mechanism and state restoration (8 hours)
4. **implementer_9d9414**: Create reboot coordination and trigger mechanisms (4 hours)
5. **tester_953f91**: Test reboot scenarios and validate client preservation (6 hours)
6. **documenter_b80ca2**: Document reboot system and operational procedures (3 hours)

## Quick Start Commands

```bash
# Execute first architect task  
# Use MCP tool: mcp__task-orchestrator__orchestrator_execute_subtask
# Task ID: architect_9e06a9

# Check system health before starting
python scripts/diagnostics/check_status.py

# Test current server functionality
python -m mcp_task_orchestrator.server
```

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

### Git Worktrees for Parallel Development

<worktree_strategy>
**Use Worktrees for Isolated Development**: Multiple tasks simultaneously with complete code isolation

**What are Git Worktrees?**
- Multiple working directories sharing one Git repository
- Each worktree can have different branch checked out
- Perfect for parallel feature development without branch switching
- Complete file isolation between concurrent Claude Code instances

**Creating New Worktrees**:
```bash
# List existing worktrees
git worktree list

# Create new worktree for a feature
git worktree add worktrees/feature-name -b feature/feature-name

# Work in the new worktree
cd worktrees/feature-name && claude
```

**Worktree Development Workflow**:
1. **Create worktree**: `git worktree add worktrees/my-feature -b feature/my-feature`
2. **Develop in isolation**: Make changes without affecting other work
3. **Commit normally**: `git add . && git commit -m "feat: implement feature"`
4. **Push branch**: `git push -u origin feature/my-feature`
5. **Create PR**: `gh pr create` or via GitHub UI
6. **Clean up after merge**: `git worktree remove worktrees/my-feature`

**Benefits**:
- Complete isolation between Claude Code instances
- No branch switching conflicts or stashing needed
- Test different features simultaneously
- Parallel development on critical infrastructure

**Best Practices**:
- Use descriptive worktree names matching feature branches
- Keep worktrees in a dedicated `worktrees/` directory
- Clean up worktrees after PRs are merged
- Document active worktrees in your PR descriptions
</worktree_strategy>

<workflow_selection>
Choose your development context based on the task type:

**Parallel Development** → Use Git worktrees (RECOMMENDED for features)
- Multiple feature development simultaneously
- Critical infrastructure components
- Independent testing environments
- Example: `git worktree add worktrees/feature-name -b feature/feature-name`

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

### Git Worktree Commit and PR Workflow

<worktree_git_workflow>
**Managing Commits and PRs Across Multiple Worktrees**

**Key Concepts**:
- Each worktree operates independently on its own branch
- Commits in one worktree don't affect others
- Multiple PRs can exist simultaneously from different worktrees
- All worktrees share the same remote repository

**Commit Workflow for Each Worktree**:
```bash
# In worktree 1 (e.g., db-migration)
cd worktrees/db-migration
git add .
git commit -m "feat: implement database migration system"
git push -u origin feature/automatic-database-migration

# In worktree 2 (e.g., server-reboot) - SIMULTANEOUSLY!
cd worktrees/server-reboot
git add .
git commit -m "feat: implement server reboot mechanism"
git push -u origin feature/in-context-server-reboot
```

**Creating Pull Requests**:
```bash
# From any worktree
gh pr create --title "feat: Feature Name" --body "Description"

# Or manually via GitHub UI - each worktree branch gets its own PR
# PR #1: feature/automatic-database-migration → main
# PR #2: feature/in-context-server-reboot → main
```

**Viewing Work Across Worktrees**:
```bash
# From anywhere in the repository
git worktree list                    # Show all worktrees
git branch -a                        # Show all branches
git log --oneline --all --graph      # See commits from all worktrees
```

**After PR Merge - Cleanup**:
```bash
# Update main branch
cd /path/to/main/repository
git checkout main
git pull origin main

# Remove completed worktrees
git worktree remove worktrees/db-migration
git branch -d feature/automatic-database-migration

# Prune remote tracking branches
git remote prune origin
```

**Common Worktree Commands**:
```bash
git worktree list                    # List all worktrees
git worktree add <path> -b <branch>  # Create new worktree
git worktree remove <path>           # Remove worktree
git worktree prune                   # Clean up stale worktree data
```

**Important Notes**:
- Never force-remove worktrees with uncommitted changes
- Each worktree maintains its own index and working directory
- Worktrees are perfect for critical infrastructure work requiring isolation
- Document active worktrees in team communication
</worktree_git_workflow>

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

## PyPI Release Management

<pypi_release_workflow>
⚠️ **CRITICAL: PyPI Release Process** ⚠️

**Package Status**: This project is published to PyPI as `mcp-task-orchestrator`
**Current Version**: Check `setup.py` line 9 for current version

### Development Workflow (Unchanged)
- **Continue developing in this directory** - this is your source repository
- **Git operations remain the same** - commit, push, pull requests, branches
- **All development and testing happens here first**

### Release Process (NEW - Required for Version Updates)

**Before Creating Pull Requests for Version Releases:**

1. **Version Management** - Update version numbers in these files:
   ```bash
   # Update these files with new version (e.g., 1.5.2)
   setup.py                           # Line 9: version="X.Y.Z"
   pyproject.toml                     # version field
   mcp_task_orchestrator/__init__.py  # __version__ (if present)
   ```

2. **Build and Test Process:**
   ```bash
   # Activate PyPI virtual environment
   source venv_pypi/bin/activate
   
   # Build package distributions
   python setup.py sdist bdist_wheel
   
   # Test upload to TestPyPI first
   python scripts/release/upload.py --test
   
   # If test successful, upload to production PyPI
   python scripts/release/upload.py
   ```

3. **Git Release Tagging:**
   ```bash
   # After successful PyPI upload, tag the release
   git tag v1.5.2
   git push origin v1.5.2
   ```

### When to Trigger PyPI Release
- **Bug fixes requiring user updates**
- **New features ready for public use**
- **Security patches**
- **Major milestone releases**

### What NOT to Upload
- **Development/experimental changes**
- **Documentation-only updates**
- **Internal refactoring without user impact**
- **Work-in-progress features**

**Important**: PyPI uploads are permanent and cannot be deleted. Only upload stable, tested versions.
</pypi_release_workflow>