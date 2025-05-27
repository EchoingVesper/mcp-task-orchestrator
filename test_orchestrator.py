#!/usr/bin/env python3
"""
Test script to verify MCP Task Orchestrator functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_task_orchestrator.orchestrator import TaskOrchestrator, StateManager, SpecialistManager


async def test_orchestrator():
    """Test basic orchestrator functionality."""
    print("Testing MCP Task Orchestrator...")
    
    try:
        # Initialize components
        state_manager = StateManager()
        specialist_manager = SpecialistManager()
        orchestrator = TaskOrchestrator(state_manager, specialist_manager)
        
        print("[OK] Components initialized successfully")
        
        # Test task planning
        description = "Create a simple web API for user management"
        complexity = "moderate"
        context = "Using Python Flask framework"
        
        print(f"\nTesting task planning with: {description}")
        breakdown = await orchestrator.plan_task(description, complexity, context)
        
        print(f"[OK] Task breakdown created with {len(breakdown.subtasks)} subtasks:")
        for subtask in breakdown.subtasks:
            print(f"  - {subtask.task_id}: {subtask.title} ({subtask.specialist_type.value})")
        
        # Test specialist context
        if breakdown.subtasks:
            first_task = breakdown.subtasks[0]
            print(f"\nTesting specialist context for: {first_task.task_id}")
            specialist_context = await orchestrator.get_specialist_context(first_task.task_id)
            
            print(f"[OK] Specialist context generated ({len(specialist_context)} characters)")
            print("Context preview:")
            print(specialist_context[:200] + "..." if len(specialist_context) > 200 else specialist_context)
        
        # Test status retrieval
        print("\nTesting status retrieval...")
        status = await orchestrator.get_status(include_completed=False)
        
        print(f"[OK] Status retrieved: {status['active_tasks']} active, {status['pending_tasks']} pending")
        
        print("\n[SUCCESS] All tests passed! MCP Task Orchestrator is working correctly.")
        return True
        
    except Exception as e:
        print(f"[FAILED] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_orchestrator())
    sys.exit(0 if success else 1)
