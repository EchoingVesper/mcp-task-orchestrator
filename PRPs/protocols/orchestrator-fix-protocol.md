# Orchestrator Fix Protocol

When MCP Task Orchestrator fails, execute this protocol immediately. DO NOT work around the issue.

## Immediate Diagnosis

```bash
# 1. Check connection status
claude mcp list | grep task-orchestrator

# 2. Check for Python errors
tail -n 100 ~/.claude/logs/mcp-*.log | grep -A 5 -B 5 "error\|exception\|traceback"

# 3. Run health check
python tools/diagnostics/health_check.py

# 4. Check database integrity
ls -la .task_orchestrator/
sqlite3 .task_orchestrator/orchestrator.db "SELECT COUNT(*) FROM tasks;"
```

## Common Fixes

### Fix 1: Connection Lost

```bash
# Simple restart
claude mcp restart task-orchestrator

# Verify reconnection
claude mcp list | grep task-orchestrator
```

### Fix 2: Code Changes Made

```bash
# Reinstall and restart after code changes
pip install -e .
claude mcp restart task-orchestrator

# Test with health check
python -c "from mcp_task_orchestrator import __version__; print(__version__)"
```

### Fix 3: Database Issues

```bash
# Backup existing database
cp .task_orchestrator/orchestrator.db .task_orchestrator/orchestrator.db.backup

# Run migration fix
python -c "
from mcp_task_orchestrator.db.database import Database
db = Database('.task_orchestrator/orchestrator.db')
db.migrate()
"

# Verify database
sqlite3 .task_orchestrator/orchestrator.db ".tables"
```

### Fix 4: Import/Module Errors

```bash
# Check for import issues
python -c "import mcp_task_orchestrator; print('Import successful')"

# Reinstall dependencies
pip install -e ".[dev]"

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
```

### Fix 5: Server Process Hung

```bash
# Find and kill hung processes
ps aux | grep mcp_task_orchestrator | grep -v grep

# Kill specific process (replace PID)
# kill -9 PID

# Full restart
claude mcp restart task-orchestrator
```

## Advanced Recovery

### Complete Reset

```bash
# 1. Stop all MCP servers
claude mcp stop --all

# 2. Clear logs
rm ~/.claude/logs/mcp-task-orchestrator-*.log

# 3. Reinstall
pip uninstall mcp-task-orchestrator -y
pip install -e .

# 4. Restart Claude Code (notify user)
echo "RESTART REQUIRED: Please restart Claude Code"
```

### Auto-Recovery Implementation

```python
# Add to mcp_task_orchestrator/monitoring/auto_recovery.py
import asyncio
import subprocess
from pathlib import Path

class OrchestratorAutoRecovery:
    def __init__(self):
        self.last_restart = None
        self.restart_count = 0
        
    async def monitor_and_recover(self):
        """Monitor orchestrator health and auto-recover."""
        while True:
            try:
                # Check health
                result = subprocess.run(
                    ["claude", "mcp", "list"],
                    capture_output=True,
                    text=True
                )
                
                if "task-orchestrator" not in result.stdout:
                    await self.attempt_recovery()
                    
            except Exception as e:
                print(f"Monitor error: {e}")
                
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def attempt_recovery(self):
        """Attempt automatic recovery."""
        print("Orchestrator disconnected - attempting recovery...")
        
        # Try restart
        subprocess.run(["claude", "mcp", "restart", "task-orchestrator"])
        
        # If code changed, reinstall
        if self.detect_code_changes():
            subprocess.run(["pip", "install", "-e", "."])
            subprocess.run(["claude", "mcp", "restart", "task-orchestrator"])
        
        self.restart_count += 1
        
    def detect_code_changes(self):
        """Detect if orchestrator code has changed."""
        # Check git status for changes in orchestrator files
        result = subprocess.run(
            ["git", "diff", "--name-only", "mcp_task_orchestrator/"],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
```

## Validation After Fix

```bash
# 1. Verify connection
claude mcp list | grep task-orchestrator

# 2. Test basic tool
echo '{"tool": "orchestrator_health_check"}' | claude mcp call task-orchestrator

# 3. Run comprehensive check
python tools/diagnostics/health_check.py --full

# 4. Test with simple task
echo '{"tool": "orchestrator_get_status"}' | claude mcp call task-orchestrator
```

## When to Notify User

Notify the user for Claude Code restart if:

1. Multiple restart attempts fail (>3)
2. Server returns "incompatible version" error
3. MCP configuration file corrupted
4. Python environment issues persist

## Prevention Measures

1. **Always commit before modifying orchestrator code**
2. **Run tests before restarting**: `pytest tests/unit/`
3. **Use health checks regularly**: `orchestrator_health_check`
4. **Monitor logs**: `tail -f ~/.claude/logs/mcp-task-orchestrator-*.log`

## Emergency Contact

If orchestrator cannot be fixed with above methods:

1. Create detailed error report in `PRPs/issues/orchestrator-failure-{date}.md`
2. Include full error logs, diagnostic output, and attempted fixes
3. Tag as `[CRITICAL]` in filename
4. Notify user that manual intervention required

Remember: **NEVER** work around a broken orchestrator. Fix it first.