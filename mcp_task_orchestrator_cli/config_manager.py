"""
Configuration manager for MCP Task Orchestrator.

This module provides functionality for managing configuration files for
different MCP clients across platforms.
"""

import json
import logging
import os
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .platforms import get_platform_module

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Configuration manager for MCP Task Orchestrator.
    
    This class provides methods for detecting and configuring MCP clients
    across different platforms.
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.platform_module = get_platform_module()
    
    def detect_clients(self) -> Dict[str, Dict[str, Any]]:
        """
        Detect installed MCP clients on the current platform.
        
        Returns:
            dict: Dictionary of detected clients with their paths and current configuration
        """
        return self.platform_module.detect_clients()
    
    def configure_client(self, client_id: str, server_path: str, server_name: str = "Task Orchestrator") -> bool:
        """
        Configure a client to use the MCP Task Orchestrator.
        
        Args:
            client_id (str): Client identifier
            server_path (str): Path to the MCP Task Orchestrator server script
            server_name (str): Display name for the server
            
        Returns:
            bool: True if configuration was successful, False otherwise
        """
        return self.platform_module.configure_client(client_id, server_path, server_name)
    
    def backup_client_config(self, client_id: str) -> Optional[Path]:
        """
        Create a backup of a client's configuration file.
        
        Args:
            client_id (str): Client identifier
            
        Returns:
            Path: Path to the backup file, or None if backup failed
        """
        return self.platform_module.backup_client_config(client_id)
    
    def is_client_configured(self, client_id: str) -> bool:
        """
        Check if a client is already configured for the MCP Task Orchestrator.
        
        Args:
            client_id (str): Client identifier
            
        Returns:
            bool: True if the client is configured, False otherwise
        """
        if client_id not in self.platform_module.CLIENT_PATHS:
            logger.warning(f"Unknown client: {client_id}")
            return False
        
        config_path = self.platform_module.CLIENT_PATHS[client_id]["config_path"]
        if not config_path.exists():
            logger.warning(f"Config file does not exist: {config_path}")
            return False
        
        return self.platform_module.is_client_configured(client_id, config_path)