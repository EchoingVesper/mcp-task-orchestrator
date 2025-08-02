

# MCP Task Orchestrator - Ongoing Maintenance Checklist

#

# 📅 Daily Development Practices

#

#

# Before Starting Any Claude Code Session:

- [ ] **Check root directory**: `ls -la | wc -l` (should be ≤15)

- [ ] **Review git status**: Ensure clean state

- [ ] **Verify project structure**: Quick visual scan of directories

- [ ] **Create session temp directory**: `mkdir -p temp/session-$(date +%Y%m%d)`

#

#

# During Development:

- [ ] **Think before creating files**: "Does this belong in root?" (Usually NO)

- [ ] **Use proper directory structure**: docs/, scripts/, temp/ as appropriate

- [ ] **Follow naming conventions**: lowercase-with-hyphens for docs, snake_case for scripts

- [ ] **Update documentation**: Keep docs current with code changes

#

#

# End of Each Session:

- [ ] **Root directory check**: Count files, move any misplaced items

- [ ] **Clean build artifacts**: Remove build/, dist/, *.egg-info/

- [ ] **Organize temp files**: Keep or clean temp/ directory

- [ ] **Validate package**: `python -c "import mcp_task_orchestrator"`

- [ ] **Commit properly**: Use conventional commit messages

#

# 📊 Weekly Health Checks

#

#

# Project Structure Audit:

```bash

# Root file count (target: ≤15)

find . -maxdepth 1 -type f | wc -l

# Check for misplaced files

find . -maxdepth 1 -name "*.py" | grep -E "(test_|build_|validate_)"
find . -maxdepth 1 -name "*.md" | grep -v -E "(README|CONTRIBUTING|TROUBLESHOOTING|QUICK_START|CHANGELOG)"

# Virtual environment check (should only be venv_mcp/)

ls -d venv*/ 2>/dev/null | wc -l

# Build artifact check (should be empty)

ls build/ dist/ *.egg-info/ 2>/dev/null

```text

#

#

# Documentation Organization:

- [ ] **All development docs** in `docs/development/`

- [ ] **All test docs** in `docs/testing/`

- [ ] **All release docs** in `docs/releases/`

- [ ] **User docs** properly organized in `docs/user-guide/`

- [ ] **No orphaned docs** in wrong locations

#

#

# Script Organization:

- [ ] **Build scripts** in `scripts/build/`

- [ ] **Test scripts** in `scripts/testing/`

- [ ] **Diagnostic scripts** in `scripts/diagnostics/`

- [ ] **No utility scripts** in root directory

#

# 🧹 Monthly Deep Clean

#

#

# Complete Structure Review:

```text
bash

# Generate project structure report

tree -I 'venv_*|.git|__pycache__' > temp/project-structure-$(date +%Y%m%d).txt

# Check for duplicate files

find . -name "*.md" -exec basename {} \; | sort | uniq -d

# Review gitignore effectiveness

git status --porcelain | grep "^??" | head -10

```text

#

#

# Performance Cleanup:

- [ ] **Remove old virtual environments**: Keep only `venv_mcp/`

- [ ] **Clean Python cache**: `find . -name "__pycache__" -exec rm -rf {} +`

- [ ] **Clean pytest cache**: `rm -rf .pytest_cache/`

- [ ] **Clean build artifacts**: `rm -rf build/ dist/ *.egg-info/`

- [ ] **Archive old logs**: Move old logs from `.task_orchestrator/logs/`

#

#

# Documentation Maintenance:

- [ ] **Update README.md**: Ensure current with latest features

- [ ] **Review CHANGELOG.md**: Add recent changes

- [ ] **Update installation docs**: Verify installation process works

- [ ] **Check internal links**: Ensure all documentation links work

- [ ] **Archive old reports**: Move old reports to `archives/`

#

# 🔧 Automation Setup

#

#

# Create Project Structure Validator:

