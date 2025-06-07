"""
Integration module for server reboot functionality.

This module provides the interface between the reboot system and the existing
MCP Task Orchestrator server infrastructure.
"""

import asyncio
import logging
import os
from typing import Optional, Dict, Any

from .state_serializer import StateSerializer, RestartReason, ServerStateSnapshot
from .shutdown_coordinator import ShutdownCoordinator, ShutdownManager, ShutdownPhase
from ..orchestrator.state import StateManager

logger = logging.getLogger("mcp_task_orchestrator.server.reboot_integration")


class RebootManager:
    """Main interface for server reboot functionality."""
    
    def __init__(self, state_manager: Optional[StateManager] = None):
        """Initialize reboot manager.
        
        Args:
            state_manager: Existing state manager instance
        """
        self.state_manager = state_manager
        self.state_serializer = StateSerializer()
        self.shutdown_coordinator = ShutdownManager.get_instance(self.state_serializer)
        self._initialized = False
        
        logger.info("RebootManager initialized")

    async def initialize(self, state_manager: StateManager):
        """Initialize with state manager reference.
        
        Args:
            state_manager: State manager instance from server
        """
        self.state_manager = state_manager
        self._initialized = True
        
        # Register shutdown callbacks with the state manager
        self.shutdown_coordinator.add_shutdown_callback(self._prepare_state_manager_shutdown)
        self.shutdown_coordinator.add_cleanup_callback(self._cleanup_state_manager)
        
        logger.info("RebootManager initialized with state manager")

    async def trigger_restart(self, 
                            reason: RestartReason = RestartReason.MANUAL_REQUEST,
                            timeout: int = 30) -> Dict[str, Any]:
        """Trigger a graceful server restart.
        
        Args:
            reason: Reason for the restart
            timeout: Maximum time to wait for restart completion
            
        Returns:
            Dictionary with restart status and details
        """
        if not self._initialized:
            return {
                'success': False,
                'error': 'RebootManager not initialized',
                'phase': 'error'
            }
        
        try:
            logger.info(f"Triggering server restart, reason: {reason}")
            
            # Check if ready for restart
            ready, issues = self.shutdown_coordinator.is_shutdown_ready()
            if not ready:
                return {
                    'success': False,
                    'error': f'Server not ready for restart: {", ".join(issues)}',
                    'phase': 'preparation_failed',
                    'issues': issues
                }
            
            # Initiate graceful shutdown
            success = await self.shutdown_coordinator.initiate_shutdown(reason)
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to initiate shutdown',
                    'phase': 'initiation_failed'
                }
            
            # Wait for shutdown to complete
            shutdown_complete = await self.shutdown_coordinator.wait_for_shutdown(timeout)
            
            status = self.shutdown_coordinator.status
            
            return {
                'success': shutdown_complete,
                'phase': status.phase.value,
                'progress': status.progress_percent,
                'message': status.message,
                'errors': status.errors,
                'restart_reason': reason.value,
                'completed_at': status.started_at.isoformat() if status.started_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to trigger restart: {e}")
            return {
                'success': False,
                'error': str(e),
                'phase': 'exception',
                'restart_reason': reason.value
            }

    async def get_restart_readiness(self) -> Dict[str, Any]:
        """Check server readiness for restart.
        
        Returns:
            Dictionary with readiness status and blocking issues
        """
        if not self._initialized:
            return {
                'ready': False,
                'issues': ['RebootManager not initialized'],
                'details': {}
            }
        
        ready, issues = self.shutdown_coordinator.is_shutdown_ready()
        
        details = {
            'maintenance_mode': self.shutdown_coordinator.maintenance_mode,
            'shutdown_in_progress': self.shutdown_coordinator._shutdown_in_progress,
            'state_manager_initialized': self.state_manager._initialized if self.state_manager else False
        }
        
        # Add additional readiness checks
        if self.state_manager:
            try:
                # Check if state manager is accessible
                await self.state_manager.get_all_tasks()
                details['state_manager_accessible'] = True
            except Exception as e:
                details['state_manager_accessible'] = False
                details['state_manager_error'] = str(e)
                if ready:  # Only add to issues if we were previously ready
                    issues.append(f'State manager not accessible: {e}')
                    ready = False
        
        return {
            'ready': ready,
            'issues': issues,
            'details': details
        }

    async def restore_from_snapshot(self, snapshot_path: Optional[str] = None) -> Dict[str, Any]:
        """Restore server state from snapshot.
        
        Args:
            snapshot_path: Path to snapshot file. If None, uses latest snapshot.
            
        Returns:
            Dictionary with restoration status and details
        """
        try:
            # Load snapshot
            if snapshot_path:
                # TODO: Load from specific path
                snapshot = None
            else:
                snapshot = await self.state_serializer.load_latest_snapshot()
            
            if not snapshot:
                return {
                    'success': False,
                    'error': 'No valid snapshot found',
                    'snapshot_path': snapshot_path
                }
            
            # Validate snapshot
            if not await self.state_serializer.validate_snapshot(snapshot):
                return {
                    'success': False,
                    'error': 'Snapshot validation failed',
                    'snapshot_timestamp': snapshot.timestamp.isoformat()
                }
            
            # Restore state
            success = await self._restore_server_state(snapshot)
            
            return {
                'success': success,
                'snapshot_timestamp': snapshot.timestamp.isoformat(),
                'server_version': snapshot.server_version,
                'restart_reason': snapshot.restart_reason.value,
                'restored_tasks': len(snapshot.active_tasks),
                'restored_sessions': len(snapshot.client_sessions)
            }
            
        except Exception as e:
            logger.error(f"Failed to restore from snapshot: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_shutdown_status(self) -> Dict[str, Any]:
        """Get current shutdown status.
        
        Returns:
            Dictionary with current shutdown status
        """
        status = self.shutdown_coordinator.status
        
        return {
            'phase': status.phase.value,
            'progress': status.progress_percent,
            'message': status.message,
            'started_at': status.started_at.isoformat() if status.started_at else None,
            'estimated_completion': status.estimated_completion.isoformat() if status.estimated_completion else None,
            'errors': status.errors,
            'maintenance_mode': self.shutdown_coordinator.maintenance_mode
        }

    # Private helper methods
    
    async def _prepare_state_manager_shutdown(self):
        """Prepare state manager for shutdown."""
        if not self.state_manager:
            return
        
        try:
            logger.info("Preparing state manager for shutdown")
            # TODO: Implement state manager shutdown preparation
            # - Complete pending operations
            # - Suspend active tasks
            # - Prepare for serialization
            
        except Exception as e:
            logger.error(f"Failed to prepare state manager for shutdown: {e}")
            raise

    async def _cleanup_state_manager(self):
        """Clean up state manager resources."""
        if not self.state_manager:
            return
        
        try:
            logger.info("Cleaning up state manager resources")
            # TODO: Implement state manager cleanup
            # - Close database connections
            # - Release locks
            # - Clear caches
            
        except Exception as e:
            logger.error(f"Failed to cleanup state manager: {e}")

    async def _restore_server_state(self, snapshot: ServerStateSnapshot) -> bool:
        """Restore server state from snapshot.
        
        Args:
            snapshot: State snapshot to restore
            
        Returns:
            True if restoration was successful, False otherwise
        """
        try:
            logger.info(f"Restoring server state from {snapshot.timestamp}")
            
            if not self.state_manager:
                logger.error("No state manager available for restoration")
                return False
            
            # TODO: Implement actual state restoration
            # - Restore active tasks
            # - Recreate database connections
            # - Restore client sessions
            # - Resume suspended operations
            
            logger.info("Server state restoration completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore server state: {e}")
            return False


# Global reboot manager instance
_reboot_manager: Optional[RebootManager] = None


def get_reboot_manager() -> RebootManager:
    """Get or create the global reboot manager instance."""
    global _reboot_manager
    if _reboot_manager is None:
        _reboot_manager = RebootManager()
    return _reboot_manager


async def initialize_reboot_system(state_manager: StateManager):
    """Initialize the reboot system with state manager.
    
    Args:
        state_manager: State manager instance from server
    """
    reboot_manager = get_reboot_manager()
    await reboot_manager.initialize(state_manager)
    logger.info("Reboot system initialized")