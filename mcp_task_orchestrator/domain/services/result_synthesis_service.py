"""
Result Synthesis Service - Handles combining results from multiple subtasks.

This service is responsible for synthesizing results from completed subtasks
into a coherent output for parent tasks.
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime

from ..repositories import TaskRepository, StateRepository


class ResultSynthesisService:
    """
    Service for synthesizing results from multiple subtasks.
    
    This service encapsulates the logic for combining subtask outputs
    into comprehensive results for parent tasks.
    """
    
    def __init__(self,
                 task_repository: TaskRepository,
                 state_repository: StateRepository):
        """
        Initialize the result synthesis service.
        
        Args:
            task_repository: Repository for task persistence
            state_repository: Repository for state persistence
        """
        self.task_repo = task_repository
        self.state_repo = state_repository
    
    async def synthesize_task_results(self, parent_task_id: str) -> str:
        """
        Synthesize results from all subtasks of a parent task.
        
        Args:
            parent_task_id: Parent task ID
            
        Returns:
            Synthesized results as a formatted string
            
        Raises:
            ValueError: If parent task not found or has no subtasks
        """
        # Get parent task
        parent_task = self.task_repo.get_task(parent_task_id)
        if not parent_task:
            raise ValueError(f"Parent task {parent_task_id} not found")
        
        # Get all subtasks
        subtasks = self.task_repo.get_subtasks(parent_task_id)
        if not subtasks:
            raise ValueError(f"Parent task {parent_task_id} has no subtasks")
        
        # Collect results from completed subtasks
        subtask_results = []
        incomplete_count = 0
        
        for subtask in subtasks:
            if subtask['status'] in ('completed', 'failed'):
                # Get task artifacts
                artifacts = self.task_repo.get_task_artifacts(subtask['id'])
                
                # Find result artifacts
                result_artifacts = [
                    a for a in artifacts 
                    if a.get('type') == 'result'
                ]
                
                subtask_info = {
                    'id': subtask['id'],
                    'title': subtask.get('title', 'Untitled'),
                    'status': subtask['status'],
                    'specialist': subtask.get('metadata', {}).get('specialist', 'unknown'),
                    'results': []
                }
                
                # Extract results
                for artifact in result_artifacts:
                    content = artifact.get('content')
                    if content:
                        subtask_info['results'].append(content)
                
                # Add any other relevant artifacts
                code_artifacts = [
                    a for a in artifacts
                    if a.get('type') in ('code', 'implementation')
                ]
                
                if code_artifacts:
                    subtask_info['code_artifacts'] = [
                        {
                            'name': a.get('name', 'unnamed'),
                            'content': a.get('content', '')
                        }
                        for a in code_artifacts
                    ]
                
                subtask_results.append(subtask_info)
                
            else:
                incomplete_count += 1
        
        # Build synthesis
        synthesis_parts = []
        
        # Header
        synthesis_parts.append(f"# Task Synthesis: {parent_task.get('title', 'Untitled')}")
        synthesis_parts.append("")
        
        # Overview
        synthesis_parts.append("## Overview")
        synthesis_parts.append(f"- Total subtasks: {len(subtasks)}")
        synthesis_parts.append(f"- Completed: {len(subtask_results)}")
        
        if incomplete_count > 0:
            synthesis_parts.append(f"- Incomplete: {incomplete_count}")
        
        synthesis_parts.append("")
        
        # Subtask results
        synthesis_parts.append("## Subtask Results")
        synthesis_parts.append("")
        
        for idx, subtask_info in enumerate(subtask_results, 1):
            synthesis_parts.append(f"### {idx}. {subtask_info['title']}")
            synthesis_parts.append(f"**Status**: {subtask_info['status']}")
            synthesis_parts.append(f"**Specialist**: {subtask_info['specialist']}")
            synthesis_parts.append("")
            
            # Results
            if subtask_info['results']:
                synthesis_parts.append("**Results**:")
                for result in subtask_info['results']:
                    # Format result based on type
                    if isinstance(result, dict):
                        synthesis_parts.append("```json")
                        synthesis_parts.append(json.dumps(result, indent=2))
                        synthesis_parts.append("```")
                    else:
                        synthesis_parts.append(str(result))
                synthesis_parts.append("")
            
            # Code artifacts
            if subtask_info.get('code_artifacts'):
                synthesis_parts.append("**Code Artifacts**:")
                for artifact in subtask_info['code_artifacts']:
                    synthesis_parts.append(f"- {artifact['name']}")
                    if artifact['content']:
                        synthesis_parts.append("```")
                        synthesis_parts.append(artifact['content'][:500])
                        if len(artifact['content']) > 500:
                            synthesis_parts.append("... (truncated)")
                        synthesis_parts.append("```")
                synthesis_parts.append("")
        
        # Summary and recommendations
        synthesis_parts.extend(self._generate_summary(parent_task, subtask_results))
        
        # Record synthesis event
        self.state_repo.record_event(
            parent_task.get('session_id'),
            'results_synthesized',
            {
                'parent_task_id': parent_task_id,
                'subtask_count': len(subtasks),
                'completed_count': len(subtask_results)
            }
        )
        
        return "\n".join(synthesis_parts)
    
    def _generate_summary(self, 
                         parent_task: Dict[str, Any], 
                         subtask_results: List[Dict[str, Any]]) -> List[str]:
        """Generate summary section for synthesis."""
        summary_parts = []
        
        summary_parts.append("## Summary")
        summary_parts.append("")
        
        # Check if all subtasks succeeded
        all_succeeded = all(
            result['status'] == 'completed' 
            for result in subtask_results
        )
        
        if all_succeeded:
            summary_parts.append("✅ All subtasks completed successfully.")
        else:
            failed_count = sum(
                1 for result in subtask_results 
                if result['status'] == 'failed'
            )
            summary_parts.append(f"⚠️ {failed_count} subtasks failed.")
        
        summary_parts.append("")
        
        # Key achievements
        summary_parts.append("### Key Achievements")
        
        # Group by specialist type
        by_specialist = {}
        for result in subtask_results:
            specialist = result['specialist']
            if specialist not in by_specialist:
                by_specialist[specialist] = []
            by_specialist[specialist].append(result['title'])
        
        for specialist, tasks in by_specialist.items():
            summary_parts.append(f"- **{specialist.title()}**: {len(tasks)} tasks completed")
            for task in tasks[:3]:  # Show first 3
                summary_parts.append(f"  - {task}")
            if len(tasks) > 3:
                summary_parts.append(f"  - ... and {len(tasks) - 3} more")
        
        summary_parts.append("")
        
        # Next steps
        summary_parts.append("### Next Steps")
        
        if all_succeeded:
            summary_parts.append("- Review the synthesized results")
            summary_parts.append("- Integrate components as needed")
            summary_parts.append("- Test the complete solution")
        else:
            summary_parts.append("- Address failed subtasks")
            summary_parts.append("- Review error details for each failure")
            summary_parts.append("- Retry or adjust approach as needed")
        
        summary_parts.append("")
        
        return summary_parts
    
    async def get_partial_synthesis(self, 
                                  parent_task_id: str,
                                  include_incomplete: bool = True) -> Dict[str, Any]:
        """
        Get a partial synthesis including incomplete tasks.
        
        Args:
            parent_task_id: Parent task ID
            include_incomplete: Whether to include incomplete task info
            
        Returns:
            Dictionary with synthesis information
        """
        parent_task = self.task_repo.get_task(parent_task_id)
        if not parent_task:
            raise ValueError(f"Parent task {parent_task_id} not found")
        
        subtasks = self.task_repo.get_subtasks(parent_task_id)
        
        synthesis_info = {
            'parent_task': {
                'id': parent_task_id,
                'title': parent_task.get('title', 'Untitled'),
                'status': parent_task['status']
            },
            'subtasks': {
                'total': len(subtasks),
                'completed': 0,
                'failed': 0,
                'in_progress': 0,
                'pending': 0
            },
            'results': [],
            'incomplete_tasks': []
        }
        
        # Process subtasks
        for subtask in subtasks:
            status = subtask['status']
            synthesis_info['subtasks'][status] = synthesis_info['subtasks'].get(status, 0) + 1
            
            if status == 'completed':
                synthesis_info['subtasks']['completed'] += 1
                
                # Get results
                artifacts = self.task_repo.get_task_artifacts(subtask['id'])
                result_artifacts = [
                    a for a in artifacts
                    if a.get('type') == 'result'
                ]
                
                if result_artifacts:
                    synthesis_info['results'].append({
                        'task_id': subtask['id'],
                        'title': subtask.get('title', 'Untitled'),
                        'content': result_artifacts[0].get('content', '')
                    })
                    
            elif status == 'failed':
                synthesis_info['subtasks']['failed'] += 1
                
            elif include_incomplete and status in ('in_progress', 'pending'):
                synthesis_info['incomplete_tasks'].append({
                    'task_id': subtask['id'],
                    'title': subtask.get('title', 'Untitled'),
                    'status': status,
                    'specialist': subtask.get('metadata', {}).get('specialist', 'unknown')
                })
        
        # Calculate progress
        if synthesis_info['subtasks']['total'] > 0:
            completed_and_failed = (
                synthesis_info['subtasks']['completed'] + 
                synthesis_info['subtasks']['failed']
            )
            synthesis_info['progress_percentage'] = round(
                (completed_and_failed / synthesis_info['subtasks']['total']) * 100,
                1
            )
        else:
            synthesis_info['progress_percentage'] = 0
        
        return synthesis_info