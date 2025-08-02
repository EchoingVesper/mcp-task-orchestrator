
# Repository Cleanup & Organization - Implementation Task

**PRP ID**: `REPO_CLEANUP_V1`  
**Type**: Task Implementation  
**Priority**: Medium-High  
**Estimated Effort**: 3-4 days  
**Dependencies**: Documentation updates completed  

#
# Task Overview

Clean up the repository structure to ensure the base directory is minimal and files are organized according to the established architecture. Address the current state where files have accumulated in improper locations.

#
# Current State Analysis

Based on the git status, there are numerous files that need proper organization:

#
## Files to Relocate

#
### Test Files in Root Directory

- `test_rebuilt_package.py` → `tests/package/`

- `test_simple_tools.py` → `tests/unit/`

#
### Documentation Reorganization

- Multiple files in `docs/developers/planning/` need archiving or proper categorization

- Legacy planning documents should move to `docs/archives/`

#
### Script Organization

- Ensure all scripts are properly categorized in `scripts/`

- Validate automation scripts have proper documentation

#
# Cleanup Tasks

#
## 1. Root Directory Cleanup

#
### Target Root Directory State

```text
/
├── README.md
├── CHANGELOG.md  
├── CONTRIBUTING.md
├── QUICK_START.md
├── CLAUDE.md
├── CLAUDE-detailed.md
├── LICENSE
├── pyproject.toml
├── setup.py
├── .gitignore
├── .github/
├── mcp_task_orchestrator/
├── tests/
├── docs/
├── scripts/
├── tools/
└── PRPs/

```text

#
### Files to Remove from Root

```text
bash

# Files that should be moved or removed

rm test_rebuilt_package.py  
# → tests/package/test_rebuilt_package.py
rm test_simple_tools.py     
# → tests/unit/test_simple_tools.py

# Temporary/generated files to remove

rm -f .file_size_history.json  
# Build artifact
rm -rf .claude/                
# Temporary directory
rm -f uv.lock                  
# Lock file should be in .gitignore

```text

#
## 2. Documentation Directory Cleanup

#
### Archive Legacy Planning Documents

```text
bash

# Move completed planning documents to archives

mkdir -p docs/archives/planning/v1.0-completed/

# Documents that are historical/completed

mv docs/developers/planning/Development-Cycle-Planning.md docs/archives/planning/v1.0-completed/
mv docs/developers/planning/Feature-Specifications.md docs/archives/planning/v1.0-completed/ 
mv docs/developers/planning/Missing-Mcp-Tools-Comprehensive.md docs/archives/planning/v1.0-completed/
mv docs/developers/planning/Testing-Strategy.md docs/archives/planning/v1.0-completed/
mv docs/developers/planning/V2.0-Implementation-Status.md docs/archives/planning/v1.0-completed/
mv docs/developers/planning/Version-Progression-Plan.md docs/archives/planning/v1.0-completed/

```text

#
### Organize Feature Documentation

```text
bash

# Create proper feature organization

mkdir -p docs/developers/planning/features/2.0-completed/
mkdir -p docs/developers/planning/features/archived/

# Move completed features

mv docs/developers/planning/features/2.0-approved/ docs/developers/planning/features/archived/2.0-approved/
mv docs/developers/planning/features/2.1-approved/ docs/developers/planning/features/archived/2.1-approved/
mv docs/developers/planning/features/completed/ docs/developers/planning/features/archived/legacy-completed/

# Clean up feature directory structure

find docs/developers/planning/features/ -name "*.md" -exec grep -l "COMPLETED\|APPROVED" {} \; | \
while read file; do
    target_dir="docs/developers/planning/features/archived/$(dirname "$file" | sed 's|.*/features/||')"
    mkdir -p "$target_dir"
    mv "$file" "$target_dir/"
done

```text

#
## 3. Test Directory Organization

#
### Restructure Tests Directory

```text
bash

# Current structure optimization

tests/
├── unit/                    
# Unit tests
│   ├── test_task_handlers.py
│   ├── test_simple_tools.py  
# Move from root
│   └── domain/
├── integration/             
# Integration tests  
│   ├── test_real_implementations_*.py
│   ├── test_task_execution.py
│   └── test_complete_task.py
├── performance/             
# Performance tests
│   └── test_error_handling_performance.py
├── package/                 
# Package testing
│   └── test_rebuilt_package.py  
# Move from root
└── error_handling/          
# Error handling tests
    └── (existing error tests)

```text

