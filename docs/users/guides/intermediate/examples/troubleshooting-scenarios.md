

# Troubleshooting Scenarios & Solutions

*Real-world problems with step-by-step solutions*

#

# Performance Issues

#

#

# Scenario 1: System Running Slowly

**Symptoms:**

- Tool responses taking 10+ seconds

- Database queries timing out

- High memory usage during operations

**Diagnostic Commands:**

```python

# Step 1: Check system health

"Check status of all active tasks and show system metrics"

# Step 2: Identify performance bottlenecks  

"Use maintenance coordinator to scan full project with basic validation"

# Step 3: Analyze results

"""
Expected findings:

- High task count (>100 active tasks)

- Many stale tasks (>24 hours old)

- Database size issues

- Memory consumption patterns
"""

```text

**Solution Workflow:**

```text
text
python

# Phase 1: Immediate relief (5 minutes)

immediate_fixes = [
    "Use maintenance coordinator to scan and cleanup current session with comprehensive validation",
    "Archive any completed workflows that are no longer needed",
    "Check for and resolve any database lock issues"
]

# Phase 2: Deep cleanup (15 minutes)

comprehensive_cleanup = [
    "Run maintenance scan on full project with comprehensive validation",
    "Review and act on all maintenance recommendations", 
    "Archive stale tasks and orphaned workflows",
    "Optimize database with vacuum and cleanup operations"
]

# Phase 3: Prevention setup (10 minutes)

prevention_measures = [
    "Set up daily maintenance routine",
    "Configure automatic archival policies",
    "Establish task count monitoring",
    "Document performance baseline metrics"
]

```text
text

**Expected Results:**

- 50-80% reduction in response times

- Database size reduction

- Memory usage optimization

- Stable performance metrics

#

#

# Scenario 2: Database Lock Issues

**Symptoms:**

- "Database is locked" errors

- Operations hanging indefinitely

- Concurrent access conflicts

**Diagnostic Process:**

```text
bash

# Check for lock files

ls -la .task_orchestrator/database/*.lock

# Check database integrity

sqlite3 .task_orchestrator/database/tasks.db "PRAGMA integrity_check;"

# Check for zombie processes

ps aux | grep mcp-task-orchestrator

```text
text

**Solution Steps:**

```text
python

# Step 1: Graceful resolution

graceful_steps = [
    "Close all MCP clients completely",
    "Wait 30 seconds for processes to terminate",
    "Remove any .lock files in database directory",
    "Restart MCP client and test functionality"
]

# Step 2: If graceful fails - force resolution  

force_resolution = [
    "Kill any hanging mcp-task-orchestrator processes",
    "Remove database lock files: rm .task_orchestrator/database/*.lock",
    "Run database repair: sqlite3 tasks.db 'PRAGMA integrity_check;'",
    "If corruption found, restore from backup or reset database"
]

# Step 3: Prevention

prevention_setup = [
    "Enable database WAL mode for better concurrency",
    "Set up automatic backup routine",
    "Monitor for concurrent access patterns",
    "Configure proper timeout settings"
]

```text
text

---

#

# Task Management Issues

#

#

# Scenario 3: Stale Tasks Accumulating

**Problem Description:**
Tasks stuck in "active" or "pending" status for days, cluttering the system and impacting performance.

**Identification Commands:**

```text
python

# Detect stale tasks

"Check status of all tasks including completed ones"

# Comprehensive stale task analysis

"Use maintenance coordinator to scan full project with comprehensive validation"

# Expected output analysis:

"""
{
  "stale_tasks_found": 5,
  "stale_tasks": [
    {
      "task_id": "implementer_abc123",
      "title": "Database integration setup",
      "status": "active", 
      "age_hours": 96.5,
      "specialist_type": "implementer"
    }
  ],
  "recommendations": [
    {
      "type": "manual_review",
      "priority": "high",
      "title": "Review long-running tasks"
    }
  ]
}
"""

```text
text

**Resolution Workflow:**

