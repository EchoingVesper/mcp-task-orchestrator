#!/usr/bin/env python3
"""
Integrated Quality Validator for CI/CD Pipeline
Coordinates all quality validation components following Japanese development standards.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class IntegratedQualityValidator:
    """Comprehensive quality validation coordinator for CI/CD pipeline."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "validation_components": {
                "japanese_standards": {"status": "pending", "score": 0, "issues": []},
                "template_compliance": {"status": "pending", "score": 0, "issues": []},
                "documentation_quality": {"status": "pending", "score": 0, "issues": []},
                "project_cleanliness": {"status": "pending", "score": 0, "issues": []},
                "security_validation": {"status": "pending", "score": 0, "issues": []}
            },
            "overall_quality_score": 0,
            "ci_cd_integration_status": "pending",
            "recommendations": []
        }
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def run_command(self, cmd: List[str], timeout: int = 300) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return 1, "", str(e)
    
    def validate_japanese_standards(self) -> bool:
        """Validate Japanese development standards compliance."""
        self.logger.info("🗾 Validating Japanese Development Standards...")
        
        try:
            # Status tag compliance
            prp_files = list(self.project_root.glob('PRPs/**/*.md'))
            status_tagged_files = [
                f for f in prp_files 
                if any(tag in f.name for tag in ['[IN-PROGRESS]', '[DRAFT]', '[COMPLETED]', '[CURRENT]'])
            ]
            
            status_compliance = len(status_tagged_files) / max(len(prp_files), 1)
            
            # Root directory cleanliness
            root_files = [f for f in os.listdir(self.project_root) if os.path.isfile(f)]
            essential_files = {
                'README.md', 'CHANGELOG.md', 'LICENSE', 'CONTRIBUTING.md',
                'CLAUDE.md', 'QUICK_START.md', 'TESTING_INSTRUCTIONS.md',
                'pyproject.toml', 'setup.py', 'requirements.txt'
            }
            non_essential = [f for f in root_files if f not in essential_files and not f.startswith('.')]
            cleanliness_score = max(0, 100 - len(non_essential) * 10)
            
            # Systematic organization
            expected_dirs = ['docs', 'tests', 'scripts', 'tools', 'mcp_task_orchestrator']
            existing_dirs = [d for d in expected_dirs if (self.project_root / d).exists()]
            organization_score = (len(existing_dirs) / len(expected_dirs)) * 100
            
            # Calculate overall Japanese standards score
            japanese_score = (status_compliance * 40 + cleanliness_score * 30 + organization_score * 30) / 100 * 100
            
            self.results["validation_components"]["japanese_standards"]["score"] = round(japanese_score, 1)
            self.results["validation_components"]["japanese_standards"]["status"] = "passed" if japanese_score >= 80 else "failed"
            
            if japanese_score < 80:
                issues = []
                if status_compliance < 0.8:
                    issues.append(f"Low status tag compliance: {status_compliance:.1%}")
                if cleanliness_score < 70:
                    issues.append(f"Root directory too cluttered: {len(non_essential)} non-essential files")
                if organization_score < 80:
                    issues.append(f"Missing expected directories: {len(existing_dirs)}/{len(expected_dirs)}")
                
                self.results["validation_components"]["japanese_standards"]["issues"] = issues
            
            return japanese_score >= 80
            
        except Exception as e:
            self.logger.error(f"Japanese standards validation failed: {e}")
            self.results["validation_components"]["japanese_standards"]["status"] = "error"
            self.results["validation_components"]["japanese_standards"]["issues"] = [str(e)]
            return False
    
    def validate_template_compliance(self) -> bool:
        """Validate template compliance across the project."""
        self.logger.info("📋 Validating Template Compliance...")
        
        try:
            compliance_score = 0
            total_checks = 0
            
            # PRP template compliance
            prp_files = list(self.project_root.glob('PRPs/**/*.md'))
            if prp_files:
                compliant_prps = 0
                for prp_file in prp_files:
                    content = prp_file.read_text()
                    required_sections = ['## Overview', '## Implementation', '## Acceptance Criteria']
                    has_required = sum(1 for section in required_sections if section in content)
                    if has_required >= 2:
                        compliant_prps += 1
                
                prp_compliance = compliant_prps / len(prp_files)
                compliance_score += prp_compliance * 50
                total_checks += 50
            
            # Documentation header consistency
            md_files = list(self.project_root.glob('**/*.md'))
            if md_files:
                consistent_headers = 0
                for md_file in md_files:
                    try:
                        content = md_file.read_text()
                        lines = content.split('\n')
                        h1_count = sum(1 for line in lines if line.strip().startswith('# '))
                        if h1_count == 1:
                            consistent_headers += 1
                    except:
                        pass
                
                header_compliance = consistent_headers / len(md_files)
                compliance_score += header_compliance * 50
                total_checks += 50
            
            # Calculate final compliance score
            final_compliance = (compliance_score / max(total_checks, 1)) if total_checks > 0 else 0
            
            self.results["validation_components"]["template_compliance"]["score"] = round(final_compliance, 1)
            self.results["validation_components"]["template_compliance"]["status"] = "passed" if final_compliance >= 75 else "failed"
            
            return final_compliance >= 75
            
        except Exception as e:
            self.logger.error(f"Template compliance validation failed: {e}")
            self.results["validation_components"]["template_compliance"]["status"] = "error"
            return False
    
    def validate_documentation_quality(self) -> bool:
        """Run comprehensive documentation quality checks."""
        self.logger.info("📚 Validating Documentation Quality...")
        
        try:
            quality_score = 100
            issues = []
            
            # Check if quality automation script exists
            quality_script = self.project_root / 'scripts' / 'quality_automation.py'
            if quality_script.exists():
                exit_code, stdout, stderr = self.run_command([
                    'python', str(quality_script), '--check', 'all'
                ])
                
                if exit_code == 0:
                    quality_score = 95  # High score for passing automation
                else:
                    quality_score = 60  # Reduced score for issues
                    issues.append("Quality automation detected issues")
            
            # Check for markdownlint
            exit_code, stdout, stderr = self.run_command([
                'markdownlint-cli2', 'docs/**/*.md', '*.md', '--config', '.markdownlint.json'
            ])
            
            if exit_code != 0:
                quality_score -= 20
                issues.append("Markdownlint found formatting issues")
            
            self.results["validation_components"]["documentation_quality"]["score"] = quality_score
            self.results["validation_components"]["documentation_quality"]["status"] = "passed" if quality_score >= 70 else "failed"
            self.results["validation_components"]["documentation_quality"]["issues"] = issues
            
            return quality_score >= 70
            
        except Exception as e:
            self.logger.error(f"Documentation quality validation failed: {e}")
            self.results["validation_components"]["documentation_quality"]["status"] = "error"
            return False
    
    def validate_project_cleanliness(self) -> bool:
        """Validate project cleanliness and organization."""
        self.logger.info("🧹 Validating Project Cleanliness...")
        
        try:
            cleanliness_score = 100
            issues = []
            
            # Check for temporary files
            temp_patterns = ['.tmp', '.temp', '~', '.bak']
            temp_files = []
            for pattern in temp_patterns:
                temp_files.extend(self.project_root.glob(f'**/*{pattern}'))
            
            if temp_files:
                cleanliness_score -= min(len(temp_files) * 5, 30)
                issues.append(f"Found {len(temp_files)} temporary files")
            
            # Check build artifacts organization
            build_artifacts = list(self.project_root.glob('**/__pycache__'))
            build_artifacts.extend(self.project_root.glob('**/*.pyc'))
            scattered_artifacts = [
                a for a in build_artifacts 
                if not any(skip in str(a) for skip in ['.git/', 'venv/', 'node_modules/'])
            ]
            
            if len(scattered_artifacts) > 10:
                cleanliness_score -= 20
                issues.append(f"Too many scattered build artifacts: {len(scattered_artifacts)}")
            
            self.results["validation_components"]["project_cleanliness"]["score"] = cleanliness_score
            self.results["validation_components"]["project_cleanliness"]["status"] = "passed" if cleanliness_score >= 80 else "failed"
            self.results["validation_components"]["project_cleanliness"]["issues"] = issues
            
            return cleanliness_score >= 80
            
        except Exception as e:
            self.logger.error(f"Project cleanliness validation failed: {e}")
            self.results["validation_components"]["project_cleanliness"]["status"] = "error"
            return False
    
    def validate_security(self) -> bool:
        """Run security validation checks."""
        self.logger.info("🔒 Validating Security...")
        
        try:
            security_score = 100
            issues = []
            
            # Basic security pattern check in documentation
            import re
            credential_patterns = [
                r'password\s*[=:]\s*["\'][^"\']+["\']',
                r'api_key\s*[=:]\s*["\'][^"\']+["\']',
                r'secret\s*[=:]\s*["\'][^"\']+["\']'
            ]
            
            md_files = list(self.project_root.glob('**/*.md'))
            security_issues = 0
            
            for md_file in md_files:
                if '.git/' in str(md_file):
                    continue
                try:
                    content = md_file.read_text()
                    for pattern in credential_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if not any(placeholder in match.lower() for placeholder in [
                                'example', 'placeholder', 'your_'
                            ]):
                                security_issues += 1
                except:
                    pass
            
            if security_issues > 0:
                security_score -= min(security_issues * 20, 60)
                issues.append(f"Found {security_issues} potential credential exposures")
            
            self.results["validation_components"]["security_validation"]["score"] = security_score
            self.results["validation_components"]["security_validation"]["status"] = "passed" if security_score >= 80 else "failed"
            self.results["validation_components"]["security_validation"]["issues"] = issues
            
            return security_score >= 80
            
        except Exception as e:
            self.logger.error(f"Security validation failed: {e}")
            self.results["validation_components"]["security_validation"]["status"] = "error"
            return False
    
    def calculate_overall_score(self) -> int:
        """Calculate overall quality score from all components."""
        total_score = 0
        component_count = 0
        
        for component_name, component in self.results["validation_components"].items():
            if component["status"] not in ["pending", "error"]:
                total_score += component["score"]
                component_count += 1
        
        overall_score = (total_score / max(component_count, 1)) if component_count > 0 else 0
        self.results["overall_quality_score"] = round(overall_score, 1)
        return overall_score
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []
        
        for component_name, component in self.results["validation_components"].items():
            if component["status"] == "failed":
                if component_name == "japanese_standards":
                    recommendations.append("Improve Japanese development standards compliance by adding status tags to PRPs and organizing root directory")
                elif component_name == "template_compliance":
                    recommendations.append("Fix template compliance issues by adding required sections and proper heading hierarchy")
                elif component_name == "documentation_quality":
                    recommendations.append("Address documentation quality issues by running markdownlint and quality automation")
                elif component_name == "project_cleanliness":
                    recommendations.append("Clean up project by removing temporary files and organizing build artifacts")
                elif component_name == "security_validation":
                    recommendations.append("Review and fix potential security issues in documentation")
        
        overall_score = self.results["overall_quality_score"]
        if overall_score < 70:
            recommendations.append("Overall quality score is low - prioritize fixing critical issues")
        elif overall_score < 90:
            recommendations.append("Good quality score - focus on addressing remaining issues for excellence")
        
        self.results["recommendations"] = recommendations
        return recommendations
    
    def run_full_validation(self) -> bool:
        """Run complete integrated quality validation."""
        self.logger.info("🚀 Starting Integrated Quality Validation...")
        
        # Run all validation components
        validations = [
            ("Japanese Standards", self.validate_japanese_standards),
            ("Template Compliance", self.validate_template_compliance),
            ("Documentation Quality", self.validate_documentation_quality),
            ("Project Cleanliness", self.validate_project_cleanliness),
            ("Security Validation", self.validate_security)
        ]
        
        passed_count = 0
        for name, validator in validations:
            try:
                if validator():
                    passed_count += 1
                    self.logger.info(f"✅ {name} validation passed")
                else:
                    self.logger.warning(f"❌ {name} validation failed")
            except Exception as e:
                self.logger.error(f"💥 {name} validation error: {e}")
        
        # Calculate overall score and generate recommendations
        overall_score = self.calculate_overall_score()
        recommendations = self.generate_recommendations()
        
        # Set CI/CD integration status
        self.results["ci_cd_integration_status"] = "passed" if passed_count >= 4 else "failed"
        
        # Log final results
        self.logger.info(f"📊 Overall Quality Score: {overall_score:.1f}%")
        self.logger.info(f"✅ Passed Validations: {passed_count}/5")
        
        if recommendations:
            self.logger.info("💡 Recommendations:")
            for rec in recommendations:
                self.logger.info(f"  - {rec}")
        
        return passed_count >= 4 and overall_score >= 75
    
    def save_results(self, output_file: str = "integrated-quality-report.json") -> None:
        """Save validation results to JSON file."""
        output_path = self.project_root / output_file
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.logger.info(f"📋 Results saved to {output_path}")


def main():
    """Main entry point for the integrated quality validator."""
    parser = argparse.ArgumentParser(
        description="Integrated Quality Validator for CI/CD Pipeline"
    )
    parser.add_argument(
        '--project-root',
        default='.',
        help='Project root directory (default: current directory)'
    )
    parser.add_argument(
        '--output',
        default='integrated-quality-report.json',
        help='Output file for results (default: integrated-quality-report.json)'
    )
    parser.add_argument(
        '--fail-on-issues',
        action='store_true',
        help='Exit with non-zero status if validation fails'
    )
    
    args = parser.parse_args()
    
    # Create and run validator
    validator = IntegratedQualityValidator(args.project_root)
    
    try:
        validation_passed = validator.run_full_validation()
        validator.save_results(args.output)
        
        if args.fail_on_issues and not validation_passed:
            print("❌ Integrated quality validation failed")
            sys.exit(1)
        else:
            print("✅ Integrated quality validation completed")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"💥 Unexpected error during validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()