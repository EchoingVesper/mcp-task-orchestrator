"""
Test the customizable roles feature in the TaskOrchestrator and SpecialistManager.
"""

import os
import tempfile
import unittest
from pathlib import Path
import yaml
import asyncio

from mcp_task_orchestrator.orchestrator.core import TaskOrchestrator
from mcp_task_orchestrator.orchestrator.specialists import SpecialistManager
from mcp_task_orchestrator.orchestrator.state import StateManager


class TestCustomRoles(unittest.TestCase):
    """Test cases for the customizable roles feature."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)
        
        # Create a test project-specific role file
        self.project_role_file = self.project_dir / "project_roles.yaml"
        project_roles = {
            "task_orchestrator": {
                "role_definition": "Test Project Task Orchestrator",
                "expertise": ["Test expertise 1", "Test expertise 2"],
                "approach": ["Test approach 1", "Test approach 2"],
                "specialist_roles": {
                    "test_specialist": "Test specialist description"
                }
            },
            "test_specialist": {
                "role_definition": "Test Specialist",
                "expertise": ["Test expertise"],
                "approach": ["Test approach"],
                "output_format": "Test output format"
            }
        }
        with open(self.project_role_file, 'w', encoding='utf-8') as f:
            yaml.dump(project_roles, f)
        
        # Create instances for testing
        self.state_manager = StateManager(":memory:")  # Use in-memory SQLite for testing
        self.specialist_manager = SpecialistManager(project_dir=self.project_dir)
        self.orchestrator = TaskOrchestrator(
            self.state_manager, 
            self.specialist_manager,
            project_dir=self.project_dir
        )

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_specialist_manager_loads_project_roles(self):
        """Test that SpecialistManager loads project-specific roles."""
        # Verify that the specialist_config contains the project-specific roles
        self.assertIn("task_orchestrator", self.specialist_manager.specialists_config)
        self.assertIn("test_specialist", self.specialist_manager.specialists_config)
        self.assertEqual(
            self.specialist_manager.specialists_config["task_orchestrator"]["role_definition"],
            "Test Project Task Orchestrator"
        )

    def test_orchestrator_uses_project_roles(self):
        """Test that TaskOrchestrator uses project-specific roles."""
        # Run the initialize_session method and check the result
        result = asyncio.run(self.orchestrator.initialize_session())
        
        # Verify that the result contains the project-specific task orchestrator role
        self.assertEqual(result["role"], "Task Orchestrator")
        self.assertIn("Test expertise 1", result["capabilities"])
        self.assertIn("Test expertise 2", result["capabilities"])
        self.assertIn("test_specialist", result["specialist_roles"])
        self.assertEqual(
            result["specialist_roles"]["test_specialist"],
            "Test specialist description"
        )


if __name__ == "__main__":
    unittest.main()
