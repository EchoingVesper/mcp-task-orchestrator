"""
Unit tests for Generic Task Model Pydantic models.

Tests comprehensive validation, state machine logic, and model functionality.
"""

import pytest
from datetime import datetime, timedelta
import json
from typing import Dict, Any

from mcp_task_orchestrator.domain.entities.task import (
    Task, TaskAttribute, TaskDependency, TaskEvent, TaskArtifact,
    TaskTemplate, TemplateParameter,
    TaskType, TaskStatus, LifecycleStage, DependencyType, DependencyStatus,
    QualityGateLevel, EventType, EventCategory, AttributeType, ArtifactType,
    LifecycleStateMachine
    # Note: create_task_from_breakdown, create_task_from_subtask removed - legacy models deprecated
)
from mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel
from mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType


class TestTaskAttribute:
    """Test TaskAttribute model."""
    
    def test_attribute_creation(self):
        """Test basic attribute creation."""
        attr = TaskAttribute(
            attribute_name="priority",
            attribute_value="high",
            attribute_type=AttributeType.STRING,
            attribute_category="metadata"
        )
        assert attr.attribute_name == "priority"
        assert attr.get_typed_value() == "high"
    
    def test_number_attribute(self):
        """Test number type validation and parsing."""
        attr = TaskAttribute(
            attribute_name="score",
            attribute_value="95.5",
            attribute_type=AttributeType.NUMBER
        )
        assert attr.get_typed_value() == 95.5
        
        # Test invalid number
        with pytest.raises(ValueError):
            TaskAttribute(
                attribute_name="score",
                attribute_value="not-a-number",
                attribute_type=AttributeType.NUMBER
            )
    
    def test_boolean_attribute(self):
        """Test boolean type validation and parsing."""
        for value, expected in [("true", True), ("false", False), ("1", True), ("0", False)]:
            attr = TaskAttribute(
                attribute_name="is_critical",
                attribute_value=value,
                attribute_type=AttributeType.BOOLEAN
            )
            assert attr.get_typed_value() == expected
    
    def test_date_attribute(self):
        """Test date type validation and parsing."""
        now = datetime.now()
        attr = TaskAttribute(
            attribute_name="deadline",
            attribute_value=now.isoformat(),
            attribute_type=AttributeType.DATE
        )
        parsed = attr.get_typed_value()
        assert isinstance(parsed, datetime)
        assert parsed.isoformat() == now.isoformat()
    
    def test_json_attribute(self):
        """Test JSON type validation and parsing."""
        data = {"key": "value", "count": 42}
        attr = TaskAttribute(
            attribute_name="config",
            attribute_value=json.dumps(data),
            attribute_type=AttributeType.JSON
        )
        assert attr.get_typed_value() == data


class TestTaskDependency:
    """Test TaskDependency model."""
    
    def test_basic_dependency(self):
        """Test basic dependency creation."""
        dep = TaskDependency(
            dependent_task_id="task_2",
            prerequisite_task_id="task_1",
            dependency_type=DependencyType.COMPLETION
        )
        assert dep.is_mandatory
        assert dep.dependency_status == DependencyStatus.PENDING
    
    def test_data_dependency_validation(self):
        """Test data dependency requires artifact references."""
        # Should fail without artifact info
        with pytest.raises(ValueError):
            TaskDependency(
                dependent_task_id="task_2",
                prerequisite_task_id="task_1",
                dependency_type=DependencyType.DATA
            )
        
        # Should succeed with artifact info
        dep = TaskDependency(
            dependent_task_id="task_2",
            prerequisite_task_id="task_1",
            dependency_type=DependencyType.DATA,
            output_artifact_ref="output_file",
            input_parameter_name="input_data"
        )
        assert dep.output_artifact_ref == "output_file"
    
    def test_waiver_validation(self):
        """Test dependency waiver requires complete information."""
        # Should fail with partial waiver info
        with pytest.raises(ValueError):
            TaskDependency(
                dependent_task_id="task_2",
                prerequisite_task_id="task_1",
                dependency_type=DependencyType.COMPLETION,
                waived_at=datetime.now()
            )
        
        # Should succeed with complete waiver info
        dep = TaskDependency(
            dependent_task_id="task_2",
            prerequisite_task_id="task_1",
            dependency_type=DependencyType.COMPLETION,
            waived_at=datetime.now(),
            waived_by="admin",
            waiver_reason="Emergency override"
        )
        assert dep.dependency_status == DependencyStatus.WAIVED
    
    def test_can_satisfy(self):
        """Test dependency satisfaction logic."""
        dep = TaskDependency(
            dependent_task_id="task_2",
            prerequisite_task_id="task_1",
            dependency_type=DependencyType.COMPLETION
        )
        
        assert not dep.can_satisfy(TaskStatus.PENDING)
        assert not dep.can_satisfy(TaskStatus.ACTIVE)
        assert dep.can_satisfy(TaskStatus.COMPLETED)
        
        # Waived dependencies are always satisfied
        dep.dependency_status = DependencyStatus.WAIVED
        assert dep.can_satisfy(TaskStatus.PENDING)


