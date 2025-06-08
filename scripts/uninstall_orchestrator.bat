@echo off
REM Comprehensive uninstall script for MCP Task Orchestrator (Windows)
REM This script removes MCP Task Orchestrator from all MCP client configurations

echo ============================================================
echo MCP Task Orchestrator - Windows Uninstall Script
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not available in PATH
    echo Please ensure Python is installed and accessible
    pause
    exit /b 1
)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%uninstall_orchestrator.py

REM Check if the Python uninstall script exists
if not exist "%PYTHON_SCRIPT%" (
    echo Error: Python uninstall script not found at:
    echo %PYTHON_SCRIPT%
    pause
    exit /b 1
)

echo Running comprehensive uninstall...
echo.

REM Run the Python uninstall script
python "%PYTHON_SCRIPT%" %*

REM Check the exit code
if errorlevel 1 (
    echo.
    echo Uninstall completed with errors. Check the log above.
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo Uninstall completed successfully!
    echo.
    echo IMPORTANT NEXT STEPS:
    echo 1. Exit Claude Code completely
    echo 2. Restart your MCP clients (Claude Desktop, Cursor, etc.)
    echo 3. Run: pip uninstall mcp-task-orchestrator
    echo.
    pause
    exit /b 0
)