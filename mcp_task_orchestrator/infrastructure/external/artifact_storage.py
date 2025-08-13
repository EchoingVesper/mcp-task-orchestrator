"""
Artifact storage implementations.
"""

from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging
import json


logger = logging.getLogger(__name__)


class FileSystemArtifactStorage:
    """
    File system based artifact storage.
    """
    
    def __init__(self, base_path: Union[str, Path]):
        """
        Initialize file system artifact storage.
        
        Args:
            base_path: Base directory for artifact storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    async def store_artifact(self, artifact_id: str, data: Dict[str, Any]) -> str:
        """
        Store an artifact.
        
        Args:
            artifact_id: Unique identifier for the artifact
            data: Artifact data to store
            
        Returns:
            Storage path or identifier
        """
        artifact_path = self.base_path / f"{artifact_id}.json"
        
        try:
            with open(artifact_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Stored artifact {artifact_id} at {artifact_path}")
            return str(artifact_path)
            
        except Exception as e:
            logger.error(f"Failed to store artifact {artifact_id}: {e}")
            raise
            
    async def retrieve_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an artifact.
        
        Args:
            artifact_id: Unique identifier for the artifact
            
        Returns:
            Artifact data or None if not found
        """
        artifact_path = self.base_path / f"{artifact_id}.json"
        
        try:
            if not artifact_path.exists():
                return None
                
            with open(artifact_path, 'r') as f:
                data = json.load(f)
                
            logger.info(f"Retrieved artifact {artifact_id} from {artifact_path}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve artifact {artifact_id}: {e}")
            return None
            
    async def delete_artifact(self, artifact_id: str) -> bool:
        """
        Delete an artifact.
        
        Args:
            artifact_id: Unique identifier for the artifact
            
        Returns:
            True if deleted, False if not found
        """
        artifact_path = self.base_path / f"{artifact_id}.json"
        
        try:
            if artifact_path.exists():
                artifact_path.unlink()
                logger.info(f"Deleted artifact {artifact_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete artifact {artifact_id}: {e}")
            return False