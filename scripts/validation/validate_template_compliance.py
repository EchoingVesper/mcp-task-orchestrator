#!/usr/bin/env python3
"""
Template Compliance Validation Script

This script validates that documentation files follow the established templates
and style guidelines for the MCP Task Orchestrator project.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValidationResult:
    """Results of template validation."""
    file_path: str
    template_type: Optional[str]
    compliance_score: float
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]


class TemplateValidator:
    """Validates documentation files against established templates."""

    def __init__(self, templates_dir: str = "docs/templates"):
        self.templates_dir = Path(templates_dir)
        self.required_sections = self._load_required_sections()
        self.quality_patterns = self._load_quality_patterns()

    def _load_required_sections(self) -> Dict[str, List[str]]:
        """Load required sections for each template type."""
        return {
            "user-guide": [
                "Purpose",
                "Audience", 
                "Overview",
                "Getting Started",
                "Core Features",
                "Configuration",
                "Quality Checklist",
                "Related Documentation"
            ],
            "api-documentation": [
                "Purpose",
                "Audience",
                "API Overview",
                "Authentication",
                "Endpoints",
                "Data Models",
                "Error Handling",
                "Quality Checklist",
                "Related Documentation"
            ],
            "troubleshooting": [
                "Purpose",
                "Audience",
                "How to Use This Guide",
                "Common Issues",
                "Getting Additional Help",
                "Quality Checklist",
                "Related Documentation"
            ],
            "architecture": [
                "Purpose",
                "Audience",
                "Architectural Overview",
                "System Components",
                "Data Architecture",
                "Security Architecture",
                "Quality Checklist",
                "Related Documentation"
            ],
            "setup-guide": [
                "Purpose",
                "Audience",
                "System Requirements",
                "Installation Methods",
                "Configuration",
                "Verification and Testing",
                "Quality Checklist",
                "Related Documentation"
            ],
            "faq": [
                "Purpose",
                "Audience",
                "General Questions",
                "Installation and Setup",
                "Configuration and Usage",
                "Troubleshooting",
                "Getting Additional Help",
                "Quality Checklist",
                "Related Documentation"
            ],
            "claude-command": [
                "Status Header",
                "Context Analysis",
                "Core Commands",
                "Directory Structure",
                "Development Patterns",
                "Integration Points",
                "Troubleshooting",
                "Cross-References"
            ]
        }

    def _load_quality_patterns(self) -> Dict[str, str]:
        """Load regex patterns for quality validation."""
        return {
            "h1_first_line": r"^# .+$",
            "proper_heading_hierarchy": r"^#{1,6} ",
            "code_block_language": r"^```([a-zA-Z]+|text)$",
            "quality_checklist": r"- \[ \] ",
            "related_docs_links": r"\[.+\]\(.+\)",
            "purpose_section": r"## Purpose\s*\n\n.+",
            "audience_section": r"## Audience\s*\n\n.+",
        }

    def validate_file(self, file_path: str) -> ValidationResult:
        """Validate a single documentation file."""
        path = Path(file_path)
        
        if not path.exists():
            return ValidationResult(
                file_path=file_path,
                template_type=None,
                compliance_score=0.0,
                issues=[f"File does not exist: {file_path}"],
                warnings=[],
                suggestions=[]
            )

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        template_type = self._detect_template_type(content, path)
        
        issues = []
        warnings = []
        suggestions = []

        # Basic structure validation
        structure_issues = self._validate_basic_structure(content)
        issues.extend(structure_issues)

        # Template-specific validation
        if template_type:
            template_issues, template_warnings = self._validate_template_structure(
                content, template_type
            )
            issues.extend(template_issues)
            warnings.extend(template_warnings)

        # Quality validation
        quality_issues, quality_warnings, quality_suggestions = self._validate_quality(content)
        issues.extend(quality_issues)
        warnings.extend(quality_warnings)
        suggestions.extend(quality_suggestions)

        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(
            content, template_type, len(issues), len(warnings)
        )

        return ValidationResult(
            file_path=file_path,
            template_type=template_type,
            compliance_score=compliance_score,
            issues=issues,
            warnings=warnings,
            suggestions=suggestions
        )

    def _detect_template_type(self, content: str, path: Path) -> Optional[str]:
        """Detect the type of template based on content and filename."""
        filename = path.name.lower()
        
        # Check filename patterns
        if "user-guide" in filename or "user_guide" in filename:
            return "user-guide"
        elif "api" in filename and ("doc" in filename or "reference" in filename):
            return "api-documentation"
        elif "troubleshooting" in filename or "troubleshoot" in filename:
            return "troubleshooting"
        elif "architecture" in filename or "arch" in filename:
            return "architecture"
        elif "setup" in filename or "install" in filename:
            return "setup-guide"
        elif "faq" in filename:
            return "faq"
        elif "claude" in filename and ("template" in filename or "CLAUDE" in str(path)):
            return "claude-command"

        # Check content patterns
        if "## API Overview" in content and "## Endpoints" in content:
            return "api-documentation"
        elif "## Common Issues" in content and "## Troubleshooting" in content:
            return "troubleshooting"
        elif "## System Components" in content and "## Architecture" in content:
            return "architecture"
        elif "## Installation" in content and "## Configuration" in content:
            return "setup-guide"
        elif "frequently asked questions" in content.lower() or "## General Questions" in content:
            return "faq"
        elif "## Core Commands" in content and "## Development Patterns" in content:
            return "claude-command"
        elif "## Getting Started" in content and "## Core Features" in content:
            return "user-guide"

        return None

    def _validate_basic_structure(self, content: str) -> List[str]:
        """Validate basic markdown structure."""
        issues = []
        lines = content.split('\n')

        # Check H1 on first line
        if not lines or not re.match(self.quality_patterns["h1_first_line"], lines[0]):
            issues.append("Document must start with H1 heading on first line")

        # Check heading hierarchy
        heading_levels = []
        for i, line in enumerate(lines):
            match = re.match(r"^(#{1,6}) ", line)
            if match:
                level = len(match.group(1))
                if heading_levels and level > heading_levels[-1] + 1:
                    issues.append(f"Line {i+1}: Heading level {level} skips levels "
                                f"(previous was {heading_levels[-1]})")
                heading_levels.append(level)

        # Check code block languages
        code_blocks = re.findall(r"^```(.*)$", content, re.MULTILINE)
        for i, lang in enumerate(code_blocks):
            if lang and not re.match(r"^[a-zA-Z]+$|^text$|^$", lang):
                issues.append(f"Code block {i+1}: Invalid or missing language specification")

        return issues

    def _validate_template_structure(self, content: str, template_type: str) -> Tuple[List[str], List[str]]:
        """Validate template-specific structure."""
        issues = []
        warnings = []

        required_sections = self.required_sections.get(template_type, [])
        
        for section in required_sections:
            pattern = f"## {re.escape(section)}"
            if not re.search(pattern, content, re.MULTILINE):
                if section in ["Purpose", "Audience", "Quality Checklist", "Related Documentation"]:
                    issues.append(f"Missing required section: ## {section}")
                else:
                    warnings.append(f"Missing recommended section: ## {section}")

        # Check for quality checklist format
        if "Quality Checklist" in content:
            checklist_pattern = r"## Quality Checklist\s*\n\n(.*?)(?=\n## |\Z)"
            match = re.search(checklist_pattern, content, re.DOTALL)
            if match:
                checklist_content = match.group(1)
                if not re.search(self.quality_patterns["quality_checklist"], checklist_content):
                    issues.append("Quality Checklist must contain checkbox items (- [ ] format)")

        return issues, warnings

    def _validate_quality(self, content: str) -> Tuple[List[str], List[str], List[str]]:
        """Validate overall quality standards."""
        issues = []
        warnings = []
        suggestions = []

        # Check Purpose section
        if not re.search(self.quality_patterns["purpose_section"], content, re.DOTALL):
            issues.append("Purpose section must contain descriptive content")

        # Check Audience section
        if not re.search(self.quality_patterns["audience_section"], content, re.DOTALL):
            warnings.append("Audience section should contain descriptive content")

        # Check Related Documentation links
        if "## Related Documentation" in content:
            related_section = re.search(
                r"## Related Documentation\s*\n\n(.*?)(?=\n## |\Z)", 
                content, 
                re.DOTALL
            )
            if related_section:
                related_content = related_section.group(1)
                links = re.findall(r"\[.+?\]\(.+?\)", related_content)
                if len(links) < 3:
                    suggestions.append("Consider adding more cross-references in Related Documentation")

        # Check for accessibility
        if not self._check_accessibility(content):
            warnings.append("Consider improving accessibility (alt text, heading hierarchy)")

        # Check for examples
        if "```" not in content:
            suggestions.append("Consider adding code examples for better usability")

        return issues, warnings, suggestions

    def _check_accessibility(self, content: str) -> bool:
        """Check basic accessibility compliance."""
        # Check proper heading hierarchy (no skipping levels)
        lines = content.split('\n')
        prev_level = 0
        
        for line in lines:
            match = re.match(r"^(#{1,6}) ", line)
            if match:
                level = len(match.group(1))
                if prev_level > 0 and level > prev_level + 1:
                    return False
                prev_level = level
        
        return True

    def _calculate_compliance_score(self, content: str, template_type: Optional[str], 
                                   issues_count: int, warnings_count: int) -> float:
        """Calculate compliance score (0-100)."""
        base_score = 100.0
        
        # Deduct for issues and warnings
        base_score -= issues_count * 10  # Major deduction for issues
        base_score -= warnings_count * 5  # Minor deduction for warnings
        
        # Bonus for template detection
        if template_type:
            base_score += 10
        
        # Bonus for quality elements
        if "## Quality Checklist" in content:
            base_score += 5
        if "## Related Documentation" in content:
            base_score += 5
        if re.search(r"```[a-zA-Z]+", content):  # Has code examples
            base_score += 5
        
        return max(0.0, min(100.0, base_score))

    def validate_directory(self, directory: str, recursive: bool = True) -> List[ValidationResult]:
        """Validate all markdown files in a directory."""
        directory_path = Path(directory)
        results = []
        
        pattern = "**/*.md" if recursive else "*.md"
        
        for file_path in directory_path.glob(pattern):
            # Skip certain files
            if file_path.name.startswith('.') or file_path.name in ['README.md']:
                continue
                
            result = self.validate_file(str(file_path))
            results.append(result)
        
        return results


class QualityMetricsCalculator:
    """Calculate documentation quality metrics."""

    def calculate_metrics(self, results: List[ValidationResult]) -> Dict:
        """Calculate overall quality metrics."""
        if not results:
            return {
                "total_files": 0,
                "average_compliance_score": 0.0,
                "compliance_distribution": {},
                "template_coverage": {},
                "common_issues": [],
                "recommendations": []
            }

        total_files = len(results)
        scores = [r.compliance_score for r in results]
        average_score = sum(scores) / len(scores)

        # Compliance distribution
        compliance_distribution = {
            "excellent": len([s for s in scores if s >= 90]),
            "good": len([s for s in scores if 75 <= s < 90]),
            "fair": len([s for s in scores if 60 <= s < 75]),
            "poor": len([s for s in scores if s < 60])
        }

        # Template coverage
        template_types = [r.template_type for r in results if r.template_type]
        template_coverage = {}
        for template_type in set(template_types):
            template_coverage[template_type] = template_types.count(template_type)

        # Common issues
        all_issues = []
        for result in results:
            all_issues.extend(result.issues)
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Recommendations
        recommendations = self._generate_recommendations(results, average_score)

        return {
            "total_files": total_files,
            "average_compliance_score": round(average_score, 2),
            "compliance_distribution": compliance_distribution,
            "template_coverage": template_coverage,
            "common_issues": common_issues,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }

    def _generate_recommendations(self, results: List[ValidationResult], average_score: float) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if average_score < 70:
            recommendations.append("Overall compliance is low. Focus on template adherence and basic structure.")
        
        # Check for missing templates
        untyped_files = [r for r in results if r.template_type is None]
        if len(untyped_files) > len(results) * 0.3:
            recommendations.append("Many files don't follow established templates. Consider template adoption.")

        # Check for quality checklists
        missing_checklists = [r for r in results if "Quality Checklist" not in str(r.issues)]
        if len(missing_checklists) > len(results) * 0.5:
            recommendations.append("Add quality checklists to more documentation files.")

        # Check for cross-references
        missing_refs = [r for r in results if "Related Documentation" not in str(r.issues)]
        if len(missing_refs) > len(results) * 0.5:
            recommendations.append("Improve cross-referencing between documentation files.")

        return recommendations


def main():
    """Main script execution."""
    parser = argparse.ArgumentParser(description="Validate documentation template compliance")
    parser.add_argument("path", help="File or directory path to validate")
    parser.add_argument("--recursive", "-r", action="store_true", 
                       help="Recursively validate directories")
    parser.add_argument("--output", "-o", help="Output file for results (JSON format)")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                       help="Output format")
    parser.add_argument("--templates-dir", default="docs/templates",
                       help="Templates directory path")
    parser.add_argument("--min-score", type=float, default=70.0,
                       help="Minimum compliance score for success")
    
    args = parser.parse_args()

    validator = TemplateValidator(args.templates_dir)
    
    # Validate files
    if os.path.isfile(args.path):
        results = [validator.validate_file(args.path)]
    else:
        results = validator.validate_directory(args.path, args.recursive)

    # Calculate metrics
    calculator = QualityMetricsCalculator()
    metrics = calculator.calculate_metrics(results)

    # Output results
    if args.format == "json":
        output_data = {
            "metrics": metrics,
            "results": [
                {
                    "file_path": r.file_path,
                    "template_type": r.template_type,
                    "compliance_score": r.compliance_score,
                    "issues": r.issues,
                    "warnings": r.warnings,
                    "suggestions": r.suggestions
                }
                for r in results
            ]
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
        else:
            print(json.dumps(output_data, indent=2))
    else:
        # Text format
        print("Documentation Template Compliance Report")
        print(f"{'='*50}")
        print(f"Total files validated: {metrics['total_files']}")
        print(f"Average compliance score: {metrics['average_compliance_score']}%")
        print()
        
        print("Compliance Distribution:")
        for level, count in metrics['compliance_distribution'].items():
            percentage = (count / metrics['total_files']) * 100 if metrics['total_files'] > 0 else 0
            print(f"  {level.capitalize()}: {count} files ({percentage:.1f}%)")
        print()
        
        if metrics['template_coverage']:
            print("Template Coverage:")
            for template_type, count in metrics['template_coverage'].items():
                print(f"  {template_type}: {count} files")
            print()
        
        if metrics['common_issues']:
            print("Most Common Issues:")
            for i, (issue, count) in enumerate(metrics['common_issues'][:5], 1):
                print(f"  {i}. {issue} ({count} files)")
            print()
        
        if metrics['recommendations']:
            print("Recommendations:")
            for i, rec in enumerate(metrics['recommendations'], 1):
                print(f"  {i}. {rec}")
            print()

        # Individual file results
        if len(results) <= 20:  # Only show individual results for small sets
            print("Individual File Results:")
            for result in sorted(results, key=lambda x: x.compliance_score):
                print(f"\n{result.file_path}")
                print(f"  Template: {result.template_type or 'Unknown'}")
                print(f"  Score: {result.compliance_score:.1f}%")
                
                if result.issues:
                    print(f"  Issues ({len(result.issues)}):")
                    for issue in result.issues[:3]:  # Show first 3 issues
                        print(f"    - {issue}")
                    if len(result.issues) > 3:
                        print(f"    ... and {len(result.issues) - 3} more")
                
                if result.warnings:
                    print(f"  Warnings ({len(result.warnings)}):")
                    for warning in result.warnings[:2]:  # Show first 2 warnings
                        print(f"    - {warning}")
                    if len(result.warnings) > 2:
                        print(f"    ... and {len(result.warnings) - 2} more")

    # Exit code based on compliance
    failed_files = [r for r in results if r.compliance_score < args.min_score]
    if failed_files:
        print(f"\n{len(failed_files)} files below minimum compliance score of {args.min_score}%")
        sys.exit(1)
    else:
        print(f"\nAll files meet minimum compliance score of {args.min_score}%")
        sys.exit(0)


if __name__ == "__main__":
    main()