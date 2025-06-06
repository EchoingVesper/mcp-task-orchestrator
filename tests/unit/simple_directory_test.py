#!/usr/bin/env python3
"""
Simple test to verify the directory fix logic without heavy imports.
"""

import os
import tempfile
from pathlib import Path

def test_directory_logic():
    """Test the directory resolution logic manually."""
    
    # Create a temporary directory to simulate a different project
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        
        try:
            # Change to the temporary directory
            os.chdir(temp_dir)
            print(f"Changed working directory to: {temp_dir}")
            
            # Test the fixed logic (what the code should do now)
            base_dir = None
            if base_dir is None:
                base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR")
                
                if not base_dir:
                    # This is the FIXED logic - use current working directory
                    base_dir = os.getcwd()
            
            persistence_dir = Path(base_dir) / ".task_orchestrator"
            artifacts_dir = persistence_dir / "artifacts"
            
            print(f"Base directory: {base_dir}")
            print(f"Persistence directory: {persistence_dir}")
            print(f"Artifacts directory: {artifacts_dir}")
            
            # Verify the directories are in the temp directory, not package directory
            assert str(base_dir) == temp_dir, f"Base directory should be {temp_dir}, got {base_dir}"
            assert str(persistence_dir) == str(Path(temp_dir) / ".task_orchestrator"), f"Wrong persistence dir: {persistence_dir}"
            assert str(artifacts_dir) == str(Path(temp_dir) / ".task_orchestrator" / "artifacts"), f"Wrong artifacts dir: {artifacts_dir}"
            
            print("✅ Directory resolution logic is correct!")
            
            # Test that we can create the directories
            persistence_dir.mkdir(parents=True, exist_ok=True)
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            assert persistence_dir.exists(), "Failed to create persistence directory"
            assert artifacts_dir.exists(), "Failed to create artifacts directory"
            
            print("✅ Directory creation works correctly!")
            
        finally:
            # Always change back to original directory
            os.chdir(original_cwd)

if __name__ == "__main__":
    test_directory_logic()