```text
python

# Phase 1: Assess each stale task

stale_task_review = """
For each stale task:

1. Determine if work was actually completed

2. Check if task is truly abandoned

3. Decide: complete, archive, or resume
"""

# Phase 2: Clean resolution

for stale_task in stale_tasks:
    if task_was_completed(stale_task):
        f"Complete subtask {stale_task.id} with summary of actual work done"
    elif task_is_abandoned(stale_task):
        "Use maintenance coordinator to archive this specific stale task"
    else:
        f"Resume work on {stale_task.id} and complete properly"

# Phase 3: Systematic cleanup

"Run comprehensive maintenance scan to catch any remaining stale tasks"

# Phase 4: Prevention

prevention_routine = """
Daily: Check for tasks active > 24 hours
Weekly: Review all pending tasks for progress
Monthly: Archive completed workflows
"""

```text
text

#

#

# Scenario 4: Missing or Corrupt Task Data

**Symptoms:**

- Task IDs not found when referenced

- Incomplete task information

- Broken parent-child relationships

**Diagnostic Commands:**

```text
python

# Check task relationships

"Use maintenance coordinator to validate structure of full project with full audit"

# Identify specific issues

structure_validation_output = """
{
  "orphaned_tasks": [
    {
      "task_id": "tester_xyz789",
      "missing_parent_id": "task_missing123"
    }
  ],
  "incomplete_workflows": [
    {
      "parent_task_id": "task_abc456", 
      "missing_subtasks": 2,
      "corruption_type": "broken_references"
    }
  ]
}
"""

```text
text

**Recovery Procedures:**

```text
python

# Option 1: Automated cleanup (recommended)

automated_recovery = [
    "Use maintenance coordinator to scan and cleanup with comprehensive validation",
    "Allow system to automatically archive orphaned tasks",
    "Review recommendations for manual intervention needed"
]

# Option 2: Manual recovery (when data is valuable)

manual_recovery = [
    "Export task data before cleanup: sqlite3 tasks.db '.dump' > backup.sql",
    "Identify salvageable task components",
    "Recreate task relationships manually if possible",
    "Archive unsalvageable fragments"
]

# Option 3: Fresh start (when corruption is extensive)

fresh_start = [
    "Backup existing artifacts: cp -r .task_orchestrator/artifacts/ backup/",
    "Reset database: rm -rf .task_orchestrator/database/",
    "Restart MCP server to recreate clean database",
    "Begin new workflow with lessons learned"
]

```text
text

---

#

# Context and Memory Issues

#

#

# Scenario 5: Approaching Context Limits

**Warning Signs:**

- Very long conversation histories

- Responses becoming less accurate

- System struggling to maintain context

**Proactive Management:**

```text
python

# Artifact-based approach

context_management_strategy = """
When completing subtasks, always use:

- Brief summary (1-2 sentences)

- Comprehensive detailed_work (stored as artifact)

- Specific file_paths for created content

- Appropriate artifact_type classification
"""

# Example completion that saves context:

"""Complete subtask implementer_abc123 with:
Summary: Implemented user authentication API with JWT tokens and password hashing
Detailed work: [Full 500-line implementation with error handling, security measures, and documentation]
File paths: [src/auth/api.py, src/auth/middleware.py, tests/test_auth.py, docs/auth-api.md]
Artifact type: code
Next action: continue"""

# Benefits:

"""

- Detailed work stored in filesystem, not conversation

- Context stays focused on coordination 

- Full implementation accessible via artifacts

- Can resume work in new conversation
"""

```text
text

**Emergency Context Recovery:**

```text
python

# When context is already overloaded

emergency_procedures = [
    "Use maintenance coordinator to prepare handover with comprehensive validation",
    "Generate complete status summary with artifact references",
    "Save conversation state and start fresh session",
    "Resume using initialize_session with prior task recovery"
]

# Resume in new session:

resume_workflow = [
    "Initialize new orchestration session",
    "System will detect and show previous interrupted tasks",
    "Review handover documentation from previous session",
    "Continue work with clean context"
]

```text
text

