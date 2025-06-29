#!/usr/bin/env python3
"""
Universal MCP Task Orchestrator Installer

This installer detects and configures MCP Task Orchestrator for all known MCP clients
across different environments (native Windows, WSL, macOS, Linux).

Supported clients:
- Claude Desktop (Windows, macOS, Linux)
- Claude Code (WSL environment)
- Cursor IDE
- Windsurf
- VS Code with MCP extensions (Roo Code, Cline, etc.)
- Continue.dev
"""

import os
import sys
import json
import platform
import subprocess
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
# Removed track import - using simple progress display instead

console = Console()
logger = logging.getLogger(__name__)


class MCPClientConfig:
    """Base class for MCP client configurations."""
    
    def __init__(self, name: str, config_paths: List[Path]):
        self.name = name
        self.config_paths = config_paths
        self.is_running = False
        self.config_data = {}
        self.workspace_support = False
    
    def detect(self) -> bool:
        """Check if this client is installed."""
        for path in self.config_paths:
            if path.exists():
                return True
        return False
    
    def check_running(self) -> bool:
        """Check if the client is currently running."""
        # Override in subclasses for specific detection
        return False
    
    def get_config_path(self) -> Optional[Path]:
        """Get the first existing config path."""
        for path in self.config_paths:
            if path.exists():
                return path
        return None
    
    def backup_config(self, path: Path) -> Optional[Path]:
        """Create a backup of the configuration file."""
        backup_path = path.with_suffix(f'.backup.{int(time.time())}.json')
        try:
            shutil.copy2(path, backup_path)
            return backup_path
        except Exception as e:
            logger.error(f"Failed to backup {path}: {e}")
            return None
    
    def load_config(self, path: Path) -> dict:
        """Load configuration from file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            return {}
    
    def save_config(self, path: Path, config: dict) -> bool:
        """Save configuration to file."""
        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save {path}: {e}")
            return False


class ClaudeDesktopConfig(MCPClientConfig):
    """Claude Desktop configuration handler."""
    
    def __init__(self):
        paths = []
        system = platform.system()
        
        if system == "Windows":
            paths.append(Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json")
        elif system == "Darwin":  # macOS
            paths.append(Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json")
        else:  # Linux
            paths.append(Path.home() / ".config" / "Claude" / "claude_desktop_config.json")
        
        super().__init__("Claude Desktop", paths)
        self.is_wsl = self._detect_wsl()
    
    def _detect_wsl(self) -> bool:
        """Detect if running in WSL."""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except:
            return False
    
    def detect(self) -> bool:
        """Check if this client is installed, considering WSL context."""
        # In WSL, we might see Windows files through the mount, but Claude Desktop
        # is actually running in Windows, not WSL. We should not configure it from WSL.
        if self.is_wsl:
            # In WSL, we can see Windows files but Claude Desktop runs in Windows
            # Don't detect Claude Desktop as available from WSL
            return False
        
        # Normal detection for native environments
        for path in self.config_paths:
            if path.exists():
                return True
        return False
    
    def check_running(self) -> bool:
        """Check if Claude Desktop is running."""
        system = platform.system()
        
        if system == "Windows":
            try:
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Claude.exe'], 
                                      capture_output=True, text=True)
                return "Claude.exe" in result.stdout
            except:
                return False
        elif system == "Darwin":
            try:
                result = subprocess.run(['pgrep', '-x', 'Claude'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            except:
                return False
        else:  # Linux
            try:
                result = subprocess.run(['pgrep', '-x', 'claude'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            except:
                return False
    
    def configure(self, server_path: str, python_path: str = None) -> bool:
        """Configure Claude Desktop for Task Orchestrator."""
        config_path = self.get_config_path()
        if not config_path:
            return False
        
        # Load existing config
        config = self.load_config(config_path)
        
        # Ensure mcpServers section exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Determine Python command
        if python_path:
            python_cmd = python_path
        else:
            python_cmd = sys.executable if platform.system() == "Windows" else "python3"
        
        # Add task orchestrator configuration
        config["mcpServers"]["task-orchestrator"] = {
            "command": python_cmd,
            "args": ["-m", "mcp_task_orchestrator.server"],
            "env": {}
        }
        
        return self.save_config(config_path, config)


class ClaudeCodeConfig(MCPClientConfig):
    """Claude Code (CLI) configuration handler."""
    
    def __init__(self):
        # Claude Code doesn't use direct file configuration
        # It uses CLI commands, but we can check if it's available
        paths = []
        super().__init__("Claude Code", paths)
        self.workspace_support = True
        self.cli_based = True
    
    def detect(self) -> bool:
        """Check if Claude Code CLI is available."""
        try:
            result = subprocess.run(['claude', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def configure(self, server_path: str, python_path: str = None) -> bool:
        """Configure Claude Code for Task Orchestrator using CLI commands."""
        try:
            # Use Claude Code's CLI to add the MCP server
            python_cmd = python_path or sys.executable
            
            # Try workspace scope first
            workspace_cmd = [
                'claude', 'mcp', 'add-json',
                '--scope', 'workspace',
                '--name', 'task-orchestrator',
                json.dumps({
                    "command": python_cmd,
                    "args": ["-m", "mcp_task_orchestrator.server"],
                    "env": {}
                })
            ]
            
            result = subprocess.run(workspace_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                console.print(f"[green]✓[/green] Configured Claude Code (workspace scope)")
                return True
            else:
                # Fallback to global scope
                global_cmd = [
                    'claude', 'mcp', 'add-json',
                    '--scope', 'user',
                    '--name', 'task-orchestrator',
                    json.dumps({
                        "command": python_cmd,
                        "args": ["-m", "mcp_task_orchestrator.server"],
                        "env": {}
                    })
                ]
                
                result = subprocess.run(global_cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    console.print(f"[green]✓[/green] Configured Claude Code (global scope)")
                    return True
                else:
                    console.print(f"[red]✗[/red] Failed to configure Claude Code: {result.stderr}")
                    return False
        
        except Exception as e:
            console.print(f"[red]✗[/red] Error configuring Claude Code: {e}")
            return False


class CursorConfig(MCPClientConfig):
    """Cursor IDE configuration handler."""
    
    def __init__(self):
        paths = []
        
        # Global config
        paths.append(Path.home() / ".cursor" / "mcp.json")
        
        # Project-specific config
        cwd = Path.cwd()
        paths.append(cwd / ".cursor" / "mcp.json")
        
        super().__init__("Cursor", paths)
        self.workspace_support = True
    
    def check_running(self) -> bool:
        """Check if Cursor is running."""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Cursor.exe'], 
                                      capture_output=True, text=True)
                return "Cursor.exe" in result.stdout
            else:
                result = subprocess.run(['pgrep', '-x', 'cursor'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
        except:
            return False
    
    def configure(self, server_path: str, python_path: str = None) -> bool:
        """Configure Cursor for Task Orchestrator."""
        # Try workspace config first, then global
        workspace_config = Path.cwd() / ".cursor" / "mcp.json"
        global_config = Path.home() / ".cursor" / "mcp.json"
        
        # Ask user preference
        use_workspace = Confirm.ask(
            f"Configure Cursor for current workspace only?", 
            default=True
        )
        
        config_path = workspace_config if use_workspace else global_config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create config
        if config_path.exists():
            config = self.load_config(config_path)
        else:
            config = {"mcpServers": {}}
        
        # Ensure mcpServers section exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Determine Python command
        python_cmd = python_path or sys.executable
        
        # Add task orchestrator configuration
        config["mcpServers"]["task-orchestrator"] = {
            "command": python_cmd,
            "args": ["-m", "mcp_task_orchestrator.server"],
            "env": {}
        }
        
        success = self.save_config(config_path, config)
        
        if success:
            scope = "workspace" if use_workspace else "global"
            console.print(f"[green]✓[/green] Configured Cursor ({scope} scope)")
        
        return success


class WindsurfConfig(MCPClientConfig):
    """Windsurf configuration handler."""
    
    def __init__(self):
        paths = []
        
        # Based on research: ~/.codeium/windsurf/mcp_config.json
        paths.append(Path.home() / ".codeium" / "windsurf" / "mcp_config.json")
        
        # Windows equivalent
        if platform.system() == "Windows":
            paths.append(Path.home() / ".codeium" / "windsurf" / "mcp_config.json")
        
        super().__init__("Windsurf", paths)
    
    def check_running(self) -> bool:
        """Check if Windsurf is running."""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Windsurf.exe'], 
                                      capture_output=True, text=True)
                return "Windsurf.exe" in result.stdout
            else:
                result = subprocess.run(['pgrep', '-x', 'windsurf'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
        except:
            return False
    
    def configure(self, server_path: str, python_path: str = None) -> bool:
        """Configure Windsurf for Task Orchestrator."""
        config_path = self.get_config_path()
        if not config_path:
            config_path = self.config_paths[0]
            config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create config
        if config_path.exists():
            config = self.load_config(config_path)
        else:
            config = {"mcpServers": {}}
        
        # Ensure mcpServers section exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Determine Python command
        python_cmd = python_path or sys.executable
        
        # Add task orchestrator configuration
        config["mcpServers"]["task-orchestrator"] = {
            "command": python_cmd,
            "args": ["-m", "mcp_task_orchestrator.server"],
            "env": {}
        }
        
        success = self.save_config(config_path, config)
        
        if success:
            console.print(f"[green]✓[/green] Configured Windsurf")
            console.print(f"[dim]Access via CMD/Ctrl + Shift + P → 'MCP Configuration Panel'[/dim]")
        
        return success


class VSCodeMCPConfig(MCPClientConfig):
    """VS Code with GitHub Copilot MCP support."""
    
    def __init__(self):
        paths = []
        system = platform.system()
        
        # VS Code settings.json locations
        if system == "Windows":
            paths.append(Path.home() / "AppData" / "Roaming" / "Code" / "User" / "settings.json")
        elif system == "Darwin":
            paths.append(Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json")
        else:
            paths.append(Path.home() / ".config" / "Code" / "User" / "settings.json")
        
        # Workspace config
        paths.append(Path.cwd() / ".vscode" / "mcp.json")
        
        super().__init__("VS Code (GitHub Copilot)", paths)
        self.workspace_support = True
    
    def check_running(self) -> bool:
        """Check if VS Code is running."""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Code.exe'], 
                                      capture_output=True, text=True)
                return "Code.exe" in result.stdout
            else:
                result = subprocess.run(['pgrep', '-x', 'code'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
        except:
            return False
    
    def configure(self, server_path: str, python_path: str = None) -> bool:
        """Configure VS Code GitHub Copilot for Task Orchestrator."""
        # Ask user preference for scope
        use_workspace = Confirm.ask(
            f"Configure VS Code for current workspace only?", 
            default=True
        )
        
        if use_workspace:
            # Create workspace-specific MCP config
            config_path = Path.cwd() / ".vscode" / "mcp.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                "mcpServers": {
                    "task-orchestrator": {
                        "command": python_path or sys.executable,
                        "args": ["-m", "mcp_task_orchestrator.server"],
                        "env": {}
                    }
                }
            }
            
            success = self.save_config(config_path, config)
            if success:
                console.print(f"[green]✓[/green] Configured VS Code (workspace scope)")
                console.print(f"[dim]Note: Requires GitHub Copilot subscription and Agent Mode enabled[/dim]")
        else:
            # Use global settings.json (less common for MCP)
            config_path = self.get_config_path()
            if not config_path:
                config_path = self.config_paths[0]
                config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing settings
            if config_path.exists():
                config = self.load_config(config_path)
            else:
                config = {}
            
            # Add MCP configuration to settings
            if "mcp.servers" not in config:
                config["mcp.servers"] = {}
            
            config["mcp.servers"]["task-orchestrator"] = {
                "command": python_path or sys.executable,
                "args": ["-m", "mcp_task_orchestrator.server"],
                "env": {}
            }
            
            success = self.save_config(config_path, config)
            if success:
                console.print(f"[green]✓[/green] Configured VS Code (global scope)")
        
        return success


class ContinueDevConfig(MCPClientConfig):
    """Continue.dev extension configuration handler."""
    
    def __init__(self):
        paths = []
        
        # Continue.dev config location
        paths.append(Path.home() / ".continue" / "config.json")
        
        # Workspace-specific config
        paths.append(Path.cwd() / ".continue" / "config.json")
        
        super().__init__("Continue.dev", paths)
        self.workspace_support = True
    
    def configure(self, server_path: str, python_path: str = None) -> bool:
        """Configure Continue.dev for Task Orchestrator."""
        # Ask user preference
        use_workspace = Confirm.ask(
            f"Configure Continue.dev for current workspace only?", 
            default=True
        )
        
        config_path = (Path.cwd() / ".continue" / "config.json" 
                      if use_workspace 
                      else Path.home() / ".continue" / "config.json")
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create config
        if config_path.exists():
            config = self.load_config(config_path)
        else:
            config = {}
        
        # Add MCP servers section
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Add task orchestrator
        config["mcpServers"]["task-orchestrator"] = {
            "command": python_path or sys.executable,
            "args": ["-m", "mcp_task_orchestrator.server"]
        }
        
        success = self.save_config(config_path, config)
        
        if success:
            scope = "workspace" if use_workspace else "global"
            console.print(f"[green]✓[/green] Configured Continue.dev ({scope} scope)")
        
        return success


class UniversalInstaller:
    """Universal installer for MCP Task Orchestrator."""
    
    def __init__(self):
        self.clients = [
            ClaudeDesktopConfig(),
            ClaudeCodeConfig(),
            CursorConfig(),
            WindsurfConfig(),
            VSCodeMCPConfig(),
            ContinueDevConfig()
        ]
        self.detected_clients = []
        self.running_clients = []
        self.is_wsl = self._detect_wsl()
        self.python_path = sys.executable
    
    def _detect_wsl(self) -> bool:
        """Detect if running in WSL."""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except:
            return False
    
    def detect_clients(self):
        """Detect installed MCP clients."""
        console.print("\n[bold]🔍 Detecting MCP Clients...[/bold]\n")
        
        table = Table(title="MCP Client Detection Results")
        table.add_column("Client", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Running", style="yellow")
        table.add_column("Config Path")
        
        for client in self.clients:
            if client.detect():
                self.detected_clients.append(client)
                is_running = client.check_running()
                if is_running:
                    self.running_clients.append(client)
                
                config_path = client.get_config_path()
                table.add_row(
                    client.name,
                    "✓ Detected",
                    "● Running" if is_running else "○ Not Running",
                    str(config_path) if config_path else "N/A"
                )
        
        if self.detected_clients:
            console.print(table)
        else:
            console.print("[red]No MCP clients detected![/red]")
            console.print("\nPlease install one of the following:")
            for client in self.clients:
                console.print(f"  • {client.name}")
    
    def _check_externally_managed(self) -> bool:
        """Check if Python environment is externally managed."""
        try:
            # Check for EXTERNALLY-MANAGED file
            site_packages = Path(sys.executable).parent.parent / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
            externally_managed = site_packages / "EXTERNALLY-MANAGED"
            
            if externally_managed.exists():
                return True
            
            # Alternative check: try a test pip install
            result = subprocess.run([sys.executable, "-m", "pip", "install", "--dry-run", "pip"], 
                                  capture_output=True, text=True)
            
            return "externally-managed-environment" in result.stderr.lower()
        except:
            return False
    
    def _detect_virtual_env(self) -> bool:
        """Check if running in a virtual environment."""
        return (hasattr(sys, 'real_prefix') or 
                (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
                os.environ.get('VIRTUAL_ENV') is not None)

    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed."""
        console.print("\n[bold]📦 Checking Dependencies...[/bold]\n")
        
        # Check environment status
        in_venv = self._detect_virtual_env()
        externally_managed = self._check_externally_managed()
        
        if externally_managed and not in_venv:
            console.print("[yellow]⚠️  Python environment is externally managed[/yellow]")
            console.print("[dim]This environment prevents direct pip installs for system protection.[/dim]\n")
            
            console.print("[bold]Recommended solution:[/bold]")
            console.print("1. Create a virtual environment:")
            console.print("   [cyan]python -m venv mcp-orchestrator-env[/cyan]")
            
            if self.is_wsl or platform.system() == "Linux":
                console.print("2. Activate it:")
                console.print("   [cyan]source mcp-orchestrator-env/bin/activate[/cyan]")
            else:
                console.print("2. Activate it:")
                console.print("   [cyan]mcp-orchestrator-env\\Scripts\\activate[/cyan]")
            
            console.print("3. Install mcp-task-orchestrator:")
            console.print("   [cyan]pip install mcp-task-orchestrator[/cyan]")
            console.print("4. Run setup:")
            console.print("   [cyan]mcp-task-orchestrator-cli setup[/cyan]")
            
            console.print("\n[dim]Alternative: Use pipx for isolated installation:[/dim]")
            console.print("   [cyan]pipx install mcp-task-orchestrator[/cyan]")
            console.print("   [cyan]pipx run mcp-task-orchestrator-cli setup[/cyan]")
            
            return False
        
        required = {
            "mcp": "mcp",
            "pydantic": "pydantic",
            "jinja2": "jinja2",
            "yaml": "pyyaml",  # Fix: import name vs package name
            "aiofiles": "aiofiles",
            "psutil": "psutil",
            "filelock": "filelock",
            "sqlalchemy": "sqlalchemy",
            "alembic": "alembic",
            "typer": "typer",
            "rich": "rich"
        }
        
        missing = []
        
        for import_name, package_name in required.items():
            try:
                __import__(import_name)
                console.print(f"  ✓ {package_name}")
            except ImportError:
                console.print(f"  ✗ {package_name}")
                missing.append(package_name)
        
        if missing:
            console.print(f"\n[red]Missing dependencies: {', '.join(missing)}[/red]")
            
            if externally_managed:
                console.print("\n[yellow]Cannot install automatically in externally managed environment.[/yellow]")
                console.print("Please install in a virtual environment or use pipx.")
                return False
            
            if Confirm.ask("\nWould you like to install missing dependencies?"):
                cmd = [sys.executable, "-m", "pip", "install"] + missing
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    console.print("[green]✓ Dependencies installed successfully![/green]")
                    return True
                else:
                    console.print(f"[red]Failed to install dependencies:[/red]\n{result.stderr}")
                    
                    if "externally-managed-environment" in result.stderr:
                        console.print("\n[yellow]This environment is externally managed.[/yellow]")
                        console.print("Please use a virtual environment or pipx as shown above.")
                    
                    return False
            return False
        
        if in_venv:
            console.print(f"\n[green]✓ All dependencies satisfied![/green] [dim](virtual environment)[/dim]")
        else:
            console.print(f"\n[green]✓ All dependencies satisfied![/green]")
        
        return True
    
    def find_server_module(self) -> Optional[str]:
        """Find the task orchestrator server module."""
        console.print("\n[bold]🔎 Locating Server Module...[/bold]\n")
        
        # Try to import and find the module
        try:
            import mcp_task_orchestrator
            module_path = Path(mcp_task_orchestrator.__file__).parent
            server_path = module_path / "server.py"
            
            if server_path.exists():
                console.print(f"[green]✓ Found server module: {server_path}[/green]")
                return str(server_path)
        except ImportError:
            pass
        
        # Check if running from source
        source_path = Path(__file__).parent.parent / "mcp_task_orchestrator" / "server.py"
        if source_path.exists():
            console.print(f"[green]✓ Found server module (source): {source_path}[/green]")
            return str(source_path)
        
        console.print("[red]✗ Could not locate server module[/red]")
        console.print("Please ensure mcp-task-orchestrator is properly installed:")
        console.print("  pip install mcp-task-orchestrator")
        return None
    
    def configure_clients(self, selected_clients: List[MCPClientConfig], server_path: str):
        """Configure selected clients."""
        console.print("\n[bold]⚙️  Configuring Clients...[/bold]\n")
        
        # Warn about running clients
        if self.running_clients:
            running_names = [c.name for c in self.running_clients if c in selected_clients]
            if running_names:
                console.print(f"[yellow]⚠️  Warning: The following clients are running:[/yellow]")
                for name in running_names:
                    console.print(f"   • {name}")
                console.print("\n[yellow]Please close these applications before continuing.[/yellow]")
                
                if not Confirm.ask("\nContinue anyway?"):
                    return
        
        success_count = 0
        total_clients = len(selected_clients)
        
        for i, client in enumerate(selected_clients, 1):
            console.print(f"\n[bold cyan]Configuring {client.name} ({i}/{total_clients})...[/bold cyan]")
            
            # Create backup
            config_path = client.get_config_path()
            if config_path and config_path.exists():
                backup = client.backup_config(config_path)
                if backup:
                    console.print(f"  📁 Backed up {client.name} config to: {backup}")
            
            # Configure client
            if client.configure(server_path, self.python_path):
                console.print(f"  [green]✓ Configured {client.name}[/green]")
                success_count += 1
            else:
                console.print(f"  [red]✗ Failed to configure {client.name}[/red]")
        
        console.print(f"\n[bold]Summary:[/bold] Configured {success_count}/{len(selected_clients)} clients")
    
    def run(self):
        """Run the universal installer."""
        console.print(Panel.fit(
            "[bold cyan]MCP Task Orchestrator Universal Installer[/bold cyan]\n"
            "[dim]Configures Task Orchestrator for all MCP clients[/dim]",
            border_style="cyan"
        ))
        
        # Environment info
        console.print(f"\n[dim]Environment: {platform.system()} {platform.release()}[/dim]")
        if self.is_wsl:
            console.print("[dim]Running in WSL (Windows Subsystem for Linux)[/dim]")
            console.print("[dim]Note: Only WSL-compatible clients will be detected.[/dim]")
            console.print("[dim]For Windows applications (Claude Desktop), run installer from Windows.[/dim]")
        console.print(f"[dim]Python: {sys.version.split()[0]} ({self.python_path})[/dim]")
        
        # Check dependencies
        if not self.check_dependencies():
            console.print("\n[red]Please install missing dependencies and try again.[/red]")
            return
        
        # Find server module
        server_path = self.find_server_module()
        if not server_path:
            return
        
        # Detect clients
        self.detect_clients()
        
        if not self.detected_clients:
            console.print("\n[red]No MCP clients found to configure.[/red]")
            return
        
        # Select clients to configure
        console.print("\n[bold]Select clients to configure:[/bold]")
        console.print("[dim]Press Space to select/deselect, Enter to confirm[/dim]\n")
        
        selected_indices = []
        for i, client in enumerate(self.detected_clients):
            if Confirm.ask(f"Configure {client.name}?", default=True):
                selected_indices.append(i)
        
        if not selected_indices:
            console.print("\n[yellow]No clients selected.[/yellow]")
            return
        
        selected_clients = [self.detected_clients[i] for i in selected_indices]
        
        # Configure selected clients
        self.configure_clients(selected_clients, server_path)
        
        # Final instructions
        console.print("\n[bold green]✨ Installation Complete![/bold green]\n")
        console.print("[bold]Next steps:[/bold]")
        console.print("1. Restart the configured MCP clients")
        console.print("2. Look for 'task-orchestrator' in available tools")
        console.print("3. Start orchestrating your tasks!\n")
        
        if any(client.workspace_support for client in selected_clients):
            console.print("[dim]Note: Some clients support workspace-specific configurations.[/dim]")
            console.print("[dim]Run this installer in each workspace where you want to use Task Orchestrator.[/dim]")


def main():
    """Main entry point."""
    installer = UniversalInstaller()
    
    try:
        installer.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Installation cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Installation error: {e}[/red]")
        logger.exception("Installation failed")
        sys.exit(1)


if __name__ == "__main__":
    import time  # For backup timestamps
    main()