# Root Directory Cleanup Plan for v2.0.0

**Document Type**: Cleanup Strategy  
**Version**: 2.0.0  
**Created**: 2025-01-28  
**Status**: Active Planning

## Current State Analysis

### Root Directory Issues Identified

1. **Release Notes Clutter**: Multiple RELEASE_NOTES files in root
2. **Test File Pollution**: test_*.py files in root should be in tests/
3. **Duplicate Directory Structures**: Legacy directories duplicated with clean architecture
4. **Planning Content Scattered**: planning/ in root separate from docs/planning/
5. **Architecture Content Scattered**: architecture/ in root separate from docs/architecture/

## Root Directory Audit

### Files to Relocate

#### Release Documentation
```bash
# Move to docs/releases/
RELEASE_NOTES_v1.7.1.md → docs/releases/
RELEASE_NOTES_v1.8.0.md → docs/releases/
DEPENDENCY_FIX_SUMMARY.md → docs/releases/ (or archive if obsolete)
```

#### Test Files (Move to tests/)
```bash
test_dependency_check.py → tests/unit/
test_working_directory.py → tests/unit/
test_workspace_edge_cases.py → tests/unit/
test_workspace_functionality.py → tests/unit/
test_workspace_mcp_integration.py → tests/integration/
```

#### Planning Content Consolidation
```bash
# Merge planning/ into docs/planning/
planning/development-cycle-planning.md → docs/planning/
planning/feature-specifications.md → docs/planning/
planning/version-progression-plan.md → docs/planning/
planning/testing-strategy.md → docs/planning/
planning/task-cleanup-analysis.md → docs/archives/historical/
planning/files-created-this-session.md → docs/archives/historical/
planning/file-tracking-implementation-roadmap.md → docs/planning/

# Remove empty planning/ directory
```

#### Architecture Content Consolidation
```bash
# Merge architecture/ into docs/architecture/
architecture/a2a-framework-integration.md → docs/architecture/
architecture/database-schema-enhancements.md → docs/architecture/
architecture/generic-task-database-design.md → docs/architecture/
architecture/nested-task-architecture.md → docs/architecture/
# (and other architecture files)

# Remove empty architecture/ directory
```

#### Archive Content Consolidation
```bash
# Merge archives/ into docs/archives/
archives/README.md → docs/archives/
archives/analysis-reports/ → docs/archives/historical/
archives/development-scripts/ → docs/archives/historical/
archives/historical-docs/ → docs/archives/historical/
archives/task_cleanup/ → docs/archives/historical/

# Remove empty archives/ directory
```

### Duplicate Directory Analysis

**Problem**: Legacy directories from pre-refactoring exist alongside clean architecture versions

#### Duplicate Structures Found:
```
ROOT LEVEL          vs    CLEAN ARCHITECTURE
orchestrator/       vs    mcp_task_orchestrator/orchestrator/
reboot/            vs    mcp_task_orchestrator/reboot/
staging/           vs    mcp_task_orchestrator/staging/
monitoring/        vs    mcp_task_orchestrator/monitoring/
```

#### Resolution Strategy:
1. **Verify Clean Architecture is Complete**: Ensure all functionality moved to mcp_task_orchestrator/
2. **Check for Active References**: Scan codebase for imports/references to root-level directories
3. **Gradual Removal**: Remove root-level duplicates after verification

### Legacy Files Analysis

#### Files to Investigate for Removal:
```bash
__init__.py                    # Likely legacy, should be in mcp_task_orchestrator/
__main__.py                    # Likely legacy, should be in mcp_task_orchestrator/
server.py                      # Likely legacy, clean version in mcp_task_orchestrator/
persistence.py                 # Likely legacy, clean version in mcp_task_orchestrator/
persistence_factory.py        # Likely legacy, clean version in mcp_task_orchestrator/
mcp_request_handlers.py        # Likely legacy, clean version in mcp_task_orchestrator/
launch_cli.py                  # Check if still needed vs mcp_task_orchestrator_cli/
launch_orchestrator.py         # Check if still needed vs new architecture
```

## Cleanup Implementation Plan

### Phase 1: Safe Relocations (Week 1)

#### Step 1: Move Documentation
```bash
# Create release directory if needed
mkdir -p docs/releases

# Move release notes
mv RELEASE_NOTES_v1.7.1.md docs/releases/
mv RELEASE_NOTES_v1.8.0.md docs/releases/
mv DEPENDENCY_FIX_SUMMARY.md docs/releases/  # or archive if obsolete

# Update any references to these files
```

#### Step 2: Move Test Files
```bash
# Move test files to appropriate test directories
mv test_dependency_check.py tests/unit/
mv test_working_directory.py tests/unit/
mv test_workspace_edge_cases.py tests/unit/
mv test_workspace_functionality.py tests/unit/
mv test_workspace_mcp_integration.py tests/integration/

# Update test runner configurations if needed
```

#### Step 3: Consolidate Planning Content
```bash
# Move planning content to docs/planning/
mv planning/*.md docs/planning/

# Archive session-specific files
mv planning/files-created-this-session.md docs/archives/historical/
mv planning/task-cleanup-analysis.md docs/archives/historical/

# Remove empty planning directory
rmdir planning/
```

