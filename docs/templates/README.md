
# Documentation Templates

Industry-standard templates for creating consistent, high-quality documentation across the MCP Task Orchestrator project.

#
# Overview

This directory contains comprehensive templates following industry best practices from Google's Technical Writing Guide, Write the Docs standards, and project-specific requirements. All templates include quality checklists, accessibility guidelines, and validation requirements.

#
# Template Organization

#
## Directory Structure

```text
docs/templates/
├── README.md                     
# This guide
├── style-guide.md               
# Comprehensive style and formatting standards
├── project-level/               
# Project governance and overview
│   ├── readme-template.md
│   ├── contributing-template.md
│   └── changelog-template.md
├── technical/                   
# System design and implementation
│   ├── architecture-template.md
│   ├── api-documentation-template.md
│   └── configuration-guide-template.md
├── development/                 
# Developer workflows and tools
│   ├── setup-guide-template.md
│   ├── workflow-template.md
│   └── testing-guide-template.md
├── user-facing/                 
# End-user guidance and support
│   ├── user-guide-template.md
│   ├── tutorial-template.md
│   └── troubleshooting-template.md
└── internal/                    
# Project-specific documentation
    ├── claude-command-template.md
    ├── process-documentation-template.md
    └── prp-template-enhancements.md

```text

#
## Current Templates

#
### CLAUDE.md Templates

- `CLAUDE-template.md` - Generic CLAUDE.md template for any directory

- `CLAUDE-core-package-template.md` - Core package implementation guide

- `CLAUDE-scripts-template.md` - Scripts and utilities guide

- `CLAUDE-testing-template.md` - Testing infrastructure guide

#
### PRP Templates

- `../PRPs/templates/prp_base.md` - Comprehensive PRP creation template

- `../PRPs/templates/prp_planning.md` - Planning and design PRP template

- `../PRPs/templates/prp_spec.md` - Specification PRP template

- `../PRPs/templates/prp_task.md` - Task-oriented PRP template

#
# Usage Guide

#
## Choosing the Right Template

#
### For Project Documentation

**Use project-level templates when creating:**

- Project README files

- Contribution guidelines

- Change logs and release notes

- Governance documents

#
### For Technical Documentation

**Use technical templates when creating:**

- System architecture documentation

- API reference documentation

- Configuration and setup guides

- Deployment and operations guides

#
### For Development Documentation

**Use development templates when creating:**

- Development environment setup

- Workflow and process documentation

- Testing strategies and guides

- Code style and standards

#
### For User Documentation

**Use user-facing templates when creating:**

- End-user guides and manuals

- Step-by-step tutorials

- Troubleshooting and support docs

- Frequently asked questions

#
### For Internal Documentation

**Use internal templates when creating:**

- CLAUDE.md directory guides

- PRP (Product Requirement Prompt) documents

- Internal process documentation

- Team-specific workflows

#
## Template Usage Process

#
### 1. Select Template

Choose the appropriate template based on your documentation type and audience:

```text
bash

# Copy template to your target location

cp docs/templates/user-facing/user-guide-template.md docs/users/guides/new-feature-guide.md

```text

#
### 2. Customize Content

Replace template placeholders with your specific content:

- Replace `{TITLE}` with your document title

- Replace `{DESCRIPTION}` with your content description

- Replace `{AUDIENCE}` with target audience

- Fill in all template sections with relevant information

#
### 3. Validate Quality

Run quality validation checks before publishing:

```text
bash

# Markdown syntax validation

markdownlint docs/users/guides/new-feature-guide.md

# Template compliance check

python scripts/validate_template_compliance.py --file docs/users/guides/new-feature-guide.md

# Link validation

markdown-link-check docs/users/guides/new-feature-guide.md

```text

#
### 4. Review and Publish

Follow the review process outlined in the style guide:

1. Self-review against quality checklist

2. Technical review for accuracy

3. Editorial review for clarity

4. Final approval and publication

#
# Quality Standards

#
## Required Elements

All templates include these mandatory sections:

#
### Header Information

```text
markdown

# Document Title

Brief description of purpose and scope

#
# Purpose

Clear statement of what this document accomplishes

#
# Audience

Who should use this document and what they should know

```text

#
### Quality Checklist

```text
markdown

## Quality Checklist

- [ ] Content is accurate and up-to-date

- [ ] All procedures tested and verified

- [ ] Code examples are functional

- [ ] Links are valid and functional

- [ ] Markdownlint validation passes

- [ ] Accessibility guidelines followed

- [ ] Cross-references are accurate

- [ ] Template compliance verified

```text

#
### Cross-References

```text
markdown

## Related Documentation

- [Related Guide](./related-guide.md) - Brief description

- [Reference Document](./reference.md) - Brief description

- [External Resource](https://example.com) - Brief description

```text

#
## Validation Requirements

All documentation created from templates must pass:

#
### Automated Validation

