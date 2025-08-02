#!/usr/bin/env python3
"""
Entry point module for MCP Task Orchestrator server.

This module provides safe entry points that avoid import conflicts between
server.py and server/ package, and manages dependencies properly.
"""

import sys
import os


def main_sync():
    """Safe synchronous entry point for console script."""
    try:
        # Import asyncio first to ensure it's available
        import asyncio
        
        # Set working directory context for workspace detection
        # This helps with the workspace paradigm requirements
        if 'MCP_TASK_ORCHESTRATOR_WORKING_DIR' not in os.environ:
            # Set the current working directory as default
            os.environ['MCP_TASK_ORCHESTRATOR_WORKING_DIR'] = os.getcwd()
        
        # Import server module using proper package import to handle relative imports
        from . import server as server_module
        
        # Call the main function
        if hasattr(server_module, 'main'):
            asyncio.run(server_module.main())
        elif hasattr(server_module, 'main_sync'):
            # Fallback to main_sync if available
            server_module.main_sync()
        else:
            print("Error: main function not found in server module", file=sys.stderr)
            sys.exit(1)
            
    except ImportError as e:
        print(f"Import error: {e}", file=sys.stderr)
        print("This likely means required dependencies are not installed.", file=sys.stderr)
        print("Please run: pip install mcp-task-orchestrator", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


def main_async():
    """Async entry point (for direct async usage)."""
    # Import server module using proper package import
    from . import server as server_module
    
    return server_module.main()


if __name__ == "__main__":
    main_sync()