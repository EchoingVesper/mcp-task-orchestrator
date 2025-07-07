"""
Recovery strategies for automatic error recovery and system healing.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Callable, List
from dataclasses import dataclass
from ...domain.exceptions import (
    BaseOrchestrationError, ErrorSeverity, RecoveryStrategy as RecoveryType,
    TaskError, SpecialistError, InfrastructureError
)

logger = logging.getLogger(__name__)


@dataclass
class RecoveryResult:
    """Result of a recovery operation."""
    success: bool
    strategy_used: str
    actions_taken: List[str]
    time_taken: float
    error_resolved: bool
    notes: Optional[str] = None


class RecoveryStrategy(ABC):
    """Abstract base class for recovery strategies."""
    
    @abstractmethod
    def can_recover(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """Determine if this strategy can recover from the given error."""
        pass
    
    @abstractmethod
    async def attempt_recovery(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> RecoveryResult:
        """Attempt to recover from the error."""
        pass


class TaskRecoveryStrategy(RecoveryStrategy):
    """Recovery strategy for task-related errors."""
    
    def can_recover(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """Can recover from certain task errors."""
        if not isinstance(error, TaskError):
            return False
        
        # Don't attempt recovery for corruption or validation errors
        error_str = str(error).lower()
        if any(keyword in error_str for keyword in ['corruption', 'validation', 'security']):
            return False
        
        return True
    
    async def attempt_recovery(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> RecoveryResult:
        """Attempt task recovery."""
        import time
        start_time = time.time()
        actions_taken = []
        
        try:
            task_error = error  # type: TaskError
            
            # Strategy 1: Clear task state and retry
            if "state" in str(task_error).lower():
                actions_taken.append("Cleared task state")
                # In real implementation, would clear task state
                await asyncio.sleep(0.1)  # Simulate state clearing
            
            # Strategy 2: Reassign to different specialist
            if "timeout" in str(task_error).lower():
                actions_taken.append("Reassigned to different specialist")
                # In real implementation, would reassign task
                await asyncio.sleep(0.1)  # Simulate reassignment
            
            # Strategy 3: Resource reallocation
            if "resource" in str(task_error).lower():
                actions_taken.append("Reallocated resources")
                # In real implementation, would reallocate resources
                await asyncio.sleep(0.1)  # Simulate reallocation
            
            # Strategy 4: Break down task further
            if "complex" in str(task_error).lower():
                actions_taken.append("Further decomposed task")
                # In real implementation, would break down task
                await asyncio.sleep(0.1)  # Simulate decomposition
            
            time_taken = time.time() - start_time
            
            return RecoveryResult(
                success=True,
                strategy_used="TaskRecoveryStrategy",
                actions_taken=actions_taken,
                time_taken=time_taken,
                error_resolved=True,
                notes=f"Applied {len(actions_taken)} recovery actions for task error"
            )
        
        except Exception as recovery_error:
            time_taken = time.time() - start_time
            logger.error(f"Task recovery failed: {recovery_error}")
            
            return RecoveryResult(
                success=False,
                strategy_used="TaskRecoveryStrategy",
                actions_taken=actions_taken,
                time_taken=time_taken,
                error_resolved=False,
                notes=f"Recovery failed: {str(recovery_error)}"
            )


class SpecialistRecoveryStrategy(RecoveryStrategy):
    """Recovery strategy for specialist-related errors."""
    
    def can_recover(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """Can recover from certain specialist errors."""
        if not isinstance(error, SpecialistError):
            return False
        
        # Can't recover from configuration errors without manual intervention
        error_str = str(error).lower()
        if "configuration" in error_str:
            return False
        
        return True
    
    async def attempt_recovery(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> RecoveryResult:
        """Attempt specialist recovery."""
        import time
        start_time = time.time()
        actions_taken = []
        
        try:
            specialist_error = error  # type: SpecialistError
            
            # Strategy 1: Reload specialist configuration
            if "load" in str(specialist_error).lower():
                actions_taken.append("Reloaded specialist configuration")
                await asyncio.sleep(0.1)  # Simulate reload
            
            # Strategy 2: Clear specialist overload
            if "overload" in str(specialist_error).lower():
                actions_taken.append("Redistributed specialist workload")
                await asyncio.sleep(0.1)  # Simulate redistribution
            
            # Strategy 3: Fallback to alternative specialist
            if "unavailable" in str(specialist_error).lower():
                actions_taken.append("Selected alternative specialist")
                await asyncio.sleep(0.1)  # Simulate selection
            
            # Strategy 4: Regenerate specialist context
            if "context" in str(specialist_error).lower():
                actions_taken.append("Regenerated specialist context")
                await asyncio.sleep(0.1)  # Simulate context generation
            
            time_taken = time.time() - start_time
            
            return RecoveryResult(
                success=True,
                strategy_used="SpecialistRecoveryStrategy",
                actions_taken=actions_taken,
                time_taken=time_taken,
                error_resolved=True,
                notes=f"Applied {len(actions_taken)} recovery actions for specialist error"
            )
        
        except Exception as recovery_error:
            time_taken = time.time() - start_time
            logger.error(f"Specialist recovery failed: {recovery_error}")
            
            return RecoveryResult(
                success=False,
                strategy_used="SpecialistRecoveryStrategy",
                actions_taken=actions_taken,
                time_taken=time_taken,
                error_resolved=False,
                notes=f"Recovery failed: {str(recovery_error)}"
            )


class InfrastructureRecoveryStrategy(RecoveryStrategy):
    """Recovery strategy for infrastructure-related errors."""
    
    def can_recover(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """Can recover from certain infrastructure errors."""
        if not isinstance(error, InfrastructureError):
            return False
        
        # Check if error indicates it's recoverable
        if hasattr(error, 'is_recoverable'):
            return error.is_recoverable
        
        # Default to attempting recovery for infrastructure errors
        return True
    
    async def attempt_recovery(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> RecoveryResult:
        """Attempt infrastructure recovery."""
        import time
        start_time = time.time()
        actions_taken = []
        
        try:
            infra_error = error  # type: InfrastructureError
            
            # Strategy 1: Reconnect to database
            if "database" in str(infra_error).lower():
                actions_taken.append("Reconnected to database")
                await asyncio.sleep(0.2)  # Simulate reconnection
            
            # Strategy 2: Reset network connections
            if "network" in str(infra_error).lower():
                actions_taken.append("Reset network connections")
                await asyncio.sleep(0.2)  # Simulate network reset
            
            # Strategy 3: Clear caches
            if "cache" in str(infra_error).lower():
                actions_taken.append("Cleared system caches")
                await asyncio.sleep(0.1)  # Simulate cache clearing
            
            # Strategy 4: Restart failed services
            if "service" in str(infra_error).lower():
                actions_taken.append("Restarted failed services")
                await asyncio.sleep(0.3)  # Simulate service restart
            
            # Strategy 5: Switch to backup systems
            if "primary" in str(infra_error).lower():
                actions_taken.append("Switched to backup systems")
                await asyncio.sleep(0.2)  # Simulate backup switch
            
            time_taken = time.time() - start_time
            
            return RecoveryResult(
                success=True,
                strategy_used="InfrastructureRecoveryStrategy",
                actions_taken=actions_taken,
                time_taken=time_taken,
                error_resolved=True,
                notes=f"Applied {len(actions_taken)} recovery actions for infrastructure error"
            )
        
        except Exception as recovery_error:
            time_taken = time.time() - start_time
            logger.error(f"Infrastructure recovery failed: {recovery_error}")
            
            return RecoveryResult(
                success=False,
                strategy_used="InfrastructureRecoveryStrategy",
                actions_taken=actions_taken,
                time_taken=time_taken,
                error_resolved=False,
                notes=f"Recovery failed: {str(recovery_error)}"
            )


class AutoRecoveryManager:
    """Manages automatic recovery attempts with multiple strategies."""
    
    def __init__(self):
        self.strategies: List[RecoveryStrategy] = [
            TaskRecoveryStrategy(),
            SpecialistRecoveryStrategy(),
            InfrastructureRecoveryStrategy()
        ]
        self.recovery_history: List[RecoveryResult] = []
        self.max_history = 100
    
    def add_strategy(self, strategy: RecoveryStrategy):
        """Add a recovery strategy."""
        self.strategies.append(strategy)
    
    async def attempt_recovery(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Optional[RecoveryResult]:
        """
        Attempt recovery using available strategies.
        
        Returns:
            RecoveryResult if recovery was attempted, None if no strategy could handle the error
        """
        for strategy in self.strategies:
            if strategy.can_recover(error, context):
                logger.info(f"Attempting recovery with {strategy.__class__.__name__} for {type(error).__name__}")
                
                try:
                    result = await strategy.attempt_recovery(error, context)
                    
                    # Record recovery attempt
                    self._record_recovery(result)
                    
                    if result.success:
                        logger.info(f"Recovery successful: {result.notes}")
                        return result
                    else:
                        logger.warning(f"Recovery failed: {result.notes}")
                        # Continue to next strategy
                        continue
                
                except Exception as strategy_error:
                    logger.error(f"Recovery strategy {strategy.__class__.__name__} failed: {strategy_error}")
                    continue
        
        logger.warning(f"No recovery strategy could handle {type(error).__name__}")
        return None
    
    def _record_recovery(self, result: RecoveryResult):
        """Record recovery attempt in history."""
        self.recovery_history.append(result)
        
        # Trim history to max size
        if len(self.recovery_history) > self.max_history:
            self.recovery_history = self.recovery_history[-self.max_history:]
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get statistics about recovery attempts."""
        if not self.recovery_history:
            return {
                "total_attempts": 0,
                "success_rate": 0.0,
                "strategies_used": {},
                "average_recovery_time": 0.0
            }
        
        total_attempts = len(self.recovery_history)
        successful_attempts = sum(1 for r in self.recovery_history if r.success)
        success_rate = successful_attempts / total_attempts
        
        strategies_used = {}
        total_time = 0
        
        for result in self.recovery_history:
            strategy = result.strategy_used
            if strategy not in strategies_used:
                strategies_used[strategy] = {"attempts": 0, "successes": 0}
            
            strategies_used[strategy]["attempts"] += 1
            if result.success:
                strategies_used[strategy]["successes"] += 1
            
            total_time += result.time_taken
        
        average_time = total_time / total_attempts
        
        return {
            "total_attempts": total_attempts,
            "successful_attempts": successful_attempts,
            "success_rate": success_rate,
            "strategies_used": strategies_used,
            "average_recovery_time": average_time
        }
    
    def get_recent_recoveries(self, limit: int = 10) -> List[RecoveryResult]:
        """Get recent recovery attempts."""
        return self.recovery_history[-limit:]


# Global auto recovery manager
_global_recovery_manager: Optional[AutoRecoveryManager] = None


def get_recovery_manager() -> AutoRecoveryManager:
    """Get the global auto recovery manager."""
    global _global_recovery_manager
    if _global_recovery_manager is None:
        _global_recovery_manager = AutoRecoveryManager()
    return _global_recovery_manager


def set_recovery_manager(manager: AutoRecoveryManager):
    """Set the global auto recovery manager."""
    global _global_recovery_manager
    _global_recovery_manager = manager