"""
Flexible Specialist Type Validation

Provides validation for both predefined and custom specialist types.
"""

from typing import Union
from .specialist_type import SpecialistType


def validate_specialist_type(specialist_type: Union[str, SpecialistType]) -> bool:
    """
    Validate a specialist type.
    
    Args:
        specialist_type: The specialist type to validate, either as a string or SpecialistType enum
        
    Returns:
        bool: True if the specialist type is valid, False otherwise
    """
    if specialist_type is None:
        return False
    
    # Handle SpecialistType enum
    if isinstance(specialist_type, SpecialistType):
        return True
    
    # Handle string values
    if isinstance(specialist_type, str):
        # Check if it's a predefined specialist type
        try:
            SpecialistType(specialist_type.lower())
            return True
        except ValueError:
            # Allow custom specialist types if they're valid strings
            return (
                len(specialist_type.strip()) > 0 and
                len(specialist_type) <= 50 and
                specialist_type.replace('_', '').replace('-', '').isalnum()
            )
    
    return False


def normalize_specialist_type(specialist_type: Union[str, SpecialistType]) -> str:
    """
    Normalize a specialist type to its string representation.
    
    Args:
        specialist_type: The specialist type to normalize
        
    Returns:
        str: The normalized specialist type string
    """
    if isinstance(specialist_type, SpecialistType):
        return specialist_type.value
    
    if isinstance(specialist_type, str):
        # Try to convert to enum first
        try:
            return SpecialistType(specialist_type.lower()).value
        except ValueError:
            # Return as custom type if valid
            if validate_specialist_type(specialist_type):
                return specialist_type.lower().strip()
    
    return SpecialistType.GENERIC.value  # Default fallback