#
### Remove Deprecated Test Files

```text
bash

# Remove tests that are no longer relevant

rm -f tests/integration/test_complete_subtask.py    
# Deprecated by new architecture
rm -f tests/integration/test_subtask_execution.py  
# Deprecated by new architecture

```text

#
## 4. Scripts Directory Organization

#
### Enhance Scripts Organization

```text
bash
scripts/
├── automation/              
# Build and automation scripts
│   ├── quality_automation.py
│   └── setup_git_hooks.py
├── migrations/              
# Database and data migrations
│   ├── complete_documentation_migration.py
│   ├── migrate_documentation.py
│   └── README_automation_migration.md
├── validation/              
# Validation and checking scripts
│   ├── fix_docs_markdownlint.py
│   ├── fix_markdown_lint.py
│   └── check_file_organization.py
├── release/                 
# Release management
│   ├── pypi_release_simple.py
│   └── README.md
├── markdown_fixer/          
# Markdown processing tools
├── test_files/              
# Test artifacts and data
└── CLAUDE.md               
# Scripts documentation

```text

#
## 5. Configuration File Cleanup

#
### Standardize Configuration

```text
bash

# Ensure proper configuration files

├── .gitignore              
# Updated with 2.0 patterns
├── .markdownlint.json      
# Markdown linting config
├── .vale.ini              
# Prose linting config
├── pyproject.toml         
# Python project config
└── setup.py               
# Package setup

```text

#
### Update .gitignore

```text
gitignore

# Add 2.0-specific patterns

.task_orchestrator/
*.sqlite
*.db
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.file_size_history.json
uv.lock
.claude/

# IDE and editor files

.vscode/
.idea/
*.swp
*.swo
*~

# Documentation build artifacts

docs/_build/
docs/.doctrees/

# Testing artifacts

.tox/
.mypy_cache/

```text

#
# Implementation Steps

#
## Day 1: Root Directory Cleanup

```text
bash
#!/bin/bash

# Root directory cleanup script

echo "Starting root directory cleanup..."

# 1. Move test files to proper locations

mkdir -p tests/package tests/unit
mv test_rebuilt_package.py tests/package/ 2>/dev/null || echo "test_rebuilt_package.py not found"
mv test_simple_tools.py tests/unit/ 2>/dev/null || echo "test_simple_tools.py not found"

# 2. Remove temporary/generated files

rm -f .file_size_history.json
rm -rf .claude/
rm -f uv.lock

# 3. Validate root directory structure

echo "Root directory contents after cleanup:"
ls -la | grep -E "^-" | wc -l
echo "Target: 8 files maximum in root directory"

echo "Root directory cleanup complete."

```text

#
## Day 2: Documentation Organization

```text
bash
#!/bin/bash

# Documentation organization script

echo "Starting documentation organization..."

# 1. Create archive structure

mkdir -p docs/archives/{planning,features,historical}
mkdir -p docs/archives/planning/{v1.0-completed,v2.0-development}
mkdir -p docs/archives/features/{completed,deprecated,archived}

# 2. Move legacy planning documents

if [ -d "docs/developers/planning" ]; then
    
# Archive completed planning documents
    find docs/developers/planning -name "*Development-Cycle*" -exec mv {} docs/archives/planning/v1.0-completed/ \;
    find docs/developers/planning -name "*Feature-Specifications*" -exec mv {} docs/archives/planning/v1.0-completed/ \;
    find docs/developers/planning -name "*Testing-Strategy*" -exec mv {} docs/archives/planning/v1.0-completed/ \;
    
    
# Archive completed features
    if [ -d "docs/developers/planning/features/2.0-approved" ]; then
        mv docs/developers/planning/features/2.0-approved docs/archives/features/archived/
    fi
    
    if [ -d "docs/developers/planning/features/2.1-approved" ]; then
        mv docs/developers/planning/features/2.1-approved docs/archives/features/archived/
    fi
fi

# 3. Validate documentation structure

echo "Documentation organization complete."
find docs/ -type f -name "*.md" | wc -l
echo "Total markdown files organized."

```text

#
## Day 3: Scripts and Configuration

