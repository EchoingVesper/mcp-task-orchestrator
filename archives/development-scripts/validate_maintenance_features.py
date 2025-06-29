#!/usr/bin/env python3
"""
Simple validation script for maintenance features and streaming system.
This script performs basic tests without requiring pytest or coverage.
"""

import os
import sys
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_task_orchestrator.orchestrator.maintenance import MaintenanceCoordinator
from mcp_task_orchestrator.orchestrator.task_lifecycle import TaskLifecycleManager
from mcp_task_orchestrator.orchestrator.streaming_artifacts import StreamingArtifactManager
from mcp_task_orchestrator.db.models import Base, SubTaskModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_maintenance_coordinator():
    """Test basic maintenance coordinator functionality."""
    print("\n=== Testing MaintenanceCoordinator ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create coordinator
        coordinator = MaintenanceCoordinator(session)
        
        # Test scan_cleanup
        print("Testing scan_cleanup...")
        result = coordinator.scan_cleanup(scope="current_session")
        print(f"  Stale tasks found: {result['stale_tasks_found']}")
        print(f"  Tasks to archive: {result['tasks_to_archive']}")
        assert result['status'] == 'success', "Scan cleanup failed"
        
        # Test validate_structure
        print("Testing validate_structure...")
        result = coordinator.validate_structure(validation_level="basic")
        print(f"  Valid tasks: {result['metrics']['valid_tasks']}")
        print(f"  Validation passed: {result['validation_passed']}")
        assert result['status'] == 'success', "Structure validation failed"
        
        session.close()
        print("✓ MaintenanceCoordinator tests passed")


def test_task_lifecycle_manager():
    """Test task lifecycle manager functionality."""
    print("\n=== Testing TaskLifecycleManager ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create test tasks
        old_task = SubTaskModel(
            id="old_task",
            task_id="task_1",
            title="Old Task",
            specialist_type="implementer",
            status="pending",
            created_at=datetime.now() - timedelta(days=10)
        )
        
        recent_task = SubTaskModel(
            id="recent_task",
            task_id="task_2",
            title="Recent Task",
            specialist_type="tester",
            status="active",
            created_at=datetime.now() - timedelta(hours=1)
        )
        
        session.add_all([old_task, recent_task])
        session.commit()
        
        # Create manager
        manager = TaskLifecycleManager(session)
        
        # Test detect_stale_tasks
        print("Testing stale task detection...")
        stale_tasks = manager.detect_stale_tasks()
        print(f"  Stale tasks detected: {len(stale_tasks)}")
        assert len(stale_tasks) == 1, "Should detect 1 stale task"
        assert stale_tasks[0].id == "old_task", "Wrong stale task detected"
        
        # Test archive_task
        print("Testing task archival...")
        success = manager.archive_task("old_task", reason="Test archival")
        assert success, "Task archival failed"
        
        # Verify task was archived
        archived = session.query(SubTaskModel).filter_by(id="old_task").first()
        assert archived.status == "archived", "Task not properly archived"
        
        session.close()
        print("✓ TaskLifecycleManager tests passed")


def test_streaming_artifacts():
    """Test streaming artifact system."""
    print("\n=== Testing StreamingArtifactManager ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create manager
        manager = StreamingArtifactManager(base_path=temp_dir)
        
        # Test store_artifact with large content
        print("Testing large content storage...")
        large_content = "x" * 15000  # 15KB content
        artifact_info = manager.store_artifact(
            task_id="test_task",
            content=large_content,
            artifact_type="test"
        )
        
        assert artifact_info['stored_successfully'], "Failed to store artifact"
        print(f"  Artifact ID: {artifact_info['artifact_id']}")
        print(f"  Content size: {artifact_info['content_size']} bytes")
        
        # Test retrieve_artifact
        print("Testing artifact retrieval...")
        retrieved = manager.retrieve_artifact(
            task_id="test_task",
            artifact_id=artifact_info['artifact_id']
        )
        
        assert retrieved is not None, "Failed to retrieve artifact"
        assert retrieved['content'] == large_content, "Content mismatch"
        print("  Content retrieved successfully")
        
        # Test file mirroring
        print("Testing file mirroring...")
        test_files = {
            "file1.py": "print('hello')",
            "file2.py": "def test(): pass"
        }
        
        for filename, content in test_files.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
        
        manager.mirror_files(
            task_id="test_task",
            artifact_id=artifact_info['artifact_id'],
            file_paths=list(test_files.keys())
        )
        
        # Verify mirrored files
        mirror_dir = os.path.join(
            temp_dir, "artifacts", "test_task", 
            artifact_info['artifact_id'], "files"
        )
        
        for filename in test_files:
            assert os.path.exists(os.path.join(mirror_dir, filename)), \
                f"File {filename} not mirrored"
        
        print("  Files mirrored successfully")
        print("✓ StreamingArtifactManager tests passed")


def test_integration():
    """Test integration of all components."""
    print("\n=== Testing Integration ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create components
        coordinator = MaintenanceCoordinator(session)
        lifecycle_mgr = TaskLifecycleManager(session)
        artifact_mgr = StreamingArtifactManager(base_path=temp_dir)
        
        # Create a task with artifact
        task = SubTaskModel(
            id="integration_task",
            task_id="parent_task",
            title="Integration Test Task",
            specialist_type="implementer",
            status="completed",
            created_at=datetime.now() - timedelta(days=8),
            detailed_work="Test implementation work"
        )
        session.add(task)
        session.commit()
        
        # Store artifact for the task
        artifact_info = artifact_mgr.store_artifact(
            task_id="integration_task",
            content="Integration test artifact content",
            artifact_type="code"
        )
        
        # Run maintenance scan
        print("Running maintenance scan...")
        scan_result = coordinator.scan_cleanup(scope="current_session")
        print(f"  Found {scan_result['stale_tasks_found']} stale tasks")
        
        # Archive stale tasks
        if scan_result['stale_tasks_found'] > 0:
            print("Archiving stale tasks...")
            for task_id in scan_result['stale_task_ids']:
                success = lifecycle_mgr.archive_task(
                    task_id, 
                    reason="Integration test cleanup"
                )
                print(f"  Archived {task_id}: {success}")
        
        # Validate final structure
        validation = coordinator.validate_structure(validation_level="comprehensive")
        print(f"  Final validation: {validation['validation_passed']}")
        
        session.close()
        print("✓ Integration tests passed")


def main():
    """Run all validation tests."""
    print("=== Maintenance Features Validation ===")
    print(f"Testing at: {datetime.now()}")
    
    try:
        test_maintenance_coordinator()
        test_task_lifecycle_manager()
        test_streaming_artifacts()
        test_integration()
        
        print("\n✅ All validation tests passed!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())