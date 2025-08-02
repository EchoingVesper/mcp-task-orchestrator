#!/usr/bin/env python3
"""
MCP Task Orchestrator Server - Clean Architecture Entry Point

A Model Context Protocol server that provides task orchestration capabilities
for AI assistants. This refactored version focuses on clean module organization
and maintainability.

File size optimized: <150 lines (previously 1407 lines)
"""

import asyncio
import os
import logging
from typing import Dict, List, Any

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Import refactored modules
from .infrastructure.mcp.tool_definitions import get_all_tools
from .infrastructure.mcp.tool_router import route_tool_call
from .infrastructure.mcp.handlers.core_handlers import (
    setup_logging,
    enable_dependency_injection,
    disable_dependency_injection
)

# Configure logging
logger = setup_logging()

# Initialize the MCP server
app = Server("task-orchestrator")


@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available orchestration tools."""
    return get_all_tools()


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls from the LLM by routing to appropriate handlers."""
    return await route_tool_call(name, arguments)


async def main():
    """Async main entry point for the MCP server."""
    try:
        # Log server initialization
        logger.info("Starting MCP Task Orchestrator server...")
        
        # Check if DI should be enabled
        enable_di = os.environ.get("MCP_TASK_ORCHESTRATOR_USE_DI", "true").lower() in ("true", "1", "yes")
        
        if enable_di:
            # Try to enable dependency injection
            try:
                await enable_dependency_injection()
                logger.info("Server running in dependency injection mode")
            except Exception as e:
                logger.error(f"Failed to enable dependency injection: {e}")
                logger.info("Falling back to legacy singleton mode")
        else:
            logger.info("Server running in legacy singleton mode")
        
        # Start the server
        logger.info("MCP Task Orchestrator server ready")
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
        # Cleanup DI resources if needed
        try:
            disable_dependency_injection()
        except Exception:
            pass  # Ignore cleanup errors during shutdown
        raise
    finally:
        logger.info("MCP Task Orchestrator server stopped")


def main_sync():
    """Synchronous entry point that calls the async main function."""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()