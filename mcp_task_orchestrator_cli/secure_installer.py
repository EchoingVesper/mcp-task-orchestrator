#!/usr/bin/env python3
"""
Secure MCP Task Orchestrator Installer

A security-first installer that follows MCP protocol standards and eliminates
security vulnerabilities found in previous implementations.

Key Security Features:
- Dynamic Python detection without hardcoded paths
- Environment-agnostic configuration generation
- Comprehensive validation and rollback capabilities
- MCP protocol compliance validation
- Zero user-specific path exposure
"""

import os
import sys
import json
import platform
import subprocess
import shutil
import time
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from enum import Enum

# Rich imports for better UX
try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback to basic console output
    class Console:
        def print(self, *args, **kwargs):
            print(*args)

console = Console()
logger = logging.getLogger(__name__)


class InstallationMode(Enum):
    """Installation mode options."""
    GLOBAL = "global"
    USER = "user" 
    PROJECT = "project"


class ValidationLevel(Enum):
    """Validation strictness levels."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    
    @classmethod
    def from_string(cls, value: str) -> "ValidationLevel":
        """Create ValidationLevel from string value."""
        value_map = {
            "minimal": cls.BASIC,
            "basic": cls.BASIC,
            "standard": cls.STANDARD,
            "strict": cls.STRICT
        }
        return value_map.get(value.lower(), cls.STANDARD)


@dataclass
class PythonEnvironment:
    """Detected Python environment information."""
    executable: Path
    version: str
    site_packages: Path
    is_virtual: bool
    virtual_env_name: Optional[str] = None


@dataclass
class MCPClientInfo:
    """MCP client detection and configuration information."""
    name: str
    config_paths: List[Path]
    detected: bool = False
    running: bool = False
    config_format: str = "json"  # json, yaml, toml
    supports_workspace: bool = False
    supports_env_vars: bool = True


class SecurePythonDetector:
    """Secure Python environment detection without hardcoded paths."""
    
    @staticmethod
    def detect_python_environments() -> List[PythonEnvironment]:
        """Detect available Python environments securely."""
        environments = []
        
        # Try different Python detection methods
        python_candidates = [
            "python3",
            "python", 
            "py",  # Windows Python Launcher
        ]
        
        if platform.system() == "Windows":
            # Windows Python Launcher (preferred)
            python_candidates.insert(0, "py -3")
            
        for candidate in python_candidates:
            try:
                env_info = SecurePythonDetector._analyze_python_env(candidate)
                if env_info:
                    environments.append(env_info)
            except Exception as e:
                logger.debug(f"Failed to analyze {candidate}: {e}")
                
        return environments
    
    @staticmethod
    def _analyze_python_env(python_cmd: str) -> Optional[PythonEnvironment]:
        """Analyze a specific Python environment."""
        try:
            # Get Python executable path
            result = subprocess.run(
                python_cmd.split() + ["-c", "import sys; print(sys.executable)"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return None
                
            executable = Path(result.stdout.strip())
            
            # Get Python version
            result = subprocess.run(
                python_cmd.split() + ["--version"],
                capture_output=True, text=True, timeout=10
            )
            version = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            # Get site-packages directory
            result = subprocess.run(
                python_cmd.split() + ["-c", 
                    "import site; print(site.getsitepackages()[0] if site.getsitepackages() else site.getusersitepackages())"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return None
                
            site_packages = Path(result.stdout.strip())
            
            # Check if it's a virtual environment
            result = subprocess.run(
                python_cmd.split() + ["-c", "import sys; print(hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))"],
                capture_output=True, text=True, timeout=10
            )
            
            is_virtual = result.stdout.strip().lower() == "true" if result.returncode == 0 else False
            
            # Get virtual environment name if applicable
            venv_name = None
            if is_virtual:
                result = subprocess.run(
                    python_cmd.split() + ["-c", "import os; print(os.environ.get('VIRTUAL_ENV', '').split(os.sep)[-1] if os.environ.get('VIRTUAL_ENV') else '')"],
                    capture_output=True, text=True, timeout=10
                )
                venv_name = result.stdout.strip() or None
            
            return PythonEnvironment(
                executable=executable,
                version=version,
                site_packages=site_packages,
                is_virtual=is_virtual,
                virtual_env_name=venv_name
            )
            
        except Exception as e:
            logger.debug(f"Failed to analyze Python environment {python_cmd}: {e}")
            return None


class MCPClientDetector:
    """Secure MCP client detection without hardcoded user paths."""
    
    # Client detection rules using environment-agnostic patterns
    CLIENT_PATTERNS = {
        "claude_desktop": {
            "name": "Claude Desktop",
            "config_paths": {
                "windows": ["~/AppData/Roaming/Claude/claude_desktop_config.json", "~/.claude/mcp.json"],
                "darwin": ["~/Library/Application Support/Claude/mcp.json", "~/.claude/mcp.json"],
                "linux": ["~/.config/claude/mcp.json", "~/.claude/mcp.json"]
            },
            "process_names": {
                "windows": ["Claude.exe"],
                "darwin": ["Claude"],
                "linux": ["claude"]
            },
            "supports_workspace": False,
            "supports_env_vars": True
        },
        "claude_code": {
            "name": "Claude Code", 
            "config_paths": {
                "windows": ["~/.claude_code/mcp.json"],
                "darwin": ["~/.claude_code/mcp.json"],
                "linux": ["~/.claude_code/mcp.json"]
            },
            "process_names": {},  # CLI tool
            "supports_workspace": True,
            "supports_env_vars": True
        },
        "cursor": {
            "name": "Cursor IDE",
            "config_paths": {
                "windows": ["~/.cursor/mcp.json", "~/AppData/Roaming/Cursor/User/mcp.json"],
                "darwin": ["~/Library/Application Support/Cursor/User/mcp.json", "~/.cursor/mcp.json"],
                "linux": ["~/.config/Cursor/User/mcp.json", "~/.cursor/mcp.json"]
            },
            "process_names": {
                "windows": ["Cursor.exe"],
                "darwin": ["Cursor"],
                "linux": ["cursor"]
            },
            "supports_workspace": True,
            "supports_env_vars": True
        },
        "windsurf": {
            "name": "Windsurf",
            "config_paths": {
                "windows": ["~/.codeium/windsurf/mcp_config.json"],
                "darwin": ["~/Library/Application Support/Codeium/Windsurf/mcp_config.json"],
                "linux": ["~/.config/codeium/windsurf/mcp_config.json"]
            },
            "process_names": {
                "windows": ["windsurf.exe"],
                "darwin": ["Windsurf"],
                "linux": ["windsurf"]
            },
            "supports_workspace": True,
            "supports_env_vars": True
        }
    }
    
    @classmethod
    def detect_clients(cls) -> List[MCPClientInfo]:
        """Detect installed MCP clients."""
        detected_clients = []
        system = platform.system().lower()
        
        for client_id, pattern in cls.CLIENT_PATTERNS.items():
            client_info = cls._detect_single_client(client_id, pattern, system)
            if client_info:
                detected_clients.append(client_info)
                
        return detected_clients
    
    @classmethod
    def _detect_single_client(cls, client_id: str, pattern: dict, system: str) -> Optional[MCPClientInfo]:
        """Detect a single MCP client."""
        try:
            # Get config paths for current system
            system_key = system if system in pattern["config_paths"] else "linux"
            config_path_patterns = pattern["config_paths"].get(system_key, [])
            
            # Expand user paths safely
            config_paths = []
            for path_pattern in config_path_patterns:
                expanded_path = Path(path_pattern).expanduser()
                config_paths.append(expanded_path)
            
            # Check if client is detected (config directory exists)
            detected = any(path.parent.exists() or path.exists() for path in config_paths)
            
            # Check if client is running
            running = cls._check_process_running(pattern.get("process_names", {}), system)
            
            return MCPClientInfo(
                name=pattern["name"],
                config_paths=config_paths,
                detected=detected,
                running=running,
                supports_workspace=pattern.get("supports_workspace", False),
                supports_env_vars=pattern.get("supports_env_vars", True)
            )
            
        except Exception as e:
            logger.debug(f"Failed to detect client {client_id}: {e}")
            return None
    
    @staticmethod
    def _check_process_running(process_names: dict, system: str) -> bool:
        """Check if client process is running."""
        system_processes = process_names.get(system, [])
        if not system_processes:
            return False
            
        try:
            if system == "windows":
                for process_name in system_processes:
                    result = subprocess.run(
                        ['tasklist', '/FI', f'IMAGENAME eq {process_name}'],
                        capture_output=True, text=True, timeout=5
                    )
                    if process_name in result.stdout:
                        return True
            else:
                for process_name in system_processes:
                    result = subprocess.run(
                        ['pgrep', '-x', process_name],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        return True
        except Exception:
            pass
            
        return False


class SecureConfigGenerator:
    """Generate secure MCP configurations without hardcoded paths."""
    
    @staticmethod
    def generate_server_config(
        python_env: PythonEnvironment,
        validation_level: ValidationLevel = ValidationLevel.STANDARD
    ) -> dict:
        """Generate secure server configuration."""
        
        # Generate environment variables dynamically
        env_vars = {}
        
        # Only add essential environment variables
        if validation_level != ValidationLevel.BASIC:
            env_vars.update({
                "PYTHONUNBUFFERED": "1",
                "PYTHONIOENCODING": "utf-8"
            })
        
        # For Windows, prefer py launcher to avoid user/system Python conflicts
        import platform
        if platform.system() == "Windows":
            # Test if py launcher can find the package
            import subprocess
            try:
                result = subprocess.run(
                    ["py", "-c", "import mcp_task_orchestrator"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    # py launcher works, use it
                    config = {
                        "command": "py",
                        "args": ["-m", "mcp_task_orchestrator.server"]
                    }
                else:
                    # Fallback to explicit Python path
                    config = {
                        "command": str(python_env.executable),
                        "args": ["-m", "mcp_task_orchestrator.server"]
                    }
            except Exception:
                # Fallback to explicit Python path
                config = {
                    "command": str(python_env.executable),
                    "args": ["-m", "mcp_task_orchestrator.server"]
                }
        else:
            # Non-Windows: use explicit Python path
            config = {
                "command": str(python_env.executable),
                "args": ["-m", "mcp_task_orchestrator.server"]
            }
        
        # Add environment variables if needed
        if env_vars:
            config["env"] = env_vars
            
        # Add unbuffered flag for reliability
        if "-u" not in config["args"]:
            config["args"].insert(0, "-u")
            
        return config
    
    @staticmethod
    def generate_client_config(
        client_info: MCPClientInfo, 
        server_config: dict,
        installation_mode: InstallationMode = InstallationMode.USER,
        project_directory: Optional[str] = None
    ) -> dict:
        """Generate client-specific configuration."""
        
        # Check if this is Claude Desktop with claude_desktop_config.json
        config_path = str(client_info.config_paths[0]) if client_info.config_paths else ""
        is_claude_desktop_config = "claude_desktop_config.json" in config_path
        
        server_config_copy = server_config.copy()
        
        # Set working directory based on client type and project directory
        import os
        if is_claude_desktop_config and project_directory:
            # Claude Desktop: use the selected project directory
            server_config_copy["cwd"] = project_directory
        elif client_info.name in ["Windsurf", "Cursor IDE"]:
            # Windsurf/Cursor: use user home to avoid permission issues (they handle workspace inheritance)
            server_config_copy["cwd"] = os.path.expanduser("~")
        
        if is_claude_desktop_config:
            # Claude Desktop uses a different config structure
            base_config = {
                "mcpServers": {
                    "task-orchestrator": server_config_copy
                }
            }
        else:
            # Standard MCP config structure  
            base_config = {
                "mcpServers": {
                    "task-orchestrator": server_config_copy
                }
            }
        
        return base_config


class BackupManager:
    """Handle configuration backups and rollback operations."""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        self.backup_dir = backup_dir or Path.home() / ".mcp_task_orchestrator" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self, config_path: Path) -> Optional[Path]:
        """Create a backup of a configuration file."""
        if not config_path.exists():
            return None
            
        timestamp = int(time.time())
        backup_name = f"{config_path.stem}_{config_path.suffix[1:]}_{timestamp}.backup"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(config_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup of {config_path}: {e}")
            return None
    
    def restore_backup(self, backup_path: Path, original_path: Path) -> bool:
        """Restore a configuration from backup."""
        try:
            shutil.copy2(backup_path, original_path)
            logger.info(f"Restored backup from {backup_path} to {original_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def list_backups(self) -> List[Path]:
        """List all available backups."""
        return list(self.backup_dir.glob("*.backup"))


class ConfigValidator:
    """Validate MCP configurations for security and compliance."""
    
    @staticmethod
    def validate_config(config: dict, validation_level: ValidationLevel = ValidationLevel.STANDARD) -> Tuple[bool, List[str]]:
        """Validate configuration for security and compliance."""
        issues = []
        
        # Check for hardcoded user paths
        if ConfigValidator._contains_hardcoded_paths(config):
            issues.append("Configuration contains hardcoded user-specific paths")
        
        # Check for PATH dumping
        if ConfigValidator._contains_path_dumping(config):
            issues.append("Configuration exposes system PATH information")
        
        # Check MCP protocol compliance
        mcp_issues = ConfigValidator._validate_mcp_compliance(config)
        issues.extend(mcp_issues)
        
        # Strict validation checks
        if validation_level == ValidationLevel.STRICT:
            strict_issues = ConfigValidator._strict_validation(config)
            issues.extend(strict_issues)
        
        return len(issues) == 0, issues
    
    @staticmethod
    def _contains_hardcoded_paths(config: dict) -> bool:
        """Check for hardcoded user-specific paths (excluding legitimate Python executables)."""
        config_str = json.dumps(config)
        
        # Patterns for legitimate paths that should be allowed
        legitimate_path_patterns = [
            # Python executables
            r"[\"']/home/[^/]+/[^/]*env[^/]*/bin/python[3]?[\"']",  # Virtual env pythons
            r"[\"']/opt/conda/bin/python[3]?[\"']",                 # Conda pythons
            r"[\"']/usr/bin/python[3]?[\"']",                       # System pythons
            r"[\"']/usr/local/bin/python[3]?[\"']",                 # Local pythons
            r"[\"']C:\\\\Users\\\\[^\\\\]+\\\\[^\\\\]*env[^\\\\]*\\\\Scripts\\\\python\.exe[\"']",  # Windows venv
            r"[\"']C:\\\\Python[0-9]+\\\\python\.exe[\"']",        # Windows system Python
            r"[\"']C:\\\\Program Files\\\\Python[0-9]+\\\\python[0-9.]*\.exe[\"']",  # Program Files Python
            r"[\"']C:\\\\Program Files\\\\Python[0-9]+\\\\python\.exe[\"']",        # Program Files Python (no version)
            
            # Working directories (cwd)
            r"[\"']C:\\\\Users\\\\[^\\\\]+[\"']",                   # Windows user home directories
            r"[\"'][C-Z]:\\\\[^\\\\\"']*[\"']",                     # Windows drive-based project directories (C:\Projects, E:\My Work, etc.)
            r"[\"']/home/[^/]+[\"']",                               # Unix user home directories
            r"[\"']/home/[^/]+/[^\"']*[\"']",                       # Unix project directories
        ]
        
        # Remove legitimate paths from validation
        import re
        clean_config_str = config_str
        for pattern in legitimate_path_patterns:
            clean_config_str = re.sub(pattern, '"safe_path"', clean_config_str)
        
        # Now check for remaining problematic hardcoded paths
        hardcoded_patterns = [
            r"C:\\Users\\[^\\]+\\(?!.*env.*\\Scripts\\python\.exe)",  # Windows user dirs (not python)
            r"/home/[^/]+/(?!.*env.*/bin/python)",        # Linux user dirs (not python)
            r"/Users/[^/]+/(?!.*env.*/bin/python)",       # macOS user dirs (not python)
        ]
        
        for pattern in hardcoded_patterns:
            if re.search(pattern, clean_config_str):
                return True
                
        return False
    
    @staticmethod
    def _contains_path_dumping(config: dict) -> bool:
        """Check for environment PATH exposure."""
        config_str = json.dumps(config).lower()
        
        # Look for full PATH dumps
        suspicious_patterns = [
            "pythonpath",
            "site-packages",
            "appdata\\roaming",
            "library/application support"
        ]
        
        # Allow PYTHONPATH but check if it's a full dump
        if "pythonpath" in config_str:
            # Check if it contains multiple paths (indicating a dump)
            pythonpath_sections = [v for v in config.get("env", {}).values() if isinstance(v, str) and "pythonpath" in v.lower()]
            for section in pythonpath_sections:
                if len(section.split(os.pathsep)) > 2:  # More than 2 paths indicates potential dump
                    return True
        
        return False
    
    @staticmethod
    def _validate_mcp_compliance(config: dict) -> List[str]:
        """Validate MCP protocol compliance."""
        issues = []
        
        # Check for required MCP server structure
        if "mcpServers" in config:
            servers = config["mcpServers"]
            for server_name, server_config in servers.items():
                if not isinstance(server_config, dict):
                    issues.append(f"Server '{server_name}' configuration must be an object")
                    continue
                
                # Check required fields
                if "command" not in server_config:
                    issues.append(f"Server '{server_name}' missing required 'command' field")
                
                # Validate command format
                command = server_config.get("command")
                if command and not isinstance(command, str):
                    issues.append(f"Server '{server_name}' command must be a string")
                
                # Validate args format
                args = server_config.get("args", [])
                if not isinstance(args, list):
                    issues.append(f"Server '{server_name}' args must be an array")
        
        return issues
    
    @staticmethod
    def _strict_validation(config: dict) -> List[str]:
        """Perform strict validation checks."""
        issues = []
        
        # Check for absolute paths
        config_str = json.dumps(config)
        if ("C:\\" in config_str or config_str.count("/") > 10):
            issues.append("Configuration may contain absolute paths (strict mode)")
        
        # Check environment variable count
        env_vars = config.get("env", {})
        if len(env_vars) > 5:
            issues.append("Too many environment variables (strict mode recommends ≤5)")
        
        return issues