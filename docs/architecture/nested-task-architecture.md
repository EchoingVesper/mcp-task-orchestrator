# Nested Task Architecture Design

> **Document Type**: Architecture Specification  
> **Version**: 1.0.0  
> **Created**: 2025-05-30  
> **Target Release**: 1.5.0+  
> **Status**: Architecture Design Phase

## Overview

The Nested Task Architecture enhances the MCP Task Orchestrator's ability to handle complex, hierarchical task structures with recursive subtask management, sophisticated dependency handling, and improved state management for multi-level task breakdowns.

## Current Architecture Analysis

### Existing Task Model
```
Current Task Structure:
├── Parent Task (task_id)
├── Subtask 1 (subtask_id, parent_id)
├── Subtask 2 (subtask_id, parent_id)
└── Subtask N (subtask_id, parent_id)
```

### Current Limitations
- Single-level parent-child relationships only
- No support for subtask-of-subtask hierarchies
- Limited dependency modeling between nested levels
- Difficulty handling complex project structures
- No recursive progress aggregation
- State management complexity for deep hierarchies

## Enhanced Nested Architecture

### Multi-Level Hierarchy Support
```
Enhanced Task Structure:
Project Task (Level 0)
├── Epic 1 (Level 1)
│   ├── Feature 1.1 (Level 2)
│   │   ├── Story 1.1.1 (Level 3)
│   │   ├── Story 1.1.2 (Level 3)
│   │   └── Story 1.1.3 (Level 3)
│   └── Feature 1.2 (Level 2)
│       ├── Story 1.2.1 (Level 3)
│       └── Story 1.2.2 (Level 3)
└── Epic 2 (Level 1)
    └── Feature 2.1 (Level 2)
        └── Story 2.1.1 (Level 3)
```

### Task Hierarchy Tree Model
```python
class TaskNode:
    def __init__(self, task_id, level=0, max_depth=None):
        self.task_id = task_id
        self.level = level
        self.max_depth = max_depth
        self.parent = None
        self.children = []
        self.dependencies = []
        self.state = TaskState.PENDING
        
    @property
    def is_leaf(self):
        return len(self.children) == 0
    
    @property
    def is_root(self):
        return self.parent is None
    
    @property
    def depth(self):
        if self.is_leaf:
            return 0
        return max(child.depth for child in self.children) + 1
```

## Enhanced Database Schema

### Core Task Hierarchy Table
```sql
-- Enhanced tasks table with hierarchy support
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    parent_task_id TEXT,
    root_task_id TEXT,  -- Reference to top-level task
    level INTEGER DEFAULT 0,
    hierarchy_path TEXT,  -- Materialized path: /root/level1/level2
    title TEXT NOT NULL,
    description TEXT,
    specialist_type TEXT,
    status TEXT DEFAULT 'pending',
    complexity_level TEXT DEFAULT 'moderate',
    estimated_effort INTEGER,
    actual_effort INTEGER,
    progress_percentage REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Hierarchy constraints
    FOREIGN KEY (parent_task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
    FOREIGN KEY (root_task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
    
    -- Ensure level consistency
    CHECK (level >= 0),
    CHECK (parent_task_id IS NULL OR level > 0)
);

-- Task dependencies with support for cross-hierarchy dependencies
CREATE TABLE task_dependencies (
    dependency_id TEXT PRIMARY KEY,
    dependent_task_id TEXT NOT NULL,
    prerequisite_task_id TEXT NOT NULL,
    dependency_type TEXT DEFAULT 'sequential',  -- sequential, parallel, conditional
    blocking_level TEXT DEFAULT 'hard',  -- hard, soft, optional
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (dependent_task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
    
    -- Prevent circular dependencies
    CHECK (dependent_task_id != prerequisite_task_id)
);

-- Task hierarchy metadata and constraints
CREATE TABLE task_hierarchy_rules (
    rule_id TEXT PRIMARY KEY,
    root_task_id TEXT NOT NULL,
    max_depth INTEGER DEFAULT 5,
    max_children_per_level INTEGER DEFAULT 20,
    allowed_specialist_types JSON,
    auto_progression_rules JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (root_task_id) REFERENCES tasks (task_id) ON DELETE CASCADE
);
```

