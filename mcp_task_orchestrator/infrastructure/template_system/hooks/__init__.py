"""
Template System Hooks - Intelligent automation framework for templates.

This module provides the hook system that enables templates to automatically
spawn agents, coordinate workflows, and manage execution lifecycles.
"""

from .base import (
    Hook,
    HookType,
    HookContext,
    HookResult,
    HookExecutionError
)

from .executor import (
    HookExecutor,
    DependencyGraph,
    ExecutionPlan
)

from .context import (
    ContextManager,
    ContextBuilder,
    ExecutionContext
)

from .builtin_hooks import (
    GitBranchHook,
    WorkspaceSetupHook,
    AgentSpawningHook,
    DocumentAssociationHook,
    CheckpointHook,
    ValidationHook,
    CommitHook,
    NotificationHook
)

from .registry import (
    HookRegistry,
    register_hook,
    get_hook,
    list_hooks
)

__all__ = [
    # Base classes
    'Hook',
    'HookType',
    'HookContext',
    'HookResult', 
    'HookExecutionError',
    
    # Execution framework
    'HookExecutor',
    'DependencyGraph',
    'ExecutionPlan',
    
    # Context management
    'ContextManager',
    'ContextBuilder',
    'ExecutionContext',
    
    # Built-in hooks
    'GitBranchHook',
    'WorkspaceSetupHook', 
    'AgentSpawningHook',
    'DocumentAssociationHook',
    'CheckpointHook',
    'ValidationHook',
    'CommitHook',
    'NotificationHook',
    
    # Registry functions
    'HookRegistry',
    'register_hook',
    'get_hook',
    'list_hooks'
]