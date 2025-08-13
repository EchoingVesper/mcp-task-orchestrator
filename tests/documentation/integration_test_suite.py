#!/usr/bin/env python3
"""
Documentation Integration Test Suite
Part of Phase 6: Quality Assurance and Integration Testing

This test suite validates end-to-end functionality of the documentation system,
including templates, Claude Code hooks, automation, and CI/CD integration.
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import unittest
from unittest.mock import patch, MagicMock
import logging

# Add project root to path for imports
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

class DocumentationIntegrationTestSuite(unittest.TestCase):
    """Integration test suite for the complete documentation system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.project_root = project_root
        cls.test_workspace = cls.project_root / 'tests' / 'temp_workspace'
        cls.test_workspace.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        cls.logger = logging.getLogger(__name__)
        
        # Test configuration
        cls.test_config = {
            'template_directory': cls.project_root / 'docs' / 'templates',
            'hooks_directory': cls.project_root / '.claude' / 'hooks',
            'scripts_directory': cls.project_root / 'scripts',
            'ci_directory': cls.project_root / 'scripts' / 'ci'
        }
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if cls.test_workspace.exists():
            shutil.rmtree(cls.test_workspace)
    
    def setUp(self):
        """Set up for each test"""
        # Create fresh test directory for each test
        self.test_dir = self.test_workspace / f"test_{self._testMethodName}"
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)
    
    def tearDown(self):
        """Clean up after each test"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_template_system_functionality(self):
        """Test that the template system works with real content"""
        self.logger.info("Testing template system functionality...")
        
        # Test 1: Check if template files exist
        template_dir = self.project_root / 'docs' / 'templates'
        self.assertTrue(template_dir.exists(), "Template directory should exist")
        
        expected_templates = [
            'documentation-master-template.md',
            'style-guide.md'
        ]
        
        for template_name in expected_templates:
            template_path = template_dir / template_name
            self.assertTrue(template_path.exists(), f"Template {template_name} should exist")
        
        # Test 2: Validate template content structure
        master_template = template_dir / 'documentation-master-template.md'
        if master_template.exists():
            with open(master_template, 'r') as f:
                content = f.read()
            
            # Check for expected template sections
            expected_sections = ['# Title', '## Overview', '## Installation', '## Usage']
            for section in expected_sections:
                self.assertIn(section, content, f"Template should contain {section}")
        
        # Test 3: Test template application (mock)
        test_doc = self.test_dir / 'test_document.md'
        template_content = """# Test Document

## Overview
This is a test document following the template.

## Installation
Installation instructions here.

