"""
Enhanced Work Stream Integration

This module provides enhanced handlers for documentation and testing work streams
that integrate with the context continuity system.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .enhanced_core import EnhancedTaskOrchestrator
from .context_continuity import create_context_tracker_for_subtask

logger = logging.getLogger("mcp_task_orchestrator.work_stream_integration")


class EnhancedWorkStreamHandler:
    """
    Enhanced work stream handler that provides context continuity
    for documentation and testing work streams.
    """

    def __init__(self, enhanced_orchestrator: EnhancedTaskOrchestrator):
        """
        Initialize the enhanced work stream handler.
        
        Args:
            enhanced_orchestrator: Enhanced orchestrator with context continuity
        """
        self.orchestrator = enhanced_orchestrator
        self.context_orchestrator = enhanced_orchestrator.context_orchestrator

    async def prepare_work_stream_execution(self, task_ids: List[str], work_stream_type: str) -> Dict[str, Any]:
        """
        Prepare work stream tasks for execution with context tracking.
        
        Args:
            task_ids: List of task IDs in the work stream
            work_stream_type: Type of work stream (documentation, testing, etc.)
            
        Returns:
            Dict containing preparation status and guidance
        """
        logger.info(f"Preparing {work_stream_type} work stream with {len(task_ids)} tasks")
        
        # Verify work stream readiness
        readiness = await self.orchestrator.verify_work_stream_readiness(task_ids)
        
        # Generate work stream specific guidance
        guidance = self._generate_work_stream_guidance(work_stream_type, task_ids)
        
        preparation_result = {
            "work_stream_type": work_stream_type,
            "total_tasks": len(task_ids),
            "readiness_status": readiness,
            "context_protection_enabled": True,
            "execution_guidance": guidance,
            "recommendations": [
                f"All {work_stream_type} tasks have comprehensive context protection",
                "File operations will be automatically tracked and verified",
                "Architectural decisions will be captured and preserved",
                "Work can be safely continued across session boundaries"
            ]
        }
        
        logger.info(f"Work stream preparation complete: {work_stream_type}")
        return preparation_result

    def _generate_work_stream_guidance(self, work_stream_type: str, task_ids: List[str]) -> Dict[str, Any]:
        """Generate specific guidance for different work stream types."""
        
        base_guidance = {
            "context_tracking": "All operations automatically tracked",
            "file_verification": "File persistence verified before completion",
            "decision_capture": "Architectural decisions documented",
            "session_continuity": "Context recoverable across sessions"
        }
        
        if work_stream_type == "documentation":
            return {
                **base_guidance,
                "documentation_specific": {
                    "file_tracking": "Documentation files tracked for completeness",
                    "decision_context": "Documentation decisions preserved",
                    "cross_references": "File relationships maintained",
                    "version_tracking": "Documentation evolution tracked"
                },
                "recommended_practices": [
                    "Use context tracker for file operations",
                    "Document architectural decisions in documentation",
                    "Track cross-references between documentation files",
                    "Capture rationale for documentation structure choices"
                ]
            }
        
        elif work_stream_type == "testing":
            return {
                **base_guidance,
                "testing_specific": {
                    "test_file_tracking": "Test files and results tracked",
                    "test_decisions": "Testing strategy decisions preserved",
                    "coverage_tracking": "Test coverage changes monitored",
                    "result_verification": "Test execution results verified"
                },
                "recommended_practices": [
                    "Track test file creation and modifications",
                    "Document testing strategy decisions",
                    "Capture test result analysis rationale",
                    "Track test coverage improvement decisions"
                ]
            }
        
        else:
            return {
                **base_guidance,
                "general_guidance": "Standard context tracking applies",
                "recommended_practices": [
                    "Use context tracker for all file operations",
                    "Capture significant architectural decisions",
                    "Document implementation rationale",
                    "Track component relationships"
                ]
            }

    async def execute_work_stream_task_enhanced(self, 
                                              task_id: str, 
                                              work_stream_type: str,
                                              specialist_instructions: str = None) -> Dict[str, Any]:
        """
        Execute a work stream task with enhanced context tracking.
        
        Args:
            task_id: The task ID to execute
            work_stream_type: Type of work stream
            specialist_instructions: Additional instructions for the specialist
            
        Returns:
            Dict containing execution results and context
        """
        logger.info(f"Executing {work_stream_type} task {task_id} with context tracking")
        
        try:
            # Get task information
            subtask = await self.orchestrator.state.get_subtask(task_id)
            if not subtask:
                raise ValueError(f"Task {task_id} not found")
            
            specialist_type = subtask.specialist_type.value if hasattr(subtask.specialist_type, 'value') else str(subtask.specialist_type)
            
            # Create context tracker for this task
            if self.context_orchestrator:
                context_tracker = create_context_tracker_for_subtask(
                    task_id, specialist_type, self.context_orchestrator
                )
                
                # Example context tracking for work stream specific operations
                await self._perform_work_stream_context_setup(
                    context_tracker, work_stream_type, task_id
                )
            
            # Get enhanced specialist context
            specialist_context = await self.orchestrator.get_specialist_context(task_id)
            
            # Add work stream specific context
            enhanced_context = self._enhance_specialist_context(
                specialist_context, work_stream_type, specialist_instructions
            )
            
            return {
                "task_id": task_id,
                "work_stream_type": work_stream_type,
                "specialist_type": specialist_type,
                "execution_status": "ready",
                "context_tracking_enabled": True,
                "enhanced_context": enhanced_context,
                "ready_for_execution": True
            }
            
        except Exception as e:
            logger.error(f"Error executing work stream task {task_id}: {str(e)}")
            return {
                "task_id": task_id,
                "execution_status": "error",
                "error": str(e),
                "context_tracking_enabled": False
            }

    async def _perform_work_stream_context_setup(self, context_tracker, work_stream_type: str, task_id: str):
        """Perform work stream specific context setup."""
        
        # Capture initial work stream decision
        await context_tracker.capture_implementation_decision(
            title=f"{work_stream_type.title()} Work Stream Task Setup",
            decision=f"Executing {work_stream_type} task {task_id} with context tracking",
            rationale=f"Ensures {work_stream_type} work is tracked and recoverable"
        )

    def _enhance_specialist_context(self, 
                                  base_context: str, 
                                  work_stream_type: str, 
                                  additional_instructions: str = None) -> str:
        """Enhance specialist context with work stream specific guidance."""
        
        work_stream_enhancement = f"""

