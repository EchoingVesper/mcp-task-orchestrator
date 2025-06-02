# 📄 Bi-directional Persistence System Specification

**Feature ID**: `BIDIRECTIONAL_PERSISTENCE_V2`  
**Priority**: HIGH ⭐ - Human-readable project organization  
**Category**: Core Infrastructure  
**Estimated Effort**: 2-3 weeks  
**Created**: 2025-06-01  
**Status**: [RESEARCH] - Comprehensive specification for dual persistence  

---

## 📋 Overview

The Bi-directional Persistence System enables the MCP Task Orchestrator to maintain data in both a high-performance database and human-readable markdown files. This dual approach provides the performance benefits of structured data while ensuring project information remains accessible, editable, and version-control friendly.

## 🎯 Key Benefits

### For Humans
- **Readable Project State**: Complete project overview in markdown format
- **Direct Editing**: Modify tasks, notes, and plans directly in text files
- **Version Control**: Track project evolution with Git
- **Backup Transparency**: Human-readable backups that don't require special tools
- **Collaboration**: Share project state without requiring orchestrator access

### For Systems
- **Performance**: Fast queries and updates through database operations
- **Consistency**: ACID compliance for critical operations
- **Scalability**: Efficient handling of large projects
- **Integration**: API access to structured data
- **Automation**: Programmatic manipulation of project data

## 🏗️ Architecture Overview

### Dual Persistence Model
```
User Edits ────→ Markdown Files ────→ Sync Engine ────→ Database
    ↑                   ↑                  ↑              ↓
    │                   │                  │              │
    │                   │                  │              ▼
    │                   │                  │        MCP Tools
    │                   │                  │              ↓
    │                   │                  │              ▼
    └────── Change Detection ←───── File Monitor ←─── Auto-Generation
```

### Core Components
```
Bi-directional Persistence System
├── Markdown Generation Engine (Database → Files)
├── Change Detection System (Monitor file modifications)  
├── User Edit Parser (Files → Database)
├── Conflict Resolution Engine (Handle sync conflicts)
├── Template System (Consistent file structure)
├── Backup Integration (Include markdown in backups)
└── Version Control Support (Git-friendly operations)
```

---

## 📁 File Structure and Organization

### Session Directory Layout
```
project_root/
├── .task_orchestrator/
│   ├── sessions/
│   │   └── [session_id]/
│   │       ├── session.md                 # Main session overview
│   │       ├── task_groups/
│   │       │   ├── frontend.md           # Task group details
│   │       │   ├── backend.md
│   │       │   └── testing.md
│   │       ├── tasks/
│   │       │   ├── completed/            # Completed tasks archive
│   │       │   ├── active/               # Current active tasks
│   │       │   └── planned/              # Future planned tasks
│   │       ├── notes/
│   │       │   ├── decisions.md          # Project decisions log
│   │       │   ├── learnings.md          # Key insights and lessons
│   │       │   └── resources.md          # Important links and references
│   │       └── meta/
│   │           ├── sync_status.md        # Sync state information
│   │           └── edit_log.md           # History of user edits
│   ├── templates/                        # Markdown templates
│   │   ├── session_template.md
│   │   ├── task_group_template.md
│   │   └── task_template.md
│   └── sync/
│       ├── conflict_resolution/          # Conflict resolution workspace
│       ├── pending_changes/              # Changes awaiting sync
│       └── backup_metadata/              # Sync state backups
```

## 📝 Markdown File Formats

