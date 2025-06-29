# Release Notes - v1.7.1

## 🚨 Critical Fixes Release

This release addresses two critical usability issues that were preventing users from properly using the MCP Task Orchestrator.

### 🐛 Bug Fixes

#### Issue #35: Claude Desktop Auto-Configuration Not Working
- **Problem**: The `mcp-task-orchestrator-cli install` command required a server path that PyPI users didn't know
- **Solution**: 
  - Added new `mcp-task-orchestrator-cli setup` command that requires no arguments
  - Enhanced `install` command to auto-detect server module path when not provided
  - Both commands now work seamlessly after `pip install mcp-task-orchestrator`

#### Issue #36: Orchestrator Files Created in Wrong Directory
- **Problem**: `.task_orchestrator` folder was created in unexpected system locations instead of user's project directory
- **Solution**:
  - Added optional `working_directory` parameter to `orchestrator_initialize_session`
  - Response now includes `working_directory` and `orchestrator_path` information
  - Users can specify exactly where orchestrator files should be created

### 📝 Documentation Updates

- Updated installation instructions to use new `setup` command
- Added documentation for `working_directory` parameter
- Enhanced session management architecture moved to CRITICAL status
- Updated README with new features and version badge

### 🔧 Technical Changes

#### CLI Enhancements (mcp_task_orchestrator_cli/cli.py)
- Added `get_server_module_path()` function for auto-detection
- Made `server_path` optional in `install` command
- Added new `setup` command for zero-configuration installation

#### Server Enhancements (mcp_task_orchestrator/server.py)
- Added `working_directory` parameter to `orchestrator_initialize_session` tool schema
- Enhanced `handle_initialize_session` to validate and use working directory
- Response now includes working directory information

### 💡 Usage Examples

#### Quick Setup (New!)
```bash
pip install mcp-task-orchestrator
mcp-task-orchestrator-cli setup
```

#### Specify Working Directory
```python
response = await call_tool("orchestrator_initialize_session", {
    "working_directory": "/path/to/your/project"
})
```

### 🚀 Upgrade Instructions

```bash
pip install --upgrade mcp-task-orchestrator
mcp-task-orchestrator-cli setup
```

### 📋 Compatibility

- Fully backward compatible
- No breaking changes
- Optional parameters default to previous behavior

### 🙏 Acknowledgments

Thank you to users who reported these critical issues. Your feedback helps make the orchestrator better for everyone!

---

**Full Changelog**: https://github.com/EchoingVesper/mcp-task-orchestrator/compare/v1.7.0...v1.7.1