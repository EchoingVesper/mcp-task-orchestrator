"""
Data models for the Universal Installer system.

This module defines the core data structures used throughout the installer,
including configuration, environment state, and operation types.
"""

import os
import sys
import subprocess
import shutil
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any, ClassVar
from enum import Enum
import time


class InstallationScope(Enum):
    """Installation scope options."""
    PROJECT = "project"      # ./venv/ in current directory
    USER = "user"           # ~/.local/bin
    SYSTEM = "system"       # System-wide installation
    CUSTOM = "custom"       # User-specified path


class InstallationSource(Enum):
    """Installation source options."""
    AUTO = "auto"           # Auto-detect based on mode
    PYPI = "pypi"          # PyPI package
    LOCAL = "local"        # Local directory (editable)
    GIT = "git"            # Git repository
    VERSION = "version"    # Specific PyPI version


class OperationType(Enum):
    """Type of operation to perform."""
    INSTALL = "install"
    UNINSTALL = "uninstall"
    REINSTALL = "reinstall"
    UPDATE = "update"
    VERIFY = "verify"
    REPAIR = "repair"
    STATUS = "status"


@dataclass
class InstallerConfig:
    """Configuration for the universal installer."""
    operation: OperationType
    scope: InstallationScope
    source: InstallationSource
    
    # Installation options
    dev_mode: bool = False
    custom_path: Optional[Path] = None
    version: Optional[str] = None
    git_url: Optional[str] = None
    
    # MCP client options
    configure_clients: bool = True
    specific_clients: Optional[List[str]] = None
    
    # Behavior options
    dry_run: bool = False
    verbose: bool = False
    force: bool = False
    preserve_config: bool = True
    create_backup: bool = True
    
    # Cleanup options
    purge_config: bool = False
    config_only: bool = False
    
    # Auto-detection cache
    _detected_context: Optional[Dict[str, Any]] = field(default=None, init=False)
    
    @classmethod
    def from_args(cls, args) -> 'InstallerConfig':
        """Create InstallerConfig from parsed command-line arguments."""
        # Determine operation
        operation = OperationType.INSTALL  # default
        if getattr(args, 'uninstall', False):
            operation = OperationType.UNINSTALL
        elif getattr(args, 'reinstall', False):
            operation = OperationType.REINSTALL
        elif getattr(args, 'update', False):
            operation = OperationType.UPDATE
        elif getattr(args, 'verify', False):
            operation = OperationType.VERIFY
        elif getattr(args, 'repair', False):
            operation = OperationType.REPAIR
        elif getattr(args, 'status', False):
            operation = OperationType.STATUS
        
        # Determine installation scope
        scope = InstallationScope.PROJECT  # default
        if getattr(args, 'user', False):
            scope = InstallationScope.USER
        elif getattr(args, 'system', False):
            scope = InstallationScope.SYSTEM
        elif getattr(args, 'venv', None):
            scope = InstallationScope.CUSTOM
        
        # Determine installation source
        source = InstallationSource.AUTO  # default
        if getattr(args, 'source', None):
            source = InstallationSource(args.source)
        elif getattr(args, 'version', None):
            source = InstallationSource.VERSION
        elif getattr(args, 'git', None):
            source = InstallationSource.GIT
        
        # Handle client configuration
        configure_clients = not getattr(args, 'no_clients', False)
        specific_clients = None
        if hasattr(args, 'clients') and args.clients:
            if args.clients == 'all':
                specific_clients = None  # Configure all detected
            else:
                specific_clients = [c.strip() for c in args.clients.split(',')]
        
        return cls(
            operation=operation,
            scope=scope,
            source=source,
            dev_mode=getattr(args, 'dev', False),
            custom_path=Path(args.venv) if getattr(args, 'venv', None) else None,
            version=getattr(args, 'version', None),
            git_url=getattr(args, 'git', None),
            configure_clients=configure_clients,
            specific_clients=specific_clients,
            dry_run=getattr(args, 'dry_run', False),
            verbose=getattr(args, 'verbose', False),
            force=getattr(args, 'force', False),
            preserve_config=not getattr(args, 'purge', False),
            create_backup=getattr(args, 'backup_only', False) or not getattr(args, 'no_backup', False),
            purge_config=getattr(args, 'purge', False),
            config_only=getattr(args, 'config', False),
        )
    
    def detect_context(self) -> Dict[str, Any]:
        """Detect installation context and cache results."""
        if self._detected_context is not None:
            return self._detected_context
        
        context = {
            'is_dev_environment': self._is_dev_environment(),
            'has_pyproject_toml': (Path.cwd() / 'pyproject.toml').exists(),
            'has_setup_py': (Path.cwd() / 'setup.py').exists(),
            'in_git_repo': self._is_git_repo(),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
            'platform': sys.platform,
            'venv_active': hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix),
        }
        
        self._detected_context = context
        return context
    
    def _is_dev_environment(self) -> bool:
        """Check if we're in a development environment."""
        cwd = Path.cwd()
        # Check for development indicators
        dev_indicators = [
            'pyproject.toml',
            'setup.py',
            'requirements.txt',
            'mcp_task_orchestrator',
            '.git'
        ]
        return any((cwd / indicator).exists() for indicator in dev_indicators)
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is in a git repository."""
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                         check=True, capture_output=True, cwd=Path.cwd())
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def auto_detect_optimal_settings(self) -> None:
        """Auto-detect and apply optimal settings based on environment."""
        context = self.detect_context()
        
        # Auto-adjust source based on environment
        if self.source == InstallationSource.AUTO:
            if context['is_dev_environment'] and context['in_git_repo']:
                self.source = InstallationSource.LOCAL
                self.dev_mode = True
            else:
                self.source = InstallationSource.PYPI
        
        # Auto-adjust scope for development
        if self.scope == InstallationScope.PROJECT and context['is_dev_environment']:
            # Development environments benefit from project-scoped installation
            pass  # Keep project scope
        elif self.scope == InstallationScope.PROJECT and not context['venv_active']:
            # Non-dev environments might benefit from user scope
            if not self.force:
                self.scope = InstallationScope.USER


@dataclass
class InstallationEnvironment:
    """Virtual environment and installation information."""
    path: Path
    python_exe: Path
    pip_exe: Path
    exists: bool
    is_valid: bool
    installed_packages: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def detect(cls, path: Path) -> 'InstallationEnvironment':
        """Detect and validate an installation environment."""
        exists = path.exists()
        
        # Determine Python executable path (cross-platform)
        if os.name == 'nt':  # Windows
            python_exe = path / 'Scripts' / 'python.exe'
            pip_exe = path / 'Scripts' / 'pip.exe'
        else:  # Unix-like
            python_exe = path / 'bin' / 'python'
            pip_exe = path / 'bin' / 'pip'
        
        is_valid = exists and cls._validate_environment(python_exe)
        
        installed_packages = {}
        if is_valid:
            installed_packages = cls._get_installed_packages(python_exe)
        
        return cls(
            path=path,
            python_exe=python_exe,
            pip_exe=pip_exe,
            exists=exists,
            is_valid=is_valid,
            installed_packages=installed_packages
        )
    
    @staticmethod
    def _validate_environment(python_exe: Path) -> bool:
        """Validate that the Python environment is functional."""
        if not python_exe.exists():
            return False
        
        try:
            result = subprocess.run(
                [str(python_exe), '-c', 'import sys; print(sys.executable)'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    @staticmethod
    def _get_installed_packages(python_exe: Path) -> Dict[str, str]:
        """Get list of installed packages and their versions."""
        try:
            result = subprocess.run(
                [str(python_exe), '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return {pkg['name']: pkg['version'] for pkg in packages}
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError, json.JSONDecodeError):
            pass
        
        return {}
    
    def has_package(self, package_name: str) -> bool:
        """Check if a specific package is installed."""
        return package_name.lower() in [name.lower() for name in self.installed_packages.keys()]
    
    def get_package_version(self, package_name: str) -> Optional[str]:
        """Get version of a specific package if installed."""
        for name, version in self.installed_packages.items():
            if name.lower() == package_name.lower():
                return version
        return None


@dataclass
class InstallationStatus:
    """Current installation status."""
    is_installed: bool
    installation_method: Optional[str] = None
    version: Optional[str] = None
    location: Optional[Path] = None
    clients_configured: List[str] = field(default_factory=list)
    configuration_valid: bool = False
    last_modified: Optional[str] = None
    environment: Optional[InstallationEnvironment] = None
    
    @classmethod
    def detect_current_installation(cls) -> 'InstallationStatus':
        """Detect current installation status across all possible locations."""
        status = cls(is_installed=False)
        
        # Try to import the package to check if it's installed
        try:
            import mcp_task_orchestrator
            status.is_installed = True
            status.version = getattr(mcp_task_orchestrator, '__version__', 'unknown')
            
            # Try to find installation location
            import importlib.util
            spec = importlib.util.find_spec('mcp_task_orchestrator')
            if spec and spec.origin:
                status.location = Path(spec.origin).parent
                
                # Check if it's an editable install
                if status.location and status.location.name == 'mcp_task_orchestrator':
                    # Likely editable install
                    status.installation_method = 'editable'
                else:
                    status.installation_method = 'package'
                    
        except ImportError:
            pass
        
        # Check for local virtual environment
        venv_path = Path.cwd() / 'venv'
        if venv_path.exists():
            env = InstallationEnvironment.detect(venv_path)
            if env.is_valid and env.has_package('mcp-task-orchestrator'):
                status.is_installed = True
                status.environment = env
                status.installation_method = 'venv'
                if not status.version:
                    status.version = env.get_package_version('mcp-task-orchestrator')
        
        # TODO: Detect MCP client configurations
        status.clients_configured = cls._detect_configured_clients()
        
        return status
    
    @staticmethod
    def _detect_configured_clients() -> List[str]:
        """Detect which MCP clients are currently configured."""
        configured = []
        
        # Check Claude Desktop
        claude_configs = [
            Path.home() / '.config' / 'claude' / 'claude_desktop_config.json',
            Path(os.environ.get('APPDATA', '')) / 'Claude' / 'config.json' if os.name == 'nt' else None
        ]
        
        for config_path in claude_configs:
            if config_path and config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        if 'mcpServers' in config and 'task-orchestrator' in config['mcpServers']:
                            configured.append('claude_desktop')
                            break
                except (json.JSONDecodeError, OSError):
                    continue
        
        # TODO: Add detection for other clients (Cursor, VS Code, etc.)
        
        return configured
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert status to dictionary for JSON serialization."""
        return {
            'is_installed': self.is_installed,
            'installation_method': self.installation_method,
            'version': self.version,
            'location': str(self.location) if self.location else None,
            'clients_configured': self.clients_configured,
            'configuration_valid': self.configuration_valid,
            'last_modified': self.last_modified,
            'environment_valid': self.environment.is_valid if self.environment else None
        }


class InstallationError(Exception):
    """Base exception for installation-related errors."""
    pass


class EnvironmentError(InstallationError):
    """Exception for virtual environment related errors."""
    pass


class PackageInstallationError(InstallationError):
    """Exception for package installation errors."""
    pass


class ClientConfigurationError(InstallationError):
    """Exception for MCP client configuration errors."""
    pass


class ValidationError(InstallationError):
    """Exception for validation failures."""
    pass