### Session Overview (session.md)
```markdown
# 🚀 Project: Advanced Analytics Dashboard

**Session ID**: `session_abc123`  
**Status**: Active  
**Mode**: `development_roles.yaml`  
**Created**: 2025-06-01 14:30:00  
**Last Updated**: 2025-06-01 16:45:00  
**Progress**: 34% (12/35 tasks completed)

## 📊 Session Metrics

| Metric | Value | Target |
|--------|-------|--------|
| **Total Tasks** | 35 | 35 |
| **Completed** | 12 (34%) | 35 (100%) |
| **In Progress** | 8 | - |
| **Planned** | 15 | - |
| **Estimated Hours** | 120h | 120h |
| **Actual Hours** | 38h | 120h |
| **Efficiency** | 95% | 90% |

## 🎯 Task Groups Overview

### [Frontend Development](task_groups/frontend.md) ⚡ Active
- **Progress**: 45% (5/11 tasks)
- **Specialist**: implementer, reviewer
- **Priority**: High
- **Estimated**: 40h | **Actual**: 18h

### [Backend API](task_groups/backend.md) 🔄 Active  
- **Progress**: 25% (3/12 tasks)
- **Specialist**: architect, implementer
- **Priority**: High
- **Estimated**: 50h | **Actual**: 15h

### [Testing & QA](task_groups/testing.md) ⏳ Planned
- **Progress**: 0% (0/8 tasks)
- **Specialist**: tester, reviewer
- **Priority**: Medium
- **Estimated**: 20h | **Actual**: 0h

### [Documentation](task_groups/documentation.md) 📚 Planned
- **Progress**: 25% (1/4 tasks)
- **Specialist**: documenter
- **Priority**: Low
- **Estimated**: 10h | **Actual**: 5h

## 📝 Recent Activity

### Last 7 Days
- ✅ **2025-06-01**: Completed user authentication system (frontend group)
- ✅ **2025-05-31**: Database schema design finalized (backend group)
- ✅ **2025-05-30**: Project setup and initial architecture (backend group)
- 🔄 **2025-05-30**: Started API endpoint development (backend group)

### Next Steps
- 🎯 Complete user dashboard components (frontend group)
- 🎯 Implement authentication API endpoints (backend group)
- 📋 Begin integration testing setup (testing group)

## 💡 Key Insights

### Decisions Made
- **Architecture**: Chose React + FastAPI for better type safety
- **Database**: PostgreSQL selected over MongoDB for complex queries
- **Authentication**: JWT tokens with refresh token rotation

### Lessons Learned
- Component testing should start earlier in development cycle
- API design reviews save significant refactoring time
- Regular progress reviews help maintain momentum

### Risks & Mitigation
- **Risk**: Database performance with large datasets
  - **Mitigation**: Implement pagination and indexing strategy
- **Risk**: Frontend state management complexity
  - **Mitigation**: Use Redux Toolkit for predictable state updates

## 🔗 Quick Links

- [Project Repository](https://github.com/company/analytics-dashboard)
- [Design Mockups](https://figma.com/project/analytics-ui)
- [API Documentation](./notes/api_documentation.md)
- [Meeting Notes](./notes/team_meetings.md)

---

**📄 File Info**  
- **Auto-sync**: Enabled ✅
- **Last DB Sync**: 2025-06-01 16:45:00  
- **Edit Status**: Synchronized  
- **Backup**: Included in session backups

---
<!-- 
EDITING INSTRUCTIONS:
- ✅ Safe to edit: Progress notes, insights, decisions, links
- ⚠️  Sync required: Task status changes, progress percentages  
- ❌ Don't edit: Session ID, creation date, auto-generated metrics
- 💡 Tip: Add content in "Notes" sections - they sync automatically!
-->
```

