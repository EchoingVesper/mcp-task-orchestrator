# 📚 Documentation Changes Pull Request

<!-- 
This template is for pull requests that include documentation changes.
Please fill out all relevant sections to help with review and quality validation.
-->

## 📋 Change Summary

**Type of Documentation Change:**
<!-- Select all that apply -->
- [ ] New documentation (adding missing content)
- [ ] Update existing documentation (fixing outdated information)
- [ ] Template compliance improvement (status tags, formatting)
- [ ] Organization improvement (better structure, Japanese standards)
- [ ] Quality automation fix (markdownlint, Vale issues)
- [ ] Lifecycle management (archiving, cleanup)
- [ ] Translation or internationalization

**Files Changed:**
<!-- List the main files being changed -->
- 
- 
- 

## 🗾 Japanese Development Standards Compliance

**Primary Japanese Standard Addressed:**
<!-- Select the main principle this PR supports -->
- [ ] 整理整頓 (Seiriseiton) - Organization and cleanliness
- [ ] 体系的アプローチ (Systematic Approach) - Systematic methodology
- [ ] ライフサイクル管理 (Lifecycle Management) - Proper maintenance
- [ ] 丁寧な保守 (Respectful Maintenance) - Careful upkeep  
- [ ] 全体的品質 (Holistic Quality) - Overall quality improvement

**Compliance Checklist:**
- [ ] Status tags used correctly (e.g., `[IN-PROGRESS]`, `[DRAFT]`, `[COMPLETED]`)
- [ ] Proper heading hierarchy (H1 → H2 → H3, no skipping)
- [ ] Files placed in appropriate directories
- [ ] Consistent naming conventions followed
- [ ] Archive organization maintained (old files properly archived)

## 📊 Quality Gates Preparation

**Quality Validation Checklist:**
- [ ] Markdownlint validation passes (`markdownlint-cli2 "docs/**/*.md" "*.md"`)
- [ ] Vale prose quality check passes (if configured)
- [ ] Template compliance verified (required sections present)
- [ ] Internal links tested and working
- [ ] Code examples tested (if applicable)
- [ ] Screenshots updated (if applicable)

**Expected CI/CD Results:**
- [ ] Documentation Quality Gates workflow should pass
- [ ] Documentation Lifecycle Management validation should pass
- [ ] Japanese Standards validation should pass
- [ ] Template compliance validation should pass

## 🎯 Detailed Changes

### What was changed and why?
<!-- Provide a clear description of what documentation was changed and the reasoning -->

### How does this improve the user experience?
<!-- Explain how these changes help users or contributors -->

### Are there any breaking changes?
<!-- List any changes that might break existing links or workflows -->
- [ ] No breaking changes
- [ ] Links or references updated (list below)
- [ ] Workflow or process changes (describe below)

**If breaking changes exist, describe them:**


## 🔍 Review Guidance

### Areas needing special attention:
<!-- Help reviewers focus on the most important aspects -->
- 
- 
- 

### Testing instructions:
<!-- How should reviewers test these documentation changes? -->
1. 
2. 
3. 

### Related issues or PRs:
<!-- Link to related issues or PRs -->
- Closes #
- Related to #
- Follows up on #

## 🚀 Post-Merge Actions

**Actions needed after merge:**
- [ ] Update related documentation
- [ ] Notify relevant teams or users
- [ ] Update external references or links
- [ ] Archive old documentation (if applicable)
- [ ] Schedule follow-up improvements

**Follow-up tasks:**
<!-- List any follow-up work that should be done -->
- 
- 

---

## 🤖 Automated Quality Gates

This PR will be automatically validated against:

### Documentation Quality Pipeline:
1. **Markdownlint**: Formatting and structure validation
2. **Vale**: Prose quality and style checking
3. **Template Compliance**: Status tags and structure validation  
4. **Japanese Standards**: Organizational principle compliance
5. **Link Validation**: Working link verification
6. **Content Freshness**: Update recency validation

### Integration Workflows:
- **Documentation Lifecycle Management**: Comprehensive quality gates
- **Project Cleanliness Validation**: Organization and structure
- **Claude Code Review**: AI-powered documentation review

### Expected Artifacts:
- Documentation quality reports
- Template compliance validation results
- Japanese standards compliance scoring
- Link validation results

---

## 📝 Reviewer Checklist

**For Reviewers:**
- [ ] Content is accurate and helpful
- [ ] Writing style is clear and professional
- [ ] Japanese development standards are followed
- [ ] Template compliance is maintained
- [ ] Links and references work correctly
- [ ] Code examples are tested and working
- [ ] Screenshots are current and helpful
- [ ] Changes don't break existing workflows
- [ ] Quality gates are expected to pass

**Documentation Review Priorities:**
1. **Accuracy**: Information is correct and up-to-date
2. **Clarity**: Content is easy to understand and follow  
3. **Completeness**: All necessary information is included
4. **Consistency**: Follows project patterns and standards
5. **Japanese Standards**: Maintains organizational principles

---

<!-- 
## 🔗 Useful Commands for Local Testing

```bash
# Test markdownlint compliance
markdownlint-cli2 "docs/**/*.md" "*.md"

# Run quality automation
python scripts/quality_automation.py --check all

# Validate template compliance
python -c "
from pathlib import Path
prps = list(Path('PRPs').glob('**/*.md'))
tagged = [f for f in prps if any(tag in f.name for tag in ['[IN-PROGRESS]', '[DRAFT]', '[COMPLETED]'])]
print(f'Status tag compliance: {len(tagged)}/{len(prps)} ({len(tagged)/max(len(prps),1):.1%})')
"
```
-->