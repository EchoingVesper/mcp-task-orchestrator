#!/usr/bin/env python3
"""
Test script to verify that the directory bug fix works correctly.

This script tests that persistence manager, state manager, and artifact manager
all use the current working directory instead of the package directory.
"""

import os
import tempfile
import shutil
from pathlib import Path

def test_path_resolution():
    """Test that all managers correctly resolve to current working directory."""
    
    # Create a temporary directory to simulate a different project
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        
        try:
            # Change to the temporary directory
            os.chdir(temp_dir)
            print(f"Changed working directory to: {temp_dir}")
            
            # Test 1: DatabasePersistenceManager
            from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
            db_mgr = DatabasePersistenceManager()
            expected_persistence_dir = Path(temp_dir) / ".task_orchestrator"
            
            print(f"Database manager persistence dir: {db_mgr.persistence_dir}")
            print(f"Expected persistence dir: {expected_persistence_dir}")
            assert db_mgr.persistence_dir == expected_persistence_dir, f"Database manager using wrong directory: {db_mgr.persistence_dir}"
            
            # Test 2: ArtifactManager
            from mcp_task_orchestrator.orchestrator.artifacts import ArtifactManager
            artifact_mgr = ArtifactManager()
            expected_artifacts_dir = Path(temp_dir) / ".task_orchestrator" / "artifacts"
            
            print(f"Artifact manager artifacts dir: {artifact_mgr.artifacts_dir}")
            print(f"Expected artifacts dir: {expected_artifacts_dir}")
            assert artifact_mgr.artifacts_dir == expected_artifacts_dir, f"Artifact manager using wrong directory: {artifact_mgr.artifacts_dir}"
            
            # Test 3: StateManager
            from .orchestrator.orchestration_state_manager import StateManager
            state_mgr = StateManager()
            expected_state_base = Path(temp_dir)
            
            print(f"State manager base dir: {state_mgr.persistence.base_dir}")
            print(f"Expected base dir: {expected_state_base}")
            assert state_mgr.persistence.base_dir == expected_state_base, f"State manager using wrong directory: {state_mgr.persistence.base_dir}"
            
            # Cleanup the state manager
            state_mgr.persistence.dispose()
            
            print("✅ All tests passed! Directory fix is working correctly.")
            
        finally:
            # Always change back to original directory
            os.chdir(original_cwd)

if __name__ == "__main__":
    test_path_resolution()