### Task Group File (task_groups/frontend.md)
```markdown
# 🎨 Frontend Development Task Group

**Group ID**: `group_frontend_001`  
**Session**: Advanced Analytics Dashboard  
**Status**: Active  
**Specialist Focus**: implementer, reviewer  
**Priority**: High (2/5)  
**Progress**: 45% (5/11 tasks completed)

## 📊 Group Metrics

| Metric | Value |
|--------|-------|
| **Total Tasks** | 11 |
| **Completed** | 5 (45%) |
| **In Progress** | 3 |
| **Planned** | 3 |
| **Estimated Hours** | 40h |
| **Actual Hours** | 18h |
| **Efficiency** | 110% |

## ✅ Completed Tasks

### ✅ User Authentication Components
- **Completed**: 2025-06-01 14:30
- **Specialist**: implementer  
- **Effort**: 6h (estimated: 5h)
- **Artifacts**: LoginForm.tsx, AuthContext.tsx, auth.test.tsx
- **Notes**: Implemented with form validation and error handling

### ✅ Navigation Layout
- **Completed**: 2025-05-31 16:00  
- **Specialist**: implementer
- **Effort**: 4h (estimated: 4h)
- **Artifacts**: NavBar.tsx, Sidebar.tsx, Layout.tsx
- **Notes**: Responsive design with mobile breakpoints

### ✅ Dashboard Layout Structure  
- **Completed**: 2025-05-31 10:00
- **Specialist**: implementer
- **Effort**: 3h (estimated: 4h)
- **Artifacts**: Dashboard.tsx, GridLayout.tsx
- **Notes**: Used CSS Grid for flexible layout system

### ✅ Theme System Setup
- **Completed**: 2025-05-30 14:00
- **Specialist**: implementer
- **Effort**: 2h (estimated: 2h)  
- **Artifacts**: theme.ts, ThemeProvider.tsx
- **Notes**: Light/dark mode support with CSS variables

### ✅ Project Setup & Configuration
- **Completed**: 2025-05-30 10:00
- **Specialist**: implementer
- **Effort**: 3h (estimated: 3h)
- **Artifacts**: package.json, vite.config.ts, tsconfig.json
- **Notes**: Configured with TypeScript, ESLint, Prettier

## 🔄 In Progress Tasks

### 🔄 User Dashboard Components
- **Started**: 2025-06-01 15:00
- **Specialist**: implementer
- **Progress**: 30%
- **Estimated**: 8h | **Spent**: 2h
- **Dependencies**: Authentication system ✅
- **Notes**: Building chart components with recharts library

### 🔄 Data Table Component
- **Started**: 2025-06-01 11:00  
- **Specialist**: implementer
- **Progress**: 60%
- **Estimated**: 6h | **Spent**: 3h
- **Dependencies**: None
- **Notes**: Implementing sorting, filtering, pagination

### 🔄 Form Components Library
- **Started**: 2025-05-31 14:00
- **Specialist**: implementer  
- **Progress**: 40%
- **Estimated**: 5h | **Spent**: 2h
- **Dependencies**: Theme system ✅
- **Notes**: Reusable form inputs with validation

## 📋 Planned Tasks

### 📋 Chart Components Integration
- **Specialist**: implementer
- **Estimated**: 6h
- **Dependencies**: Dashboard components 🔄
- **Priority**: High
- **Notes**: Integration with Chart.js or D3.js

### 📋 Mobile Responsiveness  
- **Specialist**: implementer
- **Estimated**: 4h
- **Dependencies**: Dashboard components 🔄
- **Priority**: Medium
- **Notes**: Responsive breakpoints and mobile navigation

### 📋 Performance Optimization
- **Specialist**: reviewer
- **Estimated**: 3h  
- **Dependencies**: All components complete
- **Priority**: Medium
- **Notes**: Code splitting, lazy loading, bundle analysis

## 📝 Group Notes

### Technical Decisions
- **Component Library**: Using Chakra UI for consistent styling
- **State Management**: React Query for server state, Zustand for client state
- **Testing**: Jest + React Testing Library for component tests
- **Build Tool**: Vite for fast development and building

### Challenges & Solutions
- **Challenge**: Component state management complexity
  - **Solution**: Implemented custom hooks for common patterns
- **Challenge**: Consistent styling across components
  - **Solution**: Created design token system with theme variables

### Next Steps
1. Complete dashboard components with real data integration
2. Implement comprehensive error boundary system
3. Add accessibility features (ARIA labels, keyboard navigation)
4. Performance testing with large datasets

---

**📄 File Info**  
- **Auto-sync**: Enabled ✅  
- **Last DB Sync**: 2025-06-01 16:20:00
- **Edit Status**: Synchronized
- **Dependencies**: [Backend API group](backend.md)

<!-- 
EDITING GUIDELINES:
- ✅ Add notes, insights, technical decisions
- ✅ Update progress estimates and actual hours  
- ✅ Modify task priorities and dependencies
- ⚠️  Task status changes trigger database sync
- 💡 Use checkboxes [ ] for new tasks - they'll be synced!
-->
```

## 🔄 Bi-directional Sync Engine

### File Change Detection
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
```

### User Edit Processing
```python
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
            if abs(current_progress - new_progress) > 0.01:  # Allow for small rounding differences
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
```

### Conflict Resolution System
```python
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
        if conflict.type in ["new_task", "task_deletion", "group_changes"]:
            return "user_choice"
        
        # Default to presenting choice to user
        return "user_choice"
    
    async def present_conflict_to_user(self, conflict: Conflict, workspace_dir: Path):
        """Create conflict resolution files for user review."""
        
        conflict_file = workspace_dir / f"conflict_{conflict.id}.md"
        
        conflict_content = f"""# 🔄 Sync Conflict Resolution

**Conflict ID**: `{conflict.id}`  
**Type**: {conflict.type}  
**Detected**: {conflict.detected_at}

## 📊 Conflict Details

**Item**: {conflict.item_description}  
**Database Version**: Last updated {conflict.database_timestamp}  
**File Version**: Last updated {conflict.file_timestamp}

## 🔀 Choose Resolution

### Option 1: Keep Database Version
```
{conflict.database_value}
```
*Choose this if the database version is more accurate*

### Option 2: Keep File Version  
```
{conflict.file_value}
```
*Choose this if your file edits should take precedence*

### Option 3: Manual Merge
```
[Edit this section with your preferred merged version]

```

## 📝 Resolution Instructions

1. **Review both versions** above
2. **Choose an option** by uncommenting ONE of the following:
   - `<!-- RESOLUTION: database -->`
   - `<!-- RESOLUTION: file -->`  
   - `<!-- RESOLUTION: manual -->`
3. **If manual merge**: Edit the "Manual Merge" section above
4. **Save this file** - the system will detect your choice automatically

---
**Auto-Resolution**: This conflict will auto-resolve to database version in 24 hours if not manually resolved.
"""
        
        async with aiofiles.open(conflict_file, 'w', encoding='utf-8') as f:
            await f.write(conflict_content)
        
        # Monitor for resolution
        await self.monitor_conflict_resolution(conflict_file, conflict)
