

# Server Reboot System User Guide

#

# Overview

The MCP Task Orchestrator includes an in-context server reboot system that allows seamless server restarts without disrupting client applications. This system preserves active tasks, maintains client connections, and ensures zero data loss during server updates.

#

# Key Benefits

- **Zero Client Disruption**: Client applications (Claude Desktop, VS Code, etc.) remain open during server restarts

- **State Preservation**: All active tasks and progress are maintained across restarts  

- **Automatic Reconnection**: Clients automatically reconnect after server restart

- **Graceful Shutdown**: Safe shutdown sequence ensures no data loss

- **Real-time Monitoring**: Track restart progress and status through MCP tools

#

# Quick Start

#

## Basic Server Restart

To trigger a basic server restart:

```python

# Using MCP tool

await orchestrator_restart_server()

```text

This will:

1. Enter maintenance mode (reject new requests)

2. Suspend active tasks at safe checkpoints

3. Serialize server state to disk

4. Gracefully shutdown the server

5. Start new server process

6. Restore state and resume tasks

7. Re-enable client connections

#

## Health Check Before Restart

Check if the server is ready for restart:

```text
python

# Check overall health

health_status = await orchestrator_health_check()

# Check specific restart readiness

readiness = await orchestrator_shutdown_prepare()

```text

#

# MCP Tools Reference

#

## orchestrator_restart_server

Trigger a graceful server restart with state preservation.

**Parameters:**

- `graceful` (boolean, default: true) - Whether to perform graceful shutdown

- `preserve_state` (boolean, default: true) - Whether to preserve server state

- `timeout` (integer, default: 30) - Maximum time to wait for restart (10-300 seconds)

- `reason` (string, default: "manual_request") - Reason for restart

**Restart Reasons:**

- `manual_request` - User-initiated restart

- `configuration_update` - Configuration changes requiring restart

- `schema_migration` - Database schema migration

- `error_recovery` - Recovery from system errors

- `emergency_shutdown` - Emergency restart without state preservation

**Example:**

```text
python

# Basic restart

await orchestrator_restart_server()

# Restart for configuration update with longer timeout

await orchestrator_restart_server({
    "reason": "configuration_update",
    "timeout": 60
})

# Emergency restart without state preservation

await orchestrator_restart_server({
    "graceful": false,
    "preserve_state": false,
    "reason": "emergency_shutdown"
})

```text
text

**Response:**

```text
json
{
  "success": true,
  "graceful": true,
  "preserve_state": true,
  "timeout": 30,
  "phase": "complete",
  "progress": 100.0,
  "message": "Restart completed successfully",
  "restart_reason": "manual_request",
  "completed_at": "2025-06-06T12:00:00Z"
}

```text
text

#

## orchestrator_health_check

Check server health and readiness for operations.

**Parameters:**

- `include_reboot_readiness` (boolean, default: true) - Include restart readiness

- `include_connection_status` (boolean, default: true) - Include client connections

- `include_database_status` (boolean, default: true) - Include database status

**Example:**

```text
python

# Full health check

health = await orchestrator_health_check()

# Check only restart readiness

restart_ready = await orchestrator_health_check({
    "include_reboot_readiness": true,
    "include_connection_status": false,
    "include_database_status": false
})

```text
text

**Response:**

```text
json
{
  "healthy": true,
  "timestamp": "2025-06-06T12:00:00Z",
  "server_version": "1.4.1",
  "checks": {
    "reboot_readiness": {
      "ready": true,
      "issues": []
    },
    "database": {
      "connected": true,
      "status": "operational"
    },
    "connections": {
      "active_connections": 2,
      "status": "operational"
    }
  }
}

```text
text

#

## orchestrator_shutdown_prepare

Check server readiness for graceful shutdown.

**Parameters:**

- `check_active_tasks` (boolean, default: true) - Check for active tasks

- `check_database_state` (boolean, default: true) - Check database state

- `check_client_connections` (boolean, default: true) - Check client connections

**Example:**

```text
python

# Full shutdown readiness check

readiness = await orchestrator_shutdown_prepare()

```text
text

**Response:**

```text
json
{
  "ready_for_shutdown": true,
  "blocking_issues": [],
  "timestamp": "2025-06-06T12:00:00Z",
  "checks": {
    "active_tasks": {
      "count": 2,
      "suspendable": true,
      "status": "ready"
    },
    "database": {
      "transactions_pending": 0,
      "connections_open": 1,
      "status": "ready"
    },
    "client_connections": {
      "active_connections": 2,
      "notifiable": true,
      "status": "ready"
    }
  }
}

```text
text

#

## orchestrator_restart_status

Get current status of restart operation.

**Parameters:**

- `include_history` (boolean, default: false) - Include restart history

- `include_error_details` (boolean, default: true) - Include detailed errors

**Example:**

```text
python

# Current restart status

status = await orchestrator_restart_status()

# Status with history

status_with_history = await orchestrator_restart_status({
    "include_history": true
})

```text
text

**Response:**

```text
json
{
  "current_status": {
    "phase": "complete",
    "progress": 100.0,
    "message": "Restart completed successfully",
    "started_at": "2025-06-06T12:00:00Z",
    "errors": []
  },
  "timestamp": "2025-06-06T12:00:05Z"
}

```text
text

#

## orchestrator_reconnect_test

Test client reconnection capability.

**Parameters:**

- `session_id` (string, optional) - Test specific session

- `include_buffer_status` (boolean, default: true) - Include buffer status

- `include_reconnection_stats` (boolean, default: true) - Include reconnection stats

**Example:**

```text
python

# Test all client connections

test_result = await orchestrator_reconnect_test()

# Test specific client session

session_test = await orchestrator_reconnect_test({
    "session_id": "client_session_123"
})

```text
text

