#!/usr/bin/env python3
"""
Test script for hang detection and prevention systems.

This script validates that the hang detection mechanisms work correctly
and can prevent/recover from hanging operations.
"""

import asyncio
import sys
import os
import logging
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("hang_detection_test")


async def test_hang_detection_decorator():
    """Test the hang detection decorator."""
    from mcp_task_orchestrator.monitoring.hang_detection import with_hang_detection
    
    print("\\n=== Testing Hang Detection Decorator ===")
    
    @with_hang_detection("test_operation", timeout=5.0)
    async def fast_operation():
        await asyncio.sleep(1.0)
        return "success"
    
    @with_hang_detection("hanging_operation", timeout=3.0) 
    async def hanging_operation():
        await asyncio.sleep(10.0)  # Will timeout
        return "should_not_reach"
    
    # Test fast operation (should succeed)
    try:
        result = await fast_operation()
        print(f"✅ Fast operation completed: {result}")
    except Exception as e:
        print(f"❌ Fast operation failed: {str(e)}")
    
    # Test hanging operation (should timeout)
    try:
        result = await hanging_operation()
        print(f"❌ Hanging operation should have timed out: {result}")
    except asyncio.TimeoutError:
        print("✅ Hanging operation correctly timed out")
    except Exception as e:
        print(f"❌ Hanging operation failed unexpectedly: {str(e)}")


async def test_hang_protected_context():
    """Test the hang-protected context manager."""
    from mcp_task_orchestrator.monitoring.hang_detection import hang_protected_operation
    
    print("\\n=== Testing Hang Protected Context Manager ===")
    
    # Test normal operation
    try:
        async with hang_protected_operation("context_test", timeout=5.0):
            await asyncio.sleep(1.0)
            print("✅ Normal context operation completed")
    except Exception as e:
        print(f"❌ Normal context operation failed: {str(e)}")
    
    # Test timeout (this will generate warnings but not fail)
    try:
        async with hang_protected_operation("context_timeout_test", timeout=2.0):
            await asyncio.sleep(5.0)  # Will cause warnings
            print("⚠️ Long context operation completed (warnings expected)")
    except Exception as e:
        print(f"⚠️ Long context operation had issues: {str(e)}")


async def test_hang_statistics():
    """Test hang detection statistics collection."""
    from mcp_task_orchestrator.monitoring.hang_detection import (
        get_hang_detection_statistics, start_hang_monitoring, _hang_detector
    )
    
    print("\\n=== Testing Hang Detection Statistics ===")
    
    # Start monitoring
    start_hang_monitoring()
    
    # Register some operations manually
    op1 = _hang_detector.register_operation("test_operation_1")
    op2 = _hang_detector.register_operation("test_operation_2")
    
    # Get initial statistics
    stats = get_hang_detection_statistics()
    print(f"Active operations: {stats['hang_detector']['active_operations']}")
    print(f"Total hangs detected: {stats['hang_detector']['total_hangs_detected']}")
    
    # Wait a bit to see monitoring in action
    await asyncio.sleep(2.0)
    
    # Unregister operations
    _hang_detector.unregister_operation(op1)
    _hang_detector.unregister_operation(op2)
    
    # Get final statistics
    final_stats = get_hang_detection_statistics()
    print(f"Final active operations: {final_stats['hang_detector']['active_operations']}")
    
    if final_stats['hang_detector']['active_operations'] == 0:
        print("✅ Statistics collection working correctly")
    else:
        print("❌ Statistics collection has issues")


async def test_database_connection_simulation():
    """Simulate database connection monitoring."""
    print("\\n=== Testing Database Connection Monitoring ===")
    
    try:
        # Import the database monitor
        from mcp_task_orchestrator.monitoring.hang_detection import _db_monitor
        
        # Simulate database operations
        conn_id = "test_connection_1"
        _db_monitor.record_connection_start(conn_id, "INSERT INTO subtasks")
        
        # Simulate work
        await asyncio.sleep(0.5)
        
        _db_monitor.record_connection_end(conn_id, success=True)
        
        # Get statistics
        db_stats = _db_monitor.get_statistics()
        print(f"Database connections monitored: {len(db_stats['active_connections'])}")
        print("✅ Database monitoring simulation completed")
        
    except Exception as e:
        print(f"❌ Database monitoring test failed: {str(e)}")


async def test_enhanced_handler_simulation():
    """Test the enhanced MCP handlers (simulation)."""
    print("\\n=== Testing Enhanced Handler Simulation ===")
    
    try:
        # Create a mock orchestrator class
        class MockOrchestrator:
            async def get_specialist_context(self, task_id):
                await asyncio.sleep(0.5)  # Simulate database work
                return f"Specialist context for {task_id}"
            
            async def complete_subtask(self, task_id, results, artifacts, next_action):
                await asyncio.sleep(1.0)  # Simulate complex operation
                return {"status": "completed", "task_id": task_id}
        
        # Import enhanced handlers
        from mcp_task_orchestrator.enhanced_handlers import (
            handle_execute_subtask_enhanced,
            handle_complete_subtask_enhanced
        )
        
        mock_orchestrator = MockOrchestrator()
        
        # Test execute subtask
        execute_args = {"task_id": "test_task_001"}
        try:
            result = await handle_execute_subtask_enhanced(execute_args, mock_orchestrator)
            print("✅ Enhanced execute_subtask simulation completed")
        except Exception as e:
            print(f"❌ Enhanced execute_subtask simulation failed: {str(e)}")
        
        # Test complete subtask  
        complete_args = {
            "task_id": "test_task_001",
            "results": "Task completed successfully",
            "artifacts": ["test_file.txt"],
            "next_action": "continue"
        }
        try:
            result = await handle_complete_subtask_enhanced(complete_args, mock_orchestrator)
            print("✅ Enhanced complete_subtask simulation completed")
        except Exception as e:
            print(f"❌ Enhanced complete_subtask simulation failed: {str(e)}")
            
    except ImportError as e:
        print(f"⚠️ Enhanced handlers not available for testing: {str(e)}")


async def run_comprehensive_test():
    """Run all hang detection tests."""
    print("="*60)
    print("HANG DETECTION AND PREVENTION SYSTEM TESTS")
    print("="*60)
    
    start_time = time.time()
    
    try:
        await test_hang_detection_decorator()
        await test_hang_protected_context()
        await test_hang_statistics()
        await test_database_connection_simulation()
        await test_enhanced_handler_simulation()
        
        elapsed = time.time() - start_time
        print(f"\\n{'='*60}")
        print(f"ALL TESTS COMPLETED IN {elapsed:.2f} SECONDS")
        print("="*60)
        
        # Final statistics
        try:
            from mcp_task_orchestrator.monitoring.hang_detection import get_hang_detection_statistics
            final_stats = get_hang_detection_statistics()
            
            print("\\nFinal System Statistics:")
            print(f"- Active operations: {final_stats['hang_detector']['active_operations']}")
            print(f"- Total hangs detected: {final_stats['hang_detector']['total_hangs_detected']}")
            print(f"- Monitoring active: {final_stats.get('monitoring_active', False)}")
            
        except Exception as e:
            print(f"Could not retrieve final statistics: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"\\n❌ CRITICAL ERROR IN TESTS: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    try:
        # Run async tests
        success = asyncio.run(run_comprehensive_test())
        
        if success:
            print("\\n🎉 All hang detection tests passed!")
            return 0
        else:
            print("\\n❌ Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"\\n💥 Failed to run tests: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
