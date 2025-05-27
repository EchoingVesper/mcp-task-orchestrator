#!/usr/bin/env python3
"""
Test MCP protocol functionality for the Task Orchestrator
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_task_orchestrator.server import app


async def test_mcp_protocol():
    """Test the MCP protocol tools."""
    print("Testing MCP Protocol functionality...")
    
    try:
        # Test list_tools
        print("\nTesting list_tools()...")
        tools = await app.list_tools()
        
        print(f"[OK] Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test orchestrator_plan_task tool call
        print("\nTesting orchestrator_plan_task tool call...")
        
        # Simulate a tool call
        tool_call_args = {
            "description": "Fix a memory leak in a Python web application",
            "complexity_level": "complex",
            "context": "FastAPI application with database connections"
        }
        
        result = await app.call_tool(
            name="orchestrator_plan_task",
            arguments=tool_call_args
        )
        
        print(f"[OK] Tool call successful, returned {len(result)} content items")
        
        # Parse the result
        response_text = result[0].text
        response_data = json.loads(response_text)
        
        breakdown = response_data["task_breakdown"]
        print(f"[OK] Task breakdown with {breakdown['total_subtasks']} subtasks created")
        
        # Test executing a subtask
        if breakdown["subtasks"]:
            first_subtask_id = breakdown["subtasks"][0]["task_id"]
            print(f"\nTesting orchestrator_execute_subtask for: {first_subtask_id}")
            
            result = await app.call_tool(
                name="orchestrator_execute_subtask",
                arguments={"task_id": first_subtask_id}
            )
            
            specialist_context = result[0].text
            print(f"[OK] Specialist context generated ({len(specialist_context)} chars)")
        
        # Test get_status
        print("\nTesting orchestrator_get_status...")
        result = await app.call_tool(
            name="orchestrator_get_status",
            arguments={"include_completed": False}
        )
        
        status_data = json.loads(result[0].text)
        print(f"[OK] Status: {status_data['active_tasks']} active, {status_data['pending_tasks']} pending")
        
        print("\n[SUCCESS] All MCP protocol tests passed!")
        return True
        
    except Exception as e:
        print(f"[FAILED] MCP protocol test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_protocol())
    sys.exit(0 if success else 1)
