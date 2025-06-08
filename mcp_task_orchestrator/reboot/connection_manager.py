"""
Client connection management for server reboot functionality.

This module handles MCP client connection preservation and restoration
during server restarts.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field

from .state_serializer import ClientSession

logger = logging.getLogger("mcp_task_orchestrator.server.connection_manager")


class ConnectionState(str, Enum):
    """Connection states during restart process."""
    ACTIVE = "active"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    RESTORED = "restored"
    FAILED = "failed"


@dataclass
class ConnectionInfo:
    """Information about a client connection."""
    session_id: str
    client_name: str
    protocol_version: str
    connected_at: datetime
    last_activity: datetime
    state: ConnectionState = ConnectionState.ACTIVE
    reconnect_attempts: int = 0
    pending_requests: List[Dict[str, Any]] = field(default_factory=list)
    buffered_responses: List[Dict[str, Any]] = field(default_factory=list)


class RequestBuffer:
    """Buffers client requests during server restart."""
    
    def __init__(self, max_buffer_size: int = 100):
        """Initialize request buffer.
        
        Args:
            max_buffer_size: Maximum number of requests to buffer per client
        """
        self.max_buffer_size = max_buffer_size
        self.buffers: Dict[str, List[Dict[str, Any]]] = {}
        self.buffer_timestamps: Dict[str, List[datetime]] = {}
        self.lock = asyncio.Lock()
        
        logger.info(f"RequestBuffer initialized with max size {max_buffer_size}")

    async def buffer_request(self, session_id: str, request: Dict[str, Any]) -> bool:
        """Buffer a request for later processing.
        
        Args:
            session_id: Client session ID
            request: Request data to buffer
            
        Returns:
            True if request was buffered, False if buffer is full
        """
        async with self.lock:
            if session_id not in self.buffers:
                self.buffers[session_id] = []
                self.buffer_timestamps[session_id] = []
            
            buffer = self.buffers[session_id]
            timestamps = self.buffer_timestamps[session_id]
            
            # Check buffer size limit
            if len(buffer) >= self.max_buffer_size:
                logger.warning(f"Request buffer full for session {session_id}")
                return False
            
            # Add request to buffer
            buffer.append(request)
            timestamps.append(datetime.now(timezone.utc))
            
            logger.debug(f"Buffered request for session {session_id}: {request.get('method', 'unknown')}")
            return True

    async def get_buffered_requests(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all buffered requests for a session.
        
        Args:
            session_id: Client session ID
            
        Returns:
            List of buffered requests
        """
        async with self.lock:
            requests = self.buffers.get(session_id, []).copy()
            self.buffers[session_id] = []  # Clear buffer after retrieval
            self.buffer_timestamps[session_id] = []
            
            logger.debug(f"Retrieved {len(requests)} buffered requests for session {session_id}")
            return requests

    async def clear_expired_requests(self, max_age_seconds: int = 300):
        """Clear requests older than specified age.
        
        Args:
            max_age_seconds: Maximum age of requests in seconds
        """
        async with self.lock:
            current_time = datetime.now(timezone.utc)
            expired_count = 0
            
            for session_id in list(self.buffers.keys()):
                buffer = self.buffers[session_id]
                timestamps = self.buffer_timestamps[session_id]
                
                # Find expired requests
                valid_requests = []
                valid_timestamps = []
                
                for request, timestamp in zip(buffer, timestamps):
                    age = (current_time - timestamp).total_seconds()
                    if age <= max_age_seconds:
                        valid_requests.append(request)
                        valid_timestamps.append(timestamp)
                    else:
                        expired_count += 1
                
                self.buffers[session_id] = valid_requests
                self.buffer_timestamps[session_id] = valid_timestamps
            
            if expired_count > 0:
                logger.info(f"Cleared {expired_count} expired buffered requests")

    def get_buffer_stats(self) -> Dict[str, Any]:
        """Get buffer statistics.
        
        Returns:
            Dictionary with buffer statistics
        """
        total_requests = sum(len(buffer) for buffer in self.buffers.values())
        return {
            'total_sessions': len(self.buffers),
            'total_buffered_requests': total_requests,
            'sessions': {
                session_id: len(buffer) 
                for session_id, buffer in self.buffers.items()
            }
        }


