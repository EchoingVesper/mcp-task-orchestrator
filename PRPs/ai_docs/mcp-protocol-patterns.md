
# MCP Protocol Development Patterns

**Purpose**: Essential patterns for developing Model Context Protocol servers with Python/async, focusing on security, reliability, and protocol compliance.

#
# Core Principles

#
## CRITICAL MCP Protocol Requirements

- **NEVER write to stdout in MCP servers** - stdout is reserved for JSON-RPC protocol communication

- **Always use stderr for logging** in MCP mode to avoid protocol violations

- **Implement proper JSON-RPC 2.0 error responses** - clients expect standard error formats

- **Use async/await consistently** throughout the server implementation

- **Proper resource cleanup** is essential to prevent connection leaks and warnings

#
# Server Initialization Patterns

#
## Pattern: MCP Server Setup with Clean Architecture

```python

# PATTERN: Clean server initialization with proper separation of concerns

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Infrastructure imports

from .infrastructure.mcp.tool_definitions import get_all_tools
from .infrastructure.mcp.tool_router import route_tool_call
from .infrastructure.mcp.handlers.core_handlers import setup_logging

# Initialize server

app = Server("task-orchestrator")

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available orchestration tools."""
    return get_all_tools()

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls by routing to appropriate handlers."""
    return await route_tool_call(name, arguments)

```text

#
## Pattern: MCP-Compliant Logging Setup

```text
python

# PATTERN: Logging configuration that respects MCP protocol

def setup_logging():
    """Set up logging configuration for MCP server."""
    import sys
    import logging
    
    
# CRITICAL: Detect if running as MCP server
    is_mcp_server = not sys.stdin.isatty()
    
    if is_mcp_server:
        
# MCP mode: Use stderr and reduce noise
        handler = logging.StreamHandler(sys.stderr)  
# CRITICAL: stderr not stdout
        level = logging.WARNING  
# Reduce noise for MCP clients
    else:
        
# CLI mode: Use stdout for user visibility
        handler = logging.StreamHandler(sys.stdout)
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[handler]
    )
    
    return logging.getLogger("mcp_task_orchestrator")

```text

#
# Error Handling Patterns

#
## Pattern: MCP-Compliant Error Responses

```text
python

# PATTERN: Standard MCP error handling with proper JSON-RPC 2.0 responses

from mcp import types

class McpError(Exception):
    """Base exception for MCP protocol errors."""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

async def safe_tool_handler(tool_name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Safe tool handler with proper error conversion."""
    try:
        
# Your business logic here
        result = await handle_business_logic(arguments)
        return [types.TextContent(type="text", text=json.dumps(result))]
        
    except ValidationError as e:
        
# PATTERN: Convert domain errors to MCP errors
        raise McpError(-32602, f"Invalid parameters: {e}")
        
    except DatabaseError as e:
        
# PATTERN: Don't leak internal details
        logger.error(f"Database error in {tool_name}: {e}")
        raise McpError(-32603, "Internal server error")
        
    except Exception as e:
        
# PATTERN: Catch-all with logging
        logger.exception(f"Unexpected error in {tool_name}")
        raise McpError(-32603, "Internal server error")

```text

#
## Pattern: Async Context Management

```text
python

# PATTERN: Proper async context management for resources

from contextlib import asynccontextmanager

@asynccontextmanager
async def get_database_connection():
    """Async context manager for database connections."""
    conn = None
    try:
        conn = await get_connection_from_pool()
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            await conn.close()

async def database_operation(data: dict) -> dict:
    """PATTERN: Safe database operations with proper cleanup."""
    try:
        async with get_database_connection() as conn:
            result = await conn.execute(query, params)
            return {"success": True, "data": result}
            
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise McpError(-32603, "Database operation failed")

```text

#
# Tool Registration Patterns

#
## Pattern: Modular Tool Definitions

```text
python

# PATTERN: Organize tools by functional area

from mcp import types

def get_orchestration_tools() -> List[types.Tool]:
    """Get task orchestration tools."""
    return [
        types.Tool(
            name="orchestrator_initialize_session",
            description="Initialize a new task orchestration session",
            inputSchema={
                "type": "object",
                "properties": {
                    "working_directory": {
                        "type": "string",
                        "description": "Path where .task_orchestrator should be created"
                    }
                }
            }
        ),
        
# ... more tools
    ]

def get_all_tools() -> List[types.Tool]:
    """Aggregate all available tools."""
    tools = []
    tools.extend(get_orchestration_tools())
    tools.extend(get_database_tools())
    tools.extend(get_maintenance_tools())
    return tools

```text

