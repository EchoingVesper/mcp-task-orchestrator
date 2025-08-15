#!/usr/bin/env python3
"""
GitHub Issues #46-50 Implementation Validation

This script analyzes the actual implementation state of all 5 GitHub issue fixes
and generates a comprehensive validation report showing what's implemented, 
what's missing, and what needs to be completed.

Validates:
- Issue #46: MockTask JSON serialization (compatibility layer)
- Issue #47: update_task response formatting (compatibility layer)  
- Issue #48: delete_task implementation (missing methods)
- Issue #49: cancel_task implementation (missing methods)
- Issue #50: query_tasks format mismatch (compatibility layer)
"""

import sys
import os
import json
import inspect
import importlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class ValidationResult:
    """Result of a validation check."""
    passed: bool
    message: str
    details: Dict[str, Any]
    recommendations: List[str]


@dataclass 
class IssueValidation:
    """Validation results for a single GitHub issue."""
    issue_id: str
    title: str
    worktree: str
    overall_status: str  # "IMPLEMENTED", "PARTIAL", "MISSING", "ERROR"
    validations: List[ValidationResult]
    implementation_score: float  # 0.0 to 1.0


class GitHubFixesValidator:
    """Validator for GitHub Issues #46-50 fixes."""
    
    def __init__(self, worktree_path: str):
        self.worktree_path = Path(worktree_path)
        self.worktree_name = self.worktree_path.name
        self.validation_results = {}
        
        # Set up import paths
        sys.path.insert(0, str(self.worktree_path))
    
    def validate_issue_46_mock_task_serialization(self) -> IssueValidation:
        """Validate Issue #46: MockTask JSON serialization."""
        validations = []
        
        # Check if ResponseFormatter exists
        try:
            from mcp_task_orchestrator.infrastructure.mcp.handlers.compatibility.response_formatter import ResponseFormatter
            validations.append(ValidationResult(
                passed=True,
                message="ResponseFormatter class found",
                details={"class": "ResponseFormatter", "module": "response_formatter"},
                recommendations=[]
            ))
            
            # Check if SerializationValidator exists
            try:
                from mcp_task_orchestrator.infrastructure.mcp.handlers.compatibility.serialization import SerializationValidator
                validations.append(ValidationResult(
                    passed=True,
                    message="SerializationValidator class found",
                    details={"class": "SerializationValidator", "module": "serialization"},
                    recommendations=[]
                ))
                
                # Test basic serialization functionality
                validator = SerializationValidator()
                test_data = {"test": datetime.now(), "nested": {"value": 42}}
                
                try:
                    result = validator.ensure_serializable(test_data)
                    json.dumps(result)  # Test actual JSON serialization
                    
                    validations.append(ValidationResult(
                        passed=True,
                        message="Serialization functionality works",
                        details={"test_passed": True, "result_type": type(result).__name__},
                        recommendations=[]
                    ))
                except Exception as e:
                    validations.append(ValidationResult(
                        passed=False,
                        message=f"Serialization functionality failed: {e}",
                        details={"error": str(e), "test_data": str(test_data)},
                        recommendations=["Fix serialization implementation", "Add error handling"]
                    ))
                
            except ImportError as e:
                validations.append(ValidationResult(
                    passed=False,
                    message=f"SerializationValidator not found: {e}",
                    details={"import_error": str(e)},
                    recommendations=["Implement SerializationValidator class"]
                ))
            
        except ImportError as e:
            validations.append(ValidationResult(
                passed=False,
                message=f"ResponseFormatter not found: {e}",
                details={"import_error": str(e)},
                recommendations=["Implement compatibility layer response formatter"]
            ))
        
        passed_count = sum(1 for v in validations if v.passed)
        score = passed_count / len(validations) if validations else 0.0
        
        if score >= 0.8:
            status = "IMPLEMENTED"
        elif score >= 0.5:
            status = "PARTIAL"
        elif score > 0:
            status = "MISSING"
        else:
            status = "ERROR"
        
        return IssueValidation(
            issue_id="issue_46",
            title="MockTask JSON Serialization",
            worktree=self.worktree_name,
            overall_status=status,
            validations=validations,
            implementation_score=score
        )
    
    def validate_issue_47_update_task_formatting(self) -> IssueValidation:
        """Validate Issue #47: update_task response formatting."""
        validations = []
        
        # Check if compatibility layer exists
        try:
            from mcp_task_orchestrator.infrastructure.mcp.handlers.compatibility.response_formatter import ResponseFormatter
            formatter = ResponseFormatter()
            
            # Check if format_update_response method exists
            if hasattr(formatter, 'format_update_response'):
                validations.append(ValidationResult(
                    passed=True,
                    message="format_update_response method found",
                    details={"method": "format_update_response", "class": "ResponseFormatter"},
                    recommendations=[]
                ))
                
                # Test method functionality
                try:
                    test_task = {"id": "test", "title": "Test Task", "status": "updated"}
                    test_changes = ["title", "status"]
                    
                    result = formatter.format_update_response(test_task, test_changes)
                    
                    # Validate response structure
                    required_fields = ["success", "task_id", "changes_applied", "operation", "timestamp"]
                    missing_fields = [f for f in required_fields if f not in result]
                    
                    if not missing_fields:
                        validations.append(ValidationResult(
                            passed=True,
                            message="format_update_response produces correct structure",
                            details={"required_fields": required_fields, "result_keys": list(result.keys())},
                            recommendations=[]
                        ))
                        
                        # Test JSON serialization
                        try:
                            json.dumps(result)
                            validations.append(ValidationResult(
                                passed=True,
                                message="Update response is JSON serializable",
                                details={"serializable": True},
                                recommendations=[]
                            ))
                        except Exception as e:
                            validations.append(ValidationResult(
                                passed=False,
                                message=f"Update response not JSON serializable: {e}",
                                details={"error": str(e)},
                                recommendations=["Fix serialization in response formatter"]
                            ))
                    else:
                        validations.append(ValidationResult(
                            passed=False,
                            message=f"Missing required fields in update response: {missing_fields}",
                            details={"missing_fields": missing_fields, "result": result},
                            recommendations=["Add missing fields to format_update_response"]
                        ))
                        
                except Exception as e:
                    validations.append(ValidationResult(
                        passed=False,
                        message=f"format_update_response failed: {e}",
                        details={"error": str(e)},
                        recommendations=["Fix format_update_response implementation"]
                    ))
            else:
                validations.append(ValidationResult(
                    passed=False,
                    message="format_update_response method not found",
                    details={"available_methods": [m for m in dir(formatter) if not m.startswith('_')]},
                    recommendations=["Implement format_update_response method"]
                ))
                
        except ImportError as e:
            validations.append(ValidationResult(
                passed=False,
                message=f"ResponseFormatter not available: {e}",
                details={"import_error": str(e)},
                recommendations=["Implement compatibility layer response formatter"]
            ))
        
        passed_count = sum(1 for v in validations if v.passed)
        score = passed_count / len(validations) if validations else 0.0
        
        if score >= 0.8:
            status = "IMPLEMENTED"
        elif score >= 0.5:
            status = "PARTIAL"
        elif score > 0:
            status = "MISSING"
        else:
            status = "ERROR"
        
        return IssueValidation(
            issue_id="issue_47", 
            title="update_task Response Formatting",
            worktree=self.worktree_name,
            overall_status=status,
            validations=validations,
            implementation_score=score
        )
    
    def validate_issue_48_delete_task_implementation(self) -> IssueValidation:
        """Validate Issue #48: delete_task implementation."""
        validations = []
        
        # Check TaskUseCase has delete_task method
        try:
            from mcp_task_orchestrator.application.usecases.manage_tasks import TaskUseCase
            
            if hasattr(TaskUseCase, 'delete_task'):
                validations.append(ValidationResult(
                    passed=True,
                    message="delete_task method found in TaskUseCase",
                    details={"class": "TaskUseCase", "method": "delete_task"},
                    recommendations=[]
                ))
                
                # Check method signature
                sig = inspect.signature(TaskUseCase.delete_task)
                params = list(sig.parameters.keys())
                expected_params = ['self', 'task_id', 'force', 'archive_instead']
                
                if all(param in params for param in expected_params):
                    validations.append(ValidationResult(
                        passed=True,
                        message="delete_task has correct signature",
                        details={"parameters": params, "expected": expected_params},
                        recommendations=[]
                    ))
                else:
                    missing = [p for p in expected_params if p not in params]
                    validations.append(ValidationResult(
                        passed=False,
                        message=f"delete_task missing parameters: {missing}",
                        details={"parameters": params, "missing": missing},
                        recommendations=["Update delete_task signature to include force and archive_instead parameters"]
                    ))
                
                # Check if method is async
                if inspect.iscoroutinefunction(TaskUseCase.delete_task):
                    validations.append(ValidationResult(
                        passed=True,
                        message="delete_task is async",
                        details={"async": True},
                        recommendations=[]
                    ))
                else:
                    validations.append(ValidationResult(
                        passed=False,
                        message="delete_task is not async",
                        details={"async": False},
                        recommendations=["Make delete_task async to match other use case methods"]
                    ))
                    
            else:
                validations.append(ValidationResult(
                    passed=False,
                    message="delete_task method not found in TaskUseCase",
                    details={"available_methods": [m for m in dir(TaskUseCase) if not m.startswith('_')]},
                    recommendations=["Implement delete_task method in TaskUseCase"]
                ))
                
        except ImportError as e:
            validations.append(ValidationResult(
                passed=False,
                message=f"TaskUseCase not available: {e}",
                details={"import_error": str(e)},
                recommendations=["Fix TaskUseCase import issues"]
            ))
        
        # Check repository interface
        try:
            from mcp_task_orchestrator.domain.repositories.task_repository import TaskRepository
            from mcp_task_orchestrator.domain.repositories.async_task_repository import AsyncTaskRepository
            
            # Check sync repository
            if hasattr(TaskRepository, 'delete_task'):
                validations.append(ValidationResult(
                    passed=True,
                    message="delete_task found in TaskRepository interface",
                    details={"interface": "TaskRepository"},
                    recommendations=[]
                ))
            else:
                validations.append(ValidationResult(
                    passed=False,
                    message="delete_task not found in TaskRepository interface",
                    details={"interface": "TaskRepository"},
                    recommendations=["Add delete_task to TaskRepository interface"]
                ))
            
            # Check async repository
            if hasattr(AsyncTaskRepository, 'delete_task'):
                validations.append(ValidationResult(
                    passed=True,
                    message="delete_task found in AsyncTaskRepository interface",
                    details={"interface": "AsyncTaskRepository"},
                    recommendations=[]
                ))
            else:
                validations.append(ValidationResult(
                    passed=False,
                    message="delete_task not found in AsyncTaskRepository interface",
                    details={"interface": "AsyncTaskRepository"},
                    recommendations=["Add delete_task to AsyncTaskRepository interface"]
                ))
            
        except ImportError as e:
            validations.append(ValidationResult(
                passed=False,
                message=f"Repository interfaces not available: {e}",
                details={"import_error": str(e)},
                recommendations=["Fix repository interface imports"]
            ))
        
        passed_count = sum(1 for v in validations if v.passed)
        score = passed_count / len(validations) if validations else 0.0
        
        if score >= 0.8:
            status = "IMPLEMENTED"
        elif score >= 0.5:
            status = "PARTIAL"
        elif score > 0:
            status = "MISSING"
        else:
            status = "ERROR"
        
        return IssueValidation(
            issue_id="issue_48",
            title="delete_task Implementation",
            worktree=self.worktree_name,
            overall_status=status,
            validations=validations,
            implementation_score=score
        )
    
    def validate_issue_49_cancel_task_implementation(self) -> IssueValidation:
        """Validate Issue #49: cancel_task implementation."""
        validations = []
        
        # Check TaskUseCase has cancel_task method
        try:
            from mcp_task_orchestrator.application.usecases.manage_tasks import TaskUseCase
            
            if hasattr(TaskUseCase, 'cancel_task'):
                validations.append(ValidationResult(
                    passed=True,
                    message="cancel_task method found in TaskUseCase",
                    details={"class": "TaskUseCase", "method": "cancel_task"},
                    recommendations=[]
                ))
                
                # Check method signature
                sig = inspect.signature(TaskUseCase.cancel_task)
                params = list(sig.parameters.keys())
                expected_params = ['self', 'task_id', 'reason', 'preserve_work']
                
                if all(param in params for param in expected_params):
                    validations.append(ValidationResult(
                        passed=True,
                        message="cancel_task has correct signature",
                        details={"parameters": params, "expected": expected_params},
                        recommendations=[]
                    ))
                else:
                    missing = [p for p in expected_params if p not in params]
                    validations.append(ValidationResult(
                        passed=False,
                        message=f"cancel_task missing parameters: {missing}",
                        details={"parameters": params, "missing": missing},
                        recommendations=["Update cancel_task signature to include reason and preserve_work parameters"]
                    ))
                
                # Check if method is async
                if inspect.iscoroutinefunction(TaskUseCase.cancel_task):
                    validations.append(ValidationResult(
                        passed=True,
                        message="cancel_task is async",
                        details={"async": True},
                        recommendations=[]
                    ))
                else:
                    validations.append(ValidationResult(
                        passed=False,
                        message="cancel_task is not async",
                        details={"async": False},
                        recommendations=["Make cancel_task async to match other use case methods"]
                    ))
                    
            else:
                validations.append(ValidationResult(
                    passed=False,
                    message="cancel_task method not found in TaskUseCase",
                    details={"available_methods": [m for m in dir(TaskUseCase) if not m.startswith('_')]},
                    recommendations=["Implement cancel_task method in TaskUseCase"]
                ))
                
        except ImportError as e:
            validations.append(ValidationResult(
                passed=False,
                message=f"TaskUseCase not available: {e}",
                details={"import_error": str(e)},
                recommendations=["Fix TaskUseCase import issues"]
            ))
        
        # Check repository interfaces (cancel_task is new, likely not in base interface)
        try:
            from mcp_task_orchestrator.domain.repositories.task_repository import TaskRepository
            from mcp_task_orchestrator.domain.repositories.async_task_repository import AsyncTaskRepository
            
            # Check if cancel_task exists in repositories
            sync_has_cancel = hasattr(TaskRepository, 'cancel_task')
            async_has_cancel = hasattr(AsyncTaskRepository, 'cancel_task')
            
            if sync_has_cancel:
                validations.append(ValidationResult(
                    passed=True,
                    message="cancel_task found in TaskRepository interface",
                    details={"interface": "TaskRepository"},
                    recommendations=[]
                ))
            else:
                validations.append(ValidationResult(
                    passed=False,
                    message="cancel_task not found in TaskRepository interface",
                    details={"interface": "TaskRepository"},
                    recommendations=["Add cancel_task to TaskRepository interface"]
                ))
            
            if async_has_cancel:
                validations.append(ValidationResult(
                    passed=True,
                    message="cancel_task found in AsyncTaskRepository interface",
                    details={"interface": "AsyncTaskRepository"},
                    recommendations=[]
                ))
            else:
                validations.append(ValidationResult(
                    passed=False,
                    message="cancel_task not found in AsyncTaskRepository interface",
                    details={"interface": "AsyncTaskRepository"},
                    recommendations=["Add cancel_task to AsyncTaskRepository interface"]
                ))
                
        except ImportError as e:
            validations.append(ValidationResult(
                passed=False,
                message=f"Repository interfaces not available: {e}",
                details={"import_error": str(e)},
                recommendations=["Fix repository interface imports"]
            ))
        
        passed_count = sum(1 for v in validations if v.passed)
        score = passed_count / len(validations) if validations else 0.0
        
        if score >= 0.8:
            status = "IMPLEMENTED"
        elif score >= 0.5:
            status = "PARTIAL"
        elif score > 0:
            status = "MISSING"
        else:
            status = "ERROR"
        
        return IssueValidation(
            issue_id="issue_49",
            title="cancel_task Implementation",
            worktree=self.worktree_name,
            overall_status=status,
            validations=validations,
            implementation_score=score
        )
    
    def validate_issue_50_query_tasks_format(self) -> IssueValidation:
        """Validate Issue #50: query_tasks format mismatch."""
        validations = []
        
        # Check if format_query_response exists
        try:
            from mcp_task_orchestrator.infrastructure.mcp.handlers.compatibility.response_formatter import ResponseFormatter
            formatter = ResponseFormatter()
            
            if hasattr(formatter, 'format_query_response'):
                validations.append(ValidationResult(
                    passed=True,
                    message="format_query_response method found",
                    details={"method": "format_query_response", "class": "ResponseFormatter"},
                    recommendations=[]
                ))
                
                # Test method functionality
                try:
                    test_tasks = [
                        {"id": "task1", "title": "Task 1", "metadata": "{}"},
                        {"id": "task2", "title": "Task 2", "metadata": "{}"}
                    ]
                    test_context = {"page_size": 2, "current_page": 1}
                    
                    result = formatter.format_query_response(test_tasks, test_context)
                    
                    # Validate response is dict (not list)
                    if isinstance(result, dict):
                        validations.append(ValidationResult(
                            passed=True,
                            message="format_query_response returns dict (not list)",
                            details={"result_type": "dict", "expected": "dict"},
                            recommendations=[]
                        ))
                        
                        # Check required fields
                        required_fields = ["success", "tasks", "total_count", "operation"]
                        missing_fields = [f for f in required_fields if f not in result]
                        
                        if not missing_fields:
                            validations.append(ValidationResult(
                                passed=True,
                                message="format_query_response has correct structure",
                                details={"required_fields": required_fields, "result_keys": list(result.keys())},
                                recommendations=[]
                            ))
                            
                            # Verify tasks field is list
                            if isinstance(result.get("tasks"), list):
                                validations.append(ValidationResult(
                                    passed=True,
                                    message="tasks field is list as expected",
                                    details={"tasks_type": "list", "tasks_count": len(result["tasks"])},
                                    recommendations=[]
                                ))
                            else:
                                validations.append(ValidationResult(
                                    passed=False,
                                    message=f"tasks field is {type(result.get('tasks')).__name__}, expected list",
                                    details={"tasks_type": type(result.get("tasks")).__name__},
                                    recommendations=["Fix tasks field to be list in format_query_response"]
                                ))
                        else:
                            validations.append(ValidationResult(
                                passed=False,
                                message=f"Missing required fields: {missing_fields}",
                                details={"missing_fields": missing_fields},
                                recommendations=["Add missing fields to format_query_response"]
                            ))
                    else:
                        validations.append(ValidationResult(
                            passed=False,
                            message=f"format_query_response returns {type(result).__name__}, expected dict",
                            details={"result_type": type(result).__name__, "expected": "dict"},
                            recommendations=["Change format_query_response to return dict instead of list"]
                        ))
                        
                except Exception as e:
                    validations.append(ValidationResult(
                        passed=False,
                        message=f"format_query_response failed: {e}",
                        details={"error": str(e)},
                        recommendations=["Fix format_query_response implementation"]
                    ))
            else:
                validations.append(ValidationResult(
                    passed=False,
                    message="format_query_response method not found",
                    details={"available_methods": [m for m in dir(formatter) if not m.startswith('_')]},
                    recommendations=["Implement format_query_response method"]
                ))
                
        except ImportError as e:
            validations.append(ValidationResult(
                passed=False,
                message=f"ResponseFormatter not available: {e}",
                details={"import_error": str(e)},
                recommendations=["Implement compatibility layer response formatter"]
            ))
        
        passed_count = sum(1 for v in validations if v.passed)
        score = passed_count / len(validations) if validations else 0.0
        
        if score >= 0.8:
            status = "IMPLEMENTED"
        elif score >= 0.5:
            status = "PARTIAL"
        elif score > 0:
            status = "MISSING"
        else:
            status = "ERROR"
        
        return IssueValidation(
            issue_id="issue_50",
            title="query_tasks Format Mismatch",
            worktree=self.worktree_name,
            overall_status=status,
            validations=validations,
            implementation_score=score
        )
    
    def validate_all_issues(self) -> Dict[str, IssueValidation]:
        """Validate all GitHub issues."""
        print(f"Validating GitHub Issues #46-50 fixes in {self.worktree_name}...")
        print("=" * 60)
        
        issue_validators = {
            "issue_46": self.validate_issue_46_mock_task_serialization,
            "issue_47": self.validate_issue_47_update_task_formatting,
            "issue_48": self.validate_issue_48_delete_task_implementation,
            "issue_49": self.validate_issue_49_cancel_task_implementation,
            "issue_50": self.validate_issue_50_query_tasks_format
        }
        
        results = {}
        
        for issue_id, validator in issue_validators.items():
            print(f"\nValidating {issue_id.upper()}...")
            try:
                result = validator()
                results[issue_id] = result
                
                # Print immediate feedback
                status_icon = "✅" if result.overall_status == "IMPLEMENTED" else \
                             "⚠️" if result.overall_status == "PARTIAL" else \
                             "❌" if result.overall_status == "MISSING" else "💥"
                             
                print(f"  {status_icon} {result.title}: {result.overall_status} ({result.implementation_score:.1%})")
                
                # Print key issues
                failed_validations = [v for v in result.validations if not v.passed]
                if failed_validations:
                    for validation in failed_validations[:2]:  # Show first 2 failures
                        print(f"    - {validation.message}")
                        
            except Exception as e:
                print(f"  💥 {issue_id.upper()}: ERROR - {e}")
                results[issue_id] = IssueValidation(
                    issue_id=issue_id,
                    title=f"Issue {issue_id}",
                    worktree=self.worktree_name,
                    overall_status="ERROR",
                    validations=[ValidationResult(
                        passed=False,
                        message=f"Validation failed: {e}",
                        details={"error": str(e)},
                        recommendations=["Fix validation errors"]
                    )],
                    implementation_score=0.0
                )
        
        return results
    
    def generate_comprehensive_report(self, results: Dict[str, IssueValidation]) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        # Calculate overall statistics
        total_issues = len(results)
        implemented_count = sum(1 for r in results.values() if r.overall_status == "IMPLEMENTED")
        partial_count = sum(1 for r in results.values() if r.overall_status == "PARTIAL")
        missing_count = sum(1 for r in results.values() if r.overall_status == "MISSING")
        error_count = sum(1 for r in results.values() if r.overall_status == "ERROR")
        
        average_score = sum(r.implementation_score for r in results.values()) / total_issues if total_issues > 0 else 0.0
        
        # Collect all recommendations
        all_recommendations = []
        for result in results.values():
            for validation in result.validations:
                all_recommendations.extend(validation.recommendations)
        
        # Deduplicate and prioritize recommendations
        unique_recommendations = list(set(all_recommendations))
        
        # Generate worktree-specific analysis
        worktree_analysis = {
            "compatibility_layer_ready": all(
                results.get(issue, IssueValidation("", "", "", "ERROR", [], 0.0)).overall_status == "IMPLEMENTED" 
                for issue in ["issue_46", "issue_47", "issue_50"]
            ),
            "missing_methods_ready": all(
                results.get(issue, IssueValidation("", "", "", "ERROR", [], 0.0)).overall_status == "IMPLEMENTED"
                for issue in ["issue_48", "issue_49"]
            )
        }
        
        report = {
            "metadata": {
                "worktree": self.worktree_name,
                "validation_timestamp": datetime.now().isoformat(),
                "validator_version": "1.0.0"
            },
            "summary": {
                "total_issues": total_issues,
                "implemented": implemented_count,
                "partial": partial_count,
                "missing": missing_count,
                "errors": error_count,
                "average_implementation_score": average_score,
                "overall_status": "READY" if implemented_count == total_issues else 
                                "NEEDS_WORK" if (implemented_count + partial_count) >= total_issues // 2 else
                                "NOT_READY"
            },
            "issue_details": {
                issue_id: {
                    "title": result.title,
                    "status": result.overall_status,
                    "score": result.implementation_score,
                    "validations": [
                        {
                            "passed": v.passed,
                            "message": v.message,
                            "details": v.details,
                            "recommendations": v.recommendations
                        }
                        for v in result.validations
                    ]
                }
                for issue_id, result in results.items()
            },
            "worktree_analysis": worktree_analysis,
            "recommendations": {
                "immediate_actions": [
                    rec for rec in unique_recommendations 
                    if any(word in rec.lower() for word in ["implement", "add", "create"])
                ],
                "fixes_needed": [
                    rec for rec in unique_recommendations
                    if any(word in rec.lower() for word in ["fix", "update", "change"])
                ],
                "all_recommendations": unique_recommendations
            }
        }
        
        return report


