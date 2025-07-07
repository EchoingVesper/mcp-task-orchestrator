

# Interactive Examples & Workflow Patterns

*Step-by-step examples you can follow along with immediately*

#

# Quick Start Examples

#

## Example 1: First Time Setup and Basic Usage

**Scenario**: You just installed the orchestrator and want to try it out.

**Step 1: Initialize Your First Session**

```text
Command: "Initialize a new orchestration session"

Expected Response:

- Session confirmation

- Available specialist roles listed

- Usage instructions provided

- Any interrupted tasks shown (if resuming)

```text

**Step 2: Create Your First Task Plan**
```text
text

Command: "Plan a simple Python script that reads a CSV file, processes the data, and generates a summary report"

What happens:

- LLM analyzes the request

- Creates 4-6 subtasks with appropriate specialists

- Returns parent_task_id and subtask list

- Suggests next steps

```text

**Step 3: Execute Your First Subtask**

```text

Command: "Execute the architect subtask [task_id_from_step_2]"

What you get:

- Architect specialist context and expertise

- System design guidance for CSV processing

- Approach and methodology recommendations

- Task-specific instructions

```text
text

**Step 4: Complete Your First Subtask**

```text

Command: "Complete the architect subtask [task_id] with summary: 'Designed modular CSV processing architecture with error handling', detailed work: '[your architecture document]', next action: continue"

Result:

- Task marked as completed

- Progress updated (e.g., 25% complete)

- Artifact created and stored

- Next recommended task suggested

```text
text

**Step 5: Check Progress and Run Maintenance**

```text

Command: "Check the status of all active tasks"
Then: "Use maintenance coordinator to scan and cleanup the current session"

You'll see:

- Current task progress

- System health status

- Any cleanup recommendations

```text
text

---

#

# Maintenance Coordinator Examples

#

## Example 2: Daily Maintenance Routine

**Morning Startup Routine:**

```text
bash

# 1. Initialize and check for interrupted work

"Initialize session and show any tasks I can resume"

# 2. If resuming work, check system health

"Use maintenance coordinator to validate structure of current session"

# 3. Clean up any stale items from yesterday

"Run maintenance scan and cleanup on current session with basic validation"

```text
text

**End of Day Routine:**

```text
bash

# 1. Complete any final tasks

"Complete subtask [id] with summary and prepare for handover"

# 2. Prepare comprehensive handover

"Use maintenance coordinator to prepare handover with comprehensive validation"

# 3. Check final status

"Show status of all tasks including completed ones"

```text
text

#

## Example 3: Performance Optimization Workflow

**When System Feels Slow:**

```text
bash

# Step 1: Diagnose the issue

"Check status and show system health metrics"

# Step 2: Run comprehensive cleanup

"Use maintenance coordinator with action scan_cleanup, scope full_project, validation_level comprehensive"

# Step 3: Review recommendations

"Show me the maintenance recommendations from the last scan"

# Step 4: Validate improvements

"Run structure validation on full project with basic validation"

```text
text

**Expected Results:**

- Task count reduction (stale tasks archived)

- Performance improvement recommendations

- Database optimization suggestions

- System health score improvement

#

## Example 4: Weekly Deep Maintenance

**Complete Weekly System Health Check:**

```text
python

# Week setup - run at start of work week

maintenance_schedule = {
    "action": "scan_cleanup",
    "scope": "full_project", 
    "validation_level": "comprehensive"
}

# Execute comprehensive scan

"Use maintenance coordinator to scan and cleanup the full project with comprehensive validation"

# Review and act on recommendations

"Show maintenance recommendations and help me prioritize actions"

# Validate system health after cleanup

"Run maintenance validation on full project with full audit level"

```text
text

---

#

# Workflow Pattern Examples

#

## Example 5: Full-Stack Web Application Development

**Project**: Build a task management web app with React frontend and Node.js backend

**Phase 1: Project Initialization**

```text

"Initialize orchestration session and plan a full-stack task management web application with React frontend, Node.js backend, PostgreSQL database, user authentication, real-time updates, and comprehensive testing"

```text
text

