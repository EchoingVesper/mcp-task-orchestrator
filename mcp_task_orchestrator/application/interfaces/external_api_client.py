"""
External API client interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ExternalApiClient(ABC):
    """
    Interface for communicating with external APIs.
    
    This allows the application layer to interact with external
    services without knowing implementation details.
    """
    
    @abstractmethod
    async def call_llm_api(
        self,
        prompt: str,
        model: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Call an LLM API with a prompt."""
        pass
    
    @abstractmethod
    async def store_artifact(
        self,
        content: str,
        artifact_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Store an artifact and return its ID."""
        pass
    
    @abstractmethod
    async def retrieve_artifact(self, artifact_id: str) -> str:
        """Retrieve an artifact by ID."""
        pass
    
    @abstractmethod
    async def webhook_callback(
        self,
        endpoint: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> None:
        """Send a webhook callback to an external endpoint."""
        pass