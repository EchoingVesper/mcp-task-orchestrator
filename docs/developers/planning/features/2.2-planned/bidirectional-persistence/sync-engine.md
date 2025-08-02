---
feature_id: "BIDIRECTIONAL_PERSISTENCE_SYNC_ENGINE"
version: "2.0.0"
status: "Planned"
priority: "High"
category: "Infrastructure"
dependencies: ["BIDIRECTIONAL_PERSISTENCE_V2"]
size_lines: 495
last_updated: "2025-07-08"
validation_status: "pending"
cross_references:
  - "docs/developers/planning/features/2.2-planned/bidirectional-persistence/README.md"
  - "docs/developers/planning/features/2.2-planned/bidirectional-persistence/file-organization.md"
module_type: "implementation"
modularized_from: "docs/developers/planning/features/2.2-planned/[PLANNED]_bidirectional_persistence_system.md"
---

# Bi-directional Sync Engine

This document specifies the implementation of the bi-directional synchronization engine that maintains consistency between database and markdown files.

#
# File Change Detection

The sync engine monitors markdown files for changes and triggers synchronization processes.

```python
class MarkdownChangeDetector:
    def __init__(self, session_manager, db_manager):
        self.session_manager = session_manager
        self.db = db_manager
        self.file_watchers = {}
        self.change_queue = asyncio.Queue()
        
    async def monitor_session_files(self, session_id: str):
        """Monitor all markdown files for a session."""
        
        session = await self.session_manager.get_session(session_id)
        session_dir = Path(session.project_root_path) / ".task_orchestrator" / "sessions" / session_id
        
        
# Set up file system watcher
        observer = Observer()
        event_handler = MarkdownFileHandler(self.change_queue, session_id)
        observer.schedule(event_handler, str(session_dir), recursive=True)
        observer.start()
        
        self.file_watchers[session_id] = observer
        
        
# Start change processing loop
        await self.process_change_queue()
    
    async def process_change_queue(self):
        """Process detected file changes."""
        
        while True:
            try:
                change_event = await asyncio.wait_for(self.change_queue.get(), timeout=1.0)
                await self.handle_file_change(change_event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.log_error(f"Error processing file change: {e}")

class MarkdownFileHandler(FileSystemEventHandler):
    def __init__(self, change_queue, session_id):
        self.change_queue = change_queue
        self.session_id = session_id
        self.debounce_timers = {}
        
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
            
        
# Debounce rapid file changes
        file_path = event.src_path
        if file_path in self.debounce_timers:
            self.debounce_timers[file_path].cancel()
        
        self.debounce_timers[file_path] = asyncio.create_task(
            self.schedule_change_processing(file_path)
        )
    
    async def schedule_change_processing(self, file_path: str):
        """Schedule change processing with debouncing."""
        
        
# Wait for file operations to complete
        await asyncio.sleep(0.5)
        
        change_event = FileChangeEvent(
            session_id=self.session_id,
            file_path=file_path,
            change_type="modified",
            detected_at=datetime.utcnow()
        )
        
        await self.change_queue.put(change_event)

```text

#
## Change Detection Features

- **Debounced Processing**: Prevents excessive processing during rapid file changes

- **Selective Monitoring**: Only monitors `.md` files in session directories

- **Asynchronous Queue**: Non-blocking change processing

- **Error Recovery**: Graceful handling of file system errors

#
# User Edit Processing

The edit processor analyzes markdown changes and determines database updates needed.