def main():
    """Main validation entry point."""
    if len(sys.argv) > 1:
        worktree_path = sys.argv[1]
    else:
        # Default to current directory if no path provided
        worktree_path = os.getcwd()
    
    validator = GitHubFixesValidator(worktree_path)
    
    try:
        # Run validation
        results = validator.validate_all_issues()
        
        # Generate report
        report = validator.generate_comprehensive_report(results)
        
        # Print summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        summary = report["summary"]
        print(f"Worktree: {validator.worktree_name}")
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Implementation Score: {summary['average_implementation_score']:.1%}")
        print(f"Issues Status: {summary['implemented']}/{summary['total_issues']} implemented, " +
              f"{summary['partial']} partial, {summary['missing']} missing, {summary['errors']} errors")
        
        # Print worktree analysis
        analysis = report["worktree_analysis"]
        print(f"\nWorktree Readiness:")
        print(f"  Compatibility Layer: {'✅' if analysis['compatibility_layer_ready'] else '❌'}")
        print(f"  Missing Methods: {'✅' if analysis['missing_methods_ready'] else '❌'}")
        
        # Print top recommendations
        recommendations = report["recommendations"]
        if recommendations["immediate_actions"]:
            print(f"\nImmediate Actions Needed:")
            for i, rec in enumerate(recommendations["immediate_actions"][:3], 1):
                print(f"  {i}. {rec}")
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"github_fixes_validation_{validator.worktree_name}_{timestamp}.json"
        report_path = Path(__file__).parent / report_filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\nDetailed report saved to: {report_path}")
        
        # Exit with appropriate code
        if summary["overall_status"] == "READY":
            sys.exit(0)
        elif summary["overall_status"] == "NEEDS_WORK":
            sys.exit(1)
        else:
            sys.exit(2)
        
    except Exception as e:
        print(f"\nValidation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()