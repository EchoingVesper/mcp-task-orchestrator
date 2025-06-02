"""
Platform-specific implementations for MCP Task Orchestrator CLI.

This module provides platform-specific implementations for detecting and configuring
MCP clients on different operating systems.
"""

import platform
import sys

def get_platform_module():
    """
    Get the appropriate platform-specific module based on the current operating system.
    
    Returns:
        module: The platform-specific module for the current OS
    """
    system = platform.system().lower()
    
    if system == 'windows':
        from . import windows
        return windows
    elif system == 'darwin':
        from . import macos
        return macos
    elif system == 'linux':
        from . import linux
        return linux
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")