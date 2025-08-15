"""
Data models for the Multi-Stage Validation Pipeline.

This module defines the core data structures used throughout the validation
pipeline for representing results, configurations, and stage outputs.
"""

from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator


class ValidationStatus(str, Enum):
    """Status of a validation stage or pipeline."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"
    ERROR = "error"


class SeverityLevel(str, Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    category: str
    severity: SeverityLevel
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    rule_id: Optional[str] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'category': self.category,
            'severity': self.severity.value,
            'message': self.message,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'column': self.column,
            'rule_id': self.rule_id,
            'suggestion': self.suggestion
        }


@dataclass
class StageMetrics:
    """Metrics collected during stage execution."""
    execution_time: timedelta
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    files_processed: int = 0
    tests_run: int = 0
    lines_of_code: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'execution_time_seconds': self.execution_time.total_seconds(),
            'memory_usage_mb': self.memory_usage_mb,
            'cpu_usage_percent': self.cpu_usage_percent,
            'files_processed': self.files_processed,
            'tests_run': self.tests_run,
            'lines_of_code': self.lines_of_code
        }


@dataclass
class ValidationResult:
    """Result of a single validation stage."""
    stage_id: int
    stage_name: str
    status: ValidationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    issues: List[ValidationIssue] = field(default_factory=list)
    metrics: Optional[StageMetrics] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate stage duration."""
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def passed(self) -> bool:
        """Check if stage passed validation."""
        return self.status in [ValidationStatus.PASSED, ValidationStatus.WARNING]
    
    @property
    def critical_issues(self) -> List[ValidationIssue]:
        """Get critical issues only."""
        return [issue for issue in self.issues 
                if issue.severity == SeverityLevel.CRITICAL]
    
    @property
    def high_issues(self) -> List[ValidationIssue]:
        """Get high severity issues."""
        return [issue for issue in self.issues 
                if issue.severity == SeverityLevel.HIGH]
    
    def get_issues_by_severity(self, severity: SeverityLevel) -> List[ValidationIssue]:
        """Get issues filtered by severity level."""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'stage_id': self.stage_id,
            'stage_name': self.stage_name,
            'status': self.status.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration.total_seconds() if self.duration else None,
            'issues': [issue.to_dict() for issue in self.issues],
            'metrics': self.metrics.to_dict() if self.metrics else None,
            'artifacts': self.artifacts,
            'error_message': self.error_message,
            'passed': self.passed,
            'critical_issues_count': len(self.critical_issues),
            'high_issues_count': len(self.high_issues)
        }


@dataclass
class PipelineResult:
    """Result of the entire validation pipeline."""
    pipeline_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    stages: List[ValidationResult] = field(default_factory=list)
    overall_status: ValidationStatus = ValidationStatus.PENDING
    configuration: Dict[str, Any] = field(default_factory=dict)
    environment_info: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate total pipeline duration."""
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def passed(self) -> bool:
        """Check if entire pipeline passed."""
        return self.overall_status in [ValidationStatus.PASSED, ValidationStatus.WARNING]
    
    @property
    def failed_stages(self) -> List[ValidationResult]:
        """Get stages that failed validation."""
        return [stage for stage in self.stages 
                if stage.status in [ValidationStatus.FAILED, ValidationStatus.ERROR]]
    
    @property
    def total_issues(self) -> int:
        """Get total number of issues across all stages."""
        return sum(len(stage.issues) for stage in self.stages)
    
    @property
    def critical_issues_count(self) -> int:
        """Get total critical issues across all stages."""
        return sum(len(stage.critical_issues) for stage in self.stages)
    
    def get_stage_by_id(self, stage_id: int) -> Optional[ValidationResult]:
        """Get stage result by ID."""
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'pipeline_id': self.pipeline_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration.total_seconds() if self.duration else None,
            'overall_status': self.overall_status.value,
            'passed': self.passed,
            'stages': [stage.to_dict() for stage in self.stages],
            'failed_stages_count': len(self.failed_stages),
            'total_issues': self.total_issues,
            'critical_issues_count': self.critical_issues_count,
            'configuration': self.configuration,
            'environment_info': self.environment_info
        }


class PipelineConfig(BaseModel):
    """Configuration for the validation pipeline."""
    name: str = "MCP Task Orchestrator Validation"
    version: str = "2.0"
    fail_fast: bool = True
    parallel_execution: bool = False
    timeout_minutes: int = 30
    project_root: str = Field(default=".")
    output_directory: str = "validation_results"
    
    class Config:
        use_enum_values = True


class StageConfig(BaseModel):
    """Configuration for a single validation stage."""
    name: str
    enabled: bool = True
    timeout_minutes: int = 10
    fail_on_error: bool = True
    tools: List[str] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True


class QualityGate(BaseModel):
    """Quality gate thresholds for validation stages."""
    metric_name: str
    threshold_value: Union[int, float, bool]
    comparison_operator: str = "gte"  # gte, lte, eq, ne
    severity: SeverityLevel = SeverityLevel.HIGH
    
    def evaluate(self, actual_value: Union[int, float, bool]) -> bool:
        """Evaluate if the actual value passes the quality gate."""
        if self.comparison_operator == "gte":
            return actual_value >= self.threshold_value
        elif self.comparison_operator == "lte":
            return actual_value <= self.threshold_value
        elif self.comparison_operator == "eq":
            return actual_value == self.threshold_value
        elif self.comparison_operator == "ne":
            return actual_value != self.threshold_value
        else:
            raise ValueError(f"Unknown comparison operator: {self.comparison_operator}")


@dataclass
class ToolResult:
    """Result from a specific validation tool."""
    tool_name: str
    success: bool
    output: str
    error_output: str = ""
    exit_code: int = 0
    execution_time: Optional[timedelta] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'tool_name': self.tool_name,
            'success': self.success,
            'output': self.output,
            'error_output': self.error_output,
            'exit_code': self.exit_code,
            'execution_time_seconds': self.execution_time.total_seconds() if self.execution_time else None
        }


@dataclass
class EnvironmentInfo:
    """Information about the validation environment."""
    python_version: str
    platform: str
    architecture: str
    hostname: str
    user: str
    working_directory: str
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'python_version': self.python_version,
            'platform': self.platform,
            'architecture': self.architecture,
            'hostname': self.hostname,
            'user': self.user,
            'working_directory': self.working_directory,
            'git_branch': self.git_branch,
            'git_commit': self.git_commit
        }