#### Step 4: Consolidate Architecture Content
```bash
# Move architecture content to docs/architecture/
mv architecture/*.md docs/architecture/

# Remove empty architecture directory
rmdir architecture/
```

### Phase 2: Legacy Code Analysis (Week 2)

#### Step 1: Reference Analysis
```bash
# Search for imports/references to root-level legacy files
grep -r "import server" . --exclude-dir=.git
grep -r "from server" . --exclude-dir=.git
grep -r "import orchestrator" . --exclude-dir=.git
grep -r "from orchestrator" . --exclude-dir=.git
# etc.
```

#### Step 2: Functionality Verification
```bash
# Test that clean architecture versions work
python -m mcp_task_orchestrator.server  # Should work
python server.py                        # Check if this is needed
```

#### Step 3: Entry Point Analysis
```bash
# Check launch scripts and entry points
cat launch_cli.py
cat launch_orchestrator.py
cat setup.py  # Check entry points definition
cat pyproject.toml  # Check entry points definition
```

### Phase 3: Safe Removal (Week 3)

#### Removal Criteria:
- [ ] No active imports/references found
- [ ] Functionality confirmed available in clean architecture
- [ ] Tests pass without legacy files
- [ ] Entry points work correctly

#### Legacy Files to Remove (After Verification):
```bash
# Remove duplicate directories (after verification)
rm -rf orchestrator/     # If functionality in mcp_task_orchestrator/orchestrator/
rm -rf reboot/          # If functionality in mcp_task_orchestrator/reboot/
rm -rf staging/         # If functionality in mcp_task_orchestrator/staging/
rm -rf monitoring/      # If functionality in mcp_task_orchestrator/monitoring/

# Remove legacy Python files (after verification)
rm __init__.py                    # If not needed for package
rm __main__.py                    # If functionality in mcp_task_orchestrator/
rm server.py                      # If functionality in mcp_task_orchestrator/
rm persistence.py                 # If functionality in mcp_task_orchestrator/
rm persistence_factory.py         # If functionality in mcp_task_orchestrator/
rm mcp_request_handlers.py        # If functionality in mcp_task_orchestrator/
```

#### Conditional Removals:
```bash
# Remove only if superseded by clean architecture
rm launch_cli.py          # If mcp_task_orchestrator_cli/ handles this
rm launch_orchestrator.py # If mcp_task_orchestrator/server.py handles this
```

### Phase 4: Archive Consolidation (Week 4)

#### Step 1: Merge Archives
```bash
# Move archives/ content to docs/archives/
mv archives/* docs/archives/historical/
rmdir archives/
```

#### Step 2: Create Archive Index
```bash
# Create comprehensive archive documentation
# Update docs/archives/README.md with complete index
```

## Target Root Directory Structure

### Final Clean Root Directory:
```
/
├── README.md                    # Project overview
├── CLAUDE.md                    # Development guidance  
├── CHANGELOG.md                 # Version history
├── CONTRIBUTING.md              # Contribution guidelines
├── LICENSE                      # License file
├── QUICK_START.md              # Quick start guide
├── TESTING_INSTRUCTIONS.md     # Testing guide
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies
├── setup.py                    # Package setup
├── mcp_task_orchestrator/      # Main package (clean architecture)
├── mcp_task_orchestrator_cli/  # CLI package
├── installer/                  # Installation utilities
├── testing_utils/              # Testing utilities
├── tests/                      # Test suite
├── scripts/                    # Utility scripts
├── tools/                      # Diagnostic tools
├── launch_scripts/             # Launch utilities
├── config/                     # Configuration templates
├── db/                         # Database utilities
└── docs/                       # All documentation
```

### Benefits of Clean Root:
1. **Clear Package Structure**: Main functionality clearly in mcp_task_orchestrator/
2. **No Duplication**: Single source of truth for each component
3. **Clean Dependencies**: No confusion about which files are active
4. **Easy Navigation**: Developers can quickly find what they need
5. **Professional Appearance**: Clean structure appropriate for 2.0.0 release

## Risk Mitigation

### Backup Strategy:
```bash
# Create backup before major changes
git branch cleanup-backup-$(date +%Y%m%d)
git commit -m "Backup before cleanup"
```

### Verification Steps:
1. **Test Suite Passes**: All tests must pass after each phase
2. **Server Starts**: Both MCP server and CLI must start correctly
3. **Import Check**: No broken imports after relocations
4. **Documentation Links**: Update all internal links after moves

### Rollback Plan:
- Each phase committed separately for easy rollback
- Backup branch available for emergency restore
- Gradual approach allows stopping if issues found

## Success Criteria

### Quantitative Goals:
- [ ] Reduce root directory files from 25+ to <15 essential files
- [ ] Eliminate all duplicate directory structures
- [ ] Move 40+ files to appropriate locations
- [ ] Archive 20+ legacy/historical files

### Qualitative Goals:
- [ ] Clear package structure with single source of truth
- [ ] Professional root directory appropriate for 2.0.0
- [ ] Easy navigation for new developers
- [ ] Clean separation between code, docs, and utilities

This cleanup plan prepares the repository for a professional 2.0.0 release with clean, organized structure.