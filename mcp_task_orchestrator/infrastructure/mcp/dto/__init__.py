"""
MCP Protocol Data Transfer Objects (DTOs).

This module contains Pydantic models for type-safe request/response handling
in the MCP protocol layer. These DTOs ensure proper validation and serialization
between the MCP protocol and the application layer.
"""

from .task_dtos import (
    # Task creation/planning
    CreateTaskRequest,
    CreateTaskResponse,
    
    # Task updates
    UpdateTaskRequest,
    UpdateTaskResponse,
    
    # Task deletion
    DeleteTaskRequest,
    DeleteTaskResponse,
    
    # Task cancellation
    CancelTaskRequest,
    CancelTaskResponse,
    
    # Task queries
    QueryTasksRequest,
    QueryTasksResponse,
    TaskQueryResult,
    
    # Task execution
    ExecuteTaskRequest,
    ExecuteTaskResponse,
    
    # Task completion
    CompleteTaskRequest,
    CompleteTaskResponse,
    
    # Status checking
    GetStatusRequest,
    GetStatusResponse,
    StatusSummary,
    
    # Common response components
    ErrorDetail,
    NextStep,
    MCPErrorResponse
)

__all__ = [
    # Task operations
    "CreateTaskRequest",
    "CreateTaskResponse",
    "UpdateTaskRequest", 
    "UpdateTaskResponse",
    "DeleteTaskRequest",
    "DeleteTaskResponse",
    "CancelTaskRequest",
    "CancelTaskResponse",
    "QueryTasksRequest",
    "QueryTasksResponse",
    "TaskQueryResult",
    "ExecuteTaskRequest",
    "ExecuteTaskResponse",
    "CompleteTaskRequest",
    "CompleteTaskResponse",
    
    # Status operations
    "GetStatusRequest",
    "GetStatusResponse",
    "StatusSummary",
    
    # Common components
    "ErrorDetail",
    "NextStep",
    "MCPErrorResponse"
]