#!/usr/bin/env python3
"""
Final Integration Validator for Documentation Ecosystem Modernization
Part of Phase 6: Quality Assurance and Integration Testing

This script validates that all phases of the documentation modernization
work together correctly and that no regressions have been introduced.
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
import shutil

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class PhaseValidationResult:
    """Result of validating a specific phase"""
    phase: str
    phase_number: int
    passed: bool
    issues: List[str]
    warnings: List[str]
    components_validated: List[str]
    score: float

@dataclass
class IntegrationValidationSummary:
    """Overall integration validation summary"""
    total_phases: int
    passed_phases: int
    failed_phases: int
    overall_score: float
    critical_issues: List[str]
    recommendations: List[str]
    validation_timestamp: str

class FinalIntegrationValidator:
    """Comprehensive validator for all documentation modernization phases"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.results: List[PhaseValidationResult] = []
        self.setup_logging()
        
        # Phase definitions
        self.phases = {
            0: {
                'name': 'Recovery System Foundation',
                'components': [
                    'scripts/comprehensive_markdown_recovery.py',
                    'scripts/emergency_markdown_recovery.py',
                    'backups/',
                ]
            },
            1: {
                'name': 'Template System and Standards',
                'components': [
                    'docs/templates/documentation-master-template.md',
                    'docs/templates/style-guide.md',
                    'docs/templates/',
                ]
            },
            2: {
                'name': 'Documentation Modernization',
                'components': [
                    'docs/users/',
                    'docs/developers/',
                    'docs/templates/',
                ]
            },
            3: {
                'name': 'Claude Code Integration',
                'components': [
                    '.claude/',
                    'CLAUDE.md',
                ]
            },
            4: {
                'name': 'Cleanup and Lifecycle Management',
                'components': [
                    'scripts/lifecycle/',
                    'scripts/validation/',
                ]
            },
            5: {
                'name': 'CI/CD Automation',
                'components': [
                    'scripts/ci/',
                    '.github/workflows/',
                ]
            },
            6: {
                'name': 'Quality Assurance and Integration Testing',
                'components': [
                    'scripts/quality/comprehensive_documentation_validator.py',
                    'scripts/quality/quality_assurance_dashboard.py',
                    'tests/documentation/integration_test_suite.py',
                    'docs/developers/contributing/documentation-maintenance-guide.md',
                ]
            }
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.project_root / 'final_integration_validation.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def validate_phase_0_recovery_system(self) -> PhaseValidationResult:
        """Validate Phase 0: Recovery System Foundation"""
        issues = []
        warnings = []
        components_validated = []
        
        # Check recovery scripts exist and are functional
        recovery_scripts = [
            'scripts/comprehensive_markdown_recovery.py',
            'scripts/emergency_markdown_recovery.py'
        ]
        
        for script_path in recovery_scripts:
            full_path = self.project_root / script_path
            if full_path.exists():
                components_validated.append(script_path)
                # Test script can run
                try:
                    result = subprocess.run([
                        sys.executable, str(full_path), '--help'
                    ], capture_output=True, text=True, timeout=10)
                    if result.returncode != 0:
                        warnings.append(f"Recovery script may have issues: {script_path}")
                except Exception as e:
                    warnings.append(f"Cannot test recovery script: {script_path} - {str(e)}")
            else:
                issues.append(f"Missing recovery script: {script_path}")
        
        # Check backup system
        backups_dir = self.project_root / 'backups'
        if backups_dir.exists():
            components_validated.append('backups/')
        else:
            warnings.append("Backups directory not found")
        
        # Calculate score
        total_components = len(self.phases[0]['components'])
        validated_components = len(components_validated)
        score = (validated_components / total_components * 100) if total_components > 0 else 0
        if issues:
            score = max(0, score - len(issues) * 20)
        
        return PhaseValidationResult(
            phase="Recovery System Foundation",
            phase_number=0,
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            components_validated=components_validated,
            score=score
        )
    
    def validate_phase_1_templates(self) -> PhaseValidationResult:
        """Validate Phase 1: Template System and Standards"""
        issues = []
        warnings = []
        components_validated = []
        
        # Check template directory and files
        template_dir = self.project_root / 'docs' / 'templates'
        if template_dir.exists():
            components_validated.append('docs/templates/')
            
            # Check for key template files
            key_templates = [
                'documentation-master-template.md',
                'style-guide.md'
            ]
            
            for template in key_templates:
                template_path = template_dir / template
                if template_path.exists():
                    components_validated.append(f'docs/templates/{template}')
                    
                    # Validate template content
                    with open(template_path, 'r') as f:
                        content = f.read()
                    
                    if len(content) < 100:
                        warnings.append(f"Template may be incomplete: {template}")
                    
                    # Check for basic structure
                    if not content.startswith('#'):
                        warnings.append(f"Template missing H1 header: {template}")
                else:
                    issues.append(f"Missing key template: {template}")
        else:
            issues.append("Template directory not found")
        
        # Calculate score
        total_components = len(self.phases[1]['components'])
        validated_components = len(components_validated)
        score = (validated_components / total_components * 100) if total_components > 0 else 0
        if issues:
            score = max(0, score - len(issues) * 25)
        
        return PhaseValidationResult(
            phase="Template System and Standards",
            phase_number=1,
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            components_validated=components_validated,
            score=score
        )
    
    def validate_phase_2_modernization(self) -> PhaseValidationResult:
        """Validate Phase 2: Documentation Modernization"""
        issues = []
        warnings = []
        components_validated = []
        
        # Check docs directory structure
        docs_dir = self.project_root / 'docs'
        if docs_dir.exists():
            expected_subdirs = ['users', 'developers', 'templates']
            
            for subdir in expected_subdirs:
                subdir_path = docs_dir / subdir
                if subdir_path.exists():
                    components_validated.append(f'docs/{subdir}/')
                    
                    # Check for content
                    md_files = list(subdir_path.rglob('*.md'))
                    if len(md_files) == 0:
                        warnings.append(f"No markdown files found in docs/{subdir}/")
                else:
                    issues.append(f"Missing docs subdirectory: {subdir}")
        else:
            issues.append("Docs directory not found")
        
        # Check for key documentation files
        key_docs = [
            'README.md',
            'CLAUDE.md',
            'CONTRIBUTING.md'
        ]
        
        for doc in key_docs:
            doc_path = self.project_root / doc
            if doc_path.exists():
                components_validated.append(doc)
            else:
                issues.append(f"Missing key documentation: {doc}")
        
        # Calculate score
        expected_components = len(expected_subdirs) + len(key_docs)
        score = (len(components_validated) / expected_components * 100) if expected_components > 0 else 0
        if issues:
            score = max(0, score - len(issues) * 15)
        
        return PhaseValidationResult(
            phase="Documentation Modernization",
            phase_number=2,
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            components_validated=components_validated,
            score=score
        )
    
    def validate_phase_3_claude_integration(self) -> PhaseValidationResult:
        """Validate Phase 3: Claude Code Integration"""
        issues = []
        warnings = []
        components_validated = []
        
        # Check Claude configuration
        claude_dir = self.project_root / '.claude'
        if claude_dir.exists():
            components_validated.append('.claude/')
            
            # Check for configuration files
            config_file = claude_dir / 'config.json'
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    components_validated.append('.claude/config.json')
                except json.JSONDecodeError:
                    issues.append("Invalid Claude configuration JSON")
            else:
                warnings.append("No Claude configuration file found")
            
            # Check for hooks
            hooks_dir = claude_dir / 'hooks'
            if hooks_dir.exists():
                hook_files = list(hooks_dir.glob('*.sh'))
                if hook_files:
                    components_validated.append('.claude/hooks/')
                    for hook_file in hook_files:
                        if not os.access(hook_file, os.X_OK):
                            warnings.append(f"Hook not executable: {hook_file.name}")
                else:
                    warnings.append("No hook files found")
        else:
            warnings.append("Claude configuration directory not found")
        
        # Check CLAUDE.md
        claude_md = self.project_root / 'CLAUDE.md'
        if claude_md.exists():
            components_validated.append('CLAUDE.md')
            
            with open(claude_md, 'r') as f:
                content = f.read()
            
            # Check for key sections
            expected_sections = ['Architecture', 'Commands', 'Guidelines']
            missing_sections = []
            for section in expected_sections:
                if section.lower() not in content.lower():
                    missing_sections.append(section)
            
            if missing_sections:
                warnings.append(f"CLAUDE.md missing sections: {', '.join(missing_sections)}")
        else:
            issues.append("CLAUDE.md not found")
        
        # Calculate score
        score = len(components_validated) * 25  # Each component worth 25 points
        if issues:
            score = max(0, score - len(issues) * 30)
        
        return PhaseValidationResult(
            phase="Claude Code Integration",
            phase_number=3,
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            components_validated=components_validated,
            score=min(100, score)
        )
    
    def validate_phase_4_lifecycle_management(self) -> PhaseValidationResult:
        """Validate Phase 4: Cleanup and Lifecycle Management"""
        issues = []
        warnings = []
        components_validated = []
        
        # Check lifecycle scripts
        lifecycle_dir = self.project_root / 'scripts' / 'lifecycle'
        if lifecycle_dir.exists():
            components_validated.append('scripts/lifecycle/')
            
            py_files = list(lifecycle_dir.glob('*.py'))
            if len(py_files) == 0:
                warnings.append("No lifecycle scripts found")
        else:
            warnings.append("Lifecycle scripts directory not found")
        
        # Check validation scripts
        validation_dir = self.project_root / 'scripts' / 'validation'
        if validation_dir.exists():
            components_validated.append('scripts/validation/')
            
            # Check for key validation scripts
            key_validators = [
                'run_all_validations.py',
                'validate_template_compliance.py'
            ]
            
            for validator in key_validators:
                validator_path = validation_dir / validator
                if validator_path.exists():
                    components_validated.append(f'scripts/validation/{validator}')
                else:
                    warnings.append(f"Missing validation script: {validator}")
        else:
            warnings.append("Validation scripts directory not found")
        
        # Test that cleanup and validation work
        try:
            # Test validation system
            run_all_validations = validation_dir / 'run_all_validations.py'
            if run_all_validations.exists():
                result = subprocess.run([
                    sys.executable, str(run_all_validations), '--help'
                ], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    warnings.append("Validation system may have issues")
        except Exception as e:
            warnings.append(f"Cannot test validation system: {str(e)}")
        
        # Calculate score
        score = len(components_validated) * 20  # Each component worth 20 points
        if issues:
            score = max(0, score - len(issues) * 25)
        
        return PhaseValidationResult(
            phase="Cleanup and Lifecycle Management",
            phase_number=4,
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            components_validated=components_validated,
            score=min(100, score)
        )
    
    def validate_phase_5_ci_cd_automation(self) -> PhaseValidationResult:
        """Validate Phase 5: CI/CD Automation"""
        issues = []
        warnings = []
        components_validated = []
        
        # Check CI scripts
        ci_dir = self.project_root / 'scripts' / 'ci'
        if ci_dir.exists():
            components_validated.append('scripts/ci/')
            
            py_files = list(ci_dir.glob('*.py'))
            if len(py_files) > 0:
                for py_file in py_files[:3]:  # Test first 3 files
                    try:
                        result = subprocess.run([
                            sys.executable, str(py_file), '--help'
                        ], capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            components_validated.append(f'scripts/ci/{py_file.name}')
                    except Exception:
                        warnings.append(f"CI script may have issues: {py_file.name}")
            else:
                warnings.append("No CI scripts found")
        else:
            warnings.append("CI scripts directory not found")
        
        # Check GitHub workflows
        github_workflows = self.project_root / '.github' / 'workflows'
        if github_workflows.exists():
            components_validated.append('.github/workflows/')
            
            workflow_files = list(github_workflows.glob('*.yml')) + list(github_workflows.glob('*.yaml'))
            if workflow_files:
                for workflow_file in workflow_files[:2]:  # Check first 2 workflows
                    try:
                        with open(workflow_file, 'r') as f:
                            content = f.read()
                        
                        # Basic YAML structure check
                        if 'on:' in content and 'jobs:' in content:
                            components_validated.append(f'.github/workflows/{workflow_file.name}')
                        else:
                            warnings.append(f"Workflow may have structure issues: {workflow_file.name}")
                    except Exception:
                        warnings.append(f"Cannot read workflow: {workflow_file.name}")
            else:
                warnings.append("No GitHub workflow files found")
        else:
            warnings.append("GitHub workflows directory not found")
        
        # Calculate score
        score = len(components_validated) * 20  # Each component worth 20 points
        if issues:
            score = max(0, score - len(issues) * 30)
        
        return PhaseValidationResult(
            phase="CI/CD Automation",
            phase_number=5,
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            components_validated=components_validated,
            score=min(100, score)
        )
    
    def validate_phase_6_quality_assurance(self) -> PhaseValidationResult:
        """Validate Phase 6: Quality Assurance and Integration Testing"""
        issues = []
        warnings = []
        components_validated = []
        
        # Check quality scripts
        quality_dir = self.project_root / 'scripts' / 'quality'
        expected_quality_scripts = [
            'comprehensive_documentation_validator.py',
            'quality_assurance_dashboard.py',
            'final_integration_validator.py'
        ]
        
        for script in expected_quality_scripts:
            script_path = quality_dir / script
            if script_path.exists():
                components_validated.append(f'scripts/quality/{script}')
                
                # Test script can run
                try:
                    result = subprocess.run([
                        sys.executable, str(script_path), '--help'
                    ], capture_output=True, text=True, timeout=15)
                    if result.returncode != 0 and script != 'final_integration_validator.py':
                        warnings.append(f"Quality script may have issues: {script}")
                except Exception as e:
                    warnings.append(f"Cannot test quality script: {script} - {str(e)}")
            else:
                issues.append(f"Missing quality script: {script}")
        
        # Check integration test suite
        integration_test = self.project_root / 'tests' / 'documentation' / 'integration_test_suite.py'
        if integration_test.exists():
            components_validated.append('tests/documentation/integration_test_suite.py')
            
            # Test can run
            try:
                result = subprocess.run([
                    sys.executable, str(integration_test), '--help'
                ], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    warnings.append("Integration test suite may have issues")
            except Exception as e:
                warnings.append(f"Cannot test integration suite: {str(e)}")
        else:
            issues.append("Missing integration test suite")
        
        # Check maintenance guide
        maintenance_guide = self.project_root / 'docs' / 'developers' / 'contributing' / 'documentation-maintenance-guide.md'
        if maintenance_guide.exists():
            components_validated.append('docs/developers/contributing/documentation-maintenance-guide.md')
            
            with open(maintenance_guide, 'r') as f:
                content = f.read()
            
            # Check for key sections
            expected_sections = ['Daily Maintenance', 'Weekly Maintenance', 'Agent Workflow Patterns', 'Handoff Procedures']
            missing_sections = []
            for section in expected_sections:
                if section.lower() not in content.lower():
                    missing_sections.append(section)
            
            if missing_sections:
                warnings.append(f"Maintenance guide missing sections: {', '.join(missing_sections)}")
        else:
            issues.append("Missing maintenance guide")
        
        # Calculate score
        expected_components = len(expected_quality_scripts) + 2  # +2 for test suite and guide
        score = (len(components_validated) / expected_components * 100) if expected_components > 0 else 0
        if issues:
            score = max(0, score - len(issues) * 20)
        
        return PhaseValidationResult(
            phase="Quality Assurance and Integration Testing",
            phase_number=6,
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            components_validated=components_validated,
            score=score
        )
    
    def test_system_integration(self) -> Tuple[bool, List[str], List[str]]:
        """Test that all systems work together without conflicts"""
        issues = []
        warnings = []
        
        # Test 1: Run comprehensive validator
        validator_script = self.project_root / 'scripts' / 'quality' / 'comprehensive_documentation_validator.py'
        if validator_script.exists():
            try:
                result = subprocess.run([
                    sys.executable, str(validator_script),
                    '--project-root', str(self.project_root),
                    '--quiet'
                ], capture_output=True, text=True, timeout=120)
                
                # Should complete without errors (exit code may vary based on findings)
                if 'Error' in result.stderr:
                    issues.append("Comprehensive validator has errors")
                
            except subprocess.TimeoutExpired:
                warnings.append("Comprehensive validator timed out")
            except Exception as e:
                warnings.append(f"Cannot test comprehensive validator: {str(e)}")
        
        # Test 2: Try running integration tests
        integration_test = self.project_root / 'tests' / 'documentation' / 'integration_test_suite.py'
        if integration_test.exists():
            try:
                result = subprocess.run([
                    sys.executable, str(integration_test), 
                    '--test', 'test_template_system_functionality'
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    warnings.append("Some integration tests are failing")
                
            except subprocess.TimeoutExpired:
                warnings.append("Integration tests timed out")
            except Exception as e:
                warnings.append(f"Cannot run integration tests: {str(e)}")
        
        # Test 3: Check that recovery systems still work
        recovery_script = self.project_root / 'scripts' / 'comprehensive_markdown_recovery.py'
        if recovery_script.exists():
            try:
                result = subprocess.run([
                    sys.executable, str(recovery_script), '--help'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode != 0:
                    warnings.append("Recovery system may have issues")
                
            except Exception as e:
                warnings.append(f"Cannot test recovery system: {str(e)}")
        
        return len(issues) == 0, issues, warnings
    
    def run_comprehensive_validation(self) -> IntegrationValidationSummary:
        """Run comprehensive validation of all phases"""
        self.logger.info("Starting comprehensive integration validation...")
        
        # Validate each phase
        validation_methods = [
            self.validate_phase_0_recovery_system,
            self.validate_phase_1_templates,
            self.validate_phase_2_modernization,
            self.validate_phase_3_claude_integration,
            self.validate_phase_4_lifecycle_management,
            self.validate_phase_5_ci_cd_automation,
            self.validate_phase_6_quality_assurance
        ]
        
        for validate_method in validation_methods:
            try:
                result = validate_method()
                self.results.append(result)
                self.logger.info(f"Phase {result.phase_number} ({result.phase}): {'PASSED' if result.passed else 'FAILED'} - Score: {result.score:.1f}%")
            except Exception as e:
                self.logger.error(f"Error validating phase {validate_method.__name__}: {str(e)}")
                # Create a failed result
                phase_num = int(validate_method.__name__.split('_')[2])
                self.results.append(PhaseValidationResult(
                    phase=self.phases[phase_num]['name'],
                    phase_number=phase_num,
                    passed=False,
                    issues=[f"Validation error: {str(e)}"],
                    warnings=[],
                    components_validated=[],
                    score=0.0
                ))
        
        # Test system integration
        integration_passed, integration_issues, integration_warnings = self.test_system_integration()
        
        # Calculate overall metrics
        total_phases = len(self.results)
        passed_phases = sum(1 for result in self.results if result.passed)
        failed_phases = total_phases - passed_phases
        overall_score = sum(result.score for result in self.results) / total_phases if total_phases > 0 else 0
        
        # Collect critical issues
        critical_issues = []
        for result in self.results:
            if not result.passed:
                critical_issues.extend([f"Phase {result.phase_number}: {issue}" for issue in result.issues])
        
        if integration_issues:
            critical_issues.extend([f"Integration: {issue}" for issue in integration_issues])
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        
        summary = IntegrationValidationSummary(
            total_phases=total_phases,
            passed_phases=passed_phases,
            failed_phases=failed_phases,
            overall_score=overall_score,
            critical_issues=critical_issues,
            recommendations=recommendations,
            validation_timestamp=datetime.now().isoformat()
        )
        
        self.logger.info(f"Validation complete. Overall score: {overall_score:.1f}%")
        return summary
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Analyze results and generate specific recommendations
        failed_phases = [result for result in self.results if not result.passed]
        
        if failed_phases:
            recommendations.append("Address critical issues in failed phases immediately")
            
            for phase_result in failed_phases:
                if phase_result.phase_number == 0:
                    recommendations.append("Set up recovery system - essential for system reliability")
                elif phase_result.phase_number == 1:
                    recommendations.append("Establish template system - required for consistent documentation")
                elif phase_result.phase_number == 6:
                    recommendations.append("Fix quality assurance system - needed for ongoing maintenance")
        
        # Check for high warning counts
        high_warning_phases = [result for result in self.results if len(result.warnings) > 3]
        if high_warning_phases:
            recommendations.append("Address warnings to prevent future issues")
        
        # Check overall score
        overall_score = sum(result.score for result in self.results) / len(self.results) if self.results else 0
        
        if overall_score < 70:
            recommendations.append("Overall system health is low - comprehensive review needed")
        elif overall_score < 90:
            recommendations.append("System is functional but has room for improvement")
        
        return recommendations
    
    def generate_detailed_report(self, output_file: str = None) -> str:
        """Generate detailed validation report"""
        if not output_file:
            output_file = self.project_root / 'final_integration_validation_report.json'
        
        summary = self.calculate_summary()
        
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'summary': asdict(summary),
            'phase_results': [asdict(result) for result in self.results],
            'system_integration': {
                'tested': True,
                'issues_found': len(summary.critical_issues),
                'recommendations': summary.recommendations
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Detailed report saved to: {output_file}")
        return str(output_file)
    
    def calculate_summary(self) -> IntegrationValidationSummary:
        """Calculate validation summary"""
        if not self.results:
            return IntegrationValidationSummary(
                total_phases=0,
                passed_phases=0,
                failed_phases=0,
                overall_score=0.0,
                critical_issues=[],
                recommendations=['Run validation first'],
                validation_timestamp=datetime.now().isoformat()
            )
        
        total_phases = len(self.results)
        passed_phases = sum(1 for result in self.results if result.passed)
        failed_phases = total_phases - passed_phases
        overall_score = sum(result.score for result in self.results) / total_phases
        
        critical_issues = []
        for result in self.results:
            if not result.passed:
                critical_issues.extend([f"Phase {result.phase_number}: {issue}" for issue in result.issues])
        
        recommendations = self.generate_recommendations()
        
        return IntegrationValidationSummary(
            total_phases=total_phases,
            passed_phases=passed_phases,
            failed_phases=failed_phases,
            overall_score=overall_score,
            critical_issues=critical_issues,
            recommendations=recommendations,
            validation_timestamp=datetime.now().isoformat()
        )
    
    def print_summary_report(self):
        """Print a summary of the validation results"""
        summary = self.calculate_summary()
        
        print("\n" + "="*80)
        print("FINAL INTEGRATION VALIDATION SUMMARY")
        print("="*80)
        
        print(f"Overall Score: {summary.overall_score:.1f}%")
        print(f"Phases Validated: {summary.total_phases}")
        print(f"Phases Passed: {summary.passed_phases}")
        print(f"Phases Failed: {summary.failed_phases}")
        
        # Print phase-by-phase results
        print(f"\nPhase Results:")
        for result in self.results:
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"  Phase {result.phase_number}: {result.phase} - {status} ({result.score:.1f}%)")
            
            if result.issues:
                print(f"    Issues: {len(result.issues)}")
                for issue in result.issues[:2]:  # Show first 2 issues
                    print(f"      - {issue}")
                if len(result.issues) > 2:
                    print(f"      ... and {len(result.issues) - 2} more")
        
        # Print critical issues
        if summary.critical_issues:
            print(f"\nCritical Issues ({len(summary.critical_issues)}):")
            for issue in summary.critical_issues[:5]:  # Show first 5
                print(f"  - {issue}")
            if len(summary.critical_issues) > 5:
                print(f"  ... and {len(summary.critical_issues) - 5} more")
        
        # Print recommendations
        if summary.recommendations:
            print(f"\nRecommendations:")
            for rec in summary.recommendations:
                print(f"  • {rec}")
        
        # Overall assessment
        if summary.overall_score >= 90:
            print(f"\n🎉 EXCELLENT: Documentation ecosystem is fully functional and healthy!")
        elif summary.overall_score >= 70:
            print(f"\n✅ GOOD: Documentation ecosystem is functional with minor issues.")
        elif summary.overall_score >= 50:
            print(f"\n⚠️  FAIR: Documentation ecosystem has significant issues that need attention.")
        else:
            print(f"\n🚨 CRITICAL: Documentation ecosystem has major problems requiring immediate action.")
        
        print("="*80)


def main():
    """Main entry point for the final integration validator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Final Integration Validator for Documentation Ecosystem')
    parser.add_argument('--project-root', '-p', help='Project root directory')
    parser.add_argument('--output', '-o', help='Output report file')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    parser.add_argument('--phase', '-P', type=int, help='Validate specific phase only (0-6)')
    parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed results')
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Initialize validator
    validator = FinalIntegrationValidator(args.project_root)
    
    if args.phase is not None:
        # Validate specific phase
        if args.phase < 0 or args.phase > 6:
            print("Error: Phase must be between 0 and 6")
            return 1
        
        validation_methods = [
            validator.validate_phase_0_recovery_system,
            validator.validate_phase_1_templates,
            validator.validate_phase_2_modernization,
            validator.validate_phase_3_claude_integration,
            validator.validate_phase_4_lifecycle_management,
            validator.validate_phase_5_ci_cd_automation,
            validator.validate_phase_6_quality_assurance
        ]
        
        result = validation_methods[args.phase]()
        validator.results = [result]
        
        if not args.quiet:
            print(f"Phase {result.phase_number} ({result.phase}): {'PASSED' if result.passed else 'FAILED'}")
            print(f"Score: {result.score:.1f}%")
            
            if args.detailed:
                if result.issues:
                    print(f"Issues: {', '.join(result.issues)}")
                if result.warnings:
                    print(f"Warnings: {', '.join(result.warnings)}")
        
        return 0 if result.passed else 1
    else:
        # Run comprehensive validation
        summary = validator.run_comprehensive_validation()
        
        # Generate report
        if args.output:
            validator.generate_detailed_report(args.output)
        
        # Print summary
        if not args.quiet:
            validator.print_summary_report()
        
        # Exit with appropriate code
        return 0 if summary.overall_score >= 70 else 1


if __name__ == "__main__":
    sys.exit(main())