**Expected Task Breakdown:**

1. **Architect**: System architecture and technology decisions

2. **Architect**: Database schema and API design  

3. **Implementer**: Backend API development with authentication

4. **Implementer**: Frontend React application with components

5. **Implementer**: Real-time WebSocket integration

6. **Tester**: Backend API testing and validation

7. **Tester**: Frontend testing and user experience validation

8. **Documenter**: API documentation and deployment guide

**Phase 2: Execution Pattern**

```text
python

# For each subtask:

for subtask in task_list:
    

# 1. Get specialist context

    f"Execute the {subtask.specialist_type} subtask {subtask.task_id}"
    
    

# 2. Do the work with specialist guidance

    

# [Follow the specialist instructions]

    
    

# 3. Complete with detailed documentation

    f"""Complete subtask {subtask.task_id} with:
    Summary: [Brief description of what was accomplished]
    Detailed work: [Comprehensive documentation of the implementation]
    File paths: [List of files created/modified]
    Artifact type: code
    Next action: continue"""

```text
text

**Phase 3: Integration and Finalization**

```text

# After all subtasks complete

"Synthesize results for the full-stack web application project"

# Run final quality check

"Use maintenance coordinator to validate structure and prepare handover"

# Generate final documentation

"Create comprehensive project documentation including setup, API reference, and deployment instructions"
```text
text

#

## Example 6: Data Processing Pipeline

**Project**: ETL pipeline for e-commerce analytics

**Interactive Workflow:**

```text
python

# Step 1: Initialize with specific context

"""Initialize orchestration and plan an ETL data processing pipeline that:

- Extracts data from Shopify API and CSV files

- Transforms data for analytics (customer segmentation, sales trends)

- Loads into PostgreSQL data warehouse

- Generates automated reports and dashboards

- Includes error handling, logging, and monitoring"""

# Step 2: Architecture phase

"Execute the architect subtask and help me design a scalable ETL architecture"

# Follow architect guidance, then:

"""Complete architect subtask with:
Summary: Designed modular ETL pipeline with parallel processing
Detailed work: [Architecture document with data flow diagrams]
File paths: [architecture/etl-design.md, diagrams/data-flow.png]
Artifact type: design
Next action: continue"""

# Step 3: Implementation phases

"Execute the implementer subtask for data extraction components"

# [Implement following guidance]

"Execute the implementer subtask for data transformation logic"

# [Implement following guidance]  

"Execute the implementer subtask for data loading and warehouse setup"

# [Implement following guidance]

# Step 4: Testing and validation

"Execute the tester subtask for ETL pipeline validation"

# [Create comprehensive tests]

# Step 5: Documentation and deployment

"Execute the documenter subtask for operational documentation"

# [Create deployment and monitoring guides]

# Step 6: Final integration

"Synthesize all ETL pipeline components into well-tested system"

```text
text

#

## Example 7: Documentation Project

**Project**: API documentation overhaul for existing service

**Step-by-Step Workflow:**

```text
python

# Initialize with documentation focus

"""Initialize orchestration and plan comprehensive API documentation project:

- Analyze existing codebase and API endpoints

- Create OpenAPI/Swagger specifications

- Write user-friendly guides and tutorials

- Build interactive examples and code samples

- Set up documentation site with search and navigation"""

# Research phase

"Execute the researcher subtask to analyze current API structure"

# Architecture phase for documentation structure

"Execute the architect subtask to design documentation architecture"

# Implementation phases

documentation_tasks = [
    "documenter subtask for API reference creation",
    "documenter subtask for user guide development", 
    "implementer subtask for interactive examples",
    "implementer subtask for documentation site setup"
]

for task in documentation_tasks:
    f"Execute the {task} and provide specialist guidance"
    

# [Follow guidance and implement]

    f"Complete {task} with comprehensive artifact documentation"

# Quality assurance

"Execute the reviewer subtask for documentation quality review"

# Final synthesis

"Synthesize complete documentation system with navigation and search"

```text
text

