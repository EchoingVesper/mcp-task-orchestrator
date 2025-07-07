

# Claude Code Session Template - MCP Task Orchestrator

#

# 📋 Pre-Session Setup Checklist

#

## 1. Project Structure Awareness

```text
mcp-task-orchestrator/
├── 📄 [ESSENTIAL ROOT FILES ONLY]
├── 📁 mcp_task_orchestrator/     

# Source code

├── 📁 tests/                    

# Test suite  

├── 📁 docs/                     

# ALL documentation

│   ├── development/             

# Dev docs, summaries, reports

│   ├── testing/                 

# Test reports, guidelines

│   ├── releases/                

# Release notes, changelogs

│   └── user-guide/              

# User-facing docs

├── 📁 scripts/                  

# ALL utility scripts

│   ├── build/                   

# Build automation

│   ├── testing/                 

# Test utilities

│   └── diagnostics/             

# System diagnostics

└── 📁 temp/                     

# Session temporary files

```text

#

## 2. File Creation Rules

#

### ✅ ALWAYS Do:

- **Place documentation** in `docs/` subdirectories

- **Place scripts** in `scripts/` subdirectories

- **Place temporary files** in `temp/` directory

- **Use descriptive filenames** with proper prefixes

- **Check existing structure** before creating new directories

#

### ❌ NEVER Do:

- **Create files in project root** unless absolutely essential

- **Create test scripts in root** (use `scripts/testing/`)

- **Create documentation in root** (use `docs/` subdirectories)

- **Create multiple virtual environments**

- **Leave session artifacts** in root directory

#

## 3. Directory Mapping Reference

| File Type | Destination | Examples |
|-----------|-------------|----------|
| **Development Docs** | `docs/development/` | implementation-summary.md, pr-prep.md |
| **Test Documentation** | `docs/testing/` | test-report.md, validation.md |
| **User Documentation** | `docs/user-guide/` | tutorials.md, guides.md |
| **Release Documentation** | `docs/releases/` | release-notes-v1.6.0.md |
| **Build Scripts** | `scripts/build/` | build-validator.py, package-builder.py |
| **Test Scripts** | `scripts/testing/` | test-runner.py, integration-test.py |
| **Diagnostic Scripts** | `scripts/diagnostics/` | health-check.py, system-validator.py |
| **Session Files** | `temp/` | session-notes.md, temp-test.py |

#

# 🚀 Session Workflow Template

#

## Phase 1: Session Initialization

```text
bash

# Navigate to project

cd "/mnt/e/My Work/Programming/MCP Servers/mcp-task-orchestrator"

# Check current project state

git status
ls -la  

# Should show ~15 files in root

# Create session workspace if needed

mkdir -p temp

```text

#

## Phase 2: File Creation Guidelines

#

### For Development Documentation:

```text
bash

# ✅ Correct

touch docs/development/feature-implementation-$(date +%Y%m%d).md

# ❌ Incorrect  

touch FEATURE_IMPLEMENTATION.md  

# Would clutter root

```text

#

### For Scripts:

```text
bash

# ✅ Correct

touch scripts/testing/test-new-feature.py
touch scripts/build/validate-build.py

# ❌ Incorrect

touch test_new_feature.py  

# Would clutter root

touch validate_build.py    

# Would clutter root

```text

#

### For Temporary Work:

```text
bash

# ✅ Correct

touch temp/session-$(date +%Y%m%d-%H%M)-notes.md
touch temp/quick-test.py

# ❌ Incorrect

touch session-notes.md  

# Would clutter root

```text

#

## Phase 3: Development Work

#

### Code Changes:

- **Primary code**: Modify files in `mcp_task_orchestrator/`

- **Test files**: Modify/create in `tests/`

- **Configuration**: Modify files in `config/`

#

### Documentation:

- **Implementation notes**: Create in `docs/development/`

- **Test results**: Create in `docs/testing/`

- **User-facing changes**: Update in `docs/user-guide/`

#

### Scripts and Utilities:

- **Build automation**: Create in `scripts/build/`

- **Testing utilities**: Create in `scripts/testing/`

- **Diagnostic tools**: Create in `scripts/diagnostics/`

#

# 📝 File Naming Conventions

#

## Documentation Files:

```text

✅ docs/development/implementation-summary-$(date +%Y%m%d).md
✅ docs/testing/integration-test-report.md
✅ docs/releases/release-notes-v1.6.1.md

❌ IMPLEMENTATION_SUMMARY.md  

# Wrong location + naming

❌ TestReport.md              

# Wrong location + capitalization

```text

#

## Script Files:

