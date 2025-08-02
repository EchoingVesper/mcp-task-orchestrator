
# Universal Installer/Uninstaller/Reinstaller Automation

**name**: "Universal Installer/Uninstaller/Reinstaller Automation"
**description**: "Comprehensive installation automation script for MCP Task Orchestrator supporting users and developers
=with industry best practices"

#
# Goal

Create a production-ready universal installation automation script (`install.py`) that manages the complete lifecycle
for the MCP Task Orchestrator project. The script should handle installation, uninstallation, and reinstallation for
both end users and developers with comprehensive mode support, following industry best practices from pipx, poetry, and uv.

#
# Why

- **Universal Access**: Single tool that serves both casual users and power developers

- **Industry Standards**: Follows modern Python packaging best practices and user expectations

- **Simplified Onboarding**: One-command installation with sensible defaults

- **Flexible Deployment**: Supports multiple installation scopes and configurations

- **Professional Experience**: Matches quality of tools like pipx, poetry, uv

- **Maintainable Codebase**: Reduces support burden with reliable, self-diagnosing installation

#
# What

A comprehensive Python script that provides universal installation lifecycle management with the following user-visible behavior:

#
## Command-Line Interface

```bash

# Default behavior - Project-scoped installation with auto-detected clients

./install.py                          
# Creates ./venv/, PyPI for users, local for devs

# Installation modes

./install.py --dev                    
# Developer mode: editable + dev dependencies + build tools
./install.py --user                  
# User-scoped (~/.local/bin)
./install.py --system                
# System-wide (requires admin privileges)
./install.py --venv /custom/path     
# Custom virtual environment location

# Source control

./install.py --source pypi           
# Force PyPI even for developers
./install.py --source local          
# Force local/editable install
./install.py --version 1.4.1         
# Specific PyPI version
./install.py --git https://github... 
# Git repository install

# MCP client integration

./install.py --clients all           
# Configure all detected clients (default)
./install.py --clients claude,cursor 
# Specific clients only
./install.py --no-clients           
# Skip MCP configuration entirely

# Uninstall and cleanup

./install.py --uninstall            
# Remove package, preserve config/data
./install.py --uninstall --purge    
# Remove everything including .task_orchestrator/
./install.py --uninstall --config   
# Remove only configuration files

# Reinstall strategies

./install.py --reinstall            
# Preserve config, clean package install
./install.py --reinstall --clean    
# Fresh install, backup then restore config
./install.py --reinstall --force    
# Nuclear option, overwrite everything

# Maintenance operations

./install.py --update               
# Upgrade existing installation
./install.py --verify               
# Check installation integrity
./install.py --repair               
# Fix broken installations
./install.py --status               
# Show current installation status

# Advanced options

./install.py --dry-run --verbose    
# Show what would be done
./install.py --backup-only          
# Create config backup without installing

```text

#
## Success Criteria

- [ ] **Multi-Mode Support**: Seamlessly handles user, developer, system, and custom installations

- [ ] **Source Flexibility**: Supports PyPI, local, git, and version-specific installations

- [ ] **Virtual Environment Management**: Always creates isolated environments (except user/system scope)

- [ ] **MCP Client Integration**: Automatically detects and configures supported MCP clients

- [ ] **Configuration Preservation**: Maintains user data and settings across operations

- [ ] **Cross-Platform Compatibility**: Works reliably on Windows, macOS, and Linux

- [ ] **Industry Standard UX**: Matches user expectations from modern Python tools

- [ ] **Comprehensive Error Handling**: Graceful failures with actionable recovery suggestions

- [ ] **Self-Diagnosis**: Built-in health checks and repair capabilities

- [ ] **Validation Gates**: All installation modes pass automated verification tests

#
# All Needed Context

#
## Documentation & References

