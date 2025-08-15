#!/bin/bash
#
# MCP Task Orchestrator Universal Installer - Unix Shell Wrapper
# 
# This script provides single-line installation capability for Unix-like systems
# (Linux, macOS, WSL). It automatically detects Python and runs the universal installer.
#
# Usage:
#   ./install.sh [options]
#   curl -fsSL https://raw.githubusercontent.com/EchoingVesper/mcp-task-orchestrator/main/install.sh | bash
#   wget -qO- https://raw.githubusercontent.com/EchoingVesper/mcp-task-orchestrator/main/install.sh | bash
#

set -euo pipefail

# Configuration
SCRIPT_NAME="install.sh"
PROJECT_NAME="MCP Task Orchestrator"
REPO_URL="https://github.com/EchoingVesper/mcp-task-orchestrator"
INSTALLER_URL="https://raw.githubusercontent.com/EchoingVesper/mcp-task-orchestrator/main/install.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Utility functions
log() { printf "${CYAN}[INFO]${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}[WARN]${NC} %s\n" "$*" >&2; }
error() { printf "${RED}[ERROR]${NC} %s\n" "$*" >&2; }
success() { printf "${GREEN}[SUCCESS]${NC} %s\n" "$*"; }

show_help() {
    cat << EOF
${PROJECT_NAME} Universal Installer

USAGE:
    ${SCRIPT_NAME} [OPTIONS]

OPTIONS:
    --dev               Developer mode installation
    --user              User-scoped installation (~/.local/bin)
    --system            System-wide installation (requires sudo)
    --clients LIST      Configure specific MCP clients (claude,cursor,vscode)
    --no-clients        Skip MCP client configuration
    --dry-run           Show what would be done without making changes
    --verbose           Enable verbose output
    --help              Show this help message

EXAMPLES:
    ${SCRIPT_NAME}                  # Standard installation with auto-detection
    ${SCRIPT_NAME} --dev            # Developer mode with editable install
    ${SCRIPT_NAME} --user           # User-scoped installation
    ${SCRIPT_NAME} --dry-run        # Preview installation without changes

SINGLE-LINE INSTALLATION:
    curl -fsSL ${REPO_URL}/install.sh | bash
    wget -qO- ${REPO_URL}/install.sh | bash

For more options and documentation, visit: ${REPO_URL}
EOF
}

detect_python() {
    local python_cmd=""
    
    # Try different Python commands in order of preference
    for cmd in python3.12 python3.11 python3.10 python3.9 python3.8 python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            # Check if this Python version is compatible (3.8+)
            if "$cmd" -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
                python_cmd="$cmd"
                break
            fi
        fi
    done
    
    if [[ -z "$python_cmd" ]]; then
        error "No compatible Python interpreter found."
        error "Python 3.8 or higher is required."
        error "Please install Python and try again."
        exit 1
    fi
    
    local python_version
    python_version=$("$python_cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    log "Using Python $python_version at $(command -v "$python_cmd")"
    
    echo "$python_cmd"
}

download_installer() {
    local installer_path="$1"
    
    log "Downloading universal installer..."
    
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$INSTALLER_URL" -o "$installer_path"
    elif command -v wget >/dev/null 2>&1; then
        wget -q "$INSTALLER_URL" -O "$installer_path"
    else
        error "Neither curl nor wget found. Please install one of them."
        exit 1
    fi
    
    if [[ ! -f "$installer_path" ]]; then
        error "Failed to download installer from $INSTALLER_URL"
        exit 1
    fi
    
    success "Downloaded installer successfully"
}

check_requirements() {
    # Check for required tools
    local missing_tools=()
    
    # Git is helpful but not required
    if ! command -v git >/dev/null 2>&1; then
        warn "Git not found. Some features may be limited."
    fi
    
    # Check for package managers (at least one should be available)
    if ! command -v pip >/dev/null 2>&1 && ! command -v pip3 >/dev/null 2>&1; then
        missing_tools+=("pip")
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        error "Missing required tools: ${missing_tools[*]}"
        error "Please install these tools and try again."
        exit 1
    fi
    
    # Check for WSL environment
    if grep -qi microsoft /proc/version 2>/dev/null; then
        log "Detected WSL environment"
    fi
    
    # Check for macOS
    if [[ "$(uname)" == "Darwin" ]]; then
        log "Detected macOS environment"
        
        # Check for Homebrew
        if command -v brew >/dev/null 2>&1; then
            log "Homebrew detected"
        fi
    fi
}

run_installer() {
    local python_cmd="$1"
    local installer_path="$2"
    shift 2
    local args=("$@")
    
    log "Running ${PROJECT_NAME} installer..."
    
    # Execute the installer with all provided arguments
    "$python_cmd" "$installer_path" "${args[@]}"
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        success "Installation completed successfully!"
    else
        error "Installation failed with exit code $exit_code"
        exit $exit_code
    fi
}

cleanup() {
    local installer_path="$1"
    
    # Clean up downloaded installer if it was downloaded
    if [[ -f "$installer_path" && "$installer_path" == "/tmp/install.py" ]]; then
        rm -f "$installer_path"
    fi
}

main() {
    local args=()
    local need_download=false
    local installer_path=""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                args+=("$1")
                ;;
        esac
        shift
    done
    
    # Show banner
    printf "${BLUE}================================${NC}\n"
    printf "${BLUE} %s${NC}\n" "${PROJECT_NAME}"
    printf "${BLUE} Universal Installer${NC}\n"
    printf "${BLUE}================================${NC}\n"
    printf "\n"
    
    # Check if we're in the project directory
    if [[ -f "./install.py" && -f "./pyproject.toml" ]]; then
        log "Using local installer from project directory"
        installer_path="./install.py"
    else
        log "Downloading installer from repository"
        installer_path="/tmp/install.py"
        need_download=true
    fi
    
    # Set up trap for cleanup
    trap 'cleanup "$installer_path"' EXIT
    
    # Perform pre-installation checks
    check_requirements
    
    # Detect Python
    local python_cmd
    python_cmd=$(detect_python)
    
    # Download installer if needed
    if [[ "$need_download" == "true" ]]; then
        download_installer "$installer_path"
    fi
    
    # Run the installer
    run_installer "$python_cmd" "$installer_path" "${args[@]}"
    
    echo
    success "Installation process completed!"
    log "For more information, visit: $REPO_URL"
}

# Only run main if script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi