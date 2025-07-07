"""
Progress tracking Data Transfer Objects.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ProgressStatusRequest:
    """Request for progress status."""
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    include_completed: bool = False
    include_subtasks: bool = True
    include_metrics: bool = True


@dataclass
class ProgressStatusResponse:
    """Response with progress status."""
    overall_status: str
    metrics: Dict[str, Any]
    session_info: Optional[Dict[str, Any]] = None
    task_info: Optional[Dict[str, Any]] = None
    sessions: List[Dict[str, Any]] = field(default_factory=list)
    active_tasks: List[Dict[str, Any]] = field(default_factory=list)
    pending_tasks: List[Dict[str, Any]] = field(default_factory=list)
    completed_tasks: List[Dict[str, Any]] = field(default_factory=list)
    failed_tasks: List[Dict[str, Any]] = field(default_factory=list)
    subtasks: List[Dict[str, Any]] = field(default_factory=list)