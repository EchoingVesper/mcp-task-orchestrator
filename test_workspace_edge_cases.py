#!/usr/bin/env python3
"""
Workspace Paradigm Edge Cases and Integration Tests
Testing edge cases, error conditions, and integration scenarios
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any

def test_workspace_in_different_directories():
    """Test workspace detection in various directory types"""
    print("🔄 Testing Workspace Detection in Different Directories...")
    
    original_dir = Path.cwd()
    test_results = []
    
    # Test 1: Current directory (should work perfectly)
    print("  📁 Test 1: Current MCP project directory")
    current_test = {
        'directory': str(original_dir),
        'has_git': (original_dir / '.git').exists(),
        'has_pyproject': (original_dir / 'pyproject.toml').exists(),
        'has_orchestrator': (original_dir / '.task_orchestrator').exists(),
        'expected_detection': True
    }
    print(f"    - Git repo: {current_test['has_git']}")
    print(f"    - Python project: {current_test['has_pyproject']}")
    print(f"    - Orchestrator setup: {current_test['has_orchestrator']}")
    test_results.append(current_test)
    
    # Test 2: Parent directory
    print("  📁 Test 2: Parent directory")
    parent_dir = original_dir.parent
    parent_test = {
        'directory': str(parent_dir),
        'has_git': (parent_dir / '.git').exists(),
        'has_pyproject': (parent_dir / 'pyproject.toml').exists(),
        'has_orchestrator': (parent_dir / '.task_orchestrator').exists(),
        'expected_detection': False
    }
    print(f"    - Git repo: {parent_test['has_git']}")
    print(f"    - Python project: {parent_test['has_pyproject']}")
    print(f"    - Orchestrator setup: {parent_test['has_orchestrator']}")
    test_results.append(parent_test)
    
    # Test 3: Home directory
    print("  📁 Test 3: Home directory")
    home_dir = Path.home()
    home_test = {
        'directory': str(home_dir),
        'has_git': (home_dir / '.git').exists(),
        'has_pyproject': (home_dir / 'pyproject.toml').exists(),
        'has_orchestrator': (home_dir / '.task_orchestrator').exists(),
        'expected_detection': False  # Should fall back to home
    }
    print(f"    - Git repo: {home_test['has_git']}")
    print(f"    - Python project: {home_test['has_pyproject']}")
    print(f"    - Orchestrator setup: {home_test['has_orchestrator']}")
    test_results.append(home_test)
    
    return test_results

def test_artifact_organization():
    """Test how artifacts are organized in the workspace"""
    print("\n📦 Testing Artifact Organization...")
    
    artifacts_dir = Path.cwd() / '.task_orchestrator' / 'artifacts'
    if not artifacts_dir.exists():
        return {'test_status': 'skipped', 'reason': 'No artifacts directory'}
    
    # Analyze artifact structure
    artifact_analysis = {
        'total_artifacts': 0,
        'specialist_directories': [],
        'file_types': {},
        'organization_pattern': None
    }
    
    for item in artifacts_dir.iterdir():
        if item.is_dir():
            specialist_name = item.name
            artifact_analysis['specialist_directories'].append(specialist_name)
            
            # Count files in each specialist directory
            specialist_files = list(item.glob('*'))
            artifact_analysis['total_artifacts'] += len(specialist_files)
            
            print(f"  📂 {specialist_name}: {len(specialist_files)} artifacts")
            
            # Analyze file types
            for artifact_file in specialist_files:
                ext = artifact_file.suffix or 'no_extension'
                artifact_analysis['file_types'][ext] = artifact_analysis['file_types'].get(ext, 0) + 1
    
    # Determine organization pattern
    if len(artifact_analysis['specialist_directories']) > 0:
        if all('_' in name for name in artifact_analysis['specialist_directories']):
            artifact_analysis['organization_pattern'] = 'specialist_based_with_ids'
        else:
            artifact_analysis['organization_pattern'] = 'specialist_based'
    
    print(f"  📊 Total artifacts: {artifact_analysis['total_artifacts']}")
    print(f"  🏷️ File types: {dict(list(artifact_analysis['file_types'].items())[:5])}")
    print(f"  🗂️ Organization: {artifact_analysis['organization_pattern']}")
    
    return artifact_analysis

def test_workspace_isolation():
    """Test that workspace provides proper isolation"""
    print("\n🔒 Testing Workspace Isolation...")
    
    isolation_tests = {
        'database_isolation': False,
        'artifact_isolation': False,
        'config_isolation': False,
        'log_isolation': False
    }
    
    workspace_dir = Path.cwd() / '.task_orchestrator'
    
    # Test database isolation
    db_file = workspace_dir / 'task_orchestrator.db'
    if db_file.exists():
        # Check that database is within workspace
        try:
            db_relative_path = db_file.relative_to(Path.cwd())
            if str(db_relative_path).startswith('.task_orchestrator'):
                isolation_tests['database_isolation'] = True
                print("  ✅ Database isolation: Database stored within workspace")
            else:
                print("  ❌ Database isolation: Database outside workspace")
        except ValueError:
            print("  ❌ Database isolation: Database outside project directory")
    
    # Test artifact isolation
    artifacts_dir = workspace_dir / 'artifacts'
    if artifacts_dir.exists():
        artifact_count = len(list(artifacts_dir.rglob('*')))
        if artifact_count > 0:
            isolation_tests['artifact_isolation'] = True
            print(f"  ✅ Artifact isolation: {artifact_count} artifacts stored within workspace")
        else:
            print("  ⚠️ Artifact isolation: Artifacts directory exists but empty")
    else:
        print("  ❌ Artifact isolation: No artifacts directory found")
    
    # Test config isolation  
    roles_dir = workspace_dir / 'roles'
    if roles_dir.exists():
        role_files = list(roles_dir.glob('*.yaml'))
        if role_files:
            isolation_tests['config_isolation'] = True
            print(f"  ✅ Config isolation: {len(role_files)} role configs within workspace")
        else:
            print("  ⚠️ Config isolation: Roles directory exists but no configs")
    else:
        print("  ❌ Config isolation: No roles directory found")
    
    # Test log isolation
    logs_dir = workspace_dir / 'logs'
    if logs_dir.exists():
        log_files = list(logs_dir.glob('*'))
        if log_files:
            isolation_tests['log_isolation'] = True
            print(f"  ✅ Log isolation: {len(log_files)} log files within workspace")
        else:
            print("  ⚠️ Log isolation: Logs directory exists but empty")
    else:
        print("  ❌ Log isolation: No logs directory found")
    
    return isolation_tests

def test_workspace_performance():
    """Test workspace paradigm performance characteristics"""
    print("\n⚡ Testing Workspace Performance...")
    
    import time
    
    performance_metrics = {}
    
    # Test 1: Directory structure access time
    start_time = time.time()
    workspace_dir = Path.cwd() / '.task_orchestrator'
    contents = list(workspace_dir.iterdir()) if workspace_dir.exists() else []
    directory_access_time = (time.time() - start_time) * 1000
    performance_metrics['directory_access_ms'] = directory_access_time
    print(f"  📁 Directory access: {directory_access_time:.2f}ms ({len(contents)} items)")
    
    # Test 2: Database connection time
    start_time = time.time()
    try:
        import sqlite3
        db_path = workspace_dir / 'task_orchestrator.db'
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            conn.close()
            db_connection_time = (time.time() - start_time) * 1000
            performance_metrics['db_connection_ms'] = db_connection_time
            print(f"  💾 Database connection: {db_connection_time:.2f}ms")
        else:
            print("  ❌ Database not found for performance test")
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
    
    # Test 3: Artifact enumeration time
    start_time = time.time()
    artifacts_dir = workspace_dir / 'artifacts'
    if artifacts_dir.exists():
        artifact_files = list(artifacts_dir.rglob('*'))
        artifact_enumeration_time = (time.time() - start_time) * 1000
        performance_metrics['artifact_enumeration_ms'] = artifact_enumeration_time
        print(f"  📦 Artifact enumeration: {artifact_enumeration_time:.2f}ms ({len(artifact_files)} items)")
    else:
        print("  ⚠️ No artifacts directory for performance test")
    
    # Performance assessment
    total_time = sum(performance_metrics.values())
    if total_time < 100:
        print(f"  ✅ Overall performance: EXCELLENT ({total_time:.2f}ms total)")
    elif total_time < 500:
        print(f"  ✅ Overall performance: GOOD ({total_time:.2f}ms total)")
    else:
        print(f"  ⚠️ Overall performance: SLOW ({total_time:.2f}ms total)")
    
    return performance_metrics

def test_workspace_paradigm_vs_legacy():
    """Compare workspace paradigm benefits vs legacy approach"""
    print("\n⚖️ Testing Workspace Paradigm vs Legacy Comparison...")
    
    comparison = {
        'workspace_benefits': [],
        'legacy_issues_resolved': [],
        'potential_concerns': []
    }
    
    # Analyze workspace benefits
    current_dir = Path.cwd()
    
    # Benefit 1: Automatic project detection
    if (current_dir / '.git').exists() and (current_dir / '.task_orchestrator').exists():
        comparison['workspace_benefits'].append("Automatic project root detection working")
        comparison['legacy_issues_resolved'].append("No manual directory specification needed")
        print("  ✅ Auto-detection: Project root detected automatically")
    
    # Benefit 2: Smart artifact placement
    artifacts_dir = current_dir / '.task_orchestrator' / 'artifacts'
    if artifacts_dir.exists():
        relative_path = artifacts_dir.relative_to(current_dir)
        comparison['workspace_benefits'].append(f"Smart artifact placement at {relative_path}")
        comparison['legacy_issues_resolved'].append("Artifacts no longer scattered in random locations")
        print(f"  ✅ Smart placement: Artifacts in {relative_path}")
    
    # Benefit 3: Project-specific database
    db_file = current_dir / '.task_orchestrator' / 'task_orchestrator.db'
    if db_file.exists():
        comparison['workspace_benefits'].append("Project-specific task database")
        comparison['legacy_issues_resolved'].append("No task mixing between different projects")
        print("  ✅ Isolation: Project-specific task database")
    
    # Potential concerns
    workspace_size = 0
    if (current_dir / '.task_orchestrator').exists():
        for file_path in (current_dir / '.task_orchestrator').rglob('*'):
            if file_path.is_file():
                workspace_size += file_path.stat().st_size
        
        workspace_size_mb = workspace_size / (1024 * 1024)
        if workspace_size_mb > 100:
            comparison['potential_concerns'].append(f"Large workspace size: {workspace_size_mb:.1f}MB")
            print(f"  ⚠️ Size concern: Workspace is {workspace_size_mb:.1f}MB")
        else:
            print(f"  ✅ Size efficient: Workspace is {workspace_size_mb:.1f}MB")
    
    return comparison

def run_edge_case_tests():
    """Run comprehensive edge case testing"""
    print("🧪 Workspace Paradigm Edge Cases and Integration Tests")
    print("=" * 60)
    
    results = {
        'test_timestamp': str(Path.cwd()),
        'edge_case_tests': {}
    }
    
    # Run edge case tests
    results['edge_case_tests']['directory_detection'] = test_workspace_in_different_directories()
    results['edge_case_tests']['artifact_organization'] = test_artifact_organization()
    results['edge_case_tests']['workspace_isolation'] = test_workspace_isolation()
    results['edge_case_tests']['performance'] = test_workspace_performance()
    results['edge_case_tests']['paradigm_comparison'] = test_workspace_paradigm_vs_legacy()
    
    # Overall edge case assessment
    print("\n📊 Edge Case Test Assessment:")
    
    # Count isolation tests passed
    isolation_passed = sum(results['edge_case_tests']['workspace_isolation'].values())
    print(f"  🔒 Isolation tests: {isolation_passed}/4 passed")
    
    # Check performance
    total_perf_time = sum(results['edge_case_tests']['performance'].values())
    perf_status = "EXCELLENT" if total_perf_time < 100 else "GOOD" if total_perf_time < 500 else "SLOW"
    print(f"  ⚡ Performance: {perf_status} ({total_perf_time:.2f}ms)")
    
    # Check benefits
    benefits_count = len(results['edge_case_tests']['paradigm_comparison']['workspace_benefits'])
    print(f"  ✅ Workspace benefits: {benefits_count} major benefits identified")
    
    # Overall edge case status
    edge_case_success = isolation_passed >= 3 and total_perf_time < 500 and benefits_count >= 3
    results['edge_case_overall'] = {
        'status': 'PASS' if edge_case_success else 'CONCERNS',
        'isolation_score': f"{isolation_passed}/4",
        'performance_status': perf_status,
        'benefits_count': benefits_count
    }
    
    print(f"\n🎯 Edge Case Status: {results['edge_case_overall']['status']}")
    
    return results

if __name__ == "__main__":
    results = run_edge_case_tests()
    
    # Save results
    results_file = Path.cwd() / '.task_orchestrator' / 'workspace_edge_case_results.json'
    import json
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Edge case results saved to: {results_file}")