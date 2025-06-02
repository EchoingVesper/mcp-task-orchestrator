#!/usr/bin/env python3
"""Cleanup utility for removing obsolete files."""

import shutil
from pathlib import Path
from typing import List


class ProjectCleanup:
    """Utility for cleaning up obsolete files and directories."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
        # Files and directories to remove (obsolete installation attempts)
        self.obsolete_items = [
            "install_bundled.py",
            "install_bundled_venv.py", 
            "install_for_claude.py",
            "install_system_python.bat",
            "install_bundled.bat",
            "install_bundled.ps1",
            "create_claude_config.bat",
            "fix_claude_config.py",
            "test_embedded_python.py",
            "BUNDLED_README.md",
            "bundled",  # directory
            "temp_calculator_project"  # directory
        ]
    
    def cleanup_obsolete_files(self) -> List[str]:
        """Remove obsolete files and return list of removed items."""
        removed = []
        
        for item_name in self.obsolete_items:
            item_path = self.project_root / item_name
            if item_path.exists():
                try:
                    if item_path.is_dir():
                        shutil.rmtree(item_path)
                        removed.append(f"DIR:  {item_name}/")
                    else:
                        item_path.unlink()
                        removed.append(f"FILE: {item_name}")
                except Exception as e:
                    print(f"Warning: Could not remove {item_name}: {e}")
        
        return removed
    
    def run_cleanup(self) -> bool:
        """Run the cleanup process."""
        print("Cleaning up obsolete files...")
        
        removed = self.cleanup_obsolete_files()
        
        if removed:
            print(f"Removed {len(removed)} obsolete items:")
            for item in removed:
                print(f"  - {item}")
        else:
            print("No obsolete files found")
        
        return True

def main():
    """Run cleanup as standalone script."""
    project_root = Path(__file__).parent.parent
    cleanup = ProjectCleanup(project_root)
    cleanup.run_cleanup()


if __name__ == "__main__":
    main()
