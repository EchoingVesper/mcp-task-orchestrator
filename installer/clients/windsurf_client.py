#!/usr/bin/env python3
"""Windsurf MCP client configuration."""

import os
import json
import psutil
from pathlib import Path
from .base_client import MCPClient, MCPClientError


class WindsurfClient(MCPClient):
    """Windsurf MCP client implementation."""
    
    @property
    def client_name(self) -> str:
        return "Windsurf"
    
    @property
    def client_id(self) -> str:
        return "windsurf"
    
    def detect_installation(self) -> bool:
        """Detect Windsurf installation."""
        # Check for running process
        for process in psutil.process_iter(['name']):
            try:
                if 'windsurf' in process.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Check for config directory
        config_dir = Path.home() / ".codeium" / "windsurf"
        return config_dir.exists()
    
    def get_config_path(self) -> Path:
        """Get Windsurf config file path."""
        return Path.home() / ".codeium" / "windsurf" / "mcp_config.json"

    def create_configuration(self) -> bool:
        """Create Windsurf configuration."""
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
        
        # Add our server configuration (Windsurf format)
        # Use the base class config which includes the universal launcher
        windsurf_config = self.server_config.copy()
        # Windsurf expects an env field
        windsurf_config["env"] = {}
        config["mcpServers"]["task-orchestrator"] = windsurf_config
        
        # Write configuration
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            raise MCPClientError(f"Failed to write config: {e}")