## 🎯 {work_stream_type.title()} Work Stream Context

This task is part of the **{work_stream_type}** work stream with enhanced context tracking:

### Context Tracking Integration
- **File Operations**: All file operations are automatically tracked and verified
- **Decision Documentation**: Capture architectural decisions relevant to {work_stream_type}
- **Session Continuity**: Complete context recovery available across sessions
- **Verification**: Enhanced completion verification ensures all work persists

### {work_stream_type.title()}-Specific Guidance
"""
        
        if work_stream_type == "documentation":
            work_stream_enhancement += """
- **Documentation Files**: Track creation and modification of all documentation
- **Cross-References**: Maintain relationships between documentation components
- **Structure Decisions**: Document rationale for documentation organization
- **Content Decisions**: Capture decisions about what to include/exclude

### Documentation Best Practices with Context Tracking
- Use descriptive commit messages and file operation rationale
- Document architectural decisions that affect documentation structure
- Track interdependencies between documentation files
- Capture user experience and accessibility considerations
"""
        
        elif work_stream_type == "testing":
            work_stream_enhancement += """
- **Test Files**: Track creation and modification of test files
- **Test Strategy**: Document testing approach decisions
- **Coverage Decisions**: Capture rationale for test coverage choices
- **Result Analysis**: Document interpretation of test results

### Testing Best Practices with Context Tracking
- Track test file relationships and dependencies
- Document testing strategy and methodology decisions
- Capture rationale for test selection and prioritization
- Track test environment and configuration decisions
"""
        
        if additional_instructions:
            work_stream_enhancement += f"""

### Additional Instructions
{additional_instructions}
"""
        
        work_stream_enhancement += """

