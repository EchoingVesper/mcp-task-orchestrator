#!/usr/bin/env python3
"""
Fix maintenance mode issue in MCP Task Orchestrator.

This script addresses the issue where the orchestrator gets stuck in maintenance mode
and cannot restart. It provides both diagnostic information and the ability to reset
the maintenance mode state.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp_task_orchestrator.reboot.reboot_integration import get_reboot_manager
from mcp_task_orchestrator.reboot.shutdown_coordinator import ShutdownManager
from mcp_task_orchestrator.orchestrator.orchestration_state_manager import StateManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def diagnose_maintenance_mode():
    """Diagnose the current maintenance mode state."""
    print("=== MCP Task Orchestrator Maintenance Mode Diagnostic ===")
    
    try:
        # Get the reboot manager
        reboot_manager = get_reboot_manager()
        
        # Check current readiness status
        readiness = await reboot_manager.get_restart_readiness()
        print(f"\nRestart Readiness: {readiness['ready']}")
        if readiness['issues']:
            print("Issues:")
            for issue in readiness['issues']:
                print(f"  - {issue}")
        
        print("\nDetails:")
        for key, value in readiness['details'].items():
            print(f"  {key}: {value}")
        
        # Get shutdown status
        shutdown_status = await reboot_manager.get_shutdown_status()
        print(f"\nShutdown Status:")
        print(f"  Phase: {shutdown_status['phase']}")
        print(f"  Progress: {shutdown_status['progress']}%")
        print(f"  Message: {shutdown_status['message']}")
        print(f"  Maintenance Mode: {shutdown_status['maintenance_mode']}")
        
        if shutdown_status['errors']:
            print("  Errors:")
            for error in shutdown_status['errors']:
                print(f"    - {error}")
        
        return shutdown_status['maintenance_mode']
        
    except Exception as e:
        logger.error(f"Failed to diagnose maintenance mode: {e}")
        return None


async def reset_maintenance_mode():
    """Reset the maintenance mode state to allow normal operation."""
    print("\n=== Resetting Maintenance Mode ===")
    
    try:
        # Get the shutdown coordinator instance
        shutdown_coordinator = ShutdownManager.get_instance()
        
        print(f"Current maintenance mode: {shutdown_coordinator.maintenance_mode}")
        print(f"Current shutdown in progress: {shutdown_coordinator._shutdown_in_progress}")
        print(f"Current phase: {shutdown_coordinator.status.phase}")
        
        # Reset maintenance mode
        if shutdown_coordinator.maintenance_mode:
            print("Resetting maintenance mode to False...")
            shutdown_coordinator.maintenance_mode = False
        
        # Reset shutdown in progress flag
        if shutdown_coordinator._shutdown_in_progress:
            print("Resetting shutdown_in_progress to False...")
            shutdown_coordinator._shutdown_in_progress = False
        
        # Reset status to idle
        from mcp_task_orchestrator.reboot.shutdown_coordinator import ShutdownPhase
        if shutdown_coordinator.status.phase != ShutdownPhase.IDLE:
            print("Resetting status phase to IDLE...")
            shutdown_coordinator.status.phase = ShutdownPhase.IDLE
            shutdown_coordinator.status.progress_percent = 0.0
            shutdown_coordinator.status.message = "Ready for shutdown"
            shutdown_coordinator.status.started_at = None
            shutdown_coordinator.status.completed_at = None
            shutdown_coordinator.status.errors = []
        
        # Clear the shutdown event to allow new shutdowns
        shutdown_coordinator.shutdown_event.clear()
        
        # Reset the singleton instance to ensure clean state
        ShutdownManager.reset_instance()
        
        print("Maintenance mode reset completed!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to reset maintenance mode: {e}")
        return False


async def test_orchestrator_health():
    """Test that the orchestrator is healthy after the fix."""
    print("\n=== Testing Orchestrator Health ===")
    
    try:
        # Try to initialize a new state manager
        state_manager = StateManager()
        print("✓ StateManager initialized successfully")
        
        # Try to get all tasks (basic functionality test)
        tasks = await state_manager.get_all_tasks()
        print(f"✓ Retrieved {len(tasks)} tasks from state manager")
        
        # Try to get a fresh reboot manager
        reboot_manager = get_reboot_manager()
        await reboot_manager.initialize(state_manager)
        print("✓ RebootManager initialized successfully")
        
        # Check readiness again
        readiness = await reboot_manager.get_restart_readiness()
        print(f"✓ Restart readiness: {readiness['ready']}")
        
        if not readiness['ready']:
            print("Issues found:")
            for issue in readiness['issues']:
                print(f"  - {issue}")
            return False
        
        print("✓ All health checks passed!")
        return True
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False


async def main():
    """Main function to diagnose and fix maintenance mode issues."""
    print("MCP Task Orchestrator Maintenance Mode Fix Script")
    print("=" * 50)
    
    # Step 1: Diagnose current state
    maintenance_mode = await diagnose_maintenance_mode()
    
    if maintenance_mode is None:
        print("❌ Failed to diagnose maintenance mode state")
        sys.exit(1)
    
    if not maintenance_mode:
        print("✓ Maintenance mode is not active - no fix needed")
        # Still run health check to ensure everything is working
        healthy = await test_orchestrator_health()
        sys.exit(0 if healthy else 1)
    
    print("⚠️  Maintenance mode is active - attempting to reset...")
    
    # Step 2: Reset maintenance mode
    reset_success = await reset_maintenance_mode()
    
    if not reset_success:
        print("❌ Failed to reset maintenance mode")
        sys.exit(1)
    
    # Step 3: Test health after reset
    healthy = await test_orchestrator_health()
    
    if healthy:
        print("\n✅ SUCCESS: Maintenance mode fixed and orchestrator is healthy!")
        sys.exit(0)
    else:
        print("\n❌ PARTIAL SUCCESS: Maintenance mode reset but health check failed")
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())