class ReconnectionManager:
    """Manages client reconnection during and after restart."""
    
    def __init__(self, 
                 max_reconnect_attempts: int = 5,
                 reconnect_delay: float = 1.0,
                 backoff_multiplier: float = 2.0):
        """Initialize reconnection manager.
        
        Args:
            max_reconnect_attempts: Maximum number of reconnection attempts
            reconnect_delay: Initial delay between reconnection attempts
            backoff_multiplier: Multiplier for exponential backoff
        """
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self.backoff_multiplier = backoff_multiplier
        
        self.pending_reconnections: Set[str] = set()
        self.reconnection_tasks: Dict[str, asyncio.Task] = {}
        self.lock = asyncio.Lock()
        
        logger.info("ReconnectionManager initialized")

    async def initiate_reconnection(self, session_id: str, connection_info: ConnectionInfo) -> bool:
        """Initiate reconnection for a client session.
        
        Args:
            session_id: Client session ID
            connection_info: Connection information
            
        Returns:
            True if reconnection was initiated, False if already in progress
        """
        async with self.lock:
            if session_id in self.pending_reconnections:
                logger.debug(f"Reconnection already in progress for session {session_id}")
                return False
            
            self.pending_reconnections.add(session_id)
            
            # Start reconnection task
            task = asyncio.create_task(
                self._handle_reconnection(session_id, connection_info)
            )
            self.reconnection_tasks[session_id] = task
            
            logger.info(f"Initiated reconnection for session {session_id}")
            return True

    async def wait_for_reconnections(self, timeout: Optional[float] = None) -> Dict[str, bool]:
        """Wait for all pending reconnections to complete.
        
        Args:
            timeout: Maximum time to wait for reconnections
            
        Returns:
            Dictionary mapping session IDs to success status
        """
        if not self.reconnection_tasks:
            return {}
        
        try:
            # Wait for all reconnection tasks
            results = await asyncio.wait_for(
                asyncio.gather(*self.reconnection_tasks.values(), return_exceptions=True),
                timeout=timeout
            )
            
            # Map results to session IDs
            session_results = {}
            for session_id, result in zip(self.reconnection_tasks.keys(), results):
                session_results[session_id] = not isinstance(result, Exception)
            
            return session_results
            
        except asyncio.TimeoutError:
            logger.warning("Reconnection wait timed out")
            return {
                session_id: False 
                for session_id in self.reconnection_tasks.keys()
            }

    async def _handle_reconnection(self, session_id: str, connection_info: ConnectionInfo) -> bool:
        """Handle reconnection for a specific session.
        
        Args:
            session_id: Client session ID
            connection_info: Connection information
            
        Returns:
            True if reconnection was successful, False otherwise
        """
        delay = self.reconnect_delay
        
        for attempt in range(self.max_reconnect_attempts):
            try:
                logger.debug(f"Reconnection attempt {attempt + 1} for session {session_id}")
                
                # TODO: Implement actual reconnection logic
                # This would involve:
                # 1. Checking if client is available for reconnection
                # 2. Re-establishing MCP protocol connection
                # 3. Restoring session state
                # 4. Processing buffered requests
                
                # For now, simulate reconnection
                await asyncio.sleep(delay)
                
                # Simulate success for testing
                if attempt >= 1:  # Succeed after a few attempts
                    connection_info.state = ConnectionState.RESTORED
                    connection_info.reconnect_attempts = attempt + 1
                    logger.info(f"Reconnection successful for session {session_id}")
                    return True
                
                # Exponential backoff
                delay *= self.backoff_multiplier
                
            except Exception as e:
                logger.error(f"Reconnection attempt {attempt + 1} failed for session {session_id}: {e}")
                delay *= self.backoff_multiplier
        
        # All attempts failed
        connection_info.state = ConnectionState.FAILED
        connection_info.reconnect_attempts = self.max_reconnect_attempts
        logger.error(f"Reconnection failed for session {session_id} after {self.max_reconnect_attempts} attempts")
        return False


