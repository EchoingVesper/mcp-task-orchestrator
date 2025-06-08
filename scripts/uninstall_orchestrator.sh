#!/bin/bash
# Comprehensive uninstall script for MCP Task Orchestrator (Unix/Linux/macOS)
# This script removes MCP Task Orchestrator from all MCP client configurations

set -e  # Exit on any error

echo "============================================================"
echo "MCP Task Orchestrator - Unix/Linux/macOS Uninstall Script"
echo "============================================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not available in PATH"
    echo "Please ensure Python 3 is installed and accessible"
    exit 1
fi

# Determine Python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/uninstall_orchestrator.py"

# Check if the Python uninstall script exists
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: Python uninstall script not found at:"
    echo "$PYTHON_SCRIPT"
    exit 1
fi

echo "Running comprehensive uninstall..."
echo

# Run the Python uninstall script
if "$PYTHON_CMD" "$PYTHON_SCRIPT" "$@"; then
    echo
    echo "Uninstall completed successfully!"
    echo
    echo "IMPORTANT NEXT STEPS:"
    echo "1. Exit Claude Code completely"
    echo "2. Restart your MCP clients (Claude Desktop, Cursor, etc.)"
    echo "3. Run: pip uninstall mcp-task-orchestrator"
    echo "   or: pip3 uninstall mcp-task-orchestrator"
    echo
else
    echo
    echo "Uninstall completed with errors. Check the log above."
    echo
    exit 1
fi