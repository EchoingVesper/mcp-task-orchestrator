"""
Server reboot functionality for MCP Task Orchestrator.

This package provides graceful shutdown, state serialization, restart
coordination, and client connection management for seamless server updates.
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

from .restart_manager import (
    RestartCoordinator,
    ProcessManager,
    StateRestorer,
    RestartPhase,
    RestartStatus
)

from .connection_manager import (
    ConnectionManager,
    ConnectionInfo,
    ConnectionState,
    RequestBuffer,
    ReconnectionManager
)

from .reboot_integration import (
    RebootManager,
    get_reboot_manager,
    initialize_reboot_system
)

# Server package initialization - no entry points here
# Entry points are handled by __main__.py to avoid import conflicts

__all__ = [
    # State serialization
    'StateSerializer',
    'ServerStateSnapshot', 
    'RestartReason',
    'ClientSession',
    'DatabaseState',
    
    # Shutdown coordination
    'ShutdownCoordinator',
    'ShutdownManager',
    'ShutdownPhase',
    'ShutdownStatus',
    
    # Restart management
    'RestartCoordinator',
    'ProcessManager',
    'StateRestorer',
    'RestartPhase',
    'RestartStatus',
    
    # Connection management
    'ConnectionManager',
    'ConnectionInfo',
    'ConnectionState',
    'RequestBuffer',
    'ReconnectionManager',
    
    # Integration
    'RebootManager',
    'get_reboot_manager',
    'initialize_reboot_system'
]