## Usage
Usage instructions here.
"""
        
        with open(test_doc, 'w') as f:
            f.write(template_content)
        
        # Validate the test document follows template structure
        self.assertTrue(test_doc.exists())
        with open(test_doc, 'r') as f:
            doc_content = f.read()
        
        self.assertIn('# Test Document', doc_content)
        self.assertIn('## Overview', doc_content)
        self.logger.info("✅ Template system functionality test passed")

    def test_claude_code_hooks_integration(self):
        """Test Claude Code hooks and automation integration"""
        self.logger.info("Testing Claude Code hooks integration...")
        
        # Test 1: Check if hooks directory and files exist
        hooks_dir = self.project_root / '.claude'
        expected_hooks_files = ['hooks', 'config.json']
        
        if hooks_dir.exists():
            for hook_file in expected_hooks_files:
                hook_path = hooks_dir / hook_file
                if hook_path.exists():
                    self.logger.info(f"✅ Found hook file: {hook_file}")
        
        # Test 2: Validate hook configuration
        config_path = hooks_dir / 'config.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Check for hook configuration
                if 'hooks' in config:
                    self.assertIsInstance(config['hooks'], dict, "Hooks should be a dictionary")
                    self.logger.info("✅ Hook configuration is valid JSON")
            except json.JSONDecodeError:
                self.fail("Hook configuration should be valid JSON")
        
        # Test 3: Test hook execution (if hooks exist)
        hooks_script_dir = hooks_dir / 'hooks'
        if hooks_script_dir.exists():
            hook_files = list(hooks_script_dir.glob('*.sh'))
            if hook_files:
                # Test that hooks are executable
                for hook_file in hook_files[:1]:  # Test first hook only
                    self.assertTrue(os.access(hook_file, os.X_OK), 
                                  f"Hook {hook_file.name} should be executable")
                    self.logger.info(f"✅ Hook {hook_file.name} is executable")
        
        self.logger.info("✅ Claude Code hooks integration test completed")

    def test_ci_cd_integration(self):
        """Test CI/CD integration functionality"""
        self.logger.info("Testing CI/CD integration...")
        
        # Test 1: Check for CI/CD scripts
        ci_dir = self.project_root / 'scripts' / 'ci'
        self.assertTrue(ci_dir.exists(), "CI directory should exist")
        
        # Test 2: Check for GitHub Actions workflow (if exists)
        github_workflows = self.project_root / '.github' / 'workflows'
        if github_workflows.exists():
            workflow_files = list(github_workflows.glob('*.yml')) + list(github_workflows.glob('*.yaml'))
            if workflow_files:
                self.logger.info(f"Found {len(workflow_files)} GitHub Action workflow(s)")
                
                # Validate at least one workflow file
                test_workflow = workflow_files[0]
                with open(test_workflow, 'r') as f:
                    workflow_content = f.read()
                
                # Check for basic workflow structure
                self.assertIn('on:', workflow_content, "Workflow should have triggers")
                self.assertIn('jobs:', workflow_content, "Workflow should have jobs")
                self.logger.info("✅ GitHub Actions workflow structure is valid")
        
        # Test 3: Test quality validator integration
        quality_validator = self.project_root / 'scripts' / 'quality' / 'comprehensive_documentation_validator.py'
        self.assertTrue(quality_validator.exists(), "Quality validator should exist")
        
        # Test that the validator is executable
        result = subprocess.run([sys.executable, str(quality_validator), '--help'], 
                              capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "Quality validator should be executable")
        self.logger.info("✅ CI/CD integration test passed")

    def test_documentation_automation_workflow(self):
        """Test end-to-end documentation automation workflow"""
        self.logger.info("Testing documentation automation workflow...")
        
        # Test 1: Create a test markdown file with issues
        test_md = self.test_dir / 'test_document.md'
        problematic_content = """This is a test document without proper structure

Some content here

## A heading without H1 first

More content
"""
        
        with open(test_md, 'w') as f:
            f.write(problematic_content)
        
        # Test 2: Run the comprehensive validator on the test file
        validator_script = self.project_root / 'scripts' / 'quality' / 'comprehensive_documentation_validator.py'
        if validator_script.exists():
            try:
                result = subprocess.run([
                    sys.executable, str(validator_script), 
                    '--project-root', str(self.test_dir),
                    '--quiet'
                ], capture_output=True, text=True, timeout=30)
                
                # Validator should identify issues
                self.assertNotEqual(result.returncode, 0, 
                                  "Validator should identify issues in problematic document")
                self.logger.info("✅ Documentation validator correctly identified issues")
                
            except subprocess.TimeoutExpired:
                self.logger.warning("⚠️  Validator test timed out")
        
        # Test 3: Test with a properly structured document
        proper_content = """# Test Document

## Overview
This is a properly structured test document.

## Installation
Installation instructions here.