---

#

# Troubleshooting Scenarios

#

## Example 8: Handling Stale Tasks

**Scenario**: You notice tasks that have been "active" for days but aren't progressing.

**Diagnostic Workflow:**

```text
python

# Step 1: Identify the issue

"Check status of all tasks including completed ones"

# Step 2: Run comprehensive scan

"Use maintenance coordinator to scan and cleanup full project with comprehensive validation"

# Expected output analysis:

"""
{
  "stale_tasks_found": 3,
  "stale_tasks": [
    {
      "task_id": "implementer_abc123",
      "age_hours": 72.5,
      "status": "active",
      "title": "Database integration implementation"
    }
  ]
}
"""

# Step 3: Review and decide

"Show me details about the stale tasks and recommendations for resolution"

# Step 4: Clean resolution

"Use maintenance coordinator with scan_cleanup action to archive stale tasks"

```text
text

**Prevention Strategy:**

```text
python

# Daily habit - prevent stale tasks

daily_maintenance = """
Use maintenance coordinator to:

1. Scan current session with basic validation

2. Review any tasks active > 24 hours  

3. Complete or archive tasks that aren't progressing
"""

```text
text

#

## Example 9: Database Performance Issues

**Scenario**: System is responding slowly, many tasks in database.

**Resolution Workflow:**

```text
python

# Step 1: Diagnose system health

"Check system status and run maintenance structure validation"

# Step 2: Performance analysis

"Use maintenance coordinator to scan full project with comprehensive validation"

# Typical findings:

"""
{
  "total_tasks": 150,
  "recommendations": [
    {
      "type": "performance_optimization",
      "priority": "high",
      "description": "150 tasks exceed recommended limit of 100"
    }
  ]
}
"""

# Step 3: Systematic cleanup

"Run comprehensive cleanup on full project to archive completed workflows"

# Step 4: Validate improvements

"Check system status after cleanup and measure performance improvement"

# Step 5: Establish maintenance routine

"Set up weekly maintenance schedule to prevent future performance issues"

```text
text

#

## Example 10: Context Limit Prevention

**Scenario**: Working on large project, approaching context limits.

**Proactive Workflow:**

```text
python

# Before hitting limits - use artifacts effectively

task_completion_pattern = """
Complete subtask {task_id} with:
Summary: [Brief 1-2 sentence summary]
Detailed work: [Full implementation details - stored as artifact]
File paths: [All files created/modified]  
Artifact type: [code/documentation/analysis/design]
Next action: continue
"""

# Benefits:

"""

- Detailed work stored in filesystem, not conversation

- Context preserved for future sessions

- Full implementation accessible via artifact files

- Conversation stays focused on coordination
"""

# When approaching limits:

"Use maintenance coordinator to prepare handover with comprehensive validation"

# Result:

"""

- Complete handover documentation generated

- Temporary data cleaned up

- System optimized for continuation

- Clear resume instructions provided
"""

```text
text

---

#

# Common Integration Patterns

#

## Example 11: CI/CD Integration Workflow

**Project**: Set up automated testing and deployment pipeline

```text
python

# Phase 1: Plan CI/CD architecture

"""Initialize orchestration and plan CI/CD pipeline setup:

- GitHub Actions workflow configuration

- Automated testing (unit, integration, e2e)

- Build and containerization process

- Deployment automation to staging and production

- Monitoring and rollback procedures"""

# Phase 2: Implementation with maintenance

cicd_workflow = [
    "architect: CI/CD pipeline design",
    "implementer: GitHub Actions workflow setup", 
    "implementer: Docker containerization",
    "tester: Automated test suite creation",
    "implementer: Deployment automation",
    "documenter: Operations and troubleshooting guide"
]

# Phase 3: Execute with regular maintenance

for task in cicd_workflow:
    f"Execute {task} with specialist guidance"
    

# [Implement following guidance]

    f"Complete {task} with comprehensive documentation"
    
    

# Maintenance after major phases

    if task.endswith(["workflow setup", "automation", "guide"]):
        "Run maintenance scan to optimize system before next phase"

# Phase 4: Integration testing

"Synthesize CI/CD pipeline and run comprehensive validation"

```text