```text
yaml

# MUST READ - Include these in your context window

- url: https://docs.python.org/3/library/venv.html
  why: Virtual environment creation patterns and cross-platform compatibility

- url: https://docs.python.org/3/library/argparse.html
  why: Professional command-line argument parsing and help generation

- url: https://packaging.python.org/en/latest/guides/
  why: Python packaging standards and best practices

- url: https://peps.python.org/pep-0518/
  why: Build system requirements and pyproject.toml standards

- url: https://docs.pipx.dev/docs/
  why: User-scoped application installation patterns and PATH management

- url: https://python-poetry.org/docs/
  why: Dependency management and virtual environment creation patterns

- url: https://docs.astral.sh/uv/
  why: Fast, reliable Python package installation and environment management

- file: /mnt/e/dev/mcp-servers/mcp-task-orchestrator/scripts/deployment/install.py
  why: Existing unified installer patterns and argument parsing structure

- file: /mnt/e/dev/mcp-servers/mcp-task-orchestrator/mcp_task_orchestrator_cli/cli.py
  why: CLI command structure, rich console patterns, and MCP client integration

- file: /mnt/e/dev/mcp-servers/mcp-task-orchestrator/mcp_task_orchestrator_cli/universal_installer.py
  why: Universal installer patterns and cross-platform client detection

- file: /mnt/e/dev/mcp-servers/mcp-task-orchestrator/mcp_task_orchestrator_cli/platforms/windows.py
  why: Windows-specific client path detection and configuration patterns

- file: /mnt/e/dev/mcp-servers/mcp-task-orchestrator/mcp_task_orchestrator_cli/platforms/linux.py
  why: Linux-specific client path detection and configuration patterns

- file: /mnt/e/dev/mcp-servers/mcp-task-orchestrator/mcp_task_orchestrator/infrastructure/error_handling/decorators.py
  why: Comprehensive error handling patterns with context and retry mechanisms

- file: /mnt/e/dev/mcp-servers/mcp-task-orchestrator/scripts/deployment/install_venv_simple.py
  why: Virtual environment creation and dependency installation patterns

- file: /mnt/e/dev/mcp-servers/mcp-task-orchestrator/setup.py
  why: Package configuration, dependencies, and entry point definitions

- file: /mnt/e/dev/mcp-servers/mcp-task-orchestrator/pyproject.toml
  why: Modern Python packaging configuration and dependency specifications

```text

#
## Current Codebase Structure

```text
bash
mcp-task-orchestrator/
├── install.py                                  
# [TARGET] Universal installer
├── scripts/
│   ├── deployment/
│   │   ├── install.py                          
# Existing unified installer patterns
│   │   └── install_venv_simple.py              
# Virtual environment creation patterns
│   ├── uninstall_orchestrator.py               
# Argument parsing and cleanup patterns
│   └── release/
│       └── pypi_release_simple.py              
# Build cleanup and subprocess execution
├── mcp_task_orchestrator_cli/
│   ├── cli.py                                  
# Rich console, Typer patterns, MCP integration
│   ├── universal_installer.py                  
# Cross-platform installer patterns
│   ├── platforms/
│   │   ├── windows.py                          
# Windows client detection
│   │   ├── linux.py                            
# Linux client detection
│   │   └── macos.py                            
# macOS client detection
│   └── __main__.py                             
# Safe entry point patterns
├── mcp_task_orchestrator/
│   ├── infrastructure/error_handling/
│   │   └── decorators.py                       
# Error handling and retry patterns
│   └── CLAUDE.md                               
# Core package documentation
├── setup.py                                    
# Package configuration patterns
├── pyproject.toml                              
# Modern dependency specifications
├── requirements.txt                            
# Runtime dependencies
└── tests/
    └── integration/
        └── test_real_implementations_simple.py 
# Integration testing patterns

```text

#
## Desired Codebase Structure

```text
bash
mcp-task-orchestrator/
├── install.py                                  
# Universal installer script
├── install.sh                                  
# Unix shell wrapper script
├── install.ps1                                 
# PowerShell wrapper script
├── installer/                                  
# Installer module (if needed)
│   ├── __init__.py
│   ├── core.py                                 
# Core installation logic
│   ├── platforms.py                            
# Platform-specific handling
│   ├── environments.py                         
# Virtual environment management
│   └── clients.py                              
# MCP client configuration
├── scripts/deployment/                         
# Existing deployment scripts (preserved)
└── tests/
    ├── test_universal_installer.py             
# Comprehensive installer tests
    └── integration/
        └── test_installer_integration.py       
# End-to-end installer testing

```text

