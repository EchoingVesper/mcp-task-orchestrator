"""
Decision Documentation System

This module implements comprehensive architectural decision capture and tracking
to ensure context continuity and prevent loss of decision rationale across
session boundaries.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

from sqlalchemy.orm import Session
from ..db.models import ArchitecturalDecisionModel, DecisionEvolutionModel, SubTaskModel


class DecisionCategory(Enum):
    """Categories of architectural decisions."""
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    DESIGN = "design"
    TECHNOLOGY = "technology"
    PROCESS = "process"
    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"


class DecisionImpact(Enum):
    """Impact levels for decisions."""
    HIGH = "high"        # Affects overall system architecture
    MEDIUM = "medium"    # Affects multiple components
    LOW = "low"         # Local changes only


class DecisionStatus(Enum):
    """Status of architectural decisions."""
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"


class ImplementationStatus(Enum):
    """Implementation status of decisions."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class EvolutionType(Enum):
    """Types of decision evolution."""
    SUPERSEDED = "superseded"
    REFINED = "refined"
    REVERSED = "reversed"
    CLARIFIED = "clarified"


@dataclass
class Alternative:
    """Represents an alternative considered in a decision."""
    name: str
    description: str
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    evaluation: str = ""


@dataclass
class ArchitecturalDecision:
    """Data class representing an architectural decision record."""
    # Core Identity
    decision_id: str
    decision_number: int
    title: str
    status: DecisionStatus = DecisionStatus.PROPOSED
    
    # Context and Timing
    subtask_id: str = ""
    session_id: str = ""
    specialist_type: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Decision Content
    category: DecisionCategory = DecisionCategory.IMPLEMENTATION
    impact_level: DecisionImpact = DecisionImpact.MEDIUM
    problem_statement: str = ""
    context: str = ""
    decision: str = ""
    rationale: str = ""
    
    # Implementation Tracking
    implementation_approach: str = ""
    affected_files: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # Quality and Review
    alternatives_considered: List[Alternative] = field(default_factory=list)
    trade_offs: Dict[str, str] = field(default_factory=dict)
    risks: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    
    # Implementation Status
    implementation_status: ImplementationStatus = ImplementationStatus.PLANNED
    supersedes: List[str] = field(default_factory=list)


