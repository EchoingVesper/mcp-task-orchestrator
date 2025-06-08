#!/usr/bin/env python3
"""
Entry point module for MCP Task Orchestrator CLI.

This module provides a safe entry point that manages dependencies properly
and provides clear error messages for missing requirements.
"""

import sys


def main():
    """Safe entry point for CLI console script."""
    try:
        # Import the CLI module
        from . import cli
        
        # Run the CLI app
        cli.app()
        
    except ImportError as e:
        # Handle missing dependencies gracefully
        if "typer" in str(e):
            print("Error: CLI dependencies not installed.", file=sys.stderr)
            print("Please run: pip install mcp-task-orchestrator[cli]", file=sys.stderr)
        elif "rich" in str(e):
            print("Error: Rich formatting library not installed.", file=sys.stderr) 
            print("Please run: pip install mcp-task-orchestrator[cli]", file=sys.stderr)
        else:
            print(f"Import error: {e}", file=sys.stderr)
            print("Please run: pip install mcp-task-orchestrator", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running CLI: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()