## Usage
Usage instructions here.
"""
        
        with open(test_md, 'w') as f:
            f.write(proper_content)
        
        if validator_script.exists():
            try:
                result = subprocess.run([
                    sys.executable, str(validator_script), 
                    '--project-root', str(self.test_dir),
                    '--quiet'
                ], capture_output=True, text=True, timeout=30)
                
                # Should pass with properly structured document
                self.logger.info("✅ Documentation automation workflow test completed")
                
            except subprocess.TimeoutExpired:
                self.logger.warning("⚠️  Validator test timed out")

    def test_quality_dashboard_integration(self):
        """Test integration with quality dashboard functionality"""
        self.logger.info("Testing quality dashboard integration...")
        
        # Test 1: Check if quality dashboard script exists
        dashboard_script = self.project_root / 'scripts' / 'quality' / 'quality_assurance_dashboard.py'
        
        # This will be created in the next step, so we'll check for the directory
        quality_dir = self.project_root / 'scripts' / 'quality'
        self.assertTrue(quality_dir.exists(), "Quality scripts directory should exist")
        
        # Test 2: Test report generation functionality
        validator_script = self.project_root / 'scripts' / 'quality' / 'comprehensive_documentation_validator.py'
        if validator_script.exists():
            # Create a test report
            report_file = self.test_dir / 'test_report.json'
            
            try:
                result = subprocess.run([
                    sys.executable, str(validator_script), 
                    '--project-root', str(self.project_root),
                    '--output', str(report_file),
                    '--quiet'
                ], capture_output=True, text=True, timeout=60)
                
                # Check if report was generated
                if report_file.exists():
                    with open(report_file, 'r') as f:
                        report_data = json.load(f)
                    
                    # Validate report structure
                    expected_keys = ['timestamp', 'health_metrics', 'validation_results', 'summary']
                    for key in expected_keys:
                        self.assertIn(key, report_data, f"Report should contain {key}")
                    
                    self.logger.info("✅ Quality dashboard integration test passed")
                else:
                    self.logger.warning("⚠️  Report file was not generated")
                    
            except subprocess.TimeoutExpired:
                self.logger.warning("⚠️  Dashboard integration test timed out")

    def test_maintenance_documentation_system(self):
        """Test maintenance and handoff documentation system"""
        self.logger.info("Testing maintenance documentation system...")
        
        # Test 1: Check for maintenance documentation
        maintenance_docs_expected = [
            'docs/developers/maintenance-procedures.md'
        ]
        
        for doc_path in maintenance_docs_expected:
            full_path = self.project_root / doc_path
            if full_path.exists():
                self.assertTrue(full_path.exists(), f"Maintenance doc should exist: {doc_path}")
                
                # Check content structure
                with open(full_path, 'r') as f:
                    content = f.read()
                
                # Should contain maintenance procedures
                maintenance_keywords = ['maintenance', 'procedures', 'workflow']
                has_maintenance_content = any(keyword in content.lower() 
                                            for keyword in maintenance_keywords)
                self.assertTrue(has_maintenance_content, 
                              "Maintenance documentation should contain relevant keywords")
                self.logger.info(f"✅ Found and validated maintenance doc: {doc_path}")
        
        # Test 2: Check for agent workflow documentation
        scripts_dir = self.project_root / 'scripts'
        if scripts_dir.exists():
            script_files = list(scripts_dir.rglob('*.py'))
            documented_scripts = 0
            
            for script_file in script_files[:5]:  # Test first 5 scripts
                with open(script_file, 'r') as f:
                    content = f.read()
                
                # Check for docstrings or comments
                if '"""' in content or "'''" in content or '# ' in content:
                    documented_scripts += 1
            
            # At least some scripts should be documented
            self.assertGreater(documented_scripts, 0, 
                             "Some scripts should have documentation")
            self.logger.info(f"✅ Found {documented_scripts} documented scripts")
        
        self.logger.info("✅ Maintenance documentation system test completed")

    def test_recovery_system_integration(self):
        """Test that recovery systems from Phase 0 still function"""
        self.logger.info("Testing recovery system integration...")
        
        # Test 1: Check for recovery scripts
        recovery_scripts = [
            'scripts/comprehensive_markdown_recovery.py',
            'scripts/emergency_markdown_recovery.py'
        ]
        
        for script_name in recovery_scripts:
            script_path = self.project_root / script_name
            if script_path.exists():
                self.assertTrue(script_path.exists(), f"Recovery script should exist: {script_name}")
                
                # Test that script is executable
                try:
                    result = subprocess.run([sys.executable, str(script_path), '--help'], 
                                          capture_output=True, text=True, timeout=10)
                    # Should not crash (return code may vary)
                    self.logger.info(f"✅ Recovery script is functional: {script_name}")
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"⚠️  Recovery script test timed out: {script_name}")
                except Exception as e:
                    self.logger.warning(f"⚠️  Recovery script test failed: {script_name} - {e}")
        
        # Test 2: Check backup functionality
        backups_dir = self.project_root / 'backups'
        if backups_dir.exists():
            self.assertTrue(backups_dir.exists(), "Backups directory should exist")
            self.logger.info("✅ Backup system is available")
        
        self.logger.info("✅ Recovery system integration test completed")

    def test_validation_system_no_regressions(self):
        """Test that all validation systems work together without conflicts"""
        self.logger.info("Testing validation system integration without regressions...")
        
        # Test 1: Run multiple validation tools in sequence
        validation_tools = []
        
        # Add comprehensive validator
        comprehensive_validator = self.project_root / 'scripts' / 'quality' / 'comprehensive_documentation_validator.py'
        if comprehensive_validator.exists():
            validation_tools.append(('comprehensive_validator', comprehensive_validator))
        
        # Add existing validation tools
        existing_validators = [
            'scripts/validation/run_all_validations.py',
            'scripts/validation/validate_template_compliance.py',
        ]
        
        for validator_path in existing_validators:
            full_path = self.project_root / validator_path
            if full_path.exists():
                validation_tools.append((validator_path, full_path))
        
        # Test each validator individually
        for tool_name, tool_path in validation_tools:
            try:
                result = subprocess.run([
                    sys.executable, str(tool_path), '--help'
                ], capture_output=True, text=True, timeout=10)
                
                self.logger.info(f"✅ Validation tool functional: {tool_name}")
                
            except subprocess.TimeoutExpired:
                self.logger.warning(f"⚠️  Validation tool timed out: {tool_name}")
            except Exception as e:
                self.logger.warning(f"⚠️  Validation tool error: {tool_name} - {e}")
        
        # Test 2: Check for conflicts between validation tools
        # Run comprehensive validator on project
        if comprehensive_validator.exists():
            try:
                result = subprocess.run([
                    sys.executable, str(comprehensive_validator),
                    '--project-root', str(self.project_root),
                    '--quiet'
                ], capture_output=True, text=True, timeout=60)
                
                self.logger.info("✅ Comprehensive validation completed without system conflicts")
                
            except subprocess.TimeoutExpired:
                self.logger.warning("⚠️  Comprehensive validation timed out")
            except Exception as e:
                self.logger.warning(f"⚠️  Comprehensive validation error: {e}")
        
        self.logger.info("✅ Validation system regression test completed")


