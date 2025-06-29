# Archives Directory

This directory contains historical development artifacts and documentation from the mcp-task-orchestrator project that have been organized and preserved for reference.

## Directory Structure

### `development-scripts/`
Contains one-off scripts, debugging tools, and experimental code that were created during development but are no longer needed in the main codebase:

- **Database fix scripts** - `fix_db_schema.py`, `fix_orchestrator_db.py`
- **Migration utilities** - `run_automation_migration.py`, `run_db_migration.py`, `file_tracking_migration.py`
- **Testing experiments** - Various pytest investigation and debugging scripts
- **Import debugging** - Scripts used to resolve import issues during development
- **Legacy installers** - Deprecated installation scripts

### `analysis-reports/`
Contains analysis documents and reports generated during development:

- **Git change analysis** - Documentation of repository changes and updates
- **Execution flow analysis** - Performance and timing analysis documents
- **Task cleanup reports** - JSON and markdown reports from cleanup operations

### `historical-docs/`
Contains documentation that was relevant for specific development phases:

- **Enhancement summaries** - Feature development documentation
- **Version planning** - Version progression and planning documents  
- **Pull request documentation** - Historical PR documentation

## Purpose

These archives serve several important purposes:

1. **Historical Reference** - Preserve development decisions and approaches
2. **Learning Resource** - Future developers can understand past solutions
3. **Recovery Option** - Scripts and tools can be restored if needed
4. **Clean Workspace** - Keep main repository clean while preserving work

## Usage Guidelines

- **View Only** - These files are for reference and should not be modified
- **Copy if Needed** - Copy files to active directories if you need to adapt them
- **Document Dependencies** - If using archived scripts, ensure dependencies still exist

## Maintenance

This directory should be periodically reviewed to:
- Remove truly obsolete content
- Update documentation if needed
- Reorganize if the structure becomes unwieldy

**Archive Created**: June 2, 2025
**Last Cleanup**: June 2, 2025