```text
bash
#!/bin/bash

# Scripts and configuration cleanup

echo "Starting scripts organization..."

# 1. Organize scripts by category

mkdir -p scripts/{automation,migrations,validation,release}

# Move scripts to appropriate categories

[ -f "scripts/quality_automation.py" ] && mv scripts/quality_automation.py scripts/automation/
[ -f "scripts/setup_git_hooks.py" ] && mv scripts/setup_git_hooks.py scripts/automation/

# Migration scripts

find scripts/ -name "*migration*" -not -path "*/migrations/*" -exec mv {} scripts/migrations/ \;

# Validation scripts  

find scripts/ -name "*lint*" -o -name "*fix*" -o -name "*validate*" | \
while read file; do
    [ -f "$file" ] && mv "$file" scripts/validation/
done

# 2. Update configuration files

echo "Updating .gitignore..."
cat > .gitignore << 'EOF'

# 2.0 Task Orchestrator specific

.task_orchestrator/
*.sqlite
*.db

# Python

__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing

.pytest_cache/
.coverage
htmlcov/
.tox/
.cache

# Development

.vscode/
.idea/
*.swp
*.swo
*~
.file_size_history.json
uv.lock
.claude/

# Documentation

docs/_build/
docs/.doctrees/
EOF

echo "Scripts and configuration cleanup complete."

```text

#
## Day 4: Validation and Final Cleanup

```text
bash
#!/bin/bash

# Final validation and cleanup

echo "Starting final validation..."

# 1. Validate root directory

root_file_count=$(ls -la | grep -E "^-" | wc -l)
echo "Root directory files: $root_file_count (target: ≤8)"

# 2. Validate directory structure

echo "Validating directory structure..."
for dir in mcp_task_orchestrator tests docs scripts tools PRPs; do
    if [ -d "$dir" ]; then
        echo "✓ $dir exists"
    else
        echo "✗ $dir missing"
    fi
done

# 3. Check for misplaced files

echo "Checking for misplaced files..."
find . -maxdepth 1 -name "*.py" -not -name "setup.py" | while read file; do
    echo "⚠ Python file in root: $file (should be moved)"
done

find . -maxdepth 1 -name "test_*.py" | while read file; do
    echo "⚠ Test file in root: $file (should be in tests/)"
done

# 4. Validate markdown files

echo "Validating markdown structure..."
if command -v markdownlint >/dev/null 2>&1; then
    markdownlint README.md CHANGELOG.md CLAUDE.md
else
    echo "markdownlint not available, skipping markdown validation"
fi

echo "Final validation complete."

```text

#
# File Organization Standards

#
## Root Directory Rules

- **Maximum 8 files** in root directory

- Only essential project files (README, LICENSE, CHANGELOG, etc.)

- No source code files except setup.py

- No test files

- No temporary or generated files

#
## Directory Structure Standards

```text

/
├── README.md                 
# Project overview
├── CHANGELOG.md             
# Version history  
├── CONTRIBUTING.md          
# Contribution guidelines
├── QUICK_START.md           
# Quick start guide
├── CLAUDE.md                
# Claude Code reference
├── CLAUDE-detailed.md       
# Detailed development guide
├── LICENSE                  
# License file
├── pyproject.toml          
# Python project configuration
├── setup.py                
# Package setup
├── mcp_task_orchestrator/  
# Source code
├── tests/                  
# Test files
├── docs/                   
# Documentation
├── scripts/                
# Utility scripts
├── tools/                  
# Production tools
└── PRPs/                   
# Project Request Proposals
```text

#
## Documentation Organization Rules

- `docs/users/` - User-facing documentation

- `docs/developers/` - Developer/contributor documentation

- `docs/archives/` - Historical and deprecated documentation

- No documentation files in root except essential ones

#
# Acceptance Criteria

- [ ] Root directory contains ≤8 essential files only

- [ ] All test files moved to appropriate test subdirectories

- [ ] All scripts organized in scripts/ subdirectories by category

- [ ] Legacy planning documents archived appropriately

- [ ] Configuration files updated for 2.0

- [ ] No temporary or generated files in root

- [ ] Directory structure follows established standards

- [ ] All markdown files pass linting

- [ ] Cross-references updated after file moves

#
# Success Metrics

- **Root Directory**: ≤8 files (target achieved)

- **Organization**: 100% of files in appropriate directories

- **Configuration**: All config files updated for 2.0

- **Documentation**: 100% of moved files have updated cross-references

- **Cleanup**: 0 temporary or generated files in version control
