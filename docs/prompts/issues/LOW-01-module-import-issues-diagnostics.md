# LOW-01: Module Import Issues in Diagnostics

## Priority: 🟡 LOW - DEVELOPMENT CONVENIENCE

## Issue Summary

Diagnostic scripts failing with `ModuleNotFoundError: No module named 'mcp_task_orchestrator'` when run directly, requiring proper Python path setup.

## Evidence

```
Traceback (most recent call last):
  File "E:\dev\mcp-servers\mcp-task-orchestrator\scripts\diagnostics\check_status.py", line 16
    from mcp_task_orchestrator.orchestrator.state import StateManager
ModuleNotFoundError: No module named 'mcp_task_orchestrator'
```

## Root Cause

- Scripts expect package to be installed in Python environment
- Direct execution doesn't add project root to Python path
- Missing environment activation or package installation

## Solutions

### Solution A: Fix Script Paths

```python
# Add to top of diagnostic scripts
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

# Now imports will work
from mcp_task_orchestrator.orchestrator.state import StateManager
```

### Solution B: Environment Setup Documentation

```bash
# Add to diagnostic script headers
# Usage:
#   cd "E:\dev\mcp-servers\mcp-task-orchestrator"
#   python -m scripts.diagnostics.check_status
# OR:
#   source venv_mcp/bin/activate  # Linux/Mac
#   venv_mcp\Scripts\activate     # Windows
#   python scripts/diagnostics/check_status.py
```

### Solution C: Wrapper Scripts

```python
# Create run_diagnostics.py in project root
import subprocess
import sys
import os

def run_diagnostic(script_name):
    script_path = os.path.join("scripts", "diagnostics", script_name)
    return subprocess.run([sys.executable, "-m", script_path.replace("/", ".").replace("\\", ".")[:-3]])
```

## Implementation Steps

1. **Fix Python path** in all diagnostic scripts
2. **Update documentation** with proper usage instructions
3. **Test all diagnostic scripts** work without environment activation

## Success Criteria

- [ ] All diagnostic scripts run without module import errors
- [ ] Clear usage instructions in script docstrings
- [ ] Works both with and without virtual environment activation

## Estimated Time: 30 minutes for fix
