"""
Abstract Specialist Repository interface.

This module defines the contract for specialist role persistence and
management operations that infrastructure implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class SpecialistRepository(ABC):
    """Abstract interface for specialist role persistence operations."""
    
    @abstractmethod
    def create_specialist(self, specialist_data: Dict[str, Any]) -> str:
        """
        Create a new specialist role.
        
        Args:
            specialist_data: Dictionary containing specialist information
            
        Returns:
            The ID of the created specialist
        """
        pass
    
    @abstractmethod
    def get_specialist(self, specialist_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specialist by ID.
        
        Args:
            specialist_id: The unique identifier of the specialist
            
        Returns:
            Specialist data as a dictionary, or None if not found
        """
        pass
    
    @abstractmethod
    def get_specialist_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specialist by name.
        
        Args:
            name: The name of the specialist role
            
        Returns:
            Specialist data as a dictionary, or None if not found
        """
        pass
    
    @abstractmethod
    def update_specialist(self, specialist_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing specialist.
        
        Args:
            specialist_id: The unique identifier of the specialist
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_specialist(self, specialist_id: str) -> bool:
        """
        Delete a specialist.
        
        Args:
            specialist_id: The unique identifier of the specialist
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_specialists(self, 
                        category: Optional[str] = None,
                        active_only: bool = True,
                        limit: Optional[int] = None,
                        offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List specialists with optional filtering.
        
        Args:
            category: Filter by category (e.g., 'architect', 'implementer')
            active_only: If True, only return active specialists
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of specialist dictionaries
        """
        pass
    
    @abstractmethod
    def get_specialist_categories(self) -> List[str]:
        """
        Get all unique specialist categories.
        
        Returns:
            List of category names
        """
        pass
    
    @abstractmethod
    def save_specialist_template(self, template_name: str, 
                               template_data: Dict[str, Any]) -> bool:
        """
        Save a specialist template for reuse.
        
        Args:
            template_name: Name of the template
            template_data: Template configuration
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_specialist_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specialist template by name.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template data, or None if not found
        """
        pass
    
    @abstractmethod
    def list_specialist_templates(self) -> List[Dict[str, Any]]:
        """
        List all available specialist templates.
        
        Returns:
            List of template dictionaries
        """
        pass
    
    @abstractmethod
    def record_specialist_usage(self, specialist_id: str, task_id: str,
                              usage_data: Dict[str, Any]) -> bool:
        """
        Record usage of a specialist for analytics.
        
        Args:
            specialist_id: The specialist used
            task_id: The task it was used for
            usage_data: Additional usage information
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_specialist_metrics(self, specialist_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage metrics for specialists.
        
        Args:
            specialist_id: Optional specific specialist to get metrics for
            
        Returns:
            Dictionary containing usage metrics
        """
        pass
    
    @abstractmethod
    def get_recommended_specialist(self, task_type: str, 
                                 task_context: Dict[str, Any]) -> Optional[str]:
        """
        Get a recommendation for which specialist to use.
        
        Args:
            task_type: Type of task
            task_context: Additional context about the task
            
        Returns:
            Recommended specialist ID, or None if no recommendation
        """
        pass