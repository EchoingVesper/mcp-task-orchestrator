"""
Artifact management system for the MCP Task Orchestrator.

This module provides functionality to store detailed work results as artifacts
that mirror the original file structure, preventing context limit issues while
maintaining accessibility.
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

logger = logging.getLogger("mcp_task_orchestrator.artifacts")


class ArtifactManager:
    """Manages storage and retrieval of task artifacts with file system mirroring."""
    
    ARTIFACTS_DIR = "artifacts"
    METADATA_FILE = "metadata.json"
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialize the artifact manager.
        
        Args:
            base_dir: Base directory for the orchestrator. If None, uses current directory.
        """
        if base_dir is None:
            base_dir = os.getcwd()
        
        self.base_dir = Path(base_dir)
        self.persistence_dir = self.base_dir / ".task_orchestrator"
        self.artifacts_dir = self.persistence_dir / self.ARTIFACTS_DIR
        
        # Create directory structure
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized artifact manager with base directory: {base_dir}")
    
    def store_artifact(self, 
                      task_id: str,
                      summary: str,
                      detailed_work: str,
                      file_paths: Optional[List[str]] = None,
                      artifact_type: str = "general") -> Dict[str, Any]:
        """Store detailed work as an artifact with file system mirroring.
        
        Args:
            task_id: ID of the task this artifact belongs to
            summary: Brief summary for database/UI display
            detailed_work: Full detailed work content to store
            file_paths: List of original file paths being referenced
            artifact_type: Type of artifact (code, documentation, analysis, etc.)
            
        Returns:
            Dictionary containing artifact information and file paths
        """
        # Generate unique artifact ID
        artifact_id = f"artifact_{uuid.uuid4().hex[:8]}"
        
        # Create task-specific directory
        task_artifact_dir = self.artifacts_dir / task_id
        task_artifact_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine the primary storage structure
        if file_paths and len(file_paths) > 0:
            # Mirror the file structure
            mirrored_paths = self._create_mirrored_structure(
                task_artifact_dir, file_paths, artifact_id
            )
        else:
            # Use a general artifact file
            mirrored_paths = [task_artifact_dir / f"{artifact_id}.md"]
        
        # Store the detailed work in the primary artifact file
        primary_artifact_path = mirrored_paths[0]
        primary_artifact_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create comprehensive artifact content
        artifact_content = self._create_artifact_content(
            task_id, summary, detailed_work, file_paths, artifact_type
        )
        
        # Write the artifact file
        with open(primary_artifact_path, 'w', encoding='utf-8') as f:
            f.write(artifact_content)
        
        # Create metadata
        metadata = {
            "artifact_id": artifact_id,
            "task_id": task_id,
            "summary": summary,
            "artifact_type": artifact_type,
            "file_paths": file_paths or [],
            "mirrored_paths": [str(p) for p in mirrored_paths],
            "created_at": datetime.utcnow().isoformat(),
            "primary_file": str(primary_artifact_path),
            "relative_path": str(primary_artifact_path.relative_to(self.artifacts_dir))
        }
        
        # Store metadata
        metadata_file = task_artifact_dir / f"{artifact_id}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Update task metadata index
        self._update_task_metadata_index(task_id, metadata)
        
        logger.info(f"Stored artifact {artifact_id} for task {task_id}")
        
        return {
            "artifact_id": artifact_id,
            "summary": summary,
            "artifact_type": artifact_type,
            "primary_file": str(primary_artifact_path),
            "relative_path": metadata["relative_path"],
            "mirrored_paths": metadata["mirrored_paths"],
            "accessible_via": f".task_orchestrator/artifacts/{task_id}/{artifact_id}.md"
        }
    
    def _create_mirrored_structure(self, 
                                  task_dir: Path, 
                                  file_paths: List[str], 
                                  artifact_id: str) -> List[Path]:
        """Create a mirrored directory structure for the original file paths.
        
        Args:
            task_dir: Task-specific artifact directory
            file_paths: Original file paths to mirror
            artifact_id: Unique artifact identifier
            
        Returns:
            List of mirrored file paths
        """
        mirrored_paths = []
        
        for file_path in file_paths:
            # Normalize the path
            original_path = Path(file_path)
            
            # Create mirrored structure
            if original_path.is_absolute():
                # For absolute paths, create a structure under the task directory
                # Remove drive letter and leading separators
                relative_parts = original_path.parts
                if len(relative_parts) > 0 and ':' in relative_parts[0]:
                    # Windows absolute path - remove drive
                    relative_parts = relative_parts[1:]
                elif len(relative_parts) > 0 and relative_parts[0] == '/':
                    # Unix absolute path - remove leading slash
                    relative_parts = relative_parts[1:]
                
                mirrored_path = task_dir / "mirrored" / Path(*relative_parts)
            else:
                # For relative paths, use them directly
                mirrored_path = task_dir / "mirrored" / original_path
            
            # Ensure the file has .md extension for artifact storage
            if not mirrored_path.suffix:
                mirrored_path = mirrored_path.with_suffix('.md')
            elif mirrored_path.suffix != '.md':
                mirrored_path = mirrored_path.with_suffix(mirrored_path.suffix + '.md')
            
            # Add artifact ID to avoid conflicts
            stem = mirrored_path.stem
            mirrored_path = mirrored_path.with_name(f"{stem}_{artifact_id}.md")
            
            mirrored_paths.append(mirrored_path)
        
        # If no valid mirrored paths created, use a default
        if not mirrored_paths:
            mirrored_paths = [task_dir / f"{artifact_id}.md"]
        
        return mirrored_paths
    
    def _create_artifact_content(self,
                                task_id: str,
                                summary: str,
                                detailed_work: str,
                                file_paths: Optional[List[str]],
                                artifact_type: str) -> str:
        """Create comprehensive artifact content with metadata.
        
        Args:
            task_id: Task ID
            summary: Brief summary
            detailed_work: Detailed work content
            file_paths: Original file paths
            artifact_type: Type of artifact
            
        Returns:
            Formatted artifact content as markdown
        """
        content_lines = [
            f"# Task Artifact: {task_id}",
            "",
            f"**Type:** {artifact_type}",
            f"**Created:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Summary:** {summary}",
            ""
        ]
        
        if file_paths:
            content_lines.extend([
                "## Referenced Files",
                ""
            ])
            for file_path in file_paths:
                content_lines.append(f"- `{file_path}`")
            content_lines.append("")
        
        content_lines.extend([
            "## Detailed Work",
            "",
            detailed_work,
            "",
            "---",
            "",
            f"*This artifact was generated by the MCP Task Orchestrator on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*",
            f"*Task ID: {task_id}*"
        ])
        
        return "\n".join(content_lines)
    
    def _update_task_metadata_index(self, task_id: str, metadata: Dict[str, Any]) -> None:
        """Update the task metadata index with new artifact information.
        
        Args:
            task_id: Task ID
            metadata: Artifact metadata
        """
        task_dir = self.artifacts_dir / task_id
        index_file = task_dir / "task_index.json"
        
        # Load existing index or create new one
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                index_data = {"task_id": task_id, "artifacts": []}
        else:
            index_data = {"task_id": task_id, "artifacts": []}
        
        # Add new artifact to index
        index_data["artifacts"].append({
            "artifact_id": metadata["artifact_id"],
            "summary": metadata["summary"],
            "artifact_type": metadata["artifact_type"],
            "created_at": metadata["created_at"],
            "primary_file": metadata["primary_file"],
            "relative_path": metadata["relative_path"]
        })
        
        # Sort by creation time (newest first)
        index_data["artifacts"].sort(key=lambda x: x["created_at"], reverse=True)
        
        # Write updated index
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2)
    
    def get_task_artifacts(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all artifacts for a specific task.
        
        Args:
            task_id: Task ID
            
        Returns:
            List of artifact metadata
        """
        task_dir = self.artifacts_dir / task_id
        index_file = task_dir / "task_index.json"
        
        if not index_file.exists():
            return []
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
                return index_data.get("artifacts", [])
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading task index for {task_id}: {str(e)}")
            return []
    
    def get_artifact_content(self, task_id: str, artifact_id: str) -> Optional[str]:
        """Retrieve the content of a specific artifact.
        
        Args:
            task_id: Task ID
            artifact_id: Artifact ID
            
        Returns:
            Artifact content or None if not found
        """
        task_dir = self.artifacts_dir / task_id
        
        # Try to find the artifact file
        possible_files = [
            task_dir / f"{artifact_id}.md",
            task_dir / f"{artifact_id}_metadata.json"
        ]
        
        # Look for metadata file first to get exact path
        metadata_file = task_dir / f"{artifact_id}_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    primary_file = Path(metadata["primary_file"])
                    
                    if primary_file.exists():
                        with open(primary_file, 'r', encoding='utf-8') as content_file:
                            return content_file.read()
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error reading artifact {artifact_id}: {str(e)}")
        
        # Fallback: try direct artifact file
        artifact_file = task_dir / f"{artifact_id}.md"
        if artifact_file.exists():
            try:
                with open(artifact_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except IOError as e:
                logger.error(f"Error reading artifact file {artifact_file}: {str(e)}")
        
        return None
    
    def list_all_artifacts(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all artifacts organized by task.
        
        Returns:
            Dictionary mapping task IDs to their artifacts
        """
        all_artifacts = {}
        
        if not self.artifacts_dir.exists():
            return all_artifacts
        
        for task_dir in self.artifacts_dir.iterdir():
            if task_dir.is_dir():
                task_id = task_dir.name
                all_artifacts[task_id] = self.get_task_artifacts(task_id)
        
        return all_artifacts
    
    def cleanup_artifacts(self, max_age_days: int = 30) -> int:
        """Clean up old artifacts based on age.
        
        Args:
            max_age_days: Maximum age of artifacts in days
            
        Returns:
            Number of artifacts cleaned up
        """
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        cleaned_count = 0
        
        for task_dir in self.artifacts_dir.iterdir():
            if task_dir.is_dir():
                task_id = task_dir.name
                artifacts = self.get_task_artifacts(task_id)
                
                for artifact in artifacts:
                    created_at = datetime.fromisoformat(artifact["created_at"])
                    if created_at < cutoff_date:
                        # Remove artifact files
                        try:
                            artifact_file = Path(artifact["primary_file"])
                            if artifact_file.exists():
                                artifact_file.unlink()
                            
                            metadata_file = task_dir / f"{artifact['artifact_id']}_metadata.json"
                            if metadata_file.exists():
                                metadata_file.unlink()
                            
                            cleaned_count += 1
                            logger.info(f"Cleaned up old artifact {artifact['artifact_id']}")
                        except Exception as e:
                            logger.error(f"Error cleaning artifact {artifact['artifact_id']}: {str(e)}")
                
                # Update task index to remove cleaned artifacts
                self._rebuild_task_index(task_id)
        
        return cleaned_count
    
    def _rebuild_task_index(self, task_id: str) -> None:
        """Rebuild the task index based on existing files.
        
        Args:
            task_id: Task ID to rebuild index for
        """
        task_dir = self.artifacts_dir / task_id
        index_file = task_dir / "task_index.json"
        
        if not task_dir.exists():
            return
        
        # Find all metadata files
        artifacts = []
        for metadata_file in task_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    artifacts.append({
                        "artifact_id": metadata["artifact_id"],
                        "summary": metadata["summary"],
                        "artifact_type": metadata["artifact_type"],
                        "created_at": metadata["created_at"],
                        "primary_file": metadata["primary_file"],
                        "relative_path": metadata["relative_path"]
                    })
            except Exception as e:
                logger.error(f"Error reading metadata file {metadata_file}: {str(e)}")
        
        # Sort by creation time (newest first)
        artifacts.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Write updated index
        index_data = {"task_id": task_id, "artifacts": artifacts}
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error rebuilding task index for {task_id}: {str(e)}")
