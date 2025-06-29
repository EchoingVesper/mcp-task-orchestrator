"""
Smart Working Directory Detection System for MCP Task Orchestrator.

This module provides intelligent directory detection that finds git roots, project markers,
and MCP client working directories with a robust fallback hierarchy. It forms the foundation
of the workspace paradigm by ensuring reliable working directory management.

Key Features:
- Git root detection with .git directory traversal
- Project marker detection (package.json, pyproject.toml, etc.)
- MCP client PWD detection from environment variables
- Explicit directory override capability
- Robust fallback hierarchy with validation
- Cross-platform compatibility
- Security validation to prevent directory traversal attacks
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class DetectionMethod(Enum):
    """Methods used for directory detection."""
    EXPLICIT_PARAMETER = "explicit_parameter"
    GIT_ROOT = "git_root"
    PROJECT_MARKER = "project_marker"
    MCP_CLIENT_PWD = "mcp_client_pwd"
    CURRENT_DIRECTORY = "current_directory"
    USER_HOME = "user_home"
    SYSTEM_TEMP = "system_temp"


@dataclass
class ProjectMarker:
    """Information about a detected project marker file."""
    file_path: Path
    marker_type: str
    confidence: int  # 1-10 scale
    description: str


@dataclass
class DirectoryValidation:
    """Result of directory validation."""
    is_valid: bool
    is_writable: bool
    exists: bool
    is_secure: bool
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class DetectionResult:
    """Result of working directory detection."""
    detected_path: Path
    method: DetectionMethod
    confidence: int  # 1-10 scale
    validation: DirectoryValidation
    project_markers: List[ProjectMarker]
    git_root: Optional[Path] = None
    fallback_used: bool = False
    detection_time_ms: float = 0.0


class DirectoryDetector:
    """
    Smart working directory detection system.
    
    Implements intelligent directory detection using multiple methods with
    fallback hierarchy to ensure reliable workspace management.
    """
    
    # Project marker files with confidence scores
    PROJECT_MARKERS = {
        # Python projects
        'pyproject.toml': {'confidence': 9, 'type': 'python', 'description': 'Python project configuration'},
        'setup.py': {'confidence': 8, 'type': 'python', 'description': 'Python package setup'},
        'requirements.txt': {'confidence': 6, 'type': 'python', 'description': 'Python dependencies'},
        'Pipfile': {'confidence': 7, 'type': 'python', 'description': 'Pipenv project'},
        'poetry.lock': {'confidence': 8, 'type': 'python', 'description': 'Poetry project'},
        'conda.yaml': {'confidence': 7, 'type': 'python', 'description': 'Conda environment'},
        
        # JavaScript/Node.js projects
        'package.json': {'confidence': 9, 'type': 'javascript', 'description': 'Node.js project'},
        'package-lock.json': {'confidence': 7, 'type': 'javascript', 'description': 'NPM lock file'},
        'yarn.lock': {'confidence': 7, 'type': 'javascript', 'description': 'Yarn lock file'},
        'pnpm-lock.yaml': {'confidence': 7, 'type': 'javascript', 'description': 'PNPM lock file'},
        
        # Rust projects
        'Cargo.toml': {'confidence': 9, 'type': 'rust', 'description': 'Rust project configuration'},
        'Cargo.lock': {'confidence': 7, 'type': 'rust', 'description': 'Rust dependencies lock'},
        
        # Go projects
        'go.mod': {'confidence': 9, 'type': 'go', 'description': 'Go module'},
        'go.sum': {'confidence': 7, 'type': 'go', 'description': 'Go dependencies checksum'},
        
        # Java projects
        'pom.xml': {'confidence': 8, 'type': 'java', 'description': 'Maven project'},
        'build.gradle': {'confidence': 8, 'type': 'java', 'description': 'Gradle project'},
        'gradle.properties': {'confidence': 6, 'type': 'java', 'description': 'Gradle configuration'},
        
        # C/C++ projects
        'CMakeLists.txt': {'confidence': 8, 'type': 'cpp', 'description': 'CMake project'},
        'Makefile': {'confidence': 6, 'type': 'cpp', 'description': 'Make build system'},
        'configure.ac': {'confidence': 7, 'type': 'cpp', 'description': 'Autotools project'},
        
        # .NET projects
        '*.csproj': {'confidence': 8, 'type': 'dotnet', 'description': '.NET project'},
        '*.sln': {'confidence': 9, 'type': 'dotnet', 'description': '.NET solution'},
        
        # IDE/Editor markers
        '.vscode': {'confidence': 5, 'type': 'ide', 'description': 'VS Code workspace'},
        '.idea': {'confidence': 5, 'type': 'ide', 'description': 'IntelliJ workspace'},
        '.project': {'confidence': 4, 'type': 'ide', 'description': 'Eclipse project'},
        
        # Docker projects
        'Dockerfile': {'confidence': 6, 'type': 'docker', 'description': 'Docker container'},
        'docker-compose.yml': {'confidence': 7, 'type': 'docker', 'description': 'Docker Compose'},
        'docker-compose.yaml': {'confidence': 7, 'type': 'docker', 'description': 'Docker Compose'},
        
        # Configuration files
        '.gitignore': {'confidence': 3, 'type': 'git', 'description': 'Git ignore file'},
        'README.md': {'confidence': 2, 'type': 'docs', 'description': 'Project documentation'},
        'LICENSE': {'confidence': 2, 'type': 'legal', 'description': 'Project license'},
    }
    
    # Environment variables that may contain MCP client working directory
    MCP_CLIENT_ENV_VARS = [
        'MCP_TASK_ORCHESTRATOR_WORKING_DIR',  # Our own variable
        'MCP_CLIENT_PWD',                     # Generic MCP client PWD
        'CLAUDE_WORKING_DIR',                 # Claude Desktop specific
        'CURSOR_WORKING_DIR',                 # Cursor IDE specific
        'WINDSURF_WORKING_DIR',               # Windsurf specific
        'VSCODE_WORKING_DIR',                 # VS Code specific
        'PWD',                                # Unix working directory
    ]
    
    def __init__(self, security_checks: bool = True):
        """
        Initialize the directory detector.
        
        Args:
            security_checks: Whether to perform security validation
        """
        self.security_checks = security_checks
        self._cache = {}  # Simple caching for performance
    
    def detect_project_root(
        self, 
        starting_path: Optional[str] = None,
        explicit_directory: Optional[str] = None
    ) -> DetectionResult:
        """
        Detect the project root directory using multiple methods.
        
        Args:
            starting_path: Starting path for detection (defaults to current directory)
            explicit_directory: Explicit directory override (highest priority)
            
        Returns:
            DetectionResult with detected path and metadata
        """
        import time
        start_time = time.time()
        
        try:
            # Method 1: Explicit directory override (highest priority)
            if explicit_directory:
                result = self._try_explicit_directory(explicit_directory)
                if result.validation.is_valid:
                    result.detection_time_ms = (time.time() - start_time) * 1000
                    return result
            
            # Method 2: Git root detection
            git_result = self._try_git_root_detection(starting_path)
            if git_result and git_result.validation.is_valid:
                git_result.detection_time_ms = (time.time() - start_time) * 1000
                return git_result
            
            # Method 3: Project marker detection
            marker_result = self._try_project_marker_detection(starting_path)
            if marker_result and marker_result.validation.is_valid:
                marker_result.detection_time_ms = (time.time() - start_time) * 1000
                return marker_result
            
            # Method 4: MCP client PWD
            client_result = self._try_mcp_client_pwd()
            if client_result and client_result.validation.is_valid:
                client_result.detection_time_ms = (time.time() - start_time) * 1000
                return client_result
            
            # Fallback methods
            fallback_result = self._apply_fallback_hierarchy(starting_path)
            fallback_result.detection_time_ms = (time.time() - start_time) * 1000
            return fallback_result
            
        except Exception as e:
            logger.error(f"Error during directory detection: {e}")
            # Emergency fallback
            emergency_path = Path.cwd()
            return DetectionResult(
                detected_path=emergency_path,
                method=DetectionMethod.CURRENT_DIRECTORY,
                confidence=1,
                validation=self.validate_directory(str(emergency_path)),
                project_markers=[],
                fallback_used=True,
                detection_time_ms=(time.time() - start_time) * 1000
            )
    
    def find_git_root(self, path: Path) -> Optional[Path]:
        """
        Find the Git root directory by traversing upward.
        
        Args:
            path: Starting path for Git root search
            
        Returns:
            Path to Git root or None if not found
        """
        current = Path(path).resolve()
        
        # Traverse upward looking for .git directory
        for parent in [current] + list(current.parents):
            git_dir = parent / '.git'
            if git_dir.exists():
                logger.debug(f"Found Git root at: {parent}")
                return parent
        
        return None
    
    def find_project_markers(self, path: Path, max_depth: int = 3) -> List[ProjectMarker]:
        """
        Find project marker files in the directory hierarchy.
        
        Args:
            path: Starting path for marker search
            max_depth: Maximum depth to search upward
            
        Returns:
            List of ProjectMarker objects found
        """
        markers = []
        current = Path(path).resolve()
        
        # Search current directory and parents up to max_depth
        search_paths = [current] + list(current.parents[:max_depth])
        
        for search_path in search_paths:
            try:
                # Check for direct file matches
                for marker_name, marker_info in self.PROJECT_MARKERS.items():
                    if '*' in marker_name:
                        # Handle glob patterns
                        for match in search_path.glob(marker_name):
                            if match.is_file():
                                markers.append(ProjectMarker(
                                    file_path=match,
                                    marker_type=marker_info['type'],
                                    confidence=marker_info['confidence'],
                                    description=marker_info['description']
                                ))
                    else:
                        marker_path = search_path / marker_name
                        if marker_path.exists():
                            markers.append(ProjectMarker(
                                file_path=marker_path,
                                marker_type=marker_info['type'],
                                confidence=marker_info['confidence'],
                                description=marker_info['description']
                            ))
            except (OSError, PermissionError) as e:
                logger.debug(f"Error accessing {search_path}: {e}")
                continue
        
        # Sort by confidence (highest first)
        markers.sort(key=lambda m: m.confidence, reverse=True)
        return markers
    
    def validate_directory(self, path: str) -> DirectoryValidation:
        """
        Validate a directory for workspace use.
        
        Args:
            path: Directory path to validate
            
        Returns:
            DirectoryValidation with validation results
        """
        try:
            path_obj = Path(path).resolve()
            warnings = []
            
            # Basic existence check
            exists = path_obj.exists()
            if not exists:
                try:
                    path_obj.mkdir(parents=True, exist_ok=True)
                    exists = True
                    warnings.append(f"Created directory: {path_obj}")
                except (OSError, PermissionError) as e:
                    return DirectoryValidation(
                        is_valid=False,
                        is_writable=False,
                        exists=False,
                        is_secure=False,
                        error_message=f"Cannot create directory: {e}",
                        warnings=warnings
                    )
            
            # Check if it's actually a directory
            if exists and not path_obj.is_dir():
                return DirectoryValidation(
                    is_valid=False,
                    is_writable=False,
                    exists=True,
                    is_secure=False,
                    error_message="Path exists but is not a directory",
                    warnings=warnings
                )
            
            # Test write permissions
            is_writable = False
            try:
                test_file = path_obj / '.orchestrator_write_test'
                test_file.write_text('test')
                test_file.unlink()
                is_writable = True
            except (OSError, PermissionError):
                warnings.append("Directory may not be writable")
            
            # Security checks
            is_secure = True
            if self.security_checks:
                is_secure = self._validate_directory_security(path_obj, warnings)
            
            is_valid = exists and path_obj.is_dir() and (is_writable or not self.security_checks)
            
            return DirectoryValidation(
                is_valid=is_valid,
                is_writable=is_writable,
                exists=exists,
                is_secure=is_secure,
                warnings=warnings
            )
            
        except Exception as e:
            return DirectoryValidation(
                is_valid=False,
                is_writable=False,
                exists=False,
                is_secure=False,
                error_message=f"Validation error: {e}"
            )
    
    def resolve_relative_path(self, workspace_root: Path, target: str) -> Path:
        """
        Resolve a relative path within a workspace root safely.
        
        Args:
            workspace_root: Root directory of the workspace
            target: Target path (can be absolute or relative)
            
        Returns:
            Resolved absolute path within workspace
        """
        workspace_root = Path(workspace_root).resolve()
        target_path = Path(target)
        
        if target_path.is_absolute():
            # For absolute paths, check if they're within workspace
            try:
                relative = target_path.relative_to(workspace_root)
                return workspace_root / relative
            except ValueError:
                # Path is outside workspace, return as-is but log warning
                logger.warning(f"Path {target} is outside workspace {workspace_root}")
                return target_path
        else:
            # For relative paths, resolve within workspace
            resolved = workspace_root / target_path
            return resolved.resolve()
    
    def _try_explicit_directory(self, explicit_directory: str) -> DetectionResult:
        """Try explicit directory override."""
        path = Path(explicit_directory).resolve()
        validation = self.validate_directory(str(path))
        
        return DetectionResult(
            detected_path=path,
            method=DetectionMethod.EXPLICIT_PARAMETER,
            confidence=10,  # Highest confidence for explicit override
            validation=validation,
            project_markers=self.find_project_markers(path),
            git_root=self.find_git_root(path)
        )
    
    def _try_git_root_detection(self, starting_path: Optional[str]) -> Optional[DetectionResult]:
        """Try Git root detection."""
        start_path = Path(starting_path or os.getcwd()).resolve()
        git_root = self.find_git_root(start_path)
        
        if git_root:
            validation = self.validate_directory(str(git_root))
            if validation.is_valid:
                return DetectionResult(
                    detected_path=git_root,
                    method=DetectionMethod.GIT_ROOT,
                    confidence=8,
                    validation=validation,
                    project_markers=self.find_project_markers(git_root),
                    git_root=git_root
                )
        
        return None
    
    def _try_project_marker_detection(self, starting_path: Optional[str]) -> Optional[DetectionResult]:
        """Try project marker detection."""
        start_path = Path(starting_path or os.getcwd()).resolve()
        markers = self.find_project_markers(start_path)
        
        if markers:
            # Use the directory containing the highest confidence marker
            best_marker = markers[0]
            project_root = best_marker.file_path.parent
            validation = self.validate_directory(str(project_root))
            
            if validation.is_valid:
                return DetectionResult(
                    detected_path=project_root,
                    method=DetectionMethod.PROJECT_MARKER,
                    confidence=best_marker.confidence,
                    validation=validation,
                    project_markers=markers,
                    git_root=self.find_git_root(project_root)
                )
        
        return None
    
    def _try_mcp_client_pwd(self) -> Optional[DetectionResult]:
        """Try MCP client PWD detection."""
        for env_var in self.MCP_CLIENT_ENV_VARS:
            env_value = os.environ.get(env_var)
            if env_value and Path(env_value).exists():
                path = Path(env_value).resolve()
                validation = self.validate_directory(str(path))
                
                if validation.is_valid:
                    return DetectionResult(
                        detected_path=path,
                        method=DetectionMethod.MCP_CLIENT_PWD,
                        confidence=7,
                        validation=validation,
                        project_markers=self.find_project_markers(path),
                        git_root=self.find_git_root(path)
                    )
        
        return None
    
    def _apply_fallback_hierarchy(self, starting_path: Optional[str]) -> DetectionResult:
        """Apply fallback hierarchy when primary methods fail."""
        fallback_paths = [
            (Path(starting_path or os.getcwd()).resolve(), DetectionMethod.CURRENT_DIRECTORY, 5),
            (Path.home(), DetectionMethod.USER_HOME, 3),
            (Path.home() / 'Documents', DetectionMethod.USER_HOME, 2),
            (Path.cwd(), DetectionMethod.CURRENT_DIRECTORY, 1)
        ]
        
        for path, method, confidence in fallback_paths:
            try:
                validation = self.validate_directory(str(path))
                if validation.is_valid:
                    return DetectionResult(
                        detected_path=path,
                        method=method,
                        confidence=confidence,
                        validation=validation,
                        project_markers=self.find_project_markers(path),
                        git_root=self.find_git_root(path),
                        fallback_used=True
                    )
            except Exception as e:
                logger.debug(f"Fallback path {path} failed: {e}")
                continue
        
        # Last resort: current working directory with minimal validation
        emergency_path = Path.cwd()
        return DetectionResult(
            detected_path=emergency_path,
            method=DetectionMethod.CURRENT_DIRECTORY,
            confidence=1,
            validation=DirectoryValidation(
                is_valid=True,
                is_writable=True,
                exists=True,
                is_secure=True
            ),
            project_markers=[],
            fallback_used=True
        )
    
    def _validate_directory_security(self, path: Path, warnings: List[str]) -> bool:
        """
        Validate directory security to prevent attacks.
        
        Args:
            path: Path to validate
            warnings: List to append security warnings
            
        Returns:
            True if directory is secure
        """
        try:
            # Check for directory traversal attempts
            resolved_path = path.resolve()
            if '..' in str(resolved_path):
                warnings.append("Path contains directory traversal sequences")
                return False
            
            # Check if path is within reasonable bounds (not system directories)
            system_dirs = ['/bin', '/sbin', '/etc', '/sys', '/proc', '/dev']
            if os.name != 'nt':  # Unix-like systems
                for sys_dir in system_dirs:
                    if str(resolved_path).startswith(sys_dir):
                        warnings.append(f"Path is in system directory: {sys_dir}")
                        return False
            
            # Check permissions
            if not os.access(resolved_path, os.R_OK):
                warnings.append("Directory is not readable")
                return False
            
            return True
            
        except Exception as e:
            warnings.append(f"Security validation error: {e}")
            return False