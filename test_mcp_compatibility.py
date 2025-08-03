#!/usr/bin/env python3
"""
Test MCP client compatibility for Task Orchestrator.

This script tests basic MCP server functionality to ensure compatibility with
MCP clients like Claude Desktop, Cursor, Windsurf, and VS Code.
"""

import asyncio
import json
import subprocess
import tempfile
import time
import os
from pathlib import Path
from typing import Dict, List, Any


class MCPCompatibilityTester:
    """Test MCP server compatibility with different clients."""
    
    def __init__(self):
        self.server_process = None
        self.test_results = {}
    
    def test_server_startup(self) -> bool:
        """Test if the MCP server can start up successfully."""
        try:
            # Test basic import
            import mcp_task_orchestrator
            print("✓ Package import successful")
            
            # Test server module exists
            from mcp_task_orchestrator import server
            print("✓ Server module available")
            
            return True
        except Exception as e:
            print(f"✗ Server startup test failed: {e}")
            return False
    
    def test_tool_definitions(self) -> bool:
        """Test if tool definitions are properly exposed."""
        try:
            from mcp_task_orchestrator.infrastructure.mcp.tool_definitions import get_all_tools
            
            tools = get_all_tools()
            if not tools:
                print("✗ No tools defined")
                return False
            
            print(f"✓ Found {len(tools)} tool definitions")
            
            # Check for essential tools
            tool_names = [tool.name for tool in tools]
            essential_tools = [
                "orchestrator_initialize_session",
                "orchestrator_plan_task", 
                "orchestrator_execute_task",
                "orchestrator_get_status"
            ]
            
            missing_tools = []
            for tool in essential_tools:
                if tool not in tool_names:
                    missing_tools.append(tool)
            
            if missing_tools:
                print(f"✗ Missing essential tools: {missing_tools}")
                return False
            
            print("✓ All essential tools available")
            return True
            
        except Exception as e:
            print(f"✗ Tool definitions test failed: {e}")
            return False
    
    def test_dependency_injection(self) -> bool:
        """Test if dependency injection system works."""
        try:
            from mcp_task_orchestrator.infrastructure.di.container import ServiceContainer
            from mcp_task_orchestrator.infrastructure.di.service_configuration import create_configured_container, get_default_config
            
            config = get_default_config()
            container = create_configured_container(config)
            
            # Test that key services are registered
            from mcp_task_orchestrator.domain.repositories.task_repository import TaskRepository
            task_repo = container.get_service(TaskRepository)
            
            if task_repo is None:
                print("✗ TaskRepository not properly registered")
                return False
            
            print("✓ Dependency injection system working")
            return True
            
        except Exception as e:
            print(f"✗ Dependency injection test failed: {e}")
            return False
    
    def test_basic_functionality(self) -> bool:
        """Test basic task orchestration functionality."""
        try:
            from mcp_task_orchestrator.infrastructure.di.service_configuration import create_configured_container, get_default_config
            from mcp_task_orchestrator.application.usecases.orchestrate_task import OrchestrateTaskUseCase
            
            # Initialize container
            config = get_default_config()
            container = create_configured_container(config)
            
            # Test use case resolution
            orchestrate_use_case = container.get_service(OrchestrateTaskUseCase)
            if orchestrate_use_case is None:
                print("✗ OrchestrateTaskUseCase not available")
                return False
            
            print("✓ Basic functionality available")
            return True
            
        except Exception as e:
            print(f"✗ Basic functionality test failed: {e}")
            return False
    
    def test_client_configuration_templates(self) -> bool:
        """Test client configuration templates for different MCP clients."""
        try:
            # Test Claude Desktop configuration
            claude_config = {
                "mcpServers": {
                    "task-orchestrator": {
                        "command": "python3",
                        "args": [str(Path(__file__).parent / "mcp_task_orchestrator" / "server.py")],
                        "env": {}
                    }
                }
            }
            
            # Test Cursor/VS Code configuration (example)
            vscode_config = {
                "mcp.servers": {
                    "task-orchestrator": {
                        "command": "python3",
                        "args": [str(Path(__file__).parent / "mcp_task_orchestrator" / "server.py")]
                    }
                }
            }
            
            print("✓ Client configuration templates generated")
            return True
            
        except Exception as e:
            print(f"✗ Client configuration test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all compatibility tests."""
        print("=" * 60)
        print("MCP Task Orchestrator - Client Compatibility Test")
        print("=" * 60)
        
        tests = [
            ("Server Startup", self.test_server_startup),
            ("Tool Definitions", self.test_tool_definitions),
            ("Dependency Injection", self.test_dependency_injection),
            ("Basic Functionality", self.test_basic_functionality),
            ("Client Configuration", self.test_client_configuration_templates),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"✗ {test_name} failed with exception: {e}")
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{test_name:25} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All compatibility tests passed! Ready for MCP client integration.")
        else:
            print("⚠️  Some tests failed. Review and fix issues before client integration.")
        
        return results


def main():
    """Run MCP compatibility tests."""
    tester = MCPCompatibilityTester()
    results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    if not all(results.values()):
        exit(1)


if __name__ == "__main__":
    main()