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

# Add the main_sync function for CLI entry point
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def main_sync():
    """Entry point wrapper that runs the server."""
    import asyncio
    
    # Import the server functions from the parent module
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, parent_dir)
    
    # Import server functions by reading and modifying the code
    server_file = os.path.join(parent_dir, 'server.py')
    with open(server_file, 'r') as f:
        server_code = f.read()
    
    # Replace relative imports with absolute imports
    import re
    server_code = re.sub(r'from \.([a-zA-Z_][a-zA-Z0-9_\.]*)', r'from mcp_task_orchestrator.\1', server_code)
    
    try:
        # Execute the modified server code
        namespace = {
            '__name__': '__main__', 
            '__file__': server_file,
            '__package__': 'mcp_task_orchestrator'
        }
        exec(server_code, namespace)
    except SystemExit:
        pass

async def main():
    """Async main function."""
    # This should not be called directly, use main_sync instead
    raise NotImplementedError("Use main_sync() for the console entry point")

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
    'initialize_reboot_system',
    
    # Server entry points
    'main_sync',
    'main'
]