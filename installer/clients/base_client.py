#!/usr/bin/env python3
"""Base client interface for MCP Task Orchestrator."""

from abc import ABC, abstractmethod
from pathlib import Path


class MCPClient(ABC):
    """Abstract base class for MCP client configurations."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.venv_python = project_root / "venv_mcp" / "Scripts" / "python.exe"
        self.server_config = {
            "command": str(self.venv_python),
            "args": ["-m", "mcp_task_orchestrator.server"],
            "cwd": str(project_root)
        }
    
    @property
    @abstractmethod
    def client_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def client_id(self) -> str:
        pass
    
    @abstractmethod
    def detect_installation(self) -> bool:
        pass
    
    @abstractmethod
    def get_config_path(self) -> Path:
        pass
    
    @abstractmethod
    def create_configuration(self) -> bool:
        pass


class MCPClientError(Exception):
    """Base exception for MCP client operations."""
    pass
