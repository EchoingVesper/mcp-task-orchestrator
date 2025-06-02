"""
Test the role_loader module functionality.
"""

import os
import tempfile
import unittest
from pathlib import Path
import yaml

from mcp_task_orchestrator.orchestrator.role_loader import (
    find_role_files,
    load_role_file,
    get_roles
)


class TestRoleLoader(unittest.TestCase):
    """Test cases for the role_loader module."""

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
            
        # Path to the default roles file
        self.default_roles_path = Path(__file__).parent.parent / "config" / "default_roles.yaml"

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_find_role_files(self):
        """Test finding role files in project directory."""
        role_files = find_role_files(self.project_dir)
        
        # Should find at least the project role file
        self.assertIn(self.project_role_file, role_files)
        
        # Default role file should be included if it exists
        if self.default_roles_path.exists():
            self.assertIn(self.default_roles_path, role_files)
            
        # Project role file should be first in the list (higher priority)
        self.assertEqual(role_files[0], self.project_role_file)

    def test_load_role_file(self):
        """Test loading a role file."""
        roles = load_role_file(self.project_role_file)
        
        # Verify the loaded roles match what we created
        self.assertIn("task_orchestrator", roles)
        self.assertIn("test_specialist", roles)
        self.assertEqual(roles["task_orchestrator"]["role_definition"], "Test Project Task Orchestrator")
        self.assertEqual(roles["test_specialist"]["role_definition"], "Test Specialist")

    def test_get_roles_project_specific(self):
        """Test getting roles with project-specific roles available."""
        roles = get_roles(self.project_dir)
        
        # Should get project-specific roles
        self.assertIn("task_orchestrator", roles)
        self.assertIn("test_specialist", roles)
        self.assertEqual(roles["task_orchestrator"]["role_definition"], "Test Project Task Orchestrator")

    def test_get_roles_default(self):
        """Test getting roles with no project-specific roles."""
        # Create an empty directory with no role files
        empty_dir = tempfile.TemporaryDirectory()
        try:
            # If default roles exist, they should be loaded
            roles = get_roles(empty_dir.name)
            if self.default_roles_path.exists():
                self.assertNotEqual(roles, {})
            else:
                self.assertEqual(roles, {})
        finally:
            empty_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
