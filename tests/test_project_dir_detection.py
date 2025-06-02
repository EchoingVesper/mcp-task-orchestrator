"""
Test script to verify project directory detection in the MCP Task Orchestrator.

This script creates a temporary directory with a custom roles file and verifies
that the MCP server correctly detects and uses it.
"""

import os
import tempfile
import shutil
from pathlib import Path
import yaml
import asyncio
import json

from mcp_task_orchestrator.orchestrator.role_loader import create_example_roles_file, get_roles


async def simulate_mcp_request(project_dir):
    """Simulate an MCP request with a specific project directory."""
    print(f"\nSimulating MCP request for project directory: {project_dir}")
    
    # Create a test project directory
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
    
    # Check if an example roles file exists
    example_file = Path(project_dir) / "example_roles.yaml"
    if not example_file.exists():
        print("Creating example roles file...")
        success, file_path = create_example_roles_file(project_dir)
        if success:
            print(f"Created example roles file at: {file_path}")
        else:
            print(f"Failed to create example roles file")
    else:
        print(f"Example roles file already exists at: {example_file}")
    
    # Get roles for the project directory
    roles = get_roles(project_dir)
    if roles:
        print(f"Found roles: {list(roles.keys())}")
    else:
        print("No roles found, but example file should have been created")
    
    # Check if the example roles file exists now
    example_file = Path(project_dir) / "example_roles.yaml"
    if example_file.exists():
        print(f"Example roles file exists at: {example_file}")
        print(f"File size: {example_file.stat().st_size} bytes")
        
        # Read the first few lines of the file
        with open(example_file, 'r', encoding='utf-8') as f:
            first_lines = [next(f) for _ in range(5)]
        print("First few lines of the example file:")
        for line in first_lines:
            print(f"  {line.rstrip()}")
    else:
        print("Example roles file does not exist")


async def main():
    """Run the test script."""
    # Test with the current directory
    current_dir = os.getcwd()
    await simulate_mcp_request(current_dir)
    
    # Test with a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        await simulate_mcp_request(temp_dir)
    
    # Test with a specific project directory
    # Change this to the directory you want to test with
    test_project_dir = os.path.join(os.path.dirname(os.getcwd()), "TestProject")
    await simulate_mcp_request(test_project_dir)


if __name__ == "__main__":
    asyncio.run(main())
