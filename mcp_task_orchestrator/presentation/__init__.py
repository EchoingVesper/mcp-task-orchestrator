"""
Presentation layer for MCP Task Orchestrator.

This layer contains all entry points and user interfaces for the system:
- MCP server setup and configuration
- Command-line interfaces
- API endpoints (if any)

The presentation layer coordinates application use cases but contains
no business logic itself.
"""

from .mcp_server import MCPServerEntryPoint
from .cli import CLIInterface

__all__ = [
    'MCPServerEntryPoint',
    'CLIInterface'
]