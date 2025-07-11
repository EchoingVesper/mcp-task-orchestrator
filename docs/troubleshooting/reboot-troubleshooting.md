# Server Reboot Troubleshooting Guide

## Overview

This guide provides solutions for common issues with the MCP Task Orchestrator server reboot system. Follow the diagnostic steps and solutions to resolve restart-related problems.

## Quick Diagnostic Checklist

Before troubleshooting specific issues, run these basic checks:

1. **System Health Check**
   ```python
   health = await orchestrator_health_check()
   print("System healthy:", health['healthy'])
   ```

2. **Restart Readiness**
   ```python
   readiness = await orchestrator_shutdown_prepare()
   print("Ready for restart:", readiness['ready_for_shutdown'])
   if not readiness['ready_for_shutdown']:
       print("Blocking issues:", readiness['blocking_issues'])
   ```

3. **Current Status**
   ```python
   status = await orchestrator_restart_status()
   print("Current phase:", status['current_status']['phase'])
   ```

## Common Issues and Solutions

### 1. Restart Fails to Initiate

**Symptoms:**
- `orchestrator_restart_server` returns `success: false`
- Error message: "Failed to initiate shutdown"

**Possible Causes:**
- Another restart already in progress
- System in maintenance mode
- Reboot manager not initialized

**Diagnosis:**
```python
# Check current status
status = await orchestrator_restart_status()
print("Current phase:", status['current_status']['phase'])

# Check if already in maintenance mode
if status['current_status']['maintenance_mode']:
    print("System already in maintenance mode")

# Check system health
health = await orchestrator_health_check()
if 'reboot_readiness' in health['checks']:
    print("Reboot ready:", health['checks']['reboot_readiness']['ready'])
```

**Solutions:**

1. **Wait for Current Operation** (if restart in progress):
   ```python
   # Wait for current restart to complete
   while True:
       status = await orchestrator_restart_status()
       phase = status['current_status']['phase']
       
       if phase in ['complete', 'failed', 'idle']:
           break
           
       print(f"Waiting for restart to complete: {phase}")
       await asyncio.sleep(2)
   ```

2. **Force Emergency Restart** (if stuck):
   ```python
   # Emergency restart to clear stuck state
   result = await orchestrator_restart_server({
       "graceful": false,
       "preserve_state": false,
       "reason": "emergency_shutdown"
   })
   ```

3. **Reset Maintenance Mode** (manual intervention required):
   - Check server logs for stuck processes
   - Restart server manually if necessary

### 2. Restart Times Out

**Symptoms:**
- Restart operation exceeds specified timeout
- Status shows restart "stuck" in a particular phase

**Possible Causes:**
- Large state files taking too long to serialize
- Database operations not completing
- Tasks not suspending properly

**Diagnosis:**
```python
# Monitor restart progress
status = await orchestrator_restart_status({
    "include_error_details": true
})

print("Current phase:", status['current_status']['phase'])
print("Progress:", status['current_status']['progress'])
print("Errors:", status['current_status']['errors'])

# Check what's blocking
readiness = await orchestrator_shutdown_prepare()
print("Blocking issues:", readiness['blocking_issues'])
```

**Solutions:**

1. **Increase Timeout**:
   ```python
   # Use longer timeout for complex operations
   result = await orchestrator_restart_server({
       "timeout": 120  # 2 minutes instead of default 30 seconds
   })
   ```

2. **Emergency Restart** (if timeout persists):
   ```python
   # Skip state preservation for faster restart
   result = await orchestrator_restart_server({
       "preserve_state": false,
       "timeout": 30
   })
   ```

3. **Manual Intervention** (server-side):
   - Check disk space for state files
   - Review database connection status
   - Kill hung processes manually

### 3. State Not Preserved

**Symptoms:**
- Active tasks lost after restart
- Client connections not restored
- Progress reset to initial state

**Possible Causes:**
- State serialization failed
- State file corrupted or missing
- State restoration failed during startup

**Diagnosis:**
```python
# Check if state preservation was requested
status = await orchestrator_restart_status()

# Look for serialization errors
if status['current_status']['errors']:
    for error in status['current_status']['errors']:
        if 'serialization' in error.lower():
            print(f"Serialization error: {error}")

# Check state file status
import os
state_dir = ".task_orchestrator/server_state"
if os.path.exists(f"{state_dir}/current_state.json"):
    print("State file exists")
    # Check file size and modification time
    stat = os.stat(f"{state_dir}/current_state.json")
    print(f"State file size: {stat.st_size} bytes")
    print(f"Last modified: {stat.st_mtime}")
else:
    print("State file missing!")
```

**Solutions:**

1. **Verify State Preservation Settings**:
   ```python
   # Ensure state preservation is enabled
   result = await orchestrator_restart_server({
       "preserve_state": true,
       "graceful": true
   })
   ```

2. **Check Available Disk Space**:
   ```bash
   # Check disk space for state files
   df -h .task_orchestrator/server_state/
   ```

