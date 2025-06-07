"""
Server reboot functionality for MCP Task Orchestrator.

This package provides graceful shutdown, state serialization, and restart
coordination capabilities for seamless server updates.
"""

from .state_serializer import (
    StateSerializer,
    ServerStateSnapshot,
    RestartReason,
    ClientSession,
    DatabaseState
)

from .shutdown_coordinator import (
    ShutdownCoordinator,
    ShutdownManager,
    ShutdownPhase,
    ShutdownStatus
)

__all__ = [
    'StateSerializer',
    'ServerStateSnapshot', 
    'RestartReason',
    'ClientSession',
    'DatabaseState',
    'ShutdownCoordinator',
    'ShutdownManager',
    'ShutdownPhase',
    'ShutdownStatus'
]