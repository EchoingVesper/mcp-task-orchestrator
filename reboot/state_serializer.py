"""
State serialization and restoration for server reboot functionality.

This module provides atomic state snapshots and restoration capabilities
to enable seamless server restarts without data loss.
"""

import asyncio
import json
import logging
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

from ..orchestrator.models import TaskBreakdown, SubTask, TaskStatus, SpecialistType

logger = logging.getLogger("mcp_task_orchestrator.server.state_serializer")


class RestartReason(str, Enum):
    """Reasons for server restart."""
    CONFIGURATION_UPDATE = "configuration_update"
    SCHEMA_MIGRATION = "schema_migration"
    ERROR_RECOVERY = "error_recovery"
    MANUAL_REQUEST = "manual_request"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"


@dataclass
class ClientSession:
    """Client session state for preservation across restarts."""
    session_id: str
    protocol_version: str
    connected_at: datetime
    last_activity: datetime
    pending_requests: List[Dict[str, Any]]
    context_data: Dict[str, Any]


@dataclass
class DatabaseState:
    """Database connection and transaction state."""
    db_path: str
    connection_metadata: Dict[str, Any]
    pending_transactions: List[Dict[str, Any]]
    integrity_checksum: str
    last_checkpoint: datetime


@dataclass
class ServerStateSnapshot:
    """Complete server state snapshot for serialization."""
    version: str = "1.0"
    timestamp: datetime = None
    server_version: str = "1.4.1"
    restart_reason: RestartReason = RestartReason.MANUAL_REQUEST
    
    # Core state components
    active_tasks: List[Dict[str, Any]] = None
    suspended_tasks: List[Dict[str, Any]] = None
    client_sessions: List[ClientSession] = None
    database_state: DatabaseState = None
    
    # Metadata
    process_id: int = None
    working_directory: str = None
    environment_vars: Dict[str, str] = None
    integrity_hash: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.active_tasks is None:
            self.active_tasks = []
        if self.suspended_tasks is None:
            self.suspended_tasks = []
        if self.client_sessions is None:
            self.client_sessions = []


