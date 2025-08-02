#!/usr/bin/env python3
"""
Template System Test Runner

Comprehensive testing script for the template system with detailed reporting.
Runs unit tests, integration tests, security tests, and performance validation.
"""

import sys
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import shutil

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestResult:
    """Container for test results."""
    
    def __init__(self, name: str, success: bool, duration: float, 
                 output: str = "", error: str = ""):
        self.name = name
        self.success = success
        self.duration = duration
        self.output = output
        self.error = error


class TemplateSystemTestRunner:
    """Comprehensive test runner for the template system."""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results: List[TestResult] = []
        self.temp_dirs: List[Path] = []
    
    def cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def run_pytest_suite(self, test_path: str, name: str, 
                        extra_args: List[str] = None) -> TestResult:
        """Run a pytest suite and capture results."""
        print(f"\n🧪 Running {name}...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            test_path,
            "-v",
            "--tb=short",
            "--capture=no"
        ]
        
        if extra_args:
            cmd.extend(extra_args)
        
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            if success:
                print(f"✅ {name} passed in {duration:.2f}s")
            else:
                print(f"❌ {name} failed in {duration:.2f}s")
                print(f"Error output: {result.stderr}")
            
            return TestResult(
                name=name,
                success=success,
                duration=duration,
                output=result.stdout,
                error=result.stderr
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"⏰ {name} timed out after {duration:.2f}s")
            return TestResult(
                name=name,
                success=False,
                duration=duration,
                error="Test timed out"
            )
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {name} crashed: {e}")
            return TestResult(
                name=name,
                success=False,
                duration=duration,
                error=str(e)
            )
    
    def run_manual_validation(self) -> TestResult:
        """Run manual validation tests."""
        print("\n🔧 Running manual validation tests...")
        
        start_time = time.time()
        errors = []
        
        try:
            # Test 1: Import all template system modules
            print("  Testing module imports...")
            try:
                from mcp_task_orchestrator.infrastructure.template_system.json5_parser import JSON5Parser
                from mcp_task_orchestrator.infrastructure.template_system.template_engine import TemplateEngine
                from mcp_task_orchestrator.infrastructure.template_system.security_validator import TemplateSecurityValidator
                from mcp_task_orchestrator.infrastructure.template_system.storage_manager import TemplateStorageManager
                from mcp_task_orchestrator.infrastructure.template_system.template_installer import TemplateInstaller
                print("    ✅ All modules imported successfully")
            except Exception as e:
                errors.append(f"Module import failed: {e}")
                print(f"    ❌ Module import failed: {e}")
            
            # Test 2: Basic JSON5 parsing
            print("  Testing JSON5 parsing...")
            try:
                parser = JSON5Parser()
                test_json5 = '''
                {
                    // Test comment
                    "name": "test",
                    "value": 42,
                    "array": [1, 2, 3,], // trailing comma
                }
                '''
                result = parser.parse(test_json5)
                assert result["name"] == "test"
                assert result["value"] == 42
                assert result["array"] == [1, 2, 3]
                print("    ✅ JSON5 parsing works correctly")
            except Exception as e:
                errors.append(f"JSON5 parsing failed: {e}")
                print(f"    ❌ JSON5 parsing failed: {e}")
            
            # Test 3: Security validation
            print("  Testing security validation...")
            try:
                validator = TemplateSecurityValidator()
                safe_template = {
                    "metadata": {"name": "Safe", "version": "1.0.0", "description": "Safe template"},
                    "tasks": {"task": {"title": "Safe task", "description": "Normal task"}}
                }
                validator.validate_template(safe_template)  # Should not raise
                
                malicious_template = {
                    "metadata": {"name": "Evil", "version": "1.0.0", "description": "Evil template"},
                    "tasks": {"evil": {"title": "Evil", "description": "eval('malicious')"}}
                }
                try:
                    validator.validate_template(malicious_template)
                    errors.append("Security validation failed to detect malicious template")
                    print("    ❌ Security validation failed to detect malicious template")
                except:
                    print("    ✅ Security validation correctly detected malicious template")
            except Exception as e:
                errors.append(f"Security validation testing failed: {e}")
                print(f"    ❌ Security validation testing failed: {e}")
            
            # Test 4: Template storage and retrieval
            print("  Testing template storage...")
            try:
                temp_dir = Path(tempfile.mkdtemp())
                self.temp_dirs.append(temp_dir)
                
                storage = TemplateStorageManager(workspace_dir=temp_dir)
                test_template = {
                    "metadata": {
                        "name": "Test",
                        "version": "1.0.0",
                        "description": "Test template"
                    },
                    "parameters": {
                        "param": {
                            "type": "string",
                            "description": "Test param",
                            "required": True
                        }
                    },
                    "tasks": {
                        "task": {
                            "title": "Test {{param}}",
                            "description": "Test task"
                        }
                    }
                }
                
                # Save template
                storage.save_template("test_template", test_template, "user")
                
                # Load template
                loaded = storage.load_template("test_template", "user")
                assert loaded["metadata"]["name"] == "Test"
                
                # List templates
                templates = storage.list_templates("user")
                template_ids = [t["id"] for t in templates]
                assert "test_template" in template_ids
                
                print("    ✅ Template storage works correctly")
            except Exception as e:
                errors.append(f"Template storage failed: {e}")
                print(f"    ❌ Template storage failed: {e}")
            
            # Test 5: Template instantiation
            print("  Testing template instantiation...")
            try:
                # Copy template from user category to root template directory for testing
                import shutil
                template_source = temp_dir / ".task_orchestrator" / "templates" / "user" / "test_template.json5"
                template_dest = temp_dir / ".task_orchestrator" / "templates" / "test_template.json5"
                shutil.copy(template_source, template_dest)
                
                # Create TemplateEngine with template directory
                engine = TemplateEngine(template_dir=temp_dir / ".task_orchestrator" / "templates")
                parameters = {"param": "TestValue"}
                
                instantiated = engine.instantiate_template("test_template", parameters)
                assert "TestValue" in instantiated["tasks"]["task"]["title"]
                print("    ✅ Template instantiation works correctly")
            except Exception as e:
                errors.append(f"Template instantiation failed: {e}")
                print(f"    ❌ Template instantiation failed: {e}")
            
            duration = time.time() - start_time
            success = len(errors) == 0
            
            if success:
                print(f"✅ Manual validation passed in {duration:.2f}s")
            else:
                print(f"❌ Manual validation failed in {duration:.2f}s")
                for error in errors:
                    print(f"  - {error}")
            
            return TestResult(
                name="Manual Validation",
                success=success,
                duration=duration,
                error="; ".join(errors) if errors else ""
            )
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 Manual validation crashed: {e}")
            return TestResult(
                name="Manual Validation",
                success=False,
                duration=duration,
                error=str(e)
            )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all template system tests."""
        print("🚀 Starting Template System Test Suite")
        print("=" * 60)
        
        # Test suites to run
        test_suites = [
            # Manual validation first
            ("manual", "Manual Validation", None),
            
            # Unit tests
            ("tests/unit/template_system/test_json5_parser.py", "JSON5 Parser Unit Tests", []),
            ("tests/unit/template_system/test_template_engine.py", "Template Engine Unit Tests", []),
            
            # Security tests
            ("tests/security/template_system/test_template_security.py", "Security Tests", ["-m", "not slow"]),
            
            # Integration tests
            ("tests/integration/template_system/test_template_integration.py", "Integration Tests", ["-m", "not slow"]),
        ]
        
        # Run all test suites
        for test_path, name, extra_args in test_suites:
            if test_path == "manual":
                result = self.run_manual_validation()
            else:
                result = self.run_pytest_suite(test_path, name, extra_args)
            
            self.test_results.append(result)
        
        # Generate summary
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(r.duration for r in self.test_results)
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "results": []
        }
        
        for result in self.test_results:
            summary["results"].append({
                "name": result.name,
                "success": result.success,
                "duration": result.duration,
                "error": result.error if not result.success else None
            })
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print detailed test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']} ✅")
        print(f"Failed: {summary['failed_tests']} ❌")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.2f}s")
        
        print("\n📋 DETAILED RESULTS:")
        for result in summary["results"]:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['name']} ({result['duration']:.2f}s)")
            if not result["success"] and result["error"]:
                print(f"    Error: {result['error']}")
        
        if summary["failed_tests"] == 0:
            print("\n🎉 ALL TESTS PASSED! Template system is ready for production.")
        else:
            print(f"\n⚠️  {summary['failed_tests']} tests failed. Please review and fix issues before proceeding.")
        
        return summary["failed_tests"] == 0


def main():
    """Main test runner function."""
    runner = TemplateSystemTestRunner()
    
    try:
        summary = runner.run_all_tests()
        success = runner.print_summary(summary)
        
        # Save detailed report
        report_file = project_root / "docs" / "archives" / "test-artifacts" / f"template_system_test_report_{int(time.time())}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Return appropriate exit code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        runner.cleanup()


if __name__ == "__main__":
    main()