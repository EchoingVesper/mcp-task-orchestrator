#!/usr/bin/env python3
"""
Entry point for MCP Task Orchestrator server when run as a module.
"""

import sys
import asyncio
from pathlib import Path

def main():
    """Main entry point for the server module."""
    try:
        # Import the server module properly
        from mcp_task_orchestrator.server import main_sync
        
        # Run the server using the sync wrapper
        main_sync()
        
    except ImportError as e:
        print(f"Error importing server module: {e}", file=sys.stderr)
        print("Make sure the mcp-task-orchestrator package is properly installed.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()