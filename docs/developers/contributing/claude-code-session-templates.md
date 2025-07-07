

# Claude Code Session Templates for MCP Task Orchestrator

**Post-Cleanup Professional Repository Status**: ✅ 100/100 Health Score  
**Organization Level**: Professional (Industry Standard)  
**Documentation Quality**: Comprehensive (217 files organized)  
**Automation Status**: Full (Health monitoring + Maintenance systems)

#

# Quick Start Session Template

```markdown

# MCP Task Orchestrator Development Session

#

# Pre-Session Setup ✅

- Repository Health Score: 100/100 (Professional organization)

- All scripts organized: scripts/build/, scripts/testing/, scripts/diagnostics/

- Documentation structured: docs/releases/, docs/testing/, docs/development/

- Single virtual environment: venv_mcp (Python 3.13.1)

- Clean build state: No artifacts present

#

# Session Context

**Project**: MCP Task Orchestrator v1.6.0 (well-tested)
**Architecture**: Python MCP server + comprehensive orchestration capabilities
**Organization**: Professional structure (60 files → 11 in root, 82% reduction)

#

# Available Development Paths

#

## Core Development

```bash

# Navigate to core implementation

cd mcp_task_orchestrator && claude

# Key modules:

# - orchestrator/core.py (orchestration engine)

# - server/ (MCP server components)

# - db/ (persistence and models)

```text

#

## Script Development

```text
bash

# Navigate to scripts for utilities

cd scripts && claude

# Organized categories:

# - build/ (11 scripts) - Package building and release

# - testing/ (13 scripts) - Test automation and validation

# - diagnostics/ (23 scripts) - Health monitoring and analysis

# - deployment/ (3 scripts) - Installation and deployment

```text

#

## Documentation Work

```bash

# Navigate to documentation

cd docs && claude

# Professional structure:

# - releases/ (6 files) - Version and release documentation

# - testing/ (6 files) - Test frameworks and validation

# - development/ (7 files) - Implementation and contribution guides

# - user-guide/ (comprehensive) - End-user documentation

```text

#

# Health Monitoring Commands

#

## Quick Health Check

```bash
python scripts/diagnostics/check-project-structure.py

# Expected: 100/100 health score

python scripts/diagnostics/health_monitor.py --report

# Expected: No alerts, excellent status

```text

#

## Maintenance Operations

```bash

# Check maintenance schedule

python scripts/maintenance/maintenance_scheduler.py status

# Run due maintenance tasks

python scripts/maintenance/maintenance_scheduler.py run

# Manual cleanup if needed

python scripts/maintenance/automated_cleanup.py --dry-run

```text

#

# Git Workflow (Cleanup Branch Active)

**Current Branch**: `project-organization-cleanup/comprehensive-v1.6.0`  
**Status**: 8 commits of systematic cleanup (architect → implementer → tester → reviewer)

#

## Safe Development Workflow

```text
bash

# Check current status

git status
git log --oneline -5

# Create feature branch from cleanup branch

git checkout -b feature/your-feature-name

# Or return to main for stable development

git checkout main
git pull origin main

```text

#

# Testing Quick Reference

#

## Enhanced Test Runners (Recommended)

```text
bash

# Use enhanced test infrastructure

venv_mcp/Scripts/python.exe scripts/testing/verify_script_reorganization.py
python docs/development/documentation_reorganization_verification.py
python scripts/testing/basic_migration_test.py

```text

#

## Package Development Testing

```text
bash

# Verify imports after changes

venv_mcp/Scripts/python.exe -c "import mcp_task_orchestrator; print('SUCCESS')"

# Test package installation

venv_mcp/Scripts/python.exe -m pip install -e . --quiet

```text

#

# Session End Checklist

- [ ] Health score maintained ≥95 (target: 100)

- [ ] No build artifacts left behind

- [ ] Documentation updated if modified

- [ ] Scripts tested in new locations if changed

- [ ] Git commits follow conventional format

- [ ] Virtual environment clean (only venv_mcp)

#

# Emergency Procedures

#

## Rollback to Pre-Cleanup State

```text
bash

# Return to main branch (discards cleanup)

git checkout main

# Or rollback specific changes

git checkout project-organization-cleanup/comprehensive-v1.6.0
git reset --hard <previous-commit>

```text

#

## Health Score Issues

```text
bash

# Automated diagnosis and repair

python scripts/maintenance/automated_cleanup.py
python scripts/diagnostics/health_monitor.py --check

# Manual cleanup if needed

rm -rf build/ dist/ *.egg-info/
find . -name "__pycache__" -not -path "./venv*" -exec rm -rf {} +

```text

```text

#

# Advanced Session Templates

#

## Feature Development Session

```text
text
markdown

# Feature Development in Professional Repository

#

# Setup

- Branch: feature/your-feature from main or cleanup branch

- Health Score: 100/100 baseline established

- Organization: Professional structure ready for development

#

# Development Workflow

1. Health check: `python scripts/diagnostics/health_monitor.py --report`

2. Feature implementation with organized file structure

3. Testing with enhanced test runners

4. Documentation updates in appropriate docs/ categories

5. Final health validation before commit

#

# Quality Gates

- Maintain health score ≥95

- Test all modified components

- Update relevant documentation

- Follow organized file placement patterns

```text

#

## Documentation Session

```text
markdown

# Documentation Work in Organized Structure

#

# Navigation

- User guides: `cd docs/user-guide && claude`

- Development docs: `cd docs/development && claude`

- API references: `cd docs/api && claude`

- Release notes: `cd docs/releases && claude`

#

# Documentation Standards

- User-centered design principles

- Professional information architecture

- Cross-references via docs/INDEX.md

- Category-specific organization (releases/testing/development)

#

# Verification

- Run documentation verification: `python docs/development/documentation_reorganization_verification.py`

- Update INDEX.md for new content

- Maintain professional categorization
```text
