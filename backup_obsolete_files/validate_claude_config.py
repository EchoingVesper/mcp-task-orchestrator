#!/usr/bin/env python3
"""
Claude Desktop MCP Configuration Validator
"""
import json
import os
import subprocess
import sys
from pathlib import Path

def find_claude_config():
    """Find the Claude Desktop configuration file"""
    possible_paths = [
        os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json"),  # Windows
        os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json"),  # macOS
        os.path.expanduser("~/.config/Claude/claude_desktop_config.json"),  # Linux
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def validate_server_execution():
    """Test if the server can run standalone"""
    print("Testing server execution...")
    server_path = Path(__file__).parent / "src" / "main.py"
    
    try:
        # Test server startup (timeout after 3 seconds)
        process = subprocess.Popen([
            sys.executable, str(server_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
           cwd=Path(__file__).parent)
        
        try:
            stdout, stderr = process.communicate(timeout=3)
            print("❌ Server exited unexpectedly")
            if stderr:
                print(f"Error: {stderr.decode()}")
            return False
        except subprocess.TimeoutExpired:
            process.kill()
            print("✅ Server starts and runs correctly")
            return True
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def validate_config_file(config_path):
    """Validate Claude Desktop config file"""
    print(f"Validating config: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "mcpServers" not in config:
            print("❌ Missing 'mcpServers' key in config")
            return False
            
        if "task-orchestrator" not in config["mcpServers"]:
            print("❌ Missing 'task-orchestrator' server in config")
            return False
            
        server_config = config["mcpServers"]["task-orchestrator"]
        
        # Check required fields
        if "command" not in server_config:
            print("❌ Missing 'command' in server config")
            return False
            
        if "args" not in server_config:
            print("❌ Missing 'args' in server config")
            return False
            
        # Check if main.py exists
        main_py_path = server_config["args"][0] if server_config["args"] else ""
        if not os.path.exists(main_py_path):
            print(f"❌ Server script not found: {main_py_path}")
            return False
            
        print("✅ Configuration appears valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def main():
    print("Claude Desktop MCP Configuration Validator")
    print("=" * 50)
    
    # Test 1: Validate server execution
    server_ok = validate_server_execution()
    
    # Test 2: Find and validate config
    config_path = find_claude_config()
    config_ok = False
    
    if config_path:
        print(f"Found Claude config: {config_path}")
        config_ok = validate_config_file(config_path)
    else:
        print("❌ Could not find Claude Desktop config file")
        print("Expected locations:")
        print("  Windows: ~/AppData/Roaming/Claude/claude_desktop_config.json")
        print("  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
        print("  Linux: ~/.config/Claude/claude_desktop_config.json")
    
    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY:")
    print(f"Server execution: {'✅ PASS' if server_ok else '❌ FAIL'}")
    print(f"Config validation: {'✅ PASS' if config_ok else '❌ FAIL'}")
    
    if server_ok and config_ok:
        print("🎉 Everything looks good! Try restarting Claude Desktop.")
    elif server_ok:
        print("💡 Server works. Check Claude Desktop configuration.")
        print("📋 Copy one of the config files in this directory to your Claude config.")
    else:
        print("🔧 Server has issues. Check the error messages above.")
    
    return server_ok and config_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
