"""
Source management for the Universal Installer.

This module handles package installation from various sources including
PyPI, local directories, git repositories, and specific versions.
"""

import os
import sys
import subprocess
import shutil
import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import logging
import urllib.request
import urllib.error

from .models import (
    InstallerConfig,
    InstallationStatus,
    InstallationScope,
    InstallationSource,
    PackageInstallationError,
    InstallationError
)

logger = logging.getLogger(__name__)


class SourceManager:
    """Manages package installation from various sources."""
    
    def __init__(self, config: InstallerConfig, console=None):
        self.config = config
        self.console = console
        self._package_manager = None
    
    def install_package(self) -> None:
        """Install package from configured source."""
        if self.config.dry_run:
            self._show_dry_run_install()
            return
        
        package_manager = self._get_package_manager()
        
        if self.config.source == InstallationSource.LOCAL:
            self._install_local_package(package_manager)
        elif self.config.source == InstallationSource.PYPI:
            self._install_pypi_package(package_manager)
        elif self.config.source == InstallationSource.VERSION:
            self._install_version_package(package_manager)
        elif self.config.source == InstallationSource.GIT:
            self._install_git_package(package_manager)
        else:
            raise PackageInstallationError(f"Unsupported source: {self.config.source}")
    
    def uninstall_package(self, status: InstallationStatus) -> None:
        """Uninstall package based on current installation status."""
        if self.config.dry_run:
            self.console.print("[dim]Dry run: Would uninstall package[/dim]")
            return
        
        package_manager = self._get_package_manager()
        
        if status.installation_method == 'venv':
            # Remove virtual environment
            if status.environment and status.environment.path.exists():
                self.console.print(f"[yellow]Removing virtual environment: {status.environment.path}[/yellow]")
                shutil.rmtree(status.environment.path)
        else:
            # Uninstall package using package manager
            self._uninstall_with_package_manager(package_manager)
    
    def update_package(self) -> None:
        """Update package to latest version."""
        if self.config.dry_run:
            self.console.print("[dim]Dry run: Would update package to latest version[/dim]")
            return
        
        package_manager = self._get_package_manager()
        
        # Force upgrade to latest version
        cmd = self._build_install_command(package_manager, force_upgrade=True)
        self._execute_package_command(cmd, "Updating package")
    
    def get_latest_version(self) -> str:
        """Get latest version available from PyPI."""
        try:
            # Query PyPI API for latest version
            with urllib.request.urlopen('https://pypi.org/pypi/mcp-task-orchestrator/json') as response:
                data = json.loads(response.read().decode())
                return data['info']['version']
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not fetch latest version: {e}")
            return "unknown"
    
    def _show_dry_run_install(self) -> None:
        """Show what would be done in dry run mode."""
        package_manager = self._get_package_manager()
        
        if self.config.source == InstallationSource.LOCAL:
            self.console.print(f"[dim]Dry run: Would install local package using {package_manager}[/dim]")
            self.console.print(f"[dim]  Source: {Path.cwd()}[/dim]")
            self.console.print(f"[dim]  Editable: {self.config.dev_mode}[/dim]")
        elif self.config.source == InstallationSource.PYPI:
            self.console.print(f"[dim]Dry run: Would install from PyPI using {package_manager}[/dim]")
            self.console.print(f"[dim]  Package: mcp-task-orchestrator[/dim]")
        elif self.config.source == InstallationSource.VERSION:
            self.console.print(f"[dim]Dry run: Would install version {self.config.version} using {package_manager}[/dim]")
        elif self.config.source == InstallationSource.GIT:
            self.console.print(f"[dim]Dry run: Would install from git using {package_manager}[/dim]")
            self.console.print(f"[dim]  Repository: {self.config.git_url}[/dim]")
    
    def _install_local_package(self, package_manager: str) -> None:
        """Install package from local directory."""
        project_root = Path.cwd()
        
        # Verify we're in the right directory
        if not (project_root / 'pyproject.toml').exists() and not (project_root / 'setup.py').exists():
            raise PackageInstallationError(
                "No pyproject.toml or setup.py found. "
                "Please run from the project root directory."
            )
        
        self.console.print(f"[cyan]Installing from local directory: {project_root}[/cyan]")
        
        # Build install command
        cmd = self._build_local_install_command(package_manager, project_root)
        self._execute_package_command(cmd, "Installing local package")
    
    def _install_pypi_package(self, package_manager: str) -> None:
        """Install package from PyPI."""
        self.console.print("[cyan]Installing from PyPI...[/cyan]")
        
        cmd = self._build_pypi_install_command(package_manager)
        self._execute_package_command(cmd, "Installing PyPI package")
    
    def _install_version_package(self, package_manager: str) -> None:
        """Install specific version from PyPI."""
        self.console.print(f"[cyan]Installing version {self.config.version} from PyPI...[/cyan]")
        
        cmd = self._build_version_install_command(package_manager)
        self._execute_package_command(cmd, f"Installing version {self.config.version}")
    
    def _install_git_package(self, package_manager: str) -> None:
        """Install package from git repository."""
        self.console.print(f"[cyan]Installing from git repository: {self.config.git_url}[/cyan]")
        
        cmd = self._build_git_install_command(package_manager)
        self._execute_package_command(cmd, "Installing git package")
    
    def _build_local_install_command(self, package_manager: str, project_root: Path) -> List[str]:
        """Build command for local installation."""
        # Debug dev_mode status first
        if self.config.verbose:
            self.console.print(f"[dim]Dev mode status: {self.config.dev_mode}[/dim]")
            self.console.print(f"[dim]Dev mode type: {type(self.config.dev_mode)}[/dim]")
        
        if package_manager == 'uv':
            # For uv in virtual environments, we need to specify the Python interpreter
            python_exe = self._get_python_executable()
            cmd = ['uv', 'pip', 'install', '--python', str(python_exe)]
            
            # Double-check dev_mode with explicit boolean conversion
            is_dev = bool(self.config.dev_mode)
            if self.config.verbose:
                self.console.print(f"[dim]Is dev (bool): {is_dev}[/dim]")
            
            if is_dev:
                # For editable installs with extras, need to use proper syntax: -e ".[dev]"
                if self.config.verbose:
                    self.console.print(f"[dim]Package spec with dev: .[dev][/dim]")
                cmd.extend(['-e', '.[dev]'])
            else:
                if self.config.verbose:
                    self.console.print(f"[dim]Package spec without dev: .[/dim]")
                cmd.extend(['-e', '.'])
        else:  # pip
            python_exe = self._get_python_executable()
            cmd = [str(python_exe), '-m', 'pip', 'install']
            if self.config.dev_mode:
                cmd.extend(['-e', f"{project_root}[dev]"])
            else:
                cmd.extend(['-e', str(project_root)])
        
        # Debug output for verbose mode
        if self.config.verbose:
            dev_mode_str = "with dev dependencies" if self.config.dev_mode else "without dev dependencies"
            self.console.print(f"[dim]Final install command ({dev_mode_str}): {' '.join(cmd)}[/dim]")
        
        return [x for x in cmd if x]  # Remove empty strings
    
    def _build_pypi_install_command(self, package_manager: str) -> List[str]:
        """Build command for PyPI installation."""
        package_spec = 'mcp-task-orchestrator'
        if self.config.dev_mode:
            package_spec += '[dev]'
        
        if package_manager == 'uv':
            python_exe = self._get_python_executable()
            cmd = ['uv', 'pip', 'install', '--python', str(python_exe), package_spec]
        else:  # pip
            python_exe = self._get_python_executable()
            cmd = [str(python_exe), '-m', 'pip', 'install', package_spec]
        
        return cmd
    
    def _build_version_install_command(self, package_manager: str) -> List[str]:
        """Build command for specific version installation."""
        package_spec = f'mcp-task-orchestrator=={self.config.version}'
        if self.config.dev_mode:
            package_spec = f'mcp-task-orchestrator[dev]=={self.config.version}'
        
        if package_manager == 'uv':
            python_exe = self._get_python_executable()
            cmd = ['uv', 'pip', 'install', '--python', str(python_exe), package_spec]
        else:  # pip
            python_exe = self._get_python_executable()
            cmd = [str(python_exe), '-m', 'pip', 'install', package_spec]
        
        return cmd
    
    def _build_git_install_command(self, package_manager: str) -> List[str]:
        """Build command for git installation."""
        git_spec = self.config.git_url
        if self.config.dev_mode:
            git_spec += '#egg=mcp-task-orchestrator[dev]'
        
        if package_manager == 'uv':
            python_exe = self._get_python_executable()
            cmd = ['uv', 'pip', 'install', '--python', str(python_exe), 'git+' + git_spec]
        else:  # pip
            python_exe = self._get_python_executable()
            cmd = [str(python_exe), '-m', 'pip', 'install', 'git+' + git_spec]
        
        return cmd
    
    def _build_install_command(self, package_manager: str, force_upgrade: bool = False) -> List[str]:
        """Build generic install command."""
        package_spec = 'mcp-task-orchestrator'
        if self.config.dev_mode:
            package_spec += '[dev]'
        
        if package_manager == 'uv':
            python_exe = self._get_python_executable()
            cmd = ['uv', 'pip', 'install', '--python', str(python_exe)]
            if force_upgrade:
                cmd.append('--upgrade')
            cmd.append(package_spec)
        else:  # pip
            python_exe = self._get_python_executable()
            cmd = [str(python_exe), '-m', 'pip', 'install']
            if force_upgrade:
                cmd.append('--upgrade')
            cmd.append(package_spec)
        
        return cmd
    
    def _uninstall_with_package_manager(self, package_manager: str) -> None:
        """Uninstall package using package manager."""
        self.console.print("[yellow]Uninstalling package...[/yellow]")
        
        if package_manager == 'uv':
            python_exe = self._get_python_executable()
            cmd = ['uv', 'pip', 'uninstall', '--python', str(python_exe), 'mcp-task-orchestrator']
        else:  # pip
            python_exe = self._get_python_executable()
            cmd = [str(python_exe), '-m', 'pip', 'uninstall', '-y', 'mcp-task-orchestrator']
        
        self._execute_package_command(cmd, "Uninstalling package")
    
    def _execute_package_command(self, cmd: List[str], description: str) -> None:
        """Execute package management command."""
        if self.config.verbose:
            self.console.print(f"[dim]Command: {' '.join(cmd)}[/dim]")
        
        try:
            # Set environment for virtual environment if needed
            env = os.environ.copy()
            
            # Fix WSL hardlink issues with uv
            env['UV_LINK_MODE'] = 'copy'
            
            if self.config.scope in [InstallationScope.PROJECT, InstallationScope.CUSTOM]:
                venv_path = self._get_venv_path()
                if venv_path:
                    # For uv, we need to specify the virtual environment explicitly
                    # Set VIRTUAL_ENV for uv to use the correct environment
                    env['VIRTUAL_ENV'] = str(venv_path)
                    
                    if os.name == 'nt':
                        env['PATH'] = f"{venv_path / 'Scripts'}{os.pathsep}{env['PATH']}"
                    else:
                        env['PATH'] = f"{venv_path / 'bin'}{os.pathsep}{env['PATH']}"
                    
                    if self.config.verbose:
                        self.console.print(f"[dim]Using virtual environment: {venv_path}[/dim]")
            
            # Set cwd to project root for local installs  
            cwd = None
            if self.config.source == InstallationSource.LOCAL:
                cwd = Path.cwd()
                if self.config.verbose:
                    self.console.print(f"[dim]Working directory: {cwd}[/dim]")
                    
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
                env=env,
                cwd=cwd
            )
            
            if self.config.verbose and result.stdout:
                self.console.print(f"[dim]Output: {result.stdout.strip()}[/dim]")
            
            # Check for warnings in output
            if result.stderr:
                warnings = self._extract_warnings(result.stderr)
                for warning in warnings:
                    self.console.print(f"[yellow]Warning: {warning}[/yellow]")
            
        except subprocess.CalledProcessError as e:
            error_msg = f"{description} failed"
            if e.stderr:
                error_msg += f": {e.stderr.strip()}"
            raise PackageInstallationError(error_msg)
        except subprocess.TimeoutExpired:
            raise PackageInstallationError(f"{description} timed out after 5 minutes")
    
    def _extract_warnings(self, stderr: str) -> List[str]:
        """Extract meaningful warnings from stderr output."""
        warnings = []
        lines = stderr.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if 'WARNING' in line.upper() or 'WARN' in line.upper():
                # Clean up common warning patterns
                clean_line = re.sub(r'^WARNING:?\s*', '', line, flags=re.IGNORECASE)
                if clean_line and len(clean_line) > 10:  # Ignore very short warnings
                    warnings.append(clean_line)
        
        return warnings
    
    def _get_package_manager(self) -> str:
        """Get best available package manager."""
        if self._package_manager:
            return self._package_manager
        
        # Prefer uv for speed, fallback to pip
        if shutil.which('uv'):
            self._package_manager = 'uv'
        elif shutil.which('pip'):
            self._package_manager = 'pip'
        else:
            raise PackageInstallationError("No package manager available (pip or uv required)")
        
        if self.config.verbose:
            self.console.print(f"[green]Using package manager: {self._package_manager}[/green]")
        
        return self._package_manager
    
    def _get_python_executable(self) -> Path:
        """Get Python executable for current scope."""
        if self.config.scope in [InstallationScope.PROJECT, InstallationScope.CUSTOM]:
            venv_path = self._get_venv_path()
            if venv_path:
                if os.name == 'nt':
                    return venv_path / 'Scripts' / 'python.exe'
                else:
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
    
    def verify_installation(self) -> bool:
        """Verify that the package was installed correctly."""
        try:
            python_exe = self._get_python_executable()
            
            # Try to import the package
            result = subprocess.run(
                [str(python_exe), '-c', 'import mcp_task_orchestrator; print("OK")'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and "OK" in result.stdout:
                return True
            else:
                logger.error(f"Import test failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Installation verification failed: {e}")
            return False
    
    def get_installed_version(self) -> Optional[str]:
        """Get version of installed package."""
        try:
            python_exe = self._get_python_executable()
            
            result = subprocess.run(
                [str(python_exe), '-c', 
                 'import mcp_task_orchestrator; print(getattr(mcp_task_orchestrator, "__version__", "unknown"))'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
                
        except Exception as e:
            logger.warning(f"Could not get installed version: {e}")
        
        return None