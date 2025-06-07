# Server Reboot API Reference

## Overview

This document provides detailed API reference for the MCP Task Orchestrator server reboot system. The reboot system exposes functionality through MCP (Model Context Protocol) tools that can be called by compatible clients.

## MCP Protocol Integration

The reboot system integrates with the standard MCP protocol, exposing tools that clients can discover and invoke. All tools follow MCP conventions for parameter validation, error handling, and response formatting.

### Tool Discovery

Clients can discover available reboot tools through the standard MCP tool listing:

```json
{
  "method": "tools/list",
  "params": {}
}
```

Response includes all reboot tools:
```json
{
  "tools": [
    {
      "name": "orchestrator_restart_server",
      "description": "Trigger a graceful server restart with state preservation",
      "inputSchema": { ... }
    },
    {
      "name": "orchestrator_health_check", 
      "description": "Check server health and readiness for operations",
      "inputSchema": { ... }
    }
    // ... other tools
  ]
}
```

## Tool Reference

### orchestrator_restart_server

Triggers a graceful server restart with comprehensive state preservation.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "graceful": {
      "type": "boolean",
      "description": "Whether to perform graceful shutdown",
      "default": true
    },
    "preserve_state": {
      "type": "boolean", 
      "description": "Whether to preserve server state across restart",
      "default": true
    },
    "timeout": {
      "type": "integer",
      "description": "Maximum time to wait for restart completion (seconds)",
      "default": 30,
      "minimum": 10,
      "maximum": 300
    },
    "reason": {
      "type": "string",
      "enum": [
        "configuration_update",
        "schema_migration", 
        "error_recovery",
        "manual_request",
        "emergency_shutdown"
      ],
      "description": "Reason for the restart",
      "default": "manual_request"
    }
  },
  "required": []
}
```

#### Response Schema

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether the restart was successful"
    },
    "graceful": {
      "type": "boolean",
      "description": "Whether graceful shutdown was performed"
    },
    "preserve_state": {
      "type": "boolean",
      "description": "Whether state was preserved"
    },
    "timeout": {
      "type": "integer", 
      "description": "Timeout used for restart"
    },
    "phase": {
      "type": "string",
      "enum": [
        "preparation_failed",
        "initiation_failed", 
        "maintenance_mode",
        "suspending_tasks",
        "serializing_state",
        "closing_connections",
        "finalizing",
        "complete",
        "failed"
      ],
      "description": "Current or final restart phase"
    },
    "progress": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "description": "Restart progress percentage"
    },
    "message": {
      "type": "string",
      "description": "Human-readable status message"
    },
    "restart_reason": {
      "type": "string",
      "description": "Reason for restart"
    },
    "completed_at": {
      "type": "string",
      "format": "date-time", 
      "description": "ISO timestamp when restart completed"
    },
    "errors": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of errors encountered during restart"
    }
  },
  "required": ["success", "graceful", "preserve_state", "phase"]
}
```

#### Examples

**Basic Restart:**
```json
// Request
{
  "method": "tools/call",
  "params": {
    "name": "orchestrator_restart_server",
    "arguments": {}
  }
}

// Response
{
  "content": [
    {
      "type": "text",
      "text": "{\"success\": true, \"graceful\": true, \"preserve_state\": true, \"timeout\": 30, \"phase\": \"complete\", \"progress\": 100.0, \"message\": \"Restart completed successfully\", \"restart_reason\": \"manual_request\", \"completed_at\": \"2025-06-06T12:00:05Z\", \"errors\": []}"
    }
  ]
}
```

**Configuration Update Restart:**
```json
// Request
{
  "method": "tools/call",
  "params": {
    "name": "orchestrator_restart_server", 
    "arguments": {
      "reason": "configuration_update",
      "timeout": 60
    }
  }
}
```

**Emergency Restart:**
```json
// Request  
{
  "method": "tools/call",
  "params": {
    "name": "orchestrator_restart_server",
    "arguments": {
      "graceful": false,
      "preserve_state": false,
      "reason": "emergency_shutdown",
      "timeout": 15
    }
  }
}
```

### orchestrator_health_check

