
# Async Patterns

**Purpose**: Common async/await patterns for Python development in the MCP Task Orchestrator, focusing on clean, reliable, and performant asynchronous code.

#
# Core Async Patterns

#
## Pattern: Async Context Managers

```python

# PATTERN: Database connection with async context manager

from contextlib import asynccontextmanager

@asynccontextmanager
async def get_database_connection():
    """Async context manager for database connections."""
    conn = None
    try:
        conn = await create_connection()
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            await conn.close()

# Usage

async def database_operation():
    async with get_database_connection() as conn:
        result = await conn.execute(query)
        return result

```text

#
## Pattern: Async Error Handling

```text
python

# PATTERN: Comprehensive async error handling

async def safe_async_operation(operation_func, *args, **kwargs):
    """Execute async operation with comprehensive error handling."""
    try:
        return await operation_func(*args, **kwargs)
    except asyncio.TimeoutError:
        logger.error("Operation timed out")
        raise McpError(-32603, "Operation timed out")
    except asyncio.CancelledError:
        logger.info("Operation was cancelled")
        raise
    except Exception as e:
        logger.exception(f"Async operation failed: {e}")
        raise McpError(-32603, "Internal server error")

```text

#
## Pattern: Async Resource Management

```text
python

# PATTERN: Async resource pool management

class AsyncResourcePool:
    """Manages a pool of async resources."""
    
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.pool = []
        self.semaphore = asyncio.Semaphore(max_size)
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire resource from pool."""
        async with self.semaphore:
            if self.pool:
                resource = self.pool.pop()
            else:
                resource = await self.create_resource()
            
            try:
                yield resource
            finally:
                if await self.is_resource_healthy(resource):
                    self.pool.append(resource)
                else:
                    await self.destroy_resource(resource)
```text

#
# Related Documentation

- [MCP Protocol Patterns](../ai_docs/mcp-protocol-patterns.md)

- [Database Integration Patterns](../ai_docs/database-integration-patterns.md)

- [Security Patterns](../ai_docs/security-patterns.md)
