# MCP Task Orchestrator - Troubleshooting Guide

*Quick solutions to common issues*

## 🔍 Quick Diagnosis

**Start here**: Try these in order before diving into specific errors:

1. **Restart your MCP client completely** (fixes 70% of issues)
2. **Check the basics**: Python 3.8+, Node.js 16+, supported MCP client installed
3. **Run diagnostics**: `python scripts/diagnostics/verify_tools.py`

## 🚨 Common Error Messages

### "Could not connect to MCP server" / "Claude was unable to connect"

**Most Common Cause**: Client needs restart after configuration changes

**Solutions**:
1. **Restart your MCP client completely** (not just reload)
2. Verify configuration file exists and has correct syntax:
   - **Claude Desktop**: Check `claude_desktop_config.json` file
   - **Cursor**: Check `.cursor/mcp.json` file  
3. Use absolute paths (not relative) in configuration
4. Check logs for specific error details

### ImportError: "attempted relative import with no known parent package"

**Cause**: Using deprecated installation method

**Solution**:
1. Use the optimized installer: `python run_installer.py`
2. For legacy compatibility: `python install.py` (redirects to optimized method)
3. See [Migration Guide](MIGRATION_GUIDE.md) for complete transition guidance

### Installation Method Issues ⚠️ RESOLVED

**Previous Issue**: "'SpecialistManager' object has no attribute 'project_dir'"

**Status**: ✅ **RESOLVED** - This error has been fixed in the current version

**Solution**: Use the recommended installation method:
```bash
python run_installer.py
```

If you encounter this error, you may be using an outdated installation method or have cached files. Try:
1. Use `python run_installer.py` instead of deprecated methods
2. Restart your MCP client completely
3. If persistent, delete and recreate: `rm -rf venv_mcp && python run_installer.py`

### "'StateManager' object has no attribute '_get_parent_task_id'"

**Cause**: Missing method in StateManager class

**Status**: Known issue, does not prevent core functionality

**Workaround**: Task orchestration still works, parent task tracking may show errors

### "spawn npx ENOENT" (Windows)

**Cause**: Node.js not in PATH for GUI applications

**Solutions**:
1. Use absolute path to node in configuration:
   ```json
   {
     "command": "C:\\Program Files\\nodejs\\node.exe",
     "args": ["C:\\path\\to\\mcp\\server\\index.js"]
   }
   ```
2. Add Node.js to system PATH (not just user PATH)
3. Run Command Prompt as Administrator

### "No MCP clients detected"

**Solutions**:
1. Install a supported MCP client first
2. Run the client at least once before installing orchestrator
3. Re-run `python install.py` after client installation

### "Module not found" / Import Errors

**Solutions**:
1. Delete virtual environment and reinstall:
   ```bash
   rm -rf venv_mcp && python install.py
   ```
2. Check Python version is 3.8+
3. Verify all dependencies installed correctly

## 🔧 Platform-Specific Issues

### Windows
- Use Command Prompt (not PowerShell) for installation
- Run as Administrator if permission errors occur
- Use absolute paths in all configurations
- Check Node.js is in system PATH

### macOS
- May need to allow apps to run from "System Preferences > Security"
- Use Terminal (not other shell apps) for installation
- Check Xcode command line tools installed

### Linux
- Ensure Python 3.8+ and pip are installed
- May need `python3` instead of `python` in commands
- Check file permissions on configuration directories

## 📋 Diagnostic Commands

```bash
# Check installation
python scripts/diagnostics/verify_tools.py

# Check configuration files
python scripts/diagnostics/check_status.py

# Test server manually
python -m mcp_task_orchestrator.server

# View logs
ls logs/  # Check for error logs
```

## 🆘 Getting Help

1. **Search existing issues**: [GitHub Issues](https://github.com/EchoingVesper/mcp-task-orchestrator/issues)
2. **Create new issue** with:
   - Your operating system
   - MCP client (Claude Desktop, Cursor, etc.)
   - Full error message
   - Configuration file content (remove sensitive data)
   - Output from diagnostic commands