Performs comprehensive health checking of server components and restart readiness.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "include_reboot_readiness": {
      "type": "boolean",
      "description": "Whether to include restart readiness in health check",
      "default": true
    },
    "include_connection_status": {
      "type": "boolean",
      "description": "Whether to include client connection status",
      "default": true
    },
    "include_database_status": {
      "type": "boolean",
      "description": "Whether to include database status", 
      "default": true
    }
  },
  "required": []
}
```

#### Response Schema

```json
{
  "type": "object",
  "properties": {
    "healthy": {
      "type": "boolean",
      "description": "Overall health status"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO timestamp of health check"
    },
    "server_version": {
      "type": "string",
      "description": "Server version"
    },
    "checks": {
      "type": "object",
      "properties": {
        "reboot_readiness": {
          "type": "object",
          "properties": {
            "ready": {"type": "boolean"},
            "issues": {
              "type": "array",
              "items": {"type": "string"}
            },
            "details": {"type": "object"}
          }
        },
        "database": {
          "type": "object", 
          "properties": {
            "connected": {"type": "boolean"},
            "status": {"type": "string"}
          }
        },
        "connections": {
          "type": "object",
          "properties": {
            "active_connections": {"type": "integer"},
            "status": {"type": "string"}
          }
        }
      }
    }
  },
  "required": ["healthy", "timestamp", "server_version"]
}
```

### orchestrator_shutdown_prepare

Validates server readiness for graceful shutdown, identifying any blocking conditions.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "check_active_tasks": {
      "type": "boolean",
      "description": "Whether to check for active tasks",
      "default": true
    },
    "check_database_state": {
      "type": "boolean",
      "description": "Whether to check database state",
      "default": true
    },
    "check_client_connections": {
      "type": "boolean",
      "description": "Whether to check client connections",
      "default": true
    }
  },
  "required": []
}
```

#### Response Schema

```json
{
  "type": "object",
  "properties": {
    "ready_for_shutdown": {
      "type": "boolean",
      "description": "Whether server is ready for shutdown"
    },
    "blocking_issues": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of issues blocking shutdown"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO timestamp of readiness check"
    },
    "checks": {
      "type": "object",
      "properties": {
        "active_tasks": {
          "type": "object",
          "properties": {
            "count": {"type": "integer"},
            "suspendable": {"type": "boolean"},
            "status": {"type": "string"}
          }
        },
        "database": {
          "type": "object",
          "properties": {
            "transactions_pending": {"type": "integer"},
            "connections_open": {"type": "integer"},
            "status": {"type": "string"}
          }
        },
        "client_connections": {
          "type": "object",
          "properties": {
            "active_connections": {"type": "integer"},
            "notifiable": {"type": "boolean"},
            "status": {"type": "string"}
          }
        }
      }
    }
  },
  "required": ["ready_for_shutdown", "blocking_issues", "timestamp"]
}
```

### orchestrator_restart_status

Retrieves current restart operation status and optionally historical restart information.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "include_history": {
      "type": "boolean",
      "description": "Whether to include restart history",
      "default": false
    },
    "include_error_details": {
      "type": "boolean",
      "description": "Whether to include detailed error information",
      "default": true
    }
  },
  "required": []
}
```

#### Response Schema

```json
{
  "type": "object",
  "properties": {
    "current_status": {
      "type": "object",
      "properties": {
        "phase": {
          "type": "string",
          "enum": [
            "idle", "preparing", "maintenance_mode",
            "suspending_tasks", "serializing_state",
            "closing_connections", "finalizing",
            "complete", "failed"
          ]
        },
        "progress": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "message": {"type": "string"},
        "started_at": {
          "type": "string",
          "format": "date-time"
        },
        "estimated_completion": {
          "type": "string", 
          "format": "date-time"
        },
        "errors": {
          "type": "array",
          "items": {"type": "string"}
        },
        "maintenance_mode": {"type": "boolean"}
      }
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "history": {
      "type": "object",
      "properties": {
        "recent_restarts": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "timestamp": {"type": "string", "format": "date-time"},
              "reason": {"type": "string"},
              "success": {"type": "boolean"},
              "duration": {"type": "number"}
            }
          }
        },
        "total_restarts": {"type": "integer"},
        "last_successful_restart": {
          "type": "string",
          "format": "date-time"
        }
      }
    }
  },
  "required": ["current_status", "timestamp"]
}
```

### orchestrator_reconnect_test

Tests client reconnection capabilities and connection management functionality.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "session_id": {
      "type": "string",
      "description": "Specific session ID to test (optional)"
    },
    "include_buffer_status": {
      "type": "boolean",
      "description": "Whether to include request buffer status",
      "default": true
    },
    "include_reconnection_stats": {
      "type": "boolean",
      "description": "Whether to include reconnection statistics",
      "default": true
    }
  },
  "required": []
}
```

#### Response Schema

