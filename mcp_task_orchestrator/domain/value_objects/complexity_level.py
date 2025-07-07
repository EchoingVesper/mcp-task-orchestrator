"""
Complexity Level Value Object

Defines the complexity levels for tasks in the system.
"""

from enum import Enum


class ComplexityLevel(str, Enum):
    """
    Enumeration for task complexity levels.
    
    Used to categorize tasks based on their estimated difficulty
    and resource requirements.
    """
    SIMPLE = "simple"
    MODERATE = "moderate"  
    COMPLEX = "complex"
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> "ComplexityLevel":
        """Create ComplexityLevel from string value."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.MODERATE  # Default fallback