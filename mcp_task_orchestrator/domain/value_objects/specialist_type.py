"""
Specialist-related value objects.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class SpecialistType(str, Enum):
    """Built-in specialist types."""
    ARCHITECT = "architect"
    IMPLEMENTER = "implementer" 
    REVIEWER = "reviewer"
    TESTER = "tester"
    DOCUMENTER = "documenter"
    ANALYST = "analyst"
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    OPTIMIZER = "optimizer"
    DEBUGGER = "debugger"  # Added for compatibility with default_roles.yaml
    CODER = "coder"  # Added as alias for implementer
    DEVOPS = "devops"  # Added for infrastructure tasks
    GENERIC = "generic"  # Added for flexible task assignment
    CUSTOM = "custom"
    
    @property
    def default_capabilities(self) -> List[str]:
        """Get default capabilities for this specialist type."""
        capabilities_map = {
            SpecialistType.ARCHITECT: ["system_design", "architecture_patterns", "technology_selection"],
            SpecialistType.IMPLEMENTER: ["coding", "implementation", "debugging"],
            SpecialistType.REVIEWER: ["code_review", "quality_assurance", "best_practices"],
            SpecialistType.TESTER: ["test_design", "test_execution", "test_automation"],
            SpecialistType.DOCUMENTER: ["technical_writing", "api_documentation", "user_guides"],
            SpecialistType.ANALYST: ["requirements_analysis", "data_analysis", "problem_solving"],
            SpecialistType.COORDINATOR: ["project_management", "task_coordination", "communication"],
            SpecialistType.RESEARCHER: ["information_gathering", "analysis", "synthesis"],
            SpecialistType.OPTIMIZER: ["performance_tuning", "optimization", "profiling"],
            SpecialistType.DEBUGGER: ["debugging", "troubleshooting", "root_cause_analysis"],
            SpecialistType.CODER: ["coding", "implementation", "algorithm_design"],
            SpecialistType.DEVOPS: ["infrastructure", "deployment", "automation", "monitoring"],
            SpecialistType.GENERIC: ["general_tasks", "flexible_assignment"],
            SpecialistType.CUSTOM: []
        }
        return capabilities_map.get(self, [])
    
    @property
    def interaction_style(self) -> str:
        """Get default interaction style for this specialist type."""
        styles = {
            SpecialistType.ARCHITECT: "analytical",
            SpecialistType.IMPLEMENTER: "practical",
            SpecialistType.REVIEWER: "critical",
            SpecialistType.TESTER: "methodical",
            SpecialistType.DOCUMENTER: "explanatory",
            SpecialistType.ANALYST: "investigative",
            SpecialistType.COORDINATOR: "collaborative",
            SpecialistType.RESEARCHER: "exploratory",
            SpecialistType.OPTIMIZER: "efficiency-focused",
            SpecialistType.DEBUGGER: "diagnostic",
            SpecialistType.CODER: "practical",
            SpecialistType.DEVOPS: "systematic",
            SpecialistType.GENERIC: "versatile",
            SpecialistType.CUSTOM: "professional"
        }
        return styles.get(self, "professional")


@dataclass(frozen=True)
class SpecialistCapability:
    """Represents a capability or skill of a specialist."""
    name: str
    description: str
    proficiency_level: float  # 0.0 to 1.0
    
    def __post_init__(self):
        if not 0.0 <= self.proficiency_level <= 1.0:
            raise ValueError("Proficiency level must be between 0.0 and 1.0")
        if not self.name:
            raise ValueError("Capability name cannot be empty")
    
    @property
    def proficiency_category(self) -> str:
        """Get proficiency category based on level."""
        if self.proficiency_level >= 0.9:
            return "expert"
        elif self.proficiency_level >= 0.7:
            return "advanced"
        elif self.proficiency_level >= 0.5:
            return "intermediate"
        elif self.proficiency_level >= 0.3:
            return "basic"
        else:
            return "novice"


@dataclass(frozen=True)
class SpecialistMatch:
    """Value object representing a specialist match score."""
    specialist_type: SpecialistType
    match_score: float  # 0.0 to 1.0
    matched_capabilities: List[str]
    
    def __post_init__(self):
        if not 0.0 <= self.match_score <= 1.0:
            raise ValueError("Match score must be between 0.0 and 1.0")
    
    @property
    def is_good_match(self) -> bool:
        """Check if this is a good match (>= 0.7)."""
        return self.match_score >= 0.7
    
    @property
    def match_category(self) -> str:
        """Get match category based on score."""
        if self.match_score >= 0.9:
            return "excellent"
        elif self.match_score >= 0.7:
            return "good"
        elif self.match_score >= 0.5:
            return "fair"
        else:
            return "poor"