"""
Context Continuity System Test

This script tests the complete context continuity system including
file tracking and decision documentation integration.
"""

import asyncio
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import our context continuity components
from mcp_task_orchestrator.db.models import Base
from mcp_task_orchestrator.orchestrator.context_continuity import (
    initialize_context_continuity, create_context_tracker_for_subtask
)
from mcp_task_orchestrator.orchestrator.decision_tracking import (
    DecisionCategory, DecisionImpact
)


async def test_context_continuity_system():
    """Test the complete context continuity system."""
    print("🧪 Testing Context Continuity System...")
    
    # Create temporary database for testing
    test_db_path = ":memory:"  # In-memory database for testing
    engine = create_engine(f"sqlite:///{test_db_path}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()
    
    try:
        # Initialize context continuity system
        print("📋 Initializing context continuity system...")
        context_orchestrator = await initialize_context_continuity(db_session, run_migrations=False)
        print("✅ Context continuity system initialized")
        
        # Create test subtask tracker
        test_subtask_id = "test_context_subtask_001"
        test_specialist_type = "implementer"
        tracker = create_context_tracker_for_subtask(
            test_subtask_id, test_specialist_type, context_orchestrator
        )
        print(f"📝 Created context tracker for subtask: {test_subtask_id}")
        
        # Create temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test 1: File operations with decision context
            print("🔨 Testing file operations with decision tracking...")
            
            test_file1 = temp_path / "implementation.py"
            test_file2 = temp_path / "config.json"
            
            # Track file creation with rationale
            await tracker.track_file_create(
                str(test_file1), 
                rationale="Creating main implementation file for context tracking system"
            )
            test_file1.write_text("# Implementation file\nclass ContextTracker:\n    pass")
            
            await tracker.track_file_create(
                str(test_file2),
                rationale="Creating configuration file for system settings"
            )
            test_file2.write_text('{"context_tracking": true}')
            
            # Test 2: Capture architectural decisions
            print("🏗️ Testing architectural decision capture...")
            
            arch_decision_id = await tracker.capture_architecture_decision(
                title="Context Tracking Architecture",
                problem="Need to maintain context across session boundaries",
                solution="Implement combined file and decision tracking system",
                rationale="Ensures no work is lost when chat contexts reset",
                affected_files=[str(test_file1), str(test_file2)],
                risks=["Increased database complexity", "Performance overhead"]
            )
            print(f"📋 Captured architectural decision: {arch_decision_id}")
            
            # Test 3: Capture implementation decisions
            print("⚙️ Testing implementation decision capture...")
            
            impl_decision_id = await tracker.capture_implementation_decision(
                title="Database Schema Design",
                decision="Use SQLAlchemy ORM with separate tables for operations and decisions",
                rationale="Provides flexibility and maintainability for complex relationships",
                affected_files=[str(test_file1)]
            )
            print(f"🔧 Captured implementation decision: {impl_decision_id}")
            
            # Test 4: File modifications with context
            print("📝 Testing file modifications with decision context...")
            
            await tracker.track_file_modify(
                str(test_file1),
                rationale="Adding decision tracking capabilities to the context tracker"
            )
            test_file1.write_text("# Implementation file\nclass ContextTracker:\n    def track_decisions(self): pass")
            
            # Test 5: Generate comprehensive context
            print("🔍 Testing comprehensive context generation...")
            
            context_package = await tracker.generate_comprehensive_context()
            
            print(f"📊 Context Package Summary:")
            print(f"   Files created: {len(context_package.files_created)}")
            print(f"   Files modified: {len(context_package.files_modified)}")
            print(f"   Total decisions: {context_package.decisions_summary['total_decisions']}")
            print(f"   Key decisions: {len(context_package.key_decisions)}")
            print(f"   Outstanding risks: {len(context_package.outstanding_risks)}")
            print(f"   Critical considerations: {len(context_package.critical_considerations)}")
            
            # Test 6: Subtask completion verification
            print("🏁 Testing subtask completion verification...")
            
            completion_result = await tracker.verify_subtask_completion()
            
            print(f"📋 Completion Verification:")
            print(f"   Completion approved: {completion_result['completion_approved']}")
            print(f"   Critical issues: {len(completion_result['critical_issues'])}")
            print(f"   Recommendations: {len(completion_result['recommendations'])}")
            
            # Test 7: Complete subtask with context
            print("✅ Testing complete subtask with context tracking...")
            
            completion_info = await context_orchestrator.complete_subtask_with_context(
                subtask_id=test_subtask_id,
                specialist_type=test_specialist_type,
                results="Successfully implemented context continuity system with file and decision tracking",
                artifacts=[str(test_file1), str(test_file2)]
            )
            
            print(f"📋 Subtask Completion Info:")
            print(f"   Status: {completion_info['completion_status']}")
            print(f"   Total operations: {completion_info['session_continuity_info']['total_operations']}")
            print(f"   Total decisions: {completion_info['session_continuity_info']['total_decisions']}")
            print(f"   Files affected: {completion_info['session_continuity_info']['files_affected']}")
            
            # Test 8: Context recovery
            print("🔄 Testing context recovery...")
            
            recovered_context = await context_orchestrator.recover_context_for_subtask(test_subtask_id)
            
            print(f"📋 Recovered Context:")
            print(f"   Continuation guidance available: {len(recovered_context.continuation_guidance) > 0}")
            print(f"   Recovery recommendations: {len(recovered_context.recovery_recommendations)}")
            
            # Test 9: Session continuity report
            print("📊 Testing session continuity report...")
            
            session_report = await context_orchestrator.generate_session_continuity_report()
            
            print(f"📋 Session Report:")
            print(f"   Session ID: {session_report['session_id']}")
            print(f"   Total decisions: {session_report['total_decisions']}")
            print(f"   Summary: {session_report['session_summary']}")
            
            # Validate all tests passed
            all_tests_passed = (
                len(context_package.files_created) == 2 and
                len(context_package.files_modified) == 1 and
                context_package.decisions_summary['total_decisions'] >= 4 and  # 2 explicit + file operation decisions
                completion_result['completion_approved'] and
                completion_info['completion_status'] == 'completed' and
                len(recovered_context.continuation_guidance) > 0
            )
            
            return all_tests_passed
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db_session.close()


async def main():
    """Run the context continuity test."""
    print("🚀 Starting Context Continuity System Test")
    print("=" * 60)
    
    success = await test_context_continuity_system()
    
    print("=" * 60)
    if success:
        print("✅ Context continuity system test PASSED!")
        print("🎉 The system provides complete context tracking and recovery.")
        print("📋 Features verified:")
        print("   • File operation tracking with decision context")
        print("   • Architectural and implementation decision capture")
        print("   • Comprehensive context package generation")
        print("   • Subtask completion verification")
        print("   • Context recovery across sessions")
        print("   • Session continuity reporting")
    else:
        print("❌ Context continuity system test FAILED!")
        print("🔧 Review the implementation before proceeding.")
    
    return success


if __name__ == "__main__":
    import sys
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
