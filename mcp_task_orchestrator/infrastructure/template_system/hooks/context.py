"""
Context management for template hook execution.

Provides intelligent context building, management, and preservation
with executive dysfunction-aware features for seamless workflow continuation.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

from .base import HookContext

logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    """
    Comprehensive execution context for template processing.
    
    Designed to support executive dysfunction by maintaining complete
    context across interruptions and providing clear state recovery.
    """
    # Core identifiers
    execution_id: str
    session_id: str
    template_id: str
    
    # Execution state
    current_phase: str
    phase_index: int
    total_phases: int
    execution_status: str  # "running", "paused", "completed", "failed"
    
    # Workspace management
    base_workspace_path: str
    isolated_workspaces: Dict[str, str]
    
    # Agent coordination
    spawned_agents: List[str]
    active_agents: Set[str]
    agent_assignments: Dict[str, Dict[str, Any]]
    
    # Document management
    associated_documents: List[str]
    loaded_document_content: Dict[str, str]
    document_modifications: List[Dict[str, Any]]
    
    # Progress tracking
    completed_phases: List[str]
    phase_results: Dict[str, Any]
    execution_artifacts: List[Dict[str, Any]]
    
    # Executive dysfunction support
    checkpoint_history: List[Dict[str, Any]]
    interruption_points: List[Dict[str, Any]]
    recovery_hints: Dict[str, Any]
    cognitive_load_tracking: Dict[str, Any]
    
    # Metadata
    template_parameters: Dict[str, Any]
    execution_metadata: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    
    # Timestamps
    started_at: datetime
    last_activity_at: datetime
    current_phase_started_at: datetime
    estimated_completion_at: Optional[datetime] = None
    
    def to_hook_context(self) -> HookContext:
        """Convert to HookContext for hook execution."""
        return HookContext(
            template_id=self.template_id,
            execution_id=self.execution_id,
            session_id=self.session_id,
            current_phase=self.current_phase,
            phase_index=self.phase_index,
            total_phases=self.total_phases,
            agent_id=None,  # Will be set by individual hooks
            spawned_agents=self.spawned_agents.copy(),
            active_agents=self.active_agents.copy(),
            workspace_path=self.base_workspace_path,
            isolated_workspaces=self.isolated_workspaces.copy(),
            parameters=self.template_parameters.copy(),
            metadata=self.execution_metadata.copy(),
            template_metadata=self.execution_metadata.get("template_metadata", {}),
            artifacts=self.execution_artifacts.copy(),
            associated_documents=self.associated_documents.copy(),
            execution_history=self.checkpoint_history.copy(),
            checkpoint_data=self.recovery_hints.copy(),
            interruption_safe_point=None,
            recovery_context=self.recovery_hints.copy(),
            cognitive_load_indicators=self.cognitive_load_tracking.copy(),
            execution_started_at=self.started_at,
            current_phase_started_at=self.current_phase_started_at,
            last_checkpoint_at=self.last_activity_at,
            last_activity_at=self.last_activity_at
        )
    
    def update_from_hook_context(self, hook_context: HookContext) -> None:
        """Update execution context from hook results."""
        # Update agent information
        self.spawned_agents = hook_context.spawned_agents.copy()
        self.active_agents = hook_context.active_agents.copy()
        self.isolated_workspaces.update(hook_context.isolated_workspaces)
        
        # Update artifacts and documents
        self.execution_artifacts = hook_context.artifacts.copy()
        self.associated_documents = hook_context.associated_documents.copy()
        
        # Update metadata and checkpoints
        self.execution_metadata.update(hook_context.metadata)
        self.recovery_hints.update(hook_context.recovery_context)
        self.cognitive_load_tracking.update(hook_context.cognitive_load_indicators)
        
        # Update timestamps
        self.last_activity_at = hook_context.last_activity_at or datetime.now()
        if hook_context.current_phase_started_at:
            self.current_phase_started_at = hook_context.current_phase_started_at


class ContextManager:
    """
    Manages execution context lifecycle with ED-aware features.
    
    Provides context creation, persistence, recovery, and cleanup
    with automatic checkpointing for executive dysfunction support.
    """
    
    def __init__(self, base_workspace_dir: Optional[Path] = None):
        self.base_workspace_dir = base_workspace_dir or Path.cwd() / ".task_orchestrator"
        self.context_storage_dir = self.base_workspace_dir / "execution_contexts"
        self.context_storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Active contexts (in-memory)
        self._active_contexts: Dict[str, ExecutionContext] = {}
        
        # Executive dysfunction support settings
        self.auto_checkpoint_interval = timedelta(minutes=2)
        self.context_retention_days = 7
        self.max_active_contexts = 10
    
    async def create_execution_context(
        self,
        template_id: str,
        session_id: str,
        template_parameters: Dict[str, Any],
        template_metadata: Dict[str, Any]
    ) -> ExecutionContext:
        """
        Create new execution context with ED-aware initialization.
        
        Args:
            template_id: Template being executed
            session_id: Orchestrator session ID
            template_parameters: Parameters for template
            template_metadata: Template metadata and configuration
            
        Returns:
            Initialized execution context
        """
        execution_id = f"{template_id}_{datetime.now().timestamp()}"
        
        # Create workspace directory
        workspace_path = self.base_workspace_dir / "workspaces" / execution_id
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize context
        context = ExecutionContext(
            execution_id=execution_id,
            session_id=session_id,
            template_id=template_id,
            current_phase="initialization",
            phase_index=0,
            total_phases=template_metadata.get("total_phases", 1),
            execution_status="running",
            base_workspace_path=str(workspace_path),
            isolated_workspaces={},
            spawned_agents=[],
            active_agents=set(),
            agent_assignments={},
            associated_documents=[],
            loaded_document_content={},
            document_modifications=[],
            completed_phases=[],
            phase_results={},
            execution_artifacts=[],
            checkpoint_history=[],
            interruption_points=[],
            recovery_hints={},
            cognitive_load_tracking={},
            template_parameters=template_parameters.copy(),
            execution_metadata={
                "template_metadata": template_metadata.copy(),
                "workspace_path": str(workspace_path),
                "created_with_ed_support": True
            },
            performance_metrics={},
            started_at=datetime.now(),
            last_activity_at=datetime.now(),
            current_phase_started_at=datetime.now()
        )
        
        # Store in active contexts
        self._active_contexts[execution_id] = context
        
        # Persist context
        await self._persist_context(context)
        
        # Create initial checkpoint
        await self.create_checkpoint(context, "initialization", "Initial execution context created")
        
        logger.info(f"Created execution context: {execution_id} with ED support")
        
        return context
    
    async def get_execution_context(self, execution_id: str) -> Optional[ExecutionContext]:
        """
        Get execution context by ID.
        
        Args:
            execution_id: Execution context ID
            
        Returns:
            Execution context or None if not found
        """
        # Check active contexts first
        if execution_id in self._active_contexts:
            return self._active_contexts[execution_id]
        
        # Try to load from disk
        context = await self._load_context(execution_id)
        if context:
            self._active_contexts[execution_id] = context
            
        return context
    
    async def update_execution_context(
        self,
        execution_id: str,
        hook_context: HookContext
    ) -> bool:
        """
        Update execution context from hook results.
        
        Args:
            execution_id: Execution context ID
            hook_context: Hook context with updates
            
        Returns:
            True if updated successfully
        """
        context = await self.get_execution_context(execution_id)
        if not context:
            return False
        
        # Update context from hook results
        context.update_from_hook_context(hook_context)
        
        # Persist updates
        await self._persist_context(context)
        
        # Check if auto-checkpoint is needed
        await self._check_auto_checkpoint(context)
        
        return True
    
    async def transition_phase(
        self,
        execution_id: str,
        new_phase: str,
        phase_index: int,
        phase_results: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Transition to new execution phase with checkpoint.
        
        Args:
            execution_id: Execution context ID
            new_phase: New phase name
            phase_index: New phase index
            phase_results: Results from previous phase
            
        Returns:
            True if transition successful
        """
        context = await self.get_execution_context(execution_id)
        if not context:
            return False
        
        # Record previous phase completion
        if context.current_phase and context.current_phase != "initialization":
            context.completed_phases.append(context.current_phase)
            if phase_results:
                context.phase_results[context.current_phase] = phase_results
        
        # Update phase information
        old_phase = context.current_phase
        context.current_phase = new_phase
        context.phase_index = phase_index
        context.current_phase_started_at = datetime.now()
        context.last_activity_at = datetime.now()
        
        # Create checkpoint for phase transition
        checkpoint_name = f"phase_transition_{old_phase}_to_{new_phase}"
        await self.create_checkpoint(
            context,
            checkpoint_name,
            f"Transitioned from {old_phase} to {new_phase}"
        )
        
        # Persist context
        await self._persist_context(context)
        
        logger.info(f"Context {execution_id} transitioned: {old_phase} -> {new_phase}")
        
        return True
    
    async def create_checkpoint(
        self,
        context: ExecutionContext,
        checkpoint_name: str,
        description: str = ""
    ) -> str:
        """
        Create checkpoint for executive dysfunction recovery.
        
        Args:
            context: Execution context to checkpoint
            checkpoint_name: Name for the checkpoint
            description: Optional description
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = f"{context.execution_id}_{checkpoint_name}_{datetime.now().timestamp()}"
        
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "checkpoint_name": checkpoint_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "execution_state": {
                "current_phase": context.current_phase,
                "phase_index": context.phase_index,
                "execution_status": context.execution_status,
                "completed_phases": context.completed_phases.copy(),
                "active_agents": list(context.active_agents),
                "artifacts_count": len(context.execution_artifacts)
            },
            "recovery_hints": {
                "next_suggested_action": self._generate_recovery_suggestion(context),
                "context_summary": self._generate_context_summary(context),
                "cognitive_load_state": context.cognitive_load_tracking.copy()
            }
        }
        
        # Add to context history
        context.checkpoint_history.append(checkpoint_data)
        context.recovery_hints[checkpoint_name] = checkpoint_data["recovery_hints"]
        
        # Save checkpoint to separate file
        checkpoint_file = self.context_storage_dir / f"{checkpoint_id}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2, default=str)
        
        logger.debug(f"Created checkpoint: {checkpoint_name} for {context.execution_id}")
        
        return checkpoint_id
    
    async def recover_from_interruption(
        self,
        execution_id: str,
        checkpoint_name: Optional[str] = None
    ) -> Optional[Tuple[ExecutionContext, Dict[str, Any]]]:
        """
        Recover execution context from interruption.
        
        Args:
            execution_id: Execution context ID
            checkpoint_name: Specific checkpoint to recover from (latest if None)
            
        Returns:
            Tuple of (recovered context, recovery guidance) or None if failed
        """
        context = await self.get_execution_context(execution_id)
        if not context:
            return None
        
        # Find appropriate checkpoint
        if checkpoint_name:
            checkpoint_data = context.recovery_hints.get(checkpoint_name)
        else:
            # Use latest checkpoint
            checkpoint_data = context.checkpoint_history[-1] if context.checkpoint_history else None
        
        if not checkpoint_data:
            logger.warning(f"No checkpoint found for recovery: {execution_id}")
            return None
        
        # Generate recovery guidance
        recovery_guidance = {
            "interruption_duration": self._calculate_interruption_duration(context),
            "context_summary": checkpoint_data.get("recovery_hints", {}).get("context_summary", ""),
            "suggested_next_action": checkpoint_data.get("recovery_hints", {}).get("next_suggested_action", ""),
            "cognitive_state_notes": checkpoint_data.get("recovery_hints", {}).get("cognitive_load_state", {}),
            "recovery_success_probability": self._estimate_recovery_probability(context, checkpoint_data)
        }
        
        # Update context for recovery
        context.execution_status = "recovered"
        context.last_activity_at = datetime.now()
        
        # Record recovery event
        context.interruption_points.append({
            "recovery_time": datetime.now().isoformat(),
            "checkpoint_used": checkpoint_name or "latest",
            "interruption_duration_minutes": recovery_guidance["interruption_duration"],
            "recovery_guidance": recovery_guidance
        })
        
        await self._persist_context(context)
        
        logger.info(f"Recovered context {execution_id} from interruption using checkpoint")
        
        return context, recovery_guidance
    
    async def cleanup_context(
        self,
        execution_id: str,
        preserve_artifacts: bool = True
    ) -> bool:
        """
        Clean up execution context and resources.
        
        Args:
            execution_id: Execution context ID
            preserve_artifacts: Whether to preserve artifacts
            
        Returns:
            True if cleanup successful
        """
        context = await self.get_execution_context(execution_id)
        if not context:
            return False
        
        try:
            # Archive context before cleanup
            await self._archive_context(context, preserve_artifacts)
            
            # Remove from active contexts
            if execution_id in self._active_contexts:
                del self._active_contexts[execution_id]
            
            # Clean up workspace (if not preserving artifacts)
            if not preserve_artifacts:
                workspace_path = Path(context.base_workspace_path)
                if workspace_path.exists():
                    import shutil
                    shutil.rmtree(workspace_path)
            
            logger.info(f"Cleaned up context: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup context {execution_id}: {e}")
            return False
    
    async def list_active_contexts(self) -> List[Dict[str, Any]]:
        """List all active execution contexts."""
        contexts_info = []
        
        for execution_id, context in self._active_contexts.items():
            contexts_info.append({
                "execution_id": execution_id,
                "template_id": context.template_id,
                "current_phase": context.current_phase,
                "progress_percentage": (context.phase_index / max(context.total_phases, 1)) * 100,
                "execution_status": context.execution_status,
                "started_at": context.started_at.isoformat(),
                "last_activity_at": context.last_activity_at.isoformat(),
                "active_agents": len(context.active_agents),
                "artifacts_count": len(context.execution_artifacts),
                "checkpoints_count": len(context.checkpoint_history)
            })
        
        return contexts_info
    
    async def _persist_context(self, context: ExecutionContext) -> None:
        """Persist execution context to disk."""
        context_file = self.context_storage_dir / f"{context.execution_id}_context.json"
        
        # Convert context to serializable format
        context_dict = asdict(context)
        context_dict["active_agents"] = list(context_dict["active_agents"])  # Convert set to list
        
        with open(context_file, 'w') as f:
            json.dump(context_dict, f, indent=2, default=str)
    
    async def _load_context(self, execution_id: str) -> Optional[ExecutionContext]:
        """Load execution context from disk."""
        context_file = self.context_storage_dir / f"{execution_id}_context.json"
        
        if not context_file.exists():
            return None
        
        try:
            with open(context_file, 'r') as f:
                context_dict = json.load(f)
            
            # Convert timestamps back to datetime objects
            for timestamp_field in ["started_at", "last_activity_at", "current_phase_started_at"]:
                if timestamp_field in context_dict and context_dict[timestamp_field]:
                    context_dict[timestamp_field] = datetime.fromisoformat(context_dict[timestamp_field])
            
            # Convert active_agents back to set
            context_dict["active_agents"] = set(context_dict["active_agents"])
            
            return ExecutionContext(**context_dict)
            
        except Exception as e:
            logger.error(f"Failed to load context {execution_id}: {e}")
            return None
    
    async def _check_auto_checkpoint(self, context: ExecutionContext) -> None:
        """Check if automatic checkpoint is needed."""
        if not context.checkpoint_history:
            return
        
        last_checkpoint_time = datetime.fromisoformat(context.checkpoint_history[-1]["created_at"])
        
        if datetime.now() - last_checkpoint_time > self.auto_checkpoint_interval:
            await self.create_checkpoint(
                context,
                "auto_checkpoint",
                "Automatic checkpoint for ED support"
            )
    
    def _generate_recovery_suggestion(self, context: ExecutionContext) -> str:
        """Generate suggested next action for recovery."""
        if context.current_phase == "initialization":
            return "Context is in initialization phase. Continue with template setup."
        
        progress = (context.phase_index / max(context.total_phases, 1)) * 100
        
        if progress < 25:
            return f"Early in execution ({progress:.1f}% complete). Focus on completing {context.current_phase} phase."
        elif progress < 75:
            return f"Midway through execution ({progress:.1f}% complete). Review {context.current_phase} progress and continue."
        else:
            return f"Nearing completion ({progress:.1f}% complete). Focus on finishing {context.current_phase} and cleanup."
    
    def _generate_context_summary(self, context: ExecutionContext) -> str:
        """Generate human-readable context summary."""
        summary_parts = [
            f"Template: {context.template_id}",
            f"Phase: {context.current_phase} ({context.phase_index + 1}/{context.total_phases})",
            f"Active agents: {len(context.active_agents)}",
            f"Artifacts: {len(context.execution_artifacts)}",
            f"Duration: {self._format_duration(datetime.now() - context.started_at)}"
        ]
        
        return " | ".join(summary_parts)
    
    def _calculate_interruption_duration(self, context: ExecutionContext) -> float:
        """Calculate interruption duration in minutes."""
        return (datetime.now() - context.last_activity_at).total_seconds() / 60
    
    def _estimate_recovery_probability(
        self,
        context: ExecutionContext,
        checkpoint_data: Dict[str, Any]
    ) -> float:
        """Estimate probability of successful recovery."""
        base_probability = 0.8
        
        # Reduce probability based on interruption duration
        interruption_minutes = self._calculate_interruption_duration(context)
        if interruption_minutes > 60:  # More than 1 hour
            base_probability *= 0.9
        if interruption_minutes > 480:  # More than 8 hours (sleep)
            base_probability *= 0.8
        if interruption_minutes > 1440:  # More than 1 day
            base_probability *= 0.6
        
        # Boost probability for good checkpoint quality
        if checkpoint_data.get("recovery_hints"):
            base_probability *= 1.1
        
        return min(base_probability, 1.0)
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration for human reading."""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    async def _archive_context(
        self,
        context: ExecutionContext,
        preserve_artifacts: bool
    ) -> None:
        """Archive completed context."""
        archive_dir = self.context_storage_dir / "archived"
        archive_dir.mkdir(exist_ok=True)
        
        archive_data = {
            "execution_id": context.execution_id,
            "template_id": context.template_id,
            "execution_status": context.execution_status,
            "completed_phases": context.completed_phases,
            "total_duration_minutes": (context.last_activity_at - context.started_at).total_seconds() / 60,
            "artifacts_count": len(context.execution_artifacts),
            "checkpoints_count": len(context.checkpoint_history),
            "archived_at": datetime.now().isoformat(),
            "artifacts_preserved": preserve_artifacts
        }
        
        if preserve_artifacts:
            archive_data["artifacts"] = context.execution_artifacts.copy()
        
        archive_file = archive_dir / f"{context.execution_id}_archive.json"
        with open(archive_file, 'w') as f:
            json.dump(archive_data, f, indent=2, default=str)