```

## 🛠️ Template System

### Dynamic Template Generation
```python
class MarkdownTemplateEngine:
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
    async def generate_session_markdown(self, session: Session, task_groups: List[TaskGroup], tasks: List[Task]) -> str:
        """Generate complete session markdown from database state."""
        
        template = self.jinja_env.get_template('session_template.md')
        
        # Prepare template context
        context = {
            'session': session,
            'task_groups': self.organize_task_groups(task_groups),
            'tasks': self.organize_tasks_by_group(tasks, task_groups),
            'metrics': await self.calculate_session_metrics(session, tasks),
            'recent_activity': await self.get_recent_activity(session.session_id),
            'insights': await self.get_session_insights(session.session_id),
            'generated_at': datetime.utcnow(),
            'sync_status': await self.get_sync_status(session.session_id)
        }
        
        return template.render(**context)
    
    def organize_task_groups(self, task_groups: List[TaskGroup]) -> dict:
        """Organize task groups by status and priority."""
        
        organized = {
            'active': [],
            'planned': [], 
            'completed': [],
            'paused': []
        }
        
        for group in task_groups:
            status_key = self.determine_group_status(group)
            organized[status_key].append(group)
        
        # Sort by priority within each status
        for status in organized:
            organized[status].sort(key=lambda g: (g.priority_level, g.group_name))
        
        return organized
    
    async def calculate_session_metrics(self, session: Session, tasks: List[Task]) -> dict:
        """Calculate comprehensive session metrics."""
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == 'completed'])
        in_progress_tasks = len([t for t in tasks if t.status == 'in_progress'])
        
        total_estimated_hours = sum(t.estimated_effort or 0 for t in tasks)
        total_actual_hours = sum(t.actual_effort or 0 for t in tasks)
        
        efficiency = (total_estimated_hours / total_actual_hours * 100) if total_actual_hours > 0 else 0
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'planned_tasks': total_tasks - completed_tasks - in_progress_tasks,
            'completion_percentage': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'total_estimated_hours': total_estimated_hours,
            'total_actual_hours': total_actual_hours,
            'efficiency_percentage': efficiency,
            'estimated_completion_date': await self.estimate_completion_date(session, tasks)
        }
```

### Template Customization
```markdown
<!-- session_template.md -->
# 🚀 Project: {{ session.name }}

**Session ID**: `{{ session.session_id }}`  
**Status**: {{ session.status|title }}  
**Mode**: `{{ session.mode_file }}`  
**Created**: {{ session.created_at.strftime('%Y-%m-%d %H:%M:%S') }}  
**Last Updated**: {{ generated_at.strftime('%Y-%m-%d %H:%M:%S') }}  
**Progress**: {{ "%.0f"|format(metrics.completion_percentage) }}% ({{ metrics.completed_tasks }}/{{ metrics.total_tasks }} tasks completed)

{% if session.description %}
## 📝 Project Description

{{ session.description }}
{% endif %}

## 📊 Session Metrics

| Metric | Value | Target |
|--------|-------|--------|
| **Total Tasks** | {{ metrics.total_tasks }} | {{ metrics.total_tasks }} |
| **Completed** | {{ metrics.completed_tasks }} ({{ "%.0f"|format(metrics.completion_percentage) }}%) | {{ metrics.total_tasks }} (100%) |
| **In Progress** | {{ metrics.in_progress_tasks }} | - |
| **Planned** | {{ metrics.planned_tasks }} | - |
| **Estimated Hours** | {{ metrics.total_estimated_hours }}h | {{ metrics.total_estimated_hours }}h |
| **Actual Hours** | {{ metrics.total_actual_hours }}h | {{ metrics.total_estimated_hours }}h |
| **Efficiency** | {{ "%.0f"|format(metrics.efficiency_percentage) }}% | 90% |

## 🎯 Task Groups Overview

{% for group in task_groups.active %}
### [{{ group.group_name }}](task_groups/{{ group.group_name|lower|replace(' ', '_') }}.md) ⚡ Active
- **Progress**: {{ "%.0f"|format(group.progress_percentage) }}% ({{ group.completed_tasks }}/{{ group.total_tasks }} tasks)
- **Specialist**: {{ group.specialist_focus }}
- **Priority**: {{ ['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'][group.priority_level-1] }}
- **Estimated**: {{ group.estimated_effort }}h | **Actual**: {{ group.actual_effort }}h

