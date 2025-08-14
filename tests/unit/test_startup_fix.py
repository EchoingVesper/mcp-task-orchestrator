#!/usr/bin/env python3
"""Test to verify that the missing cleanup_stale_locks method issue is resolved."""

import sys
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_startup_fix")

def test_state_manager_cleanup():
    """Test that StateManager can now call cleanup_stale_locks without errors."""
    try:
        # Import the state manager
        from mcp_task_orchestrator.orchestrator.orchestration_state_manager import StateManager
        
        logger.info("Testing StateManager cleanup integration...")
        
        # Create a state manager
        # We'll catch any AttributeError that would occur if cleanup_stale_locks is missing
        try:
            # This will call _cleanup_stale_locks() which calls persistence.cleanup_stale_locks()
            state_manager = StateManager(base_dir=str(Path(__file__).parent))
            logger.info("✓ StateManager created successfully without AttributeError")
            
            # Test direct access to the method
            cleanup_result = state_manager.persistence.cleanup_stale_locks()
            logger.info(f"✓ Direct cleanup_stale_locks call returned: {cleanup_result}")
            
            return True
            
        except AttributeError as e:
            if "cleanup_stale_locks" in str(e):
                logger.error(f"✗ StateManager still has cleanup_stale_locks AttributeError: {str(e)}")
                return False
            else:
                # Different AttributeError, re-raise
                raise
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_state_manager_cleanup()
    if success:
        logger.info("✓ All integration tests passed! Missing method issue is resolved.")
    sys.exit(0 if success else 1)