#

#

# Scenario 6: Lost Work Due to Session Interruption

**Situation:**
MCP client crashed or was closed during active work, potentially losing progress.

**Recovery Process:**

```text
python

# Step 1: Assess the situation

recovery_assessment = [
    "Initialize new orchestration session",
    "Check what tasks the system detected as interrupted",
    "Review artifact storage for any work that was saved",
    "Identify what work might need to be redone"
]

# Step 2: Systematic recovery

for interrupted_task in interrupted_tasks:
    

# Check if work was preserved

    if has_artifacts(interrupted_task):
        f"Review artifacts for {interrupted_task.id} to see what was completed"
        f"Complete the task with recovered work or continue from checkpoint"
    else:
        f"Resume work on {interrupted_task.id} from beginning with specialist guidance"

# Step 3: Prevention for future

prevention_habits = [
    "Complete subtasks promptly when work is done",
    "Use detailed_work parameter extensively",
    "Save intermediate progress as artifacts",
    "Run regular maintenance to preserve state"
]

```text
text

---

#

# Integration and Configuration Issues

#

#

# Scenario 7: Tool Not Available in MCP Client

**Problem:**
orchestrator tools don't appear in the client's tool list.

**Diagnostic Steps:**

```text
bash

# Check MCP client configuration

# For Claude Desktop:

cat ~/.config/claude/claude_desktop_config.json

# or Windows: %APPDATA%\Claude\claude_desktop_config.json

# For Cursor:

cat ~/.cursor/mcp.json

# For VS Code:

cat ~/.vscode/mcp.json

```text
text

**Configuration Verification:**

```text
json
// Correct configuration should look like:
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-task-orchestrator/mcp_task_orchestrator/server.py"],
      "env": {}
    }
  }
}

```text
text

**Resolution Steps:**

```text
python

# Step 1: Verify installation

installation_check = [
    "Run: python run_installer.py --verify",
    "Check that virtual environment exists: ls venv_mcp/",
    "Verify server can start: python mcp_task_orchestrator/server.py --test",
    "Check for any import errors or missing dependencies"
]

# Step 2: Fix configuration

configuration_fixes = [
    "Re-run installer: python run_installer.py",
    "Manually verify paths are absolute in config files", 
    "Check file permissions on server and config files",
    "Restart MCP client completely after changes"
]

# Step 3: Test functionality

functionality_test = [
    "Look for 'task-orchestrator' in available tools",
    "Try simple command: 'Initialize orchestration session'",
    "Verify response includes specialist roles",
    "Test maintenance: 'Use maintenance coordinator to scan session'"
]

```text
text

#

#

# Scenario 8: Inconsistent Tool Behavior

**Symptoms:**

- Tools work sometimes but not others

- Intermittent timeouts or errors

- Inconsistent responses

**Diagnostic Process:**

```text
python

# Check system resources

system_diagnostics = [
    "Monitor CPU and memory usage during operations",
    "Check disk space: df -h",
    "Verify database accessibility: sqlite3 .task_orchestrator/database/tasks.db '.tables'",
    "Check for competing processes"
]

# Test tool consistency

consistency_tests = [
    "Run same command multiple times",
    "Test with different scopes and validation levels",
    "Monitor response times and success rates",
    "Check logs for error patterns"
]

```text
text

**Resolution Approach:**

```text
python

# Phase 1: Environmental factors

environmental_fixes = [
    "Ensure adequate system resources (RAM, disk space)",
    "Close unnecessary applications during heavy operations",
    "Check for antivirus interference with database files",
    "Verify network stability if using remote storage"
]

# Phase 2: Configuration optimization

optimization_steps = [
    "Reduce validation levels for better performance",
    "Use smaller scopes for maintenance operations", 
    "Configure appropriate timeouts",
    "Set up database optimization routines"
]

# Phase 3: Systematic testing

testing_protocol = [
    "Create test workflow to verify functionality",
    "Document working configurations",
    "Establish baseline performance metrics",
    "Set up monitoring for early issue detection"
]

```text
text

