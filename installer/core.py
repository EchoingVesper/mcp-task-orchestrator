"""
Core installation logic for the Universal Installer.

This module implements the main UniversalInstaller class and supporting
managers for environment, source, and client management.
"""

import os
import sys
import subprocess
import shutil
import json
import time
import tempfile
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
import logging

from .models import (
    InstallerConfig,
    InstallationEnvironment,
    InstallationStatus,
    OperationType,
    InstallationScope,
    InstallationSource,
    InstallationError,
    EnvironmentError,
    PackageInstallationError,
    ClientConfigurationError,
    ValidationError
)

from .environments import EnvironmentManager
from .sources import SourceManager  
from .clients import ClientManager
from .validation import ValidationManager

logger = logging.getLogger(__name__)


class UniversalInstaller:
    """Universal installer for MCP Task Orchestrator."""
    
    def __init__(self, config: InstallerConfig, console=None):
        self.config = config
        self.console = console or self._create_fallback_console()
        
        # Initialize managers
        self.environment_manager = EnvironmentManager(config, self.console)
        self.source_manager = SourceManager(config, self.console)
        self.client_manager = ClientManager(config, self.console)
        self.validation_manager = ValidationManager(config, self.console)
        
        # State tracking
        self._rollback_actions: List[callable] = []
        self._installation_start_time = None
        
    def _create_fallback_console(self):
        """Create fallback console if rich is not available."""
        class FallbackConsole:
            def print(self, *args, **kwargs):
                # Remove rich markup for plain output
                message = ' '.join(str(arg) for arg in args)
                # Simple markup removal
                import re
                clean_message = re.sub(r'\[/?[^\]]*\]', '', message)
                print(clean_message)
            
            def status(self, message):
                print(f"Status: {message}")
                return self
            
            def __enter__(self):
                return self
            
            def __exit__(self, *args):
                pass
        
        return FallbackConsole()
    
    def execute(self) -> int:
        """Execute the installer operation."""
        self._installation_start_time = time.time()
        
        try:
            with self.console.status("[bold blue]Initializing installer..."):
                self._validate_configuration()
            
            # Dispatch to appropriate operation handler
            if self.config.operation == OperationType.INSTALL:
                return self._handle_install()
            elif self.config.operation == OperationType.UNINSTALL:
                return self._handle_uninstall()
            elif self.config.operation == OperationType.REINSTALL:
                return self._handle_reinstall()
            elif self.config.operation == OperationType.UPDATE:
                return self._handle_update()
            elif self.config.operation == OperationType.VERIFY:
                return self._handle_verify()
            elif self.config.operation == OperationType.REPAIR:
                return self._handle_repair()
            elif self.config.operation == OperationType.STATUS:
                return self._handle_status()
            else:
                raise InstallationError(f"Unsupported operation: {self.config.operation}")
                
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            if self._rollback_actions:
                self._perform_rollback()
            raise
    
    def _validate_configuration(self) -> None:
        """Validate installer configuration."""
        if self.config.scope == InstallationScope.SYSTEM:
            if not self._has_admin_privileges():
                raise InstallationError(
                    "System-wide installation requires administrator privileges. "
                    "Run with 'sudo' on Unix systems or as Administrator on Windows."
                )
        
        if self.config.source == InstallationSource.GIT and not self.config.git_url:
            raise InstallationError("Git URL is required when using git source")
        
        if self.config.source == InstallationSource.VERSION and not self.config.version:
            raise InstallationError("Version is required when using version source")
    
    def _has_admin_privileges(self) -> bool:
        """Check if running with administrator privileges."""
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:  # Unix-like
                return os.geteuid() == 0
        except Exception:
            return False
    
    def _handle_install(self) -> int:
        """Handle installation operation."""
        self.console.print("[bold green]Starting installation...[/bold green]")
        
        # Check for existing installation
        current_status = InstallationStatus.detect_current_installation()
        if current_status.is_installed and not self.config.force:
            self.console.print(
                f"[yellow]Existing installation detected (version {current_status.version})[/yellow]"
            )
            if not self._confirm_action("Continue with installation anyway?"):
                return 0
        
        try:
            # Step 1: Prepare environment
            self.console.print("[cyan]Preparing installation environment...[/cyan]")
            self.environment_manager.prepare_environment()
            
            # Step 2: Create/validate virtual environment (if needed)
            if self.config.scope in [InstallationScope.PROJECT, InstallationScope.CUSTOM]:
                self.console.print("[cyan]Setting up virtual environment...[/cyan]")
                env = self.environment_manager.create_or_validate_environment()
                self._register_rollback(lambda: self.environment_manager.cleanup_environment(env))
            
            # Step 3: Install package
            self.console.print("[cyan]Installing package and dependencies...[/cyan]")
            self.source_manager.install_package()
            
            # Step 4: Configure MCP clients (if requested)
            if self.config.configure_clients:
                self.console.print("[cyan]Configuring MCP clients...[/cyan]")
                self.client_manager.configure_clients()
            
            # Step 5: Validate installation
            self.console.print("[cyan]Validating installation...[/cyan]")
            self.validation_manager.validate_installation()
            
            # Success!
            elapsed = time.time() - self._installation_start_time
            self.console.print(
                f"[bold green]✓ Installation completed successfully in {elapsed:.1f}s[/bold green]"
            )
            
            # Show next steps
            self._show_next_steps()
            
            return 0
            
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            raise InstallationError(f"Installation failed: {e}")
    
    def _handle_uninstall(self) -> int:
        """Handle uninstallation operation."""
        self.console.print("[bold red]Starting uninstallation...[/bold red]")
        
        current_status = InstallationStatus.detect_current_installation()
        if not current_status.is_installed:
            self.console.print("[yellow]No installation detected[/yellow]")
            return 0
        
        # Confirm uninstallation
        if not self.config.force:
            action_desc = "completely remove all data" if self.config.purge_config else "uninstall package"
            if not self._confirm_action(f"Are you sure you want to {action_desc}?"):
                return 0
        
        try:
            # Create backup if preserving configuration
            backup_path = None
            if self.config.preserve_config and not self.config.purge_config:
                backup_path = self._create_configuration_backup()
                if backup_path:
                    self.console.print(f"[green]Configuration backed up to: {backup_path}[/green]")
            
            # Remove package installation
            self.source_manager.uninstall_package(current_status)
            
            # Handle configuration
            if self.config.purge_config:
                self._remove_all_configuration()
            elif self.config.config_only:
                self._remove_configuration_only()
            
            # Update MCP clients
            if self.config.configure_clients:
                self.client_manager.remove_mcp_configuration()
            
            self.console.print("[bold green]✓ Uninstallation completed successfully[/bold green]")
            return 0
            
        except Exception as e:
            logger.error(f"Uninstallation failed: {e}")
            raise InstallationError(f"Uninstallation failed: {e}")
    
    def _handle_reinstall(self) -> int:
        """Handle reinstallation operation."""
        self.console.print("[bold yellow]Starting reinstallation...[/bold yellow]")
        
        # Backup configuration if requested
        backup_path = None
        if self.config.preserve_config:
            backup_path = self._create_configuration_backup()
        
        try:
            # Uninstall current installation
            self.console.print("[cyan]Removing existing installation...[/cyan]")
            current_status = InstallationStatus.detect_current_installation()
            if current_status.is_installed:
                self.source_manager.uninstall_package(current_status)
            
            # Perform fresh installation
            self.console.print("[cyan]Performing fresh installation...[/cyan]")
            result = self._handle_install()
            
            # Restore configuration if backed up
            if backup_path and self.config.preserve_config:
                self.console.print("[cyan]Restoring configuration...[/cyan]")
                self._restore_configuration_backup(backup_path)
            
            return result
            
        except Exception as e:
            # Try to restore backup on failure
            if backup_path and self.config.preserve_config:
                try:
                    self._restore_configuration_backup(backup_path)
                except Exception as restore_error:
                    logger.error(f"Failed to restore backup: {restore_error}")
            
            logger.error(f"Reinstallation failed: {e}")
            raise InstallationError(f"Reinstallation failed: {e}")
    
    def _handle_update(self) -> int:
        """Handle update operation."""
        self.console.print("[bold blue]Checking for updates...[/bold blue]")
        
        current_status = InstallationStatus.detect_current_installation()
        if not current_status.is_installed:
            self.console.print("[red]No installation found to update[/red]")
            return 1
        
        try:
            # Check for newer version
            latest_version = self.source_manager.get_latest_version()
            current_version = current_status.version
            
            if current_version == latest_version:
                self.console.print(f"[green]Already up to date (version {current_version})[/green]")
                return 0
            
            self.console.print(
                f"[cyan]Updating from version {current_version} to {latest_version}...[/cyan]"
            )
            
            # Perform update
            self.source_manager.update_package()
            
            # Validate updated installation
            self.validation_manager.validate_installation()
            
            self.console.print(f"[bold green]✓ Updated to version {latest_version}[/bold green]")
            return 0
            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            raise InstallationError(f"Update failed: {e}")
    
    def _handle_verify(self) -> int:
        """Handle verification operation."""
        self.console.print("[bold blue]Verifying installation...[/bold blue]")
        
        try:
            status = self.validation_manager.comprehensive_validation()
            
            if status['overall_status'] == 'healthy':
                self.console.print("[bold green]✓ Installation is healthy[/bold green]")
                return 0
            else:
                self.console.print("[bold red]✗ Installation has issues[/bold red]")
                for issue in status.get('issues', []):
                    self.console.print(f"  [red]• {issue}[/red]")
                return 1
                
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            self.console.print(f"[red]Verification failed: {e}[/red]")
            return 1
    
    def _handle_repair(self) -> int:
        """Handle repair operation."""
        self.console.print("[bold yellow]Repairing installation...[/bold yellow]")
        
        try:
            issues_found = self.validation_manager.detect_issues()
            
            if not issues_found:
                self.console.print("[green]No issues detected[/green]")
                return 0
            
            self.console.print(f"[yellow]Found {len(issues_found)} issues to repair[/yellow]")
            
            # Attempt to repair each issue
            repaired = 0
            for issue in issues_found:
                try:
                    self.validation_manager.repair_issue(issue)
                    repaired += 1
                    self.console.print(f"[green]✓ Repaired: {issue['description']}[/green]")
                except Exception as e:
                    self.console.print(f"[red]✗ Failed to repair: {issue['description']} - {e}[/red]")
            
            if repaired == len(issues_found):
                self.console.print("[bold green]✓ All issues repaired successfully[/bold green]")
                return 0
            else:
                self.console.print(f"[yellow]Repaired {repaired}/{len(issues_found)} issues[/yellow]")
                return 1
                
        except Exception as e:
            logger.error(f"Repair failed: {e}")
            raise InstallationError(f"Repair failed: {e}")
    
    def _handle_status(self) -> int:
        """Handle status operation."""
        self.console.print("[bold blue]Installation Status[/bold blue]")
        
        try:
            status = InstallationStatus.detect_current_installation()
            
            # Basic status
            if status.is_installed:
                self.console.print(f"[green]✓ Installed[/green] (version {status.version})")
                self.console.print(f"  Method: {status.installation_method}")
                if status.location:
                    self.console.print(f"  Location: {status.location}")
            else:
                self.console.print("[red]✗ Not installed[/red]")
                return 1
            
            # Environment status
            if status.environment:
                env_status = "valid" if status.environment.is_valid else "invalid"
                self.console.print(f"  Environment: {env_status}")
            
            # Client configuration status
            if status.clients_configured:
                self.console.print(f"  Configured clients: {', '.join(status.clients_configured)}")
            else:
                self.console.print("  Configured clients: none")
            
            # Additional diagnostics
            if self.config.verbose:
                self._show_detailed_status()
            
            return 0
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            self.console.print(f"[red]Status check failed: {e}[/red]")
            return 1
    
    def _show_detailed_status(self) -> None:
        """Show detailed status information."""
        try:
            # Python environment info
            self.console.print("\n[bold]Environment Details:[/bold]")
            self.console.print(f"  Python: {sys.version}")
            self.console.print(f"  Platform: {sys.platform}")
            
            # Package manager info
            package_managers = []
            for cmd in ['uv', 'pip', 'pipx']:
                if shutil.which(cmd):
                    package_managers.append(cmd)
            self.console.print(f"  Package managers: {', '.join(package_managers) or 'none'}")
            
            # Virtual environment info
            venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            self.console.print(f"  Virtual environment: {'active' if venv_active else 'none'}")
            
        except Exception as e:
            logger.warning(f"Could not gather detailed status: {e}")
    
    def _confirm_action(self, message: str) -> bool:
        """Get user confirmation for an action."""
        if self.config.force or self.config.dry_run:
            return True
        
        try:
            response = input(f"{message} [y/N]: ").strip().lower()
            return response in ('y', 'yes')
        except (EOFError, KeyboardInterrupt):
            return False
    
    def _register_rollback(self, action: callable) -> None:
        """Register a rollback action."""
        self._rollback_actions.append(action)
    
    def _perform_rollback(self) -> None:
        """Perform rollback actions in reverse order."""
        self.console.print("[yellow]Performing rollback...[/yellow]")
        
        for action in reversed(self._rollback_actions):
            try:
                action()
            except Exception as e:
                logger.warning(f"Rollback action failed: {e}")
    
    def _create_configuration_backup(self) -> Optional[Path]:
        """Create backup of user configuration."""
        config_dir = Path.home() / '.task_orchestrator'
        if not config_dir.exists():
            return None
        
        timestamp = int(time.time())
        backup_dir = config_dir.with_suffix(f'.backup.{timestamp}')
        
        try:
            shutil.copytree(config_dir, backup_dir)
            return backup_dir
        except Exception as e:
            logger.warning(f"Failed to create configuration backup: {e}")
            return None
    
    def _restore_configuration_backup(self, backup_path: Path) -> None:
        """Restore configuration from backup."""
        config_dir = Path.home() / '.task_orchestrator'
        
        if config_dir.exists():
            shutil.rmtree(config_dir)
        
        shutil.copytree(backup_path, config_dir)
    
    def _remove_all_configuration(self) -> None:
        """Remove all configuration and user data."""
        config_dir = Path.home() / '.task_orchestrator'
        if config_dir.exists():
            shutil.rmtree(config_dir)
            self.console.print("[yellow]Removed all configuration data[/yellow]")
    
    def _remove_configuration_only(self) -> None:
        """Remove only configuration files, preserve data."""
        config_dir = Path.home() / '.task_orchestrator'
        if config_dir.exists():
            # Remove config files but preserve data directories
            for item in config_dir.iterdir():
                if item.is_file() and item.suffix in ['.json', '.yaml', '.toml']:
                    item.unlink()
                    self.console.print(f"[yellow]Removed config file: {item.name}[/yellow]")
    
    def _show_next_steps(self) -> None:
        """Show next steps after successful installation."""
        self.console.print("\n[bold green]Next Steps:[/bold green]")
        
        if self.config.scope == InstallationScope.PROJECT:
            self.console.print("  1. Activate the virtual environment:")
            if os.name == 'nt':
                self.console.print("     .\\venv\\Scripts\\activate")
            else:
                self.console.print("     source venv/bin/activate")
        
        self.console.print("  2. Test the installation:")
        self.console.print("     mcp-task-orchestrator --help")
        
        if self.config.configure_clients:
            self.console.print("  3. Restart your MCP clients to use the new configuration")
        
        self.console.print("\nFor documentation and examples, visit:")
        self.console.print("https://github.com/EchoingVesper/mcp-task-orchestrator")