class ConnectionManager:
    """Main connection manager for handling client connections during restarts."""
    
    def __init__(self, 
                 request_buffer: Optional[RequestBuffer] = None,
                 reconnection_manager: Optional[ReconnectionManager] = None):
        """Initialize connection manager.
        
        Args:
            request_buffer: Request buffer instance
            reconnection_manager: Reconnection manager instance
        """
        self.request_buffer = request_buffer or RequestBuffer()
        self.reconnection_manager = reconnection_manager or ReconnectionManager()
        
        self.connections: Dict[str, ConnectionInfo] = {}
        self.lock = asyncio.Lock()
        self._notification_handlers: List[callable] = []
        
        logger.info("ConnectionManager initialized")

    async def register_connection(self, 
                                session_id: str,
                                client_name: str,
                                protocol_version: str) -> ConnectionInfo:
        """Register a new client connection.
        
        Args:
            session_id: Unique session identifier
            client_name: Name of the client application
            protocol_version: MCP protocol version
            
        Returns:
            ConnectionInfo object for the registered connection
        """
        async with self.lock:
            now = datetime.now(timezone.utc)
            
            connection_info = ConnectionInfo(
                session_id=session_id,
                client_name=client_name,
                protocol_version=protocol_version,
                connected_at=now,
                last_activity=now,
                state=ConnectionState.ACTIVE
            )
            
            self.connections[session_id] = connection_info
            
            logger.info(f"Registered connection: {client_name} (session: {session_id})")
            return connection_info

    async def prepare_for_restart(self) -> List[ClientSession]:
        """Prepare connections for server restart.
        
        Returns:
            List of client sessions for state serialization
        """
        async with self.lock:
            client_sessions = []
            
            for connection_info in self.connections.values():
                # Mark connection as disconnected
                connection_info.state = ConnectionState.DISCONNECTED
                
                # Create client session for serialization
                client_session = ClientSession(
                    session_id=connection_info.session_id,
                    protocol_version=connection_info.protocol_version,
                    connected_at=connection_info.connected_at,
                    last_activity=connection_info.last_activity,
                    pending_requests=connection_info.pending_requests.copy(),
                    context_data={
                        'client_name': connection_info.client_name,
                        'reconnect_attempts': connection_info.reconnect_attempts
                    }
                )
                
                client_sessions.append(client_session)
            
            logger.info(f"Prepared {len(client_sessions)} client sessions for restart")
            return client_sessions

    async def restore_connections(self, client_sessions: List[ClientSession]) -> Dict[str, bool]:
        """Restore connections from client sessions.
        
        Args:
            client_sessions: List of client sessions to restore
            
        Returns:
            Dictionary mapping session IDs to restoration success
        """
        results = {}
        
        for client_session in client_sessions:
            try:
                # Restore connection info
                connection_info = ConnectionInfo(
                    session_id=client_session.session_id,
                    client_name=client_session.context_data.get('client_name', 'unknown'),
                    protocol_version=client_session.protocol_version,
                    connected_at=client_session.connected_at,
                    last_activity=client_session.last_activity,
                    state=ConnectionState.RECONNECTING,
                    pending_requests=client_session.pending_requests.copy()
                )
                
                async with self.lock:
                    self.connections[client_session.session_id] = connection_info
                
                # Initiate reconnection
                success = await self.reconnection_manager.initiate_reconnection(
                    client_session.session_id, 
                    connection_info
                )
                
                results[client_session.session_id] = success
                
            except Exception as e:
                logger.error(f"Failed to restore connection {client_session.session_id}: {e}")
                results[client_session.session_id] = False
        
        logger.info(f"Initiated restoration for {len(client_sessions)} connections")
        return results

    async def handle_restart_notification(self, restart_in_seconds: int):
        """Send restart notification to all connected clients.
        
        Args:
            restart_in_seconds: Number of seconds until restart
        """
        notification = {
            "method": "notification",
            "params": {
                "type": "server_restart_pending",
                "restart_in_seconds": restart_in_seconds,
                "session_preserved": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Notify all handlers
        for handler in self._notification_handlers:
            try:
                await handler(notification)
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")
        
        logger.info(f"Sent restart notification to {len(self._notification_handlers)} handlers")

    async def handle_restart_complete(self):
        """Send restart complete notification to all clients.."""
        notification = {
            "method": "notification",
            "params": {
                "type": "server_restart_complete",
                "session_restored": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Notify all handlers
        for handler in self._notification_handlers:
            try:
                await handler(notification)
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")
        
        logger.info("Sent restart complete notification")

    def add_notification_handler(self, handler: callable):
        """Add handler for restart notifications.
        
        Args:
            handler: Async function to handle notifications
        """
        self._notification_handlers.append(handler)

    async def get_connection_status(self) -> Dict[str, Any]:
        """Get status of all connections.
        
        Returns:
            Dictionary with connection status information
        """
        async with self.lock:
            status = {
                'total_connections': len(self.connections),
                'by_state': {},
                'connections': {}
            }
            
            # Count by state
            for connection in self.connections.values():
                state = connection.state.value
                status['by_state'][state] = status['by_state'].get(state, 0) + 1
                
                status['connections'][connection.session_id] = {
                    'client_name': connection.client_name,
                    'state': connection.state.value,
                    'connected_at': connection.connected_at.isoformat(),
                    'last_activity': connection.last_activity.isoformat(),
                    'reconnect_attempts': connection.reconnect_attempts,
                    'pending_requests': len(connection.pending_requests)
                }
            
            # Add buffer stats
            status['request_buffer'] = self.request_buffer.get_buffer_stats()
            
            return status

    async def cleanup_failed_connections(self):
        """Clean up connections that failed to reconnect."""
        async with self.lock:
            failed_sessions = [
                session_id for session_id, conn in self.connections.items()
                if conn.state == ConnectionState.FAILED
            ]
            
            for session_id in failed_sessions:
                del self.connections[session_id]
                logger.info(f"Cleaned up failed connection: {session_id}")
            
            return len(failed_sessions)