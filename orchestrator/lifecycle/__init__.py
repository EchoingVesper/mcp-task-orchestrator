"""
Task Lifecycle Management Package

This package provides modular task lifecycle management components split from the
original large task_lifecycle.py file for Claude Code safety and maintainability.
"""

from .base import TaskLifecycleState, StaleTaskReason
from .manager import TaskLifecycleManager

__all__ = [
    'TaskLifecycleState',
    'StaleTaskReason', 
    'TaskLifecycleManager'
]