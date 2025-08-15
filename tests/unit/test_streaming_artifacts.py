"""
Comprehensive test suite for the StreamingArtifactManager component.

Tests large content storage without truncation, cross-context accessibility,
file mirroring functionality, and metadata preservation.
"""

import pytest
import asyncio
import os
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, mock_open
import aiofiles

# from mcp_task_orchestrator.orchestrator.streaming_artifacts import  # TODO: Complete this import


class TestStreamingArtifactManager:
    """Test suite for StreamingArtifactManager functionality."""
    
    @pytest.fixture
    async def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    async def artifact_manager(self, temp_dir):
        """Create a StreamingArtifactManager instance."""
        return StreamingArtifactManager(base_dir=temp_dir)
    
    # Test basic streaming session creation
    @pytest.mark.asyncio
    async def test_create_streaming_session(self, artifact_manager):
        """Test creating a new streaming session."""
        session = await artifact_manager.create_streaming_session(
            task_id="test_task",
            summary="Test artifact creation",
            file_paths=["/path/to/file.py"],
            artifact_type="code",
            expected_size_hint=1000
        )
        
        assert session is not None
        assert session.task_id == "test_task"
        assert session.summary == "Test artifact creation"
        assert session.artifact_type == "code"
        assert session.expected_size_hint == 1000
        assert len(session.file_paths) == 1
    
    # Test large content storage
    @pytest.mark.asyncio
    async def test_store_large_content_without_truncation(self, artifact_manager):
        """Test storing large content without truncation."""
        # Create large content (10MB)
        large_content = "x" * (10 * 1024 * 1024)  # 10MB
        
        session = await artifact_manager.create_streaming_session(
            task_id="large_content_task",
            summary="Large content test",
            artifact_type="data",
            expected_size_hint=len(large_content)
        )
        
        # Write content in chunks
        chunk_size = 1024 * 1024  # 1MB chunks
        for i in range(0, len(large_content), chunk_size):
            chunk = large_content[i:i + chunk_size]
            await session.write(chunk)
        
        # Finalize session
        artifact_id = await session.finalize()
        
        # Verify content was stored completely
        stored_content = await artifact_manager.get_artifact_content(
            "large_content_task", 
            artifact_id
        )
        
        assert len(stored_content) == len(large_content)
        assert stored_content == large_content
    
    @pytest.mark.asyncio
    async def test_streaming_with_progress_tracking(self, artifact_manager):
        """Test streaming with progress tracking."""
        total_size = 1000000  # 1MB
        
        session = await artifact_manager.create_streaming_session(
            task_id="progress_task",
            summary="Progress tracking test",
            expected_size_hint=total_size
        )
        
        # Write content and track progress
        chunk_size = 100000  # 100KB
        progress_updates = []
        
        for i in range(0, total_size, chunk_size):
            chunk = "x" * chunk_size
            await session.write(chunk)
            progress = await session.get_progress()
            progress_updates.append(progress)
        
        # Verify progress was tracked correctly
        assert len(progress_updates) == 10
        assert progress_updates[0]["bytes_written"] == chunk_size
        assert progress_updates[-1]["bytes_written"] == total_size
        assert all(0 <= p["progress_percentage"] <= 100 for p in progress_updates)
    
    # Test cross-context accessibility
    @pytest.mark.asyncio
    async def test_cross_context_accessibility(self, artifact_manager):
        """Test artifacts remain accessible across different contexts."""
        # Context 1: Create artifact
        session1 = await artifact_manager.create_streaming_session(
            task_id="cross_context_task",
            summary="Cross-context test"
        )
        
        test_content = "This content should be accessible across contexts"
        await session1.write(test_content)
        artifact_id = await session1.finalize()
        
        # Simulate context switch by creating new manager instance
        new_manager = StreamingArtifactManager(base_dir=artifact_manager.base_dir.parent)
        
        # Context 2: Access artifact
        retrieved_content = await new_manager.get_artifact_content(
            "cross_context_task",
            artifact_id
        )
        
        assert retrieved_content == test_content
    
    @pytest.mark.asyncio
    async def test_resume_partial_session(self, artifact_manager):
        """Test resuming a partially completed streaming session."""
        # Start a session and write partial content
        session = await artifact_manager.create_streaming_session(
            task_id="partial_task",
            summary="Partial session test",
            expected_size_hint=1000
        )
        
        partial_content = "First part of content"
        await session.write(partial_content)
        
        # Save session state without finalizing
        await session._save_progress()
        
        # Simulate interruption - create new manager
        new_manager = StreamingArtifactManager(base_dir=artifact_manager.base_dir.parent)
        
        # Resume session
        resumed_session = await new_manager.resume_partial_session(
            "partial_task",
            session.artifact_id
        )
        
        assert resumed_session is not None
        assert resumed_session.bytes_written == len(partial_content)
        
        # Complete the session
        additional_content = " - Second part of content"
        await resumed_session.write(additional_content)
        artifact_id = await resumed_session.finalize()
        
        # Verify complete content
        final_content = await new_manager.get_artifact_content(
            "partial_task",
            artifact_id
        )
        assert final_content == partial_content + additional_content
    
    # Test file mirroring
    @pytest.mark.asyncio
    async def test_file_mirroring_basic(self, artifact_manager, temp_dir):
        """Test basic file mirroring functionality."""
        # Create a test file
        test_file_path = Path(temp_dir) / "test_file.py"
        test_content = """
def hello_world():
    print("Hello, World!")
    return 42
"""
        test_file_path.write_text(test_content)
        
        # Create session with file mirroring
        session = await artifact_manager.create_streaming_session(
            task_id="mirror_task",
            summary="File mirroring test",
            file_paths=[str(test_file_path)],
            artifact_type="code"
        )
        
        # Write content and enable mirroring
        await session.write(test_content)
        await session.enable_file_mirroring()
        artifact_id = await session.finalize()
        
        # Verify mirror was created
        mirror_path = artifact_manager.get_mirror_path("mirror_task", artifact_id, str(test_file_path))
        assert mirror_path.exists()
        assert mirror_path.read_text() == test_content
    
    @pytest.mark.asyncio
    async def test_file_mirroring_multiple_files(self, artifact_manager, temp_dir):
        """Test mirroring multiple files."""
        # Create multiple test files
        files = {}
        for i in range(3):
            file_path = Path(temp_dir) / f"file_{i}.txt"
            content = f"Content of file {i}"
            file_path.write_text(content)
            files[str(file_path)] = content
        
        # Create session for multiple files
        session = await artifact_manager.create_streaming_session(
            task_id="multi_mirror_task",
            summary="Multiple file mirroring",
            file_paths=list(files.keys()),
            artifact_type="data"
        )
        
        # Write all content
        combined_content = "\n---\n".join(files.values())
        await session.write(combined_content)
        await session.enable_file_mirroring()
        artifact_id = await session.finalize()
        
        # Verify all mirrors were created
        for file_path, content in files.items():
            mirror_path = artifact_manager.get_mirror_path(
                "multi_mirror_task", 
                artifact_id, 
                file_path
            )
            assert mirror_path.exists()
            # Mirror contains the combined content in this case
    
    # Test metadata preservation
    @pytest.mark.asyncio
    async def test_metadata_preservation(self, artifact_manager):
        """Test metadata is preserved with artifacts."""
        # Create session with rich metadata
        metadata = {
            "author": "test_user",
            "version": "1.0.0",
            "tags": ["important", "reviewed"],
            "custom_field": {"nested": "value"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        session = await artifact_manager.create_streaming_session(
            task_id="metadata_task",
            summary="Metadata preservation test",
            artifact_type="documentation"
        )
        
        # Add custom metadata
        await session.add_metadata(metadata)
        
        # Write content
        await session.write("Content with metadata")
        artifact_id = await session.finalize()
        
        # Retrieve and verify metadata
        retrieved_metadata = await artifact_manager.get_artifact_metadata(
            "metadata_task",
            artifact_id
        )
        
        assert retrieved_metadata["author"] == "test_user"
        assert retrieved_metadata["version"] == "1.0.0"
        assert "important" in retrieved_metadata["tags"]
        assert retrieved_metadata["custom_field"]["nested"] == "value"
    
    @pytest.mark.asyncio
    async def test_artifact_listing_and_search(self, artifact_manager):
        """Test listing and searching artifacts."""
        # Create multiple artifacts
        task_id = "search_task"
        artifact_ids = []
        
        for i in range(5):
            session = await artifact_manager.create_streaming_session(
                task_id=task_id,
                summary=f"Artifact {i}",
                artifact_type="code" if i % 2 == 0 else "documentation"
            )
            await session.write(f"Content {i}")
            artifact_id = await session.finalize()
            artifact_ids.append(artifact_id)
        
        # List all artifacts for task
        all_artifacts = await artifact_manager.list_artifacts(task_id)
        assert len(all_artifacts) == 5
        
        # Search by type
        code_artifacts = await artifact_manager.search_artifacts(
            task_id,
            artifact_type="code"
        )
        assert len(code_artifacts) == 3
        
        doc_artifacts = await artifact_manager.search_artifacts(
            task_id,
            artifact_type="documentation"
        )
        assert len(doc_artifacts) == 2
    
    # Test atomic operations
    @pytest.mark.asyncio
    async def test_atomic_file_operations(self, artifact_manager):
        """Test atomic file operations prevent corruption."""
        session = await artifact_manager.create_streaming_session(
            task_id="atomic_task",
            summary="Atomic operations test"
        )
        
        # Write initial content
        await session.write("Initial content")
        
        # Simulate failure during write
        with patch('aiofiles.open', side_effect=IOError("Simulated write failure")):
            with pytest.raises(IOError):
                await session.write("This should fail")
        
        # Verify session can recover
        await session.write(" - Additional content")
        artifact_id = await session.finalize()
        
        # Verify content integrity
        content = await artifact_manager.get_artifact_content("atomic_task", artifact_id)
        assert "Initial content" in content
        assert "Additional content" in content
        assert "This should fail" not in content
    
    # Test cleanup and lifecycle
    @pytest.mark.asyncio
    async def test_cleanup_incomplete_sessions(self, artifact_manager):
        """Test cleanup of incomplete streaming sessions."""
        # Create multiple sessions, some incomplete
        task_id = "cleanup_task"
        
        # Complete session
        complete_session = await artifact_manager.create_streaming_session(
            task_id=task_id,
            summary="Complete session"
        )
        await complete_session.write("Complete content")
        complete_id = await complete_session.finalize()
        
        # Incomplete sessions
        for i in range(3):
            incomplete = await artifact_manager.create_streaming_session(
                task_id=task_id,
                summary=f"Incomplete {i}"
            )
            await incomplete.write(f"Partial content {i}")
            # Don't finalize - leave incomplete
        
        # Run cleanup
        cleanup_result = await artifact_manager.cleanup_incomplete_sessions(
            max_age_hours=0  # Cleanup all incomplete immediately
        )
        
        assert cleanup_result["cleaned_sessions"] == 3
        assert cleanup_result["preserved_sessions"] == 1
        
        # Verify complete artifact still exists
        content = await artifact_manager.get_artifact_content(task_id, complete_id)
        assert content == "Complete content"
    
    @pytest.mark.asyncio
    async def test_concurrent_streaming_sessions(self, artifact_manager):
        """Test handling multiple concurrent streaming sessions."""
        task_id = "concurrent_task"
        session_count = 10
        
        async def create_and_write_session(index):
            session = await artifact_manager.create_streaming_session(
                task_id=task_id,
                summary=f"Concurrent session {index}"
            )
            
            # Write content in chunks
            for chunk in range(5):
                await session.write(f"Session {index} chunk {chunk}\n")
                await asyncio.sleep(0.01)  # Simulate work
            
            return await session.finalize()
        
        # Create sessions concurrently
        artifact_ids = await asyncio.gather(*[
            create_and_write_session(i) for i in range(session_count)
        ])
        
        # Verify all sessions completed successfully
        assert len(artifact_ids) == session_count
        assert len(set(artifact_ids)) == session_count  # All unique
        
        # Verify content integrity
        for i, artifact_id in enumerate(artifact_ids):
            content = await artifact_manager.get_artifact_content(task_id, artifact_id)
            assert f"Session {i}" in content
            assert content.count("chunk") == 5
    
    # Test error handling
    @pytest.mark.asyncio
    async def test_disk_space_handling(self, artifact_manager):
        """Test handling of disk space issues."""
        session = await artifact_manager.create_streaming_session(
            task_id="disk_space_task",
            summary="Disk space test"
        )
        
        # Mock disk space check
        with patch('shutil.disk_usage', return_value=(100, 90, 10)):  # Only 10 bytes free
            with pytest.raises(IOError, match="Insufficient disk space"):
                await session.write("x" * 1000)  # Try to write 1000 bytes
    
    @pytest.mark.asyncio
    async def test_corruption_detection(self, artifact_manager):
        """Test detection of corrupted artifacts."""
        task_id = "corruption_task"
        
        # Create valid artifact
        session = await artifact_manager.create_streaming_session(
            task_id=task_id,
            summary="Corruption test"
        )
        await session.write("Valid content")
        artifact_id = await session.finalize()
        
        # Corrupt the artifact file
        artifact_path = artifact_manager.artifacts_dir / task_id / artifact_id / "content.bin"
        artifact_path.write_bytes(b"corrupted data")
        
        # Also corrupt metadata
        metadata_path = artifact_manager.artifacts_dir / task_id / artifact_id / "metadata.json"
        metadata_path.write_text("invalid json{")
        
        # Try to read corrupted artifact
        with pytest.raises(Exception):  # Should raise corruption error
            await artifact_manager.verify_artifact_integrity(task_id, artifact_id)
    
    @pytest.mark.asyncio
    async def test_streaming_session_timeout(self, artifact_manager):
        """Test timeout handling for streaming sessions."""
        session = await artifact_manager.create_streaming_session(
            task_id="timeout_task",
            summary="Timeout test",
            session_timeout_seconds=1  # 1 second timeout
        )
        
        await session.write("Initial write")
        
        # Wait longer than timeout
        await asyncio.sleep(2)
        
        # Session should be auto-closed
        with pytest.raises(Exception, match="Session expired"):
            await session.write("This should fail")