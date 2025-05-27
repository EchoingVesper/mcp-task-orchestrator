#!/usr/bin/env python3
"""Cursor IDE MCP client configuration."""

import os
import json
import psutil
from pathlib import Path
from .base_client import MCPClient, MCPClientError


class CursorIDEClient(MCPClient):
    """Cursor IDE MCP client implementation."""
    
    @property
    def client_name(self) -> str:
        return "Cursor IDE"
    
    @property
    def client_id(self) -> str:
        return "cursor-ide"
    
    def detect_installation(self) -> bool:
        """Detect Cursor IDE installation."""
        # Check for running process
        for process in psutil.process_iter(['name']):
            try:
                if 'cursor' in process.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Check for common installation paths
        common_paths = [
            Path.home() / ".cursor",
            Path("C:/Users") / os.getenv("USERNAME", "") / "AppData/Local/Programs/cursor"
        ]
        
        return any(path.exists() for path in common_paths)
    
    def get_config_path(self) -> Path:
        """Get Cursor IDE config file path (global)."""
        return Path.home() / ".cursor" / "mcp.json"

    def create_configuration(self) -> bool:
        """Create Cursor IDE configuration."""
        config_path = self.get_config_path()
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing config or create new
        config = {}
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                config = {}
        
        # Ensure mcpServers exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Add our server configuration (Cursor format)
        cursor_config = {
            "command": str(self.venv_python),
            "args": ["-m", "mcp_task_orchestrator.server"],
            "env": {}
        }
        config["mcpServers"]["task-orchestrator"] = cursor_config
        
        # Write configuration
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            raise MCPClientError(f"Failed to write config: {e}")
