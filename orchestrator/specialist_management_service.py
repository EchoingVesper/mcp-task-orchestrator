"""
Specialist management for providing role-specific prompts and contexts.
"""

import os
import yaml
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger("mcp_task_orchestrator.specialists")

from .models import SpecialistType, SubTask
from .role_loader import get_roles


class SpecialistManager:
    """Manages specialist roles and their associated prompts and contexts."""
    
    def __init__(self, config_path: str = None, project_dir: str = None):
        # Initialize paths
        self.base_dir = Path(__file__).parent.parent.parent
        self.project_dir = project_dir or os.getcwd()
        self.persistence_dir = Path(self.project_dir) / ".task_orchestrator"
        self.roles_dir = self.persistence_dir / "roles"
        
        # Check if the persistence directory exists, create if not
        self.roles_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine config path
        if config_path is None:
            # Check environment variable first
            config_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_CONFIG_DIR")
            if config_dir:
                config_path = Path(config_dir) / "default_roles.yaml"
            else:
                # First check in the .task_orchestrator/roles directory
                persistence_config = self.roles_dir / "default_roles.yaml"
                if persistence_config.exists():
                    config_path = persistence_config
                else:
                    # Fall back to the original config directory
                    config_path = self.base_dir / "config" / "specialists.yaml"
                    
                    # If the original config exists but not in persistence, migrate it
                    if config_path.exists() and not persistence_config.exists():
                        self._migrate_config_to_persistence(config_path, persistence_config)
        
        self.config_path = Path(config_path)
        self.specialists_config = self._load_specialists_config()
        
        # Initialize Jinja2 environment for template rendering
        template_dir = self.roles_dir / "templates"
        if not template_dir.exists() and self.config_path.parent.exists():
            # Check if templates exist in the original location
            orig_template_dir = self.config_path.parent / "templates"
            if orig_template_dir.exists():
                # Migrate templates to the new location
                template_dir.mkdir(exist_ok=True)
                for template_file in orig_template_dir.glob("*"):
                    shutil.copy(template_file, template_dir / template_file.name)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)) if template_dir.exists() else None
        )
    
    def _migrate_config_to_persistence(self, source_path: Path, target_path: Path) -> None:
        """Migrate configuration from the original location to the persistence directory.
        
        Args:
            source_path: Path to the original configuration file
            target_path: Path to the target configuration file in the persistence directory
        """
        try:
            # Copy the file
            shutil.copy(source_path, target_path)
            logger.info(f"Migrated configuration from {source_path} to {target_path}")
        except Exception as e:
            logger.error(f"Failed to migrate configuration: {str(e)}")
    
    def _load_specialists_config(self) -> Dict:
        """
        Load specialist configurations from role files.
        Prioritizes project-specific role files over default role file.
        """
        # Try to get roles from project directory first
        roles = get_roles(self.project_dir)
        
        # If no roles found or loading failed, fall back to default
        if not roles and self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    roles = yaml.safe_load(f)
            except Exception:
                roles = self._get_default_specialists_config()
        elif not roles:
            roles = self._get_default_specialists_config()
            
        return roles
    
    def _get_default_specialists_config(self) -> Dict:
        """Get default specialist configurations."""
        return {
            "architect": {
                "role_definition": "You are a Senior Software Architect",
                "expertise": [
                    "System design and architecture patterns",
                    "Technology selection and trade-offs", 
                    "Scalability and performance planning",
                    "Security architecture",
                    "API design and integration patterns"
                ],
                "approach": [
                    "Think systematically about requirements and constraints",
                    "Consider scalability, maintainability, and security",
                    "Provide clear architectural diagrams and documentation",
                    "Justify your design decisions with pros and cons"
                ]
            },            "implementer": {
                "role_definition": "You are a Senior Software Developer",
                "expertise": [
                    "Writing clean, efficient, and maintainable code",
                    "Following best practices and design patterns",
                    "Implementing complex features and systems",
                    "Debugging and problem-solving",
                    "Test-driven development"
                ],
                "approach": [
                    "Break down implementation into manageable steps",
                    "Focus on code quality and readability",
                    "Consider edge cases and error handling",
                    "Write tests to verify functionality"
                ]
            },
            "debugger": {
                "role_definition": "You are a Software Debugging Expert",
                "expertise": [
                    "Root cause analysis",
                    "Systematic debugging techniques",
                    "Performance profiling and optimization",
                    "Error tracking and logging",
                    "Fixing complex bugs"
                ],
                "approach": [
                    "Analyze error messages and logs",
                    "Reproduce issues consistently",
                    "Isolate the problem through elimination",
                    "Verify fixes with comprehensive testing"
                ]
            },            "documenter": {
                "role_definition": "You are a Technical Documentation Specialist",
                "expertise": [
                    "Creating clear and comprehensive documentation",
                    "API documentation",
                    "User guides and tutorials",
                    "Technical specifications",
                    "Documentation systems and tools"
                ],
                "approach": [
                    "Understand the audience and their needs",
                    "Structure information logically and hierarchically",
                    "Include examples, diagrams, and code samples",
                    "Ensure accuracy and completeness"
                ]
            },
            "reviewer": {
                "role_definition": "You are a Code Review and Quality Assurance Expert",
                "expertise": [
                    "Code review best practices",
                    "Quality assurance processes",
                    "Performance optimization",
                    "Security vulnerability detection",
                    "Coding standards and style guides"
                ],
                "approach": [
                    "Review code systematically for quality and correctness",
                    "Check for potential bugs and edge cases",
                    "Verify adherence to requirements and standards",
                    "Provide constructive feedback and suggestions"
                ]
            },            "tester": {
                "role_definition": "You are a Software Testing Expert",
                "expertise": [
                    "Test planning and strategy",
                    "Unit, integration, and system testing",
                    "Test automation frameworks",
                    "Performance and load testing",
                    "Security testing"
                ],
                "approach": [
                    "Design comprehensive test cases",
                    "Focus on edge cases and error conditions",
                    "Automate tests where appropriate",
                    "Provide clear test reports and documentation"
                ]
            },
            "researcher": {
                "role_definition": "You are a Technical Research Specialist",
                "expertise": [
                    "Technology evaluation and comparison",
                    "Market and industry research",
                    "Best practices and standards research",
                    "Problem domain analysis",
                    "Research methodology and synthesis"
                ],
                "approach": [
                    "Define clear research questions and objectives",
                    "Gather information from reliable sources",
                    "Analyze findings systematically",
                    "Present conclusions with supporting evidence"
                ]
            }
        }
    
    async def get_specialist_prompt(self, specialist_type: SpecialistType, subtask: SubTask) -> str:
        """Get the specialist prompt for a specific subtask."""
        
        # Get specialist config
        specialist_config = self.specialists_config.get(
            specialist_type.value, self._get_default_specialists_config()[specialist_type.value]
        )
        
        # Build context
        context_parts = []
        
        # Add specialist role and expertise
        context_parts.append(f"# {specialist_config['role_definition']}")
        context_parts.append("\n## Your Expertise:")
        for expertise in specialist_config['expertise']:
            context_parts.append(f"- {expertise}")
        
        # Add approach
        context_parts.append("\n## Your Approach:")
        for approach in specialist_config['approach']:
            context_parts.append(f"- {approach}")
        
        # Add task details
        context_parts.append(f"\n## Task Details:")
        context_parts.append(f"**Task ID:** {subtask.task_id}")
        context_parts.append(f"**Title:** {subtask.title}")
        context_parts.append(f"**Description:** {subtask.description}")
        
        if subtask.dependencies:
            context_parts.append(f"\n**Dependencies:** {', '.join(subtask.dependencies)}")
        
        # Add instructions
        context_parts.append(f"\n## Instructions:")
        context_parts.append(f"""
Please complete this task as the {specialist_type.value} specialist. Focus on your area of expertise.

When you have completed the task, please provide:
1. A summary of what you've done
2. Any artifacts or deliverables created
3. Mention any recommendations for next steps

Remember: You are the {specialist_type.value} specialist for this task. Apply your expertise accordingly.
""")
        
        return "\n".join(context_parts)
    
    async def synthesize_task_results(self, parent_task_id: str, 
                                    completed_subtasks: List[SubTask]) -> str:
        """Synthesize results from multiple completed subtasks."""
        
        synthesis_parts = []
        synthesis_parts.append(f"# Task Synthesis Report")
        synthesis_parts.append(f"**Task ID:** {parent_task_id}")
        synthesis_parts.append(f"**Completed Subtasks:** {len(completed_subtasks)}")
        synthesis_parts.append("")
        
        # Group results by specialist type
        by_specialist = {}
        for subtask in completed_subtasks:
            specialist = subtask.specialist_type.value
            if specialist not in by_specialist:
                by_specialist[specialist] = []
            by_specialist[specialist].append(subtask)
        
        # Synthesize results for each specialist area
        for specialist_type, subtasks in by_specialist.items():
            synthesis_parts.append(f"## {specialist_type.title()} Results")
            for subtask in subtasks:
                synthesis_parts.append(f"### {subtask.title}")
                synthesis_parts.append(f"**Status:** {subtask.status.value}")
                if subtask.results:
                    synthesis_parts.append(f"**Results:** {subtask.results}")
                if subtask.artifacts:
                    synthesis_parts.append(f"**Artifacts:** {', '.join(subtask.artifacts)}")
                synthesis_parts.append("")
        
        # Overall summary
        synthesis_parts.append("## Overall Summary")
        synthesis_parts.append("All subtasks have been completed successfully. ")
        synthesis_parts.append("The orchestrated workflow has achieved its objectives.")
        
        return "\n".join(synthesis_parts)