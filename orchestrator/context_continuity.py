"""
Enhanced Context Continuity System

This module provides comprehensive context tracking and recovery capabilities
by integrating file tracking and decision documentation systems.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from sqlalchemy.orm import Session
from .file_tracking_integration import FileTrackingOrchestrator, SubtaskFileTracker
from .decision_tracking import DecisionManager, DecisionCapture
from ..db.models import SubTaskModel


@dataclass
class ContextRecoveryPackage:
    """Complete context recovery package for subtask continuity."""
    subtask_id: str
    session_id: str
    specialist_type: str
    timestamp: datetime
    
    # File tracking context
    file_operations_summary: Dict[str, Any]
    file_verification_summary: Dict[str, Any]
    files_created: List[str]
    files_modified: List[str]
    files_deleted: List[str]
    
    # Decision tracking context
    decisions_summary: Dict[str, Any]
    key_decisions: List[Dict[str, Any]]
    implementation_approaches: List[Dict[str, Any]]
    outstanding_risks: List[Dict[str, Any]]
    
    # Combined context
    affected_components: List[str]
    critical_considerations: List[str]
    continuation_guidance: str
    recovery_recommendations: List[str]


class SubtaskContextTracker:
    """
    Comprehensive context tracker for a single subtask.
    Coordinates file tracking and decision capture for complete continuity.
    """

    def __init__(self, 
                 subtask_id: str, 
                 session_id: str, 
                 specialist_type: str,
                 file_tracking_orchestrator: FileTrackingOrchestrator,
                 decision_manager: DecisionManager):
        """
        Initialize comprehensive context tracking for a subtask.
        
        Args:
            subtask_id: The ID of the subtask being executed
            session_id: Current session ID
            specialist_type: Type of specialist executing the subtask
            file_tracking_orchestrator: File tracking orchestrator instance
            decision_manager: Decision tracking manager instance
        """
        self.subtask_id = subtask_id
        self.session_id = session_id
        self.specialist_type = specialist_type
        
        # Initialize tracking components
        self.file_tracker = file_tracking_orchestrator.create_subtask_tracker(subtask_id)
        self.decision_capture = decision_manager.create_decision_capture(
            subtask_id, session_id, specialist_type
        )
        
        # Managers for analysis
        self.file_tracking_orchestrator = file_tracking_orchestrator
        self.decision_manager = decision_manager

    # File operation tracking methods
    async def track_file_create(self, file_path: str, rationale: str = "", metadata: dict = None) -> str:
        """Track file creation with optional decision context."""
        operation_id = await self.file_tracker.track_file_create(file_path, metadata)
        
        # Capture associated decision if rationale provided
        if rationale:
            await self.decision_capture.capture_simple_decision(
                title=f"Created file: {file_path}",
                decision=f"Created file at {file_path}",
                rationale=rationale,
                affected_files=[file_path]
            )
        
        return operation_id

    async def track_file_modify(self, file_path: str, rationale: str = "", metadata: dict = None) -> str:
        """Track file modification with optional decision context."""
        operation_id = await self.file_tracker.track_file_modify(file_path, metadata)
        
        if rationale:
            await self.decision_capture.capture_simple_decision(
                title=f"Modified file: {file_path}",
                decision=f"Modified file at {file_path}",
                rationale=rationale,
                affected_files=[file_path]
            )
        
        return operation_id

    async def track_file_delete(self, file_path: str, rationale: str = "", metadata: dict = None) -> str:
        """Track file deletion with optional decision context."""
        operation_id = await self.file_tracker.track_file_delete(file_path, metadata)
        
        if rationale:
            await self.decision_capture.capture_simple_decision(
                title=f"Deleted file: {file_path}",
                decision=f"Deleted file at {file_path}",
                rationale=rationale,
                affected_files=[file_path]
            )
        
        return operation_id

    # Decision capture methods
    async def capture_architecture_decision(self,
                                          title: str,
                                          problem: str,
                                          solution: str,
                                          rationale: str,
                                          affected_files: List[str] = None,
                                          risks: List[str] = None) -> str:
        """Capture a significant architectural decision."""
        from .decision_tracking import DecisionCategory, DecisionImpact
        
        return await self.decision_capture.capture_decision(
            title=title,
            problem_statement=problem,
            context=f"During {self.specialist_type} subtask execution",
            decision=solution,
            rationale=rationale,
            category=DecisionCategory.ARCHITECTURE,
            impact_level=DecisionImpact.HIGH,
            affected_files=affected_files or [],
            risks=risks or []
        )

    async def capture_implementation_decision(self,
                                            title: str,
                                            decision: str,
                                            rationale: str,
                                            affected_files: List[str] = None) -> str:
        """Capture an implementation decision."""
        from .decision_tracking import DecisionCategory, DecisionImpact
        
        return await self.decision_capture.capture_decision(
            title=title,
            problem_statement=f"Implementation approach needed for {title}",
            context=f"During {self.specialist_type} subtask execution",
            decision=decision,
            rationale=rationale,
            category=DecisionCategory.IMPLEMENTATION,
            impact_level=DecisionImpact.MEDIUM,
            affected_files=affected_files or []
        )

    # Context analysis and recovery
    async def generate_comprehensive_context(self) -> ContextRecoveryPackage:
        """Generate complete context recovery package."""
        # Get file tracking context
        file_operations_summary = await self.file_tracker.verify_all_operations()
        file_context = await self.file_tracker.get_context_recovery_info()
        
        # Get decision tracking context
        decision_context = await self.decision_manager.generate_decision_context_summary(self.subtask_id)
        
        # Analyze file operations by type
        file_ops = self.file_tracker.get_tracked_operations()
        files_created = [op.file_path for op in file_ops if op.operation_type.value == "create"]
        files_modified = [op.file_path for op in file_ops if op.operation_type.value == "modify"]
        files_deleted = [op.file_path for op in file_ops if op.operation_type.value == "delete"]
        
        # Combine affected components
        affected_components = list(set(
            file_context.get("files_affected", []) + 
            decision_context.get("affected_components", [])
        ))
        
        # Generate critical considerations
        critical_considerations = []
        if file_operations_summary.get("failed_verifications"):
            critical_considerations.append("Some file operations failed verification - manual review required")
        if decision_context.get("outstanding_risks"):
            critical_considerations.append(f"{len(decision_context['outstanding_risks'])} outstanding risks identified")
        if decision_context.get("key_decisions"):
            critical_considerations.append(f"{len(decision_context['key_decisions'])} high-impact decisions made")
        
        # Generate continuation guidance
        continuation_guidance = self._generate_continuation_guidance(
            file_operations_summary, decision_context
        )
        
        # Generate recovery recommendations
        recovery_recommendations = self._generate_recovery_recommendations(
            file_operations_summary, decision_context
        )
        
        return ContextRecoveryPackage(
            subtask_id=self.subtask_id,
            session_id=self.session_id,
            specialist_type=self.specialist_type,
            timestamp=datetime.utcnow(),
            file_operations_summary=file_operations_summary,
            file_verification_summary=file_context,
            files_created=[str(f) for f in files_created],
            files_modified=[str(f) for f in files_modified],
            files_deleted=[str(f) for f in files_deleted],
            decisions_summary=decision_context,
            key_decisions=decision_context.get("key_decisions", []),
            implementation_approaches=decision_context.get("implementation_approaches", []),
            outstanding_risks=decision_context.get("outstanding_risks", []),
            affected_components=affected_components,
            critical_considerations=critical_considerations,
            continuation_guidance=continuation_guidance,
            recovery_recommendations=recovery_recommendations
        )

    def _generate_continuation_guidance(self, 
                                      file_summary: Dict[str, Any], 
                                      decision_summary: Dict[str, Any]) -> str:
        """Generate guidance for continuing work in a new session."""
        guidance_parts = []
        
        guidance_parts.append("CONTEXT RECOVERY GUIDANCE:")
        guidance_parts.append(f"This {self.specialist_type} subtask involved:")
        
        # File operations guidance
        total_ops = file_summary.get("total_operations", 0)
        if total_ops > 0:
            guidance_parts.append(f"- {total_ops} file operations (creation, modification, deletion)")
            if not file_summary.get("all_verified", False):
                guidance_parts.append("  ⚠️ Some file operations may have failed - verify before continuing")
        
        # Decision guidance
        total_decisions = decision_summary.get("total_decisions", 0)
        if total_decisions > 0:
            guidance_parts.append(f"- {total_decisions} architectural decisions documented")
            key_decisions = decision_summary.get("key_decisions", [])
            if key_decisions:
                guidance_parts.append("  📋 Key decisions to remember:")
                for decision in key_decisions[:3]:  # Show top 3
                    guidance_parts.append(f"    • {decision['title']}: {decision['decision']}")
        
        # Implementation approaches
        approaches = decision_summary.get("implementation_approaches", [])
        if approaches:
            guidance_parts.append("  🔧 Implementation approaches in progress:")
            for approach in approaches[:2]:  # Show top 2
                guidance_parts.append(f"    • {approach['title']}: {approach['approach']}")
        
        return "\n".join(guidance_parts)

    def _generate_recovery_recommendations(self, 
                                         file_summary: Dict[str, Any], 
                                         decision_summary: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations for session recovery."""
        recommendations = []
        
        # File verification recommendations
        if not file_summary.get("all_verified", True):
            recommendations.append("Verify file operations completed successfully before proceeding")
        
        # Decision follow-up recommendations
        outstanding_risks = decision_summary.get("outstanding_risks", [])
        if outstanding_risks:
            recommendations.append(f"Review and address {len(outstanding_risks)} outstanding risks")
        
        # Implementation recommendations
        implementation_approaches = decision_summary.get("implementation_approaches", [])
        if implementation_approaches:
            recommendations.append("Continue implementing planned approaches from documented decisions")
        
        # Component impact recommendations
        affected_components = decision_summary.get("affected_components", [])
        if affected_components:
            recommendations.append(f"Test affected components: {', '.join(affected_components[:3])}")
        
        return recommendations

    async def verify_subtask_completion(self) -> Dict[str, Any]:
        """Comprehensive verification before subtask completion."""
        # Verify file operations
        file_verification = await self.file_tracking_orchestrator.verify_subtask_completion(self.subtask_id)
        
        # Generate complete context
        context_package = await self.generate_comprehensive_context()
        
        # Determine completion readiness
        completion_approved = (
            file_verification.get("completion_approved", False) and
            len(context_package.critical_considerations) == 0
        )
        
        return {
            "subtask_id": self.subtask_id,
            "completion_approved": completion_approved,
            "file_verification": file_verification,
            "context_package": context_package,
            "critical_issues": context_package.critical_considerations,
            "recommendations": context_package.recovery_recommendations
        }