3. **Manual State Recovery** (if backup exists):
   ```python
   # List available state backups
   import glob
   backups = glob.glob(".task_orchestrator/server_state/backup_state_*.json")
   print("Available backups:", backups)
   
   # Restore from most recent backup manually
   # (requires server restart with restored file)
   ```

### 4. Client Reconnection Issues

**Symptoms:**
- Clients fail to reconnect after restart
- Connection timeouts or errors
- Partial functionality after reconnection

**Possible Causes:**
- Client buffering not working
- Reconnection protocol failing
- Network connectivity issues

**Diagnosis:**
```python
# Test client reconnection capability
test_result = await orchestrator_reconnect_test()
print("Test status:", test_result['overall_status'])
print("Results:", test_result['results'])

# Check connection status
health = await orchestrator_health_check({
    "include_connection_status": true
})
print("Connection status:", health['checks']['connections'])

# Check buffer status
if 'buffer_status' in test_result['results']:
    buffer = test_result['results']['buffer_status']
    print(f"Buffered requests: {buffer['total_buffered_requests']}")
```

**Solutions:**

1. **Verify Client Configuration**:
   - Ensure clients have reconnection enabled
   - Check client timeout settings
   - Verify network connectivity

2. **Test Specific Client Session**:
   ```python
   # Test specific client reconnection
   session_test = await orchestrator_reconnect_test({
       "session_id": "your_client_session_id"
   })
   print("Session test result:", session_test)
   ```

3. **Clear Request Buffers** (if buffers are full):
   ```python
   # Restart with buffer clearing
   result = await orchestrator_restart_server({
       "reason": "error_recovery"
   })
   ```

4. **Manual Client Restart** (last resort):
   - Restart client application
   - Clear client cache/settings
   - Reconnect to server

### 5. Database Connection Issues

**Symptoms:**
- Database errors during restart
- State restoration fails
- Task data inconsistencies

**Possible Causes:**
- Database locks during shutdown
- Connection pool exhaustion
- Database file corruption

**Diagnosis:**
```python
# Check database health
health = await orchestrator_health_check({
    "include_database_status": true
})
print("Database status:", health['checks']['database'])

# Check for database-related errors
status = await orchestrator_restart_status({
    "include_error_details": true
})
for error in status['current_status']['errors']:
    if any(db_term in error.lower() for db_term in ['database', 'db', 'sqlite']):
        print(f"Database error: {error}")
```

**Solutions:**

1. **Wait for Database Operations** to complete:
   ```python
   # Check for pending transactions
   readiness = await orchestrator_shutdown_prepare({
       "check_database_state": true
   })
   db_check = readiness['checks']['database']
   if db_check['transactions_pending'] > 0:
       print("Waiting for database transactions to complete...")
       # Wait and retry
   ```

2. **Force Database Cleanup**:
   ```python
   # Emergency restart with database reset
   result = await orchestrator_restart_server({
       "preserve_state": false,  # Skip problematic state
       "reason": "error_recovery"
   })
   ```

3. **Database Integrity Check** (server-side):
   ```bash
   # Check SQLite database integrity
   sqlite3 .task_orchestrator/task_orchestrator.db "PRAGMA integrity_check;"
   ```

### 6. Performance Issues

**Symptoms:**
- Restart takes longer than expected
- High memory usage during restart
- Client connection delays

**Possible Causes:**
- Large task state data
- Many active client connections
- Insufficient system resources

**Diagnosis:**
```python
# Monitor restart performance
import time

start_time = time.time()
result = await orchestrator_restart_server()
duration = time.time() - start_time

print(f"Restart duration: {duration:.2f} seconds")
if duration > 30:
    print("Restart took longer than expected")

# Check system resource usage
# (requires system monitoring tools)
```

**Solutions:**

1. **Optimize State Size**:
   - Archive completed tasks before restart
   - Limit active task count
   - Clean up old artifacts

2. **Increase System Resources**:
   - Monitor CPU and memory usage
   - Increase available disk space
   - Optimize database performance

3. **Stagger Client Connections**:
   ```python
   # Use longer timeout for high-load scenarios
   result = await orchestrator_restart_server({
       "timeout": 60  # Allow more time for complex operations
   })
   ```

## Error Code Reference

### RESTART_001: Initialization Failed
- **Cause**: Reboot manager not properly initialized
- **Solution**: Check server startup logs, verify reboot system initialization

### RESTART_002: Already In Progress  
- **Cause**: Another restart operation is already running
- **Solution**: Wait for current operation to complete or force emergency restart

### RESTART_003: System Not Ready
- **Cause**: Blocking conditions prevent restart
- **Solution**: Use `orchestrator_shutdown_prepare` to identify and resolve issues

### RESTART_004: Timeout Exceeded
- **Cause**: Operation took longer than specified timeout
- **Solution**: Increase timeout or use emergency restart

### RESTART_005: State Serialization Failed
- **Cause**: Unable to save server state to disk
- **Solution**: Check disk space, file permissions, or skip state preservation

