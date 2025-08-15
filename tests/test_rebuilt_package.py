#!/usr/bin/env python3
"""
Test the rebuilt package to ensure all 17 tools are available.
"""

import asyncio

async def test_rebuilt_package():
    """Test the rebuilt MCP Task Orchestrator package."""
    try:
        # Test importing from installed package
        from mcp_task_orchestrator.server import DIEnabledMCPServer
        from mcp_task_orchestrator.infrastructure.mcp.tool_definitions import get_all_tools
        
        print("✓ Successfully imported from rebuilt package")
        
        # Create server instance
        server = DIEnabledMCPServer()
        print("✓ Successfully created server instance")
        
        # Test tool loading
        tools = get_all_tools()
        print(f"✓ Successfully loaded {len(tools)} MCP tools:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i:2d}. {tool.name}")
        
        # Test server startup
        print(f"✓ Server name: {getattr(server.server, 'name', 'Unknown')}")
        
        if len(tools) == 17:
            print("\n🎉 SUCCESS: Rebuilt package has all 17 tools!")
            return True
        else:
            print(f"\n❌ ERROR: Expected 17 tools, got {len(tools)}")
            return False
        
    except Exception as e:
        print(f"✗ Error testing rebuilt package: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Rebuilt MCP Task Orchestrator Package...")
    print("=" * 55)
    
    success = asyncio.run(test_rebuilt_package())
    
    if success:
        print("\n✅ Rebuilt package is working correctly!")
        print("The package is ready for installation in Claude Code.")
    else:
        print("\n❌ Issues found with rebuilt package.")