#!/usr/bin/env python3
"""Base client interface for MCP Task Orchestrator."""

from abc import ABC, abstractmethod
from pathlib import Path
import platform


class MCPClient(ABC):
    """Abstract base class for MCP client configurations."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.venv_python = self._find_venv_python()
        self.platform_system = platform.system()
        
        # Use universal launcher if available
        launcher_py = project_root / "launch_orchestrator.py"
        if launcher_py.exists():
            # Use the universal Python launcher
            python_cmd = self._get_system_python()
            self.server_config = {
                "command": python_cmd,
                "args": [str(launcher_py)],
                "cwd": str(project_root)
            }
        elif self.venv_python:
            # For Claude Code on WSL/Linux, we need to use the absolute path
            # without trying to execute it as a single command string
            self.server_config = {
                "command": str(self.venv_python),
                "args": ["-m", "mcp_task_orchestrator.server"],
                "cwd": str(project_root),
                "env": {}
            }
        else:
            # Last resort - use system Python with module
            python_cmd = self._get_system_python()
            self.server_config = {
                "command": python_cmd,
                "args": ["-m", "mcp_task_orchestrator.server"],
                "cwd": str(project_root),
                "env": {}
            }
    
    def _find_venv_python(self) -> Path:
        """Find the Python executable in the virtual environment."""
        venv_names = ['venv_mcp', 'venv', '.venv']
        
        for venv_name in venv_names:
            venv_path = self.project_root / venv_name
            
            if not venv_path.exists():
                continue
                
            # Check for Windows-style Scripts directory
            windows_python = venv_path / 'Scripts' / 'python.exe'
            if windows_python.exists():
                return windows_python
                
            # Check for Unix-style bin directory
            unix_python = venv_path / 'bin' / 'python'
            if unix_python.exists():
                return unix_python
                
            # Check for Unix-style with python3
            unix_python3 = venv_path / 'bin' / 'python3'
            if unix_python3.exists():
                return unix_python3
        
        return None
    
    def _get_system_python(self) -> str:
        """Get the appropriate system Python command."""
        if platform.system() == "Windows":
            return "python"
        else:
            return "python3"
    
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