class TestTaskEvent:
    """Test TaskEvent model."""
    
    def test_event_creation(self):
        """Test basic event creation."""
        event = TaskEvent(
            task_id="task_1",
            event_type=EventType.STATUS_CHANGED,
            event_category=EventCategory.LIFECYCLE,
            triggered_by="system"
        )
        assert event.task_id == "task_1"
        assert event.event_data == {}
    
    def test_event_data_parsing(self):
        """Test event data parsing from string."""
        # Test JSON string parsing
        event = TaskEvent(
            task_id="task_1",
            event_type=EventType.UPDATED,
            event_category=EventCategory.DATA,
            event_data='{"field": "value"}',
            triggered_by="user"
        )
        assert event.event_data == {"field": "value"}
        
        # Test non-JSON string handling
        event = TaskEvent(
            task_id="task_1",
            event_type=EventType.COMMENT_ADDED,
            event_category=EventCategory.USER,
            event_data="plain text",
            triggered_by="user"
        )
        assert event.event_data == {"raw": "plain text"}


class TestLifecycleStateMachine:
    """Test lifecycle state machine."""
    
    def test_valid_transitions(self):
        """Test valid state transitions."""
        assert LifecycleStateMachine.can_transition(
            LifecycleStage.CREATED, LifecycleStage.PLANNING
        )
        assert LifecycleStateMachine.can_transition(
            LifecycleStage.ACTIVE, LifecycleStage.COMPLETED
        )
        assert LifecycleStateMachine.can_transition(
            LifecycleStage.BLOCKED, LifecycleStage.ACTIVE
        )
    
    def test_invalid_transitions(self):
        """Test invalid state transitions."""
        assert not LifecycleStateMachine.can_transition(
            LifecycleStage.COMPLETED, LifecycleStage.ACTIVE
        )
        assert not LifecycleStateMachine.can_transition(
            LifecycleStage.ARCHIVED, LifecycleStage.ACTIVE
        )
    
    def test_get_allowed_transitions(self):
        """Test getting allowed transitions."""
        allowed = LifecycleStateMachine.get_allowed_transitions(LifecycleStage.ACTIVE)
        assert LifecycleStage.BLOCKED in allowed
        assert LifecycleStage.COMPLETED in allowed
        assert LifecycleStage.CREATED not in allowed


