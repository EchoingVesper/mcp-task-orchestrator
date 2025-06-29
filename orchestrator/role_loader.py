"""
Utility functions for loading role definition files from various locations.
"""

import os
import yaml
import shutil
from pathlib import Path
from typing import Dict, Optional, List, Tuple


def find_role_files(project_dir: Optional[str] = None) -> List[Path]:
    """
    Find all role definition files in the given project directory and its parent directories.
    
    Args:
        project_dir: The project directory to search in. If None, uses current working directory.
        
    Returns:
        List of paths to role definition files, ordered by priority (project-specific first).
    """
    role_files = []
    
    # Start with current directory if project_dir is not specified
    if project_dir is None:
        project_dir = os.getcwd()
    
    project_path = Path(project_dir)
    
    # First, check in .task_orchestrator/roles/ directory (highest priority)
    task_orchestrator_roles_dir = project_path / ".task_orchestrator" / "roles"
    if task_orchestrator_roles_dir.exists():
        role_yaml_files = list(task_orchestrator_roles_dir.glob("*.yaml"))
        role_files.extend(role_yaml_files)
    
    # Next, look for role files in the project directory root
    project_role_files = list(project_path.glob("*.yaml"))
    role_yaml_files = [f for f in project_role_files if f.stem.endswith("_roles")]
    role_files.extend(role_yaml_files)
    
    # Add the default role file as fallback
    default_role_file = Path(__file__).parent.parent.parent / "config" / "default_roles.yaml"
    if default_role_file.exists():
        role_files.append(default_role_file)
    
    return role_files


def load_role_file(file_path: Path) -> Dict:
    """
    Load and validate a role definition file.
    
    Args:
        file_path: Path to the role definition file.
        
    Returns:
        Dictionary containing the role definitions.
        
    Raises:
        ValueError: If the file is invalid or cannot be loaded.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            role_data = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(role_data, dict):
                raise ValueError(f"Role file {file_path} must contain a dictionary")
            
            return role_data
    except Exception as e:
        raise ValueError(f"Failed to load role file {file_path}: {str(e)}")


def create_project_roles_file(project_dir: Optional[str] = None) -> Tuple[bool, Path]:
    """
    Create a project-specific roles file that will be loaded automatically.
    
    Args:
        project_dir: The project directory to create the file in. If None, uses current working directory.
        
    Returns:
        Tuple of (success, file_path)
    """
    if project_dir is None:
        project_dir = os.getcwd()
    
    project_path = Path(project_dir)
    # Create .task_orchestrator/roles directory
    roles_dir = project_path / ".task_orchestrator" / "roles"
    roles_dir.mkdir(parents=True, exist_ok=True)
    
    project_roles_file = roles_dir / "project_roles.yaml"
    
    # Don't overwrite if the file already exists
    if project_roles_file.exists():
        return (False, project_roles_file)
    
    # Get the default roles file as a template
    default_role_file = Path(__file__).parent.parent.parent / "config" / "default_roles.yaml"
    
    try:
        if default_role_file.exists():
            # Copy the default roles file as the project template
            with open(default_role_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add header explaining customization
            customization_header = """# Project-Specific Roles Configuration
# 
# This file contains the specialist role definitions for this project.
# You can customize these roles to match your project's specific needs.
# 
# To customize:
# 1. Edit the role definitions below
# 2. Add new specialist roles as needed
# 3. Save the file - changes will be used automatically
#
# Note: This file overrides the default roles in the MCP Task Orchestrator

"""
            
            # Write the project roles file
            with open(project_roles_file, 'w', encoding='utf-8') as f:
                f.write(customization_header + content)
            
            return (True, project_roles_file)
        else:
            # If default roles file doesn't exist, create a minimal template
            minimal_template = """# Project-Specific Roles Configuration

