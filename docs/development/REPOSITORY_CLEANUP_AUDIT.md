# Repository Cleanup Audit Report - mcp-task-orchestrator

## Executive Summary

This comprehensive audit identifies unnecessary files, build artifacts, and improvements needed for the `.gitignore` file. The repository contains several items that should be removed before packaging for PyPI distribution.

## Files and Directories to Remove

### 1. Build Artifacts (Already in .gitignore but present in repo)
- `dist/` - Distribution artifacts (400KB)
- `build/` - Build artifacts (976KB)
- `mcp_task_orchestrator.egg-info/` - Egg info directory

**Action**: Remove these directories as they are generated during build and should not be in version control.

### 2. Virtual Environments (Major storage impact)
- `venv_test/` - Test virtual environment (35MB)
- `venv_mcp/` - MCP virtual environment (84MB)

**Action**: Remove these directories. They are already in .gitignore but were committed before being ignored.

### 3. Database Files
- `data/backups/migration_backup_20250606_041333/task_orchestrator.db`
- `data/backups/task_orchestrator_backup_20250603_053935.db`
- `tests/unit/task_orchestrator.db`

**Action**: Remove these database files. They contain user data and should not be in version control.

### 4. Backup Files
- `mcp_task_orchestrator/orchestrator/core.py.bak`
- `mcp_task_orchestrator/orchestrator/state.py.bak`
- `mcp_task_orchestrator/persistence.py.bak`

**Action**: Remove these backup files. They are redundant with version control.

### 5. Duplicate/Redundant Documentation
- `PYPI_PUBLISHING.md` - Should be in docs/development/ instead of root
- Multiple CLAUDE.md files:
  - `/CLAUDE.md` (root)
  - `/architecture/CLAUDE.md`
  - `/docs/CLAUDE.md`
  - `/mcp_task_orchestrator/CLAUDE.md`
  - `/scripts/CLAUDE.md`
  - `/tests/CLAUDE.md`

**Action**: Consolidate CLAUDE.md files into a single location.

### 6. Development/Internal Files
- `planning/files-created-this-session.md` - Session-specific file
- `archives/` directory - Contains old development scripts and reports

**Action**: Consider moving archives to a separate repository or removing if no longer needed.

## .gitignore Improvements

Add the following patterns to `.gitignore`:

```gitignore
# Backup files (currently missing)
*.bak
*.old
*.orig
*~

# Editor temporary files
*.swp
*.swo
*.swn

# OS-specific files
Thumbs.db
.Spotlight-V100
.Trashes

# Python egg files (more comprehensive)
*.egg
*.egg-info/
dist/
build/
eggs/
parts/
var/
sdist/
develop-eggs/
.installed.cfg

# Jupyter
*.ipynb_checkpoints

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# Local development
*.local
.env.local
.env.*.local

# Test coverage
coverage.xml
*.cover
.hypothesis/

# Translations
*.mo
*.pot

# Django stuff (if ever used)
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff (if ever used)
instance/
.webassets-cache

# Scrapy stuff (if ever used)
.scrapy

# Sphinx documentation
docs/_build/
docs/_static/
docs/_templates/

# PyBuilder
target/

# IPython
profile_default/
ipython_config.py

# Virtual environments (add more patterns)
venv*/
ENV*/
env*/
.venv/
.ENV/

# Package files
*.tar.gz
*.zip
*.7z
*.rar

# Security - API keys and secrets
*.pem
*.key
*.crt
*.p12
secrets/
.secrets/

# Temporary session files
*-session.md
files-created-this-session.md

# Archives (if keeping in repo)
# Uncomment if you want to ignore archives
# archives/

# Large test fixtures
test_fixtures/large/
```

## Sensitive Information Check

No obvious sensitive information (API keys, passwords, tokens) was found in the repository. However:

1. Ensure no hardcoded credentials in configuration files
2. Review `launch_scripts/claude_config.json` for any sensitive data
3. Check if database backups contain any user-specific data

## Large Files Analysis

The largest storage impacts are:
1. `venv_mcp/` - 84MB
2. `venv_test/` - 35MB
3. `archives/` directory - Contains historical scripts and reports
4. Multiple duplicate documentation files

## Recommendations

### Immediate Actions (Before PyPI Publishing)
1. **Remove all items listed in "Files and Directories to Remove"**
2. **Update .gitignore with the suggested improvements**
3. **Run `git clean -fdx` after updating .gitignore** (careful: this removes all untracked files)
4. **Consolidate duplicate documentation**
5. **Ensure no database files are included**

### Command Sequence for Cleanup
```bash
# Remove build artifacts
rm -rf dist/ build/ mcp_task_orchestrator.egg-info/

# Remove virtual environments
rm -rf venv_test/ venv_mcp/

# Remove database files
rm -f data/backups/migration_backup_20250606_041333/task_orchestrator.db
rm -f data/backups/task_orchestrator_backup_20250603_053935.db
rm -f tests/unit/task_orchestrator.db

# Remove backup files
find . -name "*.bak" -type f -delete

# Remove the session file
rm -f planning/files-created-this-session.md

# After updating .gitignore, clean untracked files
git add .gitignore
git commit -m "chore: update .gitignore with comprehensive patterns"
git clean -fdx -n  # Dry run first to see what will be removed
git clean -fdx     # Actually remove files
```

### Long-term Improvements
1. **Set up pre-commit hooks** to prevent committing build artifacts
2. **Use GitHub Actions** to automatically clean branches
3. **Document** the development setup process to avoid committing venvs
4. **Consider using** `.gitattributes` for consistent line endings
5. **Archive or remove** the `archives/` directory if historical scripts are no longer needed

## Package Size Impact

Removing the identified files will reduce the repository size by approximately:
- Virtual environments: ~119MB
- Build artifacts: ~1.4MB
- Database backups: ~1-2MB (estimated)
- Total reduction: ~122MB

This will significantly improve:
- Clone/download times
- PyPI package size
- CI/CD performance
- Developer experience

## Conclusion

The repository is generally well-organized but contains several artifacts that should be removed before PyPI distribution. The most significant issues are the committed virtual environments and build artifacts. Following the recommendations above will result in a clean, professional package suitable for public distribution.