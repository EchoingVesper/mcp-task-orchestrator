"""
Artifact reference value objects.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum


class ArtifactType(str, Enum):
    """Types of artifacts that can be created."""
    CODE = "code"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    DESIGN = "design"
    TEST = "test"
    CONFIG = "config"
    DATA = "data"
    REPORT = "report"
    GENERAL = "general"
    
    @property
    def default_extension(self) -> str:
        """Get default file extension for artifact type."""
        extensions = {
            ArtifactType.CODE: ".py",
            ArtifactType.DOCUMENTATION: ".md",
            ArtifactType.ANALYSIS: ".md",
            ArtifactType.DESIGN: ".md",
            ArtifactType.TEST: ".py",
            ArtifactType.CONFIG: ".yaml",
            ArtifactType.DATA: ".json",
            ArtifactType.REPORT: ".md",
            ArtifactType.GENERAL: ".txt"
        }
        return extensions.get(self, ".txt")
    
    @property
    def subdirectory(self) -> str:
        """Get subdirectory name for organizing artifacts."""
        subdirs = {
            ArtifactType.CODE: "code",
            ArtifactType.DOCUMENTATION: "docs",
            ArtifactType.ANALYSIS: "analysis",
            ArtifactType.DESIGN: "design",
            ArtifactType.TEST: "tests",
            ArtifactType.CONFIG: "config",
            ArtifactType.DATA: "data",
            ArtifactType.REPORT: "reports",
            ArtifactType.GENERAL: "artifacts"
        }
        return subdirs.get(self, "artifacts")


@dataclass(frozen=True)
class ArtifactReference:
    """Value object representing a reference to an artifact."""
    artifact_id: str
    artifact_type: ArtifactType
    file_path: Path
    task_id: str
    size_bytes: int
    mime_type: Optional[str] = None
    
    def __post_init__(self):
        if not self.artifact_id:
            raise ValueError("Artifact ID cannot be empty")
        
        if not isinstance(self.file_path, Path):
            object.__setattr__(self, 'file_path', Path(self.file_path))
        
        if self.size_bytes < 0:
            raise ValueError("Size cannot be negative")
        
        if not self.task_id:
            raise ValueError("Task ID cannot be empty")
    
    @property
    def filename(self) -> str:
        """Get the filename without path."""
        return self.file_path.name
    
    @property
    def extension(self) -> str:
        """Get file extension."""
        return self.file_path.suffix
    
    @property
    def size_kb(self) -> float:
        """Get size in kilobytes."""
        return self.size_bytes / 1024
    
    @property
    def size_mb(self) -> float:
        """Get size in megabytes."""
        return self.size_bytes / (1024 * 1024)
    
    @property
    def size_formatted(self) -> str:
        """Get human-readable size."""
        if self.size_bytes < 1024:
            return f"{self.size_bytes} B"
        elif self.size_bytes < 1024 * 1024:
            return f"{self.size_kb:.1f} KB"
        else:
            return f"{self.size_mb:.1f} MB"
    
    def exists(self) -> bool:
        """Check if the artifact file exists."""
        return self.file_path.exists()
    
    def is_text(self) -> bool:
        """Check if artifact is likely a text file."""
        text_extensions = {'.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml', 
                          '.xml', '.html', '.css', '.csv', '.log'}
        return self.extension.lower() in text_extensions


@dataclass(frozen=True)
class ArtifactMetadata:
    """Extended metadata for an artifact."""
    created_by: str
    created_at: str  # ISO format timestamp
    description: str
    tags: tuple  # Immutable list of tags
    original_files: tuple  # Immutable list of original file paths
    
    def __post_init__(self):
        if not self.created_by:
            raise ValueError("Creator cannot be empty")
        
        if not self.description:
            raise ValueError("Description cannot be empty")
        
        # Ensure tags and original_files are tuples
        if not isinstance(self.tags, tuple):
            object.__setattr__(self, 'tags', tuple(self.tags))
        
        if not isinstance(self.original_files, tuple):
            object.__setattr__(self, 'original_files', tuple(self.original_files))
    
    def has_tag(self, tag: str) -> bool:
        """Check if artifact has a specific tag."""
        return tag in self.tags
    
    def with_tag(self, tag: str) -> 'ArtifactMetadata':
        """Create new metadata with additional tag."""
        if tag in self.tags:
            return self
        
        return ArtifactMetadata(
            created_by=self.created_by,
            created_at=self.created_at,
            description=self.description,
            tags=self.tags + (tag,),
            original_files=self.original_files
        )