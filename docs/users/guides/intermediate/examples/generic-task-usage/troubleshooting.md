

# Troubleshooting

> **Navigation**: [Docs Home](../../README.md) > [Examples](../../../../../../README.md) > [Generic Task Usage](../../../../../README.md) > Troubleshooting

#

# Common Issues and Solutions

This guide covers the most common issues when working with the Generic Task Model and their solutions.

#

# Task Creation Issues

#

#

# Problem: Task ID Already Exists

```text
Error: Task with ID 'feature_auth_123' already exists

```text

**Solution**: Use unique task IDs or implement auto-generation:

```text
python

# Option 1: Check if task exists first

existing_task = await orchestrator.get_task("feature_auth_123")
if existing_task:
    

# Update existing task or generate new ID

    task_id = f"feature_auth_{int(time.time())}"
else:
    task_id = "feature_auth_123"

# Option 2: Use auto-generated IDs

task = GenericTask(
    task_id=None,  

# Will auto-generate

    task_type="feature",
    attributes={"title": "User Authentication"}
)

```text

#

#

# Problem: Invalid Parent Task ID

```text

Error: Parent task 'epic_nonexistent' not found

```text

**Solution**: Validate parent task exists before creating child tasks:

```text
python
async def safe_child_task_creation(parent_id: str, child_data: dict):
    

# Verify parent exists

    parent_task = await orchestrator.get_task(parent_id)
    if not parent_task:
        raise ValueError(f"Parent task {parent_id} not found")
    
    

# Create child task

    child_task = GenericTask(
        task_id=child_data["task_id"],
        task_type=child_data["task_type"],
        parent_task_id=parent_id,
        attributes=child_data["attributes"]
    )
    
    return await orchestrator.save_task(child_task)

```text

#

#

# Problem: Task Validation Errors

```text

Error: Task title cannot be empty
Error: Invalid task_type 'invalid_type'

```text

**Solution**: Implement comprehensive validation:

```text
python
def validate_task_data(task_data: dict):
    """Validate task data before creation."""
    
    errors = []
    
    

# Required fields

    if not task_data.get("task_id"):
        errors.append("task_id is required")
    
    if not task_data.get("task_type"):
        errors.append("task_type is required")
    
    

# Attributes validation

    attributes = task_data.get("attributes", {})
    if not attributes.get("title"):
        errors.append("Task title is required in attributes")
    
    

# Valid task types

    valid_types = ["epic", "feature", "specialist_task", "bug_fix", "deployment"]
    if task_data.get("task_type") not in valid_types:
        errors.append(f"task_type must be one of: {valid_types}")
    
    if errors:
        raise ValueError(f"Validation errors: {'; '.join(errors)}")
    
    return True

```text

#

# Dependency Issues

#

#

# Problem: Circular Dependencies

```text

Error: Adding dependency would create circular dependency

```text

**Solution**: Implement circular dependency detection:

```text
python
async def check_circular_dependency(task_id: str, new_dependency_id: str):
    """Check for circular dependencies before adding."""
    
    

# Get complete dependency chain for the new dependency

    dependency_chain = await orchestrator.get_dependency_chain(new_dependency_id)
    dependency_ids = [dep.task_id for dep in dependency_chain]
    
    

# Check if our task is already in the chain

    if task_id in dependency_ids:
        raise CircularDependencyError(
            f"Adding {new_dependency_id} as dependency of {task_id} "
            f"would create circular dependency: {' -> '.join(dependency_ids + [task_id])}"
        )
    
    return True

```text

#

#

# Problem: Dependency Task Not Found

```text

Error: Dependency task 'arch_design_001' not found

```text

**Solution**: Validate dependencies before adding:

