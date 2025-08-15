#!/usr/bin/env python3
"""
Documentation Reorganization Verification Tool
Verifies that all documentation has been properly organized and is accessible.
"""

import os
from pathlib import Path

def verify_documentation_organization():
    """Verify documentation organization and accessibility."""
    
    # Expected root documentation (essential entry points)
    essential_root_docs = [
        "README.md",
        "CHANGELOG.md", 
        "CONTRIBUTING.md",
        "CLAUDE.md",
        "QUICK_START.md"
    ]
    
    # Expected organized documentation by category
    organized_docs = {
        "docs/releases/": [
            "RELEASE_NOTES.md",
            "RELEASE_CHECKLIST.md", 
            "PyPI_Release_1.6.0_Summary.md",
            "SERVER_REBOOT_CHANGELOG.md"
        ],
        "docs/testing/": [
            "TESTING_GUIDELINES.md",
            "COMPREHENSIVE_MIGRATION_TEST_REPORT.md",
            "COMPREHENSIVE_REBOOT_TEST_REPORT.md",
            "VALIDATION_REPORT.md"
        ],
        "docs/development/": [
            "IMPLEMENTATION_SUMMARY.md",
            "MIGRATION_SYSTEM_IMPLEMENTATION_SUMMARY.md", 
            "WORKTREE_SETUP.md",
            "CLEANUP_SAFETY_FRAMEWORK.md"
        ],
        "docs/troubleshooting/": [
            "TROUBLESHOOTING.md"
        ],
        "docs/user-guide/": [
            "INTEGRATION_GUIDE.md",
            "MIGRATION_GUIDE.md"
        ]
    }
    
    results = []
    
    # Verify essential root documentation
    results.append("📚 Essential Root Documentation:")
    for doc in essential_root_docs:
        if os.path.exists(doc):
            results.append(f"   ✅ {doc} - PRESENT")
        else:
            results.append(f"   ❌ {doc} - MISSING")
    
    # Verify organized documentation
    results.append("\n📁 Organized Documentation:")
    total_organized = 0
    
    for directory, expected_files in organized_docs.items():
        results.append(f"   📂 {directory}")
        if not os.path.exists(directory):
            results.append("      ❌ Directory not found")
            continue
            
        for doc in expected_files:
            full_path = os.path.join(directory, doc)
            if os.path.exists(full_path):
                results.append(f"      ✅ {doc}")
                total_organized += 1
            else:
                results.append(f"      ❌ {doc} - MISSING")
    
    # Count all documentation files
    results.append("\n📊 Documentation Statistics:")
    
    # Count markdown files in docs/
    doc_count = len(list(Path("docs").glob("**/*.md")))
    results.append(f"   Total docs/ files: {doc_count}")
    
    # Count root markdown files
    root_md_count = len(list(Path(".").glob("*.md")))
    results.append(f"   Root .md files: {root_md_count}")
    
    results.append(f"   Successfully organized: {total_organized} files")
    
    # Verify INDEX.md has been updated
    if os.path.exists("docs/INDEX.md"):
        with open("docs/INDEX.md", 'r') as f:
            index_content = f.read()
            if "releases/" in index_content and "testing/" in index_content:
                results.append("   ✅ INDEX.md updated with new organization")
            else:
                results.append("   ⚠️  INDEX.md may need updates for new sections")
    
    return results

def main():
    """Main verification function."""
    print("🔍 Documentation Reorganization Verification")
    print("=" * 55)
    
    results = verify_documentation_organization()
    
    for result in results:
        print(result)
    
    print("\n🎯 Documentation reorganization verification complete!")
    print("📈 Professional information architecture established!")

if __name__ == "__main__":
    main()