#

# Client Integration Patterns

#

## Claude Desktop

Claude Desktop automatically handles server reconnection:

1. **Connection Loss Detection**: Detects when server becomes unavailable

2. **Automatic Retry**: Attempts reconnection with exponential backoff

3. **Session Restoration**: Restores conversation context after reconnection

4. **User Notification**: Shows connection status in UI

**Best Practices:**

- Allow 30-60 seconds for reconnection after restart

- Save important work before triggering restarts

- Monitor connection status during restart process

#

## VS Code / Cursor / Windsurf

MCP extensions in code editors handle reconnection:

1. **Extension Monitoring**: Extension monitors MCP server connection

2. **Graceful Degradation**: Features gracefully disable during restart

3. **Automatic Reconnection**: Extension reconnects when server available

4. **State Synchronization**: Workspace state synchronized after reconnection

**Integration Code:**

```text
typescript
// Extension reconnection handling
mcp.onConnectionLost(() => {
    // Show reconnection indicator
    showReconnectingStatus();
    
    // Attempt reconnection with backoff
    scheduleReconnection();
});

mcp.onReconnected(() => {
    // Hide reconnection indicator
    hideReconnectingStatus();
    
    // Sync workspace state
    syncWorkspaceState();
});

```text
text

#

# Operational Procedures

#

## Planned Maintenance

For planned server maintenance:

1. **Pre-Maintenance Check**
   
```text
python
   

# Verify system health

   health = await orchestrator_health_check()
   
   

# Check restart readiness

   readiness = await orchestrator_shutdown_prepare()
   
```text
text

2. **Notify Stakeholders** (if applicable)

- Inform users of planned maintenance window

- Estimate restart duration (typically <30 seconds)

3. **Perform Restart**
   
```text
python
   

# Restart with appropriate reason

   result = await orchestrator_restart_server({
       "reason": "configuration_update",
       "timeout": 60
   })
   
```text
text

4. **Verify Success**
   
```text
python
   

# Check restart status

   status = await orchestrator_restart_status()
   
   

# Verify system health

   health = await orchestrator_health_check()
   
```text
text

#

## Emergency Recovery

For emergency restart scenarios:

1. **Assess Situation**

- Determine if graceful restart is possible

- Check for critical data that needs preservation

2. **Emergency Restart** (if graceful restart not possible)
   
```text
python
   

# Emergency restart without state preservation

   result = await orchestrator_restart_server({
       "graceful": false,
       "preserve_state": false,
       "reason": "emergency_shutdown",
       "timeout": 15
   })
   
```text
text

3. **Post-Recovery Validation**

- Verify server functionality

- Check for data loss or corruption

- Restore from backups if necessary

#

## Configuration Updates

When updating server configuration:

1. **Backup Current State**
   
```text
python
   

# Create manual state snapshot

   health = await orchestrator_health_check()
   
```text
text

2. **Update Configuration Files**

- Modify configuration files

- Validate configuration syntax

3. **Restart with Configuration Update**
   
```text
python
   result = await orchestrator_restart_server({
       "reason": "configuration_update"
   })
   
```text
text

4. **Validate New Configuration**
   
```text
python
   

# Verify configuration applied correctly

   health = await orchestrator_health_check()
   
```text
text

#

# Monitoring and Alerting

#

## Key Metrics to Monitor

1. **Restart Success Rate**

- Target: >99% successful restarts

- Alert: <95% success rate over 24 hours

2. **Restart Duration**

- Target: <30 seconds total restart time

- Alert: >60 seconds restart time

3. **Client Reconnection Rate**

- Target: >99% automatic reconnection

- Alert: <95% reconnection success

4. **State Preservation Rate**

- Target: 100% state preservation for graceful restarts

- Alert: Any state loss during graceful restart

#

## Monitoring Setup

```text
python

# Example monitoring script

async def monitor_restart_health():
    health = await orchestrator_health_check()
    
    if not health['healthy']:
        

# Send alert

        send_alert(f"Server health check failed: {health}")
    
    

# Check restart history

    status = await orchestrator_restart_status({
        "include_history": true
    })
    
    

# Analyze restart patterns and success rates

    analyze_restart_patterns(status)

```text

#

# Performance Tuning

#

## Optimal Settings

For typical workloads:

```text
python

# Recommended timeout settings

restart_timeouts = {
    "total_restart": 30,        

# Total restart process

    "shutdown_timeout": 15,     

# Graceful shutdown

    "task_suspension": 5,       

# Task suspension

    "process_startup": 10       

# New process startup

}

# Buffer settings

buffer_config = {
    "max_buffer_size": 100,     

# Requests per client

    "buffer_expiration": 300,   

# 5 minutes

    "cleanup_interval": 60      

# 1 minute

}
```text

#

## Performance Optimization

1. **Reduce State Size**

- Archive completed tasks regularly

- Limit active task count

- Compress state snapshots

2. **Optimize Restart Timing**

- Schedule restarts during low activity

- Batch multiple configuration changes

- Use faster storage for state files

3. **Client Connection Optimization**

- Reduce reconnection timeout

- Implement connection pooling

- Use persistent connections where possible

#

# Security Considerations

#

## Access Control

- Restart operations require appropriate permissions

- Monitor restart requests for unauthorized access

- Log all restart operations with user context

#

## State Security

- State files are encrypted at rest

- Temporary state files have restricted permissions

- State snapshots exclude sensitive information

#

## Network Security

- Client reconnection uses secure channels

- Validate client identity during reconnection

- Monitor for reconnection attacks

---

*This documentation covers version 1.4.1 of the MCP Task Orchestrator. For the latest updates, see the project repository.*
