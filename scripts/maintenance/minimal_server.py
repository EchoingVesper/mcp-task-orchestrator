#!/usr/bin/env python3
"""
Minimal MCP Task Orchestrator Server

A minimal version of the MCP Task Orchestrator server that uses only
the essential components to ensure it starts properly.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("minimal_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("minimal_server")

# Set environment variables
os.environ["MCP_TASK_ORCHESTRATOR_USE_DB"] = "true"
os.environ["MCP_TASK_ORCHESTRATOR_LOG_LEVEL"] = "DEBUG"

# Import MCP server components
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Initialize the MCP server
app = Server("task-orchestrator")

# Simple tool to test if the server is working
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    logger.info("Listing tools...")
    return [
        types.Tool(
            name="initialize_session",
            description="Initialize a new task orchestration session",
            parameters=[],
        ),
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

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> types.Content:
    """Handle tool calls."""
    logger.info(f"Tool call: {name} with arguments {arguments}")
    
    if name == "echo":
        message = arguments.get("message", "No message provided")
        logger.info(f"Echoing message: {message}")
        return types.TextContent(content=f"Echo: {message}")
    
    elif name == "initialize_session":
        logger.info("Initializing session...")
        return types.TextContent(content="Session initialized successfully!")
    
    else:
        logger.warning(f"Unknown tool: {name}")
        return types.TextContent(content=f"Unknown tool: {name}")

async def main():
    """Main entry point for the MCP server."""
    try:
        # Log server initialization
        logger.info("Starting minimal MCP Task Orchestrator server...")
        
        # Use the original implementation pattern with async context manager
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream, 
                write_stream,
                app.create_initialization_options()
            )
        
        # This line will only be reached if the server exits normally
        logger.info("Minimal MCP Task Orchestrator server shutdown gracefully")
    except Exception as e:
        logger.error(f"Error in minimal MCP Task Orchestrator server: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
