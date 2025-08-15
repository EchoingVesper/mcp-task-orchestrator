---
feature_id: "ENHANCED_SESSION_STATE_MANAGEMENT"
version: "1.0.0"
status: "Research"
priority: "Critical"
category: "Core"
dependencies: ["ENHANCED_SESSION_MANAGEMENT_V1"]
size_lines: 195
last_updated: "2025-07-08"
validation_status: "pending"
cross_references:
  - "docs/developers/planning/features/research/enhanced-session-management/README.md"
  - "docs/developers/planning/features/research/enhanced-session-management/database-design.md"
module_type: "specification"
modularized_from: "docs/developers/planning/features/research/[CRITICAL]_enhanced_session_management_architecture.md"
---

# Session State Machine

This document specifies the session lifecycle states, transitions, and management architecture.

#
# Session Lifecycle States

The session state machine implements a formal lifecycle with defined states and controlled transitions.

```python
class SessionState(Enum):
    CREATING = "creating"      
# Session being initialized
    ACTIVE = "active"         
# Currently active session (only one allowed)
    PAUSED = "paused"         
# Temporarily inactive but resumable
    COMPLETED = "completed"   
# All tasks finished successfully
    ARCHIVED = "archived"     
# Moved to long-term storage
    CANCELLED = "cancelled"   
# Terminated before completion
    ERROR = "error"          
# Failed state requiring intervention

class SessionStateTransitions:
    ALLOWED_TRANSITIONS = {
        SessionState.CREATING: [SessionState.ACTIVE, SessionState.CANCELLED],
        SessionState.ACTIVE: [SessionState.PAUSED, SessionState.COMPLETED, SessionState.CANCELLED],
        SessionState.PAUSED: [SessionState.ACTIVE, SessionState.ARCHIVED, SessionState.CANCELLED],
        SessionState.COMPLETED: [SessionState.ARCHIVED],
        SessionState.ARCHIVED: [SessionState.ACTIVE],  
# Can reactivate archived sessions
        SessionState.CANCELLED: [SessionState.ARCHIVED],
        SessionState.ERROR: [SessionState.ACTIVE, SessionState.CANCELLED]  
# Recovery paths
    }

```text

#
# State Descriptions

#
## CREATING

- **Purpose**: Initial state during session initialization

- **Duration**: Temporary (seconds to minutes)

- **Valid Transitions**: ACTIVE (successful creation), CANCELLED (creation failed)

- **Constraints**: No tasks can be created in this state

#
## ACTIVE

- **Purpose**: Session is currently active and accepting operations

- **Duration**: Variable (hours to weeks)

- **Constraints**: Only one session can be ACTIVE at any time

- **Valid Transitions**: PAUSED (temporary deactivation), COMPLETED (all tasks done), CANCELLED (user termination)

#
## PAUSED

- **Purpose**: Session temporarily inactive but resumable

- **Duration**: Variable (minutes to months)

- **Valid Transitions**: ACTIVE (resume), ARCHIVED (long-term storage), CANCELLED (termination)

- **Use Cases**: Switching between projects, vacation, waiting for dependencies

#
## COMPLETED

- **Purpose**: All session tasks finished successfully

- **Duration**: Permanent (until archived)

- **Valid Transitions**: ARCHIVED (move to long-term storage)

- **Constraints**: No new tasks can be added

#
## ARCHIVED

- **Purpose**: Long-term storage state for completed or cancelled sessions

- **Duration**: Permanent (until deletion)

- **Valid Transitions**: ACTIVE (reactivate for reference or extension)

- **Constraints**: Read-only access, can be reactivated if needed

#
## CANCELLED

- **Purpose**: Session terminated before completion

- **Duration**: Permanent (until archived)

- **Valid Transitions**: ARCHIVED (move to storage)

- **Use Cases**: Project cancellation, major scope changes, abandonment

#
## ERROR

- **Purpose**: Session in failed state requiring intervention

- **Duration**: Until resolved

- **Valid Transitions**: ACTIVE (after error resolution), CANCELLED (abandon)

- **Triggers**: File system corruption, database inconsistency, validation failures

#
# Session Manager Architecture

Core session management implementation with lifecycle enforcement.

