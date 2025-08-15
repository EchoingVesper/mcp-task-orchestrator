"""
Artifact reference value object for storing references to task artifacts.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class ArtifactReference:
    """
    Value object representing a reference to a stored task artifact.
    
    Artifacts are used to store detailed work output to prevent context limits
    while maintaining access to the full work content.
    """
    artifact_id: str
    task_id: str
    path: str
    content_type: str
    size: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.artifact_id,
            "task_id": self.task_id,
            "path": self.path,
            "type": self.content_type,
            "size": self.size,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArtifactReference":
        """Create from dictionary representation."""
        return cls(
            artifact_id=data["id"],
            task_id=data["task_id"],
            path=data["path"],
            content_type=data["type"],
            size=data["size"],
            metadata=data.get("metadata", {})
        )
    
    # NOTE: File system operations removed to comply with Clean Architecture
    # These operations should be implemented in an ArtifactRepository
    # or ArtifactService in the infrastructure layer
    
    def get_file_path(self) -> str:
        """Get the file path for this artifact."""
        return self.path
    
    def get_size_mb(self) -> float:
        """Get size in megabytes."""
        return self.size / (1024 * 1024)
    
    def __str__(self) -> str:
        return f"ArtifactReference(id={self.artifact_id}, type={self.content_type}, size={self.size})"