class TestTask:
    """Test Task model."""
    
    def test_basic_task_creation(self):
        """Test creating a basic task."""
        task = Task(
            task_id="task_1",
            title="Test Task",
            description="A test task",
            hierarchy_path="/task_1"
        )
        assert task.task_id == "task_1"
        assert task.task_type == TaskType.STANDARD
        assert task.status == TaskStatus.PENDING
        assert task.lifecycle_stage == LifecycleStage.CREATED
    
    def test_hierarchy_path_validation(self):
        """Test hierarchy path validation."""
        # Should auto-fix missing leading slash
        task = Task(
            task_id="task_1",
            title="Test",
            description="Test",
            hierarchy_path="task_1"
        )
        assert task.hierarchy_path == "/task_1"
        
        # Should auto-append task_id if missing
        task = Task(
            task_id="task_2",
            title="Test",
            description="Test",
            hierarchy_path="/parent"
        )
        assert task.hierarchy_path == "/parent/task_2"
    
    def test_lifecycle_consistency(self):
        """Test status and lifecycle stage consistency."""
        # Active status should set active lifecycle
        task = Task(
            task_id="task_1",
            title="Test",
            description="Test",
            hierarchy_path="/task_1",
            status=TaskStatus.ACTIVE,
            lifecycle_stage=LifecycleStage.CREATED  # Wrong stage
        )
        assert task.lifecycle_stage == LifecycleStage.ACTIVE  # Auto-corrected
    
    def test_attribute_management(self):
        """Test adding and retrieving attributes."""
        task = Task(
            task_id="task_1",
            title="Test",
            description="Test",
            hierarchy_path="/task_1"
        )
        
        # Add string attribute
        task.add_attribute("priority", "high", AttributeType.STRING, "metadata")
        assert task.get_attribute("priority") == "high"
        
        # Add number attribute
        task.add_attribute("score", 95.5, AttributeType.NUMBER)
        assert task.get_attribute("score") == 95.5
        
        # Add JSON attribute
        config = {"key": "value"}
        task.add_attribute("config", config, AttributeType.JSON)
        assert task.get_attribute("config") == config
        
        # Non-existent attribute
        assert task.get_attribute("non_existent") is None
    
    def test_dependency_management(self):
        """Test adding and checking dependencies."""
        task = Task(
            task_id="task_2",
            title="Dependent Task",
            description="Test",
            hierarchy_path="/task_2"
        )
        
        # Add dependency
        dep = task.add_dependency("task_1", DependencyType.COMPLETION)
        assert len(task.dependencies) == 1
        assert dep.prerequisite_task_id == "task_1"
        
        # Check unsatisfied dependencies
        satisfied, unsatisfied = task.check_dependencies_satisfied()
        assert not satisfied
        assert len(unsatisfied) == 1
        
        # Satisfy dependency
        task.dependencies[0].dependency_status = DependencyStatus.SATISFIED
        satisfied, unsatisfied = task.check_dependencies_satisfied()
        assert satisfied
        assert len(unsatisfied) == 0
    
    def test_event_recording(self):
        """Test recording events."""
        task = Task(
            task_id="task_1",
            title="Test",
            description="Test",
            hierarchy_path="/task_1"
        )
        
        event = task.record_event(
            EventType.STATUS_CHANGED,
            EventCategory.LIFECYCLE,
            triggered_by="user",
            data={"old": "pending", "new": "active"}
        )
        
        assert len(task.events) == 1
        assert event.event_data["old"] == "pending"
    
    def test_storage_conversion(self):
        """Test converting to storage format."""
        task = Task(
            task_id="task_1",
            title="Test",
            description="Test",
            hierarchy_path="/task_1",
            context={"key": "value"},
            configuration={"setting": True}
        )
        
        # Add runtime data that shouldn't be stored
        task.add_attribute("test", "value")
        task.add_dependency("task_0")
        
        storage_dict = task.to_dict_for_storage()
        
        # Check runtime collections are excluded
        assert 'attributes' not in storage_dict
        assert 'dependencies' not in storage_dict
        
        # Check datetime conversion
        assert isinstance(storage_dict['created_at'], str)
        
        # Check dict to JSON conversion
        assert isinstance(storage_dict['context'], str)
        assert json.loads(storage_dict['context']) == {"key": "value"}


