#!/usr/bin/env python3
"""Claude Desktop MCP client configuration."""

import os
import json
import psutil
import platform
from pathlib import Path
from .base_client import MCPClient, MCPClientError


class ClaudeDesktopClient(MCPClient):
    """Claude Desktop MCP client implementation."""
    
    @property
    def client_name(self) -> str:
        return "Claude Desktop"
    
    @property
    def client_id(self) -> str:
        return "claude-desktop"
    
    def detect_installation(self) -> bool:
        """Detect Claude Desktop/Code installation."""
        # Check for Claude Code config file
        config_path = Path.home() / ".claude.json"
        if config_path.exists():
            return True
            
        # Check for running process
        for process in psutil.process_iter(['name']):
            try:
                if 'claude' in process.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Check for config directory (legacy)
        config_dir = self._get_config_dir()
        return config_dir.exists()
    
    def _get_config_dir(self) -> Path:
        """Get Claude Desktop config directory based on platform."""
        system = platform.system()
        if system == "Windows":
            return Path(os.environ.get("APPDATA", "")) / "Claude"
        elif system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Claude"
        else:  # Linux
            return Path.home() / ".config" / "Claude"
    
    def get_config_path(self) -> Path:
        """Get Claude Desktop/Code config file path."""
        # Claude Code uses ~/.claude.json
        return Path.home() / ".claude.json"

    def create_configuration(self) -> bool:
        """Create Claude Desktop configuration."""
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
        
        # Claude Code specific config structure
        if "experimental" not in config:
            config["experimental"] = {}
        if "codebaseContext" not in config["experimental"]:
            config["experimental"]["codebaseContext"] = {
                "enabled": True,
                "includeDocumentation": True,
                "includeTests": True
            }
        if "mcpServers" not in config["experimental"]:
            config["experimental"]["mcpServers"] = {}
        
        # Add our server configuration with proper structure
        server_config = {
            "type": "stdio",
            "command": self.server_config["command"],
            "args": self.server_config.get("args", []),
            "env": self.server_config.get("env", {})
        }
        
        config["experimental"]["mcpServers"]["task-orchestrator"] = server_config
        
        # Write configuration
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            raise MCPClientError(f"Failed to write config: {e}")
