# MCP Task Orchestrator - Project Organization Cleanup Plan

## 📊 Current State Analysis

### Root Directory File Count: **61 files** (Should be ~10-15)

### Issues Categorized:

#### 🔴 CRITICAL: Misplaced Documentation (26 files)
```
COMPREHENSIVE_MIGRATION_TEST_REPORT.md      → docs/testing/
COMPREHENSIVE_REBOOT_TEST_REPORT.md         → docs/testing/
IMPLEMENTATION_SUMMARY.md                   → docs/development/
INTEGRATION_GUIDE.md                        → docs/
MIGRATION_GUIDE.md                           → docs/
MIGRATION_SYSTEM_IMPLEMENTATION_SUMMARY.md  → docs/development/
NEXT_STEPS.md                               → docs/development/
PR_PREPARATION_SUMMARY.md                   → docs/development/
PyPI_Release_1.6.0_Summary.md              → docs/development/
RELEASE_CHECKLIST.md                         → docs/development/
RELEASE_NOTES.md                            → docs/
RELEASE_NOTES_v1.4.0.md                    → docs/releases/
REPOSITORY_CLEANUP_SUMMARY.md              → docs/development/
TESTING_CHANGELOG.md                        → docs/testing/
TESTING_GUIDELINES.md                       → docs/testing/
TEST_ARTIFACTS_SUMMARY.md                  → docs/testing/
VALIDATION_REPORT.md                        → docs/testing/
WORKTREE_SETUP.md                           → docs/development/
```

#### 🔴 CRITICAL: Misplaced Scripts (20 files)
```
basic_migration_test.py                     → scripts/testing/
build_status.py                             → scripts/build/
cleanup_and_build.py                       → scripts/build/
comprehensive_migration_test.py             → scripts/testing/
direct_build.py                            → scripts/build/
execute_build.py                           → scripts/build/
execute_pypi_build.py                      → scripts/build/
execute_test_direct.py                     → scripts/testing/
final_validation_test.py                   → scripts/testing/
manual_build.py                            → scripts/build/
migration_test_report_generator.py         → scripts/testing/
prepare_pypi_release.py                    → scripts/build/
quick_build_validate.py                    → scripts/build/
run_build_inline.py                        → scripts/build/
run_reboot_tests.py                        → scripts/testing/
server_migration_integration.py            → scripts/testing/
simple_exec_build.py                       → scripts/build/
standalone_migration_test.py               → scripts/testing/
test_migration_system.py                   → scripts/testing/
test_reboot_comprehensive.py               → scripts/testing/
test_reboot_tools.py                       → scripts/testing/
test_server_integration.py                 → scripts/testing/
validate_implementation.py                 → scripts/testing/
validate_release_ready.py                  → scripts/testing/
validate_server_integration.py             → scripts/testing/
```

#### 🟡 WARNING: Build Artifacts (Should be cleaned)
```
build/                                      → DELETE (rebuild as needed)
dist/                                       → DELETE (rebuild as needed)
mcp_task_orchestrator.egg-info/            → DELETE (rebuild as needed)
```

#### 🟡 WARNING: Multiple Virtual Environments
```
venv_mcp/                                   → KEEP (primary)
venv_pr_test/                              → DELETE
venv_pypi/                                 → DELETE
venv_pypi_test/                            → DELETE  
venv_pypi_validation/                      → DELETE
venv_test/                                 → DELETE
```

#### 🟡 WARNING: Development Artifacts
```
planning/                                   → archive/ or DELETE
worktrees/                                 → DELETE (git worktrees are external)
.claude/                                   → ADD to .gitignore
.tools/                                    → ADD to .gitignore
```

#### ⚠️ CAUTION: Duplicate Files
```
CHANGELOG.md vs CHANGE_LOG.md              → Merge into CHANGELOG.md
```

