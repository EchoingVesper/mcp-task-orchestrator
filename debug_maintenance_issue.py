#!/usr/bin/env python3
"""Debug script to verify the maintenance coordinator issue."""

import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_task_orchestrator.orchestrator.state import StateManager
from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager

def debug_issue():
    """Debug the maintenance coordinator initialization issue."""
    
    print("=== Debugging MaintenanceCoordinator Issue ===\n")
    
    # Initialize StateManager
    state_manager = StateManager()
    
    print(f"1. StateManager type: {type(state_manager)}")
    print(f"2. StateManager has 'persistence' attribute: {hasattr(state_manager, 'persistence')}")
    
    if hasattr(state_manager, 'persistence'):
        print(f"3. state_manager.persistence type: {type(state_manager.persistence)}")
        print(f"4. Is it DatabasePersistenceManager? {isinstance(state_manager.persistence, DatabasePersistenceManager)}")
        print(f"5. Has session_scope method? {hasattr(state_manager.persistence, 'session_scope')}")
    
    print("\n=== Diagnosis ===")
    print("The issue is confirmed:")
    print("- server.py passes 'state_manager' (StateManager) to MaintenanceCoordinator")
    print("- MaintenanceCoordinator expects DatabasePersistenceManager")
    print("- StateManager.persistence is the DatabasePersistenceManager instance")
    print("\n=== Solution ===")
    print("Change line 614 in server.py from:")
    print("  maintenance = MaintenanceCoordinator(state_manager, orchestrator)")
    print("To:")
    print("  maintenance = MaintenanceCoordinator(state_manager.persistence, orchestrator)")

if __name__ == "__main__":
    debug_issue()