```text
python

# scripts/diagnostics/check-project-structure.py

#!/usr/bin/env python3
"""Validate project organization follows standards."""

import os
from pathlib import Path
import sys

def check_root_files():
    """Check root directory file count and types."""
    root = Path(".")
    files = [f for f in root.iterdir() if f.is_file()]
    issues = []
    
    if len(files) > 15:
        issues.append(f"❌ Too many root files: {len(files)} (should be ≤15)")
    
    

# Check for misplaced files

    misplaced_scripts = [f for f in files if f.name.startswith(('test_', 'build_', 'validate_'))]
    if misplaced_scripts:
        issues.append(f"❌ Misplaced scripts: {[f.name for f in misplaced_scripts]}")
    
    misplaced_docs = [f for f in files if f.suffix == '.md' and 
                     f.name not in ['README.md', 'CONTRIBUTING.md', 'TROUBLESHOOTING.md', 
                                   'QUICK_START.md', 'CHANGELOG.md']]
    if misplaced_docs:
        issues.append(f"❌ Misplaced documentation: {[f.name for f in misplaced_docs]}")
    
    if not issues:
        print(f"✅ Root directory: {len(files)} files (within limits)")
    
    return issues

def check_directory_structure():
    """Verify expected directory structure exists."""
    expected_dirs = [
        'docs/development',
        'docs/testing', 
        'docs/releases',
        'scripts/build',
        'scripts/testing',
        'scripts/diagnostics'
    ]
    
    issues = []
    for dir_path in expected_dirs:
        if not Path(dir_path).exists():
            issues.append(f"❌ Missing directory: {dir_path}")
    
    if not issues:
        print("✅ Directory structure: All expected directories present")
    
    return issues

def check_virtual_environments():
    """Check for multiple virtual environments."""
    venvs = [d for d in Path(".").iterdir() if d.is_dir() and d.name.startswith('venv')]
    issues = []
    
    if len(venvs) > 1:
        issues.append(f"❌ Multiple virtual environments: {[v.name for v in venvs]}")
    elif len(venvs) == 0:
        issues.append("⚠️  No virtual environment found")
    else:
        print(f"✅ Virtual environment: {venvs[0].name} (single env)")
    
    return issues

def check_build_artifacts():
    """Check for build artifacts that should be cleaned."""
    artifacts = ['build', 'dist']
    egg_info = list(Path(".").glob("*.egg-info"))
    
    issues = []
    for artifact in artifacts:
        if Path(artifact).exists():
            issues.append(f"❌ Build artifact exists: {artifact}/ (should be cleaned)")
    
    if egg_info:
        issues.append(f"❌ Egg-info artifacts: {[d.name for d in egg_info]}")
    
    if not issues:
        print("✅ Build artifacts: Clean (no build artifacts)")
    
    return issues

def main():
    """Run all structure checks."""
    print("🔍 MCP Task Orchestrator - Project Structure Check")
    print("=" * 50)
    
    all_issues = []
    all_issues.extend(check_root_files())
    all_issues.extend(check_directory_structure())
    all_issues.extend(check_virtual_environments())
    all_issues.extend(check_build_artifacts())
    
    if all_issues:
        print("\n❌ Issues found:")
        for issue in all_issues:
            print(f"  {issue}")
        print(f"\n📋 Run cleanup: python scripts/build/cleanup-project-structure.py")
        sys.exit(1)
    else:
        print("\n🎉 Project structure looks excellent!")
        sys.exit(0)

if __name__ == "__main__":
    main()

```text

#

#

# Pre-commit Hook Setup:

```text
bash

# .git/hooks/pre-commit

#!/bin/bash
set -e

echo "🔍 Running project structure check..."
python scripts/diagnostics/check-project-structure.py

echo "🧪 Running quick tests..."
python -m pytest tests/ -x --tb=short

echo "✅ Pre-commit checks passed!"

```text

#

#

# GitHub Actions Integration:

```text
yaml

# .github/workflows/structure-check.yml

name: Project Structure Check

on: [push, pull_request]

jobs:
  structure-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Check project structure
      run: python scripts/diagnostics/check-project-structure.py
```text

#

# 📈 KPI Tracking

#

#

# Monthly Metrics:

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Root files | ≤15 | ___ | ___ |
| Misplaced docs | 0 | ___ | ___ |
| Misplaced scripts | 0 | ___ | ___ |
| Virtual envs | 1 | ___ | ___ |
| Build artifacts | 0 | ___ | ___ |

#

#

# Developer Experience Metrics:

- **Onboarding time**: Time for new developer to understand structure

- **File find time**: Time to locate specific files

- **Documentation currency**: How up-to-date docs are with code

- **CI/CD success rate**: Build/test pass rate

#

# 🚨 Red Flags to Watch For

#

#

# Immediate Action Required:

- Root directory >20 files

- Test/build scripts in root

- Multiple documentation files with similar names

- Build artifacts committed to git

- More than 2 virtual environments

#

#

# Weekly Attention Needed:

- Root directory 15-20 files

- Documentation scattered across multiple locations

- Temporary files not cleaned up

- Outdated documentation references

#

#

# Monthly Review Items:

- Overall project organization

- Documentation structure effectiveness

- Script organization efficiency

- New developer feedback on structure

#

# 🎯 Success Indicators

#

#

# Well-Organized Project Signs:

- ✅ New developers can navigate structure intuitively

- ✅ Files are in predictable locations

- ✅ Root directory is clean and focused

- ✅ Documentation is well-organized and current

- ✅ Scripts are properly categorized

- ✅ Build process is clean and repeatable

#

#

# Organizational Excellence:

- Zero misplaced files in root

- All documentation follows consistent structure

- Scripts are properly categorized by function

- Git history shows clean, organized commits

- CI/CD runs without structure-related issues

- New contributors can contribute immediately

---

*Remember: Consistent maintenance is easier than periodic major cleanups. A few minutes of attention daily prevents hours of reorganization later.*
