"""
Service configuration for dependency injection.

This module configures all services for the application, replacing
singleton patterns with proper dependency injection.
"""

from typing import Dict, Any
import os

from .container import ServiceContainer, ServiceRegistrar
from .registration import AutoRegistration
from ..database.repository_factory import RepositoryFactory
from ...domain.repositories import TaskRepository, StateRepository, SpecialistRepository
from ...domain.services import (
    TaskService,
    TaskBreakdownService,
    SpecialistAssignmentService,
    ProgressTrackingService,
    ResultSynthesisService,
    OrchestrationCoordinator
)


def configure_infrastructure_services(registrar: ServiceRegistrar, 
                                    config: Dict[str, Any]) -> ServiceRegistrar:
    """
    Configure infrastructure services.
    
    Args:
        registrar: Service registrar
        config: Application configuration
        
    Returns:
        The registrar for chaining
    """
    # Repository Factory
    def create_repository_factory(container: ServiceContainer) -> RepositoryFactory:
        from ..database.repository_factory import create_repository_factory
        return create_repository_factory(config)
    
    registrar.register_factory(RepositoryFactory, create_repository_factory).as_singleton()
    
    # Repositories
    def create_task_repository(container: ServiceContainer) -> TaskRepository:
        factory = container.get_service(RepositoryFactory)
        return factory.create_task_repository()
    
    def create_state_repository(container: ServiceContainer) -> StateRepository:
        factory = container.get_service(RepositoryFactory)
        return factory.create_state_repository()
    
    def create_specialist_repository(container: ServiceContainer) -> SpecialistRepository:
        factory = container.get_service(RepositoryFactory)
        return factory.create_specialist_repository()
    
    registrar.register_factory(TaskRepository, create_task_repository).as_singleton()
    registrar.register_factory(StateRepository, create_state_repository).as_singleton()
    registrar.register_factory(SpecialistRepository, create_specialist_repository).as_singleton()
    
    return registrar


def configure_domain_services(registrar: ServiceRegistrar,
                            config: Dict[str, Any]) -> ServiceRegistrar:
    """
    Configure domain services.
    
    Args:
        registrar: Service registrar
        config: Application configuration
        
    Returns:
        The registrar for chaining
    """
    project_dir = config.get('project_dir', os.getcwd())
    
    # Basic task service
    def create_task_service(container: ServiceContainer) -> TaskService:
        return TaskService(
            container.get_service(TaskRepository),
            container.get_service(StateRepository)
        )
    
    registrar.register_factory(TaskService, create_task_service).as_singleton()
    
    # Task breakdown service
    def create_breakdown_service(container: ServiceContainer) -> TaskBreakdownService:
        return TaskBreakdownService(
            container.get_service(TaskRepository),
            container.get_service(StateRepository),
            container.get_service(SpecialistRepository)
        )
    
    registrar.register_factory(TaskBreakdownService, create_breakdown_service).as_singleton()
    
    # Specialist assignment service
    def create_assignment_service(container: ServiceContainer) -> SpecialistAssignmentService:
        return SpecialistAssignmentService(
            container.get_service(TaskRepository),
            container.get_service(StateRepository),
            container.get_service(SpecialistRepository),
            project_dir
        )
    
    registrar.register_factory(SpecialistAssignmentService, create_assignment_service).as_singleton()
    
    # Progress tracking service
    def create_tracking_service(container: ServiceContainer) -> ProgressTrackingService:
        return ProgressTrackingService(
            container.get_service(TaskRepository),
            container.get_service(StateRepository)
        )
    
    registrar.register_factory(ProgressTrackingService, create_tracking_service).as_singleton()
    
    # Result synthesis service
    def create_synthesis_service(container: ServiceContainer) -> ResultSynthesisService:
        return ResultSynthesisService(
            container.get_service(TaskRepository),
            container.get_service(StateRepository)
        )
    
    registrar.register_factory(ResultSynthesisService, create_synthesis_service).as_singleton()
    
    # Orchestration coordinator
    def create_coordinator(container: ServiceContainer) -> OrchestrationCoordinator:
        return OrchestrationCoordinator(
            container.get_service(TaskRepository),
            container.get_service(StateRepository),
            container.get_service(SpecialistRepository),
            project_dir
        )
    
    registrar.register_factory(OrchestrationCoordinator, create_coordinator).as_singleton()
    
    return registrar


def configure_legacy_services(registrar: ServiceRegistrar,
                            config: Dict[str, Any]) -> ServiceRegistrar:
    """
    Configure legacy services for backward compatibility.
    
    Args:
        registrar: Service registrar
        config: Application configuration
        
    Returns:
        The registrar for chaining
    """
    # Legacy StateManager (if needed for compatibility)
    def create_state_manager(container: ServiceContainer):
        from .orchestrator.orchestration_state_manager import StateManager
        # Create with repository dependencies
        state_repo = container.get_service(StateRepository)
        return StateManager(state_repo)
    
    # Legacy SpecialistManager (if needed for compatibility)  
    def create_specialist_manager(container: ServiceContainer):
        from .orchestrator.specialist_management_service import SpecialistManager
        # Create with repository dependencies
        specialist_repo = container.get_service(SpecialistRepository)
        return SpecialistManager(specialist_repo)
    
    # Register legacy services as needed
    # registrar.register_factory(StateManager, create_state_manager).as_singleton()
    # registrar.register_factory(SpecialistManager, create_specialist_manager).as_singleton()
    
    return registrar


def configure_all_services(container: ServiceContainer, config: Dict[str, Any]):
    """
    Configure all application services.
    
    Args:
        container: Service container
        config: Application configuration
    """
    registrar = container.register()
    
    # Configure in order of dependencies
    configure_infrastructure_services(registrar, config)
    configure_domain_services(registrar, config)
    configure_legacy_services(registrar, config)
    
    # Apply all registrations
    registrar.build()


def create_configured_container(config: Dict[str, Any]) -> ServiceContainer:
    """
    Create and configure a service container.
    
    Args:
        config: Application configuration
        
    Returns:
        Configured ServiceContainer
    """
    container = ServiceContainer()
    configure_all_services(container, config)
    return container


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration for services.
    
    Returns:
        Default configuration dictionary
    """
    return {
        'database': {
            'url': 'sqlite:///.task_orchestrator/orchestrator.db',
            'timeout': 30.0,
            'check_same_thread': False
        },
        'project_dir': os.getcwd()
    }