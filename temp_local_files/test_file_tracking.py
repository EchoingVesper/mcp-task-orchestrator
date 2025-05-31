"""
File Tracking System Test

This script tests the file tracking and verification system to ensure
it's working correctly before full integration.
"""

import asyncio
import tempfile
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import our file tracking components
from mcp_task_orchestrator.db.models import Base
from mcp_task_orchestrator.orchestrator.file_tracking_integration import (
    initialize_file_tracking, create_file_tracker_for_subtask
)


async def test_file_tracking_system():
    """Test the complete file tracking system."""
    print("🧪 Testing File Tracking System...")
    
    # Create temporary database for testing
    test_db_path = ":memory:"  # In-memory database for testing
    engine = create_engine(f"sqlite:///{test_db_path}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()
    
    try:
        # Initialize file tracking
        print("📋 Initializing file tracking system...")
        file_tracking = await initialize_file_tracking(db_session, run_migration=False)
        print("✅ File tracking system initialized")
        
        # Create test subtask tracker
        test_subtask_id = "test_subtask_001"
        tracker = create_file_tracker_for_subtask(test_subtask_id, file_tracking)
        print(f"📝 Created tracker for subtask: {test_subtask_id}")
        
        # Create temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test_file.txt"
            
            # Test file creation tracking
            print("🔨 Testing file creation tracking...")
            await tracker.track_file_create(str(test_file), {"test": "creation"})
            
            # Actually create the file
            test_file.write_text("Hello, file tracking system!")
            
            # Test file modification tracking
            print("📝 Testing file modification tracking...")
            await tracker.track_file_modify(str(test_file), {"test": "modification"})
            
            # Actually modify the file
            test_file.write_text("Hello, modified file tracking system!")
            
            # Test file read tracking
            print("👀 Testing file read tracking...")
            await tracker.track_file_read(str(test_file), {"test": "read"})
            
            # Verify all operations
            print("🔍 Verifying all file operations...")
            verification_summary = await tracker.verify_all_operations()
            
            print(f"📊 Verification Summary:")
            print(f"   Total operations: {verification_summary['total_operations']}")
            print(f"   All verified: {verification_summary['all_verified']}")
            print(f"   Failed verifications: {len(verification_summary['failed_verifications'])}")
            
            if verification_summary['failed_verifications']:
                print("❌ Failed verifications:")
                for failure in verification_summary['failed_verifications']:
                    print(f"     - Operation {failure['operation_id']}: {failure['errors']}")
            else:
                print("✅ All operations verified successfully!")
            
            # Test subtask completion verification
            print("🏁 Testing subtask completion verification...")
            completion_result = await file_tracking.verify_subtask_completion(test_subtask_id)
            
            print(f"📋 Completion Verification:")
            print(f"   Status: {completion_result['status']}")
            print(f"   Completion approved: {completion_result['completion_approved']}")
            print(f"   Total operations: {completion_result.get('total_operations', 0)}")
            print(f"   Verified operations: {completion_result.get('verified_operations', 0)}")
            
            # Test context recovery
            print("🔄 Testing context recovery information...")
            recovery_info = await tracker.get_context_recovery_info()
            
            print(f"📋 Context Recovery Info:")
            print(f"   Total operations: {recovery_info['total_operations']}")
            print(f"   Files affected: {len(recovery_info['files_affected'])}")
            print(f"   Critical failures: {len(recovery_info['critical_failures'])}")
            
            # Test file deletion tracking
            print("🗑️ Testing file deletion tracking...")
            await tracker.track_file_delete(str(test_file), {"test": "deletion"})
            
            # Actually delete the file
            test_file.unlink()
            
            # Final verification
            print("🔍 Final verification after deletion...")
            final_verification = await tracker.verify_all_operations()
            
            print(f"📊 Final Verification Summary:")
            print(f"   Total operations: {final_verification['total_operations']}")
            print(f"   All verified: {final_verification['all_verified']}")
            
            return final_verification['all_verified']
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False
    
    finally:
        db_session.close()


async def main():
    """Run the file tracking test."""
    print("🚀 Starting File Tracking System Test")
    print("=" * 50)
    
    success = await test_file_tracking_system()
    
    print("=" * 50)
    if success:
        print("✅ File tracking system test PASSED!")
        print("🎉 The system is ready for integration with the orchestrator.")
    else:
        print("❌ File tracking system test FAILED!")
        print("🔧 Review the implementation before proceeding.")
    
    return success


if __name__ == "__main__":
    import sys
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