```text
python
class SessionManager:
    def __init__(self, db_manager, file_system_manager, mode_manager):
        self.db = db_manager
        self.fs = file_system_manager
        self.mode_manager = mode_manager
        self.active_session_cache = None
    
    async def create_session(self, name: str, description: str, 
                           project_root: str, mode_file: str = None) -> Session:
        """Create new session with automatic directory setup."""
        
        
# Validate only one active session
        if await self.get_active_session():
            raise ActiveSessionExistsError("Cannot create session while another is active")
        
        
# Create session entity
        session = Session(
            session_id=generate_session_id(),
            name=name,
            description=description,
            project_root_path=project_root,
            mode_file=mode_file or "default_roles.yaml",
            status=SessionState.CREATING
        )
        
        
# Setup file system structure
        await self.setup_session_directory(session)
        
        
# Initialize markdown file
        await self.create_session_markdown(session)
        
        
# Bind to mode
        if mode_file:
            await self.mode_manager.bind_session_to_mode(session.session_id, mode_file)
        
        
# Save to database
        await self.db.save_session(session)
        
        
# Activate immediately
        await self.activate_session(session.session_id)
        
        return session
    
    async def activate_session(self, session_id: str) -> Session:
        """Activate session as the single active session."""
        
        
# Deactivate current active session
        current_active = await self.get_active_session()
        if current_active and current_active.session_id != session_id:
            await self.pause_session(current_active.session_id)
        
        
# Activate new session
        session = await self.db.get_session(session_id)
        if not session:
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        
# Validate session can be activated
        if session.status not in [SessionState.CREATING, SessionState.PAUSED, SessionState.ARCHIVED]:
            raise InvalidSessionStateError(f"Cannot activate session in state {session.status}")
        
        
# Update session state
        session.status = SessionState.ACTIVE
        session.activated_at = datetime.utcnow()
        session.last_activity_at = datetime.utcnow()
        
        
# Set as active session
        await self.db.set_active_session(session_id, self.build_session_context(session))
        
        
# Update cache
        self.active_session_cache = session
        
        
# Initialize session context
        await self.initialize_session_context(session)
        
        return session

```text

#
# Directory Setup Architecture

Automated file system structure creation for session isolation.

```text
python
async def setup_session_directory(self, session: Session):
    """Create .task_orchestrator directory structure for session."""
    
    session_dir = Path(session.project_root_path) / ".task_orchestrator"
    
    
# Create directory structure
    directories = [
        session_dir,
        session_dir / "sessions",
        session_dir / "roles",
        session_dir / "tasks",
        session_dir / "archives",
        session_dir / "exports"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    
# Copy default roles if roles directory is empty
    roles_dir = session_dir / "roles"
    if not any(roles_dir.glob("*.yaml")):
        await self.copy_default_roles(roles_dir)
    
    
# Create session-specific subdirectories
    session_subdir = session_dir / "sessions" / session.session_id
    session_subdir.mkdir(exist_ok=True)
    
    
# Update session with directory paths
    session.markdown_file_path = str(session_subdir / "session.md")

async def copy_default_roles(self, target_dir: Path):
    """Copy default role configurations to session directory."""
    
    
# Source: project config directory
    config_dir = Path(__file__).parent.parent.parent / "config"
    default_roles_file = config_dir / "default_roles.yaml"
    
    if default_roles_file.exists():
        target_file = target_dir / "default_roles.yaml"
        shutil.copy2(default_roles_file, target_file)
    
    
# Also copy any other .yaml files from config
    for yaml_file in config_dir.glob("*.yaml"):
        if yaml_file.name != "default_roles.yaml":
            target_file = target_dir / yaml_file.name
            shutil.copy2(yaml_file, target_file)
```text

#
# State Transition Rules

#
## Transition Validation

- All state transitions must be validated against `ALLOWED_TRANSITIONS`

- Invalid transitions raise `InvalidSessionStateError`

- State changes are atomic with database rollback on failure

#
## Single Active Session Constraint

- System enforces exactly one ACTIVE session at any time

- Activating a session automatically pauses the current active session

- Active session constraint prevents resource conflicts and context confusion

#
## Error Recovery

- ERROR state allows recovery paths to ACTIVE or CANCELLED

- Recovery procedures include file system validation and data consistency checks

- Manual intervention may be required for complex error states

#
# Integration Points

- **Database Layer**: Session state persistence and constraint enforcement

- **File System**: Directory creation and role configuration deployment

- **Mode Manager**: Session-mode binding and role configuration

- **Task Manager**: Session context for all task operations

- **MCP Tools**: Session-aware tool routing and validation