#
## Pattern: Tool Routing with Type Safety

```text
python

# PATTERN: Type-safe tool routing with validation

from typing import Dict, Callable, Awaitable

TOOL_HANDLERS: Dict[str, Callable[[Dict[str, Any]], Awaitable[List[types.TextContent]]]] = {
    "orchestrator_initialize_session": handle_initialize_session,
    "orchestrator_plan_task": handle_plan_task,
    "orchestrator_execute_task": handle_execute_task,
    
# ... more handlers
}

async def route_tool_call(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Route tool calls to appropriate handlers with validation."""
    if name not in TOOL_HANDLERS:
        raise McpError(-32601, f"Unknown tool: {name}")
    
    handler = TOOL_HANDLERS[name]
    
    try:
        return await handler(arguments)
    except McpError:
        
# Re-raise MCP errors as-is
        raise
    except Exception as e:
        logger.exception(f"Handler error for {name}")
        raise McpError(-32603, "Tool execution failed")

```text

#
# Dependency Injection Patterns

#
## Pattern: DI Container Integration

```text
python

# PATTERN: Dependency injection for testability and modularity

async def main():
    """Server startup with dependency injection."""
    try:
        
# Check if DI should be enabled
        enable_di = os.environ.get("MCP_TASK_ORCHESTRATOR_USE_DI", "true").lower() in ("true", "1", "yes")
        
        if enable_di:
            try:
                await enable_dependency_injection()
                logger.info("Server running in dependency injection mode")
            except Exception as e:
                logger.error(f"Failed to enable dependency injection: {e}")
                logger.info("Falling back to legacy singleton mode")
        
        
# Start the server
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream, 
                write_stream, 
                app.create_initialization_options()
            )
            
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        
# Cleanup DI resources
        try:
            disable_dependency_injection()
        except Exception:
            pass  
# Ignore cleanup errors during shutdown
        raise

```text

#
# Validation Patterns

#
## Pattern: Input Validation with Pydantic

```text
python

# PATTERN: Strong input validation for MCP tools

from pydantic import BaseModel, Field, validator
from typing import Optional

class TaskCreationRequest(BaseModel):
    """Validated request for creating tasks."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., max_length=2000)
    priority: str = Field("medium", regex="^(low|medium|high)$")
    due_date: Optional[str] = Field(None, regex=r"^\d{4}-\d{2}-\d{2}$")
    
    @validator('title')
    def validate_title(cls, v):
        
# SECURITY: Basic XSS prevention
        if any(char in v.lower() for char in ['<script>', '<iframe>', 'javascript:']):
            raise ValueError('Invalid characters in title')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        
# SECURITY: Prevent excessively long descriptions
        if len(v.strip()) == 0:
            raise ValueError('Description cannot be empty')
        return v.strip()

async def handle_create_task(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle task creation with validation."""
    try:
        
# PATTERN: Validate input first
        request = TaskCreationRequest(**arguments)
        
        
# Process the validated request
        result = await create_task_use_case(request)
        
        return [types.TextContent(
            type="text", 
            text=json.dumps({"success": True, "task_id": result.task_id})
        )]
        
    except ValidationError as e:
        raise McpError(-32602, f"Validation failed: {e}")

```text

#
# Performance Patterns

#
## Pattern: Resource Management

```text
python

# PATTERN: Proper resource lifecycle management

class ResourceManager:
    """Manages server resources with proper cleanup."""
    
    def __init__(self):
        self._connection_pool = None
        self._cache = {}
    
    async def initialize(self):
        """Initialize resources."""
        self._connection_pool = await create_connection_pool()
        logger.info("Resource manager initialized")
    
    async def cleanup(self):
        """Clean up resources."""
        if self._connection_pool:
            await self._connection_pool.close()
        self._cache.clear()
        logger.info("Resource manager cleaned up")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection with automatic cleanup."""
        if not self._connection_pool:
            raise RuntimeError("Resource manager not initialized")
        
        conn = await self._connection_pool.acquire()
        try:
            yield conn
        finally:
            await self._connection_pool.release(conn)

```text

#
# Security Patterns

#
## Pattern: Secure Error Handling

