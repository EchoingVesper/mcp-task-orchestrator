"""
Base classes for the template hook system.

Provides the foundation for executive dysfunction-aware hook implementations
that support automated agent spawning and workflow coordination.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HookType(Enum):
    """Types of hooks in template execution lifecycle."""
    PRE_EXECUTION = "pre_execution"
    PHASE_INIT = "phase_initialization"
    PHASE_TRANSITION = "phase_transition"
    INTER_AGENT = "inter_agent_coordination"
    POST_EXECUTION = "post_execution"
    ERROR_HANDLING = "error_handling"
    CONTEXT_RECOVERY = "context_recovery"  # ED-specific
    OVERWHELM_PREVENTION = "overwhelm_prevention"  # ED-specific


@dataclass
class HookContext:
    """
    Context passed to hooks during execution.
    
    Designed to preserve all necessary context for executive dysfunction support,
    including session continuity and momentum preservation.
    """
    # Core execution context
    template_id: str
    execution_id: str
    session_id: str
    current_phase: str
    phase_index: int
    total_phases: int
    
    # Agent context
    agent_id: Optional[str] = None
    spawned_agents: List[str] = field(default_factory=list)
    active_agents: Set[str] = field(default_factory=set)
    
    # Workspace context
    workspace_path: str = ""
    isolated_workspaces: Dict[str, str] = field(default_factory=dict)
    
    # Template parameters and metadata
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    template_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Execution state
    artifacts: List[str] = field(default_factory=list)
    associated_documents: List[str] = field(default_factory=list)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Executive dysfunction support
    checkpoint_data: Dict[str, Any] = field(default_factory=dict)
    interruption_safe_point: Optional[str] = None
    recovery_context: Dict[str, Any] = field(default_factory=dict)
    cognitive_load_indicators: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps for momentum tracking
    execution_started_at: Optional[datetime] = None
    current_phase_started_at: Optional[datetime] = None
    last_checkpoint_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    
    def add_artifact(self, artifact_path: str, artifact_type: str = "file") -> None:
        """Add an artifact to the execution context."""
        artifact_info = {
            "path": artifact_path,
            "type": artifact_type,
            "created_at": datetime.now().isoformat(),
            "phase": self.current_phase
        }
        self.artifacts.append(artifact_info)
        self.metadata.setdefault("artifacts_by_phase", {})
        self.metadata["artifacts_by_phase"].setdefault(self.current_phase, [])
        self.metadata["artifacts_by_phase"][self.current_phase].append(artifact_info)
    
    def add_spawned_agent(self, agent_id: str, agent_type: str, workspace_path: str) -> None:
        """Register a newly spawned agent."""
        self.spawned_agents.append(agent_id)
        self.active_agents.add(agent_id)
        self.isolated_workspaces[agent_id] = workspace_path
        
        # Track agent spawning in execution history
        self.execution_history.append({
            "event": "agent_spawned",
            "agent_id": agent_id,
            "agent_type": agent_type,
            "workspace": workspace_path,
            "phase": self.current_phase,
            "timestamp": datetime.now().isoformat()
        })
    
    def create_checkpoint(self, checkpoint_name: str) -> None:
        """Create a checkpoint for executive dysfunction recovery."""
        checkpoint = {
            "name": checkpoint_name,
            "phase": self.current_phase,
            "phase_index": self.phase_index,
            "active_agents": list(self.active_agents),
            "artifacts": self.artifacts.copy(),
            "metadata": self.metadata.copy(),
            "timestamp": datetime.now().isoformat()
        }
        self.checkpoint_data[checkpoint_name] = checkpoint
        self.last_checkpoint_at = datetime.now()
        
        logger.info(f"Created checkpoint '{checkpoint_name}' for execution {self.execution_id}")
    
    def get_progress_percentage(self) -> float:
        """Calculate execution progress percentage."""
        if self.total_phases == 0:
            return 0.0
        return (self.phase_index / self.total_phases) * 100
    
    def get_execution_duration(self) -> Optional[float]:
        """Get total execution duration in seconds."""
        if self.execution_started_at is None:
            return None
        return (datetime.now() - self.execution_started_at).total_seconds()
    
    def update_cognitive_load(self, indicator: str, value: Any) -> None:
        """Update cognitive load indicators for ED support."""
        self.cognitive_load_indicators[indicator] = {
            "value": value,
            "updated_at": datetime.now().isoformat(),
            "phase": self.current_phase
        }


@dataclass
class HookResult:
    """Result returned by hook execution."""
    success: bool
    hook_id: str
    execution_time_ms: float
    message: str = ""
    
    # Updated context data
    metadata: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    spawned_agents: List[str] = field(default_factory=list)
    
    # Executive dysfunction support
    checkpoint_created: Optional[str] = None
    recovery_data: Dict[str, Any] = field(default_factory=dict)
    cognitive_load_impact: str = "neutral"  # "reduced", "neutral", "increased"
    
    # Error information (if success=False)
    error_type: Optional[str] = None
    error_details: Dict[str, Any] = field(default_factory=dict)
    rollback_required: bool = False
    
    def add_spawned_agent(self, agent_id: str) -> None:
        """Add a spawned agent to the result."""
        self.spawned_agents.append(agent_id)
        self.metadata.setdefault("agents_spawned", []).append(agent_id)
    
    def add_artifact(self, artifact_path: str, description: str = "") -> None:
        """Add an artifact to the result."""
        self.artifacts.append(artifact_path)
        self.metadata.setdefault("artifacts_created", []).append({
            "path": artifact_path,
            "description": description
        })
    
    def create_checkpoint(self, checkpoint_name: str, data: Dict[str, Any]) -> None:
        """Record checkpoint creation in result."""
        self.checkpoint_created = checkpoint_name
        self.recovery_data = data


class HookExecutionError(Exception):
    """Exception raised when hook execution fails."""
    
    def __init__(
        self,
        message: str,
        hook_id: str,
        context: HookContext,
        error_type: str = "execution_error",
        recoverable: bool = True
    ):
        super().__init__(message)
        self.hook_id = hook_id
        self.context = context
        self.error_type = error_type
        self.recoverable = recoverable
        self.occurred_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            "message": str(self),
            "hook_id": self.hook_id,
            "error_type": self.error_type,
            "recoverable": self.recoverable,
            "execution_id": self.context.execution_id,
            "phase": self.context.current_phase,
            "occurred_at": self.occurred_at.isoformat()
        }


class Hook(ABC):
    """
    Base class for all template hooks.
    
    Designed with executive dysfunction principles:
    - Clear, single responsibility
    - Predictable execution patterns
    - Built-in error handling and recovery
    - Context preservation across interruptions
    """
    
    def __init__(self, hook_id: str, description: str = ""):
        self.hook_id = hook_id
        self.description = description
        self.execution_count = 0
        self.success_count = 0
        self.average_execution_time = 0.0
    
    @abstractmethod
    async def execute(self, context: HookContext) -> HookResult:
        """
        Execute the hook with given context.
        
        Must be implemented by subclasses with specific hook logic.
        Should be designed to be:
        - Idempotent (safe to run multiple times)
        - Interruptible (can be safely stopped)
        - Recoverable (can resume from interruption)
        
        Args:
            context: Execution context with all necessary information
            
        Returns:
            HookResult with execution outcome and any created artifacts
            
        Raises:
            HookExecutionError: If execution fails
        """
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """
        Return list of hook IDs this hook depends on.
        
        Used for dependency resolution and execution ordering.
        
        Returns:
            List of hook IDs that must execute before this hook
        """
        pass
    
    @abstractmethod
    def supports_rollback(self) -> bool:
        """
        Return whether this hook supports rollback operations.
        
        Returns:
            True if rollback is supported, False otherwise
        """
        pass
    
    async def rollback(self, context: HookContext) -> HookResult:
        """
        Rollback changes made by this hook.
        
        Default implementation raises NotImplementedError.
        Override in subclasses that support rollback.
        
        Args:
            context: Execution context
            
        Returns:
            HookResult indicating rollback success/failure
            
        Raises:
            NotImplementedError: If rollback is not supported
        """
        if not self.supports_rollback():
            raise NotImplementedError(f"Hook {self.hook_id} does not support rollback")
        
        # Default rollback implementation
        return HookResult(
            success=False,
            hook_id=self.hook_id,
            execution_time_ms=0.0,
            message=f"Rollback not implemented for {self.hook_id}",
            error_type="rollback_not_implemented"
        )
    
    def get_ed_support_features(self) -> Dict[str, bool]:
        """
        Return executive dysfunction support features of this hook.
        
        Returns:
            Dictionary of ED support features and their availability
        """
        return {
            "creates_checkpoints": False,
            "reduces_decisions": False,
            "preserves_momentum": False,
            "delegates_pressure": False,
            "prevents_overwhelm": False,
            "supports_interruption": False
        }
    
    def validate_context(self, context: HookContext) -> List[str]:
        """
        Validate that context contains required information for this hook.
        
        Args:
            context: Execution context to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Basic context validation
        required_fields = [
            "template_id", "execution_id", "session_id",
            "current_phase", "workspace_path"
        ]
        
        for field in required_fields:
            if not getattr(context, field, None):
                errors.append(f"Required context field missing: {field}")
        
        return errors
    
    def _record_execution_metrics(self, execution_time_ms: float, success: bool) -> None:
        """Record execution metrics for performance monitoring."""
        self.execution_count += 1
        if success:
            self.success_count += 1
        
        # Update rolling average execution time
        if self.execution_count == 1:
            self.average_execution_time = execution_time_ms
        else:
            self.average_execution_time = (
                (self.average_execution_time * (self.execution_count - 1) + execution_time_ms) /
                self.execution_count
            )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this hook."""
        return {
            "hook_id": self.hook_id,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "success_rate": self.success_count / max(self.execution_count, 1),
            "average_execution_time_ms": self.average_execution_time
        }
    
    def __str__(self) -> str:
        return f"Hook({self.hook_id})"
    
    def __repr__(self) -> str:
        return f"Hook(id='{self.hook_id}', description='{self.description}')"


class ExecutiveDysfunctionHook(Hook):
    """
    Base class for hooks specifically designed for executive dysfunction support.
    
    Provides additional methods and guarantees for ED-aware hook implementations.
    """
    
    def __init__(self, hook_id: str, description: str = "", ed_features: Dict[str, bool] = None):
        super().__init__(hook_id, description)
        self.ed_features = ed_features or {}
    
    @abstractmethod
    def estimate_cognitive_load(self, context: HookContext) -> str:
        """
        Estimate the cognitive load impact of this hook.
        
        Returns:
            "low", "medium", "high" - cognitive load estimate
        """
        pass
    
    @abstractmethod
    def create_recovery_checkpoint(self, context: HookContext) -> Dict[str, Any]:
        """
        Create checkpoint data for executive dysfunction recovery.
        
        Returns:
            Dictionary with recovery data
        """
        pass
    
    def get_ed_support_features(self) -> Dict[str, bool]:
        """Return ED-specific support features."""
        base_features = super().get_ed_support_features()
        base_features.update({
            "creates_checkpoints": True,
            "supports_interruption": True,
            "preserves_momentum": True
        })
        base_features.update(self.ed_features)
        return base_features
    
    async def handle_interruption(self, context: HookContext) -> HookResult:
        """
        Handle execution interruption gracefully.
        
        Default implementation creates checkpoint and returns success.
        """
        checkpoint_data = self.create_recovery_checkpoint(context)
        checkpoint_name = f"{self.hook_id}_interruption_{datetime.now().timestamp()}"
        
        context.create_checkpoint(checkpoint_name)
        
        return HookResult(
            success=True,
            hook_id=self.hook_id,
            execution_time_ms=0.0,
            message=f"Gracefully handled interruption in {self.hook_id}",
            checkpoint_created=checkpoint_name,
            recovery_data=checkpoint_data,
            cognitive_load_impact="reduced"
        )