class ContextContinuityOrchestrator:
    """
    High-level orchestrator for comprehensive context continuity.
    Manages the complete lifecycle of context tracking and recovery.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the context continuity orchestrator.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.file_tracking_orchestrator = FileTrackingOrchestrator(db_session)
        self.decision_manager = DecisionManager(db_session)
        self._session_id = str(uuid.uuid4())

    @classmethod
    async def initialize(cls, db_session: Session, run_migrations: bool = True):
        """
        Initialize the context continuity system with migrations.
        
        Args:
            db_session: SQLAlchemy database session
            run_migrations: Whether to run database migrations
            
        Returns:
            ContextContinuityOrchestrator instance
        """
        # Initialize file tracking first
        file_tracking = await FileTrackingOrchestrator.initialize(db_session, run_migrations)
        
        # Create the orchestrator
        orchestrator = cls(db_session)
        orchestrator.file_tracking_orchestrator = file_tracking
        
        return orchestrator

    def create_subtask_context_tracker(self, subtask_id: str, specialist_type: str) -> SubtaskContextTracker:
        """
        Create a comprehensive context tracker for a subtask.
        
        Args:
            subtask_id: The ID of the subtask
            specialist_type: Type of specialist executing the subtask
            
        Returns:
            SubtaskContextTracker instance
        """
        return SubtaskContextTracker(
            subtask_id, 
            self._session_id, 
            specialist_type,
            self.file_tracking_orchestrator,
            self.decision_manager
        )

    async def complete_subtask_with_context(self, 
                                          subtask_id: str, 
                                          specialist_type: str,
                                          results: str,
                                          artifacts: List[str] = None) -> Dict[str, Any]:
        """
        Complete a subtask with full context tracking and verification.
        
        Args:
            subtask_id: The ID of the subtask being completed
            specialist_type: Type of specialist
            results: Results of the subtask execution
            artifacts: List of artifacts created
            
        Returns:
            Dict containing completion status and context information
        """
        # Create tracker for this subtask
        tracker = self.create_subtask_context_tracker(subtask_id, specialist_type)
        
        # Verify completion readiness
        completion_verification = await tracker.verify_subtask_completion()
        
        # Generate comprehensive context package
        context_package = await tracker.generate_comprehensive_context()
        
        # Update subtask with context information
        subtask = self.db_session.query(SubTaskModel).filter_by(task_id=subtask_id).first()
        if subtask:
            # Update basic completion info
            subtask.results = results
            subtask.artifacts = artifacts or []
            subtask.completed_at = datetime.utcnow()
            
            # Update verification status
            if completion_verification["completion_approved"]:
                subtask.verification_status = "verified"
                subtask.status = "completed"
            else:
                subtask.verification_status = "partial"
                subtask.status = "needs_review"
            
            self.db_session.commit()

        return {
            "subtask_id": subtask_id,
            "completion_status": "completed" if completion_verification["completion_approved"] else "needs_review",
            "completion_verification": completion_verification,
            "context_package": context_package,
            "session_continuity_info": {
                "total_operations": context_package.file_operations_summary.get("total_operations", 0),
                "total_decisions": context_package.decisions_summary.get("total_decisions", 0),
                "files_affected": len(context_package.files_created + context_package.files_modified),
                "continuation_guidance": context_package.continuation_guidance,
                "recovery_recommendations": context_package.recovery_recommendations
            }
        }

    async def recover_context_for_subtask(self, subtask_id: str) -> ContextRecoveryPackage:
        """
        Recover complete context for a subtask from previous sessions.
        
        Args:
            subtask_id: The ID of the subtask to recover context for
            
        Returns:
            ContextRecoveryPackage with complete context information
        """
        # Get subtask info
        subtask = self.db_session.query(SubTaskModel).filter_by(task_id=subtask_id).first()
        if not subtask:
            raise ValueError(f"Subtask {subtask_id} not found")

        # Create temporary tracker for analysis
        tracker = SubtaskContextTracker(
            subtask_id,
            "recovery_session",
            "context_recovery",
            self.file_tracking_orchestrator,
            self.decision_manager
        )
        
        # Generate context package
        return await tracker.generate_comprehensive_context()

    async def generate_session_continuity_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report for session continuity."""
        # Get all subtasks in this session
        file_operations = self.db_session.query(
            self.file_tracking_orchestrator.tracking_manager.db_session.query().all()
        )
        
        decisions = await self.decision_manager.get_decisions_for_session(self._session_id)
        
        return {
            "session_id": self._session_id,
            "total_file_operations": len(file_operations) if file_operations else 0,
            "total_decisions": len(decisions),
            "session_summary": "Context continuity tracking active",
            "recommendations": [
                "All file operations and decisions are tracked for context recovery",
                "Use recover_context_for_subtask() to restore context in new sessions",
                "Review context packages before continuing interrupted work"
            ]
        }


