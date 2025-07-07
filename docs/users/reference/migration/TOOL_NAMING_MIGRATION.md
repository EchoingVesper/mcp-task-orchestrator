

# Tool Naming Migration Guide

*Practical guide for transitioning to improved tool names*

#

# Quick Reference: Old vs New Names

| Current Name | Proposed Name | Status | Change Type |
|-------------|---------------|--------|-------------|
| `orchestrator_initialize_session` | `orchestrator_start_workflow` | **Recommended** | High Impact |
| `orchestrator_maintenance_coordinator` | `orchestrator_maintain_system` | **Recommended** | High Impact |
| `orchestrator_get_status` | `orchestrator_check_status` | Suggested | Medium Impact |
| `orchestrator_plan_task` | `orchestrator_create_plan` | Optional | Low Impact |
| `orchestrator_execute_subtask` | `orchestrator_run_subtask` | Optional | Low Impact |
| `orchestrator_complete_subtask` | *(no change)* | - | Already optimal |
| `orchestrator_synthesize_results` | *(no change)* | - | Already optimal |

#

# Rationale for Changes

#

## Primary Changes (Recommended)

#

### `orchestrator_initialize_session` → `orchestrator_start_workflow`

- **27 → 24 characters** (shorter, easier to type)

- **More intuitive**: "start" is more natural than "initialize"

- **Better semantics**: Reflects workflow creation, not just session setup

- **User-friendly**: Matches common application patterns

#

### `orchestrator_maintenance_coordinator` → `orchestrator_maintain_system`

- **32 → 25 characters** (significantly shorter)

- **Action-oriented**: "maintain" is a clear, direct verb

- **Simplified**: Removes unnecessary "coordinator" complexity

- **Purpose-focused**: Directly states what users want to accomplish

#

### `orchestrator_get_status` → `orchestrator_check_status`

- **More conversational**: "check" vs "get" feels more natural

- **Consistent pattern**: Aligns with action-oriented naming

- **Minimal impact**: Only 1 character longer but more intuitive

#

# Implementation Approach

#

## Phase 1: Dual Support (Months 1-6)

Both old and new names work simultaneously:

```json
// Both of these work:
{"tool": "orchestrator_start_workflow"}
{"tool": "orchestrator_initialize_session"}  // Deprecated but functional

```text

#

## Phase 2: Deprecation Warnings (Months 4-6)

Old names return warnings but still function:

```text
json
{
  "result": "...",
  "deprecation_warning": "Tool 'orchestrator_initialize_session' is deprecated. Use 'orchestrator_start_workflow' instead."
}

```text

#

## Phase 3: Legacy Removal (Month 7+)

Old names removed from system.

#

# Migration for Users

#

## For Regular Users

**No immediate action required** - old names continue working during transition period.

**Recommended actions:**

1. **Update your commands** to use new names when convenient

2. **Update any saved scripts** or documentation

3. **Learn new names** through regular usage

#

## For Documentation

**Content creators should:**

1. **Use new names** in all new documentation

2. **Update examples** to show new naming

3. **Include migration notes** where appropriate

4. **Provide both versions** during transition period

#

## For Integration Developers

**API users should:**

1. **Test with new names** during dual support phase

2. **Update integrations** gradually

3. **Plan for legacy removal** timeline

4. **Monitor deprecation warnings**

#

# User Experience Guide

#

## Before and After Examples

#

### Starting a Workflow

```text

Before: "Use orchestrator_initialize_session to begin"
After:  "Use orchestrator_start_workflow to begin"

```text

#

### System Maintenance

```text

Before: "Run orchestrator_maintenance_coordinator to clean up"
After:  "Run orchestrator_maintain_system to clean up"

```text

#

### Checking Progress

```text

Before: "Use orchestrator_get_status to see progress"
After:  "Use orchestrator_check_status to see progress"

```text

#

## Natural Language Examples

#

### More Intuitive Commands

```text

Old: "Initialize a new orchestration session"
New: "Start a new workflow"

Old: "Use the maintenance coordinator to scan the system"
New: "Maintain the system by scanning for issues"

Old: "Get the current status of tasks"
New: "Check the current status of tasks"
```text

#

# Benefits Summary

#

## For Users

- **Easier to remember** - More natural language patterns

- **Faster to type** - Shorter command names

- **Less confusion** - Clearer semantic meaning

- **Better workflow** - Names match user intentions

#

## For System

- **Improved discoverability** - Shorter names in tool lists

- **Better user adoption** - Lower learning curve

- **Professional polish** - Consistent, thoughtful naming

- **Future extensibility** - Clear naming patterns for new tools

#

# FAQ

#

## Q: Why change names that already work?

**A:** While the current names are functional, the improvements in user experience and system consistency provide significant long-term benefits. The changes make the tool more accessible to new users and more efficient for existing users.

#

## Q: Will my existing scripts break?

**A:** No. During the transition period (6+ months), both old and new names will work. You'll have plenty of time to update any scripts or integrations.

#

## Q: What if I prefer the old names?

**A:** The old names will continue working during the transition period. However, we encourage adopting the new names for consistency and to benefit from the improved user experience.

#

## Q: How will I know when to stop using old names?

**A:** The system will provide deprecation warnings when you use old names, and we'll communicate the removal timeline clearly through release notes and documentation.

#

## Q: Are there performance differences?

**A:** No. The underlying functionality is identical - only the names change. There's no performance impact from using new vs old names.

#

# Timeline

| Phase | Duration | Description | Action Required |
|-------|----------|-------------|-----------------|
| **Announcement** | Month 0 | New names announced | None - informational |
| **Dual Support** | Months 1-6 | Both names work | Optional: Start using new names |
| **Deprecation** | Months 4-6 | Warnings for old names | Recommended: Migrate to new names |
| **Legacy Removal** | Month 7+ | Old names removed | Required: Use new names only |

#

# Support and Resources

#

## Getting Help

- **Documentation**: This guide and the [Tool Naming Architecture](docs/architecture/tool-naming-conventions.md)

- **Community**: GitHub Issues for questions and feedback

- **Migration Support**: Dedicated support during transition period

#

## Feedback

We welcome feedback on the new naming conventions:

- **GitHub Issues**: For bugs or technical issues

- **Discussions**: For general feedback and suggestions

- **Documentation**: Improvements to this migration guide

---

*This migration represents a commitment to continuous improvement in user experience while maintaining system reliability and backward compatibility.*