{% endfor %}

{% for group in task_groups.planned %}
### [{{ group.group_name }}](task_groups/{{ group.group_name|lower|replace(' ', '_') }}.md) ⏳ Planned
- **Progress**: {{ "%.0f"|format(group.progress_percentage) }}% ({{ group.completed_tasks }}/{{ group.total_tasks }} tasks)
- **Specialist**: {{ group.specialist_focus }}
- **Priority**: {{ ['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'][group.priority_level-1] }}
- **Estimated**: {{ group.estimated_effort }}h | **Actual**: {{ group.actual_effort }}h

{% endfor %}

## 📝 Recent Activity

### Last 7 Days
{% for activity in recent_activity[:10] %}
- {{ activity.status_icon }} **{{ activity.date.strftime('%Y-%m-%d') }}**: {{ activity.description }} ({{ activity.group_name }})
{% endfor %}

### Next Steps
{% for next_step in insights.next_steps %}
- 🎯 {{ next_step }}
{% endfor %}

## 💡 Key Insights

{% if insights.decisions %}
### Decisions Made
{% for decision in insights.decisions %}
- **{{ decision.title }}**: {{ decision.description }}
{% endfor %}
{% endif %}

{% if insights.learnings %}
### Lessons Learned
{% for learning in insights.learnings %}
- {{ learning }}
{% endfor %}
{% endif %}

{% if insights.risks %}
### Risks & Mitigation
{% for risk in insights.risks %}
- **Risk**: {{ risk.description }}
  - **Mitigation**: {{ risk.mitigation }}
{% endfor %}
{% endif %}

## 🔗 Quick Links

{% if session.project_repository %}
- [Project Repository]({{ session.project_repository }})
{% endif %}
{% if session.design_links %}
{% for link in session.design_links %}
- [{{ link.name }}]({{ link.url }})
{% endfor %}
{% endif %}
- [API Documentation](./notes/api_documentation.md)
- [Meeting Notes](./notes/team_meetings.md)

---

**📄 File Info**  
- **Auto-sync**: Enabled ✅
- **Last DB Sync**: {{ sync_status.last_sync.strftime('%Y-%m-%d %H:%M:%S') }}  
- **Edit Status**: {{ sync_status.status|title }}  
- **Backup**: Included in session backups

---
<!-- 
EDITING INSTRUCTIONS:
- ✅ Safe to edit: Progress notes, insights, decisions, links
- ⚠️  Sync required: Task status changes, progress percentages  
- ❌ Don't edit: Session ID, creation date, auto-generated metrics
- 💡 Tip: Add content in "Notes" sections - they sync automatically!
-->
```

## 🚀 Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1)
- Markdown template system implementation
- Basic file generation from database state
- File system monitoring setup
- Simple change detection

### Phase 2: Bi-directional Sync (Week 2)  
- User edit parsing and processing
- Change detection and database updates
- Basic conflict resolution
- Sync status tracking

### Phase 3: Advanced Features (Week 3)
- Sophisticated conflict resolution
- Template customization system
- Performance optimization
- Integration with backup system

### Phase 4: Polish & Integration (Week 3)
- User experience improvements
- Error handling and recovery
- Documentation and tutorials
- Production deployment preparation

## 🎯 User Experience Guidelines

### Editing Best Practices
1. **Make small, focused changes** rather than large bulk edits
2. **Save frequently** to trigger sync operations
3. **Use the provided comment sections** for safe editing areas
4. **Check sync status** before making major changes
5. **Resolve conflicts promptly** when they arise

### Safe Editing Zones
- ✅ **Notes sections**: Insights, decisions, learnings, next steps
- ✅ **User content areas**: Comments, links, custom sections
- ✅ **Progress estimates**: Actual hours, effort adjustments
- ⚠️ **Status changes**: Task completions, progress percentages (require sync)
- ❌ **Auto-generated content**: Metrics, timestamps, system data

### Conflict Prevention
- **Coordinate with team** when multiple people edit simultaneously
- **Use version control** to track and merge changes
- **Regular syncing** by saving files frequently
- **Clear communication** about who is editing what

---

**Implementation Status**: COMPREHENSIVE SPECIFICATION COMPLETE ✅  
**User Experience**: Designed for non-technical users with clear guidelines  
**Integration Points**: Session management, backup system, conflict resolution  
**Next Steps**: Template implementation, sync engine development, user testing