### Materialized Path for Efficient Queries
```sql
-- Efficient hierarchy queries using materialized paths
-- Example: '/project_1/epic_1/feature_1_1/story_1_1_1'

-- Find all descendants of a task
SELECT * FROM tasks 
WHERE hierarchy_path LIKE '/project_1/epic_1/%'
ORDER BY level, hierarchy_path;

-- Find all ancestors of a task
WITH RECURSIVE ancestors AS (
    SELECT task_id, parent_task_id, level, hierarchy_path
    FROM tasks 
    WHERE task_id = 'story_1_1_1'
    
    UNION ALL
    
    SELECT t.task_id, t.parent_task_id, t.level, t.hierarchy_path
    FROM tasks t
    INNER JOIN ancestors a ON t.task_id = a.parent_task_id
)
SELECT * FROM ancestors;
```

## Recursive Task Operations

### Task Creation with Hierarchy
```python
class NestedTaskOrchestrator:
    def __init__(self, db_manager, max_depth=5):
        self.db = db_manager
        self.max_depth = max_depth
    
    async def create_nested_task(self, task_definition, parent_task_id=None, level=0):
        """Create a task with potential subtasks at any hierarchy level."""
        
        if level > self.max_depth:
            raise HierarchyDepthExceededError(f"Maximum depth {self.max_depth} exceeded")
        
        # Create main task
        task = await self.create_task(
            title=task_definition.title,
            description=task_definition.description,
            parent_task_id=parent_task_id,
            level=level
        )
        
        # Update hierarchy path
        await self.update_hierarchy_path(task.task_id)
        
        # Create subtasks recursively
        if task_definition.subtasks:
            for subtask_def in task_definition.subtasks:
                await self.create_nested_task(
                    task_definition=subtask_def,
                    parent_task_id=task.task_id,
                    level=level + 1
                )
        
        return task
    
    async def update_hierarchy_path(self, task_id):
        """Update materialized path for efficient hierarchy queries."""
        task = await self.db.get_task(task_id)
        
        if task.parent_task_id:
            parent = await self.db.get_task(task.parent_task_id)
            hierarchy_path = f"{parent.hierarchy_path}/{task_id}"
        else:
            hierarchy_path = f"/{task_id}"
        
        await self.db.update_task(task_id, {'hierarchy_path': hierarchy_path})
```

### Progress Aggregation
```python
async def calculate_recursive_progress(self, task_id):
    """Calculate progress percentage for a task based on all descendants."""
    
    # Get all descendant tasks
    descendants = await self.db.get_descendant_tasks(task_id)
    
    if not descendants:
        # Leaf task - return its own progress
        task = await self.db.get_task(task_id)
        return task.progress_percentage
    
    # Calculate weighted progress based on estimated effort
    total_effort = 0
    completed_effort = 0
    
    for desc_task in descendants:
        if desc_task.estimated_effort:
            total_effort += desc_task.estimated_effort
            completed_effort += (desc_task.progress_percentage / 100.0) * desc_task.estimated_effort
    
    if total_effort == 0:
        # Equal weighting if no effort estimates
        return sum(t.progress_percentage for t in descendants) / len(descendants)
    
    return (completed_effort / total_effort) * 100.0
```

## Advanced Dependency Management

### Cross-Hierarchy Dependencies
```python
class DependencyManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    async def add_dependency(self, dependent_task_id, prerequisite_task_id, 
                           dependency_type='sequential', blocking_level='hard'):
        """Add dependency between tasks at any hierarchy level."""
        
        # Validate no circular dependencies
        if await self.would_create_cycle(dependent_task_id, prerequisite_task_id):
            raise CircularDependencyError("Dependency would create a cycle")
        
        # Check cross-hierarchy dependency rules
        await self.validate_cross_hierarchy_dependency(dependent_task_id, prerequisite_task_id)
        
        dependency = TaskDependency(
            dependent_task_id=dependent_task_id,
            prerequisite_task_id=prerequisite_task_id,
            dependency_type=dependency_type,
            blocking_level=blocking_level
        )
        
        await self.db.save_dependency(dependency)
    
    async def would_create_cycle(self, dependent_id, prerequisite_id):
        """Check if adding dependency would create circular reference."""
        visited = set()
        
        async def has_path(from_task, to_task):
            if from_task == to_task:
                return True
            if from_task in visited:
                return False
            
            visited.add(from_task)
            dependencies = await self.db.get_task_dependencies(from_task)
            
            for dep in dependencies:
                if await has_path(dep.prerequisite_task_id, to_task):
                    return True
            
            return False
        
        return await has_path(prerequisite_id, dependent_id)
```

