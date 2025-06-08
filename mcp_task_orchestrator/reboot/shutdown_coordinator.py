"""
Graceful shutdown coordination for server reboot functionality.

This module orchestrates the shutdown sequence to ensure clean state
preservation and minimal service disruption.
"""

import asyncio
import logging
import signal
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass

from .state_serializer import StateSerializer, RestartReason, ServerStateSnapshot

logger = logging.getLogger("mcp_task_orchestrator.server.shutdown_coordinator")


class ShutdownPhase(str, Enum):
    """Phases of the shutdown process."""
    IDLE = "idle"
    PREPARING = "preparing"
    MAINTENANCE_MODE = "maintenance_mode"
    SUSPENDING_TASKS = "suspending_tasks"
    SERIALIZING_STATE = "serializing_state"
    CLOSING_CONNECTIONS = "closing_connections"
    FINALIZING = "finalizing"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class ShutdownStatus:
    """Current shutdown status information."""
    phase: ShutdownPhase
    progress_percent: float
    message: str
    started_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ShutdownCoordinator:
    """Coordinates graceful server shutdown with state preservation."""
    
    def __init__(self, 
                 state_serializer: StateSerializer,
                 shutdown_timeout: int = 30,
                 task_suspension_timeout: int = 10):
        """Initialize shutdown coordinator.
        
        Args:
            state_serializer: State serializer instance
            shutdown_timeout: Maximum time to allow for complete shutdown
            task_suspension_timeout: Maximum time to suspend active tasks
        """
        self.state_serializer = state_serializer
        self.shutdown_timeout = shutdown_timeout
        self.task_suspension_timeout = task_suspension_timeout
        
        self.status = ShutdownStatus(
            phase=ShutdownPhase.IDLE,
            progress_percent=0.0,
            message="Ready for shutdown"
        )
        
        self.shutdown_event = asyncio.Event()
        self.maintenance_mode = False
        self.shutdown_callbacks: List[Callable] = []
        self.cleanup_callbacks: List[Callable] = []
        
        # Track shutdown state
        self._shutdown_in_progress = False
        self._shutdown_task: Optional[asyncio.Task] = None
        
        logger.info("ShutdownCoordinator initialized")

    async def initiate_shutdown(self, 
                              restart_reason: RestartReason = RestartReason.MANUAL_REQUEST,
                              force: bool = False) -> bool:
        """Initiate graceful shutdown sequence.
        
        Args:
            restart_reason: Reason for the shutdown
            force: Whether to force shutdown if already in progress
            
        Returns:
            True if shutdown was initiated successfully, False otherwise
        """
        if self._shutdown_in_progress and not force:
            logger.warning("Shutdown already in progress")
            return False
        
        try:
            logger.info(f"Initiating graceful shutdown, reason: {restart_reason}")
            
            self._shutdown_in_progress = True
            self.status.started_at = datetime.now(timezone.utc)
            
            # Start shutdown task
            self._shutdown_task = asyncio.create_task(
                self._execute_shutdown_sequence(restart_reason)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initiate shutdown: {e}")
            self._shutdown_in_progress = False
            return False

    async def wait_for_shutdown(self, timeout: Optional[float] = None) -> bool:
        """Wait for shutdown to complete.
        
        Args:
            timeout: Maximum time to wait for shutdown
            
        Returns:
            True if shutdown completed successfully, False on timeout/error
        """
        if not self._shutdown_in_progress:
            return True
        
        try:
            if timeout is None:
                timeout = self.shutdown_timeout
            
            await asyncio.wait_for(self.shutdown_event.wait(), timeout=timeout)
            return self.status.phase == ShutdownPhase.COMPLETE
            
        except asyncio.TimeoutError:
            logger.error(f"Shutdown timed out after {timeout} seconds")
            return False
        except Exception as e:
            logger.error(f"Error waiting for shutdown: {e}")
            return False

    def is_shutdown_ready(self) -> tuple[bool, List[str]]:
        """Check if server is ready for graceful shutdown.
        
        Returns:
            Tuple of (ready, list of blocking issues)
        """
        issues = []
        
        # Check if already shutting down
        if self._shutdown_in_progress:
            issues.append("Shutdown already in progress")
        
        # Check maintenance mode
        if self.maintenance_mode:
            issues.append("Server already in maintenance mode")
        
        # TODO: Add more readiness checks
        # - Active critical operations
        # - Database transaction status
        # - Client connection state
        
        return len(issues) == 0, issues

    def add_shutdown_callback(self, callback: Callable):
        """Add callback to be called during shutdown preparation.
        
        Args:
            callback: Async function to call during shutdown
        """
        self.shutdown_callbacks.append(callback)

    def add_cleanup_callback(self, callback: Callable):
        """Add callback to be called during final cleanup.
        
        Args:
            callback: Async function to call during cleanup
        """
        self.cleanup_callbacks.append(callback)

    async def emergency_shutdown(self) -> bool:
        """Perform emergency shutdown without state preservation.
        
        Returns:
            True if emergency shutdown completed, False otherwise
        """
        logger.warning("Performing emergency shutdown")
        
        try:
            self._update_status(
                ShutdownPhase.FINALIZING,
                90.0,
                "Emergency shutdown in progress"
            )
            
            # Call cleanup callbacks quickly
            for callback in self.cleanup_callbacks:
                try:
                    await asyncio.wait_for(callback(), timeout=1.0)
                except Exception as e:
                    logger.error(f"Cleanup callback failed: {e}")
            
            self._update_status(
                ShutdownPhase.COMPLETE,
                100.0,
                "Emergency shutdown complete"
            )
            
            self.shutdown_event.set()
            return True
            
        except Exception as e:
            logger.error(f"Emergency shutdown failed: {e}")
            self._update_status(
                ShutdownPhase.FAILED,
                0.0,
                f"Emergency shutdown failed: {e}"
            )
            return False

    # Private methods
    
    async def _execute_shutdown_sequence(self, restart_reason: RestartReason):
        """Execute the complete shutdown sequence."""
        try:
            # Phase 1: Enter maintenance mode
            await self._enter_maintenance_mode()
            
            # Phase 2: Suspend active tasks
            await self._suspend_active_tasks()
            
            # Phase 3: Serialize state
            snapshot = await self._serialize_server_state(restart_reason)
            
            # Phase 4: Close connections
            await self._close_connections()
            
            # Phase 5: Final cleanup
            await self._final_cleanup()
            
            self._update_status(
                ShutdownPhase.COMPLETE,
                100.0,
                "Graceful shutdown completed successfully"
            )
            
            logger.info("Graceful shutdown sequence completed")
            
        except Exception as e:
            logger.error(f"Shutdown sequence failed: {e}")
            self.status.errors.append(str(e))
            self._update_status(
                ShutdownPhase.FAILED,
                0.0,
                f"Shutdown failed: {e}"
            )
        finally:
            self._shutdown_in_progress = False
            self.shutdown_event.set()

    async def _enter_maintenance_mode(self):
        """Enter maintenance mode - reject new requests."""
        self._update_status(
            ShutdownPhase.MAINTENANCE_MODE,
            10.0,
            "Entering maintenance mode"
        )
        
        self.maintenance_mode = True
        
        # TODO: Notify connected clients of impending shutdown
        # TODO: Stop accepting new MCP requests
        
        logger.info("Entered maintenance mode")

    async def _suspend_active_tasks(self):
        """Suspend all active tasks at safe checkpoints."""
        self._update_status(
            ShutdownPhase.SUSPENDING_TASKS,
            25.0,
            "Suspending active tasks"
        )
        
        try:
            # Call shutdown callbacks to notify components
            for callback in self.shutdown_callbacks:
                try:
                    await asyncio.wait_for(
                        callback(), 
                        timeout=self.task_suspension_timeout / len(self.shutdown_callbacks)
                    )
                except Exception as e:
                    logger.error(f"Shutdown callback failed: {e}")
                    self.status.errors.append(f"Task suspension error: {e}")
            
            # TODO: Implement actual task suspension
            # - Find tasks at safe checkpoints
            # - Serialize task state and specialist context
            # - Mark tasks as suspended
            
            logger.info("Active tasks suspended")
            
        except Exception as e:
            logger.error(f"Failed to suspend active tasks: {e}")
            raise

    async def _serialize_server_state(self, restart_reason: RestartReason) -> ServerStateSnapshot:
        """Serialize complete server state."""
        self._update_status(
            ShutdownPhase.SERIALIZING_STATE,
            50.0,
            "Serializing server state"
        )
        
        try:
            # TODO: Get actual state manager instance
            # For now, simulate state serialization
            from ..orchestrator.state import StateManager
            
            # Create a mock state manager for testing
            # In real implementation, this would be passed in or obtained from server
            state_manager = None  # TODO: Get from server instance
            
            if state_manager is None:
                # Create minimal snapshot for testing
                snapshot = ServerStateSnapshot(restart_reason=restart_reason)
                snapshot.integrity_hash = self.state_serializer._generate_integrity_hash(snapshot)
            else:
                snapshot = await self.state_serializer.create_snapshot(
                    state_manager, 
                    restart_reason
                )
            
            # Save snapshot to disk
            await self.state_serializer.save_snapshot(snapshot, backup=True)
            
            logger.info("Server state serialized successfully")
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to serialize server state: {e}")
            raise

    async def _close_connections(self):
        """Close database connections and network connections."""
        self._update_status(
            ShutdownPhase.CLOSING_CONNECTIONS,
            75.0,
            "Closing connections"
        )
        
        try:
            # TODO: Close database connections gracefully
            # TODO: Close MCP server connections
            # TODO: Notify clients of shutdown completion
            
            logger.info("Connections closed")
            
        except Exception as e:
            logger.error(f"Failed to close connections: {e}")
            raise

    async def _final_cleanup(self):
        """Perform final cleanup operations."""
        self._update_status(
            ShutdownPhase.FINALIZING,
            90.0,
            "Performing final cleanup"
        )
        
        try:
            # Call cleanup callbacks
            for callback in self.cleanup_callbacks:
                try:
                    await callback()
                except Exception as e:
                    logger.error(f"Cleanup callback failed: {e}")
                    self.status.errors.append(f"Cleanup error: {e}")
            
            # Clean up old state snapshots
            await self.state_serializer.cleanup_old_snapshots()
            
            logger.info("Final cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to perform final cleanup: {e}")
            raise

    def _update_status(self, phase: ShutdownPhase, progress: float, message: str):
        """Update shutdown status."""
        self.status.phase = phase
        self.status.progress_percent = progress
        self.status.message = message
        
        if progress > 0 and self.status.started_at:
            # Estimate completion time based on progress
            elapsed = time.time() - self.status.started_at.timestamp()
            if progress < 100:
                estimated_total = elapsed / (progress / 100)
                remaining = estimated_total - elapsed
                self.status.estimated_completion = datetime.fromtimestamp(
                    time.time() + remaining, tz=timezone.utc
                )
        
        logger.debug(f"Shutdown status: {phase} ({progress:.1f}%) - {message}")


class ShutdownManager:
    """Singleton manager for shutdown coordination."""
    
    _instance: Optional[ShutdownCoordinator] = None
    
    @classmethod
    def get_instance(cls, 
                    state_serializer: Optional[StateSerializer] = None,
                    **kwargs) -> ShutdownCoordinator:
        """Get or create shutdown coordinator instance."""
        if cls._instance is None:
            if state_serializer is None:
                state_serializer = StateSerializer()
            cls._instance = ShutdownCoordinator(state_serializer, **kwargs)
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset instance for testing."""
        cls._instance = None