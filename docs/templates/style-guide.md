
# Documentation Style Guide

Industry-standard documentation practices for the MCP Task Orchestrator project

#
# Purpose

This style guide establishes comprehensive, industry-standard documentation practices based on Google's Technical Writing Guide, Write the Docs best practices, and project-specific requirements to ensure consistent, accessible, and maintainable documentation.

#
# Core Principles

#
## 1. Clarity First

Write clear, concise, actionable content that serves the reader's needs:

- Use simple, direct language

- Avoid jargon and unnecessary technical complexity

- Define terms when first introduced

- Use active voice wherever possible

- Keep sentences under 25 words when possible

#
## 2. Consistency

Maintain uniform style, tone, and structure throughout all documentation:

- Follow established templates and patterns

- Use consistent terminology across all documents

- Apply formatting rules uniformly

- Maintain consistent cross-reference patterns

#
## 3. Accessibility

Ensure documentation is accessible to all readers:

- Use proper heading hierarchy (H1 → H2 → H3, no skipping)

- Provide alt text for images and diagrams

- Use descriptive link text (avoid "click here")

- Maintain logical reading order

- Use sufficient color contrast

#
## 4. User-Focused

Design content around user tasks and goals:

- Lead with what users need to accomplish

- Organize content by user workflow

- Provide clear success criteria

- Include practical examples and use cases

#
# Writing Standards

#
## Voice and Tone

**Voice**: Professional, helpful, and authoritative
**Tone**: Friendly but direct, technical but approachable

#
### Guidelines

- Use second person ("you") for procedures and instructions

- Use first person plural ("we") for project decisions and recommendations

- Avoid first person singular ("I") except in personal examples

- Be conversational but precise

#
### Examples

```markdown
✅ Good: "You can configure the server by editing the settings file."
❌ Poor: "One might configure the server by editing the settings file."

✅ Good: "We recommend using dependency injection for better testability."
❌ Poor: "I think dependency injection is better for testability."

```text

#
## Language and Grammar

#
### Word Choice

- Use precise, specific terms rather than vague language

- Choose common words over complex alternatives when meaning is preserved

- Avoid unnecessarily long words and sentences

- Use contractions appropriately to maintain conversational tone

#
### Grammar Rules

- Use parallel structure in lists and headings

- Place modifiers close to the words they modify

- Use consistent verb tenses within sections

- Follow standard punctuation rules

#
### Inclusive Language

- Use gender-neutral language

- Choose inclusive terminology

- Avoid idioms and cultural references that may not translate globally

- Use "they/them" as singular pronouns when appropriate

#
## Technical Writing Best Practices

#
### Code Examples

- Always specify language for code blocks

- Use meaningful variable names in examples

- Include complete, runnable examples when possible

- Provide context for code snippets

```text
markdown
✅ Good:

```bash

# Install the package in development mode

pip install -e ".[dev]"
```text

❌ Poor:
```text

pip install -e ".[dev]"

```text
```

#
### Instructions and Procedures

- Use numbered lists for sequential steps

- Start each step with an action verb

- Include expected results for verification

- Provide troubleshooting for common issues

#
### Error Messages and Troubleshooting

- Quote error messages exactly as they appear

- Explain what the error means in user terms

- Provide specific steps to resolve the issue

- Include information about when to seek additional help

#
# Formatting Standards

#
## Markdown Guidelines

#
### Headings

- Start documents with H1 on the first line

- Use sentence case for headings (first word and proper nouns capitalized)

- Don't skip heading levels (H1 → H2 → H3, not H1 → H3)

- Use descriptive, scannable headings

```text
markdown
✅ Good:

# Configuration guide

#
# Setting up the database

### Connection parameters

❌ Poor:

# Configuration Guide

#
## Database Connection Settings (skips H2)

```text

#
### Lists

- Use `1.` for all ordered list items (markdown auto-numbers)

- Use `-` for unordered lists

- Maintain consistent indentation (2 spaces)

