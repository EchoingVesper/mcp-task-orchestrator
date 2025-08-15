"""
Lifecycle Models - Task lifecycle state machine and transitions.

Contains lifecycle management models extracted from generic_models.py
to support proper task state transitions and lifecycle management.
"""

from typing import Dict, List
from ..value_objects.enums import LifecycleStage


class LifecycleStateMachine:
    """Defines valid lifecycle transitions and state management rules."""
    
    # Valid transitions: from_stage -> [allowed_to_stages]
    TRANSITIONS = {
        LifecycleStage.CREATED: [
            LifecycleStage.PLANNING,
            LifecycleStage.READY,
            LifecycleStage.ACTIVE,
            LifecycleStage.ARCHIVED
        ],
        LifecycleStage.PLANNING: [
            LifecycleStage.READY,
            LifecycleStage.BLOCKED,
            LifecycleStage.ARCHIVED
        ],
        LifecycleStage.READY: [
            LifecycleStage.ACTIVE,
            LifecycleStage.BLOCKED,
            LifecycleStage.ARCHIVED
        ],
        LifecycleStage.ACTIVE: [
            LifecycleStage.BLOCKED,
            LifecycleStage.REVIEW,
            LifecycleStage.COMPLETED,
            LifecycleStage.FAILED,
            LifecycleStage.ARCHIVED
        ],
        LifecycleStage.BLOCKED: [
            LifecycleStage.READY,
            LifecycleStage.ACTIVE,
            LifecycleStage.FAILED,
            LifecycleStage.ARCHIVED
        ],
        LifecycleStage.REVIEW: [
            LifecycleStage.ACTIVE,
            LifecycleStage.COMPLETED,
            LifecycleStage.FAILED,
            LifecycleStage.ARCHIVED
        ],
        LifecycleStage.COMPLETED: [
            LifecycleStage.ARCHIVED,
            LifecycleStage.SUPERSEDED
        ],
        LifecycleStage.FAILED: [
            LifecycleStage.READY,
            LifecycleStage.ACTIVE,
            LifecycleStage.ARCHIVED
        ],
        LifecycleStage.ARCHIVED: [
            # Terminal state - no transitions allowed
        ],
        LifecycleStage.SUPERSEDED: [
            LifecycleStage.ARCHIVED
        ]
    }
    
    @classmethod
    def can_transition(cls, from_stage: LifecycleStage, to_stage: LifecycleStage) -> bool:
        """Check if transition from one stage to another is allowed."""
        return to_stage in cls.TRANSITIONS.get(from_stage, [])
    
    @classmethod
    def get_allowed_transitions(cls, from_stage: LifecycleStage) -> List[LifecycleStage]:
        """Get list of allowed transitions from a given stage."""
        return cls.TRANSITIONS.get(from_stage, []).copy()
    
    @classmethod
    def is_terminal_stage(cls, stage: LifecycleStage) -> bool:
        """Check if a stage is terminal (no outgoing transitions)."""
        return len(cls.TRANSITIONS.get(stage, [])) == 0
    
    @classmethod
    def get_path_to_stage(cls, from_stage: LifecycleStage, to_stage: LifecycleStage) -> List[LifecycleStage]:
        """Find the shortest path between two stages (if one exists)."""
        if from_stage == to_stage:
            return [from_stage]
        
        # Simple BFS to find shortest path
        queue = [(from_stage, [from_stage])]
        visited = {from_stage}
        
        while queue:
            current_stage, path = queue.pop(0)
            
            for next_stage in cls.TRANSITIONS.get(current_stage, []):
                if next_stage == to_stage:
                    return path + [next_stage]
                
                if next_stage not in visited:
                    visited.add(next_stage)
                    queue.append((next_stage, path + [next_stage]))
        
        return []  # No path found
    
    @classmethod
    def validate_transition_sequence(cls, stages: List[LifecycleStage]) -> List[str]:
        """Validate a sequence of stage transitions and return any errors."""
        errors = []
        
        for i in range(len(stages) - 1):
            current = stages[i]
            next_stage = stages[i + 1]
            
            if not cls.can_transition(current, next_stage):
                errors.append(f"Invalid transition from {current.value} to {next_stage.value}")
        
        return errors
    
    @classmethod
    def get_stage_description(cls, stage: LifecycleStage) -> str:
        """Get human-readable description of a lifecycle stage."""
        descriptions = {
            LifecycleStage.CREATED: "Task has been created but not yet planned",
            LifecycleStage.PLANNING: "Task is being planned and prepared",
            LifecycleStage.READY: "Task is ready to be worked on",
            LifecycleStage.ACTIVE: "Task is actively being worked on",
            LifecycleStage.BLOCKED: "Task is blocked and cannot proceed",
            LifecycleStage.REVIEW: "Task is under review or validation",
            LifecycleStage.COMPLETED: "Task has been successfully completed",
            LifecycleStage.FAILED: "Task has failed and cannot be completed",
            LifecycleStage.ARCHIVED: "Task has been archived for long-term storage",
            LifecycleStage.SUPERSEDED: "Task has been replaced by another task"
        }
        
        return descriptions.get(stage, f"Unknown stage: {stage.value}")
    
    @classmethod
    def get_stage_color(cls, stage: LifecycleStage) -> str:
        """Get color code for UI representation of lifecycle stage."""
        colors = {
            LifecycleStage.CREATED: "#808080",      # Gray
            LifecycleStage.PLANNING: "#FFA500",    # Orange
            LifecycleStage.READY: "#00CED1",       # Dark Turquoise
            LifecycleStage.ACTIVE: "#32CD32",      # Lime Green
            LifecycleStage.BLOCKED: "#FF4500",     # Orange Red
            LifecycleStage.REVIEW: "#9370DB",      # Medium Purple
            LifecycleStage.COMPLETED: "#228B22",   # Forest Green
            LifecycleStage.FAILED: "#DC143C",      # Crimson
            LifecycleStage.ARCHIVED: "#696969",    # Dim Gray
            LifecycleStage.SUPERSEDED: "#A9A9A9"   # Dark Gray
        }
        
        return colors.get(stage, "#000000")  # Default to black
    
    @classmethod
    def get_reachable_stages(cls, from_stage: LifecycleStage) -> List[LifecycleStage]:
        """Get all stages that can be reached from the given stage (recursive)."""
        reachable = set()
        to_visit = [from_stage]
        
        while to_visit:
            current = to_visit.pop()
            if current in reachable:
                continue
            
            reachable.add(current)
            for next_stage in cls.TRANSITIONS.get(current, []):
                if next_stage not in reachable:
                    to_visit.append(next_stage)
        
        return sorted(list(reachable), key=lambda x: x.value)
    
    @classmethod
    def suggest_next_stage(cls, current_stage: LifecycleStage, context: Dict[str, any] = None) -> LifecycleStage:
        """Suggest the most appropriate next stage based on current stage and context."""
        # Default suggestions based on typical workflow
        suggestions = {
            LifecycleStage.CREATED: LifecycleStage.PLANNING,
            LifecycleStage.PLANNING: LifecycleStage.READY,
            LifecycleStage.READY: LifecycleStage.ACTIVE,
            LifecycleStage.ACTIVE: LifecycleStage.REVIEW,
            LifecycleStage.BLOCKED: LifecycleStage.READY,
            LifecycleStage.REVIEW: LifecycleStage.COMPLETED,
            LifecycleStage.FAILED: LifecycleStage.ACTIVE,
            LifecycleStage.COMPLETED: LifecycleStage.ARCHIVED,
            LifecycleStage.SUPERSEDED: LifecycleStage.ARCHIVED
        }
        
        default_suggestion = suggestions.get(current_stage)
        
        # If context is provided, make more intelligent suggestions
        if context and default_suggestion:
            # Example context-based logic
            if context.get('has_errors') and current_stage == LifecycleStage.ACTIVE:
                return LifecycleStage.FAILED
            elif context.get('dependencies_blocked') and current_stage == LifecycleStage.READY:
                return LifecycleStage.BLOCKED
        
        return default_suggestion or current_stage