```text

✅ scripts/build/validate-package.py
✅ scripts/testing/run-integration-tests.py
✅ scripts/diagnostics/check-system-health.py

❌ validate_package.py       

# Wrong location

❌ RunIntegrationTests.py    

# Wrong naming convention

```text

#

## Temporary Files:

```text

✅ temp/session-20250607-1430-notes.md
✅ temp/quick-test-feature.py
✅ temp/debug-output.log

❌ session-notes.md          

# Wrong location

❌ temp-test.py              

# Wrong location

```text

#

# 🧹 End-of-Session Cleanup Protocol

#

## 1. File Review Checklist:

```text
bash

# Check what files were created/modified

git status

# Review root directory (should have ≤15 files)

ls -la | wc -l

# Identify any misplaced files

find . -maxdepth 1 -type f -name "*.py" | grep -E "(test_|build_|validate_)"
find . -maxdepth 1 -type f -name "*.md" | grep -v -E "(README|CONTRIBUTING|TROUBLESHOOTING|QUICK_START|CHANGELOG)"

```text

#

## 2. Cleanup Actions:

```text
bash

# Move any misplaced files

# [Specific commands based on what's found]

# Clean temporary files if no longer needed

# rm temp/session-*  

# Only if safe to remove

# Remove any build artifacts

rm -rf build/ dist/ *.egg-info/

```text

#

## 3. Final Validation:

```text
bash

# Verify package integrity

python -c "import mcp_task_orchestrator; print('✅ Package OK')"

# Run quick test

python -m pytest tests/ -x --tb=short

# Check structure

python scripts/diagnostics/check-project-structure.py  

# If created

```text

#

## 4. Git Commit Best Practices:

```text
bash

# Stage only intended files

git add [specific-files]

# Use conventional commit format

git commit -m "feat: implement new feature

- Add new functionality in mcp_task_orchestrator/

- Update tests in tests/

- Add documentation in docs/development/

- Create utility script in scripts/testing/

Refs: #issue-number"

```text

#

# 🚨 Error Prevention Checklist

#

## Before Creating Any File:

- [ ] Is this an essential root file? (99% of time: NO)

- [ ] Which `docs/` subdirectory should this go in?

- [ ] Which `scripts/` subdirectory should this go in?

- [ ] Is this a temporary file that should go in `temp/`?

#

## Before Ending Session:

- [ ] Root directory has ≤15 files

- [ ] No misplaced documentation files in root

- [ ] No misplaced script files in root

- [ ] All temporary files properly organized

- [ ] Git status shows only intended changes

#

## Common Mistakes to Avoid:

- ❌ Creating `test_*.py` files in root

- ❌ Creating `build_*.py` files in root  

- ❌ Creating `*SUMMARY.md` files in root

- ❌ Creating `*REPORT.md` files in root

- ❌ Creating session notes in root

- ❌ Leaving debug scripts in root

#

# 📊 Success Metrics

#

## Project Health Indicators:

- **Root file count**: ≤15 files

- **Documentation organization**: All in `docs/` subdirectories

- **Script organization**: All in `scripts/` subdirectories

- **No build artifacts**: Clean `build/`, `dist/` removal

- **Single venv**: Only `venv_mcp/` exists

#

## Session Success Criteria:

- All created files in appropriate directories

- No root directory pollution

- Git history is clean and descriptive

- Package imports and tests still pass

- Documentation properly organized

#

# 🔧 Quick Reference Commands

```text
bash

# Check project structure health

find . -maxdepth 1 -type f | wc -l  

# Should be ≤15

# Find misplaced files

find . -maxdepth 1 -name "*.py" | grep -E "(test_|build_|validate_)"
find . -maxdepth 1 -name "*.md" | grep -v -E "(README|CONTRIBUTING|TROUBLESHOOTING|QUICK_START|CHANGELOG)"

# Quick cleanup

rm -rf build/ dist/ *.egg-info/ .pytest_cache/

# Validate package

python -c "import mcp_task_orchestrator; print('OK')"

# Structure validator (create if needed)

python scripts/diagnostics/check-project-structure.py
```text

#

# 💡 Pro Tips

1. **Always think "Does this belong in root?"** (Answer is usually NO)

2. **Use descriptive directory structure** - it's self-documenting

3. **Temporary files go in temp/** - don't pollute the main structure

4. **Documentation goes in docs/** - organize by audience and purpose

5. **Scripts go in scripts/** - organize by function (build/test/diagnostic)

6. **When in doubt, ask "Where would a new developer expect to find this?"**

---

*Remember: A clean project structure is a sign of professionalism and makes onboarding new contributors much easier. Future you (and your collaborators) will thank present you for maintaining organization.*
