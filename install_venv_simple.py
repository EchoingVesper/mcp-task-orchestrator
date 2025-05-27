#!/usr/bin/env python3
"""
MCP Task Orchestrator - Simple Virtual Environment Installer
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step, message):
    print(f"\n[{step}] {message}")

def main():
    project_dir = Path(__file__).parent.absolute()
    venv_path = project_dir / "venv_mcp"
    scripts_path = project_dir / "launch_scripts"
    
    print_header("MCP Task Orchestrator - Virtual Environment Installation")
    print("✅ Simple, reliable, and isolated!")
    
    # Clean up existing
    for path in [venv_path, scripts_path]:
        if path.exists():
            print_step("CLEANUP", f"Removing {path.name}...")
            shutil.rmtree(path)
    
    # Create virtual environment
    print_step("VENV", "Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], 
                      check=True, capture_output=True, text=True)
        print("[OK] Virtual environment created")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed: {e.stderr}")
        return 1
    
    # Get venv Python
    python_exe = venv_path / ("Scripts/python.exe" if os.name == 'nt' else "bin/python")

    # Upgrade pip and install dependencies
    print_step("PACKAGES", "Installing dependencies...")
    try:
        # Upgrade pip
        subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True, text=True)
        
        # Install requirements
        subprocess.run([str(python_exe), "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True, cwd=str(project_dir))
        
        # Install project
        subprocess.run([str(python_exe), "-m", "pip", "install", "-e", "."], 
                      check=True, capture_output=True, text=True, cwd=str(project_dir))
        
        print("[OK] All packages installed")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Package installation failed: {e.stderr}")
        return 1
    
    # Test installation
    print_step("TEST", "Testing installation...")
    try:
        result = subprocess.run([str(python_exe), "-c", "import mcp_task_orchestrator; print('Import OK')"], 
                               check=True, capture_output=True, text=True)
        print("[OK] Package import successful")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Import test failed: {e.stderr}")
        return 1
    
    # Create launch scripts
    print_step("SCRIPTS", "Creating launch scripts...")
    scripts_path.mkdir(exist_ok=True)
    
    # Server script
    server_script = scripts_path / "run_server.bat"
    server_script.write_text(f'''@echo off
cd /D "{project_dir}"
"{python_exe}" -m mcp_task_orchestrator.server
''')
    
    # CLI script
    cli_script = scripts_path / "run_cli.bat"
    cli_script.write_text(f'''@echo off
cd /D "{project_dir}"
"{python_exe}" -m mcp_task_orchestrator_cli.cli %*
''')

    # Create Claude configuration
    claude_config = {
        "mcpServers": {
            "task-orchestrator": {
                "command": str(python_exe),
                "args": ["-m", "mcp_task_orchestrator.server"],
                "cwd": str(project_dir)
            }
        }
    }
    
    config_file = scripts_path / "claude_config.json"
    with open(config_file, 'w') as f:
        json.dump(claude_config, f, indent=2)
    
    print("[OK] Launch scripts and config created")
    
    # Success message
    print_header("Installation Complete!")
    print(f"""
🎉 MCP Task Orchestrator installed successfully!

📁 Installation Details:
   • Virtual Environment: {venv_path}
   • Python: {python_exe}
   • Launch Scripts: {scripts_path}

🚀 Next Steps:
   1. Add this to your Claude Desktop config:
      {json.dumps(claude_config, indent=6)}
   
   2. Restart Claude Desktop

🔧 Manual Usage:
   • Run server: {scripts_path}/run_server.bat
   • Run CLI: {scripts_path}/run_cli.bat

✅ Much simpler and more reliable than embedded Python!
""")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[CANCELLED] Installation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