class TestTaskTemplate:
    """Test TaskTemplate model."""
    
    def test_template_creation(self):
        """Test creating a task template."""
        template = TaskTemplate(
            template_id="template_1",
            template_name="Code Review Template",
            template_category="development",
            description="Standard code review process",
            task_structure={
                "review": {
                    "title": "Code Review for {{feature_name}}",
                    "description": "Review code changes for {{feature_name}}",
                    "type": "review",
                    "specialist_type": "reviewer",
                    "children": {
                        "test": {
                            "title": "Test {{feature_name}}",
                            "description": "Run tests for the feature",
                            "type": "testing",
                            "specialist_type": "tester"
                        }
                    }
                }
            }
        )
        
        template.parameters = [
            TemplateParameter(
                name="feature_name",
                type="string",
                description="Name of the feature being reviewed",
                required=True
            )
        ]
        
        assert template.template_name == "Code Review Template"
        assert len(template.parameters) == 1
    
    def test_parameter_validation(self):
        """Test template parameter validation."""
        template = TaskTemplate(
            template_id="template_1",
            template_name="Test Template",
            template_category="test",
            description="Test",
            task_structure={},
            parameters=[
                TemplateParameter(
                    name="required_param",
                    type="string",
                    description="Required parameter",
                    required=True
                ),
                TemplateParameter(
                    name="optional_param",
                    type="string",
                    description="Optional parameter",
                    required=False,
                    default="default_value"
                )
            ]
        )
        
        # Test missing required parameter
        with pytest.raises(ValueError):
            template.validate_parameters({})
        
        # Test with required parameter
        validated = template.validate_parameters({"required_param": "value"})
        assert validated["required_param"] == "value"
        assert validated["optional_param"] == "default_value"
    
    def test_template_instantiation(self):
        """Test creating tasks from template."""
        template = TaskTemplate(
            template_id="review_template",
            template_name="Review Template",
            template_category="development",
            description="Code review template",
            task_structure={
                "review": {
                    "title": "Review {{feature}}",
                    "description": "Review changes for {{feature}}",
                    "type": "review",
                    "specialist_type": "reviewer",
                    "children": {
                        "test": {
                            "title": "Test {{feature}}",
                            "description": "Test the {{feature}} implementation",
                            "type": "testing",
                            "specialist_type": "tester"
                        },
                        "docs": {
                            "title": "Document {{feature}}",
                            "description": "Update documentation for {{feature}}",
                            "type": "documentation",
                            "specialist_type": "documenter"
                        }
                    }
                }
            },
            parameters=[
                TemplateParameter(
                    name="feature",
                    type="string",
                    description="Feature name",
                    required=True
                )
            ]
        )
        
        # Instantiate template
        tasks = template.instantiate({"feature": "user-auth"})
        
        assert len(tasks) == 3  # Parent + 2 children
        
        # Check parameter substitution
        review_task = tasks[0]
        assert "user-auth" in review_task.title
        assert review_task.task_type == TaskType.REVIEW
        
        # Check hierarchy
        child_tasks = [t for t in tasks if t.parent_task_id == review_task.task_id]
        assert len(child_tasks) == 2
        
        # Check usage tracking
        assert template.usage_count == 1
        assert template.last_used_at is not None


class TestBackwardCompatibility:
    """Test backward compatibility functions."""
    
    def test_convert_task_breakdown(self):
        """Test converting TaskBreakdown to Task."""
        breakdown = TaskBreakdown(
            parent_task_id="old_task_1",
            description="Implement new feature",
            complexity=ComplexityLevel.COMPLEX,
            context="Additional context",
            subtasks=[]
        )
        
        generic = create_generic_task_from_breakdown(breakdown)
        
        assert generic.task_id == "old_task_1"
        assert generic.task_type == TaskType.BREAKDOWN
        assert generic.complexity == ComplexityLevel.COMPLEX
        assert generic.parent_task_id is None
        assert generic.hierarchy_path == "/old_task_1"
        assert generic.context["original_context"] == "Additional context"
    
    def test_convert_subtask(self):
        """Test converting SubTask to Task."""
        subtask = SubTask(
            task_id="sub_1",
            title="Implement feature",
            description="Implement the new feature",
            specialist_type=SpecialistType.IMPLEMENTER,
            dependencies=["dep_1", "dep_2"],
            estimated_effort="2 days",
            status=TaskStatus.ACTIVE,
            results="Partial implementation",
            artifacts=["file1.py", {"type": "doc", "content": "docs"}]
        )
        
        generic = create_generic_task_from_subtask(
            subtask, "parent_1", "/parent_1", position=0
        )
        
        assert generic.task_id == "sub_1"
        assert generic.parent_task_id == "parent_1"
        assert generic.hierarchy_path == "/parent_1/sub_1"
        assert generic.specialist_type == SpecialistType.IMPLEMENTER
        assert generic.lifecycle_stage == LifecycleStage.ACTIVE
        
        # Check dependencies conversion
        assert len(generic.dependencies) == 2
        assert generic.dependencies[0].prerequisite_task_id == "dep_1"
        
        # Check artifacts conversion
        assert len(generic.artifacts) == 2
        assert generic.artifacts[0].content == "file1.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])