```text
python

# PATTERN: Security-conscious error responses

def sanitize_error_for_client(error: Exception, tool_name: str) -> str:
    """Sanitize error messages for client consumption."""
    
    
# SECURITY: Don't leak internal paths or sensitive information
    if isinstance(error, FileNotFoundError):
        return "Required resource not found"
    elif isinstance(error, PermissionError):
        return "Access denied"
    elif isinstance(error, DatabaseError):
        
# Log full error internally
        logger.error(f"Database error in {tool_name}: {error}")
        return "Database operation failed"
    else:
        
# Generic fallback
        logger.error(f"Unexpected error in {tool_name}: {error}")
        return "Internal server error"

async def secure_tool_handler(tool_name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Tool handler with security-conscious error handling."""
    try:
        result = await process_tool_request(arguments)
        return [types.TextContent(type="text", text=json.dumps(result))]
        
    except Exception as e:
        sanitized_message = sanitize_error_for_client(e, tool_name)
        raise McpError(-32603, sanitized_message)

```text

#
# Testing Patterns

#
## Pattern: MCP Tool Testing

```text
python

# PATTERN: Integration testing for MCP tools

import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_tool_handler_success():
    """Test successful tool execution."""
    arguments = {"title": "Test Task", "description": "Test Description"}
    
    with patch('your_module.create_task_use_case') as mock_use_case:
        mock_use_case.return_value = AsyncMock(task_id="test-123")
        
        result = await handle_create_task(arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        response = json.loads(result[0].text)
        assert response["success"] is True
        assert response["task_id"] == "test-123"

@pytest.mark.asyncio
async def test_tool_handler_validation_error():
    """Test validation error handling."""
    arguments = {"title": "", "description": "Valid description"}  
# Invalid: empty title
    
    with pytest.raises(McpError) as exc_info:
        await handle_create_task(arguments)
    
    assert exc_info.value.code == -32602
    assert "Validation failed" in exc_info.value.message

```text

#
# Common Gotchas

#
## MCP Protocol Violations

```text
python

# ❌ WRONG: Writing to stdout breaks MCP protocol

print("Debug message")  
# This will break MCP communication

# ✅ CORRECT: Use logging to stderr

logger.info("Debug message")

# ❌ WRONG: Inconsistent async/await usage

def sync_handler(args):  
# Should be async
    return process_sync(args)

# ✅ CORRECT: Consistent async patterns

async def async_handler(args):
    return await process_async(args)

# ❌ WRONG: Leaking internal errors to client

raise Exception("Database connection failed: postgresql://user:pass@host")

# ✅ CORRECT: Sanitized error responses

raise McpError(-32603, "Database operation failed")

```text

#
## Resource Management Issues

```text
python

# ❌ WRONG: Not cleaning up resources

async def bad_database_operation():
    conn = await get_connection()
    result = await conn.execute(query)
    
# Missing: await conn.close()
    return result

# ✅ CORRECT: Always use context managers

async def good_database_operation():
    async with get_connection() as conn:
        result = await conn.execute(query)
        return result  
# Connection automatically closed

```text

#
# Integration with Clean Architecture

#
## Pattern: Use Case Integration

```text
python

# PATTERN: MCP handlers as thin adapters to use cases

from ...application.usecases.task_management import CreateTaskUseCase
from ...domain.entities.task import Task

async def handle_create_task(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """MCP handler that delegates to use case."""
    
    
# PATTERN: Validate at the boundary
    request = TaskCreationRequest(**arguments)
    
    
# PATTERN: Delegate to use case
    use_case = CreateTaskUseCase()
    task = await use_case.execute(request)
    
    
# PATTERN: Format response for MCP
    response = {
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "status": task.status.value
        }
    }
    
    return [types.TextContent(type="text", text=json.dumps(response))]
```text

#
# Best Practices Summary

1. **Protocol Compliance**: Always respect MCP protocol requirements (stderr logging, JSON-RPC errors)

2. **Async Consistency**: Use async/await throughout the server implementation

3. **Resource Management**: Always use context managers for resource cleanup

4. **Input Validation**: Validate all inputs at the MCP boundary with Pydantic

5. **Error Handling**: Convert domain errors to proper MCP error codes

6. **Security**: Sanitize error messages and validate inputs

7. **Testing**: Write integration tests for all MCP tools

8. **Clean Architecture**: Keep MCP handlers as thin adapters to use cases

#
# Related Documentation

- [Database Integration Patterns](./database-integration-patterns.md)

- [Security Patterns](./security-patterns.md)

- [Context Engineering Guide](./context-engineering-guide.md)

- [Clean Architecture Guide](../../docs/developers/architecture/clean-architecture-guide.md)
