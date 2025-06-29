"""
Error handling infrastructure for the MCP Task Orchestrator.

This module provides centralized error handling, retry logic, and
recovery strategies for all system components.
"""

from .handlers import (
    ErrorHandler,
    ErrorHandlerRegistry,
    DefaultErrorHandler,
    TaskErrorHandler,
    SpecialistErrorHandler,
    InfrastructureErrorHandler
)

from .retry_coordinator import (
    RetryCoordinator,
    RetryPolicy,
    ExponentialBackoffPolicy,
    LinearBackoffPolicy,
    FixedDelayPolicy
)

from .logging_handlers import (
    ErrorLogger,
    StructuredErrorLogger,
    ErrorAggregator,
    ErrorMetrics
)

from .recovery_strategies import (
    RecoveryStrategy,
    AutoRecoveryManager,
    TaskRecoveryStrategy,
    SpecialistRecoveryStrategy,
    InfrastructureRecoveryStrategy
)

from .decorators import (
    handle_errors,
    with_error_context,
    suppress_errors,
    raise_on_error_response,
    ErrorContext,
    safe_call,
    safe_call_async,
    validate_input
)

__all__ = [
    # Error handlers
    'ErrorHandler',
    'ErrorHandlerRegistry',
    'DefaultErrorHandler',
    'TaskErrorHandler',
    'SpecialistErrorHandler',
    'InfrastructureErrorHandler',
    
    # Retry coordination
    'RetryCoordinator',
    'RetryPolicy',
    'ExponentialBackoffPolicy',
    'LinearBackoffPolicy',
    'FixedDelayPolicy',
    
    # Logging
    'ErrorLogger',
    'StructuredErrorLogger',
    'ErrorAggregator',
    'ErrorMetrics',
    
    # Recovery
    'RecoveryStrategy',
    'AutoRecoveryManager',
    'TaskRecoveryStrategy',
    'SpecialistRecoveryStrategy',
    'InfrastructureRecoveryStrategy',
    
    # Decorators and utilities
    'handle_errors',
    'with_error_context',
    'suppress_errors',
    'raise_on_error_response',
    'ErrorContext',
    'safe_call',
    'safe_call_async',
    'validate_input'
]