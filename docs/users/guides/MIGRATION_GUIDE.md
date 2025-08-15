

# MCP Task Orchestrator - Migration Guide

*Smooth transition from legacy installation methods to the optimized approach*

#

# 🎯 What Changed?

The installation method has been updated to resolve import errors and improve reliability. Here's what you need to know:

#

#

# Old Method (Deprecated)

```bash

# These methods are deprecated but still work via compatibility wrapper

python install.py
python installer/main_installer.py

```text

#

#

# New Method (Recommended)

```text
bash

# This is the new, optimized method

python run_installer.py

```text

#

# 🔧 Why the Change?

The new `run_installer.py` method provides:

- **✅ Import Error Resolution**: Fixes "ImportError: attempted relative import with no known parent package"

- **✅ Version Compatibility**: Ensures correct MCP package versions (mcp>=1.9.0)

- **✅ Better Error Handling**: Clear, helpful error messages

- **✅ Cross-Platform Support**: Improved compatibility across different Python environments

- **✅ Faster Installation**: Optimized process with fewer failure points

#

# 🚀 Migration Steps

#

#

# For Individual Users

1. **Current Scripts Work**: Your existing `python install.py` commands will continue to work

2. **Update When Convenient**: Replace with `python run_installer.py` at your convenience

3. **No Reinstallation Needed**: Already installed? No action required.

#

#

# For Documentation/Scripts

Replace these patterns:

```text
bash

# OLD (still works, but deprecated)

python install.py
python installer/main_installer.py
python installer/main_installer.py --clients claude-desktop

# NEW (recommended)

python run_installer.py
python run_installer.py
python run_installer.py --clients claude-desktop

```text

#

#

# For CI/CD Pipelines

Update your automation scripts:

```text
yaml

# OLD

- name: Install MCP Task Orchestrator
  run: python install.py

# NEW

- name: Install MCP Task Orchestrator
  run: python run_installer.py

```text

#

# 🛠️ Troubleshooting Migration

#

#

# If You Get Import Errors with Old Method

**Error Message**: `ImportError: attempted relative import with no known parent package`

**Solution**: 

```text
bash

# Use the new method instead

python run_installer.py
```text
text

#

#

# If You Get Version Conflicts

**Error Message**: References to `mcp==1.4.0` or version conflicts

**Solution**:

1. Delete virtual environment: `rm -rf venv_mcp/` (Linux/Mac) or `rmdir /s venv_mcp` (Windows)

2. Use new installer: `python run_installer.py`

#

#

# If Legacy Scripts Fail

**Issue**: Automated scripts using old installation commands fail

**Solution**:

1. **Immediate Fix**: Scripts using `python install.py` should continue working (with deprecation warnings)

2. **Long-term Fix**: Update scripts to use `python run_installer.py`

#

# 📋 Compatibility Matrix

| Installation Method | Status | Functionality | Recommendation |
|-------------------|--------|---------------|---------------|
| `python run_installer.py` | ✅ **Recommended** | Full functionality | Use for all new installations |
| `python install.py` | ⚠️ **Deprecated** | Works via wrapper | Migrate when convenient |
| `python installer/main_installer.py` | ❌ **Broken** | ImportError | Do not use |

#

# 📝 Support for Legacy Users

#

#

# Gradual Migration Approach

1. **Phase 1**: Legacy methods redirect to new method with helpful messages

2. **Phase 2**: Update your scripts and documentation at your own pace

3. **Phase 3**: Eventually, legacy wrappers may be removed (with advance notice)

#

#

# Backward Compatibility Promise

- **Current**: `python install.py` continues to work via intelligent wrapper

- **Future**: Legacy support will be maintained for at least 6 months

- **Advance Notice**: Any changes to legacy support will be announced in release notes

#

# 🎯 Quick Migration Checklist

- [ ] **Test New Method**: Run `python run_installer.py` to verify it works

- [ ] **Update Scripts**: Replace old commands in automation scripts

- [ ] **Update Documentation**: Update any internal documentation or guides

- [ ] **Team Communication**: Inform team members about the new method

- [ ] **Monitor**: Watch for deprecation warnings and plan updates accordingly

#

# 🆘 Need Help?

#

#

# Quick Solutions

- **Installation Issues**: Use `python run_installer.py` instead of old methods

- **Import Errors**: The new method resolves these automatically

- **Version Conflicts**: Delete `venv_mcp/` and reinstall with new method

#

#

# Getting Support

- **GitHub Issues**: [Report problems](https://github.com/EchoingVesper/mcp-task-orchestrator/issues)

- **Diagnostics**: Run `python scripts/diagnostics/verify_tools.py`

- **Documentation**: See [Installation Guide](docs/installation.md) for details

---

*This migration guide ensures a smooth transition while maintaining compatibility with existing workflows.*
