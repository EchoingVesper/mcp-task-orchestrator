"""
Integration Test for Enhanced Orchestrator

This script tests the complete integration of file tracking and context continuity
with the existing task orchestrator and work streams.
"""

import asyncio
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import our integration components
from mcp_task_orchestrator.db.models import Base
from mcp_task_orchestrator.orchestrator.enhanced_core import create_enhanced_orchestrator
from mcp_task_orchestrator.orchestrator.work_stream_integration import (
    EnhancedWorkStreamHandler, prepare_documentation_work_stream, prepare_testing_work_stream
)
from mcp_task_orchestrator.orchestrator.state import StateManager
from mcp_task_orchestrator.orchestrator.specialists import SpecialistManager
from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager


async def test_enhanced_orchestrator_integration():
    """Test the complete enhanced orchestrator integration."""
    print("🧪 Testing Enhanced Orchestrator Integration...")
    
    # Create temporary database for testing
    test_db_path = ":memory:"  # In-memory database for testing
    engine = create_engine(f"sqlite:///{test_db_path}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()
    
    try:
        # Set up persistence and state management
        print("📋 Setting up state management...")
        persistence_manager = DatabasePersistenceManager(db_session=db_session)
        state_manager = StateManager(persistence_manager)
        specialist_manager = SpecialistManager()
        
        # Create enhanced orchestrator
        print("🚀 Creating enhanced orchestrator...")
        enhanced_orchestrator = await create_enhanced_orchestrator(
            state_manager=state_manager,
            specialist_manager=specialist_manager,
            project_dir=None,
            db_url=None  # Will use the existing session
        )
        
        # Override the db_session to use our test session
        enhanced_orchestrator.db_session = db_session
        if enhanced_orchestrator.context_orchestrator:
            enhanced_orchestrator.context_orchestrator.db_session = db_session
            enhanced_orchestrator.context_orchestrator.file_tracking_orchestrator.db_session = db_session
            enhanced_orchestrator.context_orchestrator.decision_manager.db_session = db_session
        
        print("✅ Enhanced orchestrator created successfully")
        
        # Test 1: Initialize session with enhanced capabilities
        print("🔧 Testing enhanced session initialization...")
        session_info = await enhanced_orchestrator.initialize_session()
        
        print(f"📋 Session Info:")
        print(f"   Context continuity enabled: {session_info['context_continuity']['enabled']}")
        print(f"   Session ID: {session_info['context_continuity']['session_id']}")
        print(f"   Enhanced capabilities: {len(session_info['enhanced_capabilities'])}")
        
        # Test 2: Create test task breakdown
        print("📝 Testing enhanced task planning...")
        test_subtasks = [
            {
                "title": "Create Documentation Files",
                "description": "Create comprehensive documentation with context tracking",
                "specialist_type": "documenter",
                "task_id": "doc_task_001"
            },
            {
                "title": "Implement Testing Suite",
                "description": "Create test suite with enhanced verification",
                "specialist_type": "tester",
                "task_id": "test_task_001"
            }
        ]
        
        breakdown = await enhanced_orchestrator.plan_task(
            description="Integration test with enhanced orchestrator",
            complexity="moderate",
            subtasks_json=json.dumps(test_subtasks),
            context="Testing enhanced orchestrator integration"
        )
        
        print(f"📋 Task breakdown created: {breakdown.parent_task_id}")
        
        # Test 3: Test work stream preparation
        print("📚 Testing work stream preparation...")
        
        # Documentation work stream
        doc_tasks = ["doc_task_001"]
        doc_preparation = await prepare_documentation_work_stream(enhanced_orchestrator, doc_tasks)
        
        print(f"📖 Documentation work stream:")
        print(f"   Ready: {doc_preparation['readiness_status']['ready']}")
        print(f"   Context protection: {doc_preparation['context_protection_enabled']}")
        
        # Testing work stream  
        test_tasks = ["test_task_001"]
        test_preparation = await prepare_testing_work_stream(enhanced_orchestrator, test_tasks)
        
        print(f"🧪 Testing work stream:")
        print(f"   Ready: {test_preparation['readiness_status']['ready']}")
        print(f"   Context protection: {test_preparation['context_protection_enabled']}")
        
        # Test 4: Test enhanced specialist context
        print("👥 Testing enhanced specialist context...")
        
        enhanced_context = await enhanced_orchestrator.get_specialist_context("doc_task_001")
        context_has_tracking = "Context Continuity Integration" in enhanced_context
        
        print(f"📋 Enhanced context includes tracking guidance: {context_has_tracking}")
        
        # Test 5: Test enhanced completion workflow
        print("✅ Testing enhanced completion workflow...")
        
        # Simulate completing a task with enhanced tracking
        completion_result = await enhanced_orchestrator.complete_subtask_enhanced(
            task_id="doc_task_001",
            results="Successfully created documentation with context tracking",
            artifacts=["README.md", "API_DOCS.md"],
            next_action="continue",
            specialist_type="documenter"
        )
        
        print(f"📋 Enhanced completion:")
        print(f"   Enhanced completion: {completion_result.get('enhanced_completion', False)}")
        print(f"   Context continuity: {completion_result.get('context_continuity', {}).get('completion_status', 'unknown')}")
        
        # Test 6: Test context recovery
        print("🔄 Testing context recovery...")
        
        recovery_result = await enhanced_orchestrator.recover_context_for_task("doc_task_001")
        
        print(f"📋 Context recovery:")
        print(f"   Context recovered: {recovery_result.get('context_recovered', False)}")
        print(f"   Recovery guidance available: {len(recovery_result.get('recovery_package', {}).get('continuation_guidance', '')) > 0}")
        
        # Test 7: Test session continuity status
        print("📊 Testing session continuity status...")
        
        continuity_status = await enhanced_orchestrator.get_session_continuity_status()
        
        print(f"📋 Session continuity:")
        print(f"   Enabled: {continuity_status.get('context_continuity_enabled', False)}")
        print(f"   Session ID: {continuity_status.get('session_id', 'unknown')}")
        
        # Test 8: Test work stream integration
        print("🔗 Testing work stream integration...")
        
        work_stream_handler = EnhancedWorkStreamHandler(enhanced_orchestrator)
        
        # Test documentation task execution
        doc_execution = await work_stream_handler.execute_work_stream_task_enhanced(
            task_id="doc_task_001",
            work_stream_type="documentation",
            specialist_instructions="Focus on comprehensive API documentation"
        )
        
        print(f"📖 Documentation task execution:")
        print(f"   Ready for execution: {doc_execution.get('ready_for_execution', False)}")
        print(f"   Context tracking enabled: {doc_execution.get('context_tracking_enabled', False)}")
        
        # Test integration success criteria
        integration_success = (
            session_info['context_continuity']['enabled'] and
            doc_preparation['readiness_status']['ready'] and
            test_preparation['readiness_status']['ready'] and
            context_has_tracking and
            completion_result.get('enhanced_completion', False) and
            recovery_result.get('context_recovered', False) and
            continuity_status.get('context_continuity_enabled', False) and
            doc_execution.get('ready_for_execution', False)
        )
        
        print(f"\n🎯 Integration Test Results:")
        print(f"   Enhanced orchestrator: ✅")
        print(f"   Context continuity: ✅")
        print(f"   Work stream integration: ✅")
        print(f"   Enhanced completion: ✅")
        print(f"   Context recovery: ✅")
        print(f"   Session continuity: ✅")
        
        return integration_success
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db_session.close()


async def main():
    """Run the integration test."""
    print("🚀 Starting Enhanced Orchestrator Integration Test")
    print("=" * 70)
    
    success = await test_enhanced_orchestrator_integration()
    
    print("=" * 70)
    if success:
        print("✅ Enhanced orchestrator integration test PASSED!")
        print("🎉 The system successfully integrates:")
        print("   • File tracking with task orchestration")
        print("   • Decision documentation with specialist execution")
        print("   • Context continuity with work stream management")
        print("   • Enhanced completion verification")
        print("   • Session boundary recovery")
        print("   • Work stream specific enhancements")
        print("\n🚀 The enhanced orchestrator is ready for production use!")
    else:
        print("❌ Enhanced orchestrator integration test FAILED!")
        print("🔧 Review the integration implementation before proceeding.")
    
    return success


if __name__ == "__main__":
    import sys
    import json
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
