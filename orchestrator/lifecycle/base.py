"""
Base enums and types for task lifecycle management.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple, Union

# Common logger for lifecycle operations
logger = logging.getLogger("mcp_task_orchestrator.lifecycle")


class TaskLifecycleState(Enum):
    """Enumeration of task lifecycle states."""
    CREATED = "created"
    ACTIVE = "active"
    COMPLETED = "completed"
    STALE = "stale"
    ARCHIVED = "archived"
    FAILED = "failed"


class StaleTaskReason(Enum):
    """Enumeration of reasons why a task might be considered stale."""
    INACTIVITY_TIMEOUT = "inactivity_timeout"
    ABANDONED_WORKFLOW = "abandoned_workflow"
    ORPHANED_TASK = "orphaned_task"
    DEPENDENCY_FAILURE = "dependency_failure"
    SPECIALIST_UNAVAILABLE = "specialist_unavailable"
    USER_ABANDONED = "user_abandoned"


class LifecycleConfig:
    """Configuration container for lifecycle management."""
    
    # Configuration for stale task detection
    STALE_DETECTION_CONFIG = {
        "default_threshold_hours": 24,
        "specialist_thresholds": {
            "researcher": 12,  # Research tasks should complete faster
            "documenter": 8,   # Documentation tasks are usually quicker
            "reviewer": 6,     # Review tasks should be timely
            "tester": 16,      # Testing might take longer
            "implementer": 48, # Implementation can be complex
            "architect": 72,   # Architecture decisions need time
            "debugger": 24     # Debugging varies but should have progress
        },
        "workflow_abandonment_threshold_hours": 168,  # 1 week for entire workflows
        "minimum_progress_threshold": 0.1  # 10% progress expected within threshold
    }
    
    # Archive retention policies
    ARCHIVE_RETENTION_CONFIG = {
        "completed_tasks": 90,      # 90 days for completed tasks
        "stale_tasks": 30,          # 30 days for stale tasks  
        "failed_tasks": 60,         # 60 days for failed tasks
        "orphaned_tasks": 7,        # 7 days for orphaned tasks
        "user_abandoned": 14        # 14 days for user-abandoned tasks
    }