class DecisionCapture:
    """
    Captures architectural decisions during subtask execution.
    Provides simple interface for specialists to document their decisions.
    """

    def __init__(self, subtask_id: str, session_id: str, specialist_type: str, db_session: Session):
        """
        Initialize decision capture for a subtask.
        
        Args:
            subtask_id: The ID of the subtask being executed
            session_id: Current session ID  
            specialist_type: Type of specialist making decisions
            db_session: SQLAlchemy database session
        """
        self.subtask_id = subtask_id
        self.session_id = session_id
        self.specialist_type = specialist_type
        self.db_session = db_session
        self.captured_decisions: List[ArchitecturalDecision] = []

    async def capture_decision(self,
                             title: str,
                             problem_statement: str,
                             context: str,
                             decision: str,
                             rationale: str,
                             category: DecisionCategory = DecisionCategory.IMPLEMENTATION,
                             impact_level: DecisionImpact = DecisionImpact.MEDIUM,
                             affected_files: List[str] = None,
                             affected_components: List[str] = None,
                             alternatives: List[Dict[str, Any]] = None,
                             risks: List[str] = None,
                             implementation_approach: str = "") -> str:
        """
        Capture an architectural decision with full context.
        
        Args:
            title: Brief title of the decision
            problem_statement: What problem this decision solves
            context: Background context for the decision
            decision: The actual decision made
            rationale: Why this decision was chosen
            category: Category of decision
            impact_level: Impact level of the decision
            affected_files: List of files affected by this decision
            affected_components: List of components affected
            alternatives: List of alternatives considered
            risks: List of identified risks
            implementation_approach: How this will be implemented
            
        Returns:
            str: Decision ID
        """
        # Generate decision number
        decision_number = await self._get_next_decision_number()
        
        # Process alternatives
        processed_alternatives = []
        if alternatives:
            for alt in alternatives:
                processed_alternatives.append(Alternative(
                    name=alt.get('name', ''),
                    description=alt.get('description', ''),
                    pros=alt.get('pros', []),
                    cons=alt.get('cons', []),
                    evaluation=alt.get('evaluation', '')
                ))

        # Create decision record
        decision_record = ArchitecturalDecision(
            decision_id=str(uuid.uuid4()),
            decision_number=decision_number,
            title=title,
            subtask_id=self.subtask_id,
            session_id=self.session_id,
            specialist_type=self.specialist_type,
            category=category,
            impact_level=impact_level,
            problem_statement=problem_statement,
            context=context,
            decision=decision,
            rationale=rationale,
            implementation_approach=implementation_approach,
            affected_files=affected_files or [],
            affected_components=affected_components or [],
            alternatives_considered=processed_alternatives,
            risks=risks or [],
            status=DecisionStatus.ACCEPTED  # Auto-accept decisions made by specialists
        )

        # Store in memory
        self.captured_decisions.append(decision_record)
        
        # Persist to database
        await self._persist_decision(decision_record)
        
        return decision_record.decision_id

    async def capture_simple_decision(self,
                                    title: str,
                                    decision: str,
                                    rationale: str,
                                    affected_files: List[str] = None) -> str:
        """
        Simplified decision capture for common cases.
        
        Args:
            title: Brief title of the decision
            decision: The decision made
            rationale: Why this decision was chosen
            affected_files: List of files affected
            
        Returns:
            str: Decision ID
        """
        return await self.capture_decision(
            title=title,
            problem_statement=f"Decision needed for {title}",
            context=f"During {self.specialist_type} subtask execution",
            decision=decision,
            rationale=rationale,
            affected_files=affected_files or []
        )

    async def _get_next_decision_number(self) -> int:
        """Get the next decision number for this session."""
        # Query for the highest decision number in this session
        max_number = self.db_session.query(
            ArchitecturalDecisionModel.decision_number
        ).filter_by(session_id=self.session_id).order_by(
            ArchitecturalDecisionModel.decision_number.desc()
        ).first()
        
        return (max_number[0] if max_number else 0) + 1

    async def _persist_decision(self, decision: ArchitecturalDecision):
        """Persist decision to database."""
        # Convert alternatives to JSON-serializable format
        alternatives_json = [
            {
                'name': alt.name,
                'description': alt.description,
                'pros': alt.pros,
                'cons': alt.cons,
                'evaluation': alt.evaluation
            }
            for alt in decision.alternatives_considered
        ]

        db_decision = ArchitecturalDecisionModel(
            decision_id=decision.decision_id,
            decision_number=decision.decision_number,
            subtask_id=decision.subtask_id,
            session_id=decision.session_id,
            specialist_type=decision.specialist_type,
            title=decision.title,
            category=decision.category.value,
            impact_level=decision.impact_level.value,
            status=decision.status.value,
            problem_statement=decision.problem_statement,
            context=decision.context,
            decision=decision.decision,
            rationale=decision.rationale,
            implementation_approach=decision.implementation_approach,
            affected_files=decision.affected_files,
            affected_components=decision.affected_components,
            dependencies=decision.dependencies,
            alternatives_considered=alternatives_json,
            trade_offs=decision.trade_offs,
            risks=decision.risks,
            mitigation_strategies=decision.mitigation_strategies,
            success_criteria=decision.success_criteria,
            implementation_status=decision.implementation_status.value,
            supersedes=decision.supersedes,
            timestamp=decision.timestamp
        )
        
        self.db_session.add(db_decision)
        self.db_session.commit()

    def get_captured_decisions(self) -> List[ArchitecturalDecision]:
        """Get all decisions captured for this subtask."""
        return self.captured_decisions.copy()