```text
python
class UserEditProcessor:
    def __init__(self, db_manager, conflict_resolver):
        self.db = db_manager
        self.conflict_resolver = conflict_resolver
        
    async def process_file_changes(self, change_event: FileChangeEvent):
        """Process user edits to markdown files."""
        
        try:
            
# Read current file content
            file_content = await self.read_file_content(change_event.file_path)
            
            
# Parse markdown structure
            parsed_content = self.parse_markdown_content(file_content)
            
            
# Detect what changed compared to database
            changes = await self.detect_changes(change_event.session_id, parsed_content)
            
            
# Check for conflicts with concurrent database changes
            conflicts = await self.detect_conflicts(changes)
            
            if conflicts:
                await self.handle_conflicts(conflicts, change_event)
            else:
                await self.apply_changes_to_database(changes)
                await self.update_sync_status(change_event)
                
        except Exception as e:
            await self.handle_processing_error(change_event, e)
    
    def parse_markdown_content(self, content: str) -> ParsedMarkdown:
        """Parse markdown content to extract structured data."""
        
        parser = MarkdownStructureParser()
        
        
# Extract metadata from frontmatter or structured sections
        metadata = parser.extract_metadata(content)
        
        
# Parse task status changes (checkbox changes)
        task_changes = parser.extract_task_status_changes(content)
        
        
# Parse progress updates
        progress_changes = parser.extract_progress_changes(content)
        
        
# Parse user notes and additions
        user_content = parser.extract_user_content(content)
        
        
# Parse structural changes (new tasks, groups, etc.)
        structural_changes = parser.extract_structural_changes(content)
        
        return ParsedMarkdown(
            metadata=metadata,
            task_changes=task_changes,
            progress_changes=progress_changes,
            user_content=user_content,
            structural_changes=structural_changes,
            raw_content=content
        )
    
    async def detect_changes(self, session_id: str, parsed_content: ParsedMarkdown) -> List[Change]:
        """Detect what changed compared to database state."""
        
        changes = []
        
        
# Get current database state
        current_state = await self.get_current_database_state(session_id)
        
        
# Compare task statuses
        for task_id, new_status in parsed_content.task_changes.items():
            current_status = current_state.get_task_status(task_id)
            if current_status != new_status:
                changes.append(TaskStatusChange(
                    task_id=task_id,
                    old_status=current_status,
                    new_status=new_status,
                    source="user_edit"
                ))
        
        
# Compare progress values
        for entity_id, new_progress in parsed_content.progress_changes.items():
            current_progress = current_state.get_progress(entity_id)
            if abs(current_progress - new_progress) > 0.01:  
# Allow for small rounding differences
                changes.append(ProgressChange(
                    entity_id=entity_id,
                    old_progress=current_progress,
                    new_progress=new_progress,
                    source="user_edit"
                ))
        
        
# Detect new user content
        for section, content in parsed_content.user_content.items():
            if section in ["insights", "decisions", "notes", "learnings"]:
                current_content = current_state.get_user_content(section)
                if content != current_content:
                    changes.append(UserContentChange(
                        section=section,
                        old_content=current_content,
                        new_content=content,
                        source="user_edit"
                    ))
        
        return changes

```text

#
## Parsing Capabilities

- **Task Status Detection**: Identifies checkbox state changes (completed/incomplete)

- **Progress Tracking**: Extracts progress percentages from tables and text

- **User Content**: Identifies user-editable sections with new content

- **Structural Changes**: Detects new tasks, groups, or organizational changes

- **Metadata Extraction**: Reads YAML frontmatter and structured metadata

#
# Conflict Resolution System

The conflict resolution engine handles concurrent changes to database and files.

```text
python
class ConflictResolutionEngine:
    def __init__(self, backup_manager):
        self.backup_manager = backup_manager
        
    async def handle_conflicts(self, conflicts: List[Conflict], change_event: FileChangeEvent):
        """Handle sync conflicts between database and file changes."""
        
        conflict_resolution_dir = self.create_conflict_workspace(change_event.session_id)
        
        for conflict in conflicts:
            resolution_strategy = await self.determine_resolution_strategy(conflict)
            
            if resolution_strategy == "auto_merge":
                await self.auto_merge_conflict(conflict)
            elif resolution_strategy == "user_choice":
                await self.present_conflict_to_user(conflict, conflict_resolution_dir)
            elif resolution_strategy == "database_wins":
                await self.resolve_with_database_version(conflict)
            elif resolution_strategy == "file_wins":
                await self.resolve_with_file_version(conflict)
            else:
                await self.create_manual_resolution_task(conflict)
    
    async def determine_resolution_strategy(self, conflict: Conflict) -> str:
        """Determine the best strategy for resolving a conflict."""
        
        
# Simple changes (progress, status) can often be auto-merged
        if conflict.type in ["task_status", "progress_update"]:
            if conflict.database_timestamp - conflict.file_timestamp < timedelta(minutes=5):
                return "auto_merge"
        
        
# User content changes typically favor the file version
        if conflict.type == "user_content":
            return "file_wins"
        
        
# Structural changes require user decision
        if conflict.type == "structural_change":
            return "user_choice"
        
        
# Default to presenting choice to user
        return "user_choice"

```text

#
## Resolution Strategies

#
### Automatic Merge

- **Applicable**: Simple status and progress changes

- **Conditions**: Recent changes (within 5 minutes)

- **Process**: Intelligently merge non-conflicting changes

- **Fallback**: User choice if merge fails

#
### Database Wins

- **Applicable**: System-generated updates take precedence

