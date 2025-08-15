"""
Specialist-specific exceptions for role management and assignment errors.
"""

from typing import Optional, List, Dict, Any
from .orchestration_errors import OrchestrationError


class SpecialistError(OrchestrationError):
    """Base exception for all specialist-related errors."""
    pass


class SpecialistConfigurationError(SpecialistError):
    """Raised when specialist configuration is invalid."""
    
    def __init__(self, specialist_type: str, config_issue: str):
        super().__init__(
            f"Specialist configuration error for '{specialist_type}': {config_issue}",
            {
                "specialist_type": specialist_type,
                "config_issue": config_issue
            }
        )
        self.specialist_type = specialist_type
        self.config_issue = config_issue


class SpecialistCapabilityError(SpecialistError):
    """Raised when a specialist lacks required capabilities for a task."""
    
    def __init__(self, specialist_type: str, required_capabilities: List[str], 
                 available_capabilities: List[str]):
        super().__init__(
            f"Specialist '{specialist_type}' lacks required capabilities",
            {
                "specialist_type": specialist_type,
                "required_capabilities": required_capabilities,
                "available_capabilities": available_capabilities,
                "missing_capabilities": list(set(required_capabilities) - set(available_capabilities))
            }
        )
        self.specialist_type = specialist_type
        self.required_capabilities = required_capabilities
        self.available_capabilities = available_capabilities


class SpecialistLoadError(SpecialistError):
    """Raised when a specialist cannot be loaded or initialized."""
    
    def __init__(self, specialist_type: str, load_error: str):
        super().__init__(
            f"Failed to load specialist '{specialist_type}': {load_error}",
            {
                "specialist_type": specialist_type,
                "load_error": load_error
            }
        )
        self.specialist_type = specialist_type
        self.load_error = load_error


class SpecialistRoleConflictError(SpecialistError):
    """Raised when specialists have conflicting role assignments."""
    
    def __init__(self, task_id: str, conflicting_specialists: List[str]):
        super().__init__(
            f"Role conflict for task {task_id} between specialists: {', '.join(conflicting_specialists)}",
            {
                "task_id": task_id,
                "conflicting_specialists": conflicting_specialists
            }
        )
        self.task_id = task_id
        self.conflicting_specialists = conflicting_specialists


class SpecialistContextError(SpecialistError):
    """Raised when specialist context generation fails."""
    
    def __init__(self, specialist_type: str, context_error: str):
        super().__init__(
            f"Context generation failed for specialist '{specialist_type}': {context_error}",
            {
                "specialist_type": specialist_type,
                "context_error": context_error
            }
        )
        self.specialist_type = specialist_type
        self.context_error = context_error


class SpecialistUnavailableError(SpecialistError):
    """Raised when a specialist is temporarily unavailable."""
    
    def __init__(self, specialist_type: str, reason: str, retry_after: Optional[int] = None):
        super().__init__(
            f"Specialist '{specialist_type}' is unavailable: {reason}",
            {
                "specialist_type": specialist_type,
                "reason": reason,
                "retry_after": retry_after
            }
        )
        self.specialist_type = specialist_type
        self.reason = reason
        self.retry_after = retry_after


class SpecialistOverloadError(SpecialistError):
    """Raised when a specialist is overloaded with tasks."""
    
    def __init__(self, specialist_type: str, current_load: int, max_load: int):
        super().__init__(
            f"Specialist '{specialist_type}' is overloaded: {current_load}/{max_load} tasks",
            {
                "specialist_type": specialist_type,
                "current_load": current_load,
                "max_load": max_load
            }
        )
        self.specialist_type = specialist_type
        self.current_load = current_load
        self.max_load = max_load