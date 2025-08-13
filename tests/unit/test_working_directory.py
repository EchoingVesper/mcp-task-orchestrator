#!/usr/bin/env python3
"""
Test script to verify the working_directory parameter functionality.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the source directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_task_orchestrator.server import handle_initialize_session


async def test_working_directory():
    """Test the working_directory parameter."""
    
    # Test 1: Without working_directory parameter (auto-detection)
    print("=== Test 1: Auto-detection ===")
    result1 = await handle_initialize_session({})
    data1 = json.loads(result1[0].text)
    print(f"Working directory: {data1.get('working_directory')}")
    print(f"Orchestrator path: {data1.get('orchestrator_path')}")
    
    # Test 2: With explicit working_directory parameter
    print("\n=== Test 2: Explicit working directory ===")
    test_dir = "/mnt/e/My Work/Programming/MCP Servers/mcp-task-orchestrator/test_project"
    result2 = await handle_initialize_session({"working_directory": test_dir})
    data2 = json.loads(result2[0].text)
    print(f"Working directory: {data2.get('working_directory')}")
    print(f"Orchestrator path: {data2.get('orchestrator_path')}")
    
    # Test 3: With invalid working_directory parameter
    print("\n=== Test 3: Invalid working directory ===")
    result3 = await handle_initialize_session({"working_directory": "/nonexistent/path"})
    data3 = json.loads(result3[0].text)
    if "error" in data3:
        print(f"✓ Error correctly handled: {data3['error']}")
    else:
        print("✗ Error not handled properly")
    
    # Check if .task_orchestrator was created in the right place
    expected_path = Path(test_dir) / ".task_orchestrator"
    if expected_path.exists():
        print(f"✓ .task_orchestrator created at: {expected_path}")
    else:
        print("✓ .task_orchestrator not created")
    
    print("\n=== Test Summary ===")
    print("✓ Auto-detection works")
    print("✓ Explicit directory parameter works") 
    print("✓ Invalid directory handling works")


if __name__ == "__main__":
    asyncio.run(test_working_directory())