#### ✅ KEEP: Essential Root Files (Should remain)
```
README.md                                   ✓ Primary documentation
CONTRIBUTING.md                             ✓ Contribution guidelines  
TROUBLESHOOTING.md                          ✓ User troubleshooting
QUICK_START.md                             ✓ Quick setup guide
LICENSE                                     ✓ License file
pyproject.toml                             ✓ Build configuration
setup.py                                   ✓ Package setup
requirements.txt                           ✓ Dependencies
run_installer.py                           ✓ Primary installer
launch_cli.py                              ✓ CLI launcher
launch_orchestrator.py                     ✓ Server launcher
.gitignore                                 ✓ Version control
.env.example                               ✓ Environment template
```

## 📋 Proposed Clean Directory Structure

```
mcp-task-orchestrator/
├── 📄 README.md                          # Primary documentation
├── 📄 CONTRIBUTING.md                    # Contribution guidelines
├── 📄 TROUBLESHOOTING.md                 # User troubleshooting
├── 📄 QUICK_START.md                     # Quick setup guide
├── 📄 CHANGELOG.md                       # Release history
├── 📄 LICENSE                           # MIT license
├── 📄 pyproject.toml                     # Build system config
├── 📄 setup.py                          # Package setup
├── 📄 requirements.txt                   # Dependencies
├── 📄 run_installer.py                   # Primary installer
├── 📄 launch_cli.py                      # CLI launcher
├── 📄 launch_orchestrator.py             # Server launcher
├── 📄 .gitignore                         # Version control
├── 📄 .env.example                       # Environment template
├── 📁 mcp_task_orchestrator/             # Source code
├── 📁 mcp_task_orchestrator_cli/         # CLI source
├── 📁 tests/                            # Test suite
├── 📁 docs/                             # Documentation
│   ├── 📁 api/                          # API documentation
│   ├── 📁 user-guide/                   # User guides
│   ├── 📁 development/                  # Development docs
│   ├── 📁 testing/                      # Testing documentation
│   ├── 📁 releases/                     # Release notes
│   └── 📁 troubleshooting/              # Detailed troubleshooting
├── 📁 scripts/                          # Utility scripts
│   ├── 📁 build/                        # Build scripts
│   ├── 📁 testing/                      # Test scripts
│   └── 📁 diagnostics/                  # Diagnostic tools
├── 📁 config/                           # Configuration files
├── 📁 installer/                        # Installation system
├── 📁 launch_scripts/                   # Platform launch scripts
├── 📁 archives/                         # Historical artifacts
├── 📁 .task_orchestrator/               # Runtime state
└── 📁 venv_mcp/                         # Virtual environment
```

## 🚀 Cleanup Execution Plan

### Phase 1: Backup and Preparation
1. **Create backup branch**: `git checkout -b cleanup-backup`
2. **Commit current state**: `git add . && git commit -m "backup: pre-cleanup state"`
3. **Return to main**: `git checkout main`
4. **Create cleanup branch**: `git checkout -b project-organization-cleanup`

### Phase 2: Directory Structure Setup
1. **Create missing directories**:
   ```bash
   mkdir -p docs/{development,testing,releases}
   mkdir -p scripts/{build,testing}
   ```

### Phase 3: File Reorganization
1. **Move documentation files**
2. **Move script files**  
3. **Update any internal references**
4. **Merge duplicate files**

### Phase 4: Cleanup
1. **Remove build artifacts**
2. **Remove extra virtual environments**
3. **Remove development artifacts**
4. **Update .gitignore**

### Phase 5: Validation
1. **Test installation process**
2. **Verify all imports work**
3. **Run test suite**
4. **Validate documentation links**

## 📝 Template Instructions for Claude Code