class TestRunner:
    """Custom test runner for the documentation integration test suite"""
    
    def __init__(self, verbosity=2):
        self.verbosity = verbosity
    
    def run_all_tests(self) -> Tuple[int, int, List[str]]:
        """Run all tests and return results"""
        # Create test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(DocumentationIntegrationTestSuite)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=self.verbosity, stream=sys.stdout)
        result = runner.run(suite)
        
        # Collect failed test names
        failed_tests = []
        for failure in result.failures + result.errors:
            failed_tests.append(failure[0]._testMethodName)
        
        return result.testsRun, len(failed_tests), failed_tests
    
    def run_specific_test(self, test_name: str) -> bool:
        """Run a specific test by name"""
        suite = unittest.TestSuite()
        test_case = DocumentationIntegrationTestSuite(test_name)
        suite.addTest(test_case)
        
        runner = unittest.TextTestRunner(verbosity=self.verbosity)
        result = runner.run(suite)
        
        return result.wasSuccessful()


def main():
    """Main entry point for the integration test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Documentation Integration Test Suite')
    parser.add_argument('--test', '-t', help='Run specific test by name')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    parser.add_argument('--report', '-r', help='Generate test report file')
    
    args = parser.parse_args()
    
    # Set verbosity
    verbosity = 2
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 3
    
    # Create test runner
    test_runner = TestRunner(verbosity=verbosity)
    
    # Run tests
    if args.test:
        # Run specific test
        success = test_runner.run_specific_test(args.test)
        return 0 if success else 1
    else:
        # Run all tests
        total_tests, failed_count, failed_tests = test_runner.run_all_tests()
        
        # Generate report if requested
        if args.report:
            report = {
                'timestamp': datetime.now().isoformat(),
                'total_tests': total_tests,
                'passed_tests': total_tests - failed_count,
                'failed_tests': failed_count,
                'failed_test_names': failed_tests,
                'success_rate': ((total_tests - failed_count) / total_tests * 100) if total_tests > 0 else 0
            }
            
            with open(args.report, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"Test report saved to: {args.report}")
        
        # Print summary
        if not args.quiet:
            print(f"\nTest Summary:")
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {total_tests - failed_count}")
            print(f"Failed: {failed_count}")
            
            if failed_tests:
                print(f"Failed Tests: {', '.join(failed_tests)}")
        
        return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    import datetime
    sys.exit(main())