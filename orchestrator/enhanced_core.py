"""
Enhanced Task Orchestrator with Context Continuity Integration

This module provides an enhanced TaskOrchestrator that integrates file tracking
and decision persistence systems for comprehensive context continuity.
"""

import os
import uuid
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from .core import TaskOrchestrator as BaseTaskOrchestrator
from .models import TaskBreakdown, SubTask, TaskStatus, SpecialistType, ComplexityLevel, TaskResult
from .specialists import SpecialistManager
from .state import StateManager
from .role_loader import get_roles
from .context_continuity import initialize_context_continuity, ContextContinuityOrchestrator
from ..db.persistence import DatabasePersistenceManager
from sqlalchemy.orm import sessionmaker

# Configure logging
logger = logging.getLogger("mcp_task_orchestrator.enhanced_core")


class EnhancedTaskOrchestrator(BaseTaskOrchestrator):
    """
    Enhanced Task Orchestrator with integrated file tracking and decision persistence.
    
    Extends the base TaskOrchestrator with:
    - Comprehensive file tracking during subtask execution
    - Architectural decision capture and documentation
    - Context continuity across session boundaries
    - Enhanced subtask completion verification
    - Context recovery capabilities
    """
    
    def __init__(self, 
                 state_manager: StateManager, 
                 specialist_manager: SpecialistManager, 
                 project_dir: str = None,
                 db_session=None):
        """
        Initialize the enhanced orchestrator with context continuity.
        
        Args:
            state_manager: State management for tasks
            specialist_manager: Specialist coordination
            project_dir: Project directory for configuration
            db_session: Database session for context tracking
        """
        super().__init__(state_manager, specialist_manager, project_dir)
        self.db_session = db_session
        self.context_orchestrator: Optional[ContextContinuityOrchestrator] = None
        self._session_id = str(uuid.uuid4())
        
    @classmethod
    async def create_enhanced(cls, 
                            state_manager: StateManager, 
                            specialist_manager: SpecialistManager,
                            project_dir: str = None,
                            db_url: str = None) -> 'EnhancedTaskOrchestrator':
        """
        Create an enhanced orchestrator with full context continuity setup.
        
        Args:
            state_manager: State management for tasks
            specialist_manager: Specialist coordination  
            project_dir: Project directory for configuration
            db_url: Database URL for context tracking
            
        Returns:
            EnhancedTaskOrchestrator with context continuity enabled
        """
        # Set up database session for context tracking
        if db_url is None:
            # Use the same database as the persistence manager
            if hasattr(state_manager, 'db_session'):
                db_session = state_manager.db_session
            else:
                # Create new database connection
                from sqlalchemy import create_engine
                db_url = "sqlite:///task_orchestrator.db"
                engine = create_engine(db_url)
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                db_session = SessionLocal()
        else:
            from sqlalchemy import create_engine
            engine = create_engine(db_url)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db_session = SessionLocal()
        
        # Create enhanced orchestrator
        orchestrator = cls(state_manager, specialist_manager, project_dir, db_session)
        
        # Initialize context continuity
        orchestrator.context_orchestrator = await initialize_context_continuity(
            db_session, run_migrations=True
        )
        
        logger.info("Enhanced Task Orchestrator initialized with context continuity")
        
        return orchestrator

    async def initialize_session(self) -> Dict:
        """Initialize session with enhanced context tracking capabilities."""
        base_response = await super().initialize_session()
        
        # Add context continuity information
        base_response.update({
            "context_continuity": {
                "enabled": self.context_orchestrator is not None,
                "session_id": self._session_id,
                "features": [
                    "File operation tracking and verification",
                    "Architectural decision documentation",
                    "Context recovery across session boundaries",
                    "Enhanced subtask completion verification"
                ]
            },
            "enhanced_capabilities": [
                "Comprehensive file tracking during subtask execution",
                "Automatic architectural decision capture",
                "Context recovery for interrupted work",
                "Verification of file persistence before completion"
            ]
        })
        
        return base_response

    async def get_specialist_context(self, task_id: str) -> str:
        """Enhanced specialist context with tracking guidance."""
        base_context = await super().get_specialist_context(task_id)
        
        if self.context_orchestrator:
            # Add context tracking guidance
            enhanced_context = base_context + """

## 🔄 Context Continuity Integration

This subtask includes comprehensive context tracking:

### File Operation Tracking
Use the context tracker to log file operations:
```python
# Example usage (when integrated):
await tracker.track_file_create("new_file.py", "Creating main implementation")
await tracker.track_file_modify("config.py", "Updating configuration for new feature")
```

### Decision Documentation
Capture architectural decisions:
```python
# Example usage (when integrated):
await tracker.capture_architecture_decision(
    title="Database Schema Design",
    problem="Need efficient data storage",
    solution="Use normalized relational schema",
    rationale="Ensures data integrity and query performance"
)
```

### Important Notes:
- All file operations are automatically tracked and verified
- Architectural decisions are preserved for future context
- Completion verification includes both files and decisions
- Context is recoverable across session boundaries

The enhanced orchestrator ensures no work is lost and provides complete context continuity.
"""
            return enhanced_context
        
        return base_context

    async def complete_subtask_enhanced(self, 
                                      task_id: str, 
                                      results: str,
                                      artifacts: List[str], 
                                      next_action: str,
                                      specialist_type: str = None) -> Dict:
        """
        Enhanced subtask completion with comprehensive context tracking.
        
        Args:
            task_id: The subtask ID
            results: Results of the subtask execution
            artifacts: List of artifacts created
            next_action: Next action recommendation
            specialist_type: Type of specialist (auto-detected if not provided)
            
        Returns:
            Dict with completion status and context information
        """
        if not self.context_orchestrator:
            # Fall back to base implementation if context tracking not available
            logger.warning("Context continuity not available, using base completion")
            return await super().complete_subtask(task_id, results, artifacts, next_action)
        
        try:
            # Get subtask info for specialist type if not provided
            if not specialist_type:
                subtask = await self.state.get_subtask(task_id)
                if subtask:
                    specialist_type = subtask.specialist_type.value if hasattr(subtask.specialist_type, 'value') else str(subtask.specialist_type)
                else:
                    specialist_type = "unknown"
            
            # Complete subtask with full context tracking
            completion_info = await self.context_orchestrator.complete_subtask_with_context(
                subtask_id=task_id,
                specialist_type=specialist_type,
                results=results,
                artifacts=artifacts or []
            )
            
            # Also update the base orchestrator state
            base_completion = await super().complete_subtask(task_id, results, artifacts, next_action)
            
            # Combine results
            enhanced_result = {
                **base_completion,
                "context_continuity": completion_info,
                "session_id": self._session_id,
                "enhanced_completion": True
            }
            
            logger.info(f"Enhanced subtask completion for {task_id}: {completion_info['completion_status']}")
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in enhanced subtask completion for {task_id}: {str(e)}")
            # Fall back to base completion
            return await super().complete_subtask(task_id, results, artifacts, next_action)

    async def recover_context_for_task(self, task_id: str) -> Dict[str, Any]:
        """
        Recover complete context for a task from previous sessions.
        
        Args:
            task_id: The task ID to recover context for
            
        Returns:
            Dict containing complete context recovery information
        """
        if not self.context_orchestrator:
            return {"error": "Context continuity not available"}
        
        try:
            context_package = await self.context_orchestrator.recover_context_for_subtask(task_id)
            
            return {
                "task_id": task_id,
                "context_recovered": True,
                "recovery_package": {
                    "files_created": context_package.files_created,
                    "files_modified": context_package.files_modified,
                    "files_deleted": context_package.files_deleted,
                    "total_decisions": context_package.decisions_summary.get('total_decisions', 0),
                    "key_decisions": context_package.key_decisions,
                    "outstanding_risks": context_package.outstanding_risks,
                    "affected_components": context_package.affected_components,
                    "continuation_guidance": context_package.continuation_guidance,
                    "recovery_recommendations": context_package.recovery_recommendations
                },
                "session_info": {
                    "original_session": context_package.session_id,
                    "specialist_type": context_package.specialist_type,
                    "timestamp": context_package.timestamp.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error recovering context for task {task_id}: {str(e)}")
            return {
                "task_id": task_id,
                "context_recovered": False,
                "error": str(e)
            }

    async def get_session_continuity_status(self) -> Dict[str, Any]:
        """Get comprehensive session continuity status."""
        if not self.context_orchestrator:
            return {
                "context_continuity_enabled": False,
                "message": "Context continuity not available"
            }
        
        try:
            report = await self.context_orchestrator.generate_session_continuity_report()
            
            return {
                "context_continuity_enabled": True,
                "session_id": self._session_id,
                "continuity_report": report,
                "capabilities": {
                    "file_tracking": True,
                    "decision_documentation": True,
                    "context_recovery": True,
                    "verification_systems": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting session continuity status: {str(e)}")
            return {
                "context_continuity_enabled": False,
                "error": str(e)
            }

    async def verify_work_stream_readiness(self, work_stream_tasks: List[str]) -> Dict[str, Any]:
        """
        Verify that work stream tasks are ready to execute with context tracking.
        
        Args:
            work_stream_tasks: List of task IDs in the work stream
            
        Returns:
            Dict containing readiness assessment
        """
        if not self.context_orchestrator:
            return {
                "ready": False,
                "reason": "Context continuity not available"
            }
        
        readiness_report = {
            "ready": True,
            "context_continuity_enabled": True,
            "work_stream_protection": {
                "file_tracking": "All file operations will be tracked and verified",
                "decision_capture": "Architectural decisions will be documented",
                "context_recovery": "Complete context recovery available",
                "session_continuity": "Work can continue across session boundaries"
            },
            "recommendations": [
                "All work stream tasks now have comprehensive context protection",
                "File operations will be automatically verified before completion",
                "Architectural decisions will be captured for future reference",
                "Context recovery is available if sessions are interrupted"
            ],
            "task_readiness": []
        }
        
        # Check readiness for each task
        for task_id in work_stream_tasks:
            try:
                subtask = await self.state.get_subtask(task_id)
                if subtask:
                    task_status = {
                        "task_id": task_id,
                        "title": subtask.title,
                        "status": subtask.status.value if hasattr(subtask.status, 'value') else str(subtask.status),
                        "ready_for_enhanced_execution": True,
                        "context_tracking_enabled": True
                    }
                else:
                    task_status = {
                        "task_id": task_id,
                        "ready_for_enhanced_execution": False,
                        "error": "Task not found"
                    }
                    
                readiness_report["task_readiness"].append(task_status)
                
            except Exception as e:
                readiness_report["task_readiness"].append({
                    "task_id": task_id,
                    "ready_for_enhanced_execution": False,
                    "error": str(e)
                })
        
        return readiness_report

    # Override complete_subtask to use enhanced version by default
    async def complete_subtask(self, task_id: str, results: str, 
                             artifacts: List[str], next_action: str) -> Dict:
        """Override to use enhanced completion by default."""
        return await self.complete_subtask_enhanced(task_id, results, artifacts, next_action)


# Factory function for easy creation
async def create_enhanced_orchestrator(state_manager: StateManager,
                                     specialist_manager: SpecialistManager, 
                                     project_dir: str = None,
                                     db_url: str = None) -> EnhancedTaskOrchestrator:
    """
    Factory function to create an enhanced orchestrator with context continuity.
    
    Args:
        state_manager: State management for tasks
        specialist_manager: Specialist coordination
        project_dir: Project directory for configuration  
        db_url: Database URL for context tracking
        
    Returns:
        EnhancedTaskOrchestrator with full context continuity
    """
    return await EnhancedTaskOrchestrator.create_enhanced(
        state_manager, specialist_manager, project_dir, db_url
    )
