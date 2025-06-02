#!/usr/bin/env python3
"""
Test script for the MCP Task Orchestrator server.

This script tests that the server can be imported and initialized correctly.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to sys.path to allow importing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestServer(unittest.TestCase):
    """Test cases for the MCP Task Orchestrator server."""

    def test_imports(self):
        """Test that all required modules can be imported."""
        try:
            from mcp_task_orchestrator import server
            from mcp_task_orchestrator.orchestrator import (
                TaskOrchestrator,
                StateManager,
                SpecialistManager
            )
            from mcp_task_orchestrator.orchestrator.models import (
                TaskBreakdown,
                SubTask,
                TaskStatus
            )
            self.assertTrue(True, "All imports successful")
        except ImportError as e:
            self.fail(f"Import error: {e}")

    def test_server_initialization(self):
        """Test that the server can be initialized."""
        try:
            from mcp_task_orchestrator import server
            self.assertIsNotNone(server.app, "Server app is initialized")
            self.assertIsNotNone(server.orchestrator, "Orchestrator is initialized")
            self.assertIsNotNone(server.state_manager, "State manager is initialized")
            self.assertIsNotNone(server.specialist_manager, "Specialist manager is initialized")
        except Exception as e:
            self.fail(f"Server initialization error: {e}")

if __name__ == "__main__":
    unittest.main()