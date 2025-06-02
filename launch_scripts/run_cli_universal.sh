#!/bin/bash
# Universal launcher for MCP Task Orchestrator CLI (Unix/Linux/macOS)

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Go to project root
cd "$SCRIPT_DIR/.."

# Run the universal launcher
python3 launch_cli.py "$@" || python launch_cli.py "$@"