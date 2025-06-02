#!/usr/bin/env python3
"""
Test script to verify the role file creation fix works correctly.
"""

import os
import tempfile
import shutil
from pathlib import Path

# Add the project to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from mcp_task_orchestrator.orchestrator.role_loader import get_roles

def test_role_creation():
    """Test that roles are created in the correct location."""
    
    # Create a temporary directory to simulate a project
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing role creation in: {temp_dir}")
        
        # Change to the temporary directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Call get_roles - this should create the project roles file
            roles = get_roles(temp_dir)
            
            # Check if the roles directory was created in the right place
            roles_dir = Path(temp_dir) / ".task_orchestrator" / "roles"
            project_roles_file = roles_dir / "project_roles.yaml"
            
            print(f"Roles directory exists: {roles_dir.exists()}")
            print(f"Project roles file exists: {project_roles_file.exists()}")
            
            if project_roles_file.exists():
                print(f"✅ SUCCESS: Project roles file created at: {project_roles_file}")
                print(f"File size: {project_roles_file.stat().st_size} bytes")
                
                # Read the first few lines to verify content
                with open(project_roles_file, 'r') as f:
                    first_lines = [f.readline().strip() for _ in range(5)]
                print("First few lines of the file:")
                for i, line in enumerate(first_lines, 1):
                    print(f"  {i}: {line}")
                
                return True
            else:
                print("❌ FAILED: Project roles file was not created")
                return False
                
        finally:
            os.chdir(original_cwd)

def test_role_loading():
    """Test that project-specific roles are loaded correctly."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\nTesting role loading in: {temp_dir}")
        
        # Create a custom roles file
        roles_dir = Path(temp_dir) / ".task_orchestrator" / "roles"
        roles_dir.mkdir(parents=True)
        
        custom_roles_file = roles_dir / "custom_roles.yaml"
        custom_content = """
task_orchestrator:
  role_definition: "Test Custom Task Orchestrator"
  expertise:
    - "Custom expertise 1"
    - "Custom expertise 2"
  specialist_roles:
    custom_specialist: "Custom specialist description"

custom_specialist:
  role_definition: "Test Custom Specialist"
  expertise:
    - "Custom specialist expertise"
  approach:
    - "Custom approach"
"""
        
        with open(custom_roles_file, 'w') as f:
            f.write(custom_content)
        
        # Load roles and verify custom content is used
        roles = get_roles(temp_dir)
        
        if roles and 'task_orchestrator' in roles:
            task_orch = roles['task_orchestrator']
            if task_orch.get('role_definition') == "Test Custom Task Orchestrator":
                print("✅ SUCCESS: Custom roles loaded correctly")
                print(f"Custom role definition: {task_orch.get('role_definition')}")
                return True
            else:
                print("❌ FAILED: Custom roles not loaded properly")
                print(f"Got role definition: {task_orch.get('role_definition')}")
                return False
        else:
            print("❌ FAILED: No roles loaded")
            return False

if __name__ == "__main__":
    print("Testing role file creation and loading...")
    
    test1_result = test_role_creation()
    test2_result = test_role_loading()
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! The role fix is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
