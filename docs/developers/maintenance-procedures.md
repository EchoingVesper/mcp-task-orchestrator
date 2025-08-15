# Maintenance Procedures

This document outlines the ongoing maintenance procedures for the MCP Task Orchestrator project, implemented as part of the Documentation Ecosystem Modernization (Phase 4).

## Overview

The project implements automated lifecycle management to maintain a clean, organized structure and prevent documentation drift. These procedures ensure the project remains maintainable and follows best practices.

## Daily Operations

### Automated Systems
The following systems run automatically:
- **Claude Code Hooks**: Check for temporary file accumulation after commands
- **Cleanup Reminders**: Alert when cleanup is needed
- **Status Tag Validation**: Ensure proper lifecycle tagging

### Manual Checks (Optional)
Contributors can run these commands for immediate feedback:

```bash
# Check for temporary files needing cleanup
python scripts/lifecycle/automated_cleanup_manager.py --dry-run

# Validate current project structure
find . -maxdepth 1 -name "fix_*.py" -o -name "system_health*.json" -o -name "test_*.sh"
```

## Weekly Maintenance

### Automated Cleanup
Run the automated cleanup manager weekly:

```bash
# Dry run to see what would be cleaned
python scripts/lifecycle/automated_cleanup_manager.py --dry-run

# Apply cleanup if satisfied with dry run results  
python scripts/lifecycle/automated_cleanup_manager.py

# Update .gitignore patterns if needed
python scripts/lifecycle/automated_cleanup_manager.py --update-gitignore

# Generate cleanup report
python scripts/lifecycle/automated_cleanup_manager.py --report cleanup_report_$(date +%Y%m%d).json
```

### Manual Review Tasks
1. **Review Temporary Directory**: Check `scripts/testing/temporary/` for files older than 7 days
2. **Archive Management**: Review `docs/archives/test-artifacts/` for oversized accumulation
3. **Root Directory Scan**: Ensure no temporary files persist in project root

## Monthly Maintenance

### Archive Organization Review

```bash
# Check test artifacts retention
find docs/archives/test-artifacts -name "*.json" -mtime +90

# Review migration reports completeness  
ls -la docs/archives/migration-reports/

# Audit historical archives organization
find docs/archives/historical -type f | wc -l
```

### System Health Checks
- Review cleanup manager logs
- Validate hook system functionality
- Check for broken links in archive documentation
- Assess retention policy effectiveness

### Documentation Updates
- Update retention policies if project needs change
- Review and update maintenance procedures
- Update archive documentation for new categories

## Quarterly Maintenance

### Deep Archive Management

1. **Apply Retention Policies**:
```bash
python scripts/lifecycle/automated_cleanup_manager.py --apply-retention --dry-run
python scripts/lifecycle/automated_cleanup_manager.py --apply-retention
```

2. **Archive Completed Planning Documents**:
```bash
# Move completed planning to archives
git mv docs/planning/completed/* docs/archives/historical/planning/completed/
```

3. **Update Archive Structure**:
   - Review archive categories for new needs
   - Reorganize by-date directories if needed
   - Compress large historical backups

### System Assessment
- Review cleanup automation effectiveness
- Analyze temporal patterns in file accumulation
- Update retention policies based on project evolution
- Assess hook system performance impact

## Annual Maintenance  

### Archive Lifecycle Management

1. **Archive Aging Review**:
```bash
# Find archives older than 2 years
find docs/archives -type f -mtime +730

# Review for historical significance vs storage cost
```

2. **Compress Historical Data**:
```bash
# Create compressed archives of old data
tar -czf archives_backup_$(date +%Y).tar.gz docs/archives/historical/by-date/2023/
```

3. **Update Procedures**:
   - Review this document for accuracy
   - Update based on lessons learned
   - Incorporate new tools or practices

### Strategic Review
- Assess overall documentation ecosystem health
- Review maintenance automation return on investment
- Plan improvements to lifecycle management
- Update integration with development workflow

## Emergency Procedures

### Cleanup System Failure
If automated cleanup fails:

1. **Manual Root Directory Cleanup**:
```bash
mkdir -p scripts/testing/temporary
mv fix_*.py system_health*.json test-*hooks*.sh scripts/testing/temporary/
mv *_test_report_*.json validation_*.json docs/archives/test-artifacts/
```

2. **Restore Hook System**:
```bash
chmod +x .claude/hooks/*.sh
# Verify hook configuration in .claude/config.json
```

3. **Emergency Archive Creation**:
```bash
mkdir -p docs/archives/emergency/$(date +%Y%m%d)
mv [problematic files] docs/archives/emergency/$(date +%Y%m%d)/
```

### Repository Corruption
If repository structure becomes corrupted:

1. Check git integrity: `git fsck`
2. Restore from last known good state
3. Apply emergency cleanup procedures
4. Rebuild archive structure from backups

## Monitoring and Alerts

### Key Metrics to Monitor
- Number of temporary files in root directory
- Age of oldest temporary file
- Size of test-artifacts directory  
- Frequency of cleanup reminders
- Hook system execution success rate

### Alert Thresholds
- **Info**: 5+ temporary files or 7+ days old
- **Warning**: 10+ temporary files or 14+ days old  
- **Critical**: 20+ temporary files or 30+ days old

### Escalation Procedures
1. **Info**: Claude Code hooks provide gentle reminders
2. **Warning**: More prominent cleanup recommendations
3. **Critical**: Block development workflow until addressed

## Integration Points

### Git Workflow
- All cleanup operations preserve git history
- Cleanup commits follow project commit message conventions
- Branch protection ensures cleanup doesn't break builds

### Claude Code Integration
- Hooks provide real-time feedback
- Cleanup suggestions integrate with development workflow
- Session restoration accounts for moved files

### Orchestrator Integration
- Cleanup operations can be orchestrated as tasks
- Progress tracking for large cleanup operations
- Integration with project maintenance schedules

## Success Metrics

### Quantitative Metrics
- Days between manual cleanup interventions
- Number of accumulated temporary files (target: <5)
- Archive query response time
- Hook system execution overhead

### Qualitative Metrics
- Developer satisfaction with clean workspace
- Reduced time spent searching for files
- Improved onboarding experience
- Maintainer confidence in project structure

## Continuous Improvement

### Feedback Collection
- Monitor hook system alerts and responses
- Collect feedback on cleanup automation effectiveness
- Track patterns in temporary file creation

### Process Evolution
- Adapt retention policies based on usage patterns
- Evolve cleanup automation based on identified needs
- Integrate new tools and practices as they emerge

### Documentation Maintenance
- Keep this document updated with actual practices
- Document lessons learned from cleanup operations
- Maintain examples and troubleshooting guides

---

**Last Updated**: 2025-08-13 (Phase 4 Documentation Ecosystem Modernization)  
**Next Review**: 2025-11-13 (Quarterly)  
**Responsible**: Project Maintainers