task_orchestrator:
  role_definition: "You are a Task Orchestrator focused on breaking down complex tasks into manageable subtasks"
  expertise:
    - "Breaking down complex tasks into manageable subtasks"
    - "Assigning appropriate specialist roles to each subtask"
    - "Managing dependencies between subtasks"
    - "Tracking progress and coordinating work"
  approach:
    - "Carefully analyze the requirements and context"
    - "Identify logical components that can be worked on independently"
    - "Create a clear dependency structure between subtasks"
    - "Assign appropriate specialist roles to each subtask"
    - "Estimate effort required for each component"
  output_format: "Structured task breakdown with clear objectives, specialist assignments, effort estimation, and dependency relationships"
  specialist_roles:
    architect: "System design and architecture planning"
    implementer: "Writing code and implementing features"
    debugger: "Fixing issues and optimizing performance"
    documenter: "Creating documentation and guides"
    reviewer: "Code review and quality assurance"
    tester: "Testing and validation"
    researcher: "Research and information gathering"

architect:
  role_definition: "You are a Senior Software Architect with expertise in system design"
  expertise:
    - "System design and architecture patterns"
    - "Technology selection and trade-offs analysis"
    - "Scalability, performance, and reliability planning"
  approach:
    - "Think systematically about requirements and constraints"
    - "Consider scalability, maintainability, security, and performance"
    - "Provide clear architectural decisions with detailed rationale"
  output_format: "Structured architectural plans with clear decisions and rationale"

implementer:
  role_definition: "You are a Senior Software Developer focused on high-quality implementation"
  expertise:
    - "Clean, efficient, and maintainable code implementation"
    - "Software engineering best practices and design patterns"
    - "Performance optimization and efficient algorithms"
  approach:
    - "Write clean, readable, and well-structured code"
    - "Follow established coding standards and conventions"
    - "Include comprehensive error handling and input validation"
  output_format: "Complete, well-commented, production-ready code with explanations"

debugger:
  role_definition: "You are a Senior Debugging and Troubleshooting Specialist"
  expertise:
    - "Root cause analysis and systematic problem diagnosis"
    - "Performance profiling and optimization techniques"
    - "Error analysis and debugging methodologies"
  approach:
    - "Systematically isolate and identify the root cause of issues"
    - "Use appropriate debugging tools and techniques"
    - "Verify fixes thoroughly and test edge cases"
  output_format: "Detailed analysis with root cause identification and step-by-step solutions"

documenter:
  role_definition: "You are a Technical Documentation Specialist"
  expertise:
    - "Clear, comprehensive technical writing and communication"
    - "User-focused documentation design and information architecture"
    - "API documentation and developer guides"
  approach:
    - "Write for your target audience's expertise level and context"
    - "Use clear, concise language with practical examples"
    - "Structure information logically with good navigation"
  output_format: "Well-structured documentation with clear headings and actionable guidance"
"""
            with open(project_roles_file, 'w', encoding='utf-8') as f:
                f.write(minimal_template)
            
            return (True, project_roles_file)
    except Exception as e:
        print(f"Failed to create project roles file: {str(e)}")
        return (False, project_roles_file)


def get_roles(project_dir: Optional[str] = None) -> Dict:
    """
    Get role definitions, prioritizing project-specific roles over default roles.
    
    Args:
        project_dir: The project directory to search in. If None, uses current working directory.
        
    Returns:
        Dictionary containing the role definitions.
    """
    # Normalize project_dir
    if project_dir is None:
        project_dir = os.getcwd()
    
    # Find role files in the project directory
    role_files = find_role_files(project_dir)
    
    # If no project-specific role files found, create one
    if not role_files or all(f.name == "default_roles.yaml" for f in role_files):
        # Only create project roles if there are no project-specific role files
        project_path = Path(project_dir)
        task_orchestrator_dir = project_path / ".task_orchestrator" / "roles"
        
        # Check if there are any files in the task orchestrator roles directory
        has_project_roles = False
        if task_orchestrator_dir.exists():
            has_project_roles = any(task_orchestrator_dir.glob("*.yaml"))
        
        # Also check for any _roles.yaml files in the project root
        project_role_files = [f for f in project_path.glob("*.yaml") if f.stem.endswith("_roles")]
        has_project_roles = has_project_roles or bool(project_role_files)
        
        if not has_project_roles:
            create_project_roles_file(project_dir)
            # Re-scan for role files after creation
            role_files = find_role_files(project_dir)
    
    # If no role files found after creating, return empty dict
    if not role_files:
        return {}
    
    # Load the first valid role file (highest priority)
    for role_file in role_files:
        try:
            return load_role_file(role_file)
        except ValueError:
            continue
    
    # If all files failed to load, return empty dict
    return {}
