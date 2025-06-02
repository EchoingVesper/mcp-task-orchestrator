#!/usr/bin/env python3
"""Migration script to fix artifacts data validation issues."""

import sqlite3
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("artifacts_migration")

class ArtifactsMigrator:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.backup_path = self.db_path.with_suffix('.bak')
        
    def create_backup(self) -> bool:
        try:
            if self.backup_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.backup_path = self.db_path.with_suffix(f'.bak_{timestamp}')
            
            shutil.copy2(self.db_path, self.backup_path)
            logger.info(f"Created database backup: {self.backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            return False
    
    def sanitize_artifacts(self, artifacts_data: Any) -> List[str]:
        if artifacts_data is None:
            return []
        
        if isinstance(artifacts_data, list):
            return [str(item) for item in artifacts_data if item is not None]
        
        if isinstance(artifacts_data, str):
            if not artifacts_data.strip():
                return []
            
            try:
                parsed = json.loads(artifacts_data)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed if item is not None]
                else:
                    return [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                if '\n' in artifacts_data:
                    lines = [line.strip() for line in artifacts_data.split('\n') if line.strip()]
                    return lines
                else:
                    return [artifacts_data]
        
        return [str(artifacts_data)]
    
    def identify_problematic_records(self) -> List[Tuple[str, str, str]]:
        problematic_records = []
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT task_id, parent_task_id, artifacts
                FROM subtasks 
                WHERE artifacts IS NOT NULL 
                AND artifacts != ''
                AND artifacts NOT LIKE '[%]'
                ORDER BY parent_task_id, task_id
            """)
            
            for row in cursor.fetchall():
                task_id, parent_task_id, artifacts = row
                try:
                    parsed = json.loads(artifacts)
                    if not isinstance(parsed, list):
                        problematic_records.append((task_id, parent_task_id, artifacts))
                except (json.JSONDecodeError, TypeError):
                    problematic_records.append((task_id, parent_task_id, artifacts))
        finally:
            conn.close()
        return problematic_records
    
    def migrate_records(self, problematic_records: List[Tuple[str, str, str]]) -> Tuple[int, int]:
        success_count = 0
        failure_count = 0
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            for task_id, parent_task_id, old_artifacts in problematic_records:
                try:
                    new_artifacts = self.sanitize_artifacts(old_artifacts)
                    new_artifacts_json = json.dumps(new_artifacts)
                    cursor.execute("UPDATE subtasks SET artifacts = ? WHERE task_id = ?", 
                                 (new_artifacts_json, task_id))
                    logger.info(f"Migrated {task_id}: {old_artifacts!r} -> {new_artifacts!r}")
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to migrate {task_id}: {str(e)}")
                    failure_count += 1
            conn.commit()
            logger.info(f"Migration committed: {success_count} successful, {failure_count} failed")
        except Exception as e:
            conn.rollback()
            logger.error(f"Migration failed, changes rolled back: {str(e)}")
            raise
        finally:
            conn.close()
        return success_count, failure_count
    
    def run_migration(self) -> bool:
        logger.info("Starting artifacts migration process")
        if not self.create_backup():
            logger.error("Failed to create backup, aborting migration")
            return False
        
        try:
            logger.info("Identifying problematic records...")
            problematic_records = self.identify_problematic_records()
            
            if not problematic_records:
                logger.info("No problematic records found, migration not needed")
                return True
            
            logger.info(f"Found {len(problematic_records)} problematic records")
            success_count, failure_count = self.migrate_records(problematic_records)
            logger.info(f"Migration completed: {success_count} records migrated")
            return True
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            return False

def main():
    db_path = Path(__file__).parent / "task_orchestrator.db"
    if not db_path.exists():
        logger.error(f"Database file not found: {db_path}")
        return False
    
    logger.info(f"Running artifacts migration on: {db_path}")
    migrator = ArtifactsMigrator(str(db_path))
    return migrator.run_migration()

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