#
## Known Gotchas of Codebase & Library Quirks

```text
python

# CRITICAL: Virtual environment Python executable paths

# Windows: venv/Scripts/python.exe, Unix: venv/bin/python
python_exe = venv_path / ("Scripts/python.exe" if os.name == 'nt' else "bin/python")

# CRITICAL: CLI entry points and import handling

# The CLI uses typer which requires rich dependencies

# Must check dependencies before attempting CLI operations

def check_cli_dependencies():
    """Check if CLI dependencies are available before use."""
    try:
        import typer
        import rich
        return True
    except ImportError:
        return False

# CRITICAL: MCP client configuration backup

# Always create timestamped backups before modifying client configs
backup_path = config_path.with_suffix(f".backup.{int(time.time())}.json")

# CRITICAL: Cross-platform path handling

# Use pathlib.Path for all file operations, avoid os.path

# Handle Windows vs Unix differences explicitly

from pathlib import Path
config_path = Path.home() / ".config" / "claude" / "config.json"  
# Unix
config_path = Path(os.environ.get("APPDATA", "")) / "Claude" / "config.json"  
# Windows

# CRITICAL: Package installation detection

# Check for existing installations before proceeding
def check_existing_installation():
    """Detect existing installations and their methods."""
    
# Check for pip-installed package
    
# Check for development installation
    
# Check for custom installations

# CRITICAL: Virtual environment validation

# Ensure virtual environment is valid and functional
def validate_venv(venv_path):
    """Validate virtual environment functionality."""
    python_exe = get_venv_python_path(venv_path)
    try:
        result = subprocess.run([str(python_exe), "-c", "import sys; print(sys.executable)"], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

# CRITICAL: Dependency management with uv preference

# Prefer uv for fast package management when available
def get_package_manager():
    """Get best available package manager."""
    if shutil.which("uv"):
        return "uv"
    elif shutil.which("pip"):
        return "pip"
    else:
        raise RuntimeError("No package manager available")

# CRITICAL: Configuration preservation during updates

# Preserve user configuration and data across reinstalls
def preserve_user_data(operation="reinstall"):
    """Create backup of user configuration before operations."""
    config_dir = Path.home() / ".task_orchestrator"
    if config_dir.exists():
        backup_dir = config_dir.with_suffix(f".backup.{int(time.time())}")
        shutil.copytree(config_dir, backup_dir)
        return backup_dir
    return None

# CRITICAL: Platform-specific installation paths

# Use platform-appropriate directories for different installation scopes
def get_install_paths(scope="project"):
    """Get platform-appropriate installation paths."""
    if scope == "user":
        if platform.system() == "Windows":
            return {
                "bin": Path(os.environ.get("APPDATA", "")) / "Python" / "Scripts",
                "data": Path(os.environ.get("APPDATA", "")) / "mcp-task-orchestrator"
            }
        else:
            return {
                "bin": Path.home() / ".local" / "bin",
                "data": Path.home() / ".local" / "share" / "mcp-task-orchestrator"
            }
    elif scope == "system":
        
# System-wide installation paths
        pass
    else:  
# project scope
        return {
            "venv": Path.cwd() / "venv",
            "data": Path.cwd() / ".task_orchestrator"
        }

```text

#
# Implementation Blueprint

#
## Data Models and Structure