```text
python
async def add_dependencies_safely(task_id: str, dependencies: List[dict]):
    """Add dependencies with validation."""
    
    validated_dependencies = []
    
    for dep_data in dependencies:
        dep_task_id = dep_data["dependency_task_id"]
        
        

# Check if dependency task exists

        dep_task = await orchestrator.get_task(dep_task_id)
        if not dep_task:
            raise ValueError(f"Dependency task {dep_task_id} not found")
        
        

# Check for circular dependencies

        await check_circular_dependency(task_id, dep_task_id)
        
        

# Create dependency object

        dependency = TaskDependency(
            dependency_task_id=dep_task_id,
            dependency_type=DependencyType(dep_data["dependency_type"]),
            description=dep_data.get("description", "")
        )
        validated_dependencies.append(dependency)
    
    

# Add all dependencies

    task = await orchestrator.get_task(task_id)
    task.dependencies.extend(validated_dependencies)
    return await orchestrator.save_task(task)

```text

#

# Query and Performance Issues

#

#

# Problem: Slow Query Performance

```text

Query taking longer than expected for large task hierarchies

```text

**Solution**: Optimize queries with filters and pagination:

```text
python

# Instead of loading all tasks

all_tasks = await orchestrator.query_tasks({})  

# Slow for large datasets

# Use specific filters and pagination

filtered_tasks = await orchestrator.query_tasks({
    "filters": {
        "status": ["active", "blocked"],
        "task_type": ["feature"],
        "created_after": "2025-06-01T00:00:00Z"
    },
    "limit": 50,
    "offset": 0,
    "sort": {"field": "updated_at", "direction": "desc"}
})

# For hierarchies, use specific depth limits

hierarchy = await orchestrator.get_task_hierarchy(
    root_task_id="epic_user_system",
    max_depth=3,  

# Limit depth

    include_completed=False  

# Exclude completed tasks

)

```text

#

#

# Problem: Memory Issues with Large Hierarchies

```text

MemoryError: Task hierarchy too large to load

```text

**Solution**: Use streaming or pagination for large hierarchies:

```text
python
async def process_large_hierarchy(root_task_id: str, processor_func):
    """Process large hierarchy in chunks."""
    
    processed_count = 0
    page_size = 100
    current_page = 0
    
    while True:
        

# Get tasks in chunks

        tasks_chunk = await orchestrator.query_tasks({
            "filters": {"parent_task_id": root_task_id},
            "limit": page_size,
            "offset": current_page * page_size
        })
        
        if not tasks_chunk:
            break
        
        

# Process chunk

        for task in tasks_chunk:
            await processor_func(task)
            processed_count += 1
        
        current_page += 1
    
    return processed_count

```text

#

# Template Issues

#

#

# Problem: Template Parameter Validation

```text

Error: Required template parameter 'feature_name' missing

```text

**Solution**: Implement robust parameter validation:

```text
python
def validate_template_parameters(template_id: str, parameters: dict):
    """Validate template parameters against schema."""
    
    template = get_template(template_id)
    schema = template.parameters_schema
    
    

# Check required parameters

    required_params = schema.get("required", [])
    missing_params = [p for p in required_params if p not in parameters]
    
    if missing_params:
        raise ValueError(f"Missing required parameters: {missing_params}")
    
    

# Validate parameter types and values

    properties = schema.get("properties", {})
    for param, value in parameters.items():
        if param in properties:
            param_spec = properties[param]
            
            

# Type validation

            expected_type = param_spec.get("type")
            if expected_type == "string" and not isinstance(value, str):
                raise ValueError(f"Parameter {param} must be a string")
            
            

# Enum validation

            enum_values = param_spec.get("enum")
            if enum_values and value not in enum_values:
                raise ValueError(f"Parameter {param} must be one of: {enum_values}")
    
    return True

```text

#

#

# Problem: Template Not Found

```text

Error: Template 'feature_development_v3' not found

```text

**Solution**: Implement template discovery and fallback:

