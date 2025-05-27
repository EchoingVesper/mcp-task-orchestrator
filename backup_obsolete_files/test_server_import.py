#!/usr/bin/env python3
"""
Test script to diagnose MCP server import issues
"""
import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test if all required modules can be imported"""
    print(f"Testing imports from: {src_path}")
    
    try:
        print("✓ Testing basic Python imports...")
        import asyncio
        import json
        from typing import Any, Dict, List, Optional
        print("✓ Basic imports successful")
        
        print("✓ Testing MCP imports...")
        import mcp.types as types
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        print("✓ MCP imports successful")
        
        print("✓ Testing orchestrator imports...")
        from orchestrator.core import TaskOrchestrator
        from orchestrator.models import TaskBreakdown, SubTask, TaskStatus
        from orchestrator.specialists import SpecialistManager
        from orchestrator.state import StateManager
        print("✓ Orchestrator imports successful")
        
        print("✓ Testing server creation...")
        app = Server("task-orchestrator")
        print("✓ Server creation successful")
        
        print("🎉 All imports successful! Server should work.")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
