"""
Streaming-aware artifact management system for the MCP Task Orchestrator.

This module provides functionality to handle streaming LLM responses with robust
partial response detection, resumption capabilities, and atomic file operations.
"""

import os
import json
import uuid
import asyncio
import hashlib
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, AsyncIterator
import logging
import aiofiles
from contextlib import asynccontextmanager

logger = logging.getLogger("mcp_task_orchestrator.streaming_artifacts")


class StreamingArtifactManager:
    """Enhanced artifact manager with streaming support and partial response recovery."""
    
    ARTIFACTS_DIR = "artifacts"
    TEMP_DIR = "temp"
    METADATA_FILE = "metadata.json"
    PROGRESS_FILE = "progress.json"
    COMPLETION_MARKER = ".complete"
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialize the streaming artifact manager.
        
        Args:
            base_dir: Base directory for the orchestrator. If None, uses current directory.
        """
        if base_dir is None:
            base_dir = os.getcwd()
        
        self.base_dir = Path(base_dir)
        self.persistence_dir = self.base_dir / ".task_orchestrator"
        self.artifacts_dir = self.persistence_dir / self.ARTIFACTS_DIR
        self.temp_dir = self.persistence_dir / self.TEMP_DIR
        
        # Create directory structure
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized streaming artifact manager with base directory: {base_dir}")
    
    async def create_streaming_session(self, 
                                     task_id: str,
                                     summary: str,
                                     file_paths: Optional[List[str]] = None,
                                     artifact_type: str = "general",
                                     expected_size_hint: Optional[int] = None) -> 'StreamingSession':
        """Create a new streaming session for artifact creation.
        
        Args:
            task_id: ID of the task this artifact belongs to
            summary: Brief summary for database/UI display
            file_paths: List of original file paths being referenced
            artifact_type: Type of artifact (code, documentation, analysis, etc.)
            expected_size_hint: Expected size of content in bytes (for progress tracking)
            
        Returns:
            StreamingSession object for writing content
        """
        # Generate unique artifact ID
        artifact_id = f"artifact_{uuid.uuid4().hex[:8]}"
        
        # Create session
        session = StreamingSession(
            manager=self,
            task_id=task_id,
            artifact_id=artifact_id,
            summary=summary,
            file_paths=file_paths or [],
            artifact_type=artifact_type,
            expected_size_hint=expected_size_hint
        )
        
        await session._initialize()
        return session
    
    async def resume_partial_session(self, task_id: str, artifact_id: str) -> Optional['StreamingSession']:
        """Resume a partially completed streaming session.
        
        Args:
            task_id: Task ID
            artifact_id: Artifact ID to resume
            
        Returns:
            Resumed StreamingSession or None if not found
        """
        temp_dir = self.temp_dir / task_id / artifact_id
        progress_file = temp_dir / self.PROGRESS_FILE
        
        if not progress_file.exists():
            logger.warning(f"No partial session found for {task_id}/{artifact_id}")
            return None
        
        try:
            async with aiofiles.open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.loads(await f.read())
            
            # Verify the partial file exists and is readable
            temp_file = temp_dir / f"{artifact_id}_partial.md"
            if not temp_file.exists():
                logger.error(f"Partial file missing for {task_id}/{artifact_id}")
                return None
            
            # Create resumed session
            session = StreamingSession(
                manager=self,
                task_id=task_id,
                artifact_id=artifact_id,
                summary=progress_data["summary"],
                file_paths=progress_data["file_paths"],
                artifact_type=progress_data["artifact_type"],
                expected_size_hint=progress_data.get("expected_size_hint"),
                resume_data=progress_data
            )
            
            await session._initialize(resume=True)
            logger.info(f"Resumed partial session for {task_id}/{artifact_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error resuming session {task_id}/{artifact_id}: {str(e)}")
            return None
    
    async def list_partial_sessions(self) -> List[Dict[str, Any]]:
        """List all partial sessions that can be resumed.
        
        Returns:
            List of partial session metadata
        """
        partial_sessions = []
        
        if not self.temp_dir.exists():
            return partial_sessions
        
        try:
            for task_dir in self.temp_dir.iterdir():
                if not task_dir.is_dir():
                    continue
                
                for artifact_dir in task_dir.iterdir():
                    if not artifact_dir.is_dir():
                        continue
                    
                    progress_file = artifact_dir / self.PROGRESS_FILE
                    if progress_file.exists():
                        try:
                            async with aiofiles.open(progress_file, 'r', encoding='utf-8') as f:
                                progress_data = json.loads(await f.read())
                            
                            # Add current size information
                            temp_file = artifact_dir / f"{artifact_dir.name}_partial.md"
                            current_size = temp_file.stat().st_size if temp_file.exists() else 0
                            
                            partial_sessions.append({
                                "task_id": task_dir.name,
                                "artifact_id": artifact_dir.name,
                                "summary": progress_data["summary"],
                                "artifact_type": progress_data["artifact_type"],
                                "created_at": progress_data["created_at"],
                                "last_updated": progress_data["last_updated"],
                                "current_size": current_size,
                                "expected_size": progress_data.get("expected_size_hint"),
                                "file_paths": progress_data["file_paths"]
                            })
                        except Exception as e:
                            logger.error(f"Error reading progress file {progress_file}: {str(e)}")
                            continue
        except Exception as e:
            logger.error(f"Error listing partial sessions: {str(e)}")
        
        return partial_sessions
    
    async def cleanup_old_temp_files(self, max_age_hours: int = 24) -> int:
        """Clean up old temporary files that are older than specified age.
        
        Args:
            max_age_hours: Maximum age of temp files in hours
            
        Returns:
            Number of temp directories cleaned up
        """
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        if not self.temp_dir.exists():
            return cleaned_count
        
        try:
            for task_dir in self.temp_dir.iterdir():
                if not task_dir.is_dir():
                    continue
                
                for artifact_dir in task_dir.iterdir():
                    if not artifact_dir.is_dir():
                        continue
                    
                    progress_file = artifact_dir / self.PROGRESS_FILE
                    if progress_file.exists():
                        try:
                            file_time = datetime.fromtimestamp(progress_file.stat().st_mtime)
                            if file_time < cutoff_time:
                                # Remove entire artifact temp directory
                                import shutil
                                shutil.rmtree(artifact_dir)
                                cleaned_count += 1
                                logger.info(f"Cleaned up old temp directory: {artifact_dir}")
                        except Exception as e:
                            logger.error(f"Error cleaning temp directory {artifact_dir}: {str(e)}")
        except Exception as e:
            logger.error(f"Error during temp cleanup: {str(e)}")
        
        return cleaned_count


class StreamingSession:
    """A streaming session for writing artifact content incrementally."""
    
    def __init__(self, 
                 manager: StreamingArtifactManager,
                 task_id: str,
                 artifact_id: str,
                 summary: str,
                 file_paths: List[str],
                 artifact_type: str,
                 expected_size_hint: Optional[int] = None,
                 resume_data: Optional[Dict[str, Any]] = None):
        self.manager = manager
        self.task_id = task_id
        self.artifact_id = artifact_id
        self.summary = summary
        self.file_paths = file_paths
        self.artifact_type = artifact_type
        self.expected_size_hint = expected_size_hint
        self.resume_data = resume_data
        
        # Session state
        self.temp_dir = manager.temp_dir / task_id / artifact_id
        self.temp_file = self.temp_dir / f"{artifact_id}_partial.md"
        self.progress_file = self.temp_dir / manager.PROGRESS_FILE
        self.completion_marker = self.temp_dir / manager.COMPLETION_MARKER
        
        self.bytes_written = 0
        self.started_at = datetime.utcnow()
        self.last_update = self.started_at
        self.is_completed = False
        self.file_handle = None
        self.content_hash = hashlib.sha256()
    
    async def _initialize(self, resume: bool = False):
        """Initialize the streaming session."""
        # Create temp directory
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        if resume and self.resume_data:
            # Resume from existing file
            self.bytes_written = self.temp_file.stat().st_size if self.temp_file.exists() else 0
            self.started_at = datetime.fromisoformat(self.resume_data["created_at"])
            self.last_update = datetime.fromisoformat(self.resume_data["last_updated"])
            
            # Re-calculate hash for existing content
            if self.temp_file.exists():
                async with aiofiles.open(self.temp_file, 'rb') as f:
                    while True:
                        chunk = await f.read(8192)
                        if not chunk:
                            break
                        self.content_hash.update(chunk)
        else:
            # Create initial progress file
            await self._update_progress()
    
    @asynccontextmanager
    async def write_stream(self):
        """Context manager for streaming writes."""
        try:
            # Open file for appending (or writing if new)
            mode = 'a' if self.resume_data else 'w'
            self.file_handle = await aiofiles.open(self.temp_file, mode, encoding='utf-8')
            
            if not self.resume_data:
                # Write artifact header for new files
                header = await self._create_artifact_header()
                await self._write_content(header)
            
            yield self
            
        finally:
            if self.file_handle:
                await self.file_handle.close()
                self.file_handle = None
    
    async def write_chunk(self, content: str, is_final: bool = False):
        """Write a chunk of content to the streaming artifact.
        
        Args:
            content: Content chunk to write
            is_final: Whether this is the final chunk
        """
        if not self.file_handle:
            raise RuntimeError("write_stream context manager not active")
        
        await self._write_content(content)
        
        # Update progress periodically (every 1KB or 5 seconds)
        current_time = datetime.utcnow()
        time_diff = (current_time - self.last_update).total_seconds()
        
        if self.bytes_written % 1024 == 0 or time_diff >= 5 or is_final:
            await self._update_progress()
        
        if is_final:
            await self._finalize()
    
    async def _write_content(self, content: str):
        """Write content to file and update tracking."""
        await self.file_handle.write(content)
        await self.file_handle.flush()  # Force write to disk
        
        content_bytes = content.encode('utf-8')
        self.bytes_written += len(content_bytes)
        self.content_hash.update(content_bytes)
        self.last_update = datetime.utcnow()
    
    async def _update_progress(self):
        """Update the progress tracking file."""
        progress_data = {
            "task_id": self.task_id,
            "artifact_id": self.artifact_id,
            "summary": self.summary,
            "artifact_type": self.artifact_type,
            "file_paths": self.file_paths,
            "expected_size_hint": self.expected_size_hint,
            "created_at": self.started_at.isoformat(),
            "last_updated": self.last_update.isoformat(),
            "bytes_written": self.bytes_written,
            "content_hash": self.content_hash.hexdigest(),
            "is_completed": self.is_completed
        }
        
        async with aiofiles.open(self.progress_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(progress_data, indent=2))
    
    async def _create_artifact_header(self) -> str:
        """Create the artifact header content."""
        header_lines = [
            f"# Task Artifact: {self.task_id}",
            "",
            f"**Type:** {self.artifact_type}",
            f"**Created:** {self.started_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Summary:** {self.summary}",
            ""
        ]
        
        if self.file_paths:
            header_lines.extend([
                "## Referenced Files",
                ""
            ])
            for file_path in self.file_paths:
                header_lines.append(f"- `{file_path}`")
            header_lines.append("")
        
        header_lines.extend([
            "## Detailed Work",
            "",
            "<!-- STREAMING CONTENT BEGINS HERE -->",
            ""
        ])
        
        return "\n".join(header_lines)
    
    async def _finalize(self):
        """Finalize the streaming session and move to permanent location."""
        if self.is_completed:
            return
        
        # Add footer
        footer = [
            "",
            "<!-- STREAMING CONTENT ENDS HERE -->",
            "",
            "---",
            "",
            f"*This artifact was generated by the MCP Task Orchestrator on {self.last_update.strftime('%Y-%m-%d %H:%M:%S UTC')}*",
            f"*Task ID: {self.task_id}*",
            f"*Artifact ID: {self.artifact_id}*",
            f"*Content Hash: {self.content_hash.hexdigest()}*"
        ]
        
        await self._write_content("\n".join(footer))
        await self.file_handle.flush()
        
        # Mark as completed
        self.is_completed = True
        await self._update_progress()
        
        # Create completion marker
        async with aiofiles.open(self.completion_marker, 'w') as f:
            await f.write(json.dumps({
                "completed_at": datetime.utcnow().isoformat(),
                "final_size": self.bytes_written,
                "content_hash": self.content_hash.hexdigest()
            }))
        
        # Move to permanent location
        await self._move_to_permanent_location()
    
    async def _move_to_permanent_location(self):
        """Atomically move the completed file to its permanent location."""
        # Create task-specific directory in artifacts
        task_artifact_dir = self.manager.artifacts_dir / self.task_id
        task_artifact_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine final file path
        if self.file_paths and len(self.file_paths) > 0:
            # Use mirrored structure
            mirrored_paths = self._create_mirrored_structure(task_artifact_dir)
            final_path = mirrored_paths[0]
        else:
            # Use simple artifact file
            final_path = task_artifact_dir / f"{self.artifact_id}.md"
        
        final_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Atomic move
        import shutil
        shutil.move(str(self.temp_file), str(final_path))
        
        # Create metadata
        await self._create_metadata(final_path, mirrored_paths if self.file_paths else [final_path])
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir)
        
        logger.info(f"Finalized streaming artifact {self.artifact_id} for task {self.task_id}")
    
    def _create_mirrored_structure(self, task_dir: Path) -> List[Path]:
        """Create mirrored directory structure (synchronous version)."""
        mirrored_paths = []
        
        for file_path in self.file_paths:
            original_path = Path(file_path)
            
            if original_path.is_absolute():
                relative_parts = original_path.parts
                if len(relative_parts) > 0 and ':' in relative_parts[0]:
                    relative_parts = relative_parts[1:]
                elif len(relative_parts) > 0 and relative_parts[0] == '/':
                    relative_parts = relative_parts[1:]
                
                mirrored_path = task_dir / "mirrored" / Path(*relative_parts)
            else:
                mirrored_path = task_dir / "mirrored" / original_path
            
            if not mirrored_path.suffix:
                mirrored_path = mirrored_path.with_suffix('.md')
            elif mirrored_path.suffix != '.md':
                mirrored_path = mirrored_path.with_suffix(mirrored_path.suffix + '.md')
            
            stem = mirrored_path.stem
            mirrored_path = mirrored_path.with_name(f"{stem}_{self.artifact_id}.md")
            mirrored_paths.append(mirrored_path)
        
        if not mirrored_paths:
            mirrored_paths = [task_dir / f"{self.artifact_id}.md"]
        
        return mirrored_paths
    
    async def _create_metadata(self, primary_path: Path, mirrored_paths: List[Path]):
        """Create metadata files for the completed artifact."""
        metadata = {
            "artifact_id": self.artifact_id,
            "task_id": self.task_id,
            "summary": self.summary,
            "artifact_type": self.artifact_type,
            "file_paths": self.file_paths,
            "mirrored_paths": [str(p) for p in mirrored_paths],
            "created_at": self.started_at.isoformat(),
            "completed_at": self.last_update.isoformat(),
            "final_size": self.bytes_written,
            "content_hash": self.content_hash.hexdigest(),
            "primary_file": str(primary_path),
            "relative_path": str(primary_path.relative_to(self.manager.artifacts_dir))
        }
        
        # Store metadata
        metadata_file = primary_path.parent / f"{self.artifact_id}_metadata.json"
        async with aiofiles.open(metadata_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(metadata, indent=2))
        
        # Update task index
        await self._update_task_metadata_index(metadata)
    
    async def _update_task_metadata_index(self, metadata: Dict[str, Any]):
        """Update the task metadata index."""
        task_dir = self.manager.artifacts_dir / self.task_id
        index_file = task_dir / "task_index.json"
        
        # Load existing index or create new one
        if index_file.exists():
            try:
                async with aiofiles.open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.loads(await f.read())
            except:
                index_data = {"task_id": self.task_id, "artifacts": []}
        else:
            index_data = {"task_id": self.task_id, "artifacts": []}
        
        # Add new artifact to index
        index_data["artifacts"].append({
            "artifact_id": metadata["artifact_id"],
            "summary": metadata["summary"],
            "artifact_type": metadata["artifact_type"],
            "created_at": metadata["created_at"],
            "completed_at": metadata["completed_at"],
            "final_size": metadata["final_size"],
            "content_hash": metadata["content_hash"],
            "primary_file": metadata["primary_file"],
            "relative_path": metadata["relative_path"]
        })
        
        # Sort by creation time (newest first)
        index_data["artifacts"].sort(key=lambda x: x["created_at"], reverse=True)
        
        # Write updated index
        async with aiofiles.open(index_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(index_data, indent=2))
    
    def get_progress_info(self) -> Dict[str, Any]:
        """Get current progress information."""
        progress_percent = None
        if self.expected_size_hint and self.expected_size_hint > 0:
            progress_percent = min(100.0, (self.bytes_written / self.expected_size_hint) * 100)
        
        return {
            "task_id": self.task_id,
            "artifact_id": self.artifact_id,
            "bytes_written": self.bytes_written,
            "progress_percent": progress_percent,
            "started_at": self.started_at.isoformat(),
            "last_updated": self.last_update.isoformat(),
            "is_completed": self.is_completed,
            "content_hash": self.content_hash.hexdigest()
        }


# Convenience functions for backward compatibility
async def create_streaming_artifact(base_dir: str,
                                  task_id: str,
                                  summary: str,
                                  content_generator: AsyncIterator[str],
                                  file_paths: Optional[List[str]] = None,
                                  artifact_type: str = "general") -> Dict[str, Any]:
    """Create an artifact from a streaming content generator.
    
    Args:
        base_dir: Base directory for artifact storage
        task_id: Task ID
        summary: Brief summary
        content_generator: Async generator yielding content chunks
        file_paths: Optional file paths to mirror
        artifact_type: Type of artifact
        
    Returns:
        Artifact information dictionary
    """
    manager = StreamingArtifactManager(base_dir)
    session = await manager.create_streaming_session(
        task_id=task_id,
        summary=summary,
        file_paths=file_paths,
        artifact_type=artifact_type
    )
    
    async with session.write_stream():
        async for chunk in content_generator:
            await session.write_chunk(chunk)
        await session.write_chunk("", is_final=True)
    
    return {
        "artifact_id": session.artifact_id,
        "summary": session.summary,
        "artifact_type": session.artifact_type,
        "final_size": session.bytes_written,
        "content_hash": session.content_hash.hexdigest(),
        "task_id": session.task_id
    }
