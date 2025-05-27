#!/usr/bin/env python3
"""VS Code (Cline) MCP client configuration."""

import os
import json
import psutil
from pathlib import Path
from .base_client import MCPClient, MCPClientError


class VSCodeClient(MCPClient):
    """VS Code (Cline extension) MCP client implementation."""
    
    @property
    def client_name(self) -> str:
        return "VS Code (Cline)"
    
    @property
    def client_id(self) -> str:
        return "vscode-cline"
    
    def detect_installation(self) -> bool:
        """Detect VS Code installation."""
        # Check for running process
        for process in psutil.process_iter(['name']):
            try:
                name = process.info['name'].lower()
                if 'code' in name or 'vscode' in name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Check for common installation paths
        common_paths = [
            Path("C:/Program Files/Microsoft VS Code"),
            Path("C:/Program Files (x86)/Microsoft VS Code"),
            Path.home() / ".vscode"
        ]
        
        return any(path.exists() for path in common_paths)
    
    def get_config_path(self) -> Path:
        """Get VS Code Cline config file path (global)."""
        return Path.home() / ".vscode" / "mcp.json"

    def create_configuration(self) -> bool:
        """Create VS Code Cline configuration."""
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
        
        # Add our server configuration (VS Code format)
        vscode_config = {
            "command": str(self.venv_python),
            "args": ["-m", "mcp_task_orchestrator.server"]
        }
        config["mcpServers"]["task-orchestrator"] = vscode_config
        
        # Write configuration
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            raise MCPClientError(f"Failed to write config: {e}")
