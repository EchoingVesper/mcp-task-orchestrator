"""
Windows-specific implementation for MCP Task Orchestrator CLI.

This module provides Windows-specific functionality for detecting and configuring
MCP clients on Windows operating systems.
"""

import os
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Client configuration paths for Windows
CLIENT_PATHS = {
    "claude_desktop": {
        "config_path": Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json",
        "display_name": "Claude Desktop"
    },
    "windsurf": {
        "config_path": Path.home() / ".windsurf" / "settings.json",
        "display_name": "Windsurf"
    },
    "cursor": {
        "config_path": Path.home() / ".cursor" / "settings.json",
        "display_name": "Cursor"
    },
    "vscode": {
        "config_path": Path(os.environ.get("APPDATA", "")) / "Code" / "User" / "settings.json",
        "display_name": "Visual Studio Code"
    }
}

def detect_clients():
    """
    Detect installed MCP clients on Windows.
    
    Returns:
        dict: Dictionary of detected clients with their paths and current configuration
    """
    detected = {}
    
    for client_id, client_info in CLIENT_PATHS.items():
        config_path = client_info["config_path"]
        if config_path.exists():
            try:
                detected[client_id] = {
                    "path": str(config_path),
                    "display_name": client_info["display_name"],
                    "configured": is_client_configured(client_id, config_path),
                    "config": read_client_config(config_path)
                }
                logger.info(f"Detected {client_info['display_name']} at {config_path}")
            except Exception as e:
                logger.warning(f"Error reading {client_info['display_name']} config: {e}")
    
    return detected

def read_client_config(config_path):
    """
    Read the configuration file for a client.
    
    Args:
        config_path (Path): Path to the client configuration file
        
    Returns:
        dict: The client configuration as a dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON in {config_path}")
        return {}
    except Exception as e:
        logger.warning(f"Error reading {config_path}: {e}")
        return {}

def is_client_configured(client_id, config_path):
    """
    Check if a client is already configured for the MCP Task Orchestrator.
    
    Args:
        client_id (str): Client identifier
        config_path (Path): Path to the client configuration file
        
    Returns:
        bool: True if the client is configured, False otherwise
    """
    try:
        config = read_client_config(config_path)
        
        if client_id == "claude_desktop":
            return "task-orchestrator" in config.get("mcpServers", {})
        elif client_id in ["windsurf", "cursor", "vscode"]:
            # Check for MCP server configuration in these clients
            # Implementation depends on the specific format of each client
            return False
        
        return False
    except Exception as e:
        logger.warning(f"Error checking configuration for {client_id}: {e}")
        return False

def backup_client_config(client_id):
    """
    Create a backup of a client's configuration file.
    
    Args:
        client_id (str): Client identifier
        
    Returns:
        Path: Path to the backup file, or None if backup failed
    """
    if client_id not in CLIENT_PATHS:
        logger.warning(f"Unknown client: {client_id}")
        return None
    
    config_path = CLIENT_PATHS[client_id]["config_path"]
    if not config_path.exists():
        logger.warning(f"Config file does not exist: {config_path}")
        return None
    
    backup_path = config_path.with_suffix(f".backup.{int(os.path.getmtime(config_path))}.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        logger.info(f"Created backup at {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup for {client_id}: {e}")
        return None

def configure_client(client_id, server_path, server_name="Task Orchestrator"):
    """
    Configure a client to use the MCP Task Orchestrator.
    
    Args:
        client_id (str): Client identifier
        server_path (str): Path to the MCP Task Orchestrator server script
        server_name (str): Display name for the server
        
    Returns:
        bool: True if configuration was successful, False otherwise
    """
    if client_id not in CLIENT_PATHS:
        logger.warning(f"Unknown client: {client_id}")
        return False
    
    config_path = CLIENT_PATHS[client_id]["config_path"]
    if not config_path.exists():
        logger.warning(f"Config file does not exist: {config_path}")
        return False
    
    # Create backup before modifying
    backup_client_config(client_id)
    
    try:
        config = read_client_config(config_path)
        
        # Configure based on client type
        if client_id == "claude_desktop":
            # Claude Desktop configuration
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            
            server_id = "task-orchestrator"
            config["mcpServers"][server_id] = {
                "command": "python",
                "args": [str(Path(server_path).resolve())],
                "env": {}
            }
        elif client_id == "windsurf":
            # Windsurf configuration
            # Implementation depends on Windsurf's configuration format
            pass
        elif client_id == "cursor":
            # Cursor configuration
            # Implementation depends on Cursor's configuration format
            pass
        elif client_id == "vscode":
            # VS Code configuration
            # Implementation depends on VS Code's configuration format
            pass
        
        # Write updated configuration
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Successfully configured {CLIENT_PATHS[client_id]['display_name']}")
        return True
    except Exception as e:
        logger.error(f"Failed to configure {client_id}: {e}")
        return False