```text
python

# Core data structures for universal installer

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Literal
from enum import Enum

class InstallationScope(Enum):
    """Installation scope options."""
    PROJECT = "project"      
# ./venv/ in current directory
    USER = "user"           
# ~/.local/bin
    SYSTEM = "system"       
# System-wide installation
    CUSTOM = "custom"       
# User-specified path

class InstallationSource(Enum):
    """Installation source options."""
    AUTO = "auto"           
# Auto-detect based on mode
    PYPI = "pypi"          
# PyPI package
    LOCAL = "local"        
# Local directory (editable)
    GIT = "git"            
# Git repository
    VERSION = "version"    
# Specific PyPI version

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

@dataclass
class InstallationEnvironment:
    """Virtual environment and installation information."""
    path: Path
    python_exe: Path
    pip_exe: Path
    exists: bool
    is_valid: bool
    installed_packages: Dict[str, str]
    
    @classmethod
    def detect(cls, path: Path) -> 'InstallationEnvironment':
        """Detect and validate an installation environment."""
        
# Implementation for environment detection
        pass

@dataclass
class InstallationStatus:
    """Current installation status."""
    is_installed: bool
    installation_method: Optional[str]
    version: Optional[str]
    location: Optional[Path]
    clients_configured: List[str]
    configuration_valid: bool
    last_modified: Optional[str]

```text

#
## List of Tasks to Complete

```text
yaml
Task 1:
CREATE install.py (main script):
  - COPY argument parsing pattern from: scripts/deployment/install.py
  - MODIFY to support comprehensive installation modes
  - ADD industry-standard command line interface design
  - INCLUDE rich console output with progress indicators
  - IMPLEMENT configuration validation and sanitization

Task 2:
IMPLEMENT core installation logic:
  - CREATE InstallerCore class with lifecycle management
  - ADD installation scope detection and validation
  - IMPLEMENT virtual environment creation with cross-platform support
  - ADD package manager detection (uv, pip, pipx preferences)
  - INCLUDE comprehensive error handling with recovery suggestions

Task 3:
IMPLEMENT environment management:
  - CREATE EnvironmentManager class for venv lifecycle
  - ADD cross-platform Python executable detection
  - IMPLEMENT pip upgrade and verification
  - ADD environment validation and health checks
  - INCLUDE cleanup and rollback mechanisms

Task 4:
IMPLEMENT source management:
  - CREATE SourceManager class for installation sources
  - ADD PyPI package installation with version support
  - IMPLEMENT local/editable installation for development
  - ADD git repository installation support
  - INCLUDE source validation and fallback strategies

Task 5:
IMPLEMENT MCP client integration:
  - COPY client detection from: mcp_task_orchestrator_cli/platforms/
  - ADD automated client configuration management
  - IMPLEMENT backup and restore for client configurations
  - ADD multi-client support with selective configuration
  - INCLUDE validation of client integration

Task 6:
IMPLEMENT uninstall and cleanup:
  - CREATE UninstallManager class for clean removal
  - ADD configuration preservation with selective cleanup
  - IMPLEMENT purge mode for complete removal
  - ADD backup creation before uninstall operations
  - INCLUDE verification of uninstall completion

Task 7:
IMPLEMENT update and maintenance:
  - CREATE UpdateManager class for version upgrades
  - ADD self-update capability with version detection
  - IMPLEMENT repair functionality for broken installations
  - ADD health checks and diagnostics
  - INCLUDE rollback capability for failed updates

Task 8:
IMPLEMENT comprehensive validation:
  - CREATE ValidationManager class for installation verification
  - ADD status reporting with detailed health information
  - IMPLEMENT integrity checks for all installation components
  - ADD performance verification and optimization recommendations
  - INCLUDE detailed reporting and troubleshooting guidance

Task 9:
IMPLEMENT platform-specific wrappers:
  - CREATE install.sh for Unix/Linux/macOS systems
  - CREATE install.ps1 for Windows PowerShell
  - ADD single-line installation capability
  - IMPLEMENT automatic Python detection and validation
  - INCLUDE platform-specific error handling

Task 10:
IMPLEMENT comprehensive testing:
  - CREATE unit tests for all installer components
  - ADD integration tests for complete installation workflows
  - IMPLEMENT cross-platform testing validation
  - ADD performance and reliability testing
  - INCLUDE edge case and error condition testing

```text

#
## Per Task Pseudocode

