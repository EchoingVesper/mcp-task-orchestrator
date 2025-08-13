#!/usr/bin/env python3
"""
Comprehensive documentation quality automation script.
Integrates markdownlint, Vale prose linting, and hyperlink validation.
"""

import os
import sys
import subprocess
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import time

class QualityGate:
    """Documentation quality gate runner."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.docs_path = self.project_root / "docs"
        self.results = {
            "markdownlint": {"passed": False, "errors": [], "warnings": []},
            "vale": {"passed": False, "errors": [], "warnings": []},
            "hyperlinks": {"passed": False, "errors": [], "warnings": []},
            "code_examples": {"passed": False, "errors": [], "warnings": []}
        }
    
    def run_command(self, cmd: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd or self.project_root,
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result
        except subprocess.TimeoutExpired:
            print(f"Command timed out: {' '.join(cmd)}")
            return subprocess.CompletedProcess(cmd, 1, "", "Timeout expired")
    
    def check_markdownlint(self) -> bool:
        """Run markdownlint on all markdown files."""
        print("🔍 Running markdownlint...")
        
        # Check if markdownlint is available
        check_cmd = ["markdownlint", "--version"]
        result = self.run_command(check_cmd)
        
        if result.returncode != 0:
            print("⚠️  markdownlint not found. Install with: npm install -g markdownlint-cli")
            self.results["markdownlint"]["errors"].append("markdownlint not installed")
            return False
        
        # Run markdownlint on docs directory
        lint_cmd = ["markdownlint", "--config", ".markdownlint.json", "docs/", "*.md"]
        result = self.run_command(lint_cmd)
        
        if result.returncode == 0:
            print("✅ markdownlint passed")
            self.results["markdownlint"]["passed"] = True
            return True
        else:
            print("❌ markdownlint failed")
            for line in result.stdout.split('\n'):
                if line.strip():
                    self.results["markdownlint"]["errors"].append(line.strip())
            return False
    
    def check_vale(self) -> bool:
        """Run Vale prose linting."""
        print("📝 Running Vale prose linting...")
        
        # Check if Vale is available
        check_cmd = ["vale", "--version"]
        result = self.run_command(check_cmd)
        
        if result.returncode != 0:
            print("⚠️  Vale not found. Install from: https://vale.sh/docs/vale-cli/installation/")
            self.results["vale"]["warnings"].append("Vale not installed")
            return True  # Non-blocking for now
        
        # Run Vale on docs directory
        vale_cmd = ["vale", "docs/"]
        result = self.run_command(vale_cmd)
        
        # Vale returns different codes for different severity levels
        if result.returncode == 0:
            print("✅ Vale passed")
            self.results["vale"]["passed"] = True
            return True
        elif result.returncode == 1:
            print("⚠️  Vale found style suggestions")
            for line in result.stdout.split('\n'):
                if line.strip() and "suggestion" in line.lower():
                    self.results["vale"]["warnings"].append(line.strip())
            self.results["vale"]["passed"] = True  # Suggestions don't fail the gate
            return True
        else:
            print("❌ Vale found errors")
            for line in result.stdout.split('\n'):
                if line.strip():
                    self.results["vale"]["errors"].append(line.strip())
            return False
    
    def check_hyperlinks(self) -> bool:
        """Check for broken hyperlinks."""
        print("🔗 Checking hyperlinks...")
        
        # Simple implementation using grep and basic validation
        # For production, consider using tools like linkchecker or markdown-link-check
        
        md_files = list(self.docs_path.rglob("*.md"))
        broken_links = []
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for relative links that might be broken
                import re
                relative_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                
                for link_text, link_url in relative_links:
                    if link_url.startswith(('http://', 'https://')):
                        continue  # Skip external links for now
                    
                    if link_url.startswith('#'):
                        continue  # Skip anchor links for now
                    
                    # Check if relative file exists
                    if link_url.startswith('/'):
                        target_path = self.project_root / link_url.lstrip('/')
                    else:
                        target_path = md_file.parent / link_url
                    
                    if not target_path.exists():
                        broken_links.append(f"{md_file.relative_to(self.project_root)}: {link_url}")
            
            except Exception as e:
                self.results["hyperlinks"]["warnings"].append(f"Error reading {md_file}: {e}")
        
        if broken_links:
            print(f"❌ Found {len(broken_links)} broken links")
            self.results["hyperlinks"]["errors"] = broken_links
            return False
        else:
            print("✅ Hyperlink check passed")
            self.results["hyperlinks"]["passed"] = True
            return True
    
    def check_code_examples(self) -> bool:
        """Validate code examples in documentation."""
        print("💻 Checking code examples...")
        
        md_files = list(self.docs_path.rglob("*.md"))
        issues = []
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for unlabeled code blocks
                import re
                unlabeled_blocks = re.findall(r'```\s*\n', content)
                if unlabeled_blocks:
                    issues.append(f"{md_file.relative_to(self.project_root)}: {len(unlabeled_blocks)} unlabeled code blocks")
                
                # Check for Python code syntax (basic validation)
                python_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
                for i, block in enumerate(python_blocks):
                    try:
                        compile(block, f"{md_file}:block_{i}", 'exec')
                    except SyntaxError as e:
                        issues.append(f"{md_file.relative_to(self.project_root)}: Python syntax error in block {i}: {e}")
            
            except Exception as e:
                self.results["code_examples"]["warnings"].append(f"Error checking {md_file}: {e}")
        
        if issues:
            print(f"⚠️  Found {len(issues)} code example issues")
            self.results["code_examples"]["warnings"] = issues
            self.results["code_examples"]["passed"] = True  # Warnings don't fail the gate
            return True
        else:
            print("✅ Code examples check passed")
            self.results["code_examples"]["passed"] = True
            return True
    
    def run_all_checks(self) -> bool:
        """Run all quality checks."""
        print("🚀 Starting documentation quality checks...\n")
        start_time = time.time()
        
        all_passed = True
        
        # Run each check
        checks = [
            ("Markdown Lint", self.check_markdownlint),
            ("Vale Prose Linting", self.check_vale),
            ("Hyperlink Validation", self.check_hyperlinks),
            ("Code Examples", self.check_code_examples)
        ]
        
        for check_name, check_func in checks:
            print(f"\n--- {check_name} ---")
            try:
                passed = check_func()
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"❌ {check_name} failed with exception: {e}")
                all_passed = False
        
        # Generate summary
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{'='*50}")
        print("📊 QUALITY GATE SUMMARY")
        print(f"{'='*50}")
        print(f"⏱️  Total time: {duration:.2f} seconds")
        
        for gate_name, gate_result in self.results.items():
            status = "✅ PASS" if gate_result["passed"] else "❌ FAIL"
            error_count = len(gate_result["errors"])
            warning_count = len(gate_result["warnings"])
            print(f"{status} {gate_name.replace('_', ' ').title()}: {error_count} errors, {warning_count} warnings")
        
        if all_passed:
            print("\n🎉 All quality gates passed!")
        else:
            print("\n🚨 Some quality gates failed. See details above.")
        
        return all_passed
    
    def generate_report(self, output_file: str = "quality_report.json"):
        """Generate a detailed quality report."""
        # Ensure the output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "timestamp": time.time(),
            "summary": {
                "total_gates": len(self.results),
                "passed_gates": sum(1 for r in self.results.values() if r["passed"]),
                "total_errors": sum(len(r["errors"]) for r in self.results.values()),
                "total_warnings": sum(len(r["warnings"]) for r in self.results.values())
            },
            "detailed_results": self.results
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Detailed report saved to {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Documentation quality automation")
    parser.add_argument("--check", choices=["all", "lint", "vale", "links", "code"], 
                       default="all", help="Which checks to run")
    parser.add_argument("--report", help="Generate JSON report to file")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    gate = QualityGate(args.project_root)
    
    if args.check == "all":
        success = gate.run_all_checks()
    elif args.check == "lint":
        success = gate.check_markdownlint()
    elif args.check == "vale":
        success = gate.check_vale()
    elif args.check == "links":
        success = gate.check_hyperlinks()
    elif args.check == "code":
        success = gate.check_code_examples()
    
    if args.report:
        gate.generate_report(args.report)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()