# MCP Task Orchestrator - Release Checklist

## Pre-Release Validation

### 1. Code Quality Checks
- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] No linting errors: `python -m flake8 mcp_task_orchestrator/`
- [ ] Type checking passes (if applicable): `python -m mypy mcp_task_orchestrator/`
- [ ] No security vulnerabilities: Check dependencies

### 2. Version Verification
- [ ] Version updated in `setup.py`
- [ ] Version updated in `mcp_task_orchestrator/__init__.py`
- [ ] Version updated in `README.md` badges
- [ ] Version consistent across all files

### 3. Documentation Review
- [ ] README.md is up to date
- [ ] Installation instructions are correct
- [ ] CHANGELOG.md updated with new version
- [ ] API documentation is current
- [ ] All examples work with new version

### 4. Repository Cleanup
- [ ] No uncommitted changes: `git status`
- [ ] No untracked files that should be committed
- [ ] No sensitive information in repository
- [ ] Virtual environments not in git
- [ ] Build artifacts cleaned: `rm -rf dist/ build/ *.egg-info/`

### 5. Package Build Validation
- [ ] Clean build succeeds: `python setup.py sdist bdist_wheel`
- [ ] Package size is reasonable (< 10MB)
- [ ] All required files included in package
- [ ] No unnecessary files in package
- [ ] `twine check dist/*` passes

### 6. Installation Testing
- [ ] Create fresh virtual environment
- [ ] Test pip install from built package: `pip install dist/*.whl`
- [ ] Verify package imports correctly
- [ ] Test CLI commands work
- [ ] Test with multiple Python versions (3.8+)

### 7. Functional Testing
- [ ] Basic orchestration workflow works
- [ ] Task persistence functions correctly
- [ ] Maintenance coordinator operates
- [ ] All MCP tools are accessible
- [ ] Error handling works properly

### 8. Environment Setup
- [ ] `.env` file configured with PyPI token
- [ ] Token has upload permissions
- [ ] TestPyPI token configured (optional)
- [ ] Git tags are up to date

### 9. Final Checks
- [ ] GitHub PR merged to main branch
- [ ] CI/CD passes (if configured)
- [ ] No open critical issues
- [ ] Release notes prepared
- [ ] Team/users notified of upcoming release

## Release Execution

### Automated Release
```bash
# For patch release (1.5.1 -> 1.5.2)
python scripts/release/release.py --patch

# For minor release (1.5.2 -> 1.6.0)
python scripts/release/release.py --minor

# Test with TestPyPI first
python scripts/release/release.py --patch --test
```

### Manual Release (Fallback)
```bash
# 1. Build
python setup.py sdist bdist_wheel

# 2. Check
twine check dist/*

# 3. Upload
python scripts/release/upload.py
```

## Post-Release Validation

### 1. PyPI Verification
- [ ] Package visible on https://pypi.org/project/mcp-task-orchestrator/
- [ ] Correct version displayed
- [ ] Description renders properly
- [ ] Links work correctly

### 2. Installation Verification
```bash
# In a fresh environment
pip install mcp-task-orchestrator
mcp-task-orchestrator-cli install
```

### 3. GitHub Tasks
- [ ] Create GitHub release with tag
- [ ] Upload release notes
- [ ] Close related issues
- [ ] Update project board

### 4. Communication
- [ ] Announce on relevant channels
- [ ] Update documentation site
- [ ] Notify major users of changes

## Rollback Plan

If issues are discovered post-release:

1. **Minor Issues**: Release patch version with fix
2. **Major Issues**: 
   - Yank release from PyPI: `python -m twine remove mcp-task-orchestrator==X.Y.Z`
   - Notify users immediately
   - Fix and release new version

## Common Issues

### Build Failures
- Check all dependencies installed
- Ensure setup.py is valid
- Clean build directories

### Upload Failures
- Verify PyPI token is correct
- Check network connectivity
- Ensure version doesn't already exist

### Import Errors After Install
- Check MANIFEST.in includes all files
- Verify package_data in setup.py
- Test in clean environment