#

## Example 12: Team Handoff Pattern

**Scenario**: Transferring project to another team member.

**Complete Handoff Workflow:**

```text
python

# Step 1: Prepare comprehensive handover

"Use maintenance coordinator to prepare handover with comprehensive validation"

# Step 2: Generate status summary

"Show complete status of all tasks with progress details"

# Step 3: Organize artifacts

"List all artifacts created during this project with access instructions"

# Step 4: Create transition documentation

"""Create handover documentation including:

- Project overview and current status

- Next steps and priorities  

- Artifact locations and access methods

- Known issues and resolutions

- Contact information and resources"""

# Step 5: Validate handover completeness

"Run maintenance validation to ensure all components are properly documented"

# Handover package includes:

"""

1. Complete task history and progress

2. All artifacts with organized file structure

3. Next steps documentation

4. System health status

5. Troubleshooting guidance

6. Resume instructions for new team member
"""

```text
text

---

#

# Advanced Workflow Examples

#

## Example 13: Multi-Phase Complex Project

**Project**: Legacy system modernization (6-month project)

**Phase 1: Analysis and Planning (Month 1)**

```text
python

# Week 1: System analysis

"Initialize orchestration for legacy system analysis phase"

analysis_tasks = [
    "researcher: Current system architecture analysis",
    "researcher: Technology stack evaluation", 
    "architect: Modernization strategy design",
    "architect: Migration approach planning"
]

# Week 2-4: Detailed planning

"Plan detailed modernization roadmap with risk analysis and timeline"

# Monthly maintenance

"Run comprehensive maintenance and prepare phase 1 handover"

```text
text

**Phase 2: Infrastructure Modernization (Months 2-3)**

```text
python

# Infrastructure first approach

"Plan infrastructure modernization including containerization, cloud migration, and CI/CD setup"

# Regular maintenance during long phase

weekly_maintenance_schedule = """
Week 1: Basic cleanup
Week 2: Comprehensive scan  
Week 3: Structure validation
Week 4: Performance optimization and handover prep
"""

```text
text

**Phase 3: Application Migration (Months 4-5)**

```text
python

# Application layer modernization

"Plan application code migration with API redesign and testing strategy"

# Continuous maintenance for complex phase

"Run daily basic maintenance and weekly comprehensive validation"

```text
text

**Phase 4: Integration and Deployment (Month 6)**

```text
python

# Final integration

"Plan final integration testing, deployment, and user training"

# Project completion

"Synthesize complete modernization project and prepare final handover"
```text
text

---

#

# Best Practices from Examples

#

## Workflow Management

1. **Always initialize** before starting any work

2. **Break complex projects** into logical phases

3. **Use specific descriptions** in task planning

4. **Follow specialist guidance** from execute_subtask

5. **Complete tasks promptly** with detailed artifacts

#

## Maintenance Integration

1. **Daily basic cleanup** prevents issues

2. **Weekly comprehensive scans** maintain performance

3. **Monthly full audits** ensure system health

4. **Pre-handoff preparation** enables smooth transitions

5. **Post-completion archival** keeps system optimized

#

## Artifact Management

1. **Use detailed_work extensively** for comprehensive storage

2. **Specify artifact_type** for better organization

3. **Include all file_paths** for complete tracking

4. **Access artifacts** via file system when needed

5. **Reference artifacts** in handover documentation

#

## Error Prevention

1. **Check status regularly** to monitor progress

2. **Run structure validation** before major milestones

3. **Use appropriate scopes** for maintenance operations

4. **Monitor task counts** to prevent performance issues

5. **Prepare handovers** before context limits

---

*These examples provide practical, copy-paste workflows you can adapt for your specific projects. Start with the simpler examples and progress to more complex patterns as you become comfortable with the orchestration approach.*
