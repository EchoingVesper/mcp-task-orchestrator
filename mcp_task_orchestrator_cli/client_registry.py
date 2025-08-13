#!/usr/bin/env python3
"""
MCP Client Registry System
Loads client configurations from YAML registry file
"""

import os
import sys
import shutil
import yaml
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Import unified configuration system with fallback handling
try:
    from ..config import get_config
    _config_available = True
except ImportError:
    _config_available = False


@dataclass
class ClientConfig:
    """Configuration data for an MCP client."""
    name: str
    official_docs: str
    config_format: str
    config_paths: Dict[str, str]
    schema: Dict[str, Any]
    process_names: Dict[str, List[str]]
    workspace_support: bool = False
    notes: List[str] = None


class ClientRegistry:
    """Registry for MCP client configurations."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize the registry."""
        if registry_path is None:
            # Try multiple locations for the registry file
            possible_paths = [
                # When running from source
                Path(__file__).parent.parent / "config" / "mcp_clients_registry.yaml",
                # When installed via pip (relative to package)
                Path(__file__).parent / "config" / "mcp_clients_registry.yaml",
                # System config location
                Path("/usr/local/share/mcp-task-orchestrator/config/mcp_clients_registry.yaml"),
                # User config location
                Path.home() / ".config" / "mcp-task-orchestrator" / "mcp_clients_registry.yaml"
            ]
            
            registry_path = None
            for path in possible_paths:
                if path.exists():
                    registry_path = path
                    break
            
            if registry_path is None:
                raise FileNotFoundError(
                    "Could not find mcp_clients_registry.yaml in any of these locations:\n" +
                    "\n".join(f"  - {p}" for p in possible_paths)
                )
        
        self.registry_path = registry_path
        self.clients: Dict[str, ClientConfig] = {}
        self.task_orchestrator_config = {}
        self.platform_adjustments = {}
        
        self.load_registry()
    
    def load_registry(self):
        """Load the registry from YAML file."""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Load clients
            for client_id, client_data in data.get('clients', {}).items():
                self.clients[client_id] = ClientConfig(
                    name=client_data['name'],
                    official_docs=client_data['official_docs'],
                    config_format=client_data['config_format'],
                    config_paths=client_data['config_paths'],
                    schema=client_data['schema'],
                    process_names=client_data['process_names'],
                    workspace_support=client_data.get('workspace_support', False),
                    notes=client_data.get('notes', [])
                )
            
            # Load task orchestrator config
            self.task_orchestrator_config = data.get('task_orchestrator_config', {})
            
            # Load platform adjustments
            self.platform_adjustments = data.get('platform_adjustments', {})
            
        except Exception as e:
            raise RuntimeError(f"Failed to load client registry from {self.registry_path}: {e}")
    
    def get_client(self, client_id: str) -> Optional[ClientConfig]:
        """Get a specific client configuration."""
        return self.clients.get(client_id)
    
    def get_all_clients(self) -> Dict[str, ClientConfig]:
        """Get all client configurations."""
        return self.clients
    
    def expand_path(self, path_template: str) -> Path:
        """Expand a path template with platform-specific variables."""
        system = platform.system()
        
        # Handle platform-specific variables
        if system == "Windows":
            # Try unified configuration system first, then fall back to environment variables
            appdata_path = ""
            if _config_available:
                try:
                    config = get_config()
                    # Use system paths from configuration if available
                    appdata_path = getattr(config.paths, 'appdata_dir', None) or os.environ.get("APPDATA", "")
                except:
                    appdata_path = os.environ.get("APPDATA", "")
            else:
                appdata_path = os.environ.get("APPDATA", "")
            
            path = path_template.replace("%APPDATA%", appdata_path)
            path = path.replace("~", str(Path.home()))
        else:
            path = os.path.expanduser(path_template)
        
        return Path(path)
    
    def get_config_paths_for_client(self, client_id: str) -> List[Path]:
        """Get all possible config paths for a client on current platform."""
        client = self.get_client(client_id)
        if not client:
            return []
        
        paths = []
        system = platform.system().lower()
        
        # Add platform-specific paths
        for path_key, path_template in client.config_paths.items():
            if system in path_key or path_key in ['global', 'project', 'workspace']:
                paths.append(self.expand_path(path_template))
        
        return paths
    
    def get_task_orchestrator_config(self) -> Dict[str, Any]:
        """Get task orchestrator configuration."""
        config = self.task_orchestrator_config.copy()
        
        # Apply platform adjustments
        system = platform.system().lower()
        if system in self.platform_adjustments:
            adjustments = self.platform_adjustments[system]
            if 'python_executable' in adjustments:
                config['command_python'] = adjustments['python_executable']
        
        return config
    
    def get_python_command(self) -> str:
        """Get the appropriate Python command for the current platform."""
        system = platform.system().lower()
        
        if system in self.platform_adjustments:
            return self.platform_adjustments[system].get('python_executable', sys.executable)
        
        return sys.executable
    
    def create_server_config(self, client_id: str, python_path: Optional[str] = None) -> Dict[str, Any]:
        """Create server configuration for a specific client."""
        client = self.get_client(client_id)
        if not client:
            raise ValueError(f"Unknown client: {client_id}")
        
        task_config = self.get_task_orchestrator_config()
        python_cmd = python_path or self.get_python_command()
        
        # Base server configuration
        server_config = {
            "command": python_cmd,
            "args": task_config['command_args'],
            "env": task_config.get('env', {})
        }
        
        # Adjust for client-specific schema
        if client.schema.get('server_schema', {}).get('name'):
            # Continue.dev uses 'name' field
            server_config['name'] = task_config['name']
        
        return server_config
    
    def create_full_config(self, client_id: str, python_path: Optional[str] = None) -> Dict[str, Any]:
        """Create full configuration file content for a client using official MCP patterns."""
        client = self.get_client(client_id)
        if not client:
            raise ValueError(f"Unknown client: {client_id}")
        
        # Create server configuration following official MCP best practices
        task_config = self.get_task_orchestrator_config()
        python_cmd = python_path or self.get_python_command()
        
        # Ensure we use absolute path for Python command (MCP documentation requirement)
        if python_cmd and not os.path.isabs(python_cmd):
            python_cmd = shutil.which(python_cmd) or python_cmd
        
        server_config = {
            "command": python_cmd,
            "args": ["-m", "mcp_task_orchestrator.server"]  # Official MCP pattern
        }
        
        # Add environment variables following MCP documentation guidance
        # Only USER, HOME, PATH are automatically inherited - be explicit about others
        env_vars = {}
        
        # For MCP servers, minimal environment is better (per MCP documentation)
        # Only add environment variables if absolutely necessary
        
        # Check if we have a problematic mixed installation that needs PYTHONPATH
        needs_pythonpath = False
        try:
            import mcp_task_orchestrator
            import mcp
            
            orchestrator_path = mcp_task_orchestrator.__file__
            mcp_path = mcp.__file__
            
            # Check if one is in source directory and other in site-packages
            orchestrator_in_source = ("Programming" in orchestrator_path and 
                                    "mcp-task-orchestrator" in orchestrator_path)
            mcp_in_site_packages = "site-packages" in mcp_path
            
            needs_pythonpath = orchestrator_in_source and mcp_in_site_packages
            
        except ImportError:
            needs_pythonpath = True  # Assume problematic if we can't import
        
        # For most MCP clients (Cursor, Windsurf), prefer minimal environment
        # Claude Desktop seems to work better with more environment variables
        if client_id == 'claude_desktop':
            # Claude Desktop benefits from more complete environment
            if needs_pythonpath:
                try:
                    import mcp
                    site_packages_dir = str(Path(mcp.__file__).parent.parent)
                    env_vars["PYTHONPATH"] = site_packages_dir
                except ImportError:
                    pass
            
            # Add essential environment variables for Claude Desktop
            # Try unified configuration system first, then fall back to environment variables
            system_path = ""
            home_path = ""
            
            if _config_available:
                try:
                    config = get_config()
                    # Use system paths from configuration if available
                    system_path = getattr(config.paths, 'system_path', None) or os.environ.get("PATH", "")
                    home_path = getattr(config.paths, 'home_dir', None) or os.environ.get("HOME", os.environ.get("USERPROFILE", ""))
                except:
                    system_path = os.environ.get("PATH", "")
                    home_path = os.environ.get("HOME", os.environ.get("USERPROFILE", ""))
            else:
                system_path = os.environ.get("PATH", "")
                home_path = os.environ.get("HOME", os.environ.get("USERPROFILE", ""))
            
            env_vars.update({
                "PATH": system_path,
                "HOME": home_path
            })
        else:
            # For other clients (Windsurf, Cursor, etc.), use minimal environment
            # But always add PYTHONPATH if we detected a mixed installation
            if needs_pythonpath:
                try:
                    import mcp
                    site_packages_dir = str(Path(mcp.__file__).parent.parent)
                    env_vars["PYTHONPATH"] = site_packages_dir
                except ImportError:
                    pass
            
            # Add minimal PATH for Windows clients to find system libraries
            if client_id in ['cursor', 'windsurf'] and sys.platform == 'win32':
                # Include just the Python Scripts directory for DLL dependencies
                python_dir = Path(python_cmd).parent if python_cmd else None
                if python_dir and python_dir.exists():
                    scripts_dir = python_dir / "Scripts"
                    if scripts_dir.exists():
                        env_vars["PATH"] = str(scripts_dir)
        
        # Add any additional environment variables from the registry
        if 'env' in task_config:
            env_vars.update(task_config['env'])
        
        # Only add env section if we have meaningful variables to set
        if env_vars:
            server_config["env"] = env_vars
        
        root_key = client.schema['root_key']
        
        # Create the full configuration structure
        if client_id == 'continue_dev':
            # Special handling for Continue.dev YAML format
            return {
                root_key: [{
                    "name": "task-orchestrator",
                    **server_config
                }]  # Array format
            }
        else:
            # Standard JSON format
            return {
                root_key: {
                    "task-orchestrator": server_config
                }
            }


# Global registry instance
_registry = None

def get_registry() -> ClientRegistry:
    """Get the global client registry instance."""
    global _registry
    if _registry is None:
        _registry = ClientRegistry()
    return _registry