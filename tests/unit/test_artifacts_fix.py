#!/usr/bin/env python3
"""Test script to verify that artifacts validation issues are fixed."""

import sys
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_artifacts_fix")

def test_artifacts_validation():
    """Test that previously problematic tasks can now be loaded."""
    try:
        # Create persistence manager
        db_path = Path(__file__).parent / "task_orchestrator.db"
        db_url = f"sqlite:///{db_path}"
        persistence = DatabasePersistenceManager(base_dir=str(Path(__file__).parent), db_url=db_url)
        
        # Test loading the previously problematic tasks
        problematic_task_ids = ['task_159abae8', 'task_56e556bb']
        
        for task_id in problematic_task_ids:
            logger.info(f"Testing task {task_id}...")
            
            try:
                breakdown = persistence.load_task_breakdown(task_id)
                if breakdown:
                    logger.info(f"✓ Successfully loaded {task_id}")
                    logger.info(f"  - Description: {breakdown.description}")
                    logger.info(f"  - Subtasks: {len(breakdown.subtasks)}")
                    
                    # Check each subtask's artifacts
                    for subtask in breakdown.subtasks:
                        logger.info(f"  - Subtask {subtask.task_id}: {subtask.artifacts}")
                        
                        # Verify artifacts is a list
                        if not isinstance(subtask.artifacts, list):
                            logger.error(f"  ✗ Artifacts not a list: {type(subtask.artifacts)}")
                            return False
                        
                else:
                    logger.warning(f"Task {task_id} not found")
                    
            except Exception as e:
                logger.error(f"✗ Failed to load {task_id}: {str(e)}")
                return False
        
        logger.info("✓ All tests passed! Artifacts validation issues are fixed.")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_artifacts_validation()
    sys.exit(0 if success else 1)
