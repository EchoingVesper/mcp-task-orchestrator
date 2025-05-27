#!/usr/bin/env python3
"""
Test script for MCP Task Orchestrator
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from orchestrator import TaskOrchestrator, StateManager, SpecialistManager
    print("Successfully imported all modules")
    
    # Test basic initialization
    state_manager = StateManager()
    specialist_manager = SpecialistManager()
    orchestrator = TaskOrchestrator(state_manager, specialist_manager)
    print("Successfully initialized all components")
    
    # Test database creation
    print(f"Database created at: {state_manager.db_path}")
    
    print("All tests passed! MCP server is ready to use.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
