"""
Use case for managing specialists.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from ...domain import (
    SpecialistRepository,
    Specialist,
    SpecialistType,
    SpecialistNotFoundError,
    OrchestrationError
)


@dataclass
class ManageSpecialistsUseCase:
    """
    Application use case for managing specialists.
    
    This use case handles specialist creation, retrieval, and matching.
    """
    specialist_repository: SpecialistRepository
    
    async def get_specialist(self, specialist_type: str) -> Specialist:
        """
        Get a specialist by type.
        
        Args:
            specialist_type: Type of specialist to retrieve
            
        Returns:
            Specialist instance
            
        Raises:
            SpecialistNotFoundError: If specialist not found
        """
        try:
            specialist = await self.specialist_repository.get_by_type(specialist_type)
            if not specialist:
                raise SpecialistNotFoundError(specialist_type)
            return specialist
        except SpecialistNotFoundError:
            raise
        except Exception as e:
            raise OrchestrationError(
                f"Failed to get specialist: {str(e)}",
                {"specialist_type": specialist_type}
            )
    
    async def list_specialists(self) -> List[Specialist]:
        """
        List all available specialists.
        
        Returns:
            List of all specialists
        """
        try:
            return await self.specialist_repository.list_all()
        except Exception as e:
            raise OrchestrationError(
                f"Failed to list specialists: {str(e)}"
            )
    
    async def find_best_specialist(self, task_requirements: List[str]) -> Optional[Specialist]:
        """
        Find the best specialist for given task requirements.
        
        Args:
            task_requirements: List of required capabilities
            
        Returns:
            Best matching specialist or None
        """
        try:
            specialists = await self.specialist_repository.list_all()
            
            if not specialists:
                return None
            
            # Calculate match scores
            matches = []
            for specialist in specialists:
                score = specialist.match_score(task_requirements)
                if score > 0:
                    matches.append((specialist, score))
            
            if not matches:
                return None
            
            # Sort by score and return best match
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0][0]
            
        except Exception as e:
            raise OrchestrationError(
                f"Failed to find specialist: {str(e)}",
                {"requirements": task_requirements}
            )
    
    async def create_custom_specialist(
        self,
        name: str,
        description: str,
        expertise_areas: List[str],
        system_prompt: str,
        **kwargs
    ) -> Specialist:
        """
        Create a custom specialist.
        
        Args:
            name: Specialist name
            description: Specialist description
            expertise_areas: Areas of expertise
            system_prompt: System prompt for the specialist
            **kwargs: Additional specialist attributes
            
        Returns:
            Created specialist
        """
        try:
            specialist = Specialist.create_custom(
                name=name,
                description=description,
                expertise_areas=expertise_areas,
                system_prompt=system_prompt,
                **kwargs
            )
            
            # Save to repository
            await self.specialist_repository.save(specialist)
            
            return specialist
            
        except Exception as e:
            raise OrchestrationError(
                f"Failed to create specialist: {str(e)}",
                {
                    "name": name,
                    "description": description,
                    "expertise_areas": expertise_areas
                }
            )
    
    async def get_specialist_types(self) -> List[str]:
        """
        Get all available specialist types.
        
        Returns:
            List of specialist type names
        """
        try:
            # Get built-in types
            types = [t.value for t in SpecialistType]
            
            # Add any custom types from repository
            specialists = await self.specialist_repository.list_all()
            for specialist in specialists:
                if specialist.type == SpecialistType.CUSTOM and specialist.name not in types:
                    types.append(specialist.name.lower().replace(" ", "_"))
            
            return types
            
        except Exception as e:
            raise OrchestrationError(
                f"Failed to get specialist types: {str(e)}"
            )