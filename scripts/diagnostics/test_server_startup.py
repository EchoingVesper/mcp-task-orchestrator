#!/usr/bin/env python3
"""
Test server startup and basic functionality.
"""

import asyncio
import sys
import logging
import traceback
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_state_manager():
    """Test that StateManager initializes correctly."""
    try:
        from mcp_task_orchestrator.orchestrator.orchestration_state_manager import StateManager
        
        print("Testing StateManager initialization...")
        state_manager = StateManager()
        print(f"✓ StateManager created: {state_manager._initialized}")
        
        print("Testing get_all_tasks...")
        tasks = await state_manager.get_all_tasks()
        print(f"✓ Retrieved {len(tasks)} tasks")
        
        return True
        
    except Exception as e:
        print(f"❌ StateManager test failed: {e}")
        traceback.print_exc()
        return False


async def test_reboot_manager():
    """Test that reboot manager works correctly."""
    try:
        from mcp_task_orchestrator.reboot.reboot_integration import get_reboot_manager
        from mcp_task_orchestrator.orchestrator.orchestration_state_manager import StateManager
        
        print("Testing RebootManager initialization...")
        reboot_manager = get_reboot_manager()
        
        # Initialize with state manager
        state_manager = StateManager()
        await reboot_manager.initialize(state_manager)
        print("✓ RebootManager initialized")
        
        # Test health check
        readiness = await reboot_manager.get_restart_readiness()
        print(f"✓ Restart readiness: {readiness['ready']}")
        print(f"  Details: {readiness['details']}")
        
        if not readiness['ready']:
            print("  Issues:")
            for issue in readiness['issues']:
                print(f"    - {issue}")
        
        return readiness['ready']
        
    except Exception as e:
        print(f"❌ RebootManager test failed: {e}")
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("MCP Task Orchestrator Server Startup Test")
    print("=" * 50)
    
    success = True
    
    # Test 1: StateManager
    print("\n1. Testing StateManager...")
    if not await test_state_manager():
        success = False
    
    # Test 2: RebootManager  
    print("\n2. Testing RebootManager...")
    if not await test_reboot_manager():
        success = False
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! Server components are working correctly.")
        print("The maintenance mode issue should be resolved.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Further investigation needed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())