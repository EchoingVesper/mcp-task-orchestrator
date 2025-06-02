# MCP Task Orchestrator - Windows Installation Script
# This script installs and configures the MCP Task Orchestrator for Windows

# Ensure we're running as admin
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run this script as Administrator!"
    exit 1
}

# Script variables
$ErrorActionPreference = "Stop"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Item $ScriptPath).Parent.FullName
$PythonCmd = "python"

# Display welcome message
Write-Host "MCP Task Orchestrator - Windows Installation" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "This script will install and configure the MCP Task Orchestrator server."
Write-Host "Project root: $ProjectRoot"
Write-Host ""

# Check Python installation
try {
    $PythonVersion = & $PythonCmd --version
    Write-Host "Found $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found! Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Install the package
Write-Host "Installing MCP Task Orchestrator package..." -ForegroundColor Yellow
try {
    & $PythonCmd -m pip install -e "$ProjectRoot"
    Write-Host "Package installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to install package: $_" -ForegroundColor Red
    exit 1
}

# Run the CLI installer
Write-Host "Configuring MCP clients..." -ForegroundColor Yellow
try {
    & $PythonCmd -m mcp_task_orchestrator_cli.cli install "$ProjectRoot\mcp_task_orchestrator\server.py" --name "Task Orchestrator"
    if ($LASTEXITCODE -ne 0) {
        throw "CLI installer returned exit code $LASTEXITCODE"
    }
    Write-Host "Configuration completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Configuration failed: $_" -ForegroundColor Red
    Write-Host "You may need to manually configure your MCP clients." -ForegroundColor Yellow
}

# Installation complete
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "MCP Task Orchestrator installation complete!" -ForegroundColor Green
Write-Host "You can now use the Task Orchestrator in your MCP-compatible clients."
Write-Host "To update your configuration in the future, run:"
Write-Host "mcp-task-orchestrator-cli update <server_path>"
Write-Host ""
Write-Host "Thank you for installing MCP Task Orchestrator!" -ForegroundColor Green