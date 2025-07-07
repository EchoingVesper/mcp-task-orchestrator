"""
Abstract State Repository interface.

This module defines the contract for orchestration state persistence 
operations that infrastructure implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime


class StateRepository(ABC):
    """Abstract interface for orchestration state persistence operations."""
    
    @abstractmethod
    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """
        Save or update a session.
        
        Args:
            session_id: Unique identifier for the session
            session_data: Session data to persist
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: The unique identifier of the session
            
        Returns:
            Session data as a dictionary, or None if not found
        """
        pass
    
    @abstractmethod
    def list_sessions(self, 
                     active_only: bool = False,
                     limit: Optional[int] = None,
                     offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all sessions with optional filtering.
        
        Args:
            active_only: If True, only return active sessions
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of session dictionaries
        """
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all associated data.
        
        Args:
            session_id: The unique identifier of the session
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def save_context(self, session_id: str, context_key: str, 
                    context_data: Dict[str, Any]) -> bool:
        """
        Save context data for a session.
        
        Args:
            session_id: The session this context belongs to
            context_key: Unique key for this context
            context_data: The context data to save
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_context(self, session_id: str, context_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve context data for a session.
        
        Args:
            session_id: The session ID
            context_key: The context key
            
        Returns:
            Context data as a dictionary, or None if not found
        """
        pass
    
    @abstractmethod
    def list_contexts(self, session_id: str) -> List[str]:
        """
        List all context keys for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            List of context keys
        """
        pass
    
    @abstractmethod
    def save_workflow_state(self, session_id: str, workflow_data: Dict[str, Any]) -> bool:
        """
        Save the current workflow state for a session.
        
        Args:
            session_id: The session ID
            workflow_data: Current workflow state
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_workflow_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current workflow state for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Workflow state data, or None if not found
        """
        pass
    
    @abstractmethod
    def record_event(self, session_id: str, event_type: str, 
                    event_data: Dict[str, Any]) -> bool:
        """
        Record an event in the session history.
        
        Args:
            session_id: The session ID
            event_type: Type of event
            event_data: Event details
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_session_events(self, session_id: str, 
                          event_type: Optional[str] = None,
                          limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get events for a session.
        
        Args:
            session_id: The session ID
            event_type: Optional filter by event type
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        pass
    
    @abstractmethod
    def cleanup_old_sessions(self, older_than: datetime, 
                           keep_active: bool = True) -> int:
        """
        Clean up old sessions.
        
        Args:
            older_than: Delete sessions last updated before this date
            keep_active: If True, don't delete active sessions
            
        Returns:
            Number of sessions deleted
        """
        pass
    
    @abstractmethod
    def get_session_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about sessions.
        
        Returns:
            Dictionary containing metrics like active count, total count, etc.
        """
        pass