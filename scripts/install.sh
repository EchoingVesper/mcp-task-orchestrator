#!/bin/bash
# MCP Task Orchestrator - Unix Installation Script
# This script installs and configures the MCP Task Orchestrator for macOS and Linux

# Exit on error
set -e

# Script variables
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_CMD="python3"

# Display welcome message
echo -e "\033[0;32mMCP Task Orchestrator - Unix Installation\033[0m"
echo -e "\033[0;32m================================================\033[0m"
echo "This script will install and configure the MCP Task Orchestrator server."
echo "Project root: $PROJECT_ROOT"
echo ""

# Check Python installation
if command -v $PYTHON_CMD >/dev/null 2>&1; then
    PYTHON_VERSION=$($PYTHON_CMD --version)
    echo -e "\033[0;32mFound $PYTHON_VERSION\033[0m"
else
    echo -e "\033[0;31mPython 3 not found! Please install Python 3.8 or higher.\033[0m"
    exit 1
fi

# Install the package
echo -e "\033[0;33mInstalling MCP Task Orchestrator package...\033[0m"
$PYTHON_CMD -m pip install -e "$PROJECT_ROOT" || {
    echo -e "\033[0;31mFailed to install package\033[0m"
    exit 1
}
echo -e "\033[0;32mPackage installed successfully!\033[0m"

# Run the CLI installer
echo -e "\033[0;33mConfiguring MCP clients...\033[0m"
$PYTHON_CMD -m mcp_task_orchestrator_cli.cli install "$PROJECT_ROOT/mcp_task_orchestrator/server.py" --name "Task Orchestrator" || {
    echo -e "\033[0;31mConfiguration failed\033[0m"
    echo -e "\033[0;33mYou may need to manually configure your MCP clients.\033[0m"
}
echo -e "\033[0;32mConfiguration completed successfully!\033[0m"

# Installation complete
echo ""
echo -e "\033[0;32m================================================\033[0m"
echo -e "\033[0;32mMCP Task Orchestrator installation complete!\033[0m"
echo "You can now use the Task Orchestrator in your MCP-compatible clients."
echo "To update your configuration in the future, run:"
echo "mcp-task-orchestrator-cli update <server_path>"
echo ""
echo -e "\033[0;32mThank you for installing MCP Task Orchestrator!\033[0m"