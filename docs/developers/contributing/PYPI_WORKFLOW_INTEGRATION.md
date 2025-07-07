

# PyPI Release Workflow Integration

This document explains how the PyPI release automation integrates into the overall development workflow for the MCP Task Orchestrator project.

#

# Complete Development Workflow

```mermaid
graph TD
    A[Feature Development] --> B[Create Feature Branch]
    B --> C[Implement Changes]
    C --> D[Local Testing]
    D --> E[Create Pull Request]
    E --> F[Code Review]
    F --> G[Merge to Main]
    G --> H{Release Needed?}
    
    H -->|Yes| I[PyPI Release Automation]
    H -->|No| J[Continue Development]
    
    I --> K[Safety Checks]
    K --> L[Version Update]
    L --> M[Build & Test]
    M --> N[Upload to PyPI]
    N --> O[Git Tag & Push]
    O --> P[GitHub Release]
    P --> Q[Notify Users]
    
    J --> A
    Q --> A

```text

#

# Development Phases

#

## 1. Feature Development

Standard development process remains unchanged:

- Create feature branches

- Implement changes locally

- Test thoroughly

- Create pull requests

- Code review and merge

#

## 2. Release Decision Point

After merging to main, decide if a release is needed:

**Release Triggers:**

- Bug fixes affecting user functionality

- New features ready for public use  

- Security patches

- Breaking changes requiring version bump

- Accumulated minor improvements

**No Release Needed:**

- Documentation updates

- Internal refactoring

- Development tool changes

- Work-in-progress features

#

## 3. Release Execution

When a release is needed, use the PyPI automation:

```text
bash

# Standard patch release

python scripts/release/pypi_release_automation.py

# Feature release  

python scripts/release/pypi_release_automation.py --version minor

# Breaking change release

python scripts/release/pypi_release_automation.py --version major

```text

#

# Integration Points

#

## Git Workflow Integration

#

### Before Automation

Traditional manual steps that are now automated:

```text
bash

# Manual version updates (NOW AUTOMATED)

# Edit setup.py, pyproject.toml manually

# git add . && git commit -m "bump version"

# Manual building (NOW AUTOMATED)  

# python setup.py sdist bdist_wheel

# Manual upload (NOW AUTOMATED)

# twine upload dist/*

# Manual git operations (NOW AUTOMATED)

# git tag v1.x.x && git push origin v1.x.x

```text
text

#

### After Automation

Single command replaces all manual steps:

```text
bash
python scripts/release/pypi_release_automation.py

```text
text

#

## CI/CD Integration

#

### GitHub Actions (Future Enhancement)

The automation can be integrated into GitHub Actions:

```text
yaml

# .github/workflows/release.yml

name: Automated Release

on:
  workflow_dispatch:
    inputs:
      version_type:
        description: 'Version increment type'
        required: true
        default: 'patch'
        type: choice
        options:
        - patch
        - minor
        - major

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install rich python-dotenv twine build
      - name: Run Release Automation
        env:
          PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
        run: python scripts/release/pypi_release_automation.py --version ${{ github.event.inputs.version_type }}

```text

#

## MCP Client Updates

#

### User Installation Workflow

After each release, users can update with:

```text
bash
pip install --upgrade mcp-task-orchestrator

```text
text

#

### Claude Code Configuration

The CLI tools help users update their Claude Code configuration:

```text
bash

# Check current installation

python -m mcp_task_orchestrator_cli.cli status

# Update to latest version

python -m mcp_task_orchestrator_cli.cli update --force

```text
text

#

# Branch Protection Strategy

#

## Main Branch Protection

Recommended GitHub branch protection rules:

- Require pull request reviews

- Require status checks to pass

- Restrict pushes to main branch

- Require branches to be up to date

#

## Release Branch Strategy

```text
bash

# Option 1: Direct from main (current approach)

main → PyPI Release

# Option 2: Release branches (for complex releases)

main → release/v1.7.0 → PyPI Release → merge back to main

```text

#

# Version Management Strategy

#

## Semantic Versioning

Follow semantic versioning (semver) principles:

**MAJOR** (X.0.0): Breaking changes

- API changes that break backward compatibility

- Removal of deprecated features

- Major architectural changes

**MINOR** (1.X.0): New features

- New functionality that is backward compatible