```text
python

# Task 1: Main script structure with industry-standard CLI

def main():
    """Universal installer main entry point."""
    
# PATTERN: Follow modern CLI design with mutually exclusive groups
    parser = argparse.ArgumentParser(
        description="MCP Task Orchestrator Universal Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          
# Project install with auto-detection
  %(prog)s --dev                    
# Developer mode installation
  %(prog)s --user --clients claude  
# User-scoped with specific client
  %(prog)s --uninstall --purge      
# Complete removal
  %(prog)s --status                 
# Check installation status
        """
    )
    
    
# Operation modes (mutually exclusive)
    operation_group = parser.add_mutually_exclusive_group()
    operation_group.add_argument("--install", action="store_true", default=True)
    operation_group.add_argument("--uninstall", action="store_true")
    operation_group.add_argument("--reinstall", action="store_true")
    operation_group.add_argument("--update", action="store_true")
    operation_group.add_argument("--verify", action="store_true")
    operation_group.add_argument("--repair", action="store_true")
    operation_group.add_argument("--status", action="store_true")
    
    
# Installation scope
    scope_group = parser.add_mutually_exclusive_group()
    scope_group.add_argument("--user", action="store_true")
    scope_group.add_argument("--system", action="store_true")
    scope_group.add_argument("--venv", type=Path, metavar="PATH")
    
    args = parser.parse_args()
    
    try:
        config = InstallerConfig.from_args(args)
        installer = UniversalInstaller(config)
        return installer.execute()
    except KeyboardInterrupt:
        console.print("\n[yellow]Installation cancelled by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Installation failed: {e}[/red]")
        return 1

# Task 2: Core installation logic with comprehensive scope handling

class UniversalInstaller:
    """Universal installer for MCP Task Orchestrator."""
    
    def __init__(self, config: InstallerConfig):
        self.config = config
        self.console = Console()
        self.environment_manager = EnvironmentManager(config)
        self.source_manager = SourceManager(config)
        self.client_manager = ClientManager(config)
        
    def execute(self) -> int:
        """Execute the installer operation."""
        with self.console.status("[bold blue]Initializing installer..."):
            self.validate_configuration()
            
        if self.config.operation == OperationType.INSTALL:
            return self.install()
        elif self.config.operation == OperationType.UNINSTALL:
            return self.uninstall()
        
# ... other operations
        
    def install(self) -> int:
        """Perform installation with comprehensive validation."""
        
# PATTERN: Multi-step installation with progress tracking
        steps = [
            ("Preparing installation environment", self.prepare_environment),
            ("Creating virtual environment", self.environment_manager.create),
            ("Installing package dependencies", self.install_package),
            ("Configuring MCP clients", self.configure_clients),
            ("Validating installation", self.validate_installation),
        ]
        
        with Progress() as progress:
            task = progress.add_task("Installing...", total=len(steps))
            
            for step_name, step_func in steps:
                progress.update(task, description=step_name)
                try:
                    step_func()
                    progress.advance(task)
                except Exception as e:
                    self.handle_installation_error(e, step_name)
                    return 1
        
        return 0

# Task 3: Environment management with cross-platform support

class EnvironmentManager:
    """Manages virtual environments across platforms."""
    
    def create(self):
        """Create and validate virtual environment."""
        
# PATTERN: Cross-platform venv creation with validation
        if self.config.scope == InstallationScope.PROJECT:
            venv_path = Path.cwd() / "venv"
        elif self.config.scope == InstallationScope.CUSTOM:
            venv_path = self.config.custom_path
        else:
            
# User/system installs don't need venv
            return
            
        if venv_path.exists() and not self.config.force:
            if not self.validate_existing_venv(venv_path):
                raise InstallationError(f"Invalid virtual environment at {venv_path}")
            return
        
        
# Create new virtual environment
        self.console.print(f"Creating virtual environment at [cyan]{venv_path}[/cyan]")
        
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], check=True, capture_output=True, text=True)
            
            
# Upgrade pip immediately
            python_exe = self.get_venv_python(venv_path)
            subprocess.run([
                str(python_exe), "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True, text=True)
            
        except subprocess.CalledProcessError as e:
            raise InstallationError(f"Failed to create virtual environment: {e.stderr}")

# Task 5: MCP client integration with comprehensive support

def configure_clients(self):
    """Configure MCP clients with backup and validation."""
    
# PATTERN: Use existing client detection with enhanced error handling
    if not self.config.configure_clients:
        return
        
    
# Detect available clients
    detected_clients = self.detect_mcp_clients()
    
    if not detected_clients:
        self.console.print("[yellow]No MCP clients detected, skipping configuration[/yellow]")
        return
    
    
# Filter clients if specific ones requested
    target_clients = detected_clients
    if self.config.specific_clients:
        target_clients = {
            client_id: info for client_id, info in detected_clients.items()
            if client_id in self.config.specific_clients
        }
    
    
# Configure each client with backup
    for client_id, client_info in target_clients.items():
        try:
            self.configure_single_client(client_id, client_info)
        except Exception as e:
            self.console.print(f"[yellow]Warning: Failed to configure {client_id}: {e}[/yellow]")

# Task 6: Uninstall with selective cleanup

def uninstall(self) -> int:
    """Perform uninstallation with preservation options."""
    
# PATTERN: Selective cleanup with backup creation
    status = self.get_installation_status()
    
    if not status.is_installed:
        self.console.print("[yellow]No installation detected[/yellow]")
        return 0
    
    
# Create backup if preserving configuration
    backup_path = None
    if self.config.preserve_config and not self.config.purge_config:
        backup_path = self.create_configuration_backup()
    
    
# Remove package installation
    self.remove_package_installation(status)
    
    
# Handle configuration
    if self.config.purge_config:
        self.remove_all_configuration()
    elif self.config.config_only:
        self.remove_configuration_only()
    
    
# Update MCP clients
    if self.config.configure_clients:
        self.remove_mcp_configuration()
    
    return 0

```text

