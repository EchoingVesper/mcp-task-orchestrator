# Fix Persistence Test Imports

**Task ID**: `cicd-import-01`  
**Type**: Fix Implementation  
**Local LLM Ready**: ✅ High  
**Estimated Duration**: 15 minutes  
**Priority**: 🔴 Critical

## Objective

Fix import errors in `tests/unit/test_persistence.py` that prevent test collection.

## Current Error

```
ImportError: attempted relative import with no known parent package
tests/unit/test_persistence.py:19: in <module>
    from .orchestrator.orchestration_state_manager import StateManager
```

## Specific Changes Required

**File**: `tests/unit/test_persistence.py`

**Replace this import (line 19)**:
```python
from .orchestrator.orchestration_state_manager import StateManager
```

**With absolute import**:
```python
from mcp_task_orchestrator.orchestrator.orchestration_state_manager import StateManager
```

## Additional Import Fixes Needed

Review and fix any other relative imports in the same file following the pattern:
- `from .something` → `from mcp_task_orchestrator.something`
- `from ..something` → `from mcp_task_orchestrator.something`

## Validation

**Test the fix**:
```bash
python -m pytest tests/unit/test_persistence.py --collect-only
```

**Expected Result**: No import errors during collection

## Success Criteria

- [ ] All relative imports replaced with absolute imports
- [ ] Test collection succeeds without import errors
- [ ] File maintains same functionality
- [ ] Code follows project import standards

## Local LLM Prompt Template

```
Fix Python import errors in this file:

FILE_PATH: tests/unit/test_persistence.py
CURRENT_IMPORTS: {current_imports}
PACKAGE_STRUCTURE: mcp_task_orchestrator/

Convert all relative imports to absolute imports:
- Replace relative imports (from .module) with absolute imports (from mcp_task_orchestrator.module)
- Ensure imports match actual package structure
- Preserve all other code unchanged

Return the complete fixed file content.
```

## Agent Instructions

1. Read current file content
2. Identify all relative imports  
3. Replace with absolute imports using `mcp_task_orchestrator.` prefix
4. Validate test collection works
5. Commit fix with clear message