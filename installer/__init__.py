#!/usr/bin/env python3
"""
MCP Task Orchestrator Unified Installer Package

This package provides a unified installation system for configuring the MCP Task Orchestrator
across multiple supported MCP clients with automatic detection and configuration.

Supported Clients:
- Claude Desktop
- Cursor IDE  
- Windsurf
- VS Code (with Cline extension)

Usage:
    from installer import UnifiedInstaller
    
    installer = UnifiedInstaller()
    installer.run_installation()
"""

from .main_installer import UnifiedInstaller
from .client_detector import ClientDetector
from .clients import MCPClient, MCPClientError

__version__ = "1.0.0"
__all__ = [
    'UnifiedInstaller',
    'ClientDetector', 
    'MCPClient',
    'MCPClientError'
]
