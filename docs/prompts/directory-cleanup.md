# MCP Task Orchestrator - Directory Cleanup and Organization

## Context
The project directory has accumulated test files, diagnostic scripts, and various artifacts that should be properly organized. This prompt guides cleaning up and organizing the project structure.

## Current Directory Issues

### Test Files in Root Directory
- `test_synchronization_fix.py` - Complex synchronization test
- `simple_sync_test.py` - Basic import and operation test  
- `quick_sync_test.py` - Core operation testing
- `test_complete_subtask.py` - Full pipeline testing

### Diagnostic/Development Files in Root
- `diagnose_db.py` - Database analysis utility
- `test_cleanup_locks.py` - Lock cleanup testing
- `test_artifacts_fix.py` - Artifacts validation testing
- `migrate_artifacts.py` - Migration script for artifacts format

### Log Files
- `server_diagnosis.log` - Server diagnostic output
- Various other `.log` files

## Required Cleanup Actions

### 1. Create Proper Directory Structure

```
MCP Task Orchestrator/
├── docs/
│   ├── development/          # Development notes and guides
│   ├── testing/              # Testing documentation  
│   ├── troubleshooting/      # Diagnostic guides
│   └── prompts/              # Context prompts (already exists)
├── tests/
│   ├── integration/          # Integration tests
│   ├── unit/                 # Unit tests
│   └── performance/          # Performance tests
├── scripts/
│   ├── diagnostics/          # Diagnostic utilities
│   ├── migrations/           # Database migration scripts
│   └── maintenance/          # Maintenance scripts
├── logs/                     # Log files (gitignored)
└── [main project files]
```

### 2. File Reorganization

#### Move Test Files to `tests/`
```bash
# Integration tests
mv test_synchronization_fix.py tests/integration/
mv test_complete_subtask.py tests/integration/

# Performance tests  
mv simple_sync_test.py tests/performance/
mv quick_sync_test.py tests/performance/

# Unit tests
mv test_cleanup_locks.py tests/unit/
mv test_artifacts_fix.py tests/unit/
```

#### Move Scripts to `scripts/`
```bash
# Diagnostic utilities
mv diagnose_db.py scripts/diagnostics/

# Migration scripts
mv migrate_artifacts.py scripts/migrations/

# Any other utility scripts
```

#### Move Logs to `logs/`
```bash
# Create logs directory and move log files
mkdir -p logs/
mv *.log logs/
mv server_diagnosis.log logs/
```

### 3. Create Documentation Files

#### `docs/development/synchronization-fixes.md`
Document the synchronization work completed:
- Overview of issues that were fixed
- Architecture decisions made
- Performance improvements achieved
- Future optimization recommendations

#### `docs/testing/test-suite-guide.md`
Document the test suite:
- How to run different types of tests
- What each test validates
- Expected performance benchmarks
- Troubleshooting test failures

#### `docs/troubleshooting/database-issues.md`
Document database troubleshooting:
- Common database performance issues
- How to use diagnostic scripts
- Interpreting log files
- Database maintenance procedures

### 4. Update .gitignore

Add proper ignore patterns:
```gitignore
# Logs
logs/
*.log
server_diagnosis.log

# Test outputs
test_results/
performance_reports/

# Database files (if needed)
*.db-journal
*.db-wal

# Python cache
__pycache__/
*.pyc
*.pyo

# Development artifacts
.vscode/
.idea/
*.swp
*.swo
```

### 5. Create Helper Scripts

#### `scripts/run-tests.py`
```python
#!/usr/bin/env python3
"""Run test suite with proper organization."""
import subprocess
import sys
from pathlib import Path

def run_performance_tests():
    """Run performance tests."""
    # Implementation to run tests in tests/performance/
    
def run_integration_tests():
    """Run integration tests."""
    # Implementation to run tests in tests/integration/
    
def run_all_tests():
    """Run complete test suite."""
    # Implementation to run all tests with reporting
```

#### `scripts/diagnostics/analyze-system.py`
```python
#!/usr/bin/env python3
"""Comprehensive system diagnostic script."""
# Combine functionality from diagnose_db.py and other diagnostic tools
```

### 6. README Updates

Update the main README.md to reflect new structure:
- Document the tests/ directory and how to run tests
- Explain the scripts/ directory utilities
- Reference docs/ for detailed documentation
- Add troubleshooting section pointing to docs/troubleshooting/

## Implementation Checklist

- [ ] Create directory structure (`docs/`, `tests/`, `scripts/`, `logs/`)
- [ ] Move test files to appropriate `tests/` subdirectories
- [ ] Move utility scripts to `scripts/` subdirectories  
- [ ] Move log files to `logs/` directory
- [ ] Create documentation files in `docs/`
- [ ] Update .gitignore with proper patterns
- [ ] Create helper scripts for testing and diagnostics
- [ ] Update README.md with new directory structure
- [ ] Test that moved files still work from new locations
- [ ] Update any import paths that may have changed

## Benefits of This Cleanup

1. **Professional Organization**: Clean project structure following Python best practices
2. **Easy Navigation**: Developers can quickly find tests, docs, and utilities
3. **Better Maintenance**: Separation of concerns makes maintenance easier
4. **Improved Onboarding**: New developers can understand project structure quickly
5. **CI/CD Ready**: Organized test structure ready for automated testing
6. **Documentation Clarity**: Proper docs organization for different audiences

## Files to Keep in Root

Only keep essential project files in root:
- `README.md`
- `setup.py` or `pyproject.toml` 
- `.gitignore`
- Main package directory (`mcp_task_orchestrator/`)
- Configuration files (`config/` if exists)

Everything else should be organized into appropriate subdirectories.