```text
bash

# Level 1: Syntax and Style

markdownlint **/*.md --config .markdownlint.json
vale **/*.md  
# When configured
cspell "**/*.md"

# Level 2: Content Validation

markdown-link-check **/*.md
python scripts/validate_template_compliance.py --directory docs/
python scripts/validate_cross_references.py --base-file CLAUDE.md

# Level 3: Quality Metrics

python scripts/calculate_doc_quality_metrics.py --output quality_report.json
python scripts/check_accessibility_compliance.py --directory docs/

```text

#
### Manual Review

- Technical accuracy verification

- User experience testing

- Editorial review for clarity

- Accessibility compliance check

#
# Template Features

#
## Industry Standards Compliance

All templates implement:

- **Google Technical Writing Standards**: Clear, concise, user-focused content

- **Write the Docs Best Practices**: Structured, maintainable documentation

- **Web Accessibility Guidelines**: Screen reader compatible, proper heading hierarchy

- **Markdown Best Practices**: Consistent formatting, link validation, code block languages

#
## Accessibility Features

- Proper heading hierarchy (H1 → H2 → H3)

- Descriptive link text

- Alt text placeholders for images

- Screen reader compatibility

- Logical content flow

#
## Template Consistency

- Standardized section ordering

- Consistent cross-reference patterns

- Uniform quality validation

- Shared terminology and conventions

#
## Maintenance Support

- Version tracking and change logs

- Update procedures and schedules

- Quality validation automation

- Cross-reference integrity checking

#
# Creating New Templates

#
## Template Creation Process

#
### 1. Identify Need

Document the gap in current template coverage:

- What type of documentation is missing?

- Who is the target audience?

- What specific requirements exist?

- How does it relate to existing templates?

#
### 2. Research Standards

Gather industry standards and examples:

- Research similar documentation in other projects

- Review industry style guides and best practices

- Analyze user needs and workflow patterns

- Identify accessibility and compliance requirements

#
### 3. Design Template Structure

Create template outline based on:

- Target audience needs and workflows

- Content organization best practices

- Quality validation requirements

- Integration with existing documentation

#
### 4. Implement and Test

Develop the template with:

- All required sections and elements

- Comprehensive quality checklist

- Cross-reference patterns

- Validation and compliance checks

#
### 5. Validate and Refine

Test template with:

- Real-world usage scenarios

- Multiple content creators

- Quality validation tools

- User feedback and iteration

#
## Template Contribution Guidelines

#
### Requirements

New templates must include:

- **Purpose Statement**: Clear description of when to use this template

- **Audience Definition**: Target users and their needs

- **Required Sections**: All mandatory content areas

- **Quality Checklist**: Comprehensive validation requirements

- **Cross-References**: Integration with existing documentation

- **Usage Examples**: Practical implementation guidance

#
### Review Process

1. **Initial Review**: Template structure and completeness

2. **Standards Review**: Compliance with style guide and accessibility

3. **Usage Testing**: Real-world application and usability

4. **Integration Review**: Cross-reference accuracy and system integration

5. **Final Approval**: Quality validation and publication

#
# Tools and Resources

#
## Validation Tools

```text
bash

# Markdown linting

markdownlint docs/**/*.md --config .markdownlint.json

# Prose style checking (when vale is configured)

vale docs/**/*.md

# Link validation

markdown-link-check docs/**/*.md

# Template compliance

python scripts/validate_template_compliance.py --directory docs/

# Accessibility validation

python scripts/validate_accessibility.py --directory docs/
```text

#
## Reference Materials

- [Style Guide](./style-guide.md) - Comprehensive style and formatting standards

- [Google Technical Writing](https://developers.google.com/tech-writing) - Industry writing standards

- [Write the Docs Guide](https://www.writethedocs.org/guide/) - Documentation best practices

- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) - Web accessibility standards

#
## Project Resources

- [Main CLAUDE.md](../../CLAUDE.md) - Essential project guidance

- [Documentation Architecture](../CLAUDE.md) - Complete documentation system

- [Contributing Guidelines](../../CONTRIBUTING.md) - Project contribution process

- [PRP Templates](../../PRPs/templates/) - Product requirement templates

#
# Support and Maintenance

#
## Getting Help

- **Template Questions**: Create issue with `documentation` label

- **Style Guide Clarification**: Reference style guide or create discussion

- **Technical Issues**: Use `bug` label for template problems

- **Feature Requests**: Use `enhancement` label for new template needs

#
## Maintenance Schedule

#
### Monthly

- Validate external links in all templates

- Review and update version-specific information

- Check template usage feedback and issues

#
### Quarterly

- Full template compliance audit

- Accessibility validation review

- Style guide updates based on new industry standards

- Cross-reference integrity verification

#
### Annually

- Complete template review and refresh

- Industry standards compliance update

- User research and feedback integration

- Template performance and usage analysis

---

📋 **This template collection provides the foundation for consistent, high-quality documentation across the MCP Task Orchestrator project. Follow the style guide and validation requirements to ensure professional, accessible documentation.**
