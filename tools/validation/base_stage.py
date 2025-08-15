"""
Base validation stage implementation.

This module provides the abstract base class for all validation stages,
defining the common interface and shared functionality.
"""

import asyncio
import logging
import subprocess
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from .models import (
    ValidationResult, ValidationStatus, ValidationIssue, 
    StageMetrics, SeverityLevel, ToolResult
)


logger = logging.getLogger(__name__)


class ValidationStageBase(ABC):
    """Abstract base class for validation stages."""
    
    def __init__(self, stage_id: int, stage_name: str, config: Dict[str, Any]):
        self.stage_id = stage_id
        self.stage_name = stage_name
        self.config = config
        self.project_root = Path(config.get('project_root', '.'))
        self.timeout_minutes = config.get('timeout_minutes', 10)
        self.enabled = config.get('enabled', True)
        
        # Initialize result object
        self.result = ValidationResult(
            stage_id=self.stage_id,
            stage_name=self.stage_name,
            status=ValidationStatus.PENDING,
            start_time=datetime.now()
        )
    
    async def run(self) -> ValidationResult:
        """Run the validation stage with timeout and error handling."""
        if not self.enabled:
            self.result.status = ValidationStatus.SKIPPED
            self.result.end_time = datetime.now()
            logger.info(f"Stage {self.stage_id} ({self.stage_name}) skipped - disabled")
            return self.result
        
        logger.info(f"Starting Stage {self.stage_id}: {self.stage_name}")
        self.result.status = ValidationStatus.RUNNING
        
        try:
            # Run with timeout
            await asyncio.wait_for(
                self._execute_stage(),
                timeout=self.timeout_minutes * 60
            )
            
            # Determine final status based on issues
            self._finalize_status()
            
        except asyncio.TimeoutError:
            self.result.status = ValidationStatus.ERROR
            self.result.error_message = f"Stage timed out after {self.timeout_minutes} minutes"
            logger.error(f"Stage {self.stage_id} timed out")
            
        except Exception as e:
            self.result.status = ValidationStatus.ERROR
            self.result.error_message = str(e)
            logger.exception(f"Stage {self.stage_id} failed with exception: {e}")
        
        finally:
            self.result.end_time = datetime.now()
            logger.info(f"Stage {self.stage_id} completed with status: {self.result.status}")
        
        return self.result
    
    @abstractmethod
    async def _execute_stage(self) -> None:
        """Execute the specific validation logic for this stage."""
        pass
    
    def _finalize_status(self) -> None:
        """Determine final status based on collected issues."""
        if self.result.critical_issues:
            self.result.status = ValidationStatus.FAILED
        elif self.result.high_issues:
            # Check if stage allows warnings
            if self.config.get('fail_on_error', True):
                self.result.status = ValidationStatus.FAILED
            else:
                self.result.status = ValidationStatus.WARNING
        elif self.result.issues:
            self.result.status = ValidationStatus.WARNING
        else:
            self.result.status = ValidationStatus.PASSED
    
    async def _run_tool(self, command: List[str], cwd: Optional[Path] = None) -> ToolResult:
        """Run a command-line tool and capture its output."""
        tool_name = command[0]
        start_time = time.time()
        
        try:
            if cwd is None:
                cwd = self.project_root
            
            logger.debug(f"Running tool: {' '.join(command)} in {cwd}")
            
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            execution_time = timedelta(seconds=time.time() - start_time)
            
            return ToolResult(
                tool_name=tool_name,
                success=process.returncode == 0,
                output=stdout.decode('utf-8', errors='ignore'),
                error_output=stderr.decode('utf-8', errors='ignore'),
                exit_code=process.returncode,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = timedelta(seconds=time.time() - start_time)
            logger.error(f"Tool {tool_name} failed: {e}")
            
            return ToolResult(
                tool_name=tool_name,
                success=False,
                output="",
                error_output=str(e),
                exit_code=-1,
                execution_time=execution_time
            )
    
    def _add_issue(self, 
                   category: str,
                   severity: SeverityLevel,
                   message: str,
                   file_path: Optional[str] = None,
                   line_number: Optional[int] = None,
                   column: Optional[int] = None,
                   rule_id: Optional[str] = None,
                   suggestion: Optional[str] = None) -> None:
        """Add a validation issue to the result."""
        issue = ValidationIssue(
            category=category,
            severity=severity,
            message=message,
            file_path=file_path,
            line_number=line_number,
            column=column,
            rule_id=rule_id,
            suggestion=suggestion
        )
        
        self.result.issues.append(issue)
        logger.debug(f"Added {severity.value} issue: {message}")
    
    def _add_metric(self, metrics: StageMetrics) -> None:
        """Add metrics to the result."""
        self.result.metrics = metrics
    
    def _add_artifact(self, name: str, data: Any) -> None:
        """Add an artifact to the result."""
        self.result.artifacts[name] = data
    
    def _check_file_exists(self, file_path: Union[str, Path]) -> bool:
        """Check if a file exists relative to project root."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.project_root / path
        return path.exists()
    
    def _get_python_files(self, directory: Optional[Path] = None) -> List[Path]:
        """Get all Python files in the project."""
        if directory is None:
            directory = self.project_root
        
        python_files = []
        for pattern in ['**/*.py']:
            python_files.extend(directory.glob(pattern))
        
        # Filter out common exclusions
        exclusions = [
            '__pycache__',
            '.git',
            'build',
            'dist',
            '.venv',
            'venv',
            '.pytest_cache'
        ]
        
        filtered_files = []
        for file_path in python_files:
            if not any(exclusion in str(file_path) for exclusion in exclusions):
                filtered_files.append(file_path)
        
        return filtered_files
    
    def _count_lines_of_code(self, files: List[Path]) -> int:
        """Count total lines of code in files."""
        total_lines = 0
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines += sum(1 for line in f if line.strip())
            except Exception as e:
                logger.warning(f"Could not count lines in {file_path}: {e}")
        
        return total_lines
    
    def _parse_ruff_output(self, output: str) -> List[ValidationIssue]:
        """Parse Ruff output into validation issues."""
        issues = []
        for line in output.strip().split('\n'):
            if not line or line.startswith('Found'):
                continue
            
            try:
                # Ruff output format: file:line:column: code message
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    file_path = parts[0]
                    line_number = int(parts[1]) if parts[1].isdigit() else None
                    column = int(parts[2]) if parts[2].isdigit() else None
                    message_part = parts[3].strip()
                    
                    # Extract rule code if present
                    rule_id = None
                    if ' ' in message_part:
                        first_word = message_part.split(' ')[0]
                        if first_word.startswith(('E', 'W', 'F', 'C', 'N')):
                            rule_id = first_word
                            message = message_part[len(first_word):].strip()
                        else:
                            message = message_part
                    else:
                        message = message_part
                    
                    # Determine severity based on rule type
                    severity = SeverityLevel.MEDIUM
                    if rule_id:
                        if rule_id.startswith('E') or rule_id.startswith('F'):
                            severity = SeverityLevel.HIGH
                        elif rule_id.startswith('W'):
                            severity = SeverityLevel.MEDIUM
                        elif rule_id.startswith('C') or rule_id.startswith('N'):
                            severity = SeverityLevel.LOW
                    
                    issues.append(ValidationIssue(
                        category="linting",
                        severity=severity,
                        message=message,
                        file_path=file_path,
                        line_number=line_number,
                        column=column,
                        rule_id=rule_id
                    ))
                    
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse Ruff output line: {line} ({e})")
        
        return issues
    
    def _parse_mypy_output(self, output: str) -> List[ValidationIssue]:
        """Parse MyPy output into validation issues."""
        issues = []
        for line in output.strip().split('\n'):
            if not line or line.startswith('Success') or line.startswith('Found'):
                continue
            
            try:
                # MyPy output format: file:line: level: message
                parts = line.split(':', 3)
                if len(parts) >= 3:
                    file_path = parts[0]
                    line_number = int(parts[1]) if parts[1].isdigit() else None
                    level_and_message = parts[2].strip()
                    
                    # Determine severity
                    severity = SeverityLevel.MEDIUM
                    if 'error' in level_and_message.lower():
                        severity = SeverityLevel.HIGH
                    elif 'warning' in level_and_message.lower():
                        severity = SeverityLevel.MEDIUM
                    elif 'note' in level_and_message.lower():
                        severity = SeverityLevel.LOW
                    
                    issues.append(ValidationIssue(
                        category="type_checking",
                        severity=severity,
                        message=level_and_message,
                        file_path=file_path,
                        line_number=line_number
                    ))
                    
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse MyPy output line: {line} ({e})")
        
        return issues