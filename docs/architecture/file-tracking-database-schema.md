# File Tracking Database Schema

*Database design for file operation tracking and verification*

## Core Tables

### File Operations Tracking
```sql
CREATE TABLE file_operations (
    operation_id VARCHAR(36) PRIMARY KEY,
    subtask_id VARCHAR(36) NOT NULL,
    session_id VARCHAR(36) NOT NULL,
    operation_type VARCHAR(20) NOT NULL,
    file_path TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    content_hash VARCHAR(64),
    file_size INTEGER,
    metadata JSON,
    verification_status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subtask_id) REFERENCES subtasks(task_id)
);
```

### Verification Results
```sql
CREATE TABLE file_verifications (
    verification_id VARCHAR(36) PRIMARY KEY,
    operation_id VARCHAR(36) NOT NULL,
    verification_timestamp DATETIME NOT NULL,
    file_exists BOOLEAN NOT NULL,
    content_matches BOOLEAN,
    size_matches BOOLEAN,
    permissions_correct BOOLEAN,
    verification_status VARCHAR(20) NOT NULL,
    errors JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES file_operations(operation_id)
);
```

### Enhanced Subtasks Table
```sql
ALTER TABLE subtasks ADD COLUMN file_operations_count INTEGER DEFAULT 0;
ALTER TABLE subtasks ADD COLUMN verification_status VARCHAR(20) DEFAULT 'pending';
```

## Implementation Priority

**Phase 1**: Core tracking and verification
**Phase 2**: Context recovery system  
**Phase 3**: Integration with existing orchestrator

**Status**: ARCHITECTURE COMPLETE - READY FOR IMPLEMENTATION