## Execution Strategies

### Depth-First Execution
```python
async def execute_depth_first(self, root_task_id):
    """Execute tasks in depth-first order, completing subtasks before parents."""
    
    execution_plan = await self.build_depth_first_plan(root_task_id)
    
    for task_batch in execution_plan:
        # Execute tasks in parallel within each batch
        await self.execute_task_batch(task_batch)
        
        # Update parent progress after each batch
        await self.update_ancestor_progress(task_batch)

async def build_depth_first_plan(self, root_task_id):
    """Build execution plan prioritizing leaf tasks first."""
    task_tree = await self.load_task_tree(root_task_id)
    execution_batches = []
    
    # Group tasks by reverse level (deepest first)
    tasks_by_level = defaultdict(list)
    for task in task_tree.all_nodes():
        tasks_by_level[task.level].append(task)
    
    # Execute from deepest level to root
    max_level = max(tasks_by_level.keys())
    for level in range(max_level, -1, -1):
        level_tasks = tasks_by_level[level]
        
        # Sort by dependencies within level
        sorted_tasks = await self.topological_sort(level_tasks)
        execution_batches.append(sorted_tasks)
    
    return execution_batches
```

### Breadth-First Execution
```python
async def execute_breadth_first(self, root_task_id):
    """Execute tasks level by level, completing parents before children."""
    
    execution_plan = await self.build_breadth_first_plan(root_task_id)
    
    for task_batch in execution_plan:
        # Execute all tasks at current level
        await self.execute_task_batch(task_batch)
        
        # Create subtasks for next level based on completed tasks
        await self.create_next_level_subtasks(task_batch)
```

## State Management

### Hierarchical State Transitions
```python
class HierarchicalStateManager:
    def __init__(self):
        self.state_rules = {
            'pending': ['in_progress', 'cancelled'],
            'in_progress': ['completed', 'blocked', 'cancelled'],
            'blocked': ['in_progress', 'cancelled'],
            'completed': [],  # Terminal state
            'cancelled': []   # Terminal state
        }
    
    async def transition_task_state(self, task_id, new_state):
        """Transition task state with cascade rules for hierarchy."""
        
        task = await self.db.get_task(task_id)
        current_state = task.status
        
        # Validate state transition
        if new_state not in self.state_rules[current_state]:
            raise InvalidStateTransitionError(
                f"Cannot transition from {current_state} to {new_state}"
            )
        
        # Update task state
        await self.db.update_task(task_id, {'status': new_state})
        
        # Apply cascade rules
        await self.apply_state_cascade_rules(task_id, new_state)
    
    async def apply_state_cascade_rules(self, task_id, new_state):
        """Apply state change cascade rules up and down hierarchy."""
        
        if new_state == 'completed':
            # Check if all siblings are complete, then complete parent
            await self.try_complete_parent(task_id)
            
            # Cancel any blocked subtasks
            await self.cancel_blocked_descendants(task_id)
        
        elif new_state == 'blocked':
            # Block all dependent descendants
            await self.block_dependent_descendants(task_id)
        
        elif new_state == 'cancelled':
            # Cancel all incomplete descendants
            await self.cancel_incomplete_descendants(task_id)
```

## Performance Optimizations

### Lazy Loading and Caching
```python
class HierarchyCache:
    def __init__(self, cache_size=1000):
        self.task_cache = LRUCache(cache_size)
        self.hierarchy_cache = LRUCache(cache_size // 2)
    
    async def get_task_with_hierarchy(self, task_id, depth=None):
        """Get task with cached hierarchy information."""
        cache_key = f"{task_id}:depth:{depth}"
        
        if cache_key in self.hierarchy_cache:
            return self.hierarchy_cache[cache_key]
        
        # Load from database
        task_tree = await self.load_task_hierarchy(task_id, depth)
        self.hierarchy_cache[cache_key] = task_tree
        
        return task_tree
    
    async def invalidate_task_hierarchy(self, task_id):
        """Invalidate cache entries related to task hierarchy."""
        # Remove all cache entries containing this task_id
        keys_to_remove = [
            key for key in self.hierarchy_cache.keys() 
            if task_id in key
        ]
        
        for key in keys_to_remove:
            del self.hierarchy_cache[key]
```