class ContextBuilder:
    """
    Builds rich context for hook execution.
    
    Provides intelligent context assembly with document loading,
    agent coordination, and executive dysfunction support features.
    """
    
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
    
    async def build_hook_context(
        self,
        execution_context: ExecutionContext,
        hook_id: str,
        agent_id: Optional[str] = None
    ) -> HookContext:
        """
        Build comprehensive hook context from execution context.
        
        Args:
            execution_context: Base execution context
            hook_id: Hook being executed
            agent_id: Optional agent ID if hook is agent-specific
            
        Returns:
            Enriched hook context
        """
        # Start with base hook context
        hook_context = execution_context.to_hook_context()
        
        # Set agent-specific information
        if agent_id:
            hook_context.agent_id = agent_id
            
            # Set agent workspace if available
            if agent_id in execution_context.isolated_workspaces:
                hook_context.workspace_path = execution_context.isolated_workspaces[agent_id]
        
        # Enrich with hook-specific context
        await self._enrich_context_for_hook(hook_context, hook_id, execution_context)
        
        return hook_context
    
    async def _enrich_context_for_hook(
        self,
        hook_context: HookContext,
        hook_id: str,
        execution_context: ExecutionContext
    ) -> None:
        """Enrich context with hook-specific information."""
        
        # Add hook-specific metadata
        hook_context.metadata["current_hook"] = hook_id
        hook_context.metadata["hook_execution_count"] = execution_context.execution_metadata.get("hook_executions", {}).get(hook_id, 0)
        
        # Add phase-specific information
        current_phase_config = execution_context.execution_metadata.get("phase_configs", {}).get(execution_context.current_phase, {})
        hook_context.metadata["current_phase_config"] = current_phase_config
        
        # Add cognitive load information
        hook_context.cognitive_load_indicators.update(execution_context.cognitive_load_tracking)
        
        # Add recovery context
        hook_context.recovery_context.update(execution_context.recovery_hints)
        
        # Set interruption safe point
        if execution_context.checkpoint_history:
            latest_checkpoint = execution_context.checkpoint_history[-1]
            hook_context.interruption_safe_point = latest_checkpoint["checkpoint_name"]