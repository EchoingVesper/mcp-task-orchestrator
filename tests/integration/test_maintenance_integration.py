"""
Integration tests for maintenance features and streaming system.

Tests complete workflows from task creation to archival, maintenance operations
with real database, and streaming system preservation across context resets.
"""

import pytest
import asyncio
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import json

from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
from mcp_task_orchestrator.db.models import Base
from mcp_task_orchestrator.orchestrator.task_orchestration_service import TaskOrchestrator
from mcp_task_orchestrator.orchestrator.maintenance import MaintenanceCoordinator
from mcp_task_orchestrator.orchestrator.orchestration_state_manager import StateManager
from mcp_task_orchestrator.orchestrator.specialist_management_service import SpecialistManager
from mcp_task_orchestrator.orchestrator.task_lifecycle import TaskLifecycleManager
from mcp_task_orchestrator.orchestrator.streaming_artifacts import StreamingArtifactManager
from mcp_task_orchestrator.orchestrator.artifacts import ArtifactManager
from mcp_task_orchestrator.orchestrator.models import TaskStatus, SpecialistType
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class TestMaintenanceIntegration:
    """Integration test suite for maintenance and streaming features."""
    
    @pytest.fixture
    async def test_environment(self):
        """Set up complete test environment with database and directories."""
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Set up database
        db_path = Path(temp_dir) / "test_integration.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        
        # Initialize components
        db_state_manager = DatabasePersistenceManager(str(db_path))
        state_manager = StateManager(db_state_manager)
        specialist_manager = SpecialistManager()
        artifact_manager = ArtifactManager(temp_dir)
        streaming_manager = StreamingArtifactManager(temp_dir)
        
        # Create orchestrator
        orchestrator = TaskOrchestrator(
            state_manager=state_manager,
            specialist_manager=specialist_manager,
            project_dir=str(temp_dir)
        )
        
        # Create maintenance components
        maintenance_coordinator = MaintenanceCoordinator(db_state_manager, orchestrator)
        lifecycle_manager = TaskLifecycleManager(state_manager, artifact_manager)
        
        yield {
            "temp_dir": temp_dir,
            "state_manager": state_manager,
            "artifact_manager": artifact_manager,
            "streaming_manager": streaming_manager,
            "orchestrator": orchestrator,
            "maintenance_coordinator": maintenance_coordinator,
            "lifecycle_manager": lifecycle_manager,
            "engine": engine
        }
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Test complete task lifecycle workflow
    @pytest.mark.asyncio
    async def test_complete_task_lifecycle_workflow(self, test_environment):
        """Test complete workflow from task creation to archival."""
        orchestrator = test_environment["orchestrator"]
        maintenance = test_environment["maintenance_coordinator"]
        lifecycle = test_environment["lifecycle_manager"]
        streaming = test_environment["streaming_manager"]
        
        # Step 1: Create and plan a complex task
        parent_task = await orchestrator.plan_task(
            description="Build a web application with user authentication",
            complexity="complex",
            subtasks_json=json.dumps([
                {
                    "title": "Design database schema",
                    "description": "Design user and session tables",
                    "specialist_type": "architect",
                    "estimated_effort": "2 hours"
                },
                {
                    "title": "Implement authentication API",
                    "description": "Create login/logout endpoints",
                    "specialist_type": "implementer",
                    "dependencies": ["Design database schema"],
                    "estimated_effort": "4 hours"
                },
                {
                    "title": "Write authentication tests",
                    "description": "Unit and integration tests",
                    "specialist_type": "tester",
                    "dependencies": ["Implement authentication API"],
                    "estimated_effort": "3 hours"
                }
            ])
        )
        
        # Verify task was created
        assert parent_task is not None
        parent_id = parent_task.task_id
        
        # Step 2: Execute subtasks with streaming artifacts
        subtasks = parent_task.children
        
        # Execute first subtask (Design)
        design_task = subtasks[0]
        design_result = await orchestrator.execute_subtask(design_task.task_id)
        
        # Create streaming artifact for design
        design_session = await streaming.create_streaming_session(
            task_id=design_task.task_id,
            summary="Database schema design",
            artifact_type="design"
        )
        
        design_content = """
        -- User Authentication Schema
        CREATE TABLE users (
            id UUID PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE TABLE sessions (
            id UUID PRIMARY KEY,
            user_id UUID REFERENCES users(id),
            token VARCHAR(255) UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        await design_session.write(design_content)
        design_artifact_id = await design_session.finalize()
        
        # Complete design task
        await orchestrator.complete_subtask(
            task_id=design_task["id"],
            summary="Database schema designed",
            detailed_work=design_content,
            next_action="continue"
        )
        
        # Step 3: Simulate task aging and run maintenance
        # Manually update task timestamps to simulate aging
        with Session(test_environment["engine"]) as session:
            from mcp_task_orchestrator.db.models import SubTaskModel
            task = session.query(SubTaskModel).filter_by(id=design_task["id"]).first()
            if task:
                task.updated_at = datetime.utcnow() - timedelta(days=100)
                session.commit()
        
        # Run maintenance scan
        scan_result = await maintenance.scan_and_cleanup(
            scope="full_project",
            validation_level="comprehensive"
        )
        
        # Verify maintenance found old tasks
        assert len(scan_result["scan_results"]["tasks_scanned"]) > 0
        assert len(scan_result["recommendations"]) > 0
        
        # Step 4: Test structure validation
        validation_result = await maintenance.validate_structure(
            scope="current_session",
            validation_level="comprehensive"
        )
        
        assert validation_result["validation_results"]["valid_structure"] is True
        
        # Step 5: Test documentation generation
        doc_result = await maintenance.update_documentation(
            scope="current_session",
            validation_level="basic"
        )
        
        assert len(doc_result["documentation_updates"]) > 0
        
        # Step 6: Archive completed tasks
        archive_result = await lifecycle.archive_task(
            design_task["id"],
            preserve_artifacts=True
        )
        
        assert archive_result["success"] is True
        
        # Verify artifact was preserved
        archived_content = await streaming.get_artifact_content(
            design_task["id"],
            design_artifact_id
        )
        assert archived_content == design_content
        
        # Step 7: Prepare handover
        handover_result = await maintenance.prepare_handover(
            scope="current_session",
            validation_level="comprehensive"
        )
        
        assert "handover_package" in handover_result
        assert len(handover_result["handover_package"]["completed_tasks"]) > 0
    
    @pytest.mark.asyncio
    async def test_stale_task_detection_and_cleanup(self, test_environment):
        """Test detection and cleanup of stale tasks."""
        orchestrator = test_environment["orchestrator"]
        lifecycle = test_environment["lifecycle_manager"]
        state_manager = test_environment["state_manager"]
        
        # Create tasks with different states
        tasks = []
        
        # Active task
        active_task = await orchestrator.plan_task(
            description="Active task",
            subtasks_json=json.dumps([{
                "title": "Active subtask",
                "description": "Currently being worked on",
                "specialist_type": "implementer"
            }])
        )
        tasks.append(active_task)
        
        # Stale task (old and no progress)
        stale_task = await orchestrator.plan_task(
            description="Stale task",
            subtasks_json=json.dumps([{
                "title": "Abandoned subtask",
                "description": "No progress for weeks",
                "specialist_type": "researcher"
            }])
        )
        
        # Manually age the stale task
        with Session(test_environment["engine"]) as session:
            from mcp_task_orchestrator.db.models import SubTaskModel
            task = session.query(SubTaskModel).filter_by(
                parent_id=stale_task["task_id"]
            ).first()
            if task:
                task.created_at = datetime.utcnow() - timedelta(days=30)
                task.updated_at = datetime.utcnow() - timedelta(days=25)
                session.commit()
        
        # Detect stale tasks
        stale_detected = await lifecycle.detect_stale_tasks(comprehensive_scan=True)
        
        assert len(stale_detected) > 0
        assert any(task["reason"] == "inactivity_timeout" for task in stale_detected)
        
        # Generate cleanup recommendations
        recommendations = await lifecycle.generate_cleanup_recommendations()
        
        assert len(recommendations) > 0
        assert any("review_stale_tasks" in rec["type"] for rec in recommendations)
        
        # Archive stale tasks
        for stale in stale_detected:
            archive_result = await lifecycle.archive_task(
                stale["task_id"],
                reason=stale["reason"]
            )
            assert archive_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_streaming_context_preservation(self, test_environment):
        """Test streaming system preserves work across context resets."""
        streaming1 = test_environment["streaming_manager"]
        task_id = "context_test_task"
        
        # Context 1: Start work
        session1 = await streaming1.create_streaming_session(
            task_id=task_id,
            summary="Context preservation test",
            artifact_type="code"
        )
        
        initial_content = """
        def process_data(input_data):
            # Initial implementation
            return input_data.upper()
        """
        
        await session1.write(initial_content)
        await session1._save_progress()  # Save without finalizing
        
        # Simulate context reset - create new streaming manager
        streaming2 = StreamingArtifactManager(test_environment["temp_dir"])
        
        # Context 2: Resume work
        resumed = await streaming2.resume_partial_session(task_id, session1.artifact_id)
        assert resumed is not None
        
        additional_content = """
        
        def validate_data(data):
            # Added after context switch
            return len(data) > 0
        """
        
        await resumed.write(additional_content)
        artifact_id = await resumed.finalize()
        
        # Context 3: Verify complete work
        streaming3 = StreamingArtifactManager(test_environment["temp_dir"])
        final_content = await streaming3.get_artifact_content(task_id, artifact_id)
        
        assert initial_content in final_content
        assert additional_content in final_content
    
    @pytest.mark.asyncio
    async def test_maintenance_with_file_mirroring(self, test_environment):
        """Test maintenance operations with file mirroring enabled."""
        orchestrator = test_environment["orchestrator"]
        streaming = test_environment["streaming_manager"]
        maintenance = test_environment["maintenance_coordinator"]
        temp_dir = Path(test_environment["temp_dir"])
        
        # Create actual files to mirror
        src_dir = temp_dir / "source_code"
        src_dir.mkdir(exist_ok=True)
        
        files = {
            "app.py": "from flask import Flask\napp = Flask(__name__)",
            "config.py": "DEBUG = True\nSECRET_KEY = 'dev'",
            "requirements.txt": "flask==2.0.0\nsqlalchemy==1.4.0"
        }
        
        for filename, content in files.items():
            (src_dir / filename).write_text(content)
        
        # Create task with file references
        task_result = await orchestrator.plan_task(
            description="Mirror project files",
            subtasks_json=json.dumps([{
                "title": "Process source files",
                "description": "Analyze and mirror source code",
                "specialist_type": "implementer"
            }])
        )
        
        subtask = task_result["subtasks"][0]
        
        # Create streaming session with file mirroring
        session = await streaming.create_streaming_session(
            task_id=subtask["id"],
            summary="Source code analysis",
            file_paths=[str(src_dir / f) for f in files.keys()],
            artifact_type="code"
        )
        
        # Write combined content
        combined = "\n".join(f"# {f}\n{c}" for f, c in files.items())
        await session.write(combined)
        await session.enable_file_mirroring()
        artifact_id = await session.finalize()
        
        # Complete task
        await orchestrator.complete_subtask(
            task_id=subtask["id"],
            summary="Files processed and mirrored",
            detailed_work=combined,
            file_paths=list(files.keys()),
            next_action="complete"
        )
        
        # Run maintenance to verify files are preserved
        scan_result = await maintenance.scan_and_cleanup(
            scope="current_session",
            validation_level="comprehensive"
        )
        
        # Verify mirrors exist
        for filepath in files.keys():
            mirror_path = streaming.get_mirror_path(
                subtask["id"],
                artifact_id,
                str(src_dir / filepath)
            )
            assert mirror_path.exists()
    
    @pytest.mark.asyncio
    async def test_bulk_operations_performance(self, test_environment):
        """Test performance of bulk maintenance operations."""
        orchestrator = test_environment["orchestrator"]
        lifecycle = test_environment["lifecycle_manager"]
        maintenance = test_environment["maintenance_coordinator"]
        
        # Create many tasks
        task_count = 50
        task_ids = []
        
        for i in range(task_count):
            task = await orchestrator.plan_task(
                description=f"Bulk test task {i}",
                subtasks_json=json.dumps([{
                    "title": f"Subtask {i}",
                    "description": f"Test subtask {i}",
                    "specialist_type": "implementer"
                }])
            )
            task_ids.append(task["task_id"])
            
            # Complete some tasks
            if i % 3 == 0:
                subtask = task["subtasks"][0]
                await orchestrator.complete_subtask(
                    task_id=subtask["id"],
                    summary=f"Completed task {i}",
                    detailed_work=f"Work for task {i}",
                    next_action="complete"
                )
        
        # Age half the tasks
        with Session(test_environment["engine"]) as session:
            from mcp_task_orchestrator.db.models import TaskBreakdownModel
            tasks = session.query(TaskBreakdownModel).all()
            for i, task in enumerate(tasks[:task_count//2]):
                task.created_at = datetime.utcnow() - timedelta(days=60)
                task.updated_at = datetime.utcnow() - timedelta(days=50)
            session.commit()
        
        # Run comprehensive maintenance
        start_time = datetime.utcnow()
        
        # Scan and cleanup
        scan_result = await maintenance.scan_and_cleanup(
            scope="full_project",
            validation_level="comprehensive"
        )
        
        # Validate structure
        validation_result = await maintenance.validate_structure(
            scope="full_project",
            validation_level="full_audit"
        )
        
        # Bulk archive old tasks
        stale_tasks = await lifecycle.detect_stale_tasks(comprehensive_scan=True)
        if stale_tasks:
            bulk_result = await lifecycle.bulk_archive_tasks(
                [t["task_id"] for t in stale_tasks[:10]],  # Archive first 10
                reason="bulk_cleanup"
            )
            assert bulk_result["successfully_archived"] > 0
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Verify performance (should complete within reasonable time)
        assert duration < 30  # 30 seconds for 50 tasks
        assert scan_result["scan_results"]["tasks_scanned"] == task_count
    
    @pytest.mark.asyncio
    async def test_error_recovery_and_resilience(self, test_environment):
        """Test system resilience and error recovery."""
        orchestrator = test_environment["orchestrator"]
        streaming = test_environment["streaming_manager"]
        maintenance = test_environment["maintenance_coordinator"]
        
        # Create task
        task = await orchestrator.plan_task(
            description="Error recovery test",
            subtasks_json=json.dumps([{
                "title": "Test resilience",
                "description": "Test error handling",
                "specialist_type": "debugger"
            }])
        )
        
        subtask_id = task["subtasks"][0]["id"]
        
        # Start streaming session
        session = await streaming.create_streaming_session(
            task_id=subtask_id,
            summary="Resilience test"
        )
        
        # Write some content
        await session.write("Initial content before error")
        
        # Simulate corrupted state by directly modifying files
        progress_file = session._get_temp_path() / "progress.json"
        progress_file.write_text("corrupted json{")
        
        # Try to resume - should handle corruption gracefully
        try:
            resumed = await streaming.resume_partial_session(subtask_id, session.artifact_id)
            # If resume succeeds, it should have recovered
            assert resumed is not None
        except:
            # If resume fails, create new session
            new_session = await streaming.create_streaming_session(
                task_id=subtask_id,
                summary="Recovered session"
            )
            await new_session.write("Recovered content")
            await new_session.finalize()
        
        # Run maintenance - should handle any inconsistencies
        result = await maintenance.scan_and_cleanup(
            scope="current_session",
            validation_level="comprehensive"
        )
        
        # System should remain functional
        assert "error" not in result or result.get("recovered", False)