- New MCP tools or capabilities

- Performance improvements

**PATCH** (1.0.X): Bug fixes

- Bug fixes that don't add functionality

- Security patches

- Documentation corrections

#

## Pre-release Versions

For testing major changes:

```text
bash

# Alpha releases for early testing

python scripts/release/pypi_release_automation.py --test --version major

# Creates 2.0.0a1 on TestPyPI

# Beta releases for broader testing  

python scripts/release/pypi_release_automation.py --test --version minor

# Creates 1.7.0b1 on TestPyPI

```text
text

#

# Release Communication

#

## Automated Communication

The automation handles:

- Git commit messages with consistent format

- Git tags for version tracking

- GitHub releases with installation instructions

- Changelog generation (basic)

#

## Manual Communication

After automation completes:

- Update project README if needed

- Notify users through appropriate channels

- Update documentation if APIs changed

- Create detailed changelog for major releases

#

# Quality Assurance Integration

#

## Automated Testing

The automation includes built-in test execution:

```bash

# Tests run automatically unless skipped

python scripts/release/pypi_release_automation.py

# Skip tests only in emergencies

python scripts/release/pypi_release_automation.py --skip-tests

```text

#

## Manual QA Checkpoints

Before running automation:

- [ ] All PRs merged and tested

- [ ] Local testing completed

- [ ] Documentation updated

- [ ] No known critical issues

- [ ] Dependencies up to date

#

## Post-Release Validation

After automation completes:

- [ ] Verify package installs correctly

- [ ] Test basic functionality

- [ ] Check that MCP clients can connect

- [ ] Monitor for user-reported issues

#

# Emergency Release Procedures

#

## Hotfix Workflow

For critical security or functionality issues:

```text
text
bash

# 1. Create hotfix branch from main

git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# 2. Implement fix

# ... make changes ...

# 3. Test and commit

git add .
git commit -m "fix: critical security issue"

# 4. Merge to main via fast-track PR

gh pr create --title "HOTFIX: Critical Security Fix" --body "Emergency fix for security vulnerability"

# 5. After merge, immediate release

python scripts/release/pypi_release_automation.py --version patch

```text

#

## Rollback Procedures

If a release causes issues:

```text
bash

# 1. Identify last good version

git tag --sort=-version:refname | head -5

# 2. Create rollback release

# Manually edit version back to last good + patch increment

# Or revert problematic commits and create new release

# 3. Emergency communication

# Notify users of recommended version to use

```text

#

# Monitoring and Metrics

#

## Release Health Monitoring

Track release success metrics:

- Time from merge to release

- Release automation success rate

- User adoption of new versions

- Issue reports post-release

#

## Automation Performance

Monitor automation script performance:

- Execution time

- Failure points

- Safety check effectiveness

- User satisfaction with process

#

# Future Enhancements

#

## Planned Improvements

1. **Enhanced Testing Integration**

- Integration with more test frameworks

- Performance regression testing

- Compatibility testing across Python versions

2. **Advanced GitHub Integration**

- Automatic milestone creation

- Issue linking in releases

- Contributor recognition in releases

3. **User Notification System**

- Email notifications for releases

- Integration with project communication channels

- Update recommendations in CLI tools

4. **Release Analytics**

- Download metrics tracking

- User feedback collection

- Release impact analysis

#

# Troubleshooting Integration Issues

#

## Common Workflow Problems

**Automation Fails After Merge:**

- Check branch protection rules

- Verify merge actually completed

- Ensure local repository is updated

**Version Conflicts:**

- Check if version was manually edited

- Verify no parallel releases in progress

- Use `--version` flag to specify increment type

**Integration with External Tools:**

- Update CLI configuration scripts

- Test with MCP clients after release

- Verify documentation reflects new version

#

# Best Practices

#

## Development Team Guidelines

1. **One Release per Merged PR Set**: Group related changes for single release

2. **Test Before Merge**: Ensure all functionality works before triggering release

3. **Communication**: Coordinate releases among team members

4. **Documentation**: Update docs before running automation

#

## Release Timing

- **Avoid Fridays**: Don't release just before weekends

- **Business Hours**: Release during active support hours

- **Coordination**: Check with users for maintenance windows

- **Testing Window**: Allow time for post-release validation

This integration ensures smooth, automated releases while maintaining quality and safety standards.