#
## Integration Points

```text
yaml
VIRTUAL_ENVIRONMENT:
  - creation: "Python built-in venv module with pip upgrade"
  - validation: "Import test and executable verification"
  - cleanup: "Complete directory removal with error handling"

PACKAGE_MANAGEMENT:
  - preference: "uv > pipx > pip based on availability"
  - installation: "Editable for dev mode, wheel for production"
  - verification: "Import test and entry point validation"

MCP_CLIENT_INTEGRATION:
  - detection: "Reuse existing platform-specific detection logic"
  - configuration: "JSON backup and atomic updates"
  - validation: "Configuration schema validation and connectivity tests"

CONFIGURATION_MANAGEMENT:
  - preservation: "Timestamped backups with selective restore"
  - migration: "Automatic upgrade of configuration formats"
  - validation: "Schema validation and integrity checks"

CROSS_PLATFORM_SUPPORT:
  - paths: "Platform-appropriate directory structures"
  - executables: "Windows .exe vs Unix binary handling"
  - permissions: "sudo detection and privilege escalation"

ERROR_HANDLING:
  - recovery: "Automatic rollback on partial failures"
  - diagnosis: "Self-diagnosing error messages with suggestions"
  - logging: "Detailed logs with user-friendly summaries"

```text

#
# Validation Loop

#
## Level 1: Syntax & Style

```text
bash

# Run these FIRST - fix any errors before proceeding

ruff check install.py --fix                    
# Auto-fix formatting and style
mypy install.py                                
# Type checking
python -m py_compile install.py                
# Basic syntax validation

# Expected: No errors. If errors, READ the error message and fix the root cause.

```text

#
## Level 2: Unit Tests

