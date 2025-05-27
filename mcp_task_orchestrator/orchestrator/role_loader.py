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
    
    # Look for role files in the project directory
    project_role_files = list(project_path.glob("*.yaml"))
    role_yaml_files = [f for f in project_role_files if f.stem.endswith("_roles")]
    role_files.extend(role_yaml_files)
    
    # Add the default role file
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


def create_example_roles_file(project_dir: Optional[str] = None) -> Tuple[bool, Path]:
    """
    Create an example roles file in the project directory if none exists.
    The example file will be commented out by default.
    
    Args:
        project_dir: The project directory to create the file in. If None, uses current working directory.
        
    Returns:
        Tuple of (success, file_path)
    """
    if project_dir is None:
        project_dir = os.getcwd()
    
    project_path = Path(project_dir)
    example_file_path = project_path / "example_roles.yaml"
    
    # Don't overwrite if the file already exists
    if example_file_path.exists():
        return (False, example_file_path)
    
    # Get the default roles file as a template
    default_role_file = Path(__file__).parent.parent.parent / "config" / "default_roles.yaml"
    
    try:
        if default_role_file.exists():
            # Read the default roles file
            with open(default_role_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Comment out the content
            commented_content = "# Example roles file for this project\n"
            commented_content += "# Uncomment and modify to customize the specialist roles for this project\n"
            commented_content += "# File must be named with a suffix of _roles.yaml (e.g., project_roles.yaml)\n\n"
            
            # Add each line commented out
            for line in content.split('\n'):
                if line.strip() and not line.strip().startswith('#'):
                    commented_content += f"# {line}\n"
                else:
                    commented_content += f"{line}\n"
            
            # Write the example file
            with open(example_file_path, 'w', encoding='utf-8') as f:
                f.write(commented_content)
            
            return (True, example_file_path)
        else:
            # If default roles file doesn't exist, create a minimal example
            minimal_example = """# Example roles file for this project
# Uncomment and modify to customize the specialist roles for this project
# File must be named with a suffix of _roles.yaml (e.g., project_roles.yaml)

# task_orchestrator:
#   role_definition: "You are a Task Orchestrator focused on breaking down complex tasks into manageable subtasks"
#   expertise:
#     - "Breaking down complex tasks into manageable subtasks"
#     - "Assigning appropriate specialist roles to each subtask"
#   approach:
#     - "Carefully analyze the requirements and context"
#     - "Identify logical components that can be worked on independently"
#   output_format: "Structured task breakdown with clear objectives"
#   specialist_roles:
#     custom_role: "Description of your custom role"

# custom_role:
#   role_definition: "You are a Custom Specialist focused on..."
#   expertise:
#     - "Expertise area 1"
#     - "Expertise area 2"
#   approach:
#     - "Approach step 1"
#     - "Approach step 2"
#   output_format: "Expected output format description"
"""
            with open(example_file_path, 'w', encoding='utf-8') as f:
                f.write(minimal_example)
            
            return (True, example_file_path)
    except Exception as e:
        print(f"Failed to create example roles file: {str(e)}")
        return (False, example_file_path)


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
    
    # If no role files found, create an example file
    if not role_files or all(f.name == "default_roles.yaml" for f in role_files):
        # Only create example if there are no project-specific role files
        if not any(f.stem.endswith("_roles") and f.parent == Path(project_dir) for f in role_files):
            create_example_roles_file(project_dir)
    
    # If no role files found after creating example, return empty dict
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