```text
python
async def create_from_template_with_fallback(template_id: str, parameters: dict):
    """Create from template with fallback to similar templates."""
    
    try:
        

# Try to get exact template

        template = await orchestrator.get_template(template_id)
        return await orchestrator.create_from_template(template_id, parameters)
    
    except TemplateNotFoundError:
        

# Look for similar templates

        similar_templates = await orchestrator.find_similar_templates(template_id)
        
        if similar_templates:
            fallback_template = similar_templates[0]
            print(f"Template {template_id} not found. Using {fallback_template.template_id} instead.")
            return await orchestrator.create_from_template(fallback_template.template_id, parameters)
        else:
            

# Create basic task structure manually

            return await create_basic_task_structure(parameters)

```text

#

# API and Tool Issues

#

#

# Problem: MCP Tool Timeout

```text

Error: MCP tool call timed out after 30 seconds

```text

**Solution**: Implement timeout handling and retry logic:

```text
python
import asyncio
from typing import Optional

async def robust_mcp_call(tool_name: str, arguments: dict, max_retries: int = 3, timeout: int = 60):
    """Make MCP tool call with timeout and retry logic."""
    
    for attempt in range(max_retries):
        try:
            

# Make MCP call with timeout

            result = await asyncio.wait_for(
                mcp_call(tool_name, arguments),
                timeout=timeout
            )
            return result
            
        except asyncio.TimeoutError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  

# Exponential backoff

                print(f"Tool call timed out. Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_time)
            else:
                raise TimeoutError(f"Tool call failed after {max_retries} attempts")
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Tool call failed: {e}. Retrying...")
                await asyncio.sleep(1)
            else:
                raise

```text

#

#

# Problem: Invalid MCP Tool Arguments

```text

Error: Invalid argument 'task_type' for tool 'orchestrator_create_generic_task'

```text

**Solution**: Validate arguments before making tool calls:

```text
python
def validate_mcp_tool_arguments(tool_name: str, arguments: dict):
    """Validate MCP tool arguments against expected schema."""
    
    tool_schemas = {
        "orchestrator_create_generic_task": {
            "required": ["task_type"],
            "optional": ["attributes", "parent_task_id", "dependencies"]
        },
        "orchestrator_query_tasks": {
            "required": [],
            "optional": ["filters", "sort", "limit", "offset", "include_hierarchy"]
        }
    }
    
    if tool_name not in tool_schemas:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    schema = tool_schemas[tool_name]
    
    

# Check required arguments

    missing_required = [arg for arg in schema["required"] if arg not in arguments]
    if missing_required:
        raise ValueError(f"Missing required arguments for {tool_name}: {missing_required}")
    
    

# Check for unexpected arguments

    all_valid_args = schema["required"] + schema["optional"]
    unexpected_args = [arg for arg in arguments if arg not in all_valid_args]
    if unexpected_args:
        raise ValueError(f"Unexpected arguments for {tool_name}: {unexpected_args}")
    
    return True

```text

#

# Database and Persistence Issues

#

#

# Problem: Database Connection Errors

```text

Error: Unable to connect to database

```text

**Solution**: Implement connection retry and health checks:

```text
python
async def ensure_database_connection():
    """Ensure database connection is healthy."""
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            

# Test database connection

            await orchestrator.health_check()
            return True
            
        except DatabaseConnectionError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Database connection failed. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise DatabaseConnectionError("Unable to establish database connection after retries")

```text

#

#

# Problem: Task State Corruption

```text

Error: Task state inconsistent with database

```text

**Solution**: Implement state validation and recovery:

```text
python
async def validate_and_fix_task_state(task_id: str):
    """Validate task state and fix inconsistencies."""
    
    

# Get task from cache and database

    cached_task = await orchestrator.get_task_from_cache(task_id)
    db_task = await orchestrator.get_task_from_db(task_id)
    
    if not db_task:
        raise ValueError(f"Task {task_id} not found in database")
    
    if cached_task and cached_task.updated_at != db_task.updated_at:
        print(f"Task {task_id} state inconsistency detected. Refreshing from database.")
        
        

# Clear cache and reload from database

        await orchestrator.clear_task_cache(task_id)
        refreshed_task = await orchestrator.get_task(task_id)
        
        return refreshed_task
    
    return db_task

```text

