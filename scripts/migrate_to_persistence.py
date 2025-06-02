#!/usr/bin/env python3
"""
Migration utility for MCP Task Orchestrator.

This script migrates existing configuration files to the new .task_orchestrator
directory structure introduced in version 1.3.0.
"""

import os
import sys
import shutil
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("migration_utility")

def setup_persistence_directory(base_dir: Path) -> Path:
    """Set up the .task_orchestrator directory structure.
    
    Args:
        base_dir: Base directory for the project
        
    Returns:
        Path to the .task_orchestrator directory
    """
    persistence_dir = base_dir / ".task_orchestrator"
    
    # Create main directories
    persistence_dir.mkdir(exist_ok=True)
    (persistence_dir / "roles").mkdir(exist_ok=True)
    (persistence_dir / "tasks").mkdir(exist_ok=True)
    (persistence_dir / "tasks" / "active").mkdir(exist_ok=True)
    (persistence_dir / "tasks" / "archive").mkdir(exist_ok=True)
    (persistence_dir / "locks").mkdir(exist_ok=True)
    (persistence_dir / "logs").mkdir(exist_ok=True)
    
    logger.info(f"Created persistence directory structure at {persistence_dir}")
    return persistence_dir

def migrate_config_files(base_dir: Path, persistence_dir: Path) -> None:
    """Migrate configuration files to the .task_orchestrator directory.
    
    Args:
        base_dir: Base directory for the project
        persistence_dir: Path to the .task_orchestrator directory
    """
    # Source paths
    config_dir = base_dir / "config"
    specialists_file = config_dir / "specialists.yaml"
    templates_dir = config_dir / "templates"
    
    # Target paths
    roles_dir = persistence_dir / "roles"
    default_roles_file = roles_dir / "default_roles.yaml"
    persistence_templates_dir = roles_dir / "templates"
    
    # Migrate specialists.yaml
    if specialists_file.exists() and not default_roles_file.exists():
        shutil.copy(specialists_file, default_roles_file)
        logger.info(f"Migrated {specialists_file} to {default_roles_file}")
    
    # Migrate templates
    if templates_dir.exists():
        persistence_templates_dir.mkdir(exist_ok=True)
        
        # Copy all template files
        for template_file in templates_dir.glob("*"):
            target_file = persistence_templates_dir / template_file.name
            if not target_file.exists():
                shutil.copy(template_file, target_file)
                logger.info(f"Migrated template {template_file} to {target_file}")
    
    logger.info("Configuration migration completed")

def main():
    """Main entry point for the migration utility."""
    parser = argparse.ArgumentParser(
        description="Migrate MCP Task Orchestrator configuration to the new persistence structure"
    )
    parser.add_argument(
        "--base-dir", 
        help="Base directory for the MCP Task Orchestrator project",
        default=None
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force migration even if target files already exist"
    )
    
    args = parser.parse_args()
    
    # Determine base directory
    if args.base_dir:
        base_dir = Path(args.base_dir)
    else:
        # Try to find the base directory
        current_dir = Path.cwd()
        
        # Check if we're in the project directory
        if (current_dir / "mcp_task_orchestrator").exists():
            base_dir = current_dir
        else:
            # Check if we're in the scripts directory
            if current_dir.name == "scripts" and (current_dir.parent / "mcp_task_orchestrator").exists():
                base_dir = current_dir.parent
            else:
                logger.error("Could not determine project base directory. Please specify with --base-dir.")
                sys.exit(1)
    
    logger.info(f"Using base directory: {base_dir}")
    
    # Set up the persistence directory
    persistence_dir = setup_persistence_directory(base_dir)
    
    # Migrate configuration files
    migrate_config_files(base_dir, persistence_dir)
    
    logger.info("Migration completed successfully")

if __name__ == "__main__":
    main()