### RESTART_006: Process Management Failed
- **Cause**: Unable to start/stop server processes
- **Solution**: Check system permissions, process limits, or restart manually

### RESTART_007: Connection Manager Error
- **Cause**: Client connection handling failed
- **Solution**: Test client connections, clear buffers, or restart clients

### RESTART_008: Database Error
- **Cause**: Database operations failed during restart
- **Solution**: Check database integrity, close connections, or reset database

## Advanced Troubleshooting

### Enable Debug Logging

Set environment variable for detailed logging:
```bash
export MCP_TASK_ORCHESTRATOR_LOG_LEVEL=DEBUG
```

### Manual State File Inspection

```python
import json

# Load and inspect state file
with open('.task_orchestrator/server_state/current_state.json', 'r') as f:
    state = json.load(f)

print("State metadata:")
print(f"  Version: {state['version']}")
print(f"  Timestamp: {state['timestamp']}")
print(f"  Server version: {state['server_version']}")
print(f"  Restart reason: {state['restart_reason']}")
print(f"  Active tasks: {len(state['active_tasks'])}")
print(f"  Client sessions: {len(state['client_sessions'])}")

# Check integrity
if state['integrity_hash']:
    print("State has integrity hash - validation available")
```

### Process Monitoring

```bash
# Monitor server processes during restart
ps aux | grep mcp_task_orchestrator

# Check for hung processes
ps aux | grep -E "(zombie|<defunct>)"

# Monitor file descriptor usage
lsof | grep task_orchestrator | wc -l
```

### Network Diagnostics

```bash
# Check for open connections
netstat -an | grep ESTABLISHED | grep <server_port>

# Monitor connection attempts
tcpdump -i lo port <server_port>
```

## Recovery Procedures

### Complete System Recovery

If the server is completely unresponsive:

1. **Stop Server Process**:
   ```bash
   pkill -f mcp_task_orchestrator
   ```

2. **Clear Lock Files** (if any):
   ```bash
   rm -f .task_orchestrator/*.lock
   ```

3. **Backup Current State**:
   ```bash
   cp .task_orchestrator/server_state/current_state.json \
      .task_orchestrator/server_state/recovery_backup.json
   ```

4. **Restart Server**:
   ```bash
   python -m mcp_task_orchestrator.server
   ```

5. **Verify Recovery**:
   ```python
   health = await orchestrator_health_check()
   print("Recovery successful:", health['healthy'])
   ```

### State Recovery from Backup

If state file is corrupted:

1. **List Available Backups**:
   ```bash
   ls -la .task_orchestrator/server_state/backup_state_*.json
   ```

2. **Restore from Backup**:
   ```bash
   # Stop server first
   cp .task_orchestrator/server_state/backup_state_<timestamp>.json \
      .task_orchestrator/server_state/current_state.json
   ```

3. **Restart and Verify**:
   ```python
   # Start server and check state restoration
   health = await orchestrator_health_check()
   status = await orchestrator_restart_status()
   ```

## Prevention Best Practices

### Regular Maintenance

1. **Monitor Restart Health**:
   ```python
   # Daily health check
   health = await orchestrator_health_check()
   if not health['healthy']:
       # Send alert or take corrective action
       send_alert("Server health check failed")
   ```

2. **Clean Up Old State Files**:
   ```bash
   # Weekly cleanup of old backups (keep last 10)
   cd .task_orchestrator/server_state/
   ls -t backup_state_*.json | tail -n +11 | xargs rm -f
   ```

3. **Archive Completed Tasks**:
   ```python
   # Monthly task archival
   # (implementation depends on task management system)
   ```

### Monitoring Setup

```python
# Example monitoring script
async def monitor_restart_system():
    health = await orchestrator_health_check()
    
    # Check health metrics
    if not health['healthy']:
        alert("Server health check failed", health)
    
    # Check recent restart history
    status = await orchestrator_restart_status({"include_history": true})
    
    # Analyze restart patterns
    if status.get('history'):
        recent_failures = [
            r for r in status['history']['recent_restarts']
            if not r['success']
        ]
        
        if len(recent_failures) > 3:
            alert("Multiple restart failures detected", recent_failures)

# Run monitoring periodically
import asyncio
asyncio.create_task(monitor_restart_system())
```

## Support and Escalation

### Log Collection

Before contacting support, collect these logs:

1. **Server Logs**:
   ```bash
   # Main server log
   grep -A 10 -B 10 "restart\|reboot\|shutdown" server.log
   ```

2. **System Information**:
   ```bash
   # System resources
   df -h
   free -h
   ps aux | head -20
   ```

3. **State Files**:
   ```bash
   # State file information
   ls -la .task_orchestrator/server_state/
   ```

### Contact Information

For issues not resolved by this guide:
- Check project documentation: [Project Repository]
- Report bugs: [Issue Tracker]
- Community support: [Community Forum]

---

*This troubleshooting guide covers common issues with the server reboot system. For additional support, consult the project documentation or community resources.*