"""
Retry coordination and policy management for error recovery.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Callable, Awaitable, Union
from dataclasses import dataclass
from ...domain.exceptions import BaseOrchestrationError, RecoveryStrategy

logger = logging.getLogger(__name__)


@dataclass
class RetryResult:
    """Result of a retry operation."""
    success: bool
    attempts: int
    total_time: float
    last_error: Optional[Exception] = None
    final_result: Optional[Any] = None


class RetryPolicy(ABC):
    """Abstract base class for retry policies."""
    
    @abstractmethod
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Determine if operation should be retried."""
        pass
    
    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """Get delay before next retry attempt."""
        pass


class ExponentialBackoffPolicy(RetryPolicy):
    """Exponential backoff retry policy."""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, backoff_factor: float = 2.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Retry if within attempt limit and error is retryable."""
        if attempt >= self.max_attempts:
            return False
        
        # Check if error is retryable
        if isinstance(error, BaseOrchestrationError):
            return error.is_retryable()
        
        # Default to retryable for standard exceptions
        return True
    
    def get_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))
        return min(delay, self.max_delay)


class LinearBackoffPolicy(RetryPolicy):
    """Linear backoff retry policy."""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, 
                 increment: float = 1.0, max_delay: float = 30.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.increment = increment
        self.max_delay = max_delay
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Retry if within attempt limit and error is retryable."""
        if attempt >= self.max_attempts:
            return False
        
        if isinstance(error, BaseOrchestrationError):
            return error.is_retryable()
        
        return True
    
    def get_delay(self, attempt: int) -> float:
        """Calculate linear backoff delay."""
        delay = self.base_delay + (self.increment * (attempt - 1))
        return min(delay, self.max_delay)


class FixedDelayPolicy(RetryPolicy):
    """Fixed delay retry policy."""
    
    def __init__(self, max_attempts: int = 3, delay: float = 5.0):
        self.max_attempts = max_attempts
        self.delay = delay
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Retry if within attempt limit and error is retryable."""
        if attempt >= self.max_attempts:
            return False
        
        if isinstance(error, BaseOrchestrationError):
            return error.is_retryable()
        
        return True
    
    def get_delay(self, attempt: int) -> float:
        """Return fixed delay."""
        return self.delay


class RetryCoordinator:
    """Coordinates retry operations with configurable policies."""
    
    def __init__(self, default_policy: Optional[RetryPolicy] = None):
        self.default_policy = default_policy or ExponentialBackoffPolicy()
        self.active_retries: Dict[str, int] = {}
    
    async def retry_async(
        self,
        operation: Callable[[], Awaitable[Any]],
        operation_id: str,
        policy: Optional[RetryPolicy] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RetryResult:
        """
        Execute an async operation with retry logic.
        
        Args:
            operation: Async callable to retry
            operation_id: Unique identifier for this operation
            policy: Retry policy to use (defaults to default_policy)
            context: Additional context for logging
            
        Returns:
            RetryResult with outcome information
        """
        retry_policy = policy or self.default_policy
        attempt = 0
        start_time = time.time()
        last_error = None
        
        # Track active retry
        self.active_retries[operation_id] = 0
        
        try:
            while True:
                attempt += 1
                self.active_retries[operation_id] = attempt
                
                try:
                    logger.debug(f"Retry attempt {attempt} for operation {operation_id}")
                    result = await operation()
                    
                    # Success!
                    total_time = time.time() - start_time
                    logger.info(f"Operation {operation_id} succeeded on attempt {attempt} after {total_time:.2f}s")
                    
                    return RetryResult(
                        success=True,
                        attempts=attempt,
                        total_time=total_time,
                        final_result=result
                    )
                
                except Exception as error:
                    last_error = error
                    logger.warning(f"Operation {operation_id} failed on attempt {attempt}: {error}")
                    
                    # Check if we should retry
                    if not retry_policy.should_retry(attempt, error):
                        break
                    
                    # Wait before next attempt
                    delay = retry_policy.get_delay(attempt)
                    logger.debug(f"Waiting {delay}s before retry {attempt + 1} for operation {operation_id}")
                    await asyncio.sleep(delay)
            
            # All retries exhausted
            total_time = time.time() - start_time
            logger.error(f"Operation {operation_id} failed after {attempt} attempts in {total_time:.2f}s")
            
            return RetryResult(
                success=False,
                attempts=attempt,
                total_time=total_time,
                last_error=last_error
            )
        
        finally:
            # Clean up tracking
            self.active_retries.pop(operation_id, None)
    
    def retry_sync(
        self,
        operation: Callable[[], Any],
        operation_id: str,
        policy: Optional[RetryPolicy] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RetryResult:
        """
        Execute a sync operation with retry logic.
        
        Args:
            operation: Callable to retry
            operation_id: Unique identifier for this operation
            policy: Retry policy to use (defaults to default_policy)
            context: Additional context for logging
            
        Returns:
            RetryResult with outcome information
        """
        retry_policy = policy or self.default_policy
        attempt = 0
        start_time = time.time()
        last_error = None
        
        # Track active retry
        self.active_retries[operation_id] = 0
        
        try:
            while True:
                attempt += 1
                self.active_retries[operation_id] = attempt
                
                try:
                    logger.debug(f"Retry attempt {attempt} for operation {operation_id}")
                    result = operation()
                    
                    # Success!
                    total_time = time.time() - start_time
                    logger.info(f"Operation {operation_id} succeeded on attempt {attempt} after {total_time:.2f}s")
                    
                    return RetryResult(
                        success=True,
                        attempts=attempt,
                        total_time=total_time,
                        final_result=result
                    )
                
                except Exception as error:
                    last_error = error
                    logger.warning(f"Operation {operation_id} failed on attempt {attempt}: {error}")
                    
                    # Check if we should retry
                    if not retry_policy.should_retry(attempt, error):
                        break
                    
                    # Wait before next attempt
                    delay = retry_policy.get_delay(attempt)
                    logger.debug(f"Waiting {delay}s before retry {attempt + 1} for operation {operation_id}")
                    time.sleep(delay)
            
            # All retries exhausted
            total_time = time.time() - start_time
            logger.error(f"Operation {operation_id} failed after {attempt} attempts in {total_time:.2f}s")
            
            return RetryResult(
                success=False,
                attempts=attempt,
                total_time=total_time,
                last_error=last_error
            )
        
        finally:
            # Clean up tracking
            self.active_retries.pop(operation_id, None)
    
    def get_active_retries(self) -> Dict[str, int]:
        """Get information about currently active retry operations."""
        return self.active_retries.copy()
    
    def cancel_retries(self, operation_id: str) -> bool:
        """
        Cancel active retries for an operation.
        
        Note: This only removes tracking; actual cancellation
        depends on the operation implementation.
        """
        return self.active_retries.pop(operation_id, None) is not None
    
    def get_retry_stats(self) -> Dict[str, Any]:
        """Get statistics about retry operations."""
        return {
            "active_retries": len(self.active_retries),
            "active_operations": list(self.active_retries.keys()),
            "default_policy": self.default_policy.__class__.__name__
        }


# Global retry coordinator instance
_global_retry_coordinator: Optional[RetryCoordinator] = None


def get_retry_coordinator() -> RetryCoordinator:
    """Get the global retry coordinator instance."""
    global _global_retry_coordinator
    if _global_retry_coordinator is None:
        _global_retry_coordinator = RetryCoordinator()
    return _global_retry_coordinator


def set_retry_coordinator(coordinator: RetryCoordinator):
    """Set the global retry coordinator instance."""
    global _global_retry_coordinator
    _global_retry_coordinator = coordinator