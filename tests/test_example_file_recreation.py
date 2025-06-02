"""
Test script to verify the behavior of example file creation after renaming.

This script tests whether the system creates another example_roles.yaml file
after we've renamed or removed the original one.
"""

import os
import sys
import shutil
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_task_orchestrator.orchestrator.role_loader import get_roles, create_example_roles_file


def test_example_file_recreation():
    """Test if the system recreates the example_roles.yaml file after it's been renamed."""
    print("\n=== Testing Example File Recreation ===")
    
    # Get the project directory
    project_dir = Path(__file__).parent.parent
    print(f"Project directory: {project_dir}")
    
    # Check if the example_roles.yaml file exists
    example_file = project_dir / "example_roles.yaml"
    if example_file.exists():
        print(f"Example roles file already exists: {example_file}")
        print("Removing existing example file for clean test...")
        os.remove(example_file)
    
    # Check if the custom roles file exists
    custom_roles_file = project_dir / "mcp_orchestrator_roles.yaml"
    if custom_roles_file.exists():
        print(f"Custom roles file exists: {custom_roles_file}")
    else:
        print(f"ERROR: Custom roles file not found: {custom_roles_file}")
        return False
    
    # Call get_roles to trigger potential example file creation
    print("Calling get_roles to potentially trigger example file creation...")
    roles = get_roles(project_dir)
    
    # Check if the example_roles.yaml file was recreated
    if example_file.exists():
        print(f"Example roles file was recreated: {example_file}")
        print(f"File size: {example_file.stat().st_size} bytes")
        return False
    else:
        print("Example roles file was NOT recreated (expected behavior)")
    
    # Now let's explicitly try to create an example file
    print("\nExplicitly calling create_example_roles_file...")
    success, file_path = create_example_roles_file(project_dir)
    
    if success:
        print(f"Example roles file was created by explicit call: {file_path}")
        print(f"File size: {file_path.stat().st_size} bytes")
        
        # Clean up the created file
        os.remove(file_path)
        print("Cleaned up the created example file")
    else:
        print(f"Example roles file was NOT created by explicit call: {file_path}")
        if file_path.exists():
            print(f"File exists but creation reported as unsuccessful")
        
    return True


if __name__ == "__main__":
    success = test_example_file_recreation()
    if success:
        print("\nTEST PASSED: Example file recreation behavior is correct")
        sys.exit(0)
    else:
        print("\nTEST FAILED: Example file recreation behavior is incorrect")
        sys.exit(1)
