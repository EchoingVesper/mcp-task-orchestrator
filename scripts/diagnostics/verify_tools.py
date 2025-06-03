#!/usr/bin/env python3
"""
Quick verification that all MCP Task Orchestrator tools are available.
"""

import asyncio
from mcp_task_orchestrator.server import app

async def verify_tools():
    """Verify that all expected tools are available."""
    print("Verifying MCP Task Orchestrator tools...")
    print("=" * 50)
    
    try:
        # Import the list_tools function directly from server module
        from mcp_task_orchestrator.server import list_tools
        
        # Call the async function directly
        tools = await list_tools()
        
        expected_tools = [
            "orchestrator_plan_task",
            "orchestrator_execute_subtask",
            "orchestrator_complete_subtask", 
            "orchestrator_synthesize_results",
            "orchestrator_get_status"
        ]
        
        available_tools = [tool.name for tool in tools]
        
        print(f"Found {len(available_tools)} tools:")
        for tool_name in available_tools:
            print(f"  - {tool_name}")
        
        print()
        
        # Check if all expected tools are present
        missing_tools = set(expected_tools) - set(available_tools)
        if missing_tools:
            print(f"[WARNING] Missing tools: {missing_tools}")
            return False
        else:
            print("[SUCCESS] All expected tools are available!")
            return True
            
    except Exception as e:
        print(f"[ERROR] Failed to verify tools: {e}")
        return False

def main():
    """Run the verification."""
    success = asyncio.run(verify_tools())
    
    if success:
        print("\n[READY] MCP Task Orchestrator is fully functional!")
    else:
        print("\n[ERROR] There are issues with the tool setup.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
