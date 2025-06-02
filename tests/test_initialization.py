# Test script to verify orchestrator starts correctly
# Save this as test_initialization.py and run it

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

try:
    # Set environment variables
    os.environ["MCP_TASK_ORCHESTRATOR_DB_PATH"] = r"E:\My Work\Programming\MCP Task Orchestrator\task_orchestrator.db"
    os.environ["MCP_TASK_ORCHESTRATOR_BASE_DIR"] = r"E:\My Work\Programming\MCP Task Orchestrator"
    
    from mcp_task_orchestrator.orchestrator.state import StateManager
    from mcp_task_orchestrator.orchestrator.core import TaskOrchestrator
    from mcp_task_orchestrator.orchestrator.specialists import SpecialistManager
    
    # Initialize components
    state_manager = StateManager()
    specialist_manager = SpecialistManager()
    orchestrator = TaskOrchestrator(state_manager, specialist_manager)
    
    print("SUCCESS: Orchestrator initialization works correctly!")
    print("StateManager fix is working")
    print("Ready for release")
    
except AttributeError as e:
    if "_get_parent_task_id" in str(e):
        print("CRITICAL FAILURE: StateManager issue still exists!")
        print(f"Error: {e}")
        print("DO NOT RELEASE - Fix required")
    else:
        print(f"Other AttributeError: {e}")
except Exception as e:
    print(f"Initialization failed: {e}")
    print("Investigate before release")