- Use parallel structure in list items

#
### Code Blocks

- Always specify language: `bash`, `python`, `yaml`, `json`, `text`

- Use descriptive filenames in code examples

- Include comments to explain complex operations

#
### Links

- Use descriptive link text that makes sense out of context

- Prefer relative links for internal content

- Validate all external links during reviews

```text
markdown
✅ Good: [installation instructions](../installation.md)
❌ Poor: [click here](../installation.md) for installation

```text

#
### Tables

- Use tables for structured data comparison

- Include table headers

- Keep tables simple and scannable

- Consider alternatives for complex data

#
### Images and Diagrams

- Include alt text for all images

- Use clear, descriptive filenames

- Optimize image sizes for web

- Provide text alternatives for visual information

#
## File Organization

#
### File Naming

- Use lowercase with hyphens: `user-guide.md`

- Use descriptive, searchable names

- Follow established naming patterns

- Include file extensions

#
### Directory Structure

```text
text
docs/templates/
├── README.md                     
# Template usage guide
├── style-guide.md               
# This file
├── project-level/               
# Project documentation templates
├── technical/                   
# Technical documentation templates
├── development/                 
# Development documentation templates
├── user-facing/                 
# User-oriented templates
└── internal/                    
# Internal documentation templates

```text

#
# Quality Standards

#
## Content Quality

#
### Completeness

- Address all user questions for the topic

- Include all necessary steps in procedures

- Provide complete code examples

- Cover error scenarios and troubleshooting

#
### Accuracy

- Verify all technical information

- Test all code examples and procedures

- Update content when systems change

- Include version information when relevant

#
### Usability

- Organize content logically

- Use clear section headings

- Provide navigation aids

- Include cross-references to related content

#
## Technical Quality

#
### Markdown Compliance

All documentation must pass markdownlint validation:

```text
bash
markdownlint docs/**/*.md --config .markdownlint.json

```text

#
### Link Validation

- All internal links must be functional

- External links should be validated regularly

- Broken links should be fixed promptly

#
### Template Compliance

- Follow established template patterns

- Include required sections for document type

- Maintain consistent cross-reference structure

#
# Template Standards

#
## Required Elements

All documentation templates must include:

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

Who should use this document

```text

#
### Quality Checklist

```text
markdown

## Quality Checklist

- [ ] Content is accurate and up-to-date

- [ ] All code examples are tested

- [ ] Links are functional

- [ ] Markdownlint validation passes

- [ ] Accessibility guidelines followed

- [ ] Cross-references are accurate

```text

#
### Cross-References

```text
markdown

## Related Documentation

- [Related Guide 1](./path/to/guide1.md)

- [Related Guide 2](./path/to/guide2.md)

- [API Reference](./api-reference.md)

```text

#
## Template Categories

#
### Project-Level Templates

For project overview, contribution guidelines, and governance documents:

- README template

- CONTRIBUTING template

- CHANGELOG template

- LICENSE template

#
### Technical Templates

For system design, architecture, and implementation details:

- Architecture documentation template

- API documentation template

- Configuration guide template

- Deployment guide template

#
### Development Templates

For developer workflows, tools, and processes:

- Setup guide template

- Workflow documentation template

- Testing guide template

- Style guide template

#
### User-Facing Templates

For end-user guidance and support:

- User guide template

- Tutorial template

- Troubleshooting template

- FAQ template

#
### Internal Templates

For project-specific documentation needs:

- CLAUDE command template

- PRP template

- Process documentation template

#
# Validation Framework

#
## Automated Validation

#
### Level 1: Syntax and Style

```text
bash

# Markdown linting

markdownlint docs/**/*.md --config .markdownlint.json

# Prose quality checking (when vale is configured)

vale docs/**/*.md

# Spell checking

cspell "docs/**/*.md"

```text

#
### Level 2: Content Validation

```text
bash

# Link validation

markdown-link-check docs/**/*.md

# Template compliance

