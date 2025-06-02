#!/usr/bin/env python3
"""
Simplified MCP Task Orchestrator Server

A simplified version of the MCP Task Orchestrator server that uses only
the essential components to help diagnose initialization issues.
"""

import asyncio
import logging
import os
from pathlib import Path

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("simple_server")

# Initialize the MCP server
app = Server("simple-task-orchestrator")

# Simple tool to test if the server is working
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="echo",
            description="Echo back the input",
            parameters=[
                types.Parameter(
                    name="message",
                    description="Message to echo",
                    type=types.ParameterType.STRING,
                    required=True,
                )
            ],
        )
    ]

@app.call_tool("echo")
async def echo(message: str) -> types.TextContent:
    """Echo back the input."""
    logger.info(f"Echoing message: {message}")
    return types.TextContent(content=f"Echo: {message}")

async def main():
    """Main entry point for the MCP server."""
    try:
        # Log server initialization
        logger.info("Starting simple MCP Task Orchestrator server...")
        
        # Use the original implementation pattern with async context manager
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream, 
                write_stream,
                app.create_initialization_options()
            )
        
        # This line will only be reached if the server exits normally
        logger.info("Simple MCP Task Orchestrator server shutdown gracefully")
    except Exception as e:
        logger.error(f"Error in simple MCP Task Orchestrator server: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
