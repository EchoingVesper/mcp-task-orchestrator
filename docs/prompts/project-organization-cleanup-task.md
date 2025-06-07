# MCP Task Orchestrator Project Cleanup - Task Breakdown Prompt

## Project Context
**Project**: MCP Task Orchestrator (v1.6.0)  
**Location**: `/mnt/e/My Work/Programming/MCP Servers/mcp-task-orchestrator`  
**Current Health Score**: 10/100 (Critical - Immediate Action Required)

## Validated Current State Analysis ✅

**Root Directory Issues (Confirmed by validation script):**
- **60 root files** (target: ≤15) - 4x over limit
- **24 misplaced scripts** in root directory
- **22 misplaced documentation files** in root directory  
- **6 virtual environments** (target: 1) - 5 extra to remove
- **Build artifacts present**: build/, dist/, mcp_task_orchestrator.egg-info/

**Project Structure Metrics:**
- Documentation files: 193 total (need reorganization)
- Script files: 46 total (need categorization) 
- Test files: 65 total (properly organized)
- Missing directories: docs/releases, scripts/testing
- Missing .gitignore patterns for Claude Code compatibility

**Specific Files Requiring Relocation:**

*Misplaced Scripts (24 files):*
```
build_status.py, comprehensive_migration_test.py, execute_build.py, 
execute_pypi_build.py, execute_test_direct.py, final_validation_test.py, 
manual_build.py, migration_test_report_generator.py, quick_build_validate.py, 
run_build_inline.py, run_reboot_tests.py, server_migration_integration.py, 
simple_exec_build.py, standalone_migration_test.py, test_migration_system.py, 
test_reboot_comprehensive.py, test_reboot_tools.py, test_server_integration.py, 
validate_implementation.py, validate_release_ready.py, validate_server_integration.py
```

*Misplaced Documentation (22 files):*
```
CHANGE_LOG.md, CLAUDE.md, COMPREHENSIVE_MIGRATION_TEST_REPORT.md, 
COMPREHENSIVE_REBOOT_TEST_REPORT.md, IMPLEMENTATION_SUMMARY.md, 
INTEGRATION_GUIDE.md, MIGRATION_GUIDE.md, MIGRATION_SYSTEM_IMPLEMENTATION_SUMMARY.md, 
NEXT_STEPS.md, PR_PREPARATION_SUMMARY.md, PyPI_Release_1.6.0_Summary.md, 
pypi_release_summary.md, RELEASE_CHECKLIST.md, RELEASE_NOTES.md, 
RELEASE_NOTES_v1.4.0.md, REPOSITORY_CLEANUP_SUMMARY.md, TESTING_CHANGELOG.md, 
TESTING_GUIDELINES.md, TEST_ARTIFACTS_SUMMARY.md, test_report.md, 
VALIDATION_REPORT.md, WORKTREE_SETUP.md
```

## Task Orchestrator Request

"Initialize a new orchestration session and plan a comprehensive project organization cleanup for the MCP Task Orchestrator repository. 

**Current State (Pre-Validated):**
- Health Score: 10/100 (Critical)
- Root files: 60 (should be ≤15)
- 24 misplaced scripts cluttering root directory
- 22 misplaced documentation files in wrong locations
- 6 virtual environments (5 extras consuming disk space)
- Build artifacts (build/, dist/, *.egg-info/) need cleanup
- Missing directory structure (docs/releases, scripts/testing)
- Incomplete .gitignore for Claude Code compatibility

**Objective:** Transform this from a 10/100 health score to 95+ through systematic cleanup that preserves all functionality while creating professional project organization.

**Key Requirements:**
- Move all 24 misplaced scripts to appropriate scripts/ subdirectories
- Relocate all 22 misplaced documentation files to docs/ structure
- Remove 5 extra virtual environments (keep only venv_mcp)
- Clean all build artifacts and regenerate as needed
- Create missing directory structure
- Update .gitignore with Claude Code patterns (temp/, *-session.md)
- Validate functionality at each step (imports, tests, installer)
- Use Git properly (backup, atomic commits, history preservation)

