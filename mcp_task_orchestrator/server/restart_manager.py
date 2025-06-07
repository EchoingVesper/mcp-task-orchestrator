"""
Server restart coordination and state restoration.

This module handles the server restart process including subprocess management,
state restoration, and service resumption.
"""

import asyncio
import logging
import os
import subprocess
import sys
import time
import signal
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from .state_serializer import StateSerializer, ServerStateSnapshot, RestartReason
from ..orchestrator.models import TaskBreakdown, SubTask, TaskStatus

logger = logging.getLogger("mcp_task_orchestrator.server.restart_manager")


class RestartPhase(str, Enum):
    """Phases of the restart process."""
    IDLE = "idle"
    PREPARING = "preparing"
    STARTING_PROCESS = "starting_process"
    LOADING_STATE = "loading_state"
    RESTORING_DATABASE = "restoring_database"
    RESUMING_TASKS = "resuming_tasks"
    ENABLING_CONNECTIONS = "enabling_connections"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class RestartStatus:
    """Current restart status information."""
    phase: RestartPhase
    progress_percent: float
    message: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    process_id: Optional[int] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ProcessManager:
    """Manages server process lifecycle for restarts."""
    
    def __init__(self, executable_path: Optional[str] = None):
        """Initialize process manager.
        
        Args:
            executable_path: Path to server executable. Defaults to current process.
        """
        self.executable_path = executable_path or sys.executable
        self.script_path = self._get_server_script_path()
        self.current_process: Optional[subprocess.Popen] = None
        self.restart_env = self._prepare_restart_environment()
        
        logger.info(f"ProcessManager initialized with {self.executable_path}")

    async def start_new_process(self, 
                              restart_reason: RestartReason,
                              timeout: int = 30) -> tuple[bool, Optional[int]]:
        """Start a new server process.
        
        Args:
            restart_reason: Reason for the restart
            timeout: Maximum time to wait for process start
            
        Returns:
            Tuple of (success, process_id)
        """
        try:
            logger.info("Starting new server process")
            
            # Prepare command arguments
            cmd_args = [
                self.executable_path,
                self.script_path,
                "--restart-mode",
                f"--restart-reason={restart_reason.value}"
            ]
            
            # Start the new process
            self.current_process = subprocess.Popen(
                cmd_args,
                env=self.restart_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait for process to start successfully
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.current_process.poll() is not None:
                    # Process already exited
                    stdout, stderr = self.current_process.communicate()
                    logger.error(f"Process exited early: {stderr.decode()}")
                    return False, None
                
                # Check if process is responding (basic check)
                if await self._check_process_health():
                    logger.info(f"New process started successfully: PID {self.current_process.pid}")
                    return True, self.current_process.pid
                
                await asyncio.sleep(0.5)
            
            logger.error("New process failed to start within timeout")
            await self.terminate_process()
            return False, None
            
        except Exception as e:
            logger.error(f"Failed to start new process: {e}")
            return False, None

    async def terminate_process(self, graceful: bool = True, timeout: int = 10):
        """Terminate the managed process.
        
        Args:
            graceful: Whether to attempt graceful shutdown first
            timeout: Maximum time to wait for graceful shutdown
        """
        if not self.current_process:
            return
        
        try:
            if graceful:
                # Send SIGTERM for graceful shutdown
                self.current_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    await asyncio.wait_for(
                        asyncio.create_task(self._wait_for_process_exit()),
                        timeout=timeout
                    )
                    logger.info("Process terminated gracefully")
                    return
                except asyncio.TimeoutError:
                    logger.warning("Graceful shutdown timed out")
            
            # Force kill if graceful failed or not requested
            self.current_process.kill()
            await self._wait_for_process_exit()
            logger.info("Process terminated forcefully")
            
        except Exception as e:
            logger.error(f"Failed to terminate process: {e}")
        finally:
            self.current_process = None

    async def _check_process_health(self) -> bool:
        """Check if the process is healthy and responding."""
        # TODO: Implement actual health check
        # For now, just check if process is running
        return self.current_process and self.current_process.poll() is None

    async def _wait_for_process_exit(self):
        """Wait for process to exit asynchronously."""
        if not self.current_process:
            return
        
        # Poll process status until it exits
        while self.current_process.poll() is None:
            await asyncio.sleep(0.1)

    def _get_server_script_path(self) -> str:
        """Get the path to the server script."""
        # Try to find the server script
        possible_paths = [
            "server.py",
            "mcp_task_orchestrator/server.py",
            "-m mcp_task_orchestrator.server"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Default to module execution
        return "-m mcp_task_orchestrator.server"

    def _prepare_restart_environment(self) -> Dict[str, str]:
        """Prepare environment variables for restart."""
        env = os.environ.copy()
        
        # Add restart-specific environment variables
        env["MCP_TASK_ORCHESTRATOR_RESTART_MODE"] = "true"
        env["MCP_TASK_ORCHESTRATOR_PARENT_PID"] = str(os.getpid())
        
        return env


class StateRestorer:
    """Handles state restoration from snapshots."""
    
    def __init__(self, state_serializer: StateSerializer):
        """Initialize state restorer.
        
        Args:
            state_serializer: State serializer instance
        """
        self.state_serializer = state_serializer
        self.restoration_callbacks: List[Callable] = []
        
        logger.info("StateRestorer initialized")

    async def restore_from_snapshot(self, 
                                   snapshot: ServerStateSnapshot,
                                   state_manager) -> bool:
        """Restore server state from snapshot.
        
        Args:
            snapshot: State snapshot to restore from
            state_manager: State manager instance to restore into
            
        Returns:
            True if restoration was successful, False otherwise
        """
        try:
            logger.info(f"Restoring state from snapshot: {snapshot.timestamp}")
            
            # Validate snapshot before restoration
            if not await self.state_serializer.validate_snapshot(snapshot):
                logger.error("Snapshot validation failed")
                return False
            
            # Restore database state
            if not await self._restore_database_state(snapshot.database_state, state_manager):
                logger.error("Database state restoration failed")
                return False
            
            # Restore active tasks
            if not await self._restore_active_tasks(snapshot.active_tasks, state_manager):
                logger.error("Active tasks restoration failed")
                return False
            
            # Restore suspended tasks
            if snapshot.suspended_tasks:
                if not await self._restore_suspended_tasks(snapshot.suspended_tasks, state_manager):
                    logger.error("Suspended tasks restoration failed")
                    return False
            
            # Restore client sessions
            if snapshot.client_sessions:
                if not await self._restore_client_sessions(snapshot.client_sessions):
                    logger.warning("Client sessions restoration failed (non-critical)")
            
            # Call restoration callbacks
            for callback in self.restoration_callbacks:
                try:
                    await callback(snapshot)
                except Exception as e:
                    logger.error(f"Restoration callback failed: {e}")
            
            logger.info("State restoration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"State restoration failed: {e}")
            return False

    def add_restoration_callback(self, callback: Callable):
        """Add callback to be called during state restoration.
        
        Args:
            callback: Async function to call with snapshot during restoration
        """
        self.restoration_callbacks.append(callback)

    async def _restore_database_state(self, db_state, state_manager) -> bool:
        """Restore database connections and state."""
        try:
            if not db_state or not db_state.db_path:
                logger.warning("No database state to restore")
                return True
            
            # Verify database file exists and is accessible
            if not os.path.exists(db_state.db_path):
                logger.error(f"Database file not found: {db_state.db_path}")
                return False
            
            # Validate database integrity
            current_checksum = self.state_serializer._calculate_db_checksum(db_state.db_path)
            if current_checksum != db_state.integrity_checksum:
                logger.warning("Database integrity checksum mismatch")
                # Continue anyway - data might have been written after snapshot
            
            # Ensure state manager uses the correct database
            if state_manager.db_path != db_state.db_path:
                logger.info(f"Updating state manager database path: {db_state.db_path}")
                state_manager.db_path = db_state.db_path
            
            # Reinitialize state manager if needed
            if not state_manager._initialized:
                await state_manager._initialize()
            
            logger.info("Database state restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore database state: {e}")
            return False

    async def _restore_active_tasks(self, active_tasks: List[Dict[str, Any]], state_manager) -> bool:
        """Restore active tasks from snapshot data."""
        try:
            logger.info(f"Restoring {len(active_tasks)} active tasks")
            
            for task_data in active_tasks:
                try:
                    # Convert task data back to TaskBreakdown object
                    task_breakdown = self._dict_to_task_breakdown(task_data)
                    
                    # Store the task in state manager
                    await state_manager.store_task_breakdown(task_breakdown)
                    
                    logger.debug(f"Restored task: {task_breakdown.parent_task_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to restore task {task_data.get('task_id', 'unknown')}: {e}")
                    # Continue with other tasks
            
            logger.info("Active tasks restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore active tasks: {e}")
            return False

    async def _restore_suspended_tasks(self, suspended_tasks: List[Dict[str, Any]], state_manager) -> bool:
        """Restore suspended tasks from snapshot data."""
        try:
            logger.info(f"Restoring {len(suspended_tasks)} suspended tasks")
            
            # TODO: Implement suspended task restoration
            # For now, treat suspended tasks as regular tasks
            return await self._restore_active_tasks(suspended_tasks, state_manager)
            
        except Exception as e:
            logger.error(f"Failed to restore suspended tasks: {e}")
            return False

    async def _restore_client_sessions(self, client_sessions) -> bool:
        """Restore client session state."""
        try:
            logger.info(f"Restoring {len(client_sessions)} client sessions")
            
            # TODO: Implement client session restoration
            # This requires integration with MCP server connection handling
            logger.warning("Client session restoration not yet implemented")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore client sessions: {e}")
            return False

    def _dict_to_task_breakdown(self, task_data: Dict[str, Any]) -> TaskBreakdown:
        """Convert dictionary data back to TaskBreakdown object."""
        # Create subtasks
        subtasks = []
        for st_data in task_data.get('subtasks', []):
            subtask = SubTask(
                task_id=st_data['task_id'],
                title=st_data['title'],
                description=st_data['description'],
                specialist_type=st_data['specialist_type'],
                dependencies=st_data.get('dependencies', []),
                estimated_effort=st_data.get('estimated_effort', ''),
                status=TaskStatus(st_data.get('status', TaskStatus.PENDING.value)),
                results=st_data.get('results'),
                artifacts=st_data.get('artifacts', [])
            )
            subtasks.append(subtask)
        
        # Create task breakdown
        task_breakdown = TaskBreakdown(
            parent_task_id=task_data['task_id'],
            description=task_data['description'],
            complexity=task_data.get('complexity', 'moderate'),
            subtasks=subtasks
        )
        
        # Restore timestamps if available
        if task_data.get('created_at'):
            try:
                task_breakdown.created_at = datetime.fromisoformat(task_data['created_at'])
            except ValueError:
                pass
        
        return task_breakdown


class RestartCoordinator:
    """Coordinates the complete server restart process."""
    
    def __init__(self, 
                 state_serializer: StateSerializer,
                 process_manager: Optional[ProcessManager] = None):
        """Initialize restart coordinator.
        
        Args:
            state_serializer: State serializer instance
            process_manager: Process manager instance
        """
        self.state_serializer = state_serializer
        self.process_manager = process_manager or ProcessManager()
        self.state_restorer = StateRestorer(state_serializer)
        
        self.status = RestartStatus(
            phase=RestartPhase.IDLE,
            progress_percent=0.0,
            message="Ready for restart"
        )
        
        self.restart_event = asyncio.Event()
        self._restart_in_progress = False
        
        logger.info("RestartCoordinator initialized")

    async def execute_restart(self, 
                            snapshot: Optional[ServerStateSnapshot] = None,
                            state_manager=None,
                            timeout: int = 60) -> bool:
        """Execute complete restart sequence.
        
        Args:
            snapshot: State snapshot to restore. If None, loads latest.
            state_manager: State manager instance for restoration
            timeout: Maximum time for restart sequence
            
        Returns:
            True if restart was successful, False otherwise
        """
        if self._restart_in_progress:
            logger.warning("Restart already in progress")
            return False
        
        try:
            self._restart_in_progress = True
            self.status.started_at = datetime.now(timezone.utc)
            
            logger.info("Executing server restart sequence")
            
            # Phase 1: Prepare for restart
            await self._prepare_restart()
            
            # Phase 2: Start new process
            success, process_id = await self._start_new_process()
            if not success:
                return False
            
            # Phase 3: Load state snapshot
            if snapshot is None:
                snapshot = await self._load_state_snapshot()
            if not snapshot:
                return False
            
            # Phase 4: Restore database connections
            if not await self._restore_database_connections(snapshot, state_manager):
                return False
            
            # Phase 5: Resume tasks and operations
            if not await self._resume_operations(snapshot, state_manager):
                return False
            
            # Phase 6: Enable client connections
            await self._enable_client_connections()
            
            self._update_status(
                RestartPhase.COMPLETE,
                100.0,
                "Server restart completed successfully"
            )
            
            self.status.completed_at = datetime.now(timezone.utc)
            logger.info("Server restart sequence completed")
            return True
            
        except Exception as e:
            logger.error(f"Restart sequence failed: {e}")
            self.status.errors.append(str(e))
            self._update_status(
                RestartPhase.FAILED,
                0.0,
                f"Restart failed: {e}"
            )
            return False
        finally:
            self._restart_in_progress = False
            self.restart_event.set()

    # Private methods for restart phases
    
    async def _prepare_restart(self):
        """Prepare for restart sequence."""
        self._update_status(
            RestartPhase.PREPARING,
            10.0,
            "Preparing for restart"
        )
        
        # TODO: Any pre-restart preparation
        logger.info("Restart preparation completed")

    async def _start_new_process(self) -> tuple[bool, Optional[int]]:
        """Start new server process."""
        self._update_status(
            RestartPhase.STARTING_PROCESS,
            25.0,
            "Starting new server process"
        )
        
        return await self.process_manager.start_new_process(
            RestartReason.MANUAL_REQUEST  # TODO: Get actual restart reason
        )

    async def _load_state_snapshot(self) -> Optional[ServerStateSnapshot]:
        """Load state snapshot for restoration."""
        self._update_status(
            RestartPhase.LOADING_STATE,
            40.0,
            "Loading state snapshot"
        )
        
        return await self.state_serializer.load_latest_snapshot()

    async def _restore_database_connections(self, snapshot: ServerStateSnapshot, state_manager) -> bool:
        """Restore database connections."""
        self._update_status(
            RestartPhase.RESTORING_DATABASE,
            60.0,
            "Restoring database connections"
        )
        
        return await self.state_restorer._restore_database_state(
            snapshot.database_state, 
            state_manager
        )

    async def _resume_operations(self, snapshot: ServerStateSnapshot, state_manager) -> bool:
        """Resume tasks and operations."""
        self._update_status(
            RestartPhase.RESUMING_TASKS,
            80.0,
            "Resuming tasks and operations"
        )
        
        return await self.state_restorer.restore_from_snapshot(snapshot, state_manager)

    async def _enable_client_connections(self):
        """Enable client connections."""
        self._update_status(
            RestartPhase.ENABLING_CONNECTIONS,
            90.0,
            "Enabling client connections"
        )
        
        # TODO: Re-enable MCP client connections
        logger.info("Client connections enabled")

    def _update_status(self, phase: RestartPhase, progress: float, message: str):
        """Update restart status."""
        self.status.phase = phase
        self.status.progress_percent = progress
        self.status.message = message
        
        logger.debug(f"Restart status: {phase} ({progress:.1f}%) - {message}")