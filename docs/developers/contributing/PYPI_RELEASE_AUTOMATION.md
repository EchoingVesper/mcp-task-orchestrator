

# PyPI Release Automation

This document describes the comprehensive PyPI release automation system for the MCP Task Orchestrator project.

#

# Overview

The PyPI release automation script handles the complete release process from version updates to package publishing, with comprehensive safety checks to prevent accidental releases.

#

# Prerequisites

#

#

# Required Dependencies

```bash
pip install rich python-dotenv twine build

```text

#

#

# GitHub CLI (Optional)

For automatic GitHub release creation:

```text
bash

# Install GitHub CLI

gh --version

```text
text

#

#

# Environment Configuration

Ensure `.env` file is configured with PyPI tokens:

```text
bash

# .env file

PYPI_API_TOKEN=pypi-your-production-token
PYPI_TEST_TOKEN=pypi-your-test-token

```text
text

#

# Usage

#

#

# Basic Release (Patch Version)

```text
bash
python scripts/release/pypi_release_automation.py

```text

#

#

# Version Type Selection

```text
bash

# Patch release (1.6.1 → 1.6.2)

python scripts/release/pypi_release_automation.py --version patch

# Minor release (1.6.1 → 1.7.0)

python scripts/release/pypi_release_automation.py --version minor

# Major release (1.6.1 → 2.0.0)

python scripts/release/pypi_release_automation.py --version major

```text

#

#

# Test Mode

```text
bash

# Upload to TestPyPI for validation

python scripts/release/pypi_release_automation.py --test

```text

#

#

# Skip Tests

```text
bash

# Skip test suite (use with caution)

python scripts/release/pypi_release_automation.py --skip-tests

```text

#

# Safety Checks

The automation includes comprehensive safety checks:

#

#

# 1. Branch Validation

- ✅ Must be on `main` branch

- ❌ Fails if on feature/development branch

#

#

# 2. Uncommitted Changes

- ✅ Working directory must be clean

- ❌ Fails if uncommitted changes exist

#

#

# 3. Upstream Synchronization

- ✅ Local main must be up-to-date with remote

- ❌ Fails if behind remote main

- ⚠️ Warns if ahead of remote main

#

#

# 4. Version Validation

- ✅ Validates current version format

- ✅ Calculates new version correctly

- ❌ Fails on invalid version patterns

#

#

# 5. Build Verification

- ✅ Verifies build artifacts exist

- ✅ Checks wheel and source distributions

- ❌ Fails if build artifacts missing

#

# Release Process

```text
mermaid
graph TD
    A[Start Release] --> B{Safety Checks}
    B -->|Pass| C[Update Version Files]
    B -->|Fail| Z[Exit with Error]
    
    C --> D{Run Tests}
    D -->|Pass| E[Build Package]
    D -->|Fail| F{Continue Anyway?}
    F -->|No| Z
    F -->|Yes| E
    
    E --> G{Upload to PyPI}
    G -->|Success| H[Create Git Tag]
    G -->|Fail| Z
    
    H --> I[Push to Remote]
    I --> J[Create GitHub Release]
    J --> K[Cleanup Artifacts]
    K --> L[Release Complete]

```text

#

# Files Updated

The automation updates version numbers in:

- `setup.py` - Main package version

- `pyproject.toml` - Project metadata version

- `mcp_task_orchestrator/__init__.py` - Module version (if present)

#

# Git Operations

#

#

# Automatic Operations

- Creates commit with version changes

- Creates git tag (format: `v1.6.2`)

- Pushes main branch to remote

- Pushes tag to remote

#

#

# Commit Message Format

```text

release: v1.6.2

🤖 Generated with PyPI Release Automation

```text

#

# GitHub Release

If GitHub CLI is available, creates a release with:

- Release title: `Release 1.6.2`

- Auto-generated release notes

- Installation instructions

- Changelog link

#

# Error Handling

#

#

# Common Failure Points

1. **Branch Check**: Switch to main branch

2. **Uncommitted Changes**: Commit or stash changes

3. **Behind Remote**: Run `git pull origin main`

4. **Build Failure**: Check code syntax and dependencies

5. **Upload Failure**: Verify PyPI tokens and network

#

#

# Recovery Procedures

- **Failed Upload**: Re-run script after fixing issues

- **Failed Git Operations**: Package uploaded but manual git work needed

- **Failed GitHub Release**: Create release manually on GitHub

#

# Manual Fallback

If automation fails, follow manual steps:

#

#

# 1. Version Update

```text
bash

# Edit version in setup.py, pyproject.toml

# Commit changes

git add .
git commit -m "release: v1.6.2"

```text

#

#

# 2. Build and Upload

```text
bash

# Build package

python setup.py sdist bdist_wheel

# Upload to PyPI

python -m twine upload dist/*

```text

#

#

# 3. Git Operations

```text
bash

# Create and push tag

git tag v1.6.2
git push origin main
git push origin v1.6.2

```text

#

#

# 4. GitHub Release

```text
bash

# Create GitHub release

gh release create v1.6.2 --title "Release 1.6.2" --generate-notes

```text

#

# Integration with Development Workflow

#

#

# When to Use Automation

- ✅ Bug fixes requiring user updates

- ✅ New features ready for public use

- ✅ Security patches

- ✅ Major milestone releases

#

#

# When NOT to Use

- ❌ Development/experimental changes

- ❌ Documentation-only updates

- ❌ Internal refactoring without user impact

- ❌ Work-in-progress features

#

# Configuration Options

#

#

# Environment Variables

```text
bash

# .env configuration

AUTO_GIT_TAG=true              

# Automatically create git tags

RUN_TESTS_BEFORE_UPLOAD=true   

# Run test suite before uploading

CLEAN_BUILD_ARTIFACTS=true     

# Clean dist/ and build/ after upload

VERBOSE_OUTPUT=false           

# Show detailed output

```text

#

#

# Custom Repository URLs

```text
bash
PYPI_REPOSITORY_URL=https://upload.pypi.org/legacy/
TEST_PYPI_REPOSITORY_URL=https://test.pypi.org/legacy/

```text

#

# Troubleshooting

#

#

# Common Issues

**"externally-managed-environment" Error**:

```text
bash

# Use virtual environment

python -m venv release_env
source release_env/bin/activate  

# Linux/Mac

# OR

release_env\Scripts\activate     

# Windows

pip install -r requirements.txt

```text
text

**Missing Dependencies**:

```text
bash
pip install rich python-dotenv twine build
```text
text

**Token Issues**:

- Verify tokens in `.env` file

- Check token permissions on PyPI

- Ensure tokens haven't expired

**Network Issues**:

- Check internet connection

- Verify PyPI repository URLs

- Try TestPyPI first

#

# Security Considerations

#

#

# Token Protection

- Never commit `.env` file to repository

- Use `.env.example` for template

- Rotate tokens regularly

- Use separate tokens for test and production

#

#

# Access Control

- Limit PyPI token scope to specific packages

- Use organization tokens for team projects

- Enable two-factor authentication on PyPI

#

# See Also

- [PyPI Publishing Guide](PYPI_PUBLISHING.md)

- [Development Workflow](../.PYPI_WORKFLOW_INTEGRATION.md)

- [Security Best Practices](../security/pypi-security.md)
