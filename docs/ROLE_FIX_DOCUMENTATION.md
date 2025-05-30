# Role File Location Fix

## Problem Fixed

The MCP Task Orchestrator was creating role configuration files in the wrong location:

**Before (Bug):** 
- `mcp_orchestrator_roles.yaml` created in orchestrator's base directory
- Could not customize roles per project
- All projects shared the same roles

**After (Fixed):**
- Project-specific roles created in `.task_orchestrator/roles/project_roles.yaml` 
- Each project can have its own custom specialist roles
- Proper per-project configuration isolation

## What Changed

### 1. Fixed Directory Path Bug
In `mcp_task_orchestrator/orchestrator/specialists.py`:
```python
# BEFORE (Bug):
self.persistence_dir = self.base_dir / ".task_orchestrator"

# AFTER (Fixed):
self.persistence_dir = Path(self.project_dir) / ".task_orchestrator"
```

### 2. Improved Role File Creation
In `mcp_task_orchestrator/orchestrator/role_loader.py`:
- Renamed `create_example_roles_file()` to `create_project_roles_file()`
- Creates files in `.task_orchestrator/roles/` directory
- Files are immediately usable (not commented out)
- Clear instructions for customization in file header

### 3. Enhanced Role Loading Priority
Updated `find_role_files()` to check directories in this order:
1. `.task_orchestrator/roles/*.yaml` (highest priority - project-specific)
2. `*_roles.yaml` in project root
3. Default roles as fallback

## How It Works Now

### When You Start a New Project:
1. Initialize orchestration in any directory
2. System automatically creates `.task_orchestrator/roles/project_roles.yaml`
3. File contains all default roles, ready for customization

### To Customize Roles for Your Project:
1. Edit `.task_orchestrator/roles/project_roles.yaml`
2. Modify existing roles or add new ones
3. Save the file - changes take effect immediately

### Example Project Structure:
```
my-project/
├── .task_orchestrator/
│   └── roles/
│       └── project_roles.yaml  ← Customize this file
├── src/
├── tests/
└── README.md
```

## Testing the Fix

Run the test script to verify the fix works:
```bash
python test_role_fix.py
```

Expected output shows project roles being created in the correct location.

## Benefits

1. **Per-project customization**: Each project can have specialized roles
2. **Clean separation**: No more global role pollution
3. **Easy customization**: Clear file with instructions
4. **Automatic setup**: Works out of the box for new projects
5. **Version control friendly**: Project roles can be committed with your code

## Migration

If you have the old `mcp_orchestrator_roles.yaml` file in the base directory:
1. Copy the content you want to keep
2. Delete the old file 
3. Start a new orchestration session in your project
4. Edit the new `.task_orchestrator/roles/project_roles.yaml` file with your customizations

Your project-specific role customizations will now work as intended!
