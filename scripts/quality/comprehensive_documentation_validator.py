#!/usr/bin/env python3
"""
Comprehensive Documentation Validator for MCP Task Orchestrator
Part of Phase 6: Quality Assurance and Integration Testing

This script provides automated validation of all documentation against templates,
link validation, content accuracy validation, and markdownlint batch processing.
"""

import os
import re
import sys
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse, urljoin
import logging
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml

# Add parent directories to path for imports
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class ValidationResult:
    """Represents the result of a validation check"""
    file_path: str
    check_name: str
    passed: bool
    issues: List[str]
    warnings: List[str]
    metadata: Dict = None

@dataclass
class DocumentationHealth:
    """Overall health metrics for documentation"""
    total_files: int
    passed_files: int
    failed_files: int
    total_checks: int
    passed_checks: int
    failed_checks: int
    warnings_count: int
    coverage_percentage: float
    health_score: float

class ComprehensiveDocumentationValidator:
    """Comprehensive validation system for all project documentation"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.results: List[ValidationResult] = []
        self.setup_logging()
        
        # Configuration
        self.config = {
            'doc_directories': [
                'docs', 'PRPs', 'README.md', 'CLAUDE.md', 'CONTRIBUTING.md',
                'CHANGELOG.md', 'QUICK_START.md', 'TESTING_INSTRUCTIONS.md'
            ],
            'template_directory': 'docs/templates',
            'excluded_patterns': [
                '*.backup', '*.bak', '*.tmp', '*/archives/*', 
                '*/legacy/*', '*/test*', '*/.git/*'
            ],
            'required_sections': {
                'README.md': ['# Project', 'Installation', 'Usage'],
                'CLAUDE.md': ['# CLAUDE.md', 'Commands', 'Architecture'],
                'CONTRIBUTING.md': ['# Contributing', 'Development', 'Testing']
            },
            'markdownlint_config': {
                'MD013': False,  # Line length
                'MD025': False,  # Multiple top-level headers
                'MD033': False,  # Inline HTML
                'MD041': False   # First line in file should be a top level header
            }
        }
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.project_root / 'validation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def discover_documentation_files(self) -> List[Path]:
        """Discover all documentation files in the project"""
        doc_files = []
        
        for doc_dir in self.config['doc_directories']:
            path = self.project_root / doc_dir
            
            if path.is_file():
                doc_files.append(path)
            elif path.is_dir():
                for pattern in ['*.md', '*.rst', '*.txt']:
                    doc_files.extend(path.rglob(pattern))
        
        # Filter out excluded patterns
        filtered_files = []
        for file_path in doc_files:
            relative_path = str(file_path.relative_to(self.project_root))
            if not any(re.match(pattern.replace('*', '.*'), relative_path) 
                      for pattern in self.config['excluded_patterns']):
                filtered_files.append(file_path)
        
        self.logger.info(f"Discovered {len(filtered_files)} documentation files")
        return sorted(set(filtered_files))

    def validate_template_compliance(self, file_path: Path) -> ValidationResult:
        """Validate that documentation follows template standards"""
        issues = []
        warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required sections based on file type
            filename = file_path.name
            if filename in self.config['required_sections']:
                for required_section in self.config['required_sections'][filename]:
                    if required_section not in content:
                        issues.append(f"Missing required section: {required_section}")
            
            # Check for proper markdown structure
            lines = content.split('\n')
            
            # Check for proper title (H1)
            has_h1 = any(line.startswith('# ') for line in lines[:10])
            if not has_h1:
                issues.append("Missing H1 title in first 10 lines")
            
            # Check for proper heading hierarchy
            heading_levels = []
            for line in lines:
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    heading_levels.append(level)
            
            for i, level in enumerate(heading_levels[1:], 1):
                prev_level = heading_levels[i-1]
                if level - prev_level > 1:
                    warnings.append(f"Heading hierarchy jump from H{prev_level} to H{level}")
            
            # Check for status tags in filenames (if applicable)
            if '[' in filename and ']' in filename:
                status_match = re.search(r'\[([A-Z-]+)\]', filename)
                if status_match:
                    status = status_match.group(1)
                    valid_statuses = ['CURRENT', 'IN-PROGRESS', 'DRAFT', 'NEEDS-VALIDATION', 
                                    'NEEDS-UPDATE', 'DEPRECATED', 'COMPLETED']
                    if status not in valid_statuses:
                        issues.append(f"Invalid status tag: [{status}]")
        
        except Exception as e:
            issues.append(f"Error reading file: {str(e)}")
        
        return ValidationResult(
            file_path=str(file_path.relative_to(self.project_root)),
            check_name="template_compliance",
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )

    def validate_links(self, file_path: Path) -> ValidationResult:
        """Validate all links in the documentation"""
        issues = []
        warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all markdown links
            link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
            links = re.findall(link_pattern, content)
            
            for link_text, url in links:
                if url.startswith('http'):
                    # External link - check if accessible (with timeout)
                    try:
                        response = requests.head(url, timeout=5, allow_redirects=True)
                        if response.status_code >= 400:
                            issues.append(f"Broken external link: {url} ({response.status_code})")
                    except requests.RequestException:
                        warnings.append(f"Could not verify external link: {url}")
                        
                elif url.startswith('#'):
                    # Anchor link - check if header exists
                    header_id = url[1:].lower().replace(' ', '-')
                    if not re.search(rf"#{{{1,6}}}\s+.*{re.escape(link_text)}", content, re.IGNORECASE):
                        warnings.append(f"Anchor link may be broken: {url}")
                        
                else:
                    # Internal link - check if file exists
                    if url.startswith('/'):
                        target_path = self.project_root / url[1:]
                    else:
                        target_path = file_path.parent / url
                    
                    if not target_path.exists():
                        issues.append(f"Broken internal link: {url}")
        
        except Exception as e:
            issues.append(f"Error validating links: {str(e)}")
        
        return ValidationResult(
            file_path=str(file_path.relative_to(self.project_root)),
            check_name="link_validation",
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )

    def validate_content_accuracy(self, file_path: Path) -> ValidationResult:
        """Validate content accuracy against current codebase"""
        issues = []
        warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for outdated file paths in documentation
            code_pattern = r'`([^`]+\.(py|js|ts|json|yaml|yml|md))`'
            mentioned_files = re.findall(code_pattern, content)
            
            for file_mention, _ in mentioned_files:
                if '/' in file_mention:  # Looks like a path
                    potential_path = self.project_root / file_mention
                    if not potential_path.exists():
                        warnings.append(f"Referenced file may not exist: {file_mention}")
            
            # Check for outdated command references
            command_pattern = r'```(?:bash|shell|console)\n([^`]+)```'
            code_blocks = re.findall(command_pattern, content, re.MULTILINE)
            
            for code_block in code_blocks:
                lines = code_block.strip().split('\n')
                for line in lines:
                    if line.strip().startswith('python -m mcp_task_orchestrator'):
                        # Check if the module structure exists
                        module_path = self.project_root / 'mcp_task_orchestrator'
                        if not module_path.exists():
                            issues.append("References non-existent mcp_task_orchestrator module")
            
            # Check modification date vs content freshness
            file_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            days_old = (datetime.now() - file_modified).days
            
            if days_old > 90:  # More than 3 months old
                warnings.append(f"File is {days_old} days old - may need review")
        
        except Exception as e:
            issues.append(f"Error validating content accuracy: {str(e)}")
        
        return ValidationResult(
            file_path=str(file_path.relative_to(self.project_root)),
            check_name="content_accuracy",
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )

    def run_markdownlint(self, files: List[Path]) -> List[ValidationResult]:
        """Run markdownlint on all markdown files"""
        results = []
        
        # Create temporary config file
        config_file = self.project_root / '.markdownlint-temp.json'
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config['markdownlint_config'], f, indent=2)
            
            # Run markdownlint on each file
            for file_path in files:
                if file_path.suffix.lower() == '.md':
                    try:
                        cmd = ['markdownlint', '-c', str(config_file), str(file_path)]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        
                        issues = []
                        if result.returncode != 0:
                            issues = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                        
                        results.append(ValidationResult(
                            file_path=str(file_path.relative_to(self.project_root)),
                            check_name="markdownlint",
                            passed=result.returncode == 0,
                            issues=issues,
                            warnings=[]
                        ))
                        
                    except FileNotFoundError:
                        self.logger.warning("markdownlint not found - skipping lint checks")
                        break
                    except Exception as e:
                        results.append(ValidationResult(
                            file_path=str(file_path.relative_to(self.project_root)),
                            check_name="markdownlint",
                            passed=False,
                            issues=[f"Error running markdownlint: {str(e)}"],
                            warnings=[]
                        ))
        
        finally:
            if config_file.exists():
                config_file.unlink()
        
        return results

    def validate_documentation_structure(self) -> ValidationResult:
        """Validate overall documentation structure"""
        issues = []
        warnings = []
        
        # Check for required root files
        required_root_files = ['README.md', 'CLAUDE.md', 'CONTRIBUTING.md']
        for required_file in required_root_files:
            if not (self.project_root / required_file).exists():
                issues.append(f"Missing required root file: {required_file}")
        
        # Check for proper docs directory structure
        docs_dir = self.project_root / 'docs'
        if docs_dir.exists():
            expected_subdirs = ['users', 'developers', 'templates']
            for subdir in expected_subdirs:
                if not (docs_dir / subdir).exists():
                    warnings.append(f"Missing expected docs subdirectory: {subdir}")
        
        # Check for template system
        template_dir = self.project_root / self.config['template_directory']
        if not template_dir.exists():
            warnings.append("No template directory found")
        
        return ValidationResult(
            file_path="<project-structure>",
            check_name="documentation_structure",
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )

    def run_comprehensive_validation(self) -> DocumentationHealth:
        """Run all validation checks and return health metrics"""
        self.logger.info("Starting comprehensive documentation validation...")
        
        # Discover all documentation files
        doc_files = self.discover_documentation_files()
        
        # Run structure validation
        structure_result = self.validate_documentation_structure()
        self.results.append(structure_result)
        
        # Run validation checks on each file with parallel processing
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit template compliance checks
            template_futures = {
                executor.submit(self.validate_template_compliance, file_path): file_path 
                for file_path in doc_files
            }
            
            # Submit link validation checks
            link_futures = {
                executor.submit(self.validate_links, file_path): file_path 
                for file_path in doc_files
            }
            
            # Submit content accuracy checks
            content_futures = {
                executor.submit(self.validate_content_accuracy, file_path): file_path 
                for file_path in doc_files
            }
            
            # Collect results
            all_futures = list(template_futures.keys()) + list(link_futures.keys()) + list(content_futures.keys())
            for future in as_completed(all_futures):
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    self.logger.error(f"Validation check failed: {str(e)}")
        
        # Run markdownlint checks
        lint_results = self.run_markdownlint(doc_files)
        self.results.extend(lint_results)
        
        # Calculate health metrics
        health = self.calculate_health_metrics()
        
        self.logger.info(f"Validation complete. Health score: {health.health_score:.1f}%")
        return health

    def calculate_health_metrics(self) -> DocumentationHealth:
        """Calculate overall documentation health metrics"""
        files_checked = set(result.file_path for result in self.results if result.file_path != "<project-structure>")
        
        total_files = len(files_checked)
        total_checks = len(self.results)
        passed_checks = sum(1 for result in self.results if result.passed)
        failed_checks = total_checks - passed_checks
        total_warnings = sum(len(result.warnings) for result in self.results)
        
        # Calculate file-level pass rate
        file_results = {}
        for result in self.results:
            if result.file_path not in file_results:
                file_results[result.file_path] = []
            file_results[result.file_path].append(result.passed)
        
        passed_files = sum(1 for file_path, results in file_results.items() 
                          if all(results) and file_path != "<project-structure>")
        failed_files = total_files - passed_files
        
        # Calculate coverage and health score
        coverage_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Health score considers pass rate and warnings
        health_score = coverage_percentage
        if total_warnings > 0:
            warning_penalty = min(total_warnings * 2, 20)  # Max 20% penalty for warnings
            health_score = max(0, health_score - warning_penalty)
        
        return DocumentationHealth(
            total_files=total_files,
            passed_files=passed_files,
            failed_files=failed_files,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings_count=total_warnings,
            coverage_percentage=coverage_percentage,
            health_score=health_score
        )

    def generate_detailed_report(self, output_file: str = None) -> Dict:
        """Generate a detailed validation report"""
        if not output_file:
            output_file = self.project_root / 'documentation_validation_report.json'
        
        health = self.calculate_health_metrics()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'health_metrics': asdict(health),
            'validation_results': [asdict(result) for result in self.results],
            'summary': {
                'total_files_checked': health.total_files,
                'health_score': health.health_score,
                'issues_found': health.failed_checks,
                'warnings_found': health.warnings_count
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Detailed report saved to: {output_file}")
        return report

    def print_summary(self):
        """Print a summary of validation results"""
        health = self.calculate_health_metrics()
        
        print("\n" + "="*80)
        print("COMPREHENSIVE DOCUMENTATION VALIDATION SUMMARY")
        print("="*80)
        
        print(f"Health Score: {health.health_score:.1f}%")
        print(f"Files Checked: {health.total_files}")
        print(f"Validation Checks: {health.total_checks}")
        print(f"Passed: {health.passed_checks} | Failed: {health.failed_checks}")
        print(f"Warnings: {health.warnings_count}")
        
        if health.failed_checks > 0:
            print(f"\nFailed Checks by Type:")
            check_types = {}
            for result in self.results:
                if not result.passed:
                    check_types[result.check_name] = check_types.get(result.check_name, 0) + 1
            
            for check_type, count in sorted(check_types.items()):
                print(f"  {check_type}: {count}")
        
        if health.health_score >= 90:
            print(f"\n✅ Documentation health is EXCELLENT!")
        elif health.health_score >= 70:
            print(f"\n⚠️  Documentation health is GOOD but has room for improvement.")
        elif health.health_score >= 50:
            print(f"\n❌ Documentation health is POOR and needs attention.")
        else:
            print(f"\n🚨 Documentation health is CRITICAL and requires immediate action.")
        
        print("="*80)


def main():
    """Main entry point for the comprehensive documentation validator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Documentation Validator')
    parser.add_argument('--project-root', '-p', help='Project root directory')
    parser.add_argument('--output', '-o', help='Output report file')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed results')
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Initialize validator
    validator = ComprehensiveDocumentationValidator(args.project_root)
    
    # Run comprehensive validation
    health = validator.run_comprehensive_validation()
    
    # Generate report
    report = validator.generate_detailed_report(args.output)
    
    # Print summary
    if not args.quiet:
        validator.print_summary()
        
        if args.detailed:
            print(f"\nDetailed Issues:")
            for result in validator.results:
                if not result.passed or result.warnings:
                    print(f"\nFile: {result.file_path}")
                    print(f"Check: {result.check_name}")
                    if result.issues:
                        print(f"  Issues: {', '.join(result.issues)}")
                    if result.warnings:
                        print(f"  Warnings: {', '.join(result.warnings)}")
    
    # Exit with appropriate code
    return 0 if health.health_score >= 70 else 1


if __name__ == "__main__":
    sys.exit(main())