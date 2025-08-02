"""
MCP client configuration management for the Universal Installer.

This module handles automatic detection and configuration of MCP clients
including Claude Desktop, Cursor, VS Code, and others.
"""

import os
import sys
import json
import shutil
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

from .models import (
    InstallerConfig,
    ClientConfigurationError,
    InstallationError,
    InstallationScope,
    InstallationSource
)

logger = logging.getLogger(__name__)


class ClientManager:
    """Manages MCP client detection and configuration."""
    
    def __init__(self, config: InstallerConfig, console=None):
        self.config = config
        self.console = console
        self._detected_clients: Optional[Dict[str, Any]] = None
    
    def configure_clients(self) -> None:
        """Configure MCP clients with backup and validation."""
        if self.config.dry_run:
            self._show_dry_run_configuration()
            return
        
        # Detect available clients
        detected_clients = self.detect_mcp_clients()
        
        if not detected_clients:
            self.console.print("[yellow]No MCP clients detected, skipping configuration[/yellow]")
            return
        
        # Filter clients if specific ones requested
        target_clients = self._filter_target_clients(detected_clients)
        
        if not target_clients:
            self.console.print("[yellow]No matching clients found for configuration[/yellow]")
            return
        
        # Configure each client with backup
        configured_count = 0
        for client_id, client_info in target_clients.items():
            try:
                self._configure_single_client(client_id, client_info)
                configured_count += 1
                self.console.print(f"[green]✓ Configured {client_info['display_name']}[/green]")
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to configure {client_info['display_name']}: {e}[/yellow]")
                logger.warning(f"Client configuration failed for {client_id}: {e}")
        
        if configured_count > 0:
            self.console.print(f"[green]Successfully configured {configured_count} MCP client(s)[/green]")
        else:
            self.console.print("[yellow]No clients were configured[/yellow]")
    
    def remove_mcp_configuration(self) -> None:
        """Remove MCP configuration from all clients."""
        if self.config.dry_run:
            self.console.print("[dim]Dry run: Would remove MCP configuration from all clients[/dim]")
            return
        
        detected_clients = self.detect_mcp_clients()
        
        for client_id, client_info in detected_clients.items():
            try:
                self._remove_client_configuration(client_id, client_info)
                self.console.print(f"[yellow]Removed configuration from {client_info['display_name']}[/yellow]")
            except Exception as e:
                logger.warning(f"Failed to remove configuration from {client_id}: {e}")
    
    def detect_mcp_clients(self) -> Dict[str, Dict[str, Any]]:
        """Detect available MCP clients on the system."""
        if self._detected_clients is not None:
            return self._detected_clients
        
        clients = {}
        
        # Detect platform-specific clients
        if os.name == 'nt':  # Windows
            clients.update(self._detect_windows_clients())
        else:  # Unix-like (Linux, macOS)
            clients.update(self._detect_unix_clients())
        
        # Filter out clients that aren't actually installed
        available_clients = {}
        for client_id, client_info in clients.items():
            if self._is_client_available(client_info):
                available_clients[client_id] = client_info
        
        self._detected_clients = available_clients
        
        if self.config.verbose:
            if available_clients:
                client_names = [info['display_name'] for info in available_clients.values()]
                self.console.print(f"[green]Detected clients: {', '.join(client_names)}[/green]")
            else:
                self.console.print("[yellow]No MCP clients detected[/yellow]")
        
        return available_clients
    
    def _detect_windows_clients(self) -> Dict[str, Dict[str, Any]]:
        """Detect MCP clients on Windows."""
        clients = {}
        
        # Claude Desktop - Fixed path
        claude_config_paths = [
            Path(os.environ.get('APPDATA', '')) / 'Claude' / 'claude_desktop_config.json',
            Path.home() / 'AppData' / 'Roaming' / 'Claude' / 'claude_desktop_config.json'
        ]
        
        for config_path in claude_config_paths:
            if config_path.parent.exists():  # Directory exists even if file doesn't
                clients['claude_desktop'] = {
                    'display_name': 'Claude Desktop',
                    'config_path': config_path,
                    'type': 'json_config',
                    'server_key': 'mcpServers'
                }
                break
        
        # Cursor - Fixed path
        cursor_paths = [
            Path.home() / '.cursor' / 'mcp.json',
            Path(os.environ.get('APPDATA', '')) / 'Cursor' / 'User' / 'mcp.json',
            Path.home() / 'AppData' / 'Roaming' / 'Cursor' / 'User' / 'mcp.json'
        ]
        
        for config_path in cursor_paths:
            if config_path.parent.exists():  # Directory exists even if file doesn't
                clients['cursor'] = {
                    'display_name': 'Cursor IDE',
                    'config_path': config_path,
                    'type': 'json_config',
                    'server_key': 'mcpServers'
                }
                break
        
        # VS Code - Fixed path  
        vscode_paths = [
            Path(os.environ.get('APPDATA', '')) / 'Code' / 'User' / 'mcp.json',
            Path.home() / 'AppData' / 'Roaming' / 'Code' / 'User' / 'mcp.json'
        ]
        
        for config_path in vscode_paths:
            if config_path.parent.exists():
                clients['vscode'] = {
                    'display_name': 'Visual Studio Code',
                    'config_path': config_path,
                    'type': 'json_config',
                    'server_key': 'servers'
                }
                break
        
        # Windsurf - Added detection
        windsurf_paths = [
            Path.home() / '.codeium' / 'windsurf' / 'mcp_config.json',
            Path(os.environ.get('APPDATA', '')) / '.codeium' / 'windsurf' / 'mcp_config.json'
        ]
        
        for config_path in windsurf_paths:
            if config_path.parent.exists():
                clients['windsurf'] = {
                    'display_name': 'Windsurf IDE',
                    'config_path': config_path,
                    'type': 'json_config',
                    'server_key': 'mcpServers'
                }
                break
        
        return clients
    
    def _detect_unix_clients(self) -> Dict[str, Dict[str, Any]]:
        """Detect MCP clients on Unix-like systems."""
        clients = {}
        
        # Claude Desktop (Linux/macOS)
        claude_config_paths = []
        if sys.platform == 'darwin':  # macOS
            claude_config_paths = [
                Path.home() / 'Library' / 'Application Support' / 'Claude' / 'claude_desktop_config.json'
            ]
        else:  # Linux
            claude_config_paths = [
                Path.home() / '.config' / 'claude' / 'claude_desktop_config.json'
            ]
        
        for config_path in claude_config_paths:
            if config_path.parent.exists():  # Directory exists
                clients['claude_desktop'] = {
                    'display_name': 'Claude Desktop',
                    'config_path': config_path,
                    'type': 'json_config',
                    'server_key': 'mcpServers'
                }
                break
        
        # Claude Code CLI
        if shutil.which('claude'):
            clients['claude_code'] = {
                'display_name': 'Claude Code',
                'config_path': None,  # Uses CLI commands
                'type': 'cli_config',
                'command': 'claude'
            }
        
        # Cursor (Linux/macOS) - Fixed path
        cursor_paths = []
        if sys.platform == 'darwin':  # macOS
            cursor_paths = [
                Path.home() / '.cursor' / 'mcp.json',
                Path.home() / 'Library' / 'Application Support' / 'Cursor' / 'User' / 'mcp.json'
            ]
        else:  # Linux
            cursor_paths = [
                Path.home() / '.cursor' / 'mcp.json',
                Path.home() / '.config' / 'Cursor' / 'User' / 'mcp.json'
            ]
        
        for config_path in cursor_paths:
            if config_path.parent.exists():
                clients['cursor'] = {
                    'display_name': 'Cursor IDE',
                    'config_path': config_path,
                    'type': 'json_config',
                    'server_key': 'mcpServers'
                }
                break
        
        # VS Code (Linux/macOS) - Fixed path
        vscode_paths = []
        if sys.platform == 'darwin':  # macOS
            vscode_paths = [
                Path.home() / 'Library' / 'Application Support' / 'Code' / 'User' / 'mcp.json'
            ]
        else:  # Linux
            vscode_paths = [
                Path.home() / '.config' / 'Code' / 'User' / 'mcp.json'
            ]
        
        # Check if VS Code is actually installed locally (not just Windows mount in WSL)
        vscode_available = False
        if shutil.which('code'):
            code_path = shutil.which('code')
            # Skip if it's a Windows mount in WSL (starts with /mnt/)
            if not code_path.startswith('/mnt/'):
                vscode_available = True
        
        if vscode_available:
            for config_path in vscode_paths:
                if config_path.parent.exists():  # Check directory exists
                    clients['vscode'] = {
                        'display_name': 'Visual Studio Code',
                        'config_path': config_path,
                        'type': 'json_config',
                        'server_key': 'servers'
                    }
                    break
        
        # Windsurf (Linux/macOS) - Added detection
        windsurf_paths = []
        if sys.platform == 'darwin':  # macOS
            windsurf_paths = [
                Path.home() / '.codeium' / 'windsurf' / 'mcp_config.json'
            ]
        else:  # Linux
            windsurf_paths = [
                Path.home() / '.codeium' / 'windsurf' / 'mcp_config.json',
                Path.home() / '.config' / 'windsurf' / 'mcp_config.json'
            ]
        
        for config_path in windsurf_paths:
            if config_path.parent.exists():
                clients['windsurf'] = {
                    'display_name': 'Windsurf IDE',
                    'config_path': config_path,
                    'type': 'json_config',
                    'server_key': 'mcpServers'
                }
                break
        
        return clients
    
    def _is_client_available(self, client_info: Dict[str, Any]) -> bool:
        """Check if a client is actually available/installed."""
        if client_info['type'] == 'cli_config':
            # For CLI clients, check if command exists
            return shutil.which(client_info['command']) is not None
        else:
            # For JSON config clients, check if config directory exists
            config_path = client_info['config_path']
            return config_path.parent.exists() if config_path else False
    
    def _filter_target_clients(self, detected_clients: Dict[str, Any]) -> Dict[str, Any]:
        """Filter clients based on user configuration."""
        if not self.config.specific_clients:
            # Configure all detected clients
            return detected_clients
        
        target_clients = {}
        for client_name in self.config.specific_clients:
            client_name = client_name.strip().lower()
            
            # Handle common aliases
            if client_name in ['claude', 'claude_desktop']:
                client_name = 'claude_desktop'
            elif client_name in ['code', 'vscode', 'vs_code']:
                client_name = 'vscode'
            
            if client_name in detected_clients:
                target_clients[client_name] = detected_clients[client_name]
            else:
                self.console.print(f"[yellow]Warning: Client '{client_name}' not found[/yellow]")
        
        return target_clients
    
    def _configure_single_client(self, client_id: str, client_info: Dict[str, Any]) -> None:
        """Configure a single MCP client."""
        if client_info['type'] == 'cli_config':
            self._configure_cli_client(client_id, client_info)
        else:
            self._configure_json_client(client_id, client_info)
    
    def _configure_cli_client(self, client_id: str, client_info: Dict[str, Any]) -> None:
        """Configure CLI-based client (like Claude Code)."""
        if client_id == 'claude_code':
            self._configure_claude_code()
        else:
            raise ClientConfigurationError(f"Unsupported CLI client: {client_id}")
    
    def _configure_claude_code(self) -> None:
        """Configure Claude Code CLI."""
        try:
            # Build server configuration JSON
            server_config = self._build_server_config()
            server_json = json.dumps(server_config)
            
            # If force mode or existing config detected, remove first
            if self.config.force or self._claude_code_server_exists():
                try:
                    remove_cmd = ['claude', 'mcp', 'remove', 'task-orchestrator']
                    subprocess.run(remove_cmd, check=True, capture_output=True, timeout=30)
                    if self.config.verbose:
                        self.console.print("[dim]Removed existing Claude Code configuration[/dim]")
                except subprocess.CalledProcessError:
                    # Ignore errors if server doesn't exist
                    pass
            
            # Add server using claude mcp add-json command with correct syntax
            cmd = [
                'claude', 'mcp', 'add-json',
                'task-orchestrator',
                server_json
            ]
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if self.config.verbose:
                self.console.print(f"[dim]Command: {' '.join(cmd[:3])} task-orchestrator <config>[/dim]")
                if result.stdout:
                    self.console.print(f"[dim]Output: {result.stdout.strip()}[/dim]")
                    
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            # Check if it's just a duplicate configuration warning
            if "already exists" in error_msg and not self.config.force:
                raise ClientConfigurationError(f"Failed to configure Claude Code: {error_msg}. Use --force to overwrite existing configuration.")
            raise ClientConfigurationError(f"Failed to configure Claude Code: {error_msg}")
        except subprocess.TimeoutExpired:
            raise ClientConfigurationError("Claude Code configuration timed out")
    
    def _claude_code_server_exists(self) -> bool:
        """Check if task-orchestrator server already exists in Claude Code."""
        try:
            result = subprocess.run(
                ['claude', 'mcp', 'get', 'task-orchestrator'],
                check=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False
    
    def _configure_json_client(self, client_id: str, client_info: Dict[str, Any]) -> None:
        """Configure JSON-based client configuration."""
        config_path = client_info['config_path']
        
        # Create backup
        backup_path = self._create_config_backup(config_path)
        
        try:
            # Load or create configuration based on client type
            config = self._load_json_config(config_path)
            
            # Build server configuration specific to the client
            server_config = self._build_client_specific_config(client_id, client_info)
            
            # Update configuration using client-specific method
            self._update_client_config(config, client_id, client_info, server_config)
            
            # Save configuration
            self._save_json_config(config_path, config)
            
        except Exception as e:
            # Restore backup on failure
            if backup_path and backup_path.exists():
                shutil.copy2(backup_path, config_path)
            raise ClientConfigurationError(f"Failed to configure {client_info['display_name']}: {e}")
    
    def _remove_client_configuration(self, client_id: str, client_info: Dict[str, Any]) -> None:
        """Remove MCP configuration from a client."""
        if client_info['type'] == 'cli_config':
            self._remove_cli_client_config(client_id)
        else:
            self._remove_json_client_config(client_info)
    
    def _remove_cli_client_config(self, client_id: str) -> None:
        """Remove CLI client configuration."""
        if client_id == 'claude_code':
            try:
                subprocess.run(
                    ['claude', 'mcp', 'remove', 'task-orchestrator'],
                    check=True,
                    capture_output=True,
                    timeout=30
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                # Ignore errors during removal
                pass
    
    def _remove_json_client_config(self, client_info: Dict[str, Any]) -> None:
        """Remove JSON client configuration."""
        config_path = client_info['config_path']
        server_key = client_info['server_key']
        
        if not config_path.exists():
            return
        
        try:
            config = self._load_json_config(config_path)
            
            if server_key in config and 'task-orchestrator' in config[server_key]:
                del config[server_key]['task-orchestrator']
                
                # Remove empty server sections
                if not config[server_key]:
                    del config[server_key]
                
                self._save_json_config(config_path, config)
                
        except Exception as e:
            logger.warning(f"Failed to remove configuration from {config_path}: {e}")
    
    def _build_client_specific_config(self, client_id: str, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Build MCP server configuration specific to the client."""
        # Use the correct Python executable (venv Python if in project scope)
        python_command = self._get_python_command()
        
        base_config = {
            "command": str(python_command),
            "args": ["-m", "mcp_task_orchestrator"]
        }
        
        # Only Claude Desktop needs the cwd property
        # Other clients (VS Code, Cursor, Windsurf) don't need or allow it
        if client_id == 'claude_desktop' and self.config.scope == InstallationScope.PROJECT:
            server_path = self._get_server_path()
            base_config["cwd"] = str(server_path.parent)
        
        # Client-specific configuration adjustments
        if client_id == 'vscode':
            # VS Code uses 'type' field for transport and doesn't need cwd
            return {
                "type": "stdio",
                **base_config
            }
        elif client_id in ['claude_desktop', 'cursor', 'windsurf']:
            # These clients use the standard format
            return base_config
        else:
            return base_config
    
    def _update_client_config(self, config: Dict[str, Any], client_id: str, 
                             client_info: Dict[str, Any], server_config: Dict[str, Any]) -> None:
        """Update client configuration with server config."""
        server_key = client_info['server_key']
        
        # Ensure the server section exists
        if server_key not in config:
            config[server_key] = {}
        
        # Add the task-orchestrator server
        config[server_key]['task-orchestrator'] = server_config
    
    def _get_python_command(self) -> Path:
        """Get the correct Python executable path for MCP server configuration."""
        if self.config.scope in [InstallationScope.PROJECT, InstallationScope.CUSTOM]:
            venv_path = self._get_venv_path()
            if venv_path:
                if os.name == 'nt':  # Windows
                    return venv_path / 'Scripts' / 'python.exe'
                else:  # Unix-like
                    return venv_path / 'bin' / 'python'
        
        # System/user scope uses current Python
        return Path(sys.executable)
    
    def _get_venv_path(self) -> Optional[Path]:
        """Get virtual environment path if applicable."""
        if self.config.scope == InstallationScope.PROJECT:
            return Path.cwd() / 'venv'
        elif self.config.scope == InstallationScope.CUSTOM:
            return self.config.custom_path
        return None
    
    def _build_server_config(self) -> Dict[str, Any]:
        """Build MCP server configuration (legacy method for backward compatibility)."""
        python_command = self._get_python_command()
        server_path = self._get_server_path()
        
        return {
            "command": str(python_command),
            "args": ["-m", "mcp_task_orchestrator"],
            "cwd": str(server_path.parent) if self.config.scope == InstallationScope.PROJECT else None
        }
    
    def _get_server_path(self) -> Path:
        """Get the path to the MCP server module."""
        try:
            # Try to find the installed module
            result = subprocess.run(
                [sys.executable, '-c', 
                 'import mcp_task_orchestrator; print(mcp_task_orchestrator.__file__)'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                module_path = Path(result.stdout.strip())
                if module_path.exists():
                    return module_path.parent
                    
        except Exception:
            pass
        
        # Fallback to project directory for development installs
        if self.config.scope == InstallationScope.PROJECT or self.config.source == InstallationSource.LOCAL:
            project_root = Path.cwd()
            server_module = project_root / 'mcp_task_orchestrator'
            if server_module.exists():
                return server_module
        
        raise ClientConfigurationError("Could not locate MCP server module")
    
    def _load_json_config(self, config_path: Path) -> Dict[str, Any]:
        """Load JSON configuration file."""
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise ClientConfigurationError(f"Failed to load config file {config_path}: {e}")
    
    def _save_json_config(self, config_path: Path, config: Dict[str, Any]) -> None:
        """Save JSON configuration file."""
        try:
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write configuration with proper formatting
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                f.write('\n')  # Add trailing newline
                
        except OSError as e:
            raise ClientConfigurationError(f"Failed to save config file {config_path}: {e}")
    
    def _create_config_backup(self, config_path: Path) -> Optional[Path]:
        """Create backup of configuration file."""
        if not config_path.exists():
            return None
        
        timestamp = int(time.time())
        backup_path = config_path.with_suffix(f'.backup.{timestamp}.json')
        
        try:
            shutil.copy2(config_path, backup_path)
            return backup_path
        except OSError as e:
            logger.warning(f"Failed to create backup of {config_path}: {e}")
            return None
    
    def _show_dry_run_configuration(self) -> None:
        """Show what clients would be configured in dry run mode."""
        detected_clients = self.detect_mcp_clients()
        
        if not detected_clients:
            self.console.print("[dim]Dry run: No MCP clients detected[/dim]")
            return
        
        target_clients = self._filter_target_clients(detected_clients)
        
        if not target_clients:
            self.console.print("[dim]Dry run: No matching clients found[/dim]")
            return
        
        self.console.print("[dim]Dry run: Would configure these clients:[/dim]")
        for client_id, client_info in target_clients.items():
            self.console.print(f"[dim]  • {client_info['display_name']}[/dim]")
            if client_info['type'] == 'json_config':
                self.console.print(f"[dim]    Config: {client_info['config_path']}[/dim]")
            else:
                self.console.print(f"[dim]    CLI: {client_info['command']}[/dim]")