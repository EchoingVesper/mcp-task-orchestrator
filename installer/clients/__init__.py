#!/usr/bin/env python3
"""
MCP Client implementations for various IDEs and AI tools.
"""

from .base_client import MCPClient, MCPClientError
from .claude_client import ClaudeDesktopClient
from .cursor_client import CursorIDEClient
from .windsurf_client import WindsurfClient
from .vscode_client import VSCodeClient

__all__ = [
    'MCPClient',
    'MCPClientError',
    'ClaudeDesktopClient',
    'CursorIDEClient', 
    'WindsurfClient',
    'VSCodeClient'
]

# Registry of available clients
AVAILABLE_CLIENTS = {
    'claude-desktop': ClaudeDesktopClient,
    'cursor-ide': CursorIDEClient,
    'windsurf': WindsurfClient,
    'vscode-cline': VSCodeClient
}


def get_all_clients(project_root):
    """Get instances of all available MCP clients."""
    return [client_class(project_root) for client_class in AVAILABLE_CLIENTS.values()]


def get_client(client_id: str, project_root):
    """Get a specific client by ID."""
    if client_id not in AVAILABLE_CLIENTS:
        raise ValueError(f"Unknown client ID: {client_id}")
    
    return AVAILABLE_CLIENTS[client_id](project_root)