- **Use Cases**: Automated task completion, system calculations

- **Process**: Regenerate markdown file from database state

- **Backup**: Save user version before overwriting

#
### File Wins

- **Applicable**: User content and manual edits

- **Use Cases**: Notes, decisions, insights, manual progress updates

- **Process**: Update database with file content

- **Validation**: Ensure data integrity before applying

#
### User Choice

- **Applicable**: Complex conflicts requiring human judgment

- **Interface**: Present both versions with diff visualization

- **Options**: Database version, file version, or manual merge

- **Workflow**: Guide user through resolution process

#
# Sync Conflict Resolution Interface

When conflicts require user intervention, the system presents a clear resolution interface:

```text
markdown

# 🔄 Sync Conflict Resolution

#
# 📊 Conflict Details

**File**: `task_groups/frontend.md`
**Section**: Task progress updates
**Conflict Type**: Progress percentage mismatch
**Detected**: 2025-06-01 16:45:23

#
# 🔀 Choose Resolution

#
## Option 1: Keep Database Version

```text
**Progress**: 45% (database calculation)
**Last Updated**: 2025-06-01 16:44:15 (system)

```text

#
## Option 2: Keep File Version  

```text

**Progress**: 50% (user estimate)
**Last Updated**: 2025-06-01 16:45:20 (user edit)

```text

#
## Option 3: Manual Merge

Edit the content below to create your preferred version:
```text

**Progress**: [Enter your value]% 
**Note**: [Add explanation if needed]

```text

#
# 📝 Resolution Instructions

1. Choose your preferred option above

2. Click "Apply Resolution" to update both database and file

3. The system will monitor for successful synchronization

4. A backup of both versions is saved in `sync/backup_metadata/`

---
**Resolution Status**: Waiting for user input
```text

#
## Conflict Prevention

- **Timestamp Tracking**: Monitor when files and database were last modified

- **Change Validation**: Verify changes don't conflict before applying

- **Lock Mechanisms**: Prevent simultaneous modifications during sync

- **Backup Creation**: Always backup before applying changes

#
## Performance Optimization

- **Selective Parsing**: Only parse sections that may have changed

- **Caching**: Cache parsed content for repeated access

- **Batch Processing**: Group related changes for efficient processing

- **Async Operations**: Non-blocking file I/O and database operations

#
# Error Handling

#
## File System Errors

- **Permission Issues**: Graceful degradation with user notification

- **File Corruption**: Restore from backup and log incident

- **Disk Space**: Monitor available space and warn before critical levels

- **Network Drives**: Handle network interruptions and reconnection

#
## Parsing Errors

- **Malformed Markdown**: Attempt recovery and report specific issues

- **Invalid Data**: Validate extracted data before database operations

- **Encoding Issues**: Handle various text encodings gracefully

- **Large Files**: Implement streaming for very large markdown files

#
## Database Errors

- **Connection Failures**: Implement retry logic with exponential backoff

- **Transaction Conflicts**: Retry with optimistic locking

- **Constraint Violations**: Validate data before committing changes

- **Recovery Procedures**: Rollback mechanisms for failed transactions

#
# Monitoring and Diagnostics

#
## Sync Status Tracking

```text
python
class SyncStatusTracker:
    def track_sync_operation(self, operation_type: str, session_id: str):
        """Track sync operation for monitoring and debugging."""
        
        return SyncOperation(
            operation_id=generate_operation_id(),
            operation_type=operation_type,
            session_id=session_id,
            started_at=datetime.utcnow(),
            status="in_progress"
        )
    
    async def record_sync_success(self, operation: SyncOperation):
        """Record successful sync operation."""
        
        operation.completed_at = datetime.utcnow()
        operation.status = "completed"
        await self.update_operation_status(operation)
    
    async def record_sync_failure(self, operation: SyncOperation, error: Exception):
        """Record failed sync operation with error details."""
        
        operation.failed_at = datetime.utcnow()
        operation.status = "failed"
        operation.error_message = str(error)
        operation.error_details = traceback.format_exc()
        await self.update_operation_status(operation)
```text

#
## Health Metrics

- **Sync Success Rate**: Percentage of successful synchronizations

- **Conflict Rate**: Percentage of changes requiring conflict resolution

- **Processing Time**: Average time for sync operations

- **Error Frequency**: Rate of various error types

- **User Resolution Rate**: How often users successfully resolve conflicts

This sync engine provides reliable, efficient bi-directional synchronization while maintaining data integrity and providing excellent user experience for conflict resolution.
