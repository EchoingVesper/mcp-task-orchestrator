"""
Specialist entity - Represents a specialized AI agent role.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

# Import these from value objects to avoid duplication
from ..value_objects.specialist_type import SpecialistType, SpecialistCapability as SpecialistCapabilityVO


@dataclass
class Specialist:
    """
    Domain entity representing a specialist role.
    
    Specialists are AI agents with specific expertise and responsibilities.
    """
    name: str
    type: SpecialistType
    description: str
    expertise_areas: List[str]
    capabilities: List[SpecialistCapabilityVO]
    system_prompt: str
    interaction_style: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_architect(cls) -> 'Specialist':
        """Factory method for Architect specialist."""
        return cls(
            name="System Architect",
            type=SpecialistType.ARCHITECT,
            description="Designs system architecture and high-level solutions",
            expertise_areas=["system design", "architecture patterns", "technology selection"],
            capabilities=[
                SpecialistCapabilityVO("System Design", "Create comprehensive system architectures", 0.95),
                SpecialistCapabilityVO("Pattern Recognition", "Identify and apply design patterns", 0.9),
                SpecialistCapabilityVO("Technology Assessment", "Evaluate technology choices", 0.85)
            ],
            system_prompt="You are a System Architect specialist. Focus on creating robust, scalable architectures.",
            interaction_style="analytical"
        )
    
    @classmethod
    def create_implementer(cls) -> 'Specialist':
        """Factory method for Implementer specialist."""
        return cls(
            name="Code Implementer", 
            type=SpecialistType.IMPLEMENTER,
            description="Implements code solutions based on designs",
            expertise_areas=["coding", "implementation", "best practices"],
            capabilities=[
                SpecialistCapabilityVO("Code Implementation", "Write production-quality code", 0.95),
                SpecialistCapabilityVO("Problem Solving", "Solve technical challenges", 0.9),
                SpecialistCapabilityVO("Optimization", "Optimize code performance", 0.8)
            ],
            system_prompt="You are a Code Implementer specialist. Focus on writing clean, efficient code.",
            interaction_style="practical"
        )
    
    @classmethod
    def create_reviewer(cls) -> 'Specialist':
        """Factory method for Reviewer specialist."""
        return cls(
            name="Code Reviewer",
            type=SpecialistType.REVIEWER,
            description="Reviews code quality and suggests improvements",
            expertise_areas=["code review", "quality assurance", "best practices"],
            capabilities=[
                SpecialistCapabilityVO("Code Review", "Identify issues and improvements", 0.95),
                SpecialistCapabilityVO("Security Analysis", "Spot security vulnerabilities", 0.85),
                SpecialistCapabilityVO("Performance Analysis", "Identify performance issues", 0.8)
            ],
            system_prompt="You are a Code Reviewer specialist. Focus on code quality and maintainability.",
            interaction_style="critical"
        )
    
    @classmethod
    def create_custom(cls, name: str, description: str, expertise_areas: List[str], 
                     system_prompt: str, **kwargs) -> 'Specialist':
        """Factory method for custom specialists."""
        return cls(
            name=name,
            type=SpecialistType.CUSTOM,
            description=description,
            expertise_areas=expertise_areas,
            capabilities=kwargs.get('capabilities', []),
            system_prompt=system_prompt,
            interaction_style=kwargs.get('interaction_style', 'professional'),
            metadata=kwargs.get('metadata', {})
        )
    
    def match_score(self, task_requirements: List[str]) -> float:
        """Calculate how well this specialist matches task requirements."""
        if not task_requirements:
            return 0.5  # Neutral score for no requirements
        
        matches = sum(1 for req in task_requirements if any(
            req.lower() in area.lower() or area.lower() in req.lower()
            for area in self.expertise_areas
        ))
        
        return matches / len(task_requirements)
    
    def enhance_prompt(self, base_prompt: str) -> str:
        """Enhance a prompt with specialist-specific context."""
        return f"{self.system_prompt}\n\n{base_prompt}"


@dataclass  
class SpecialistContext:
    """Context provided to a specialist for task execution."""
    specialist: Specialist
    task_description: str
    parent_context: Optional[str]
    related_artifacts: List[str]
    constraints: List[str]
    guidance: Dict[str, Any] = field(default_factory=dict)
    
    def build_prompt(self) -> str:
        """Build the complete prompt for the specialist."""
        sections = [
            self.specialist.system_prompt,
            f"\nTask: {self.task_description}"
        ]
        
        if self.parent_context:
            sections.append(f"\nContext from parent task:\n{self.parent_context}")
        
        if self.related_artifacts:
            sections.append(f"\nRelated artifacts: {', '.join(self.related_artifacts)}")
        
        if self.constraints:
            sections.append("\nConstraints:")
            for constraint in self.constraints:
                sections.append(f"- {constraint}")
        
        if self.guidance:
            sections.append("\nAdditional guidance:")
            for key, value in self.guidance.items():
                sections.append(f"- {key}: {value}")
        
        return "\n".join(sections)