```python

# CREATE tests/test_universal_installer.py with comprehensive test coverage:

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from installer.core import UniversalInstaller, InstallerConfig, InstallationScope

def test_installer_config_validation():
    """Test installer configuration validation and defaults."""
    config = InstallerConfig(
        operation=OperationType.INSTALL,
        scope=InstallationScope.PROJECT,
        source=InstallationSource.AUTO,
        dev_mode=True
    )
    
    assert config.operation == OperationType.INSTALL
    assert config.preserve_config is True  
# Default value
    assert config.configure_clients is True  
# Default value

def test_cross_platform_venv_paths():
    """Test cross-platform virtual environment path handling."""
    installer = UniversalInstaller(test_config)
    
    with patch('platform.system', return_value='Windows'):
        python_exe = installer.environment_manager.get_venv_python(Path("test_venv"))
        assert str(python_exe).endswith("Scripts/python.exe")
    
    with patch('platform.system', return_value='Linux'):
        python_exe = installer.environment_manager.get_venv_python(Path("test_venv"))
        assert str(python_exe).endswith("bin/python")

def test_installation_scope_detection():
    """Test automatic installation scope detection based on context."""
    
# Test developer context detection
    with patch('Path.cwd') as mock_cwd:
        mock_cwd.return_value = Path("/dev/mcp-task-orchestrator")
        installer = UniversalInstaller(test_config)
        scope = installer.detect_optimal_scope()
        assert scope == InstallationScope.PROJECT

def test_mcp_client_backup_creation():
    """Test MCP client configuration backup functionality."""
    installer = UniversalInstaller(test_config)
    
    with patch('builtins.open', mock_open(read_data='{"test": "config"}')):
        with patch('time.time', return_value=1234567890):
            backup_path = installer.client_manager.create_backup("claude_desktop")
            assert "backup.1234567890" in str(backup_path)

def test_error_recovery_mechanisms():
    """Test error recovery and rollback functionality."""
    installer = UniversalInstaller(test_config)
    
    with patch('subprocess.run') as mock_run:
        
# Simulate installation failure
        mock_run.side_effect = subprocess.CalledProcessError(1, "pip", stderr="Network error")
        
        with pytest.raises(InstallationError):
            installer.install_package()
        
        
# Verify cleanup was attempted
        assert installer.rollback_called

def test_package_manager_preference():
    """Test package manager selection with preference order."""
    installer = UniversalInstaller(test_config)
    
    
# Test uv preference
    with patch('shutil.which') as mock_which:
        mock_which.side_effect = lambda cmd: "/usr/bin/uv" if cmd == "uv" else None
        manager = installer.source_manager.get_package_manager()
        assert manager == "uv"
    
    
# Test pip fallback
    with patch('shutil.which') as mock_which:
        mock_which.side_effect = lambda cmd: "/usr/bin/pip" if cmd == "pip" else None
        manager = installer.source_manager.get_package_manager()
        assert manager == "pip"

def test_configuration_preservation():
    """Test configuration preservation during reinstall."""
    config = InstallerConfig(
        operation=OperationType.REINSTALL,
        scope=InstallationScope.USER,
        preserve_config=True
    )
    installer = UniversalInstaller(config)
    
    with patch('Path.exists', return_value=True):
        with patch('shutil.copytree') as mock_copytree:
            backup_path = installer.preserve_user_data()
            mock_copytree.assert_called_once()
            assert backup_path is not None

```text

```text
bash

# Run and iterate until all tests pass:

uv run pytest tests/test_universal_installer.py -v --cov=install

# If failing: Read test output, understand the failure, fix the code, re-run

# Achieve >95% test coverage before proceeding

```text

#
## Level 3: Integration Testing

```text
bash

# Test complete installation workflows in isolated environments

cd /tmp
mkdir test_universal_installer
cd test_universal_installer

# Copy installer and minimal project structure

cp /path/to/install.py .
cp /path/to/pyproject.toml .
cp /path/to/requirements.txt .

# Test dry run across all modes

python install.py --dry-run --verbose                    
# Default project mode
python install.py --dev --dry-run --verbose             
# Developer mode
python install.py --user --dry-run --verbose            
# User-scoped mode
python install.py --uninstall --purge --dry-run         
# Uninstall with purge

# Expected: All dry runs complete without errors, show planned operations

# Test actual installation (project scope)

python install.py --dev --verbose --clients claude

# Expected: Creates ./venv/, installs package editbly, configures Claude Desktop

# Verify: ./venv/bin/python -c "import mcp_task_orchestrator; print('OK')"

# Test status and verification

python install.py --status
python install.py --verify

# Expected: Shows installation details, passes all integrity checks

# Test update functionality

python install.py --update --verbose

# Expected: Updates package to latest version, preserves configuration

# Test uninstall with preservation

python install.py --uninstall --verbose

# Expected: Removes package, preserves configuration backup

# Verify: Configuration backup exists, package is uninstalled

# Test purge uninstall

python install.py --uninstall --purge --verbose

# Expected: Complete removal including all configuration

# Verify: No traces of installation remain

```text

