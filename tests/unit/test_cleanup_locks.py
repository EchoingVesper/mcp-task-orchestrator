#!/usr/bin/env python3
"""Test script for the cleanup_stale_locks method implementation."""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
from mcp_task_orchestrator.db.models import LockTrackingModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_cleanup_locks")

def test_cleanup_stale_locks():
    """Test the cleanup_stale_locks method implementation."""
    try:
        # Create persistence manager
        db_path = Path(__file__).parent / "task_orchestrator.db"
        db_url = f"sqlite:///{db_path}"
        persistence = DatabasePersistenceManager(base_dir=str(Path(__file__).parent), db_url=db_url)
        
        logger.info("Testing cleanup_stale_locks method...")
        
        # Test 1: Check that method exists and is callable
        if not hasattr(persistence, 'cleanup_stale_locks'):
            logger.error("✗ cleanup_stale_locks method not found")
            return False
        
        if not callable(getattr(persistence, 'cleanup_stale_locks')):
            logger.error("✗ cleanup_stale_locks is not callable")
            return False
        
        logger.info("✓ cleanup_stale_locks method exists and is callable")
        
        # Test 2: Call the method with default parameters
        try:
            result = persistence.cleanup_stale_locks()
            logger.info(f"✓ cleanup_stale_locks() returned: {result}")
            
            if not isinstance(result, int):
                logger.error(f"✗ Expected int return value, got {type(result)}")
                return False
            
            if result < 0:
                logger.error(f"✗ Expected non-negative return value, got {result}")
                return False
                
        except Exception as e:
            logger.error(f"✗ cleanup_stale_locks() failed: {str(e)}")
            return False
        
        # Test 3: Call with custom max_age_seconds
        try:
            result = persistence.cleanup_stale_locks(max_age_seconds=120)  # 2 minutes
            logger.info(f"✓ cleanup_stale_locks(120) returned: {result}")
            
        except Exception as e:
            logger.error(f"✗ cleanup_stale_locks(120) failed: {str(e)}")
            return False
        
        # Test 4: Test with very large max_age (should clean up all locks)
        try:
            result = persistence.cleanup_stale_locks(max_age_seconds=0)  # Clean up all
            logger.info(f"✓ cleanup_stale_locks(0) returned: {result}")
            
        except Exception as e:
            logger.error(f"✗ cleanup_stale_locks(0) failed: {str(e)}")
            return False
        
        logger.info("✓ All cleanup_stale_locks tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_cleanup_stale_locks()
    sys.exit(0 if success else 1)