python scripts/validate_template_compliance.py --directory docs/

# Cross-reference validation

python scripts/validate_cross_references.py --base-file CLAUDE.md

```text

#
### Level 3: Quality Metrics

```text
bash

# Readability analysis

python scripts/calculate_readability_scores.py --directory docs/

# Content freshness check

python scripts/check_content_freshness.py --directory docs/

# Accessibility validation

python scripts/validate_accessibility.py --directory docs/
```text

#
## Manual Review Process

#
### Content Review

1. **Technical Accuracy**: Verify all technical information

2. **User Testing**: Test procedures with target audience

3. **Editorial Review**: Check grammar, style, and clarity

4. **Accessibility Review**: Ensure content meets accessibility standards

#
### Template Review

1. **Template Compliance**: Verify template adherence

2. **Cross-Reference Validation**: Check all links and references

3. **Version Control**: Ensure proper versioning and change tracking

4. **Integration Testing**: Verify template works in documentation system

#
# Accessibility Guidelines

#
## Screen Reader Compatibility

- Use proper heading hierarchy

- Provide descriptive link text

- Include alt text for images

- Use meaningful list structures

#
## Visual Design

- Maintain sufficient color contrast

- Don't rely solely on color to convey information

- Use clear, readable fonts

- Ensure adequate white space

#
## Content Structure

- Use logical reading order

- Provide multiple navigation methods

- Include skip links for long pages

- Use descriptive page titles

#
# Maintenance Procedures

#
## Regular Maintenance

#
### Monthly Reviews

- Validate all external links

- Check content freshness

- Update version-specific information

- Review user feedback and questions

#
### Quarterly Reviews

- Full template compliance audit

- Accessibility validation

- Style guide updates based on new standards

- Cross-reference integrity check

#
## Update Procedures

#
### Content Updates

1. Check current status tags

2. Update affected cross-references

3. Validate template compliance

4. Run automated quality checks

5. Update maintenance notes

#
### Template Updates

1. Version control template changes

2. Update all documentation using the template

3. Validate system-wide compliance

4. Communicate changes to contributors

5. Update training materials

#
# Implementation Guidelines

#
## For Contributors

#
### Creating New Documentation

1. Choose appropriate template from `docs/templates/`

2. Follow style guide requirements

3. Include all required elements

4. Validate against quality standards

5. Update navigation and cross-references

#
### Updating Existing Documentation

1. Check current status and compliance

2. Follow established patterns

3. Maintain cross-reference accuracy

4. Validate changes against quality standards

5. Update maintenance information

#
## For Reviewers

#
### Review Checklist

- [ ] Content accuracy and completeness

- [ ] Template compliance

- [ ] Style guide adherence

- [ ] Accessibility standards met

- [ ] Quality validation passed

- [ ] Cross-references accurate

#
### Approval Process

1. Technical review for accuracy

2. Editorial review for clarity and style

3. User testing for usability

4. Final approval and publication

#
# Tools and Resources

#
## Recommended Tools

- **Markdownlint**: Markdown syntax and style validation

- **Vale**: Prose style and grammar checking

- **Grammarly**: Additional grammar and style checking

- **Hemingway Editor**: Readability analysis

- **WAVE**: Web accessibility evaluation

#
## Reference Materials

- [Google Technical Writing Courses](https://developers.google.com/tech-writing)

- [Write the Docs Guide](https://www.writethedocs.org/guide/)

- [Plain Language Guidelines](https://plainlanguage.gov/guidelines/)

- [Web Content Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

#
## Project-Specific Resources

- [Markdownlint Configuration](./.markdownlint.json)

- [Template Collection](./docs/templates/)

- [CLAUDE.md Ecosystem](../CLAUDE.md)

- [Contributing Guidelines](../CONTRIBUTING.md)

---

📋 **This style guide provides the foundation for all MCP Task Orchestrator documentation. Follow these standards to ensure consistent, accessible, and maintainable documentation across the project.**
