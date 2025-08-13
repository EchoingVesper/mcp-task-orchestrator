"""
Unit tests for Generic Task Repository.

Tests async database operations, query performance, and error handling.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List
import tempfile
import os

# from mcp_task_orchestrator.db.generic_repository import  # TODO: Complete this import
# from mcp_task_orchestrator.orchestrator.generic_models import  # TODO: Complete this import


@pytest.fixture
async def test_db():
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db_url = f"sqlite:///{db_path}"
    repo = GenericTaskRepository(db_url)
    
    # Create schema
    from mcp_task_orchestrator.db.models import Base
    from sqlalchemy import create_engine
    engine = create_engine(db_url)
    
    # Execute the generic task schema
    schema_path = os.path.join(
        os.path.dirname(__file__), 
        '../../mcp_task_orchestrator/db/generic_task_schema.sql'
    )
    
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema creation
        with engine.connect() as conn:
            for statement in schema_sql.split(';'):
                if statement.strip():
                    try:
                        conn.execute(statement)
                    except Exception:
                        # Ignore trigger creation errors in test
                        if 'CREATE TRIGGER' not in statement:
                            raise
    
    yield repo
    
    # Cleanup
    await repo.dispose()
    os.unlink(db_path)


@pytest.mark.asyncio
class TestTaskCRUD:
    """Test basic CRUD operations."""
    
    async def test_create_task(self, test_db):
        """Test creating a task."""
        task = GenericTask(
            task_id="test_1",
            title="Test Task",
            description="A test task",
            hierarchy_path="/test_1"
        )
        
        created = await test_db.create_task(task)
        assert created.task_id == "test_1"
        
        # Verify in database
        retrieved = await test_db.get_task("test_1")
        assert retrieved is not None
        assert retrieved.title == "Test Task"
    
    async def test_create_task_with_attributes(self, test_db):
        """Test creating a task with attributes."""
        task = GenericTask(
            task_id="test_2",
            title="Task with Attributes",
            description="Test",
            hierarchy_path="/test_2"
        )
        
        task.add_attribute("priority", "high", AttributeType.STRING)
        task.add_attribute("points", 5, AttributeType.NUMBER)
        
        await test_db.create_task(task)
        
        retrieved = await test_db.get_task("test_2")
        assert len(retrieved.attributes) == 2
        assert retrieved.get_attribute("priority") == "high"
        assert retrieved.get_attribute("points") == 5.0
    
    async def test_update_task(self, test_db):
        """Test updating a task."""
        # Create initial task
        task = GenericTask(
            task_id="test_3",
            title="Original Title",
            description="Original description",
            hierarchy_path="/test_3"
        )
        await test_db.create_task(task)
        
        # Update task
        task.title = "Updated Title"
        task.status = TaskStatus.ACTIVE
        task.lifecycle_stage = LifecycleStage.ACTIVE
        
        updated = await test_db.update_task(task)
        
        # Verify update
        retrieved = await test_db.get_task("test_3")
        assert retrieved.title == "Updated Title"
        assert retrieved.status == TaskStatus.ACTIVE
    
    async def test_delete_task_soft(self, test_db):
        """Test soft deleting a task."""
        task = GenericTask(
            task_id="test_4",
            title="To Delete",
            description="Test",
            hierarchy_path="/test_4"
        )
        await test_db.create_task(task)
        
        # Soft delete
        deleted = await test_db.delete_task("test_4", hard_delete=False)
        assert deleted
        
        # Should not be retrievable
        retrieved = await test_db.get_task("test_4")
        assert retrieved is None
    
    async def test_task_not_found(self, test_db):
        """Test retrieving non-existent task."""
        task = await test_db.get_task("non_existent")
        assert task is None


@pytest.mark.asyncio
class TestHierarchyOperations:
    """Test hierarchical task operations."""
    
    async def test_create_hierarchy(self, test_db):
        """Test creating a task hierarchy."""
        # Create parent
        parent = GenericTask(
            task_id="parent_1",
            title="Parent Task",
            description="Parent",
            hierarchy_path="/parent_1"
        )
        await test_db.create_task(parent)
        
        # Create children
        for i in range(3):
            child = GenericTask(
                task_id=f"child_{i}",
                parent_task_id="parent_1",
                title=f"Child {i}",
                description="Child task",
                hierarchy_path=f"/parent_1/child_{i}",
                hierarchy_level=1,
                position_in_parent=i
            )
            await test_db.create_task(child)
        
        # Get parent with children
        parent_with_children = await test_db.get_task("parent_1", include_children=True)
        assert len(parent_with_children.children) == 3
        assert parent_with_children.children[0].task_id == "child_0"
    
    async def test_get_subtree(self, test_db):
        """Test getting task subtree."""
        # Create hierarchy
        root = GenericTask(
            task_id="root",
            title="Root",
            description="Root task",
            hierarchy_path="/root"
        )
        await test_db.create_task(root)
        
        # Create two levels of children
        for i in range(2):
            child = GenericTask(
                task_id=f"child_{i}",
                parent_task_id="root",
                title=f"Child {i}",
                description="Level 1",
                hierarchy_path=f"/root/child_{i}",
                hierarchy_level=1
            )
            await test_db.create_task(child)
            
            # Grandchildren
            for j in range(2):
                grandchild = GenericTask(
                    task_id=f"grandchild_{i}_{j}",
                    parent_task_id=f"child_{i}",
                    title=f"Grandchild {i}-{j}",
                    description="Level 2",
                    hierarchy_path=f"/root/child_{i}/grandchild_{i}_{j}",
                    hierarchy_level=2
                )
                await test_db.create_task(grandchild)
        
        # Get full subtree
        subtree = await test_db.get_subtree("root")
        assert len(subtree) == 6  # 2 children + 4 grandchildren
        
        # Get subtree with max depth
        subtree_depth_1 = await test_db.get_subtree("root", max_depth=1)
        assert len(subtree_depth_1) == 2  # Only direct children
    
    async def test_get_ancestors(self, test_db):
        """Test getting task ancestors."""
        # Create three-level hierarchy
        await test_db.create_task(GenericTask(
            task_id="level0",
            title="Level 0",
            description="Root",
            hierarchy_path="/level0"
        ))
        
        await test_db.create_task(GenericTask(
            task_id="level1",
            parent_task_id="level0",
            title="Level 1",
            description="Child",
            hierarchy_path="/level0/level1",
            hierarchy_level=1
        ))
        
        await test_db.create_task(GenericTask(
            task_id="level2",
            parent_task_id="level1",
            title="Level 2",
            description="Grandchild",
            hierarchy_path="/level0/level1/level2",
            hierarchy_level=2
        ))
        
        # Get ancestors
        ancestors = await test_db.get_ancestors("level2")
        assert len(ancestors) == 2
        assert ancestors[0].task_id == "level0"
        assert ancestors[1].task_id == "level1"
    
    async def test_move_task(self, test_db):
        """Test moving a task to a new parent."""
        # Create initial hierarchy
        await test_db.create_task(GenericTask(
            task_id="parent_a",
            title="Parent A",
            description="First parent",
            hierarchy_path="/parent_a"
        ))
        
        await test_db.create_task(GenericTask(
            task_id="parent_b",
            title="Parent B",
            description="Second parent",
            hierarchy_path="/parent_b"
        ))
        
        await test_db.create_task(GenericTask(
            task_id="moveable",
            parent_task_id="parent_a",
            title="Moveable Task",
            description="Task to move",
            hierarchy_path="/parent_a/moveable",
            hierarchy_level=1
        ))
        
        # Add a child to moveable
        await test_db.create_task(GenericTask(
            task_id="moveable_child",
            parent_task_id="moveable",
            title="Child of Moveable",
            description="Should move with parent",
            hierarchy_path="/parent_a/moveable/moveable_child",
            hierarchy_level=2
        ))
        
        # Move task
        moved = await test_db.move_task("moveable", "parent_b")
        assert moved.parent_task_id == "parent_b"
        assert moved.hierarchy_path == "/parent_b/moveable"
        
        # Check child was updated too
        child = await test_db.get_task("moveable_child")
        assert child.hierarchy_path == "/parent_b/moveable/moveable_child"
    
    async def test_move_task_cycle_detection(self, test_db):
        """Test that moving a task to its descendant is prevented."""
        # Create hierarchy
        await test_db.create_task(GenericTask(
            task_id="parent",
            title="Parent",
            description="Parent",
            hierarchy_path="/parent"
        ))
        
        await test_db.create_task(GenericTask(
            task_id="child",
            parent_task_id="parent",
            title="Child",
            description="Child",
            hierarchy_path="/parent/child",
            hierarchy_level=1
        ))
        
        # Try to move parent under child (should fail)
        with pytest.raises(ValueError, match="cycle"):
            await test_db.move_task("parent", "child")


@pytest.mark.asyncio
class TestDependencyOperations:
    """Test dependency management."""
    
    async def test_add_dependency(self, test_db):
        """Test adding dependencies between tasks."""
        # Create tasks
        await test_db.create_task(GenericTask(
            task_id="prereq",
            title="Prerequisite",
            description="Must complete first",
            hierarchy_path="/prereq"
        ))
        
        await test_db.create_task(GenericTask(
            task_id="dependent",
            title="Dependent",
            description="Depends on prereq",
            hierarchy_path="/dependent"
        ))
        
        # Add dependency
        dep = TaskDependency(
            dependent_task_id="dependent",
            prerequisite_task_id="prereq",
            dependency_type=DependencyType.COMPLETION
        )
        
        created_dep = await test_db.add_dependency(dep)
        assert created_dep.dependent_task_id == "dependent"
        
        # Verify dependency is loaded with task
        task = await test_db.get_task("dependent")
        assert len(task.dependencies) == 1
        assert task.dependencies[0].prerequisite_task_id == "prereq"
    
    async def test_dependency_cycle_detection(self, test_db):
        """Test that circular dependencies are prevented."""
        # Create three tasks
        for task_id in ["task_a", "task_b", "task_c"]:
            await test_db.create_task(GenericTask(
                task_id=task_id,
                title=f"Task {task_id}",
                description="Test",
                hierarchy_path=f"/{task_id}"
            ))
        
        # Create chain: A -> B -> C
        await test_db.add_dependency(TaskDependency(
            dependent_task_id="task_b",
            prerequisite_task_id="task_a",
            dependency_type=DependencyType.COMPLETION
        ))
        
        await test_db.add_dependency(TaskDependency(
            dependent_task_id="task_c",
            prerequisite_task_id="task_b",
            dependency_type=DependencyType.COMPLETION
        ))
        
        # Try to create cycle: C -> A (should fail)
        with pytest.raises(CycleDetectedError):
            await test_db.add_dependency(TaskDependency(
                dependent_task_id="task_a",
                prerequisite_task_id="task_c",
                dependency_type=DependencyType.COMPLETION
            ))
    
    async def test_check_dependencies(self, test_db):
        """Test checking if dependencies are satisfied."""
        # Create tasks
        await test_db.create_task(GenericTask(
            task_id="prereq_1",
            title="Prereq 1",
            description="Test",
            hierarchy_path="/prereq_1",
            status=TaskStatus.COMPLETED
        ))
        
        await test_db.create_task(GenericTask(
            task_id="prereq_2",
            title="Prereq 2",
            description="Test",
            hierarchy_path="/prereq_2",
            status=TaskStatus.PENDING
        ))
        
        task = GenericTask(
            task_id="main_task",
            title="Main Task",
            description="Has dependencies",
            hierarchy_path="/main_task"
        )
        await test_db.create_task(task)
        
        # Add dependencies
        await test_db.add_dependency(TaskDependency(
            dependent_task_id="main_task",
            prerequisite_task_id="prereq_1",
            dependency_type=DependencyType.COMPLETION,
            auto_satisfy=True
        ))
        
        await test_db.add_dependency(TaskDependency(
            dependent_task_id="main_task",
            prerequisite_task_id="prereq_2",
            dependency_type=DependencyType.COMPLETION
        ))
        
        # Check dependencies
        satisfied, unsatisfied = await test_db.check_dependencies("main_task")
        assert not satisfied
        assert len(unsatisfied) == 1
        assert unsatisfied[0].prerequisite_task_id == "prereq_2"
    
    async def test_get_dependency_graph(self, test_db):
        """Test getting the dependency graph."""
        # Create a small project structure
        tasks = [
            ("design", "Design Phase"),
            ("backend", "Backend Implementation"),
            ("frontend", "Frontend Implementation"),
            ("testing", "Testing Phase"),
            ("deploy", "Deployment")
        ]
        
        for task_id, title in tasks:
            await test_db.create_task(GenericTask(
                task_id=task_id,
                title=title,
                description="Test",
                hierarchy_path=f"/{task_id}"
            ))
        
        # Create dependencies
        deps = [
            ("backend", "design"),
            ("frontend", "design"),
            ("testing", "backend"),
            ("testing", "frontend"),
            ("deploy", "testing")
        ]
        
        for dependent, prerequisite in deps:
            await test_db.add_dependency(TaskDependency(
                dependent_task_id=dependent,
                prerequisite_task_id=prerequisite,
                dependency_type=DependencyType.COMPLETION
            ))
        
        # Get dependency graph
        graph = await test_db.get_dependency_graph()
        
        assert len(graph) == 4  # 4 tasks have dependencies
        assert set(graph["backend"]) == {"design"}
        assert set(graph["testing"]) == {"backend", "frontend"}
        assert set(graph["deploy"]) == {"testing"}


@pytest.mark.asyncio
class TestQueryOperations:
    """Test query and search operations."""
    
    async def test_query_by_status(self, test_db):
        """Test querying tasks by status."""
        # Create tasks with different statuses
        statuses = [
            TaskStatus.PENDING,
            TaskStatus.ACTIVE,
            TaskStatus.ACTIVE,
            TaskStatus.COMPLETED
        ]
        
        for i, status in enumerate(statuses):
            await test_db.create_task(GenericTask(
                task_id=f"task_{i}",
                title=f"Task {i}",
                description="Test",
                hierarchy_path=f"/task_{i}",
                status=status
            ))
        
        # Query active tasks
        active_tasks = await test_db.query_tasks({"status": TaskStatus.ACTIVE})
        assert len(active_tasks) == 2
        
        # Query completed tasks
        completed_tasks = await test_db.query_tasks({"status": TaskStatus.COMPLETED})
        assert len(completed_tasks) == 1
    
    async def test_query_with_pagination(self, test_db):
        """Test paginated queries."""
        # Create 10 tasks
        for i in range(10):
            await test_db.create_task(GenericTask(
                task_id=f"task_{i:02d}",
                title=f"Task {i}",
                description="Test",
                hierarchy_path=f"/task_{i:02d}"
            ))
        
        # Query with limit and offset
        page1 = await test_db.query_tasks({}, limit=5, offset=0)
        assert len(page1) == 5
        
        page2 = await test_db.query_tasks({}, limit=5, offset=5)
        assert len(page2) == 5
        
        # Ensure no overlap
        page1_ids = {t.task_id for t in page1}
        page2_ids = {t.task_id for t in page2}
        assert len(page1_ids & page2_ids) == 0
    
    async def test_search_by_attribute(self, test_db):
        """Test searching by attribute value."""
        # Create tasks with attributes
        for i in range(5):
            task = GenericTask(
                task_id=f"task_{i}",
                title=f"Task {i}",
                description="Test",
                hierarchy_path=f"/task_{i}"
            )
            
            # Add priority attribute
            priority = "high" if i < 2 else "normal"
            task.add_attribute("priority", priority, AttributeType.STRING, indexed=True)
            
            await test_db.create_task(task)
        
        # Search for high priority tasks
        high_priority = await test_db.search_by_attribute("priority", "high")
        assert len(high_priority) == 2
        
        # Search for normal priority tasks
        normal_priority = await test_db.search_by_attribute("priority", "normal")
        assert len(normal_priority) == 3


@pytest.mark.asyncio
class TestTemplateOperations:
    """Test template management."""
    
    async def test_save_and_retrieve_template(self, test_db):
        """Test saving and retrieving templates."""
        template = TaskTemplate(
            template_id="test_template",
            template_name="Test Template",
            template_category="testing",
            description="A test template",
            parameters=[
                TemplateParameter(
                    name="project_name",
                    type="string",
                    description="Project name",
                    required=True
                )
            ],
            task_structure={
                "root": {
                    "title": "Project {{project_name}}",
                    "description": "Root task for {{project_name}}",
                    "type": "standard"
                }
            }
        )
        
        # Save template
        saved = await test_db.save_template(template)
        assert saved.template_id == "test_template"
        
        # Retrieve template
        retrieved = await test_db.get_template("test_template")
        assert retrieved is not None
        assert retrieved.template_name == "Test Template"
        assert len(retrieved.parameters) == 1


@pytest.mark.asyncio
class TestPerformance:
    """Test performance characteristics."""
    
    async def test_bulk_insert_performance(self, test_db):
        """Test bulk insert performance."""
        import time
        
        start_time = time.time()
        
        # Create 100 tasks
        for i in range(100):
            task = GenericTask(
                task_id=f"perf_task_{i:03d}",
                title=f"Performance Task {i}",
                description="Performance test",
                hierarchy_path=f"/perf_task_{i:03d}"
            )
            await test_db.create_task(task)
        
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time
        assert elapsed < 5.0
        
        # Verify all created
        all_tasks = await test_db.query_tasks({})
        assert len(all_tasks) >= 100
    
    async def test_deep_hierarchy_performance(self, test_db):
        """Test performance with deep hierarchies."""
        import time
        
        # Create a 10-level deep hierarchy
        parent_id = None
        parent_path = ""
        
        for level in range(10):
            task_id = f"level_{level}"
            hierarchy_path = f"{parent_path}/{task_id}"
            
            task = GenericTask(
                task_id=task_id,
                parent_task_id=parent_id,
                title=f"Level {level}",
                description="Deep hierarchy test",
                hierarchy_path=hierarchy_path,
                hierarchy_level=level
            )
            
            await test_db.create_task(task)
            
            parent_id = task_id
            parent_path = hierarchy_path
        
        # Time subtree query
        start_time = time.time()
        subtree = await test_db.get_subtree("level_0")
        elapsed = time.time() - start_time
        
        assert len(subtree) == 9  # All descendants
        assert elapsed < 0.1  # Should be fast with proper indexing


if __name__ == "__main__":
    asyncio.run(pytest.main([__file__, "-v"]))