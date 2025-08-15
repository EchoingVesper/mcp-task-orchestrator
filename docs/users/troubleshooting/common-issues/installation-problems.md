

# Installation Problems

#

# MCP Tools Not Appearing

#

#

# Symptoms

- MCP Task Orchestrator tools don't show up in your MCP client

- Client shows "No tools available" or similar message

- Connection errors in MCP client logs

#

#

# Solution Steps

1. **Verify Installation**

```bash

# Check if package is installed

pip show mcp-task-orchestrator

# Test server directly

python -m mcp_task_orchestrator.server --version

```text

2. **Check MCP Client Configuration**

For Claude Desktop, verify your configuration file:

```text
json
{
  "mcp-task-orchestrator": {
    "command": "python",
    "args": ["-m", "mcp_task_orchestrator.server"],
    "env": {
      "MCP_TASK_ORCHESTRATOR_USE_DI": "true"
    }
  }
}

```text

3. **Restart MCP Client**

- Completely close and restart your MCP client

- Check if tools appear after restart

#

#

# Common Fixes

**Wrong Python path**: Use full path to Python executable
**Missing environment variables**: Add required env vars to config
**Permission issues**: Check file system permissions

#

# Database Connection Errors

#

#

# Symptoms

- "Database locked" or "Database access denied" errors

- Tasks fail to initialize or save state

- Workspace creation fails

#

#

# Solution Steps

1. **Check Workspace Directory**

```text
bash

# Verify workspace directory exists and is writable

ls -la .task_orchestrator/
touch .task_orchestrator/test_write
rm .task_orchestrator/test_write

```text

2. **Database Permissions**

```text
bash

# Fix database permissions

chmod 664 .task_orchestrator/*.db
chown $USER:$USER .task_orchestrator/

```text

3. **Clear Corrupted Database**

```text
bash

# Backup and recreate database (WARNING: loses all data)

mv .task_orchestrator/workspace.db .task_orchestrator/workspace.db.bak
python -m mcp_task_orchestrator.tools.diagnostics.init_workspace

```text

#

#

# Prevention

- Don't run multiple instances simultaneously

- Ensure adequate disk space

- Use proper file permissions

#

# Import Errors

#

#

# Symptoms

- "Module not found" errors

- Import failures when starting server

- Missing dependency errors

#

#

# Solution Steps

1. **Check Python Environment**

```text
bash

# Verify you're in the right environment

which python
pip list | grep mcp-task-orchestrator

```text

2. **Reinstall Dependencies**

```text
bash

# Clean reinstall

pip uninstall mcp-task-orchestrator
pip install mcp-task-orchestrator

# Or with development dependencies

pip install mcp-task-orchestrator[dev]

```text

3. **Virtual Environment Issues**

```text
bash

# Create fresh environment

python -m venv fresh_env
source fresh_env/bin/activate  

# Linux/Mac

# fresh_env\Scripts\activate   

# Windows

pip install mcp-task-orchestrator

```text

#

#

# Common Causes

**Wrong Python version**: Requires Python 3.8+
**Conflicting packages**: Check for package conflicts
**Incomplete installation**: Reinstall from scratch

#

# Configuration File Errors

#

#

# Symptoms

- "Invalid configuration" errors

- Server fails to start with config errors

- YAML parsing errors

#

#

# Solution Steps

1. **Validate YAML Syntax**

```text
bash

# Test YAML syntax online or with:

python -c "import yaml; yaml.safe_load(open('.task_orchestrator/config.yaml'))"

```text

2. **Reset to Default Configuration**

```text
bash

# Backup current config

cp .task_orchestrator/config.yaml .task_orchestrator/config.yaml.bak

# Regenerate default config

python -m mcp_task_orchestrator.tools.diagnostics.reset_config

```text

3. **Check Required Fields**

Ensure your config has these minimum fields:

```text
yaml
workspace:
  name: "default"
  database_path: ".task_orchestrator/workspace.db"

specialists:
  default_roles:
    - implementer
    - reviewer

```text

#

# Network and Firewall Issues

#

#

# Symptoms

- Timeouts during task execution

- Connection refused errors

- Slow performance

#

#

# Solution Steps

1. **Check Network Connectivity**

```text
bash

# Test basic connectivity

ping google.com

# Check if firewall is blocking

telnet localhost 3000  

# If using custom port

```text

2. **Proxy Configuration**

If behind corporate firewall:

```text
bash

# Set proxy environment variables

export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

```text

3. **Local Development Mode**

```text
bash

# Force local-only mode

export MCP_TASK_ORCHESTRATOR_OFFLINE=true

```text

#

# Performance Problems

#

#

# Symptoms

- Very slow task execution

- High memory usage

- System becomes unresponsive

#

#

# Solution Steps

1. **Check System Resources**

```text
bash

# Monitor resource usage

htop  

# or Task Manager on Windows

df -h  

# Check disk space

```text

2. **Adjust Configuration**

```text
yaml

# In .task_orchestrator/config.yaml

orchestration:
  max_concurrent_tasks: 1  

# Reduce from default 3

  timeout_minutes: 15      

# Reduce from default 30

```text

3. **Clear Old Data**

```text
bash

# Clean up old artifacts

python -m mcp_task_orchestrator.tools.maintenance.cleanup_artifacts

```text

#

# Getting Additional Help

#

#

# Diagnostic Commands

```text
bash

# Comprehensive health check

python -m mcp_task_orchestrator.tools.diagnostics.health_check

# Generate diagnostic report

python -m mcp_task_orchestrator.tools.diagnostics.generate_report

```text

#

#

# Log Analysis

```text
bash

# Enable debug logging

export MCP_TASK_ORCHESTRATOR_LOG_LEVEL=debug

# Check logs location

python -c "import mcp_task_orchestrator; print(mcp_task_orchestrator.get_log_path())"
```text

#

#

# Community Support

- Check [GitHub Issues](https://github.com/your-org/mcp-task-orchestrator/issues)

- Review [FAQ](../../../troubleshooting/README.md)

- Post in [Discussions](https://github.com/your-org/mcp-task-orchestrator/discussions)

#

# Next Steps

- [Database Issues](../error-reference/database-errors.md)

- [Connection Problems](../error-reference/connection-errors.md)

- [Performance Optimization](../diagnostic-tools/performance-monitoring.md)