#
## Level 4: Cross-Platform Validation

```text
bash

# Test on multiple platforms (Windows, macOS, Linux)

# Platform-specific testing commands:

# Windows (PowerShell)

python install.py --system --verbose                     
# Requires admin
python install.py --user --clients "claude_desktop"     
# User-scoped

# Linux/macOS (Bash)

sudo python install.py --system --verbose               
# System-wide
python install.py --user --clients claude,cursor        
# User-scoped

# WSL (Windows Subsystem for Linux)

python install.py --dev --verbose                       
# Development mode

# Test MCP client integration

# Verify client configuration files are correctly updated

# Test backup and restore functionality

# Validate cross-platform path handling

# Expected: All platforms install successfully with appropriate paths and permissions

```text

#
## Level 5: Industry Standard Validation

```bash

# Test against industry standard tools and patterns

# Compare behavior with pipx, poetry, uv installations

# Test single-line installation (when wrapper scripts ready)

curl -LsSf https://install.mcp-task-orchestrator.sh | sh

# or

iex (iwr https://install.mcp-task-orchestrator.ps1)

# Test self-update capability

mcp-task-orchestrator-installer --update

# Test comprehensive help and documentation

python install.py --help                               
# Should be comprehensive and clear
python install.py --version                            
# Should show version info

# Test error handling and recovery

# Simulate network failures, permission issues, corrupted installations

# Verify graceful error messages and recovery suggestions

# Performance testing

time python install.py --dev                           
# Should complete in <60 seconds
time python install.py --uninstall --purge            
# Should complete in <10 seconds

# Expected: Matches or exceeds industry standards for reliability and user experience

```text

#
# Final Validation Checklist

- [ ] All unit tests pass: `uv run pytest tests/test_universal_installer.py -v --cov=install`

- [ ] No syntax errors: `python -m py_compile install.py`

- [ ] No linting errors: `ruff check install.py`

- [ ] Type checking passes: `mypy install.py`

- [ ] Cross-platform compatibility verified on Windows/Linux/macOS

- [ ] All installation modes work: project, user, system, custom

- [ ] All operation types work: install, uninstall, reinstall, update, verify, repair, status

- [ ] MCP client integration functional: backup, configure, validate

- [ ] Error handling comprehensive: graceful failures with actionable messages

- [ ] Configuration preservation verified: backup and restore functionality

- [ ] Performance acceptable: installation <60s, uninstall <10s

- [ ] Industry standard UX: matches expectations from pipx/poetry/uv

- [ ] Documentation complete: help text, examples, troubleshooting

#
# Anti-Patterns to Avoid

- ❌ Don't hardcode installation paths - use platform-appropriate detection

- ❌ Don't skip backup creation - always preserve user configuration

- ❌ Don't ignore virtual environment validation - ensure functionality

- ❌ Don't silently fail MCP client configuration - provide clear feedback

- ❌ Don't force system-wide installation without explicit user consent

- ❌ Don't skip dependency checks - validate environment before proceeding

- ❌ Don't use shell=True in subprocess calls - security and compatibility risk

- ❌ Don't assume package manager availability - implement fallback chains

- ❌ Don't ignore cross-platform path differences - use pathlib consistently

- ❌ Don't skip rollback on failures - implement comprehensive error recovery

- ❌ Don't create inconsistent CLI interface - follow industry standards

- ❌ Don't forget about edge cases - handle corrupted installs, permission issues, network failures

#
# Score: 9/10

**Confidence Level**: Very High - This PRP provides comprehensive context covering industry best practices from pipx,
poetry, and uv. It includes detailed implementation guidance, extensive validation loops, and addresses all requirements
for a professional-grade universal installer. The comprehensive research and existing codebase analysis provide strong
foundation for one-pass implementation.

**Potential Risks**: Minor complexity around cross-platform MCP client configuration edge cases, but the comprehensive
error handling and validation framework should address these scenarios effectively.