# Enhanced migration for decision tracking tables
async def migrate_context_continuity_schema(db_session: Session) -> bool:
    """
    Migrate database schema to support full context continuity.
    
    Args:
        db_session: SQLAlchemy database session
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from ..db.models import Base
        from sqlalchemy import create_engine
        
        # Get the engine from the session
        engine = db_session.get_bind()
        
        # Create all tables including new decision tracking tables
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        return True
        
    except Exception as e:
        print(f"Error migrating context continuity schema: {str(e)}")
        return False


# Convenience functions for easy integration

async def initialize_context_continuity(db_session: Session, run_migrations: bool = True) -> ContextContinuityOrchestrator:
    """
    Initialize complete context continuity system.
    
    Args:
        db_session: SQLAlchemy database session
        run_migrations: Whether to run database migrations
        
    Returns:
        ContextContinuityOrchestrator instance
    """
    if run_migrations:
        success = await migrate_context_continuity_schema(db_session)
        if not success:
            raise RuntimeError("Failed to migrate context continuity schema")
    
    return await ContextContinuityOrchestrator.initialize(db_session, run_migrations=False)


def create_context_tracker_for_subtask(subtask_id: str, 
                                      specialist_type: str, 
                                      context_orchestrator: ContextContinuityOrchestrator) -> SubtaskContextTracker:
    """
    Create a context tracker for a specific subtask.
    
    Args:
        subtask_id: The ID of the subtask
        specialist_type: Type of specialist
        context_orchestrator: Context continuity orchestrator instance
        
    Returns:
        SubtaskContextTracker instance
    """
    return context_orchestrator.create_subtask_context_tracker(subtask_id, specialist_type)