## Integration with A2A Framework

### Hierarchical Task Distribution
```python
async def distribute_hierarchy_across_agents(self, root_task_id):
    """Distribute different hierarchy levels across specialized agents."""
    
    task_tree = await self.load_task_tree(root_task_id)
    
    # Strategy: Different agents handle different levels
    level_assignments = {
        0: 'orchestrator_agent',    # Root project management
        1: 'epic_manager_agent',    # Epic coordination
        2: 'feature_agent',         # Feature development
        3: 'story_implementer'      # Story implementation
    }
    
    for task in task_tree.all_nodes():
        target_agent = level_assignments.get(task.level, 'general_agent')
        
        await self.a2a_client.assign_task(
            agent_id=target_agent,
            task_id=task.task_id,
            task_context=task.to_context(),
            hierarchy_context=self.build_hierarchy_context(task)
        )
```

## Testing Strategies

### Hierarchy-Specific Test Cases
```python
class NestedTaskTests:
    async def test_deep_hierarchy_creation(self):
        """Test creation of deep task hierarchies."""
        # Create 5-level deep task structure
        root_task = await self.create_test_hierarchy(depth=5, width=3)
        
        # Verify all levels created correctly
        assert await self.count_tasks_at_level(root_task.id, 0) == 1
        assert await self.count_tasks_at_level(root_task.id, 1) == 3
        assert await self.count_tasks_at_level(root_task.id, 2) == 9
        # ... and so on
    
    async def test_circular_dependency_prevention(self):
        """Test that circular dependencies are prevented."""
        task_a = await self.create_task("Task A")
        task_b = await self.create_task("Task B", parent=task_a)
        task_c = await self.create_task("Task C", parent=task_b)
        
        # This should raise CircularDependencyError
        with pytest.raises(CircularDependencyError):
            await self.dependency_manager.add_dependency(
                dependent_task_id=task_a.id,
                prerequisite_task_id=task_c.id
            )
    
    async def test_progress_aggregation(self):
        """Test recursive progress calculation."""
        root_task = await self.create_test_hierarchy_with_progress()
        
        calculated_progress = await self.calculate_recursive_progress(root_task.id)
        expected_progress = self.manual_progress_calculation(root_task)
        
        assert abs(calculated_progress - expected_progress) < 0.1
```

## Migration Strategy

### Backward Compatibility
- Existing single-level tasks continue to work unchanged
- Gradual migration to nested structures as needed
- Optional depth limits for performance control
- Legacy API endpoints maintain compatibility

### Migration Tools
```python
async def migrate_flat_to_nested(self, task_ids, grouping_strategy):
    """Migrate existing flat task structures to nested hierarchies."""
    
    if grouping_strategy == 'by_specialist':
        # Group tasks by specialist type into feature groups
        groups = await self.group_by_specialist_type(task_ids)
    elif grouping_strategy == 'by_complexity':
        # Create epics for complex tasks, stories for simple ones
        groups = await self.group_by_complexity(task_ids)
    
    for group_name, task_group in groups.items():
        # Create parent task for group
        parent_task = await self.create_task(
            title=f"Epic: {group_name}",
            description=f"Auto-generated epic for {group_name} tasks"
        )
        
        # Move tasks under parent
        for task_id in task_group:
            await self.move_task_to_parent(task_id, parent_task.id)
```

---

## Implementation Roadmap

### Phase 1: Core Hierarchy (v1.5.0)
- Multi-level parent-child relationships
- Basic hierarchy queries and navigation
- Recursive progress calculation
- Enhanced database schema

### Phase 2: Advanced Dependencies (v1.6.0)
- Cross-hierarchy dependency support
- Circular dependency prevention
- Complex execution strategies
- State cascade management

### Phase 3: Performance & Scale (v1.7.0)
- Hierarchy caching and optimization
- Large-scale hierarchy management
- Advanced visualization tools
- Integration with A2A framework

---

*This architecture enables sophisticated project management capabilities while maintaining backward compatibility and providing clear migration paths for existing deployments.*