"""
Notification service interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class NotificationService(ABC):
    """
    Interface for sending notifications about task events.
    
    This is an application-level service that can be implemented
    by infrastructure components.
    """
    
    @abstractmethod
    async def notify_task_started(self, task_id: str, metadata: Dict[str, Any]) -> None:
        """Send notification when a task starts."""
        pass
    
    @abstractmethod
    async def notify_task_completed(
        self,
        task_id: str,
        result: str,
        artifacts: list[str],
        metadata: Dict[str, Any]
    ) -> None:
        """Send notification when a task completes."""
        pass
    
    @abstractmethod
    async def notify_task_failed(
        self,
        task_id: str,
        error: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Send notification when a task fails."""
        pass
    
    @abstractmethod
    async def notify_session_completed(
        self,
        session_id: str,
        summary: Dict[str, Any]
    ) -> None:
        """Send notification when an orchestration session completes."""
        pass