**Success Criteria:**
- Root directory ≤15 files (down from 60)
- Health score ≥95/100
- All package functionality preserved
- Professional developer onboarding experience
- Automated validation tools in place

Break this down into specialist-driven subtasks with validation gates between phases. Each subtask should be executable safely with rollback capability."

## Expected Orchestration Breakdown

The task orchestrator should create specialist-driven subtasks covering:

### Phase 1: Infrastructure & Safety (Architect + Implementer)
- Git backup strategy and branch creation
- Create missing directory structure (docs/releases, scripts/testing)
- Validation checkpoint: Directory structure ready

### Phase 2: Build Cleanup (Implementer)
- Remove build artifacts (build/, dist/, *.egg-info/)
- Clean Python cache files (.pytest_cache, __pycache__)
- Test package import functionality
- Validation checkpoint: Clean build state

### Phase 3: Script Reorganization (Implementer)
- Categorize and move 24 misplaced scripts to scripts/ subdirectories
- Update any internal script references
- Test script functionality in new locations
- Validation checkpoint: Scripts properly organized

### Phase 4: Documentation Reorganization (Documenter + Implementer)
- Move 22 documentation files to appropriate docs/ subdirectories
- Handle duplicate files (CHANGE_LOG.md vs CHANGELOG.md)
- Update internal documentation links
- Validation checkpoint: Documentation well-organized

### Phase 5: Environment Cleanup (Implementer)
- Remove 5 extra virtual environments safely
- Verify venv_mcp remains functional
- Update .gitignore with Claude Code patterns
- Validation checkpoint: Clean environment state

### Phase 6: Testing & Validation (Tester)
- Run comprehensive test suite
- Test package installation process
- Verify all imports work correctly
- Test MCP server functionality
- Validation checkpoint: Full functionality preserved

### Phase 7: Automation & Monitoring (Implementer)
- Ensure project structure validator script works
- Create ongoing maintenance procedures
- Set up health monitoring tools
- Validation checkpoint: Automation in place

### Phase 8: Final Integration & Documentation (Reviewer + Documenter)
- Final health score validation (target: 95+)
- Create Claude Code session templates
- Document new project structure
- Git commit strategy and merge planning
- Validation checkpoint: Project ready for production

## Implementation Specifications

### Technical Requirements
- **Use WSL paths** (`/mnt/e/...`) for all file operations
- **Preserve Git history** throughout the process
- **Atomic operations** where possible to allow rollback
- **Validation after each phase** using the diagnostic script
- **Conventional commit messages** for all changes

### File Organization Targets
```
mcp-task-orchestrator/
├── [≤15 essential files in root]
├── docs/
│   ├── development/     # Implementation summaries, PR prep, etc.
│   ├── testing/         # Test reports, validation reports
│   ├── releases/        # Release notes by version
│   └── user-guide/      # User-facing documentation
├── scripts/
│   ├── build/           # Build, package, release scripts
│   ├── testing/         # Test runners, validation scripts
│   └── diagnostics/     # Health checks, validation tools
└── [existing source directories unchanged]
```

### Risk Mitigation
- **Comprehensive backup** before starting
- **Phase-by-phase validation** with rollback capability
- **Functionality testing** after each major change
- **Git branch strategy** for safe experimentation

### Success Metrics
- Health score improvement: 10 → 95+ (850%+ improvement)
- Root file reduction: 60 → ≤15 (75%+ reduction)
- Virtual environment cleanup: 6 → 1 (83% reduction)
- Professional project organization achieved
- Automated monitoring in place

## Context Dependencies
- Python 3.12.3 with python-is-python3 installed
- Git repository with active development history
- WSL environment for file operations
- Task orchestrator system functional and ready
- Diagnostic validation script operational