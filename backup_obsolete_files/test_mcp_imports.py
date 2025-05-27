#!/usr/bin/env python3
"""
Quick test to verify MCP imports work with the specified Python executable
"""

import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")

try:
    import mcp.types as types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    print("✅ MCP imports successful!")
except ImportError as e:
    print(f"❌ MCP import failed: {e}")
    sys.exit(1)

try:
    # Test creating a server
    app = Server("test-server")
    print("✅ MCP Server creation successful!")
except Exception as e:
    print(f"❌ MCP Server creation failed: {e}")
    sys.exit(1)

print("🎉 All MCP components working correctly!")