```json
{
  "type": "object",
  "properties": {
    "test_completed": {
      "type": "boolean",
      "description": "Whether the test completed successfully"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "overall_status": {
      "type": "string",
      "enum": ["pass", "fail", "partial"]
    },
    "results": {
      "type": "object",
      "properties": {
        "session_test": {
          "type": "object",
          "properties": {
            "session_id": {"type": "string"},
            "reachable": {"type": "boolean"},
            "reconnect_capable": {"type": "boolean"},
            "status": {"type": "string"}
          }
        },
        "all_sessions": {
          "type": "object",
          "properties": {
            "total_sessions": {"type": "integer"},
            "reachable_sessions": {"type": "integer"},
            "reconnect_capable": {"type": "integer"},
            "status": {"type": "string"}
          }
        },
        "buffer_status": {
          "type": "object",
          "properties": {
            "total_buffered_requests": {"type": "integer"},
            "sessions_with_buffers": {"type": "integer"},
            "status": {"type": "string"}
          }
        },
        "reconnection_stats": {
          "type": "object",
          "properties": {
            "successful_reconnections": {"type": "integer"},
            "failed_reconnections": {"type": "integer"},
            "average_reconnection_time": {"type": "number"},
            "status": {"type": "string"}
          }
        }
      }
    }
  },
  "required": ["test_completed", "timestamp", "overall_status"]
}
```

## Error Handling

### Error Response Format

All tools follow consistent error response formatting:

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"success\": false, \"error\": \"Error description\", \"phase\": \"error_phase\", \"timestamp\": \"2025-06-06T12:00:00Z\"}"
    }
  ]
}
```

### Common Error Codes

- **INITIALIZATION_FAILED**: Reboot manager not properly initialized
- **SHUTDOWN_IN_PROGRESS**: Restart already in progress
- **INVALID_PARAMETERS**: Invalid or out-of-range parameters
- **SYSTEM_NOT_READY**: System not ready for requested operation
- **TIMEOUT_EXCEEDED**: Operation exceeded specified timeout
- **STATE_CORRUPTION**: Server state corrupted or invalid
- **PROCESS_FAILED**: Process management operation failed

### Error Recovery

When tools return errors:

1. **Check System Health**: Use `orchestrator_health_check` to identify issues
2. **Verify Readiness**: Use `orchestrator_shutdown_prepare` to check blocking conditions
3. **Monitor Status**: Use `orchestrator_restart_status` to track ongoing operations
4. **Retry Logic**: Implement exponential backoff for transient errors
5. **Fallback Procedures**: Use emergency restart if graceful restart fails

## Integration Patterns

### Async/Await Pattern

```python
async def restart_with_monitoring():
    # Check health first
    health = await orchestrator_health_check()
    if not health['healthy']:
        raise Exception("System not healthy")
    
    # Trigger restart
    result = await orchestrator_restart_server({
        "reason": "configuration_update"
    })
    
    if not result['success']:
        raise Exception(f"Restart failed: {result.get('error', 'Unknown error')}")
    
    # Monitor until complete
    while result['phase'] != 'complete':
        await asyncio.sleep(1)
        status = await orchestrator_restart_status()
        result = status['current_status']
        
        if result['phase'] == 'failed':
            raise Exception("Restart failed during execution")
    
    return result
```

### Error Handling Pattern

```python
async def safe_restart():
    try:
        # Attempt graceful restart
        result = await orchestrator_restart_server()
        return result
        
    except Exception as e:
        # Log error and attempt emergency restart
        logger.error(f"Graceful restart failed: {e}")
        
        emergency_result = await orchestrator_restart_server({
            "graceful": false,
            "preserve_state": false,
            "reason": "emergency_shutdown"
        })
        
        return emergency_result
```

### Client Integration Pattern

```javascript
// JavaScript/TypeScript client integration
class RebootManager {
    async restartServer(options = {}) {
        const params = {
            name: 'orchestrator_restart_server',
            arguments: options
        };
        
        const response = await this.mcp.call('tools/call', params);
        const result = JSON.parse(response.content[0].text);
        
        if (!result.success) {
            throw new Error(`Restart failed: ${result.error}`);
        }
        
        return result;
    }
    
    async waitForRestart(timeout = 60000) {
        const start = Date.now();
        
        while (Date.now() - start < timeout) {
            try {
                const health = await this.healthCheck();
                if (health.healthy) return true;
            } catch (e) {
                // Server still restarting
            }
            
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        throw new Error('Restart timeout exceeded');
    }
}
```

## Rate Limiting and Throttling

### Request Limits

- **Health Checks**: No limit (monitoring operations)
- **Restart Operations**: 1 per minute per client
- **Status Queries**: 10 per minute per client
- **Reconnection Tests**: 5 per minute per client

### Throttling Behavior

When rate limits are exceeded:
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "retry_after": 60,
  "phase": "rate_limited"
}
```

## Versioning and Compatibility

### API Version

Current API version: `1.0`

### Backward Compatibility

- All parameters are optional with sensible defaults
- Response format is stable with additive changes only  
- New fields may be added to responses
- Deprecated fields will be supported for 2 major versions

### Version Detection

```python
# Check server version
health = await orchestrator_health_check()
server_version = health['server_version']  # e.g., "1.4.1"
```

---

*This API reference covers version 1.4.1 of the MCP Task Orchestrator. For the latest updates and examples, see the project repository.*