#

# Debug Tools and Diagnostics

#

#

# Task State Inspector

```text
python
async def inspect_task_state(task_id: str):
    """Comprehensive task state inspection for debugging."""
    
    inspection_report = {
        "task_id": task_id,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    try:
        

# Basic task retrieval

        task = await orchestrator.get_task(task_id)
        inspection_report["task_found"] = True
        inspection_report["task_data"] = {
            "task_type": task.task_type,
            "status": task.status,
            "parent_task_id": task.parent_task_id,
            "dependencies_count": len(task.dependencies),
            "created_at": task.created_at.isoformat() if task.created_at else None
        }
        
        

# Parent task validation

        if task.parent_task_id:
            parent = await orchestrator.get_task(task.parent_task_id)
            inspection_report["checks"]["parent_exists"] = parent is not None
        
        

# Dependencies validation

        dependency_issues = []
        for dep in task.dependencies:
            dep_task = await orchestrator.get_task(dep.dependency_task_id)
            if not dep_task:
                dependency_issues.append(f"Missing dependency: {dep.dependency_task_id}")
        
        inspection_report["checks"]["dependency_issues"] = dependency_issues
        
        

# Circular dependency check

        try:
            await check_circular_dependency(task_id, task_id)
            inspection_report["checks"]["circular_dependencies"] = False
        except CircularDependencyError:
            inspection_report["checks"]["circular_dependencies"] = True
        
    except Exception as e:
        inspection_report["task_found"] = False
        inspection_report["error"] = str(e)
    
    return inspection_report

```text

#

#

# Performance Diagnostics

```text
python
async def diagnose_performance_issues():
    """Diagnose common performance issues."""
    
    diagnostics = {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {}
    }
    
    

# Task count metrics

    total_tasks = await orchestrator.count_tasks()
    active_tasks = await orchestrator.count_tasks({"status": "active"})
    
    diagnostics["metrics"]["total_tasks"] = total_tasks
    diagnostics["metrics"]["active_tasks"] = active_tasks
    
    

# Large hierarchy detection

    large_hierarchies = await orchestrator.find_large_hierarchies(threshold=100)
    diagnostics["metrics"]["large_hierarchies"] = len(large_hierarchies)
    
    

# Database performance

    query_time = await measure_query_performance()
    diagnostics["metrics"]["avg_query_time_ms"] = query_time
    
    

# Recommendations

    recommendations = []
    if total_tasks > 10000:
        recommendations.append("Consider archiving old completed tasks")
    if len(large_hierarchies) > 5:
        recommendations.append("Large hierarchies detected - consider breaking them down")
    if query_time > 1000:
        recommendations.append("Slow queries detected - check database indexes")
    
    diagnostics["recommendations"] = recommendations
    
    return diagnostics

```text

#

# Getting Help

#

#

# Debug Mode

Enable debug mode for detailed logging:

```text
python
import logging

# Enable debug logging

logging.getLogger("mcp_task_orchestrator").setLevel(logging.DEBUG)

# Create task with debug info

task = await orchestrator.create_task_with_debug(task_data)

```text

#

#

# Health Check

Run comprehensive health check:

```text
python
health_status = await orchestrator.comprehensive_health_check()
print(f"System health: {health_status}")
```text

#

#

# Support Information

When reporting issues, include:

1. **Task Orchestrator version**: `await orchestrator.get_version()`

2. **Task details**: Use `inspect_task_state()` function above

3. **System metrics**: Use `diagnose_performance_issues()` function

4. **Error logs**: Full error messages and stack traces

5. **Reproduction steps**: Minimal code to reproduce the issue

---

**Related Documentation**:

- **Previous**: [Complex Workflows](complex-workflows.md)

- **Back to**: [Getting Started](getting-started.md)

- **See also**: [API Quick Reference](../../../../referenceapi-reference.md)