### Pre-Session Setup Template
```markdown
# Claude Code Session Setup - MCP Task Orchestrator

## Project Structure Rules
- **NEVER** create files in project root unless they're essential (README, setup.py, etc.)
- **ALWAYS** place documentation in `docs/` subdirectories
- **ALWAYS** place scripts in `scripts/` subdirectories  
- **ALWAYS** place tests in `tests/` subdirectories

## File Naming Conventions
- Use lowercase with hyphens for documentation: `user-guide.md`
- Use snake_case for Python files: `test_feature.py`
- Use descriptive prefixes: `test_*`, `build_*`, `deploy_*`

## Temporary Files
- Create temporary files in `temp/` directory (gitignored)
- Name with session identifier: `temp/session-20250607-*.py`
- Clean up at end of session

## Directory Mapping
| File Type | Destination | Examples |
|-----------|-------------|----------|
| User docs | `docs/user-guide/` | tutorials, guides |
| Dev docs | `docs/development/` | implementation notes |
| Test docs | `docs/testing/` | test reports |
| Build scripts | `scripts/build/` | build automation |
| Test scripts | `scripts/testing/` | test utilities |
| Config files | `config/` | YAML, JSON configs |
```

### End-of-Session Cleanup Template
```markdown
# Claude Code Session Cleanup Checklist

## Files Created This Session
- [ ] Review all created files
- [ ] Move any root-level files to appropriate directories
- [ ] Remove any temporary test scripts
- [ ] Update documentation if needed

## Directory Check
- [ ] No new files in project root (except essential)
- [ ] All scripts moved to `scripts/` subdirectories
- [ ] All documentation moved to `docs/` subdirectories
- [ ] Temporary files cleaned up

## Git Status
- [ ] Review `git status` for unintended files
- [ ] Stage only intended changes
- [ ] Commit with descriptive message
```

## 🔧 Automation Recommendations

### Pre-commit Hook Script
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Count files in root
ROOT_FILES=$(find . -maxdepth 1 -type f | wc -l)
if [ $ROOT_FILES -gt 20 ]; then
    echo "WARNING: Too many files in root directory ($ROOT_FILES). Consider reorganizing."
    echo "Run: python scripts/build/check_project_structure.py"
fi

# Check for common misplaced files
if ls *.py 2>/dev/null | grep -E "(test_|build_|validate_)" >/dev/null; then
    echo "ERROR: Found misplaced script files in root. Move to scripts/ directory."
    exit 1
fi
```

### Project Structure Validator Script
```python
# scripts/build/check_project_structure.py
"""Validate project organization follows standards."""

import os
from pathlib import Path

def validate_project_structure():
    root = Path(".")
    issues = []
    
    # Check root file count
    root_files = [f for f in root.iterdir() if f.is_file()]
    if len(root_files) > 20:
        issues.append(f"Too many root files: {len(root_files)} (should be <20)")
    
    # Check for misplaced scripts
    misplaced_scripts = [f for f in root_files if f.name.startswith(('test_', 'build_', 'validate_'))]
    if misplaced_scripts:
        issues.append(f"Misplaced scripts in root: {[f.name for f in misplaced_scripts]}")
    
    # Check for misplaced docs
    misplaced_docs = [f for f in root_files if f.suffix == '.md' and f.name not in ['README.md', 'CONTRIBUTING.md', 'TROUBLESHOOTING.md', 'QUICK_START.md', 'CHANGELOG.md']]
    if misplaced_docs:
        issues.append(f"Misplaced documentation: {[f.name for f in misplaced_docs]}")
    
    return issues

if __name__ == "__main__":
    issues = validate_project_structure()
    if issues:
        print("❌ Project structure issues found:")
        for issue in issues:
            print(f"  - {issue}")
        exit(1)
    else:
        print("✅ Project structure looks good!")
```

## 📊 Success Metrics

### Before Cleanup
- Root files: **61**
- Virtual environments: **6**
- Build artifacts: **3 directories**
- Documentation organization: **Poor**

### After Cleanup Target
- Root files: **≤15**
- Virtual environments: **1**
- Build artifacts: **0 (cleaned)**
- Documentation organization: **Excellent**

### Maintenance KPIs
- Monthly root file count check
- Automated structure validation in CI/CD
- Documentation organization score
- Developer onboarding efficiency