"""
Test the automatic example roles file creation feature.
"""

import os
import tempfile
import unittest
from pathlib import Path

from mcp_task_orchestrator.orchestrator.role_loader import (
    create_example_roles_file,
    get_roles
)


class TestExampleFileCreation(unittest.TestCase):
    """Test cases for the automatic example roles file creation feature."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_create_example_roles_file(self):
        """Test creating an example roles file."""
        success, file_path = create_example_roles_file(self.project_dir)
        
        # Should successfully create the file
        self.assertTrue(success)
        self.assertTrue(file_path.exists())
        
        # File should be named example_roles.yaml
        self.assertEqual(file_path.name, "example_roles.yaml")
        
        # File should contain commented-out content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that the file contains the expected header
        self.assertIn("# Example roles file for this project", content)
        self.assertIn("# Uncomment and modify to customize", content)
        
        # Check that the content is properly commented out
        lines = content.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                self.fail(f"Found uncommented line in example file: {line}")

    def test_get_roles_creates_example_file(self):
        """Test that get_roles creates an example file when no roles are found."""
        # Call get_roles on an empty directory
        roles = get_roles(self.project_dir)
        
        # The roles might not be empty if the default roles file exists and is loaded
        # That's okay for this test - we're just checking if the example file is created
        
        # Should create an example file
        example_file = self.project_dir / "example_roles.yaml"
        self.assertTrue(example_file.exists())
        
        # Verify file contents
        with open(example_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check that the file contains the expected header
        self.assertIn("# Example roles file for this project", content)


if __name__ == "__main__":
    unittest.main()
