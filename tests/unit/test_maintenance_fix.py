#!/usr/bin/env python3
"""Test script to verify the maintenance coordinator fix."""

import sys
import asyncio
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_maintenance_coordinator():
    """Test the maintenance coordinator fix directly."""
    
    print("=== Testing MaintenanceCoordinator Fix ===\n")
    
    try:
        # Import required modules
        from mcp_task_orchestrator.orchestrator.orchestration_state_manager import StateManager
        from mcp_task_orchestrator.orchestrator.task_orchestration_service import TaskOrchestrator
        from mcp_task_orchestrator.orchestrator.specialist_management_service import SpecialistManager
        from mcp_task_orchestrator.orchestrator.maintenance import MaintenanceCoordinator
        
        print("✅ All modules imported successfully")
        
        # Initialize components
        state_manager = StateManager()
        specialist_manager = SpecialistManager()
        orchestrator = TaskOrchestrator(state_manager, specialist_manager)
        
        print("✅ Core components initialized")
        
        # Test the fix: use state_manager.persistence
        maintenance = MaintenanceCoordinator(state_manager.persistence, orchestrator)
        print("✅ MaintenanceCoordinator initialized successfully with state_manager.persistence")
        
        # Test basic maintenance operation
        result = await maintenance.scan_and_cleanup("current_session", "basic")
        print("✅ scan_and_cleanup executed successfully")
        print(f"Result keys: {list(result.keys())}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This is expected if dependencies aren't installed")
        return False
    except AttributeError as e:
        print(f"❌ AttributeError: {e}")
        print("This indicates the fix didn't work")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_maintenance_coordinator())
    if success:
        print("\n🎉 MaintenanceCoordinator fix verified successfully!")
    else:
        print("\n💔 MaintenanceCoordinator fix needs further investigation")
    sys.exit(0 if success else 1)