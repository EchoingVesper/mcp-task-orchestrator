"""
Specialist management for providing role-specific prompts and contexts.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader

from .models import SpecialistType, SubTask


class SpecialistManager:
    """Manages specialist roles and their associated prompts and contexts."""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "specialists.yaml"
        
        self.config_path = Path(config_path)
        self.specialists_config = self._load_specialists_config()
        
        # Initialize Jinja2 environment for template rendering
        template_dir = self.config_path.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)) if template_dir.exists() else None
        )
    
    def _load_specialists_config(self) -> Dict:
        """Load specialist configurations from YAML file."""
        if not self.config_path.exists():
            return self._get_default_specialists_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
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
                    "Provide clear architectural decisions with rationale",
                    "Focus on high-level design before implementation details"
                ],
                "output_format": "Structured architectural plans with diagrams and decision rationale"
            },
            "implementer": {
                "role_definition": "You are a Senior Software Developer",
                "expertise": [
                    "Clean, efficient code implementation",
                    "Best practices and design patterns",
                    "Multiple programming languages and frameworks",
                    "Code organization and modularity",
                    "Performance optimization"
                ],
                "approach": [
                    "Write clean, readable, and maintainable code",
                    "Follow established patterns and conventions",
                    "Include appropriate error handling",
                    "Add helpful comments and documentation",
                    "Consider edge cases and validation"
                ],
                "output_format": "Well-commented, production-ready code with explanations"
            },
            "debugger": {
                "role_definition": "You are a Senior Debugging Specialist",
                "expertise": [
                    "Root cause analysis and problem diagnosis",
                    "Performance profiling and optimization",
                    "Error analysis and troubleshooting",
                    "Testing strategies and validation",
                    "Code review and quality assurance"
                ],
                "approach": [
                    "Systematically isolate and identify issues",
                    "Use debugging tools and techniques effectively",
                    "Verify fixes thoroughly before concluding",
                    "Document findings and prevention strategies"
                ],
                "output_format": "Detailed analysis with root cause identification and solutions"
            },
            "documenter": {
                "role_definition": "You are a Technical Documentation Specialist",
                "expertise": [
                    "Clear, comprehensive technical writing",
                    "User-focused documentation design",
                    "API and code documentation",
                    "Tutorial and guide creation",
                    "Documentation tooling and formats"
                ],
                "approach": [
                    "Write for your target audience's expertise level",
                    "Use clear, concise language with examples",
                    "Structure information logically",
                    "Include practical examples and use cases"
                ],
                "output_format": "Well-structured documentation with examples and clear explanations"
            },
            "reviewer": {
                "role_definition": "You are a Senior Code Review Specialist",
                "expertise": [
                    "Code quality assessment",
                    "Security vulnerability identification",
                    "Performance analysis",
                    "Best practices enforcement",
                    "Architectural consistency review"
                ],
                "approach": [
                    "Provide constructive, specific feedback",
                    "Focus on critical issues first",
                    "Suggest concrete improvements",
                    "Consider maintainability and readability"
                ],
                "output_format": "Structured review with prioritized feedback and recommendations"
            },
            "researcher": {
                "role_definition": "You are a Technical Research Specialist",
                "expertise": [
                    "Information gathering and analysis",
                    "Technology evaluation and comparison",
                    "Market and trend research",
                    "Documentation and resource discovery",
                    "Feasibility analysis"
                ],
                "approach": [
                    "Gather information from reliable sources",
                    "Analyze and synthesize findings",
                    "Present balanced perspectives",
                    "Focus on actionable insights"
                ],
                "output_format": "Comprehensive research reports with sources and recommendations"
            }
        }
    
    async def get_specialist_context(self, specialist_type: SpecialistType, 
                                   description: str, title: str) -> str:
        """Get specialist context and prompts for a specific task."""
        
        specialist_key = specialist_type.value
        config = self.specialists_config.get(specialist_key, {})
        
        # Build the specialist context prompt
        context_parts = []
        
        # Role definition
        role_def = config.get("role_definition", f"You are a {specialist_type.value} specialist")
        context_parts.append(f"## Role\n{role_def}")
        
        # Expertise areas
        expertise = config.get("expertise", [])
        if expertise:
            context_parts.append("## Your Expertise")
            for item in expertise:
                context_parts.append(f"• {item}")
        
        # Approach guidelines
        approach = config.get("approach", [])
        if approach:
            context_parts.append("\n## Your Approach")
            for item in approach:
                context_parts.append(f"• {item}")
        
        # Output format
        output_format = config.get("output_format", "Clear and detailed response")
        context_parts.append(f"\n## Expected Output Format\n{output_format}")
        
        # Current task context
        context_parts.append(f"\n## Current Task\n**Title:** {title}")
        context_parts.append(f"**Description:** {description}")
        
        # Mode activation instruction
        context_parts.append(f"""
## Instructions
You are now operating in {specialist_type.value.upper()} MODE. Focus entirely on this role and apply your specialized expertise to complete the task described above. 

When you have completed this task, be sure to:
1. Provide a clear summary of what was accomplished
2. List any artifacts or deliverables created
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
