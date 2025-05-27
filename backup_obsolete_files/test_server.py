#!/usr/bin/env python3
"""Test script to verify MCP Task Orchestrator can be imported and run."""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    # Test imports
    import main
    print("✓ Successfully imported main module")
    
    # Test core components
    from orchestrator.core import TaskOrchestrator
    from orchestrator.models import TaskBreakdown, SubTask, TaskStatus
    from orchestrator.specialists import SpecialistManager
    from orchestrator.state import StateManager
    
    print("✓ Successfully imported all core components")
    
    # Test initialization
    state_manager = StateManager()
    specialist_manager = SpecialistManager()
    orchestrator = TaskOrchestrator(state_manager, specialist_manager)
    
    print("✓ Successfully initialized all components")
    print("🎉 MCP Task Orchestrator is ready to run!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