class DecisionManager:
    """
    High-level manager for architectural decision tracking and context recovery.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the decision manager.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    def create_decision_capture(self, subtask_id: str, session_id: str, specialist_type: str) -> DecisionCapture:
        """Create a new decision capture instance for a subtask."""
        return DecisionCapture(subtask_id, session_id, specialist_type, self.db_session)

    async def get_decisions_for_subtask(self, subtask_id: str) -> List[ArchitecturalDecisionModel]:
        """Get all decisions made during a specific subtask."""
        return self.db_session.query(ArchitecturalDecisionModel).filter_by(
            subtask_id=subtask_id
        ).order_by(ArchitecturalDecisionModel.decision_number).all()

    async def get_decisions_for_session(self, session_id: str) -> List[ArchitecturalDecisionModel]:
        """Get all decisions made during a specific session."""
        return self.db_session.query(ArchitecturalDecisionModel).filter_by(
            session_id=session_id
        ).order_by(ArchitecturalDecisionModel.decision_number).all()

    async def generate_decision_context_summary(self, subtask_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive decision context summary for recovery.
        
        Args:
            subtask_id: The subtask ID to generate summary for
            
        Returns:
            Dict containing decision context information
        """
        decisions = await self.get_decisions_for_subtask(subtask_id)
        
        summary = {
            "subtask_id": subtask_id,
            "total_decisions": len(decisions),
            "decisions_by_category": {},
            "decisions_by_impact": {},
            "key_decisions": [],
            "affected_files": set(),
            "affected_components": set(),
            "implementation_approaches": [],
            "outstanding_risks": [],
            "context_for_recovery": ""
        }

        # Analyze decisions
        for decision in decisions:
            # Count by category
            category = decision.category
            summary["decisions_by_category"][category] = summary["decisions_by_category"].get(category, 0) + 1
            
            # Count by impact
            impact = decision.impact_level
            summary["decisions_by_impact"][impact] = summary["decisions_by_impact"].get(impact, 0) + 1
            
            # Track affected files and components
            if decision.affected_files:
                summary["affected_files"].update(decision.affected_files)
            if decision.affected_components:
                summary["affected_components"].update(decision.affected_components)
            
            # Collect implementation approaches
            if decision.implementation_approach:
                summary["implementation_approaches"].append({
                    "decision_id": decision.decision_id,
                    "title": decision.title,
                    "approach": decision.implementation_approach
                })
            
            # Collect outstanding risks
            if decision.risks:
                summary["outstanding_risks"].extend([
                    {
                        "decision_id": decision.decision_id,
                        "decision_title": decision.title,
                        "risk": risk
                    }
                    for risk in decision.risks
                ])
            
            # High-impact decisions are key decisions
            if decision.impact_level == "high":
                summary["key_decisions"].append({
                    "decision_id": decision.decision_id,
                    "title": decision.title,
                    "decision": decision.decision,
                    "rationale": decision.rationale,
                    "impact": decision.impact_level
                })

        # Convert sets to lists for JSON serialization
        summary["affected_files"] = list(summary["affected_files"])
        summary["affected_components"] = list(summary["affected_components"])
        
        # Generate context narrative
        if decisions:
            summary["context_for_recovery"] = self._generate_context_narrative(decisions, summary)
        
        return summary

    def _generate_context_narrative(self, decisions: List[ArchitecturalDecisionModel], summary: Dict[str, Any]) -> str:
        """Generate a human-readable context narrative from decisions."""
        narrative_parts = []
        
        narrative_parts.append(f"During this subtask, {len(decisions)} architectural decisions were made.")
        
        if summary["key_decisions"]:
            narrative_parts.append(f"\nKey high-impact decisions:")
            for decision in summary["key_decisions"]:
                narrative_parts.append(f"- {decision['title']}: {decision['decision']}")
        
        if summary["affected_files"]:
            narrative_parts.append(f"\nFiles affected by decisions: {', '.join(summary['affected_files'][:5])}")
            if len(summary["affected_files"]) > 5:
                narrative_parts.append(f" and {len(summary['affected_files']) - 5} others")
        
        if summary["outstanding_risks"]:
            narrative_parts.append(f"\nOutstanding risks to monitor:")
            for risk in summary["outstanding_risks"][:3]:  # Show top 3 risks
                narrative_parts.append(f"- {risk['risk']} (from {risk['decision_title']})")
        
        return "".join(narrative_parts)

    async def create_decision_evolution(self,
                                      original_decision_id: str,
                                      new_decision_id: str,
                                      evolution_type: EvolutionType,
                                      reason: str) -> str:
        """
        Track the evolution of a decision (supersession, refinement, etc.).
        
        Args:
            original_decision_id: ID of the original decision
            new_decision_id: ID of the new decision
            evolution_type: Type of evolution
            reason: Reason for the evolution
            
        Returns:
            str: Evolution record ID
        """
        evolution = DecisionEvolutionModel(
            evolution_id=str(uuid.uuid4()),
            original_decision_id=original_decision_id,
            new_decision_id=new_decision_id,
            evolution_type=evolution_type.value,
            evolution_reason=reason,
            timestamp=datetime.utcnow()
        )
        
        self.db_session.add(evolution)
        
        # Update original decision status if superseded
        if evolution_type == EvolutionType.SUPERSEDED:
            original_decision = self.db_session.query(ArchitecturalDecisionModel).filter_by(
                decision_id=original_decision_id
            ).first()
            if original_decision:
                original_decision.status = DecisionStatus.SUPERSEDED.value
        
        self.db_session.commit()
        
        return evolution.evolution_id

    async def search_decisions(self,
                             search_terms: List[str] = None,
                             category: DecisionCategory = None,
                             impact_level: DecisionImpact = None,
                             affected_file: str = None) -> List[ArchitecturalDecisionModel]:
        """
        Search for decisions based on various criteria.
        
        Args:
            search_terms: Terms to search in title, decision, and rationale
            category: Filter by decision category
            impact_level: Filter by impact level
            affected_file: Filter by affected file
            
        Returns:
            List of matching decisions
        """
        query = self.db_session.query(ArchitecturalDecisionModel)
        
        if category:
            query = query.filter(ArchitecturalDecisionModel.category == category.value)
        
        if impact_level:
            query = query.filter(ArchitecturalDecisionModel.impact_level == impact_level.value)
        
        if affected_file:
            # JSON search for affected files (SQLite compatible)
            query = query.filter(
                ArchitecturalDecisionModel.affected_files.contains(f'"{affected_file}"')
            )
        
        if search_terms:
            # Search in title, decision, and rationale
            search_filter = None
            for term in search_terms:
                term_filter = (
                    ArchitecturalDecisionModel.title.contains(term) |
                    ArchitecturalDecisionModel.decision.contains(term) |
                    ArchitecturalDecisionModel.rationale.contains(term)
                )
                if search_filter is None:
                    search_filter = term_filter
                else:
                    search_filter = search_filter & term_filter
            
            query = query.filter(search_filter)
        
        return query.order_by(ArchitecturalDecisionModel.timestamp.desc()).all()


# Convenience functions for easy integration

def create_decision_capture_for_subtask(subtask_id: str, session_id: str, specialist_type: str, db_session: Session) -> DecisionCapture:
    """
    Create a decision capture instance for a subtask.
    
    Args:
        subtask_id: The ID of the subtask
        session_id: Current session ID
        specialist_type: Type of specialist
        db_session: SQLAlchemy database session
        
    Returns:
        DecisionCapture instance
    """
    return DecisionCapture(subtask_id, session_id, specialist_type, db_session)


async def generate_context_recovery_summary(subtask_id: str, db_session: Session) -> Dict[str, Any]:
    """
    Generate context recovery summary for a subtask.
    
    Args:
        subtask_id: The subtask ID
        db_session: SQLAlchemy database session
        
    Returns:
        Dict containing context recovery information
    """
    decision_manager = DecisionManager(db_session)
    return await decision_manager.generate_decision_context_summary(subtask_id)