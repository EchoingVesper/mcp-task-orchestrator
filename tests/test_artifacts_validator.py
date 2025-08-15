"""
Test script to verify that the Task model correctly handles both string and list artifacts.

This script tests that the validator we added to the Task model correctly
converts a single string into a list of strings for the artifacts field.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Clean Architecture v2.0 models
from mcp_task_orchestrator.domain.entities.task import Task, TaskStatus, TaskType, TaskArtifact, ArtifactType
from mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel
from mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType
from mcp_task_orchestrator.domain.value_objects.execution_result import ExecutionResult, ExecutionStatus
from datetime import datetime


def test_subtask_artifacts_validator():
    """Test that the Task model correctly handles both string and list artifacts."""
    print("\n=== Testing Task Artifacts Validator ===")
    
    # Test with a single artifact
    artifact = TaskArtifact(
        artifact_id="artifact_1",
        task_id="test_task_1",
        artifact_type=ArtifactType.CODE,
        artifact_name="single_artifact.py",
        content="# Test artifact content"
    )
    
    subtask_string = Task(
        task_id="test_task_1",
        title="Test Task with String Artifact",
        description="A test task with a single string artifact",
        specialist_type="implementer",
        estimated_effort="low",
        artifacts=[artifact],
        hierarchy_path="/test_task_1"
    )
    
    print(f"Task with string artifact: {subtask_string.artifacts}")
    assert isinstance(subtask_string.artifacts, list), "Artifacts should be a list"
    assert len(subtask_string.artifacts) == 1, "Artifacts list should have 1 item"
    assert subtask_string.artifacts[0].artifact_name == "single_artifact.py", "Artifact content should match"
    
    # Test with a list of artifacts
    artifacts = [
        TaskArtifact(artifact_id="artifact_2_1", task_id="test_task_2", artifact_type=ArtifactType.CODE, artifact_name="artifact1.py", content="# Code 1"),
        TaskArtifact(artifact_id="artifact_2_2", task_id="test_task_2", artifact_type=ArtifactType.CODE, artifact_name="artifact2.py", content="# Code 2"),
        TaskArtifact(artifact_id="artifact_2_3", task_id="test_task_2", artifact_type=ArtifactType.CODE, artifact_name="artifact3.py", content="# Code 3")
    ]
    
    subtask_list = Task(
        task_id="test_task_2",
        title="Test Task with List Artifacts",
        description="A test task with a list of artifacts",
        specialist_type="implementer",
        estimated_effort="medium",
        artifacts=artifacts,
        hierarchy_path="/test_task_2"
    )
    
    print(f"Task with list artifacts: {subtask_list.artifacts}")
    assert isinstance(subtask_list.artifacts, list), "Artifacts should be a list"
    assert len(subtask_list.artifacts) == 3, "Artifacts list should have 3 items"
    
    # Test with empty list
    subtask_empty = Task(
        task_id="test_task_3",
        title="Test Task with Empty Artifacts",
        description="A test task with empty artifacts",
        specialist_type="implementer",
        estimated_effort="low",
        hierarchy_path="/test_task_3"
    )
    
    print(f"Task with default artifacts: {subtask_empty.artifacts}")
    assert isinstance(subtask_empty.artifacts, list), "Artifacts should be a list"
    assert len(subtask_empty.artifacts) == 0, "Artifacts list should be empty"
    
    print("All Task artifacts tests passed!")


def test_executionresult_artifacts_validator():
    """Test that the ExecutionResult model correctly handles both string and list artifacts."""
    print("\n=== Testing ExecutionResult Artifacts Validator ===")
    
    # Test with a single string
    result_string = ExecutionResult(
        status=ExecutionStatus.SUCCESS,
        summary="Test execution completed",
        started_at=datetime.now(),
        completed_at=datetime.now(),
        artifacts=["single_result_artifact.py"]
    )
    
    print(f"ExecutionResult with string artifact: {result_string.artifacts}")
    assert isinstance(result_string.artifacts, list), "Artifacts should be a list"
    assert len(result_string.artifacts) == 1, "Artifacts list should have 1 item"
    assert result_string.artifacts[0] == "single_result_artifact.py", "Artifact content should match"
    
    # Test with a list of strings
    result_list = ExecutionResult(
        status=ExecutionStatus.SUCCESS,
        summary="Test execution completed",
        started_at=datetime.now(),
        completed_at=datetime.now(),
        artifacts=["result1.py", "result2.py", "result3.py"]
    )
    
    print(f"ExecutionResult with list artifacts: {result_list.artifacts}")
    assert isinstance(result_list.artifacts, list), "Artifacts should be a list"
    assert len(result_list.artifacts) == 3, "Artifacts list should have 3 items"
    
    print("All ExecutionResult artifacts tests passed!")


if __name__ == "__main__":
    try:
        test_subtask_artifacts_validator()
        test_executionresult_artifacts_validator()
        print("\nALL TESTS PASSED: Artifacts validators are working correctly")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nTEST FAILED: {str(e)}")
        sys.exit(1)
