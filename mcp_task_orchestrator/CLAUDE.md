# Core Implementation - Claude Code Guide

Core implementation guidance for the MCP Task Orchestrator's main Python package.

## Core Architecture

**Orchestration Engine**: Core MCP server with SQLite persistence, async operations, and enhanced features.

### Package Structure
- `orchestrator/` - Core orchestration logic and state management
- `db/` - Database persistence layer with SQLAlchemy ORM
- `testing/` - Enhanced testing infrastructure
- `monitoring/` - Diagnostics and health monitoring
- `config/` - Configuration management

## Development Commands

### Core Implementation Development
```bash
# Run the MCP server
python -m mcp_task_orchestrator.server

# Alternative server launch
python server.py

# Enhanced handlers testing
python -c "from enhanced_handlers import *; test_handlers()"

# Database persistence validation
python -c "from persistence import *; validate_persistence()"
```

### Database Operations
```bash
# Test database connectivity
python -c "from db.persistence import get_db_connection; get_db_connection()"

# Schema validation
python -c "from db.models import *; validate_schema()"

# SQLAlchemy ORM testing
python -c "from sqlalchemy import create_engine; engine = create_engine('sqlite:///task_orchestrator.db')"
```

## Core Development Patterns

### Async Safety Guidelines
- **Database Operations**: Use async-safe contexts with proper timeout handling
- **Connection Management**: Leverage connection pooling and health checks
- **Error Recovery**: Implement retry mechanisms with exponential backoff
- **Resource Cleanup**: Ensure proper disposal of connections and resources

### MCP Protocol Implementation
```python
# Server initialization pattern
from mcp.server import Server
from mcp.types import Tool

# Enhanced handlers integration
from enhanced_handlers import register_enhanced_tools

server = Server("task-orchestrator")
register_enhanced_tools(server)
```

### Database Persistence Patterns
```python
# Managed connection pattern
from db.persistence import get_managed_connection

async with get_managed_connection() as conn:
    # Database operations with automatic cleanup
    result = await conn.execute(query)
    
# SQLAlchemy ORM pattern
from db.models import TaskBreakdown, Subtask
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
with Session() as session:
    task = session.query(TaskBreakdown).filter_by(id=task_id).first()
```

### Orchestration Logic Patterns
```python
# Specialist assignment pattern
from orchestrator.specialists import get_specialist_context

specialist_context = get_specialist_context(
    specialist_type="implementer",
    task_description="Create new feature"
)

# State management pattern
from orchestrator.state import StateManager

state_manager = StateManager()
await state_manager.create_task_breakdown(description, subtasks)
```

### Error Handling and Recovery
- **Timeout Management**: All async operations include appropriate timeouts
- **Graceful Degradation**: Fallback mechanisms for service failures
- **State Recovery**: Ability to resume interrupted operations
- **Logging**: Comprehensive error tracking and diagnostics

### Integration with Enhanced Features
- **Artifact Storage**: Leverage artifact system for complex operations
- **Maintenance Coordination**: Use maintenance tools for lifecycle management
- **Testing Infrastructure**: Integrate with enhanced testing patterns

---

**Core Implementation**: This directory contains the main orchestration engine. Follow async safety patterns and use proper resource management.
