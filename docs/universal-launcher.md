# Universal Launcher for MCP Task Orchestrator

The MCP Task Orchestrator now includes universal launcher scripts that automatically detect and use the appropriate virtual environment, regardless of the operating system.

## Features

- **Cross-platform support**: Works on Windows, Linux, macOS, and WSL
- **Automatic venv detection**: Finds and uses the virtual environment automatically
- **No manual activation needed**: The launcher handles venv activation internally
- **Multiple venv name support**: Detects `venv_mcp`, `venv`, or `.venv`
- **Intelligent fallbacks**: Uses system Python if venv is not found

## Usage

### Starting the Server

From the project root directory:

```bash
# On Unix/Linux/macOS/WSL
python3 launch_orchestrator.py

# On Windows
python launch_orchestrator.py

# Or use the platform-specific scripts
./launch_scripts/run_server_universal.sh  # Unix/Linux/macOS
launch_scripts\run_server_universal.bat   # Windows
```

### Using the CLI

```bash
# On Unix/Linux/macOS/WSL
python3 launch_cli.py [arguments]

# On Windows
python launch_cli.py [arguments]

# Or use the platform-specific scripts
./launch_scripts/run_cli_universal.sh [arguments]  # Unix/Linux/macOS
launch_scripts\run_cli_universal.bat [arguments]   # Windows
```

## How It Works

1. The launcher scripts (`launch_orchestrator.py` and `launch_cli.py`) automatically detect your operating system
2. They search for the virtual environment in common locations (`venv_mcp`, `venv`, `.venv`)
3. They detect whether the venv uses Windows-style `Scripts/` or Unix-style `bin/` directories
4. They launch the appropriate Python executable from the venv with the correct module

## Installation Integration

The installer (`run_installer.py`) now automatically configures MCP clients to use the universal launcher, ensuring that:

- Claude Desktop, Cursor, VS Code, and other MCP clients will use the correct Python environment
- The configuration works regardless of whether the venv was created on Windows or Unix
- Users don't need to manually activate the virtual environment

## Benefits

- **Simplified usage**: No need to remember venv activation commands
- **Consistent behavior**: Same commands work across all platforms
- **Better integration**: MCP clients automatically use the correct environment
- **Reduced errors**: Eliminates common venv-related issues

## Troubleshooting

If the launcher can't find your virtual environment:

1. Ensure you've run the installer: `python run_installer.py`
2. Check that one of these directories exists: `venv_mcp`, `venv`, or `.venv`
3. Verify the virtual environment contains the required packages

If you're using a custom virtual environment name, you can:
- Create a symlink to one of the expected names
- Modify the launcher scripts to include your custom name
- Use the direct Python command with manual venv activation