"""
Built-in hooks for common template operations.

Provides executive dysfunction-aware hook implementations for:
- Git operations (branch creation, commits)
- Workspace management
- Agent spawning and coordination
- Document association
- Progress tracking and checkpointing
"""

import asyncio
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .base import Hook, ExecutiveDysfunctionHook, HookContext, HookResult, HookExecutionError

logger = logging.getLogger(__name__)


class GitBranchHook(ExecutiveDysfunctionHook):
    """
    Creates git branches automatically to eliminate naming decisions.
    
    ED Features:
    - Automatic branch naming (no decisions required)
    - Safe branch creation with conflict detection
    - Automatic cleanup on rollback
    """
    
    def __init__(self):
        super().__init__(
            hook_id="git_branch_creation",
            description="Automatically create git branch for template execution",
            ed_features={
                "reduces_decisions": True,
                "creates_checkpoints": True,
                "supports_interruption": True
            }
        )
        self._created_branches: List[str] = []
    
    async def execute(self, context: HookContext) -> HookResult:
        """Create git branch with automatic naming."""
        try:
            # Generate branch name automatically (no user decision needed)
            branch_name = self._generate_branch_name(context)
            
            # Check if we're in a git repository
            if not self._is_git_repository(context.workspace_path):
                return HookResult(
                    success=True,
                    hook_id=self.hook_id,
                    execution_time_ms=0.0,
                    message="Not in git repository - skipping branch creation",
                    cognitive_load_impact="reduced"
                )
            
            # Check if branch already exists
            if self._branch_exists(branch_name, context.workspace_path):
                # Use existing branch or create variant
                branch_name = self._create_unique_branch_name(branch_name, context.workspace_path)
            
            # Create and switch to branch
            success = await self._create_and_checkout_branch(branch_name, context.workspace_path)
            
            if success:
                self._created_branches.append(branch_name)
                
                # Update context
                context.metadata["git_branch"] = branch_name
                context.metadata["git_branch_created"] = True
                
                # Create checkpoint for rollback
                checkpoint_data = self.create_recovery_checkpoint(context)
                
                return HookResult(
                    success=True,
                    hook_id=self.hook_id,
                    execution_time_ms=0.0,  # Will be updated by executor
                    message=f"Created and switched to branch: {branch_name}",
                    metadata={"git_branch": branch_name},
                    cognitive_load_impact="reduced",
                    recovery_data=checkpoint_data
                )
            else:
                return HookResult(
                    success=False,
                    hook_id=self.hook_id,
                    execution_time_ms=0.0,
                    message=f"Failed to create branch: {branch_name}",
                    error_type="git_branch_creation_failed"
                )
                
        except Exception as e:
            raise HookExecutionError(
                f"Git branch creation failed: {e}",
                self.hook_id,
                context,
                error_type="git_operation_error"
            )
    
    def get_dependencies(self) -> List[str]:
        """No dependencies for git branch creation."""
        return []
    
    def supports_rollback(self) -> bool:
        """Support rollback by deleting created branch."""
        return True
    
    async def rollback(self, context: HookContext) -> HookResult:
        """Rollback by deleting created branch."""
        branch_name = context.metadata.get("git_branch")
        if not branch_name:
            return HookResult(
                success=True,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message="No branch to rollback"
            )
        
        try:
            # Switch to main/master before deleting
            await self._checkout_main_branch(context.workspace_path)
            
            # Delete the created branch
            success = await self._delete_branch(branch_name, context.workspace_path)
            
            if success and branch_name in self._created_branches:
                self._created_branches.remove(branch_name)
            
            return HookResult(
                success=success,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Rolled back branch creation: {branch_name}"
            )
            
        except Exception as e:
            return HookResult(
                success=False,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Rollback failed: {e}",
                error_type="rollback_error"
            )
    
    def estimate_cognitive_load(self, context: HookContext) -> str:
        """Very low cognitive load - completely automated."""
        return "low"
    
    def create_recovery_checkpoint(self, context: HookContext) -> Dict[str, Any]:
        """Create checkpoint data for recovery."""
        return {
            "created_branches": self._created_branches.copy(),
            "current_branch": context.metadata.get("git_branch"),
            "workspace_path": context.workspace_path
        }
    
    def _generate_branch_name(self, context: HookContext) -> str:
        """Generate automatic branch name to eliminate decisions."""
        # Use template ID and timestamp for uniqueness
        template_part = context.template_id.replace("_", "-")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"template/{template_part}-{timestamp}"
    
    def _is_git_repository(self, workspace_path: str) -> bool:
        """Check if directory is a git repository."""
        git_dir = Path(workspace_path) / ".git"
        return git_dir.exists()
    
    def _branch_exists(self, branch_name: str, workspace_path: str) -> bool:
        """Check if branch exists."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--verify", f"refs/heads/{branch_name}"],
                cwd=workspace_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _create_unique_branch_name(self, base_name: str, workspace_path: str) -> str:
        """Create unique branch name if base name exists."""
        counter = 1
        while True:
            candidate = f"{base_name}-{counter}"
            if not self._branch_exists(candidate, workspace_path):
                return candidate
            counter += 1
    
    async def _create_and_checkout_branch(self, branch_name: str, workspace_path: str) -> bool:
        """Create and checkout git branch."""
        try:
            # Create branch
            create_result = await asyncio.create_subprocess_exec(
                "git", "checkout", "-b", branch_name,
                cwd=workspace_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await create_result.communicate()
            
            if create_result.returncode == 0:
                logger.info(f"Created and checked out branch: {branch_name}")
                return True
            else:
                logger.error(f"Failed to create branch {branch_name}: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Git branch creation error: {e}")
            return False
    
    async def _checkout_main_branch(self, workspace_path: str) -> bool:
        """Checkout main or master branch."""
        for branch in ["main", "master"]:
            try:
                checkout_result = await asyncio.create_subprocess_exec(
                    "git", "checkout", branch,
                    cwd=workspace_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await checkout_result.communicate()
                
                if checkout_result.returncode == 0:
                    return True
                    
            except Exception:
                continue
        
        return False
    
    async def _delete_branch(self, branch_name: str, workspace_path: str) -> bool:
        """Delete git branch."""
        try:
            delete_result = await asyncio.create_subprocess_exec(
                "git", "branch", "-D", branch_name,
                cwd=workspace_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await delete_result.communicate()
            return delete_result.returncode == 0
            
        except Exception:
            return False


class WorkspaceSetupHook(ExecutiveDysfunctionHook):
    """
    Sets up isolated workspaces to prevent overwhelm and conflicts.
    
    ED Features:
    - Pre-created directory structure (no decisions)
    - Isolated environments prevent conflicts
    - Clear organization reduces cognitive load
    """
    
    def __init__(self):
        super().__init__(
            hook_id="workspace_setup",
            description="Setup isolated workspace with pre-defined structure",
            ed_features={
                "reduces_decisions": True,
                "prevents_overwhelm": True,
                "creates_checkpoints": True
            }
        )
        self._created_directories: List[str] = []
    
    async def execute(self, context: HookContext) -> HookResult:
        """Setup workspace with automatic directory structure."""
        try:
            workspace_root = Path(context.workspace_path)
            
            # Create standard directory structure (no decisions needed)
            directories = self._get_standard_directories(context)
            
            created_dirs = []
            for dir_path in directories:
                full_path = workspace_root / dir_path
                if not full_path.exists():
                    full_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(str(full_path))
                    self._created_directories.append(str(full_path))
            
            # Create workspace metadata
            metadata_file = workspace_root / ".workspace_metadata.json"
            metadata = {
                "execution_id": context.execution_id,
                "template_id": context.template_id,
                "created_at": datetime.now().isoformat(),
                "directories": directories,
                "purpose": "Template execution workspace with ED support"
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            created_dirs.append(str(metadata_file))
            
            # Update context
            context.metadata["workspace_directories"] = directories
            context.metadata["workspace_metadata_file"] = str(metadata_file)
            
            return HookResult(
                success=True,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Created workspace with {len(directories)} directories",
                metadata={"created_directories": created_dirs},
                cognitive_load_impact="reduced"
            )
            
        except Exception as e:
            raise HookExecutionError(
                f"Workspace setup failed: {e}",
                self.hook_id,
                context,
                error_type="workspace_setup_error"
            )
    
    def get_dependencies(self) -> List[str]:
        """No dependencies for workspace setup."""
        return []
    
    def supports_rollback(self) -> bool:
        """Support rollback by removing created directories."""
        return True
    
    async def rollback(self, context: HookContext) -> HookResult:
        """Rollback by removing created directories."""
        try:
            removed_count = 0
            for dir_path in reversed(self._created_directories):
                try:
                    path = Path(dir_path)
                    if path.is_file():
                        path.unlink()
                        removed_count += 1
                    elif path.is_dir() and not any(path.iterdir()):
                        path.rmdir()
                        removed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove {dir_path}: {e}")
            
            return HookResult(
                success=True,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Cleaned up {removed_count} workspace items"
            )
            
        except Exception as e:
            return HookResult(
                success=False,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Rollback failed: {e}",
                error_type="rollback_error"
            )
    
    def estimate_cognitive_load(self, context: HookContext) -> str:
        """Low cognitive load - automated directory creation."""
        return "low"
    
    def create_recovery_checkpoint(self, context: HookContext) -> Dict[str, Any]:
        """Create checkpoint for recovery."""
        return {
            "created_directories": self._created_directories.copy(),
            "workspace_path": context.workspace_path
        }
    
    def _get_standard_directories(self, context: HookContext) -> List[str]:
        """Get standard directory structure for workspace."""
        return [
            "artifacts",           # Generated artifacts
            "checkpoints",         # ED checkpoints
            "context",            # Context and documentation
            "logs",               # Execution logs
            "temp",               # Temporary files
            "agents",             # Agent-specific workspaces
            f"agents/{context.execution_id}",  # Current execution
        ]


class AgentSpawningHook(ExecutiveDysfunctionHook):
    """
    Spawns specialist agents automatically based on task requirements.
    
    ED Features:
    - Automatic agent assignment (no decisions)
    - Isolated agent workspaces
    - Delegated pressure through specialization
    """
    
    def __init__(self):
        super().__init__(
            hook_id="agent_spawning",
            description="Spawn specialist agents for template phases",
            ed_features={
                "reduces_decisions": True,
                "delegates_pressure": True,
                "creates_checkpoints": True
            }
        )
        self._spawned_agents: List[Dict[str, Any]] = []
    
    async def execute(self, context: HookContext) -> HookResult:
        """Spawn agents based on template phase requirements."""
        try:
            # Analyze phase requirements for agent assignment
            phase_config = context.metadata.get("current_phase_config", {})
            required_agents = self._analyze_agent_requirements(phase_config, context)
            
            spawned_agent_info = []
            for agent_spec in required_agents:
                agent_info = await self._spawn_agent(agent_spec, context)
                spawned_agent_info.append(agent_info)
                self._spawned_agents.append(agent_info)
            
            # Update context with spawned agents
            for agent_info in spawned_agent_info:
                context.add_spawned_agent(
                    agent_info["agent_id"],
                    agent_info["agent_type"],
                    agent_info["workspace_path"]
                )
            
            return HookResult(
                success=True,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Spawned {len(spawned_agent_info)} specialist agents",
                spawned_agents=[a["agent_id"] for a in spawned_agent_info],
                metadata={"spawned_agent_details": spawned_agent_info},
                cognitive_load_impact="reduced"  # Pressure delegated to agents
            )
            
        except Exception as e:
            raise HookExecutionError(
                f"Agent spawning failed: {e}",
                self.hook_id,
                context,
                error_type="agent_spawning_error"
            )
    
    def get_dependencies(self) -> List[str]:
        """Depends on workspace setup."""
        return ["workspace_setup"]
    
    def supports_rollback(self) -> bool:
        """Support rollback by terminating spawned agents."""
        return True
    
    async def rollback(self, context: HookContext) -> HookResult:
        """Rollback by terminating spawned agents."""
        try:
            terminated_count = 0
            for agent_info in self._spawned_agents:
                success = await self._terminate_agent(agent_info["agent_id"])
                if success:
                    terminated_count += 1
            
            return HookResult(
                success=True,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Terminated {terminated_count} spawned agents"
            )
            
        except Exception as e:
            return HookResult(
                success=False,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Agent termination failed: {e}",
                error_type="rollback_error"
            )
    
    def estimate_cognitive_load(self, context: HookContext) -> str:
        """Reduces cognitive load by delegating work to specialists."""
        return "low"
    
    def create_recovery_checkpoint(self, context: HookContext) -> Dict[str, Any]:
        """Create checkpoint for recovery."""
        return {
            "spawned_agents": self._spawned_agents.copy(),
            "active_agents": list(context.active_agents)
        }
    
    def _analyze_agent_requirements(self, phase_config: Dict[str, Any], context: HookContext) -> List[Dict[str, Any]]:
        """Analyze what agents are needed for this phase."""
        requirements = []
        
        # Example agent assignment logic
        if phase_config.get("requires_research"):
            requirements.append({
                "agent_type": "research_specialist",
                "priority": "high",
                "resources": {"max_memory": "2GB", "max_cpu": "50%"}
            })
        
        if phase_config.get("requires_implementation"):
            requirements.append({
                "agent_type": "implementation_specialist", 
                "priority": "high",
                "resources": {"max_memory": "4GB", "max_cpu": "75%"}
            })
        
        if phase_config.get("requires_testing"):
            requirements.append({
                "agent_type": "testing_specialist",
                "priority": "medium",
                "resources": {"max_memory": "1GB", "max_cpu": "25%"}
            })
        
        return requirements
    
    async def _spawn_agent(self, agent_spec: Dict[str, Any], context: HookContext) -> Dict[str, Any]:
        """Spawn a single agent with given specification."""
        agent_id = f"{agent_spec['agent_type']}_{datetime.now().timestamp()}"
        
        # Create isolated workspace for agent
        agent_workspace = Path(context.workspace_path) / "agents" / agent_id
        agent_workspace.mkdir(parents=True, exist_ok=True)
        
        # Agent info (in real implementation, would spawn actual agent process)
        agent_info = {
            "agent_id": agent_id,
            "agent_type": agent_spec["agent_type"],
            "workspace_path": str(agent_workspace),
            "resources": agent_spec.get("resources", {}),
            "priority": agent_spec.get("priority", "medium"),
            "spawned_at": datetime.now().isoformat(),
            "status": "spawned"
        }
        
        # Create agent context file
        context_file = agent_workspace / "agent_context.json"
        with open(context_file, 'w') as f:
            json.dump({
                "execution_id": context.execution_id,
                "template_id": context.template_id,
                "agent_info": agent_info,
                "task_context": context.metadata
            }, f, indent=2)
        
        logger.info(f"Spawned agent: {agent_id} ({agent_spec['agent_type']})")
        
        return agent_info
    
    async def _terminate_agent(self, agent_id: str) -> bool:
        """Terminate spawned agent."""
        # In real implementation, would terminate actual agent process
        logger.info(f"Terminated agent: {agent_id}")
        return True


class CheckpointHook(ExecutiveDysfunctionHook):
    """
    Creates automatic checkpoints for executive dysfunction recovery.
    
    ED Features:
    - Automatic state preservation
    - Momentum preservation across interruptions
    - Recovery point creation
    """
    
    def __init__(self):
        super().__init__(
            hook_id="checkpoint_creation",
            description="Create execution checkpoints for ED recovery",
            ed_features={
                "preserves_momentum": True,
                "supports_interruption": True,
                "creates_checkpoints": True
            }
        )
    
    async def execute(self, context: HookContext) -> HookResult:
        """Create comprehensive checkpoint."""
        try:
            checkpoint_name = f"phase_{context.current_phase}_{datetime.now().timestamp()}"
            
            # Create comprehensive checkpoint data
            checkpoint_data = {
                "execution_context": {
                    "execution_id": context.execution_id,
                    "template_id": context.template_id,
                    "current_phase": context.current_phase,
                    "phase_index": context.phase_index,
                    "progress_percentage": context.get_progress_percentage()
                },
                "agent_state": {
                    "spawned_agents": context.spawned_agents.copy(),
                    "active_agents": list(context.active_agents),
                    "agent_workspaces": context.isolated_workspaces.copy()
                },
                "artifacts": context.artifacts.copy(),
                "metadata": context.metadata.copy(),
                "execution_history": context.execution_history.copy(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Save checkpoint to file
            checkpoint_file = Path(context.workspace_path) / "checkpoints" / f"{checkpoint_name}.json"
            checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            # Update context
            context.create_checkpoint(checkpoint_name)
            
            return HookResult(
                success=True,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Created checkpoint: {checkpoint_name}",
                checkpoint_created=checkpoint_name,
                recovery_data=checkpoint_data,
                cognitive_load_impact="reduced"
            )
            
        except Exception as e:
            raise HookExecutionError(
                f"Checkpoint creation failed: {e}",
                self.hook_id,
                context,
                error_type="checkpoint_error"
            )
    
    def get_dependencies(self) -> List[str]:
        """Depends on workspace setup."""
        return ["workspace_setup"]
    
    def supports_rollback(self) -> bool:
        """No rollback needed for checkpoints."""
        return False
    
    def estimate_cognitive_load(self, context: HookContext) -> str:
        """Very low - completely automated."""
        return "low"
    
    def create_recovery_checkpoint(self, context: HookContext) -> Dict[str, Any]:
        """Checkpoint hook creates its own recovery data."""
        return {
            "checkpoint_hook_executed": True,
            "execution_context": context.metadata.copy()
        }


class ValidationHook(Hook):
    """
    Validates template execution state and quality.
    
    Provides automated validation to reduce manual checking overhead.
    """
    
    def __init__(self):
        super().__init__(
            hook_id="execution_validation",
            description="Validate execution state and artifacts"
        )
    
    async def execute(self, context: HookContext) -> HookResult:
        """Validate current execution state."""
        try:
            validation_results = []
            
            # Validate workspace structure
            workspace_valid = self._validate_workspace(context)
            validation_results.append(("workspace", workspace_valid))
            
            # Validate artifacts
            artifacts_valid = self._validate_artifacts(context)
            validation_results.append(("artifacts", artifacts_valid))
            
            # Validate agent states
            agents_valid = self._validate_agents(context)
            validation_results.append(("agents", agents_valid))
            
            # Check if all validations passed
            all_valid = all(valid for _, valid in validation_results)
            failed_validations = [name for name, valid in validation_results if not valid]
            
            return HookResult(
                success=all_valid,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Validation {'passed' if all_valid else 'failed'}" + 
                       (f" - Failed: {failed_validations}" if failed_validations else ""),
                metadata={"validation_results": dict(validation_results)},
                cognitive_load_impact="reduced"
            )
            
        except Exception as e:
            raise HookExecutionError(
                f"Validation failed: {e}",
                self.hook_id,
                context,
                error_type="validation_error"
            )
    
    def get_dependencies(self) -> List[str]:
        """No dependencies - can validate at any point."""
        return []
    
    def supports_rollback(self) -> bool:
        """No rollback needed for validation."""
        return False
    
    def _validate_workspace(self, context: HookContext) -> bool:
        """Validate workspace structure."""
        workspace_path = Path(context.workspace_path)
        required_dirs = context.metadata.get("workspace_directories", [])
        
        for dir_name in required_dirs:
            dir_path = workspace_path / dir_name
            if not dir_path.exists():
                logger.warning(f"Missing workspace directory: {dir_name}")
                return False
        
        return True
    
    def _validate_artifacts(self, context: HookContext) -> bool:
        """Validate that expected artifacts exist."""
        for artifact in context.artifacts:
            if isinstance(artifact, dict) and "path" in artifact:
                artifact_path = Path(artifact["path"])
            else:
                artifact_path = Path(str(artifact))
            
            if not artifact_path.exists():
                logger.warning(f"Missing artifact: {artifact_path}")
                return False
        
        return True
    
    def _validate_agents(self, context: HookContext) -> bool:
        """Validate agent states."""
        for agent_id in context.active_agents:
            workspace_path = context.isolated_workspaces.get(agent_id)
            if not workspace_path or not Path(workspace_path).exists():
                logger.warning(f"Missing workspace for agent: {agent_id}")
                return False
        
        return True


class CommitHook(ExecutiveDysfunctionHook):
    """
    Automatically commits work to preserve progress.
    
    ED Features:
    - Automatic commit messages (no decision paralysis)
    - Regular commits preserve momentum
    - Clear commit structure
    """
    
    def __init__(self):
        super().__init__(
            hook_id="auto_commit",
            description="Automatically commit work progress",
            ed_features={
                "reduces_decisions": True,
                "preserves_momentum": True
            }
        )
    
    async def execute(self, context: HookContext) -> HookResult:
        """Create automatic commit with generated message."""
        try:
            # Generate commit message automatically
            commit_message = self._generate_commit_message(context)
            
            # Check if there are changes to commit
            has_changes = await self._has_git_changes(context.workspace_path)
            
            if not has_changes:
                return HookResult(
                    success=True,
                    hook_id=self.hook_id,
                    execution_time_ms=0.0,
                    message="No changes to commit",
                    cognitive_load_impact="neutral"
                )
            
            # Stage and commit changes
            success = await self._stage_and_commit(commit_message, context.workspace_path)
            
            if success:
                context.metadata["last_commit_message"] = commit_message
                context.metadata["last_commit_phase"] = context.current_phase
                
                return HookResult(
                    success=True,
                    hook_id=self.hook_id,
                    execution_time_ms=0.0,
                    message=f"Committed changes: {commit_message}",
                    metadata={"commit_message": commit_message},
                    cognitive_load_impact="reduced"
                )
            else:
                return HookResult(
                    success=False,
                    hook_id=self.hook_id,
                    execution_time_ms=0.0,
                    message="Failed to commit changes",
                    error_type="commit_failed"
                )
                
        except Exception as e:
            raise HookExecutionError(
                f"Commit failed: {e}",
                self.hook_id,
                context,
                error_type="git_commit_error"
            )
    
    def get_dependencies(self) -> List[str]:
        """Depends on git branch creation."""
        return ["git_branch_creation"]
    
    def supports_rollback(self) -> bool:
        """Could support rollback via git reset."""
        return True
    
    def estimate_cognitive_load(self, context: HookContext) -> str:
        """Low load - automated commit messages."""
        return "low"
    
    def create_recovery_checkpoint(self, context: HookContext) -> Dict[str, Any]:
        """Create recovery checkpoint."""
        return {
            "last_commit": context.metadata.get("last_commit_message"),
            "phase": context.current_phase
        }
    
    def _generate_commit_message(self, context: HookContext) -> str:
        """Generate automatic commit message."""
        template_name = context.template_id.replace("_", " ").title()
        phase = context.current_phase.replace("_", " ").title()
        
        # Generate descriptive but automatic message
        return f"feat({context.template_id}): {phase} phase progress\n\n" \
               f"Template: {template_name}\n" \
               f"Phase: {phase} ({context.phase_index + 1}/{context.total_phases})\n" \
               f"Execution ID: {context.execution_id}\n" \
               f"\nAutomatically generated commit - no manual decisions required."
    
    async def _has_git_changes(self, workspace_path: str) -> bool:
        """Check if there are uncommitted changes."""
        try:
            status_result = await asyncio.create_subprocess_exec(
                "git", "status", "--porcelain",
                cwd=workspace_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await status_result.communicate()
            return len(stdout.strip()) > 0
            
        except Exception:
            return False
    
    async def _stage_and_commit(self, commit_message: str, workspace_path: str) -> bool:
        """Stage all changes and commit."""
        try:
            # Stage all changes
            add_result = await asyncio.create_subprocess_exec(
                "git", "add", "-A",
                cwd=workspace_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await add_result.communicate()
            if add_result.returncode != 0:
                return False
            
            # Commit changes
            commit_result = await asyncio.create_subprocess_exec(
                "git", "commit", "-m", commit_message,
                cwd=workspace_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await commit_result.communicate()
            return commit_result.returncode == 0
            
        except Exception:
            return False


class NotificationHook(Hook):
    """
    Sends notifications about template execution progress.
    
    Provides progress updates to maintain awareness without overwhelming.
    """
    
    def __init__(self):
        super().__init__(
            hook_id="progress_notification",
            description="Send progress notifications"
        )
    
    async def execute(self, context: HookContext) -> HookResult:
        """Send progress notification."""
        try:
            # Prepare notification content
            progress_percentage = context.get_progress_percentage()
            execution_duration = context.get_execution_duration()
            
            notification_content = {
                "template": context.template_id,
                "phase": context.current_phase,
                "progress": f"{progress_percentage:.1f}%",
                "duration": f"{execution_duration:.1f}s" if execution_duration else "Unknown",
                "active_agents": len(context.active_agents),
                "artifacts_created": len(context.artifacts)
            }
            
            # In real implementation, would send via notification service
            logger.info(f"Progress notification: {notification_content}")
            
            return HookResult(
                success=True,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Sent progress notification: {progress_percentage:.1f}% complete",
                metadata=notification_content,
                cognitive_load_impact="neutral"
            )
            
        except Exception as e:
            # Non-critical failure - don't fail execution
            logger.warning(f"Notification failed: {e}")
            
            return HookResult(
                success=True,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Notification failed (non-critical): {e}",
                cognitive_load_impact="neutral"
            )
    
    def get_dependencies(self) -> List[str]:
        """No dependencies - can notify at any time."""
        return []
    
    def supports_rollback(self) -> bool:
        """No rollback needed for notifications."""
        return False


class DocumentAssociationHook(ExecutiveDysfunctionHook):
    """
    Automatically associates relevant documents with template execution.
    
    ED Features:
    - Automatic document discovery (no manual searching)
    - Context loading reduces setup overhead
    - Intelligent relevance ranking
    """
    
    def __init__(self):
        super().__init__(
            hook_id="document_association",
            description="Associate relevant documents with execution",
            ed_features={
                "reduces_decisions": True,
                "delegates_pressure": True
            }
        )
    
    async def execute(self, context: HookContext) -> HookResult:
        """Discover and associate relevant documents."""
        try:
            # Get explicit associations from template
            explicit_docs = context.metadata.get("associated_documents", [])
            
            # Discover implicit associations
            implicit_docs = await self._discover_relevant_documents(context)
            
            # Combine and rank documents
            all_docs = explicit_docs + implicit_docs
            ranked_docs = self._rank_documents_by_relevance(all_docs, context)
            
            # Load document content for context
            loaded_docs = await self._load_document_content(ranked_docs[:10])  # Top 10
            
            # Update context
            context.associated_documents.extend([doc["path"] for doc in loaded_docs])
            context.metadata["loaded_documents"] = loaded_docs
            context.metadata["document_count"] = len(loaded_docs)
            
            return HookResult(
                success=True,
                hook_id=self.hook_id,
                execution_time_ms=0.0,
                message=f"Associated {len(loaded_docs)} relevant documents",
                metadata={"associated_documents": loaded_docs},
                cognitive_load_impact="reduced"
            )
            
        except Exception as e:
            raise HookExecutionError(
                f"Document association failed: {e}",
                self.hook_id,
                context,
                error_type="document_association_error"
            )
    
    def get_dependencies(self) -> List[str]:
        """No dependencies - can run early."""
        return []
    
    def supports_rollback(self) -> bool:
        """No rollback needed for document association."""
        return False
    
    def estimate_cognitive_load(self, context: HookContext) -> str:
        """Reduces cognitive load by providing relevant context."""
        return "low"
    
    def create_recovery_checkpoint(self, context: HookContext) -> Dict[str, Any]:
        """Create recovery checkpoint."""
        return {
            "associated_documents": context.associated_documents.copy(),
            "loaded_document_count": len(context.metadata.get("loaded_documents", []))
        }
    
    async def _discover_relevant_documents(self, context: HookContext) -> List[str]:
        """Discover documents relevant to template execution."""
        relevant_docs = []
        
        # Search for documentation files
        doc_patterns = ["*.md", "*.txt", "README*", "CHANGELOG*"]
        for pattern in doc_patterns:
            # In real implementation, would use file system search
            pass
        
        # Search for configuration files
        config_patterns = ["*.json", "*.yaml", "*.toml", "*.ini"]
        for pattern in config_patterns:
            # In real implementation, would search with pattern
            pass
        
        # Search for related code files based on template
        if "implementation" in context.template_id:
            relevant_docs.extend([
                "docs/architecture/*.md",
                "docs/api/*.md",
                "examples/*.py"
            ])
        
        return relevant_docs
    
    def _rank_documents_by_relevance(self, documents: List[str], context: HookContext) -> List[Dict[str, Any]]:
        """Rank documents by relevance to current execution."""
        ranked_docs = []
        
        for doc_path in documents:
            relevance_score = self._calculate_relevance_score(doc_path, context)
            ranked_docs.append({
                "path": doc_path,
                "relevance_score": relevance_score
            })
        
        # Sort by relevance (highest first)
        ranked_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return ranked_docs
    
    def _calculate_relevance_score(self, doc_path: str, context: HookContext) -> float:
        """Calculate relevance score for a document."""
        score = 0.0
        
        # Boost score based on file type
        if doc_path.endswith(".md"):
            score += 0.3
        elif doc_path.endswith((".json", ".yaml")):
            score += 0.2
        
        # Boost score based on path keywords
        path_lower = doc_path.lower()
        template_keywords = context.template_id.lower().split("_")
        
        for keyword in template_keywords:
            if keyword in path_lower:
                score += 0.4
        
        # Boost score for common important files
        if any(name in path_lower for name in ["readme", "architecture", "api", "guide"]):
            score += 0.3
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _load_document_content(self, ranked_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Load content for top-ranked documents."""
        loaded_docs = []
        
        for doc_info in ranked_docs:
            try:
                doc_path = Path(doc_info["path"])
                if doc_path.exists() and doc_path.is_file():
                    # Read file content
                    with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    loaded_docs.append({
                        "path": str(doc_path),
                        "relevance_score": doc_info["relevance_score"],
                        "content": content[:5000],  # Limit content size
                        "size": len(content),
                        "loaded_at": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to load document {doc_info['path']}: {e}")
        
        return loaded_docs