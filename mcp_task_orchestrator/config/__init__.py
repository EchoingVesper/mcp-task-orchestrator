"""
Configuration module for MCP Task Orchestrator.

This module provides configuration management functionality for the MCP Task Orchestrator,
including loading specialist templates and server settings.
"""

from pathlib import Path
import os

# Default configuration paths
DEFAULT_CONFIG_DIR = Path(__file__).parent
USER_CONFIG_DIR = Path.home() / ".mcp_task_orchestrator"

# Create user config directory if it doesn't exist
os.makedirs(USER_CONFIG_DIR, exist_ok=True)

def get_config_path(filename):
    """
    Get the path to a configuration file, checking user directory first,
    then falling back to the default configuration.
    
    Args:
        filename (str): Name of the configuration file
        
    Returns:
        Path: Path to the configuration file
    """
    user_path = USER_CONFIG_DIR / filename
    default_path = DEFAULT_CONFIG_DIR / filename
    
    if user_path.exists():
        return user_path
    return default_path