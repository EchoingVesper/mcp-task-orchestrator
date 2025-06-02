"""
Client detector for MCP Task Orchestrator.

This module provides functionality for detecting installed MCP clients
across different platforms.
"""

import json
import logging
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ClientDetector:
    """
    Client detector for MCP Task Orchestrator.
    
    This class provides methods for detecting installed MCP clients
    across different platforms.
    """
    
    @staticmethod
    def get_platform() -> str:
        """
        Get the current platform.
        
        Returns:
            str: The current platform (windows, macos, linux)
        """
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        return system
    
    @staticmethod
    def get_client_paths() -> Dict[str, Dict[str, Any]]:
        """
        Get the paths to client configuration files for the current platform.
        
        Returns:
            dict: Dictionary of client paths
        """
        platform_name = ClientDetector.get_platform()
        
        if platform_name == "windows":
            from .platforms import windows
            return windows.CLIENT_PATHS
        elif platform_name == "macos":
            from .platforms import macos
            return macos.CLIENT_PATHS
        elif platform_name == "linux":
            from .platforms import linux
            return linux.CLIENT_PATHS
        else:
            logger.warning(f"Unsupported platform: {platform_name}")
            return {}
    
    @staticmethod
    def detect_clients() -> Dict[str, Dict[str, Any]]:
        """
        Detect installed MCP clients on the current platform.
        
        Returns:
            dict: Dictionary of detected clients with their paths and status
        """
        platform_name = ClientDetector.get_platform()
        
        if platform_name == "windows":
            from .platforms import windows
            return windows.detect_clients()
        elif platform_name == "macos":
            from .platforms import macos
            return macos.detect_clients()
        elif platform_name == "linux":
            from .platforms import linux
            return linux.detect_clients()
        else:
            logger.warning(f"Unsupported platform: {platform_name}")
            return {}