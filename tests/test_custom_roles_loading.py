"""
Test script to verify that custom roles files are correctly loaded and used.

This script tests that the MCP Task Orchestrator correctly loads and uses
the custom roles file (mcp_orchestrator_roles.yaml) instead of the default roles.
"""

import os
import sys
import yaml
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_task_orchestrator.orchestrator.role_loader import get_roles


def test_custom_roles_loading():
    """Test that custom roles are correctly loaded from mcp_orchestrator_roles.yaml."""
    print("\n=== Testing Custom Roles Loading ===")
    
    # Get the project directory
    project_dir = Path(__file__).parent.parent
    print(f"Project directory: {project_dir}")
    
    # Check if the custom roles file exists
    custom_roles_file = project_dir / "mcp_orchestrator_roles.yaml"
    if custom_roles_file.exists():
        print(f"Custom roles file exists: {custom_roles_file}")
    else:
        print(f"ERROR: Custom roles file not found: {custom_roles_file}")
        return False
    
    # Load roles using the role_loader module
    roles = get_roles(project_dir)
    
    # Check if roles were loaded
    if not roles:
        print("ERROR: No roles were loaded")
        return False
    
    print(f"Loaded roles: {list(roles.keys())}")
    
    # Check if custom specialist roles are present
    expected_custom_roles = [
        "mcp_architect", 
        "feature_implementer", 
        "protocol_specialist",
        "client_integrator",
        "documentation_writer",
        "test_engineer"
    ]
    
    missing_roles = [role for role in expected_custom_roles if role not in roles]
    if missing_roles:
        print(f"ERROR: Missing custom roles: {missing_roles}")
        return False
    
    # Check if task_orchestrator has the custom specialist_roles
    if "task_orchestrator" in roles and "specialist_roles" in roles["task_orchestrator"]:
        specialist_roles = roles["task_orchestrator"]["specialist_roles"]
        print(f"Task Orchestrator specialist roles: {list(specialist_roles.keys())}")
        
        missing_specialist_roles = [role for role in expected_custom_roles if role not in specialist_roles]
        if missing_specialist_roles:
            print(f"ERROR: Missing specialist roles in task_orchestrator: {missing_specialist_roles}")
            return False
    else:
        print("ERROR: task_orchestrator or specialist_roles not found")
        return False
    
    # Verify that the custom role definitions are loaded correctly
    if "mcp_architect" in roles:
        role_def = roles["mcp_architect"]["role_definition"]
        if "MCP Protocol Architect" in role_def:
            print("Custom role definition for mcp_architect loaded correctly")
        else:
            print(f"ERROR: Unexpected role definition for mcp_architect: {role_def}")
            return False
    
    print("All custom roles loaded successfully!")
    return True


if __name__ == "__main__":
    success = test_custom_roles_loading()
    if success:
        print("\nTEST PASSED: Custom roles file is correctly loaded and used")
        sys.exit(0)
    else:
        print("\nTEST FAILED: Custom roles file is not correctly loaded or used")
        sys.exit(1)
