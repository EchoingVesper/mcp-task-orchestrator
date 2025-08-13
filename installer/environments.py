"""
Environment management for the Universal Installer.

This module handles virtual environment creation, validation, and management
across different platforms and installation scopes.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, List
import logging

from .models import (
    InstallerConfig,
    InstallationEnvironment,
    InstallationScope,
    EnvironmentError,
    InstallationError
)

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """Manages virtual environments across platforms."""
    
    def __init__(self, config: InstallerConfig, console=None):
        self.config = config
        self.console = console
    
    def prepare_environment(self) -> None:
        """Prepare the installation environment."""
        if self.config.dry_run:
            self.console.print("[dim]Dry run: Would prepare installation environment[/dim]")
            return
        
        # Check Python version compatibility
        self._validate_python_version()
        
        # Check for externally managed environment
        if self._is_externally_managed():
            if self.config.scope == InstallationScope.SYSTEM:
                raise EnvironmentError(
                    "This Python installation is externally managed. "
                    "Use --user or --venv instead of --system."
                )
        
        # Validate package managers
        self._validate_package_managers()
    
    def create_or_validate_environment(self) -> InstallationEnvironment:
        """Create or validate virtual environment based on scope."""
        if self.config.scope == InstallationScope.PROJECT:
            return self._handle_project_environment()
        elif self.config.scope == InstallationScope.CUSTOM:
            return self._handle_custom_environment()
        else:
            # User/system scope doesn't use virtual environments
            return self._get_system_environment()
    
    def cleanup_environment(self, env: InstallationEnvironment) -> None:
        """Clean up environment on installation failure."""
        if self.config.dry_run:
            self.console.print(f"[dim]Dry run: Would clean up environment at {env.path}[/dim]")
            return
        
        if env.path.exists() and env.path.name == 'venv':
            # Only remove if it's a standard venv directory
            try:
                shutil.rmtree(env.path)
                self.console.print(f"[yellow]Cleaned up failed environment: {env.path}[/yellow]")
            except Exception as e:
                logger.warning(f"Failed to cleanup environment: {e}")
    
    def _handle_project_environment(self) -> InstallationEnvironment:
        """Handle project-scoped virtual environment."""
        venv_path = Path.cwd() / 'venv'
        
        # Check existing environment
        if venv_path.exists():
            env = InstallationEnvironment.detect(venv_path)
            if env.is_valid:
                if not self.config.force:
                    self.console.print(f"[green]Using existing virtual environment: {venv_path}[/green]")
                    return env
                else:
                    self.console.print("[yellow]Recreating virtual environment (--force specified)[/yellow]")
                    self._remove_environment(venv_path)
            else:
                self.console.print("[yellow]Removing invalid virtual environment[/yellow]")
                self._remove_environment(venv_path)
        
        # Create new environment
        return self._create_virtual_environment(venv_path)
    
    def _handle_custom_environment(self) -> InstallationEnvironment:
        """Handle custom virtual environment path."""
        venv_path = self.config.custom_path
        
        if venv_path.exists():
            env = InstallationEnvironment.detect(venv_path)
            if env.is_valid and not self.config.force:
                self.console.print(f"[green]Using existing virtual environment: {venv_path}[/green]")
                return env
            elif self.config.force:
                self.console.print("[yellow]Recreating virtual environment (--force specified)[/yellow]")
                self._remove_environment(venv_path)
            else:
                raise EnvironmentError(f"Invalid virtual environment at {venv_path}")
        
        # Create new environment at custom path
        return self._create_virtual_environment(venv_path)
    
    def _get_system_environment(self) -> InstallationEnvironment:
        """Get system environment information."""
        # For user/system installations, use the current Python environment
        python_exe = Path(sys.executable)
        pip_exe = self._find_pip_executable(python_exe)
        
        return InstallationEnvironment(
            path=python_exe.parent.parent,  # Approximate system path
            python_exe=python_exe,
            pip_exe=pip_exe,
            exists=True,
            is_valid=True,
            installed_packages=self._get_installed_packages(python_exe)
        )
    
    def _create_virtual_environment(self, venv_path: Path) -> InstallationEnvironment:
        """Create a new virtual environment."""
        if self.config.dry_run:
            self.console.print(f"[dim]Dry run: Would create virtual environment at {venv_path}[/dim]")
            # Return a mock environment for dry run
            return InstallationEnvironment(
                path=venv_path,
                python_exe=venv_path / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python'),
                pip_exe=venv_path / ('Scripts/pip.exe' if os.name == 'nt' else 'bin/pip'),
                exists=False,
                is_valid=True,
                installed_packages={}
            )
        
        self.console.print(f"[cyan]Creating virtual environment at {venv_path}...[/cyan]")
        
        try:
            # Create the virtual environment
            cmd = [sys.executable, '-m', 'venv', str(venv_path)]
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if self.config.verbose:
                self.console.print(f"[dim]Command: {' '.join(cmd)}[/dim]")
                if result.stdout:
                    self.console.print(f"[dim]Output: {result.stdout.strip()}[/dim]")
            
        except subprocess.CalledProcessError as e:
            raise EnvironmentError(f"Failed to create virtual environment: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise EnvironmentError("Virtual environment creation timed out")
        
        # Detect and validate the new environment
        env = InstallationEnvironment.detect(venv_path)
        if not env.is_valid:
            raise EnvironmentError("Created virtual environment is not functional")
        
        # Upgrade pip immediately
        self._upgrade_pip(env)
        
        return env
    
    def _upgrade_pip(self, env: InstallationEnvironment) -> None:
        """Upgrade pip in the virtual environment."""
        self.console.print("[cyan]Upgrading pip...[/cyan]")
        
        try:
            cmd = [str(env.python_exe), '-m', 'pip', 'install', '--upgrade', 'pip']
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if self.config.verbose:
                self.console.print(f"[dim]Command: {' '.join(cmd)}[/dim]")
                if result.stdout:
                    self.console.print(f"[dim]Output: {result.stdout.strip()}[/dim]")
                    
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to upgrade pip: {e.stderr}")
            # Don't fail the installation for pip upgrade failures
        except subprocess.TimeoutExpired:
            logger.warning("Pip upgrade timed out")
    
    def _remove_environment(self, venv_path: Path) -> None:
        """Remove an existing virtual environment."""
        try:
            if venv_path.exists():
                shutil.rmtree(venv_path)
        except Exception as e:
            raise EnvironmentError(f"Failed to remove existing environment: {e}")
    
    def _validate_python_version(self) -> None:
        """Validate Python version compatibility."""
        min_version = (3, 8)
        current_version = sys.version_info[:2]
        
        if current_version < min_version:
            raise EnvironmentError(
                f"Python {min_version[0]}.{min_version[1]}+ is required, "
                f"but you have Python {current_version[0]}.{current_version[1]}"
            )
        
        if self.config.verbose:
            self.console.print(f"[green]✓ Python {current_version[0]}.{current_version[1]} is compatible[/green]")
    
    def _is_externally_managed(self) -> bool:
        """Check if Python installation is externally managed."""
        # Check for EXTERNALLY-MANAGED file (PEP 668)
        stdlib_path = Path(sys.executable).parent.parent / 'lib'
        for python_dir in stdlib_path.glob('python*'):
            externally_managed = python_dir / 'EXTERNALLY-MANAGED'
            if externally_managed.exists():
                return True
        
        # Check for common package manager indicators
        # This is a heuristic check for package manager installations
        if 'site-packages' in str(Path(sys.executable)):
            return False  # Likely a user installation
        
        # Check for Debian/Ubuntu package manager
        if Path('/usr/lib/python*/dist-packages').exists():
            return sys.executable.startswith('/usr/bin/python')
        
        return False
    
    def _validate_package_managers(self) -> None:
        """Validate available package managers."""
        managers = self._detect_package_managers()
        
        if not managers:
            raise EnvironmentError(
                "No package manager found. Please install pip or uv.\n"
                "Visit https://pip.pypa.io/en/stable/installation/ for pip installation."
            )
        
        if self.config.verbose:
            self.console.print(f"[green]✓ Package managers available: {', '.join(managers)}[/green]")
    
    def _detect_package_managers(self) -> List[str]:
        """Detect available package managers."""
        managers = []
        for manager in ['uv', 'pip', 'pipx']:
            if shutil.which(manager):
                managers.append(manager)
        return managers
    
    def _find_pip_executable(self, python_exe: Path) -> Path:
        """Find pip executable for given Python executable."""
        # Try pip in same directory first
        if os.name == 'nt':
            pip_exe = python_exe.parent / 'pip.exe'
        else:
            pip_exe = python_exe.parent / 'pip'
        
        if pip_exe.exists():
            return pip_exe
        
        # Try using python -m pip
        try:
            result = subprocess.run(
                [str(python_exe), '-m', 'pip', '--version'],
                check=True,
                capture_output=True,
                timeout=10
            )
            # If this works, we can use python -m pip
            return python_exe  # We'll use -m pip with this
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        
        # Last resort: system pip
        system_pip = shutil.which('pip')
        if system_pip:
            return Path(system_pip)
        
        raise EnvironmentError("Could not find pip executable")
    
    def _get_installed_packages(self, python_exe: Path) -> Dict[str, str]:
        """Get installed packages for a Python executable."""
        try:
            result = subprocess.run(
                [str(python_exe), '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                import json
                packages = json.loads(result.stdout)
                return {pkg['name']: pkg['version'] for pkg in packages}
        except Exception:
            pass
        
        return {}
    
    def get_venv_python_path(self, venv_path: Path) -> Path:
        """Get Python executable path for virtual environment."""
        if os.name == 'nt':  # Windows
            return venv_path / 'Scripts' / 'python.exe'
        else:  # Unix-like
            return venv_path / 'bin' / 'python'