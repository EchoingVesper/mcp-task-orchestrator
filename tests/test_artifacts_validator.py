"""
Test script to verify that the SubTask model correctly handles both string and list artifacts.

This script tests that the validator we added to the SubTask model correctly
converts a single string into a list of strings for the artifacts field.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_task_orchestrator.orchestrator.models import SubTask, SpecialistType, TaskResult


def test_subtask_artifacts_validator():
    """Test that the SubTask model correctly handles both string and list artifacts."""
    print("\n=== Testing SubTask Artifacts Validator ===")
    
    # Test with a single string
    subtask_string = SubTask(
        task_id="test_task_1",
        title="Test Task with String Artifact",
        description="A test task with a single string artifact",
        specialist_type=SpecialistType.IMPLEMENTER,
        estimated_effort="low",
        artifacts="single_artifact.py"
    )
    
    print(f"SubTask with string artifact: {subtask_string.artifacts}")
    assert isinstance(subtask_string.artifacts, list), "Artifacts should be a list"
    assert len(subtask_string.artifacts) == 1, "Artifacts list should have 1 item"
    assert subtask_string.artifacts[0] == "single_artifact.py", "Artifact content should match"
    
    # Test with a list of strings
    subtask_list = SubTask(
        task_id="test_task_2",
        title="Test Task with List Artifacts",
        description="A test task with a list of artifacts",
        specialist_type=SpecialistType.IMPLEMENTER,
        estimated_effort="medium",
        artifacts=["artifact1.py", "artifact2.py", "artifact3.py"]
    )
    
    print(f"SubTask with list artifacts: {subtask_list.artifacts}")
    assert isinstance(subtask_list.artifacts, list), "Artifacts should be a list"
    assert len(subtask_list.artifacts) == 3, "Artifacts list should have 3 items"
    
    # Test with empty list
    subtask_empty = SubTask(
        task_id="test_task_3",
        title="Test Task with Empty Artifacts",
        description="A test task with empty artifacts",
        specialist_type=SpecialistType.IMPLEMENTER,
        estimated_effort="low"
    )
    
    print(f"SubTask with default artifacts: {subtask_empty.artifacts}")
    assert isinstance(subtask_empty.artifacts, list), "Artifacts should be a list"
    assert len(subtask_empty.artifacts) == 0, "Artifacts list should be empty"
    
    print("All SubTask artifacts tests passed!")


def test_taskresult_artifacts_validator():
    """Test that the TaskResult model correctly handles both string and list artifacts."""
    print("\n=== Testing TaskResult Artifacts Validator ===")
    
    # Test with a single string
    result_string = TaskResult(
        task_id="test_result_1",
        content="Test result content",
        artifacts="single_result_artifact.py"
    )
    
    print(f"TaskResult with string artifact: {result_string.artifacts}")
    assert isinstance(result_string.artifacts, list), "Artifacts should be a list"
    assert len(result_string.artifacts) == 1, "Artifacts list should have 1 item"
    assert result_string.artifacts[0] == "single_result_artifact.py", "Artifact content should match"
    
    # Test with a list of strings
    result_list = TaskResult(
        task_id="test_result_2",
        content="Test result content",
        artifacts=["result1.py", "result2.py", "result3.py"]
    )
    
    print(f"TaskResult with list artifacts: {result_list.artifacts}")
    assert isinstance(result_list.artifacts, list), "Artifacts should be a list"
    assert len(result_list.artifacts) == 3, "Artifacts list should have 3 items"
    
    print("All TaskResult artifacts tests passed!")


if __name__ == "__main__":
    try:
        test_subtask_artifacts_validator()
        test_taskresult_artifacts_validator()
        print("\nALL TESTS PASSED: Artifacts validators are working correctly")
        sys.exit(0)
    except AssertionError as e:
        print(f"\nTEST FAILED: {str(e)}")
        sys.exit(1)
