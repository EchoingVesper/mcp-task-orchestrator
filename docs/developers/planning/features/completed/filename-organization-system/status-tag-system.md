---
feature_id: "STATUS_TAG_SYSTEM"
version: "1.0.0"
status: "Completed"
priority: "High"
category: "Foundation"
dependencies: ["FILENAME_ORGANIZATION_SYSTEM"]
size_lines: 225
last_updated: "2025-07-08"
validation_status: "pending"
cross_references:
  - "docs/developers/planning/features/completed/filename-organization-system/README.md"
  - "docs/developers/planning/features/completed/filename-organization-system/priority-matrix.md"
module_type: "specification"
modularized_from: "docs/developers/planning/features/completed/[COMPLETED]_filename_key_and_organization_system.md"
---

# 🏷️ Status Tag System

Comprehensive specification for document status tags and lifecycle management.

#
# Primary Status Tags

Status tags indicate the current phase of a document's lifecycle:

| Tag | Description | Use Cases | Color Code |
|-----|-------------|-----------|------------|
| **[RESEARCH]** | Analysis and investigation phase | Requirements gathering, feasibility studies, current state analysis | 🔵 Blue |
| **[APPROVED]** | Ready for implementation | Completed specifications, approved designs, validated requirements | 🟢 Green |
| **[IN-PROGRESS]** | Currently being worked on | Active development, ongoing documentation, implementation phase | 🟡 Yellow |
| **[TESTING]** | Implementation complete, testing phase | Verification, validation, quality assurance | 🟣 Purple |
| **[COMPLETED]** | Fully implemented and validated | well-tested, documented features, finished components | ✅ Green Check |
| **[ARCHIVED]** | Deprecated or cancelled | Obsolete features, cancelled projects, superseded documents | ⚫ Gray |
| **[BLOCKED]** | Waiting on dependencies | Pending external input, blocked by other work, resource constraints | 🔴 Red |

#
# Secondary Status Tags (Optional)

Additional context for specific situations:

| Tag | Description | Use Cases |
|-----|-------------|-----------||
| **[HIGH-PRIORITY]** | Urgent implementation needed | Critical fixes, blocking issues, time-sensitive features |
| **[LOW-PRIORITY]** | Future consideration | Nice-to-have features, optimization, long-term improvements |
| **[EXPERIMENTAL]** | Proof of concept | Research spikes, experimental features, early prototypes |
| **[DEPRECATED]** | Being phased out | Legacy systems, outdated approaches, migration targets |
| **[SECURITY]** | Security-related content | Security fixes, threat analysis, compliance requirements |
| **[BREAKING]** | Contains breaking changes | API changes, schema migrations, compatibility issues |

#
# File Naming Convention

#
## Standard Format

```text
[PRIMARY_STATUS]_descriptive_file_name.md
[PRIMARY_STATUS]_[SECONDARY_STATUS]_descriptive_file_name.md

```text

#
## Examples

```text
text
✅ Good Examples:
[RESEARCH]_enhanced_session_management_architecture.md
[APPROVED]_database_schema_enhancements.md
[IN-PROGRESS]_mcp_tools_implementation.md
[COMPLETED]_installation_guide_update.md
[BLOCKED]_[HIGH-PRIORITY]_github_integration_fix.md
[TESTING]_bidirectional_persistence_system.md
[ARCHIVED]_legacy_task_management_approach.md

❌ Bad Examples:
enhanced_session_management.md (no status tag)
[research]_session_management.md (lowercase tag)
[IN-PROGRESS][HIGH-PRIORITY]_feature.md (no separation)
very_long_descriptive_filename_that_exceeds_reasonable_length.md (too long)

```text

#
## Filename Requirements

1. **Status Tag**: Must be the first element in square brackets

2. **Descriptive Name**: Clear, concise description using underscores

3. **Length Limit**: Maximum 80 characters total filename

4. **Case Convention**: Status tags in UPPERCASE, filenames in lowercase_with_underscores

5. **Extension**: `.md` for documentation files

#
# Status Progression Flow

```text
mermaid
graph TD
    A[RESEARCH] --> B[APPROVED]
    B --> C[IN-PROGRESS]
    C --> D[TESTING]
    D --> E[COMPLETED]
    
    A --> F[ARCHIVED]
    B --> F
    C --> F
    D --> F
    
    A --> G[BLOCKED]
    B --> G
    C --> G
    D --> G
    
    G --> A
    G --> B
    G --> C
    G --> D
```text

#
## Normal Progression

1. **[RESEARCH]** → **[APPROVED]** → **[IN-PROGRESS]** → **[TESTING]** → **[COMPLETED]**

#
## Alternative Paths

- Any status → **[ARCHIVED]** (cancellation or obsolescence)

- Any status → **[BLOCKED]** (waiting on dependencies)

- **[BLOCKED]** → Previous status (when unblocked)

#
## Status Transition Rules

