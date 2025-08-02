#!/usr/bin/env python3
"""
Run All Documentation Validations

This script runs all validation checks for the feature documentation standardization project
and generates a comprehensive report showing the overall health and compliance status.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import concurrent.futures
import argparse

@dataclass
class ValidationResult:
    validator_name: str
    status: str  # "passed", "failed", "error"
    exit_code: int
    duration: float
    output: str
    error_output: str
    summary: Optional[Dict] = None

@dataclass
class ComprehensiveValidationReport:
    timestamp: datetime
    total_validators: int
    passed_validators: int
    failed_validators: int
    error_validators: int
    overall_status: str
    validation_results: List[ValidationResult] = field(default_factory=list)
    summary_statistics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

class ComprehensiveValidator:
    """Runs all validation scripts and generates comprehensive reports."""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.validators = self._discover_validators()
        
    def _discover_validators(self) -> List[Dict]:
        """Discover all validation scripts."""
        validators = [
            {
                'name': 'Template Compliance',
                'script': 'validate_feature_template_compliance.py',
                'description': 'Validates feature documentation template compliance',
                'critical': True,
                'args': ['--format', 'json']
            },
            {
                'name': 'Outdated References',
                'script': 'check_outdated_references.py',
                'description': 'Checks for outdated references and patterns',
                'critical': False,
                'args': ['--format', 'json']
            },
            {
                'name': 'Cross-References',
                'script': 'validate_cross_references.py',
                'description': 'Validates cross-references and links',
                'critical': False,
                'args': ['--format', 'json', '--no-urls']  # Skip URL validation for speed
            },
            {
                'name': 'File Size Monitoring',
                'script': 'monitor_file_sizes.py',
                'description': 'Monitors file sizes and flags oversized files',
                'critical': True,
                'args': ['--format', 'json']
            },
            {
                'name': 'Metadata Validation',
                'script': 'validate_metadata.py',
                'description': 'Validates YAML frontmatter metadata',
                'critical': True,
                'args': ['--format', 'json']
            },
            {
                'name': 'Modularization Analysis',
                'script': 'analyze_modularization_opportunities.py',
                'description': 'Analyzes modularization opportunities',
                'critical': False,
                'args': ['--format', 'json']
            },
            {
                'name': 'Markdown Linting',
                'script': 'markdownlint',
                'description': 'Markdown linting with feature-specific rules',
                'critical': False,
                'args': ['--config', 'feature_docs_markdownlint.json', '--json'],
                'external': True
            }
        ]
        
        return validators
    
    def run_single_validator(self, validator: Dict, target_path: str, timeout: int = 300) -> ValidationResult:
        """Run a single validator script."""
        start_time = datetime.now()
        
        try:
            # Prepare command
            if validator.get('external', False):
                # External tool (like markdownlint)
                cmd = [validator['script']] + validator['args'] + [target_path]
            else:
                # Python validation script
                script_path = self.base_dir / validator['script']
                if not script_path.exists():
                    return ValidationResult(
                        validator_name=validator['name'],
                        status="error",
                        exit_code=-1,
                        duration=0.0,
                        output="",
                        error_output=f"Validation script not found: {script_path}"
                    )
                
                cmd = [sys.executable, str(script_path)] + validator['args'] + [target_path]
            
            # Run validation
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.base_dir
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Determine status
            status = "passed" if result.returncode == 0 else "failed"
            
            # Try to parse JSON output for summary
            summary = None
            if result.stdout.strip():
                try:
                    summary = json.loads(result.stdout)
                except json.JSONDecodeError:
                    # Not JSON output, that's okay
                    pass
            
            return ValidationResult(
                validator_name=validator['name'],
                status=status,
                exit_code=result.returncode,
                duration=duration,
                output=result.stdout,
                error_output=result.stderr,
                summary=summary
            )
            
        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds()
            return ValidationResult(
                validator_name=validator['name'],
                status="error",
                exit_code=-2,
                duration=duration,
                output="",
                error_output=f"Validation timed out after {timeout} seconds"
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return ValidationResult(
                validator_name=validator['name'],
                status="error",
                exit_code=-3,
                duration=duration,
                output="",
                error_output=f"Validation error: {str(e)}"
            )
    
    def run_all_validations(self, target_path: str, parallel: bool = True, timeout: int = 300) -> ComprehensiveValidationReport:
        """Run all validation scripts."""
        start_time = datetime.now()
        results = []
        
        if parallel:
            # Run validations in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_to_validator = {
                    executor.submit(self.run_single_validator, validator, target_path, timeout): validator
                    for validator in self.validators
                }
                
                for future in concurrent.futures.as_completed(future_to_validator):
                    result = future.result()
                    results.append(result)
        else:
            # Run validations sequentially
            for validator in self.validators:
                result = self.run_single_validator(validator, target_path, timeout)
                results.append(result)
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report(results, start_time)
        return report
    
    def _generate_comprehensive_report(self, results: List[ValidationResult], start_time: datetime) -> ComprehensiveValidationReport:
        """Generate comprehensive validation report."""
        passed_count = sum(1 for r in results if r.status == "passed")
        failed_count = sum(1 for r in results if r.status == "failed")
        error_count = sum(1 for r in results if r.status == "error")
        
        # Determine overall status
        critical_validators = [v for v in self.validators if v.get('critical', False)]
        critical_names = {v['name'] for v in critical_validators}
        critical_failures = [r for r in results if r.validator_name in critical_names and r.status != "passed"]
        
        if critical_failures:
            overall_status = "critical_failure"
        elif error_count > 0:
            overall_status = "error"
        elif failed_count > 0:
            overall_status = "failed"
        else:
            overall_status = "passed"
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_statistics(results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(results)
        
        return ComprehensiveValidationReport(
            timestamp=start_time,
            total_validators=len(results),
            passed_validators=passed_count,
            failed_validators=failed_count,
            error_validators=error_count,
            overall_status=overall_status,
            validation_results=results,
            summary_statistics=summary_stats,
            recommendations=recommendations
        )
    
    def _calculate_summary_statistics(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Calculate summary statistics from all validation results."""
        stats = {
            'total_execution_time': sum(r.duration for r in results),
            'average_execution_time': sum(r.duration for r in results) / len(results) if results else 0,
            'success_rate': len([r for r in results if r.status == "passed"]) / len(results) if results else 0,
            'critical_issues': 0,
            'warning_issues': 0,
            'info_issues': 0,
            'total_files_analyzed': 0,
            'files_with_issues': 0,
            'validation_coverage': {},
            'performance_metrics': {}
        }
        
        # Aggregate statistics from individual validator summaries
        for result in results:
            if result.summary:
                # Template compliance stats
                if result.validator_name == 'Template Compliance' and 'summary' in result.summary:
                    summary = result.summary['summary']
                    stats['total_files_analyzed'] = max(stats['total_files_analyzed'], summary.get('total_files', 0))
                    stats['critical_issues'] += summary.get('total_errors', 0)
                    stats['warning_issues'] += summary.get('total_warnings', 0)
                
                # Metadata validation stats
                elif result.validator_name == 'Metadata Validation' and 'summary' in result.summary:
                    summary = result.summary['summary']
                    stats['validation_coverage']['metadata'] = summary.get('metadata_coverage', 0)
                    stats['critical_issues'] += summary.get('total_errors', 0)
                    stats['warning_issues'] += summary.get('total_warnings', 0)
                
                # File size monitoring stats
                elif result.validator_name == 'File Size Monitoring' and 'report' in result.summary:
                    report = result.summary['report']
                    stats['critical_issues'] += report.get('critical_files', 0)
                    stats['warning_issues'] += report.get('warning_files', 0)
                
                # Cross-reference validation stats
                elif result.validator_name == 'Cross-References' and 'summary' in result.summary:
                    summary = result.summary['summary']
                    stats['validation_coverage']['cross_references'] = summary.get('validation_rate', 0)
                    stats['warning_issues'] += summary.get('invalid_references', 0)
                
                # Outdated references stats
                elif result.validator_name == 'Outdated References' and 'summary' in result.summary:
                    summary = result.summary['summary']
                    stats['warning_issues'] += summary.get('total_issues', 0)
        
        # Performance metrics
        for result in results:
            stats['performance_metrics'][result.validator_name] = {
                'duration': result.duration,
                'status': result.status
            }
        
        return stats
    
    def _generate_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Check for critical failures
        critical_failures = [r for r in results if r.status != "passed" and 
                           any(v['name'] == r.validator_name and v.get('critical', False) 
                               for v in self.validators)]
        
        if critical_failures:
            recommendations.append("🚨 CRITICAL: Address critical validation failures immediately")
            for failure in critical_failures:
                recommendations.append(f"   • Fix {failure.validator_name} issues")
        
        # Check for template compliance issues
        template_result = next((r for r in results if r.validator_name == 'Template Compliance'), None)
        if template_result and template_result.status == "failed":
            recommendations.append("📋 HIGH PRIORITY: Fix template compliance issues")
            recommendations.append("   • Ensure all required metadata fields are present")
            recommendations.append("   • Follow standardized document structure")
        
        # Check for file size issues
        filesize_result = next((r for r in results if r.validator_name == 'File Size Monitoring'), None)
        if filesize_result and filesize_result.summary:
            report = filesize_result.summary.get('report', {})
            if report.get('critical_files', 0) > 0:
                recommendations.append("📏 URGENT: Address oversized files that may crash Claude Code")
                recommendations.append("   • Break large files into smaller modules")
                recommendations.append("   • Extract content to separate files")
        
        # Check for metadata issues
        metadata_result = next((r for r in results if r.validator_name == 'Metadata Validation'), None)
        if metadata_result and metadata_result.summary:
            summary = metadata_result.summary.get('summary', {})
            if summary.get('metadata_coverage', 1.0) < 0.8:
                recommendations.append("📝 MEDIUM PRIORITY: Improve metadata coverage")
                recommendations.append("   • Add YAML frontmatter to files missing metadata")
                recommendations.append("   • Complete required metadata fields")
        
        # Check for cross-reference issues
        crossref_result = next((r for r in results if r.validator_name == 'Cross-References'), None)
        if crossref_result and crossref_result.summary:
            summary = crossref_result.summary.get('summary', {})
            if summary.get('invalid_references', 0) > 0:
                recommendations.append("🔗 MEDIUM PRIORITY: Fix broken cross-references")
                recommendations.append("   • Update broken file links")
                recommendations.append("   • Verify reference targets exist")
        
        # Check for outdated patterns
        outdated_result = next((r for r in results if r.validator_name == 'Outdated References'), None)
        if outdated_result and outdated_result.summary:
            summary = outdated_result.summary.get('summary', {})
            if summary.get('total_issues', 0) > 10:
                recommendations.append("🔄 LOW PRIORITY: Update outdated references and patterns")
                recommendations.append("   • Replace deprecated naming patterns")
                recommendations.append("   • Update architecture references")
        
        # General recommendations
        error_results = [r for r in results if r.status == "error"]
        if error_results:
            recommendations.append("⚙️ INFRASTRUCTURE: Fix validation script errors")
            for error in error_results:
                recommendations.append(f"   • Debug {error.validator_name}: {error.error_output[:100]}...")
        
        if not recommendations:
            recommendations.append("✅ All validations passed! Documentation is in good shape.")
        
        return recommendations
    
    def generate_report_file(self, report: ComprehensiveValidationReport, output_path: str, format: str = "json"):
        """Generate report file in specified format."""
        if format == "json":
            self._generate_json_report(report, output_path)
        elif format == "html":
            self._generate_html_report(report, output_path)
        elif format == "markdown":
            self._generate_markdown_report(report, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_json_report(self, report: ComprehensiveValidationReport, output_path: str):
        """Generate JSON report."""
        report_data = {
            'timestamp': report.timestamp.isoformat(),
            'overall_status': report.overall_status,
            'summary': {
                'total_validators': report.total_validators,
                'passed_validators': report.passed_validators,
                'failed_validators': report.failed_validators,
                'error_validators': report.error_validators
            },
            'statistics': report.summary_statistics,
            'recommendations': report.recommendations,
            'validation_results': [
                {
                    'validator_name': r.validator_name,
                    'status': r.status,
                    'exit_code': r.exit_code,
                    'duration': r.duration,
                    'output': r.output,
                    'error_output': r.error_output,
                    'summary': r.summary
                } for r in report.validation_results
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
    
    def _generate_markdown_report(self, report: ComprehensiveValidationReport, output_path: str):
        """Generate Markdown report."""
        content = f"""# Documentation Validation Report

**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Overall Status:** {report.overall_status.upper()}

## Summary

- **Total Validators:** {report.total_validators}
- **Passed:** {report.passed_validators} ✅
- **Failed:** {report.failed_validators} ❌
- **Errors:** {report.error_validators} ⚠️
- **Success Rate:** {(report.passed_validators / report.total_validators * 100):.1f}%

## Statistics

- **Total Execution Time:** {report.summary_statistics.get('total_execution_time', 0):.2f} seconds
- **Critical Issues:** {report.summary_statistics.get('critical_issues', 0)}
- **Warning Issues:** {report.summary_statistics.get('warning_issues', 0)}
- **Files Analyzed:** {report.summary_statistics.get('total_files_analyzed', 0)}

## Recommendations

"""
        
        for i, rec in enumerate(report.recommendations, 1):
            content += f"{i}. {rec}\\n"
        
        content += "\\n## Validation Results\\n\\n"
        
        for result in report.validation_results:
            status_icon = {"passed": "✅", "failed": "❌", "error": "⚠️"}.get(result.status, "❓")
            content += f"### {result.validator_name} {status_icon}\\n\\n"
            content += f"- **Status:** {result.status}\\n"
            content += f"- **Duration:** {result.duration:.2f}s\\n"
            
            if result.status != "passed":
                content += f"- **Exit Code:** {result.exit_code}\\n"
                if result.error_output:
                    content += f"- **Error:** {result.error_output}\\n"
            
            content += "\\n"
        
        with open(output_path, 'w') as f:
            f.write(content)
    
    def _generate_html_report(self, report: ComprehensiveValidationReport, output_path: str):
        """Generate HTML report."""
        status_colors = {
            "passed": "#28a745",
            "critical_failure": "#dc3545", 
            "failed": "#ffc107",
            "error": "#dc3545"
        }
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation Validation Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; }}
        .header {{ background: {status_colors.get(report.overall_status, '#6c757d')}; color: white; padding: 20px; border-radius: 8px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .recommendations {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .validator {{ margin: 20px 0; padding: 15px; border-radius: 8px; }}
        .passed {{ background: #d4edda; border-left: 4px solid #28a745; }}
        .failed {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
        .error {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
        .duration {{ color: #6c757d; font-size: 0.9em; }}
        pre {{ background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Documentation Validation Report</h1>
        <p>Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Status: <strong>{report.overall_status.upper()}</strong></p>
    </div>
    
    <div class="summary">
        <div class="card">
            <h3>Validators</h3>
            <p><strong>{report.total_validators}</strong> total</p>
            <p>{report.passed_validators} passed, {report.failed_validators} failed, {report.error_validators} errors</p>
        </div>
        <div class="card">
            <h3>Success Rate</h3>
            <p><strong>{(report.passed_validators / report.total_validators * 100):.1f}%</strong></p>
        </div>
        <div class="card">
            <h3>Issues Found</h3>
            <p>{report.summary_statistics.get('critical_issues', 0)} critical</p>
            <p>{report.summary_statistics.get('warning_issues', 0)} warnings</p>
        </div>
        <div class="card">
            <h3>Execution Time</h3>
            <p><strong>{report.summary_statistics.get('total_execution_time', 0):.2f}s</strong></p>
        </div>
    </div>
    
    <div class="recommendations">
        <h2>Recommendations</h2>
        <ol>
"""
        
        for rec in report.recommendations:
            html_content += f"            <li>{rec}</li>\\n"
        
        html_content += """        </ol>
    </div>
    
    <h2>Validation Results</h2>
"""
        
        for result in report.validation_results:
            html_content += f"""    <div class="validator {result.status}">
        <h3>{result.validator_name}</h3>
        <p><strong>Status:</strong> {result.status}</p>
        <p class="duration">Duration: {result.duration:.2f}s</p>
"""
            
            if result.status != "passed" and result.error_output:
                html_content += f"        <p><strong>Error:</strong></p>\\n        <pre>{result.error_output}</pre>\\n"
            
            html_content += "    </div>\\n"
        
        html_content += """</body>
</html>"""
        
        with open(output_path, 'w') as f:
            f.write(html_content)

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Run comprehensive documentation validation')
    parser.add_argument('path', help='Directory path to validate')
    parser.add_argument('--output', help='Output report file')
    parser.add_argument('--format', choices=['json', 'text', 'markdown', 'html'], 
                       default='text', help='Output format')
    parser.add_argument('--parallel', action='store_true', default=True, 
                       help='Run validations in parallel')
    parser.add_argument('--timeout', type=int, default=300, 
                       help='Timeout per validator in seconds')
    parser.add_argument('--quick', action='store_true', 
                       help='Run only critical validators')
    parser.add_argument('--verbose', action='store_true', 
                       help='Show detailed output')
    
    args = parser.parse_args()
    
    # Validate input
    target_path = Path(args.path)
    if not target_path.exists():
        print(f"Error: Path does not exist: {args.path}")
        return 1
    
    # Initialize validator
    validator = ComprehensiveValidator()
    
    # Filter validators if quick mode
    if args.quick:
        validator.validators = [v for v in validator.validators if v.get('critical', False)]
    
    # Run validations
    print(f"Running {len(validator.validators)} validators on {target_path}...")
    if args.parallel:
        print("Running in parallel mode...")
    
    report = validator.run_all_validations(str(target_path), args.parallel, args.timeout)
    
    # Output results
    if args.format == 'text':
        # Console output
        status_icons = {
            "passed": "✅",
            "critical_failure": "🚨", 
            "failed": "❌",
            "error": "⚠️"
        }
        
        print(f"\\n{status_icons.get(report.overall_status, '❓')} Overall Status: {report.overall_status.upper()}")
        print("=" * 60)
        print(f"Validators: {report.passed_validators}/{report.total_validators} passed")
        print(f"Success Rate: {(report.passed_validators / report.total_validators * 100):.1f}%")
        print(f"Execution Time: {report.summary_statistics.get('total_execution_time', 0):.2f}s")
        print(f"Issues: {report.summary_statistics.get('critical_issues', 0)} critical, {report.summary_statistics.get('warning_issues', 0)} warnings")
        
        print("\\nValidation Results:")
        print("-" * 40)
        for result in report.validation_results:
            icon = {"passed": "✅", "failed": "❌", "error": "⚠️"}.get(result.status, "❓")
            print(f"{icon} {result.validator_name}: {result.status} ({result.duration:.2f}s)")
            if args.verbose and result.status != "passed":
                if result.error_output:
                    print(f"   Error: {result.error_output}")
        
        print("\\nRecommendations:")
        print("-" * 20)
        for i, rec in enumerate(report.recommendations, 1):
            print(f"{i}. {rec}")
    
    # Generate report file if requested
    if args.output:
        validator.generate_report_file(report, args.output, args.format)
        print(f"\\nReport saved to: {args.output}")
    
    # Return appropriate exit code
    if report.overall_status in ["critical_failure", "error"]:
        return 2
    elif report.overall_status == "failed":
        return 1
    else:
        return 0

if __name__ == '__main__':
    sys.exit(main())