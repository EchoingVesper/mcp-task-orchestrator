#!/usr/bin/env python3
"""Simple test to verify synchronization fixes."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import asyncio
import time

async def test_basic_import():
    """Test that we can import and initialize components without hanging."""
    print("Testing basic imports...")
    
    try:
        from .orchestrator.orchestration_state_manager import StateManager
        print("StateManager imported successfully")
        
        # Test initialization
        start_time = time.time()
        state_manager = StateManager()
        elapsed = time.time() - start_time
        print(f"StateManager initialized in {elapsed:.2f}s")
        
        # Test basic operation
        start_time = time.time()
        tasks = await state_manager.get_all_tasks()
        elapsed = time.time() - start_time
        print(f"Retrieved {len(tasks)} tasks in {elapsed:.2f}s")
        
        if elapsed > 10.0:
            print(f"WARNING: Operation took {elapsed:.2f}s - may indicate hanging issues")
        else:
            print("Operation completed in reasonable time")
            
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting simple synchronization test...")
    
    success = asyncio.run(test_basic_import())
    
    if success:
        print("Basic test PASSED - synchronization fixes appear to be working!")
    else:
        print("Basic test FAILED - synchronization issues may remain")
        
    sys.exit(0 if success else 1)
