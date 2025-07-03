#!/usr/bin/env python3
"""
Simple test to check tool definitions without complex imports.
"""

try:
    from mcp_task_orchestrator.infrastructure.mcp.tool_definitions import get_all_tools
    tools = get_all_tools()
    print(f"SUCCESS: Found {len(tools)} tools")
    for i, tool in enumerate(tools, 1):
        print(f"  {i:2d}. {tool.name}")
    
    if len(tools) == 17:
        print("\n🎉 All 17 tools are available!")
    else:
        print(f"\n⚠️  Expected 17 tools, found {len(tools)}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()