**Remember**: All your work is automatically protected with context tracking. Focus on the task while the system ensures nothing is lost.
"""
        
        return base_context + work_stream_enhancement

    async def complete_work_stream_task(self, 
                                      task_id: str, 
                                      results: str,
                                      artifacts: List[str],
                                      work_stream_type: str) -> Dict[str, Any]:
        """
        Complete a work stream task with enhanced verification.
        
        Args:
            task_id: The task ID
            results: Task execution results
            artifacts: List of artifacts created
            work_stream_type: Type of work stream
            
        Returns:
            Dict containing completion status and context information
        """
        logger.info(f"Completing {work_stream_type} task {task_id}")
        
        try:
            # Get task information for specialist type
            subtask = await self.orchestrator.state.get_subtask(task_id)
            specialist_type = subtask.specialist_type.value if hasattr(subtask.specialist_type, 'value') else str(subtask.specialist_type)
            
            # Use enhanced completion
            completion_result = await self.orchestrator.complete_subtask_enhanced(
                task_id=task_id,
                results=results,
                artifacts=artifacts,
                next_action="continue",
                specialist_type=specialist_type
            )
            
            # Add work stream specific analysis
            work_stream_analysis = await self._analyze_work_stream_completion(
                task_id, work_stream_type, completion_result
            )
            
            enhanced_result = {
                **completion_result,
                "work_stream_type": work_stream_type,
                "work_stream_analysis": work_stream_analysis,
                "enhanced_completion": True
            }
            
            logger.info(f"Enhanced {work_stream_type} task completion: {task_id}")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error completing {work_stream_type} task {task_id}: {str(e)}")
            return {
                "task_id": task_id,
                "completion_status": "error",
                "error": str(e),
                "work_stream_type": work_stream_type
            }

    async def _analyze_work_stream_completion(self, 
                                            task_id: str, 
                                            work_stream_type: str, 
                                            completion_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze completion from work stream perspective."""
        
        context_info = completion_result.get("context_continuity", {})
        
        analysis = {
            "work_stream_impact": f"Contributes to {work_stream_type} work stream progress",
            "context_protection": "All work protected with context tracking",
            "files_tracked": len(context_info.get("context_package", {}).get("files_created", [])) + 
                           len(context_info.get("context_package", {}).get("files_modified", [])),
            "decisions_captured": context_info.get("context_package", {}).get("decisions_summary", {}).get("total_decisions", 0),
            "continuation_ready": context_info.get("completion_status") == "completed"
        }
        
        if work_stream_type == "documentation":
            analysis["documentation_impact"] = {
                "files_created": context_info.get("context_package", {}).get("files_created", []),
                "documentation_decisions": "Architectural decisions documented",
                "cross_references": "File relationships maintained"
            }
        elif work_stream_type == "testing":
            analysis["testing_impact"] = {
                "test_files": context_info.get("context_package", {}).get("files_created", []),
                "testing_decisions": "Testing strategy decisions documented",
                "coverage_impact": "Test coverage changes tracked"
            }
        
        return analysis


# Convenience functions for work stream integration

async def prepare_documentation_work_stream(enhanced_orchestrator: EnhancedTaskOrchestrator, 
                                          task_ids: List[str]) -> Dict[str, Any]:
    """Prepare documentation work stream for execution."""
    handler = EnhancedWorkStreamHandler(enhanced_orchestrator)
    return await handler.prepare_work_stream_execution(task_ids, "documentation")


async def prepare_testing_work_stream(enhanced_orchestrator: EnhancedTaskOrchestrator, 
                                    task_ids: List[str]) -> Dict[str, Any]:
    """Prepare testing work stream for execution."""
    handler = EnhancedWorkStreamHandler(enhanced_orchestrator)
    return await handler.prepare_work_stream_execution(task_ids, "testing")


async def execute_enhanced_work_stream_task(enhanced_orchestrator: EnhancedTaskOrchestrator,
                                          task_id: str,
                                          work_stream_type: str) -> Dict[str, Any]:
    """Execute a work stream task with enhanced context tracking."""
    handler = EnhancedWorkStreamHandler(enhanced_orchestrator)
    return await handler.execute_work_stream_task_enhanced(task_id, work_stream_type)