---

#

# Advanced Troubleshooting

#

#

# Scenario 9: Complex Multi-Phase Project Issues

**Challenge:**
Large project with multiple phases experiencing coordination issues, task conflicts, and maintenance challenges.

**Systematic Approach:**

```text
python

# Phase 1: Project health assessment

project_assessment = [
    "Run comprehensive structure validation on full project",
    "Analyze task distribution and completion rates",
    "Identify bottlenecks and dependency issues",
    "Review artifact organization and accessibility"
]

# Phase 2: Phase-by-phase analysis

for project_phase in project_phases:
    phase_analysis = f"""
    Analyze {project_phase}:
    - Task completion status
    - Specialist distribution
    - Artifact quality and completeness
    - Dependencies and blockers
    """
    
    f"Use maintenance coordinator to validate structure of {project_phase} tasks"

# Phase 3: Coordinated resolution

resolution_strategy = [
    "Archive completed phases to reduce system load",
    "Reorganize active tasks by priority and dependencies",
    "Set up phase-specific maintenance routines",
    "Establish clear handoff procedures between phases"
]

```text
text

#

#

# Scenario 10: Team Coordination Issues

**Problem:**
Multiple team members using the same orchestrator instance causing conflicts and confusion.

**Coordination Solutions:**

```text
python

# Approach 1: Workspace separation

workspace_separation = [
    "Create separate .task_orchestrator directories for each team member",
    "Use environment variables to point to different databases",
    "Establish naming conventions for shared artifacts",
    "Set up clear handoff procedures"
]

# Approach 2: Structured collaboration

structured_collaboration = [
    "Define ownership for different project phases",
    "Use consistent task naming and artifact organization",
    "Establish regular sync points with handover preparation",
    "Document shared context and decisions"
]

# Approach 3: Merge and sync procedures

merge_procedures = [
    "Use maintenance coordinator to prepare handovers before switches",
    "Document all active tasks with comprehensive summaries",
    "Organize artifacts with clear access instructions",
    "Maintain shared project documentation"
]

```text
text

---

#

# Prevention and Monitoring

#

#

# Establishing Healthy Patterns

**Daily Habits:**

```text
python
daily_routine = [
    "Start: Initialize session and check for interrupted tasks",
    "During work: Complete tasks promptly with detailed artifacts",
    "End: Run basic maintenance scan and cleanup",
    "Before handoff: Prepare comprehensive handover documentation"
]

```text
text

**Weekly Maintenance:**

```text
python
weekly_maintenance = [
    "Monday: Comprehensive project health check",
    "Wednesday: Performance optimization scan", 
    "Friday: Archive completed workflows and prepare for next week",
    "Weekend: Full system validation and optimization"
]

```text
text

**Monthly Reviews:**

```text
python
monthly_reviews = [
    "Full audit of all project components",
    "Performance metrics analysis and optimization",
    "Artifact organization and cleanup",
    "Process improvement and lessons learned documentation"
]

```text
text

#

#

# Monitoring and Alerting

**Key Metrics to Watch:**

```text
python
monitoring_metrics = {
    "task_counts": "Keep active tasks under 100 for optimal performance",
    "stale_tasks": "Address any tasks stale for >24 hours immediately",
    "database_size": "Monitor for excessive growth, optimize regularly",
    "response_times": "Track tool response times for performance degradation",
    "error_rates": "Monitor for increasing error patterns"
}

```text
text

**Early Warning Signs:**

```text
python
warning_signs = [
    "Tool responses taking >5 seconds consistently",
    "More than 5 stale tasks accumulating", 
    "Database size growing >10MB without proportional work",
    "Frequent timeout errors or connection issues",
    "Memory usage consistently >500MB for simple operations"
]
```text
text

---

*These troubleshooting scenarios cover the most common issues users encounter. Use them as templates for diagnosing and resolving similar problems in your own workflows. The key is systematic diagnosis followed by targeted resolution and prevention measures.*