#
### From [RESEARCH]

- ✅ **To [APPROVED]**: When specifications are complete and validated

- ✅ **To [ARCHIVED]**: When research concludes feature is not viable

- ✅ **To [BLOCKED]**: When research requires external dependencies

#
### From [APPROVED]

- ✅ **To [IN-PROGRESS]**: When implementation begins

- ✅ **To [ARCHIVED]**: When priorities change or feature is cancelled

- ✅ **To [BLOCKED]**: When implementation dependencies are not met

#
### From [IN-PROGRESS]

- ✅ **To [TESTING]**: When implementation is complete

- ✅ **To [APPROVED]**: When scope changes require re-approval

- ✅ **To [BLOCKED]**: When implementation encounters blockers

- ✅ **To [ARCHIVED]**: When work is abandoned

#
### From [TESTING]

- ✅ **To [COMPLETED]**: When all tests pass and validation is complete

- ✅ **To [IN-PROGRESS]**: When significant issues require rework

- ✅ **To [BLOCKED]**: When testing reveals dependency issues

#
### From [COMPLETED]

- ✅ **To [ARCHIVED]**: When feature becomes obsolete

- ⚠️ **To [IN-PROGRESS]**: Only for major revisions (discouraged)

#
# Tag Usage Guidelines

#
## [RESEARCH] Guidelines

**Purpose**: Investigation and analysis phase

**Criteria for Use**:

- Gathering requirements or analyzing current state

- Feasibility studies or technology evaluation

- Problem definition and solution exploration

- Initial design concepts and approaches

**Required Content**:

- Problem statement or investigation scope

- Current state analysis (if applicable)

- Research findings and conclusions

- Recommendations for next steps

**Exit Criteria**:

- Clear understanding of requirements

- Viable solution approach identified

- Stakeholder alignment on direction

- Ready for detailed specification

#
## [APPROVED] Guidelines

**Purpose**: Ready for implementation

**Criteria for Use**:

- Complete specifications or designs

- Stakeholder review and approval complete

- Dependencies identified and available

- Resource allocation confirmed

**Required Content**:

- Detailed specifications or requirements

- Implementation approach defined

- Acceptance criteria established

- Risk assessment completed

**Exit Criteria**:

- Implementation resources available

- All dependencies resolved

- Implementation can begin immediately

#
## [IN-PROGRESS] Guidelines

**Purpose**: Active development or documentation

**Criteria for Use**:

- Work has actively begun

- Regular progress is being made

- Team member assigned and working

- Intermediate deliverables being produced

**Required Content**:

- Current progress status

- Work completed and remaining

- Any issues or blockers encountered

- Expected completion timeline

**Exit Criteria**:

- Implementation is functionally complete

- Ready for testing and validation

- Documentation is current and complete

#
## [TESTING] Guidelines

**Purpose**: Validation and quality assurance

**Criteria for Use**:

- Implementation is functionally complete

- Testing plan is defined and being executed

- Quality assurance activities underway

- User acceptance testing in progress

**Required Content**:

- Testing plan and test cases

- Test results and coverage metrics

- Known issues and their status

- Validation criteria and progress

**Exit Criteria**:

- All critical tests passing

- User acceptance criteria met

- Performance requirements satisfied

- Documentation is complete and accurate

#
## [COMPLETED] Guidelines

**Purpose**: Fully implemented and validated

**Criteria for Use**:

- All testing and validation complete

- Feature is deployed and operational

- Documentation is complete and current

- Stakeholder sign-off received

**Required Content**:

- Final implementation summary

- Test results and validation evidence

- Usage instructions and documentation

- Lessons learned and recommendations

**Maintenance**:

- Monitor for issues or enhancement requests

- Update documentation as needed

- Plan for eventual archival when obsolete

#
## [BLOCKED] Guidelines

**Purpose**: Waiting on external dependencies

**Criteria for Use**:

- Work cannot proceed due to external factors

- Dependencies are clearly identified

- Blocking issues are documented

- Resolution timeline is uncertain

**Required Content**:

- Clear description of blocking issues

- Dependencies that must be resolved

- Impact on timeline and deliverables

- Alternative approaches considered

**Resolution Process**:

- Regular review of blocking conditions

- Escalation when appropriate

- Communication with stakeholders

- Transition back to appropriate status when unblocked

#
## [ARCHIVED] Guidelines

**Purpose**: No longer active or relevant

**Criteria for Use**:

- Feature has been cancelled or superseded

- Technology or approach is obsolete

- Project priorities have changed

- Legal or business requirements have changed

**Required Content**:

- Reason for archival

- Historical context and decisions

- References to replacement solutions

- Lessons learned for future reference

**Archive Process**:

- Document reason for archival

- Update any references in other documents

- Move to archived directory structure

- Maintain for historical reference

This status tag system provides clear, consistent communication about document states while supporting efficient project management and development workflows.