class StateSerializer:
    """Handles server state serialization and restoration."""
    
    def __init__(self, base_dir: str = None):
        """Initialize state serializer.
        
        Args:
            base_dir: Base directory for state files. Defaults to .task_orchestrator/server_state/
        """
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), ".task_orchestrator", "server_state")
        
        self.state_dir = Path(base_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.lock = asyncio.Lock()
        
        # State file naming
        self.current_state_file = self.state_dir / "current_state.json"
        self.backup_pattern = "backup_state_{timestamp}.json"
        
        logger.info(f"StateSerializer initialized with state directory: {self.state_dir}")

    async def create_snapshot(self, 
                            state_manager,
                            restart_reason: RestartReason = RestartReason.MANUAL_REQUEST,
                            include_client_sessions: bool = True) -> ServerStateSnapshot:
        """Create atomic state snapshot.
        
        Args:
            state_manager: Current state manager instance
            restart_reason: Reason for creating snapshot
            include_client_sessions: Whether to include client session state
            
        Returns:
            ServerStateSnapshot containing complete server state
        """
        async with self.lock:
            try:
                logger.info(f"Creating state snapshot for restart reason: {restart_reason}")
                
                # Create snapshot object
                snapshot = ServerStateSnapshot(
                    restart_reason=restart_reason,
                    process_id=os.getpid(),
                    working_directory=os.getcwd(),
                    environment_vars=self._get_relevant_env_vars()
                )
                
                # Capture active tasks
                snapshot.active_tasks = await self._serialize_active_tasks(state_manager)
                snapshot.suspended_tasks = await self._serialize_suspended_tasks(state_manager)
                
                # Capture database state
                snapshot.database_state = await self._serialize_database_state(state_manager)
                
                # Capture client sessions if requested
                if include_client_sessions:
                    snapshot.client_sessions = await self._serialize_client_sessions()
                
                # Generate integrity hash
                snapshot.integrity_hash = self._generate_integrity_hash(snapshot)
                
                logger.info(f"State snapshot created successfully with {len(snapshot.active_tasks)} active tasks")
                return snapshot
                
            except Exception as e:
                logger.error(f"Failed to create state snapshot: {e}")
                raise

    async def save_snapshot(self, snapshot: ServerStateSnapshot, backup: bool = True) -> str:
        """Save snapshot to disk atomically.
        
        Args:
            snapshot: Snapshot to save
            backup: Whether to create backup of existing state
            
        Returns:
            Path to saved state file
        """
        async with self.lock:
            try:
                # Create backup if requested and current state exists
                if backup and self.current_state_file.exists():
                    await self._create_backup()
                
                # Convert snapshot to JSON-serializable format
                state_data = self._snapshot_to_dict(snapshot)
                
                # Write to temporary file first for atomicity
                temp_file = self.current_state_file.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(state_data, f, indent=2, default=str)
                
                # Atomic move to final location
                temp_file.replace(self.current_state_file)
                
                logger.info(f"State snapshot saved to: {self.current_state_file}")
                return str(self.current_state_file)
                
            except Exception as e:
                logger.error(f"Failed to save state snapshot: {e}")
                raise

    async def load_latest_snapshot(self) -> Optional[ServerStateSnapshot]:
        """Load the most recent state snapshot.
        
        Returns:
            ServerStateSnapshot if found and valid, None otherwise
        """
        try:
            if not self.current_state_file.exists():
                logger.warning("No current state file found")
                return None
            
            with open(self.current_state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            snapshot = self._dict_to_snapshot(state_data)
            
            # Validate integrity
            if not await self.validate_snapshot(snapshot):
                logger.error("State snapshot failed integrity validation")
                return None
            
            logger.info(f"Loaded state snapshot from {snapshot.timestamp}")
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to load state snapshot: {e}")
            return None

    async def validate_snapshot(self, snapshot: ServerStateSnapshot) -> bool:
        """Validate snapshot integrity and consistency.
        
        Args:
            snapshot: Snapshot to validate
            
        Returns:
            True if snapshot is valid, False otherwise
        """
        try:
            # Check required fields
            if not snapshot.timestamp or not snapshot.version:
                logger.error("Snapshot missing required fields")
                return False
            
            # Validate integrity hash
            expected_hash = self._generate_integrity_hash(snapshot)
            if snapshot.integrity_hash != expected_hash:
                logger.error("Snapshot integrity hash mismatch")
                return False
            
            # Validate task data structure
            for task_data in snapshot.active_tasks:
                if not isinstance(task_data, dict) or 'task_id' not in task_data:
                    logger.error("Invalid task data in snapshot")
                    return False
            
            # Validate database state
            if snapshot.database_state and not snapshot.database_state.db_path:
                logger.error("Invalid database state in snapshot")
                return False
            
            logger.info("State snapshot validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Snapshot validation failed: {e}")
            return False

    async def cleanup_old_snapshots(self, keep_count: int = 5):
        """Clean up old backup snapshots, keeping only the most recent.
        
        Args:
            keep_count: Number of backup snapshots to keep
        """
        try:
            # Find all backup files
            backup_files = list(self.state_dir.glob("backup_state_*.json"))
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Remove old backups beyond keep_count
            for backup_file in backup_files[keep_count:]:
                backup_file.unlink()
                logger.debug(f"Removed old backup: {backup_file}")
            
            logger.info(f"Cleanup completed, kept {min(len(backup_files), keep_count)} backups")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old snapshots: {e}")

    # Private helper methods
    
    async def _serialize_active_tasks(self, state_manager) -> List[Dict[str, Any]]:
        """Serialize active tasks from state manager."""
        try:
            tasks = []
            # Get all active tasks from state manager
            all_tasks = await state_manager.get_all_tasks()
            
            for task in all_tasks:
                if task.status in [TaskStatus.ACTIVE, TaskStatus.PENDING]:
                    task_dict = {
                        'task_id': task.parent_task_id,
                        'description': task.description,
                        'complexity': task.complexity,
                        'status': task.status.value,
                        'created_at': task.created_at.isoformat() if task.created_at else None,
                        'subtasks': [
                            {
                                'task_id': st.task_id,
                                'title': st.title,
                                'description': st.description,
                                'specialist_type': st.specialist_type.value,
                                'status': st.status.value,
                                'dependencies': st.dependencies,
                                'estimated_effort': st.estimated_effort,
                                'results': st.results,
                                'artifacts': st.artifacts
                            }
                            for st in task.subtasks
                        ]
                    }
                    tasks.append(task_dict)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to serialize active tasks: {e}")
            return []

    async def _serialize_suspended_tasks(self, state_manager) -> List[Dict[str, Any]]:
        """Serialize suspended tasks."""
        # For now, return empty list - will be implemented when task suspension is added
        return []

    async def _serialize_database_state(self, state_manager) -> DatabaseState:
        """Serialize database connection state."""
        try:
            return DatabaseState(
                db_path=state_manager.db_path,
                connection_metadata={
                    'initialized': state_manager._initialized,
                    'base_dir': getattr(state_manager, 'base_dir', None)
                },
                pending_transactions=[],  # TODO: Implement transaction tracking
                integrity_checksum=self._calculate_db_checksum(state_manager.db_path),
                last_checkpoint=datetime.now(timezone.utc)
            )
        except Exception as e:
            logger.error(f"Failed to serialize database state: {e}")
            return DatabaseState(
                db_path="",
                connection_metadata={},
                pending_transactions=[],
                integrity_checksum="",
                last_checkpoint=datetime.now(timezone.utc)
            )

    async def _serialize_client_sessions(self) -> List[ClientSession]:
        """Serialize client session state."""
        # TODO: Implement client session tracking
        # For now, return empty list
        return []

    def _get_relevant_env_vars(self) -> Dict[str, str]:
        """Get environment variables relevant for restart."""
        relevant_vars = [
            'MCP_TASK_ORCHESTRATOR_LOG_LEVEL',
            'MCP_TASK_ORCHESTRATOR_DB_PATH',
            'MCP_TASK_ORCHESTRATOR_BASE_DIR'
        ]
        
        return {var: os.environ.get(var, '') for var in relevant_vars if os.environ.get(var)}

    def _generate_integrity_hash(self, snapshot: ServerStateSnapshot) -> str:
        """Generate integrity hash for snapshot validation."""
        # Create deterministic representation for hashing
        hash_data = {
            'timestamp': snapshot.timestamp.isoformat(),
            'server_version': snapshot.server_version,
            'active_tasks_count': len(snapshot.active_tasks),
            'suspended_tasks_count': len(snapshot.suspended_tasks),
            'client_sessions_count': len(snapshot.client_sessions)
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

    def _calculate_db_checksum(self, db_path: str) -> str:
        """Calculate database file checksum."""
        try:
            if not os.path.exists(db_path):
                return ""
            
            hash_sha256 = hashlib.sha256()
            with open(db_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to calculate database checksum: {e}")
            return ""

    async def _create_backup(self):
        """Create backup of current state file."""
        if not self.current_state_file.exists():
            return
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_file = self.state_dir / self.backup_pattern.format(timestamp=timestamp)
        
        import shutil
        shutil.copy2(self.current_state_file, backup_file)
        logger.debug(f"Created backup: {backup_file}")

    def _snapshot_to_dict(self, snapshot: ServerStateSnapshot) -> Dict[str, Any]:
        """Convert snapshot to JSON-serializable dictionary."""
        # Convert dataclass to dict
        result = asdict(snapshot)
        
        # Handle datetime serialization
        if isinstance(result['timestamp'], datetime):
            result['timestamp'] = result['timestamp'].isoformat()
        
        # Handle database_state datetime
        if result['database_state'] and 'last_checkpoint' in result['database_state']:
            result['database_state']['last_checkpoint'] = result['database_state']['last_checkpoint'].isoformat()
        
        # Handle client sessions datetimes
        for session in result['client_sessions']:
            if 'connected_at' in session:
                session['connected_at'] = session['connected_at'].isoformat()
            if 'last_activity' in session:
                session['last_activity'] = session['last_activity'].isoformat()
        
        return result

    def _dict_to_snapshot(self, data: Dict[str, Any]) -> ServerStateSnapshot:
        """Convert dictionary back to ServerStateSnapshot."""
        # Handle datetime parsing
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Handle database_state datetime
        if data.get('database_state') and 'last_checkpoint' in data['database_state']:
            db_state = data['database_state']
            if isinstance(db_state['last_checkpoint'], str):
                db_state['last_checkpoint'] = datetime.fromisoformat(db_state['last_checkpoint'])
            data['database_state'] = DatabaseState(**db_state)
        
        # Handle client sessions
        client_sessions = []
        for session_data in data.get('client_sessions', []):
            if 'connected_at' in session_data and isinstance(session_data['connected_at'], str):
                session_data['connected_at'] = datetime.fromisoformat(session_data['connected_at'])
            if 'last_activity' in session_data and isinstance(session_data['last_activity'], str):
                session_data['last_activity'] = datetime.fromisoformat(session_data['last_activity'])
            client_sessions.append(ClientSession(**session_data))
        
        data['client_sessions'] = client_sessions
        
        # Handle restart reason enum
        if 'restart_reason' in data and isinstance(data['restart_reason'], str):
            data['restart_reason'] = RestartReason(data['restart_reason'])
        
        return ServerStateSnapshot(**data)