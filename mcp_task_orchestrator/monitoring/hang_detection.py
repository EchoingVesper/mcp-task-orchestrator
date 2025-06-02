#!/usr/bin/env python3
"""
MCP Tool Hanging Points Analysis and Monitoring System

This module provides comprehensive analysis, monitoring, and prevention of hanging 
issues in the MCP Task Orchestrator tool.
"""

import asyncio
import logging
import time
import signal
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from contextlib import asynccontextmanager
from functools import wraps
import inspect
import traceback

logger = logging.getLogger("mcp_tool_hanging_analysis")


class HangDetector:
    """Detects and monitors potential hanging operations."""
    
    def __init__(self, operation_timeout: float = 30.0, warning_timeout: float = 10.0):
        self.operation_timeout = operation_timeout
        self.warning_timeout = warning_timeout
        self.active_operations: Dict[str, dict] = {}
        self.hang_statistics: Dict[str, int] = {}
        self._monitor_task: Optional[asyncio.Task] = None
        self._shutdown = False
    
    def start_monitoring(self):
        """Start the hang detection monitoring."""
        if self._monitor_task is None or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(self._monitor_operations())
            logger.info("Hang detection monitoring started")
    
    def stop_monitoring(self):
        """Stop the hang detection monitoring."""
        self._shutdown = True
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            logger.info("Hang detection monitoring stopped")
    
    async def _monitor_operations(self):
        """Monitor active operations for potential hangs."""
        while not self._shutdown:
            try:
                current_time = time.time()
                
                for op_id, op_info in list(self.active_operations.items()):
                    duration = current_time - op_info['start_time']
                    
                    # Warning for long-running operations
                    if duration > self.warning_timeout and not op_info.get('warning_logged'):
                        logger.warning(
                            f"Operation {op_id} ({op_info['operation']}) has been running for "
                            f"{duration:.1f}s - potential hang detected"
                        )
                        op_info['warning_logged'] = True
                    
                    # Timeout for hanging operations
                    if duration > self.operation_timeout:
                        logger.error(
                            f"Operation {op_id} ({op_info['operation']}) exceeded timeout "
                            f"({self.operation_timeout}s) - forcing cleanup"
                        )
                        
                        # Record hang statistics
                        operation_name = op_info['operation']
                        self.hang_statistics[operation_name] = self.hang_statistics.get(operation_name, 0) + 1
                        
                        # Clean up the operation
                        self._cleanup_hanging_operation(op_id, op_info)
                
                await asyncio.sleep(1.0)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in hang monitor: {str(e)}")
                await asyncio.sleep(5.0)  # Wait longer on error
    
    def _cleanup_hanging_operation(self, op_id: str, op_info: dict):
        """Clean up a hanging operation."""
        try:
            # Remove from active operations
            self.active_operations.pop(op_id, None)
            
            # If there's a cancellation token, use it
            if 'cancel_token' in op_info and op_info['cancel_token']:
                try:
                    op_info['cancel_token'].cancel()
                except Exception as e:
                    logger.warning(f"Failed to cancel operation {op_id}: {str(e)}")
            
            logger.info(f"Cleaned up hanging operation {op_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up hanging operation {op_id}: {str(e)}")
    
    def register_operation(self, operation_name: str, operation_id: str = None, 
                          cancel_token: Optional[asyncio.Task] = None) -> str:
        """Register an operation for monitoring."""
        if operation_id is None:
            operation_id = f"{operation_name}_{int(time.time() * 1000000)}"
        
        self.active_operations[operation_id] = {
            'operation': operation_name,
            'start_time': time.time(),
            'cancel_token': cancel_token,
            'warning_logged': False
        }
        
        logger.debug(f"Registered operation {operation_id} ({operation_name})")
        return operation_id
    
    def unregister_operation(self, operation_id: str):
        """Unregister a completed operation."""
        if operation_id in self.active_operations:
            duration = time.time() - self.active_operations[operation_id]['start_time']
            operation_name = self.active_operations[operation_id]['operation']
            
            self.active_operations.pop(operation_id, None)
            logger.debug(f"Unregistered operation {operation_id} ({operation_name}) after {duration:.2f}s")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get hang detection statistics."""
        return {
            'active_operations': len(self.active_operations),
            'active_operation_details': [
                {
                    'id': op_id,
                    'operation': op_info['operation'],
                    'duration': time.time() - op_info['start_time'],
                    'warning_logged': op_info.get('warning_logged', False)
                }
                for op_id, op_info in self.active_operations.items()
            ],
            'hang_statistics': self.hang_statistics.copy(),
            'total_hangs_detected': sum(self.hang_statistics.values())
        }


# Global hang detector instance
_hang_detector = HangDetector()


def with_hang_detection(operation_name: str = None, timeout: float = 30.0):
    """Decorator to add hang detection to async operations."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal operation_name
            if operation_name is None:
                operation_name = f"{func.__module__}.{func.__qualname__}"
            
            # Start monitoring
            _hang_detector.start_monitoring()
            
            # Create a task for the operation
            operation_task = asyncio.create_task(func(*args, **kwargs))
            
            # Register with hang detector
            op_id = _hang_detector.register_operation(operation_name, cancel_token=operation_task)
            
            try:
                # Wait for completion with timeout
                result = await asyncio.wait_for(operation_task, timeout=timeout)
                return result
            except asyncio.TimeoutError:
                logger.error(f"Operation {operation_name} timed out after {timeout}s")
                operation_task.cancel()
                raise
            finally:
                # Unregister operation
                _hang_detector.unregister_operation(op_id)
        
        return wrapper
    return decorator
