#!/usr/bin/env python3
"""
Workspace Paradigm Functionality Test Suite
Test script to validate workspace detection and functionality
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

def test_project_markers():
    """Test that the current directory has proper project markers"""
    print("🔍 Testing Project Markers...")
    current_dir = Path.cwd()
    
    expected_markers = {
        'pyproject.toml': 'Python project configuration',
        'setup.py': 'Python package setup', 
        '.git': 'Git repository',
        'README.md': 'Project documentation',
        'requirements.txt': 'Python dependencies'
    }
    
    found_markers = {}
    missing_markers = {}
    
    for marker, description in expected_markers.items():
        marker_path = current_dir / marker
        if marker_path.exists():
            found_markers[marker] = description
            print(f"  ✅ Found {marker} - {description}")
        else:
            missing_markers[marker] = description
            print(f"  ❌ Missing {marker} - {description}")
    
    return {
        'found': found_markers,
        'missing': missing_markers,
        'detection_confidence': len(found_markers) / len(expected_markers) * 100
    }

def test_workspace_structure():
    """Test that .task_orchestrator directory has proper structure"""
    print("\n🏗️ Testing Workspace Structure...")
    orchestrator_dir = Path.cwd() / '.task_orchestrator'
    
    if not orchestrator_dir.exists():
        print("  ❌ .task_orchestrator directory not found!")
        return {'exists': False}
    
    expected_structure = {
        'artifacts': 'Task artifacts storage',
        'logs': 'Server logs', 
        'roles': 'Role configurations',
        'server_state': 'Server state files',
        'task_orchestrator.db': 'Main database'
    }
    
    structure_results = {'exists': True, 'components': {}}
    
    for component, description in expected_structure.items():
        component_path = orchestrator_dir / component
        exists = component_path.exists()
        structure_results['components'][component] = {
            'exists': exists,
            'description': description,
            'path': str(component_path)
        }
        status = "✅" if exists else "❌"
        print(f"  {status} {component} - {description}")
    
    return structure_results

def test_database_connectivity():
    """Test database connectivity and basic queries"""
    print("\n💾 Testing Database Connectivity...")
    try:
        import sqlite3
        db_path = Path.cwd() / '.task_orchestrator' / 'task_orchestrator.db'
        
        if not db_path.exists():
            print("  ❌ Database file not found!")
            return {'accessible': False, 'error': 'Database file missing'}
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Test basic schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"  ✅ Database accessible with {len(tables)} tables")
        print(f"  📋 Tables: {', '.join(tables)}")
        
        # Test workspace-aware features
        workspace_tables = [t for t in tables if 'workspace' in t.lower()]
        if workspace_tables:
            print(f"  ✅ Workspace-aware tables found: {', '.join(workspace_tables)}")
        else:
            print("  ⚠️ No explicit workspace tables found (may use different naming)")
        
        conn.close()
        return {
            'accessible': True,
            'tables': tables,
            'workspace_tables': workspace_tables
        }
        
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return {'accessible': False, 'error': str(e)}

def test_directory_detection_logic():
    """Test the directory detection logic directly"""
    print("\n🎯 Testing Directory Detection Logic...")
    
    try:
        # Try to import and test the directory detection
        sys.path.insert(0, str(Path.cwd() / 'mcp_task_orchestrator'))
        from orchestrator.directory_detection import DirectoryDetector
        
        detector = DirectoryDetector()
        result = detector.detect_project_root()
        
        print(f"  ✅ Detection successful!")
        print(f"  📍 Detected path: {result.detected_path}")
        print(f"  🔧 Method used: {result.method.value}")
        print(f"  📊 Confidence: {result.confidence}/10")
        print(f"  ⏱️ Detection time: {result.detection_time_ms:.2f}ms")
        print(f"  ✅ Valid: {result.validation.is_valid}")
        print(f"  ✏️ Writable: {result.validation.is_writable}")
        
        if result.project_markers:
            print(f"  🏷️ Project markers found:")
            for marker in result.project_markers[:3]:  # Show top 3
                print(f"    - {marker.file_path.name} ({marker.marker_type}, confidence: {marker.confidence})")
        
        if result.git_root:
            print(f"  📂 Git root: {result.git_root}")
        
        return {
            'detection_successful': True,
            'detected_path': str(result.detected_path),
            'method': result.method.value,
            'confidence': result.confidence,
            'detection_time_ms': result.detection_time_ms,
            'validation': {
                'valid': result.validation.is_valid,
                'writable': result.validation.is_writable,
                'exists': result.validation.exists
            },
            'markers_count': len(result.project_markers),
            'git_root': str(result.git_root) if result.git_root else None
        }
        
    except ImportError as e:
        print(f"  ❌ Could not import directory detection: {e}")
        return {'detection_successful': False, 'error': 'Import failed'}
    except Exception as e:
        print(f"  ❌ Detection failed: {e}")
        return {'detection_successful': False, 'error': str(e)}

def test_workspace_paradigm_benefits():
    """Test specific workspace paradigm benefits"""
    print("\n🎯 Testing Workspace Paradigm Benefits...")
    
    benefits_test = {
        'artifact_placement': False,
        'project_awareness': False,
        'automatic_detection': False,
        'workspace_isolation': False
    }
    
    # Test artifact placement
    artifacts_dir = Path.cwd() / '.task_orchestrator' / 'artifacts'
    if artifacts_dir.exists():
        artifacts = list(artifacts_dir.glob('*'))
        if artifacts:
            print(f"  ✅ Smart artifact placement: {len(artifacts)} artifacts in workspace")
            benefits_test['artifact_placement'] = True
        else:
            print("  ⚠️ Artifacts directory exists but empty")
    else:
        print("  ❌ No artifacts directory found")
    
    # Test project awareness
    current_path = Path.cwd()
    if current_path.name == 'mcp-task-orchestrator' and (current_path / 'pyproject.toml').exists():
        print("  ✅ Project awareness: Correctly identified as MCP Task Orchestrator project")
        benefits_test['project_awareness'] = True
    else:
        print("  ⚠️ Project awareness: May not have correctly identified project type")
    
    # Test automatic detection (implicit from structure existence)
    if (current_path / '.task_orchestrator').exists():
        print("  ✅ Automatic detection: Workspace created without manual intervention")
        benefits_test['automatic_detection'] = True
    else:
        print("  ❌ Automatic detection: Workspace not automatically created")
    
    # Test workspace isolation
    workspace_db = current_path / '.task_orchestrator' / 'task_orchestrator.db'
    if workspace_db.exists():
        print("  ✅ Workspace isolation: Project has its own task database")
        benefits_test['workspace_isolation'] = True
    else:
        print("  ❌ Workspace isolation: No isolated task database found")
    
    return benefits_test

def run_comprehensive_test():
    """Run all workspace functionality tests"""
    print("🧪 Workspace Paradigm Functionality Test Suite")
    print("=" * 50)
    
    results = {
        'test_timestamp': str(Path.cwd()),
        'working_directory': str(Path.cwd()),
        'tests': {}
    }
    
    # Run all tests
    results['tests']['project_markers'] = test_project_markers()
    results['tests']['workspace_structure'] = test_workspace_structure()
    results['tests']['database_connectivity'] = test_database_connectivity()
    results['tests']['directory_detection'] = test_directory_detection_logic()
    results['tests']['paradigm_benefits'] = test_workspace_paradigm_benefits()
    
    # Overall assessment
    print("\n📊 Overall Assessment:")
    
    total_tests = 0
    passed_tests = 0
    
    # Count passed tests
    if results['tests']['project_markers']['detection_confidence'] >= 80:
        passed_tests += 1
        print("  ✅ Project marker detection: PASS")
    else:
        print("  ❌ Project marker detection: FAIL")
    total_tests += 1
    
    if results['tests']['workspace_structure']['exists']:
        passed_tests += 1
        print("  ✅ Workspace structure: PASS")
    else:
        print("  ❌ Workspace structure: FAIL")
    total_tests += 1
    
    if results['tests']['database_connectivity']['accessible']:
        passed_tests += 1
        print("  ✅ Database connectivity: PASS")
    else:
        print("  ❌ Database connectivity: FAIL")
    total_tests += 1
    
    if results['tests']['directory_detection']['detection_successful']:
        passed_tests += 1
        print("  ✅ Directory detection: PASS")
    else:
        print("  ❌ Directory detection: FAIL")
    total_tests += 1
    
    benefits_passed = sum(results['tests']['paradigm_benefits'].values())
    if benefits_passed >= 3:
        passed_tests += 1
        print(f"  ✅ Paradigm benefits: PASS ({benefits_passed}/4 benefits working)")
    else:
        print(f"  ❌ Paradigm benefits: FAIL ({benefits_passed}/4 benefits working)")
    total_tests += 1
    
    results['overall'] = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'success_rate': passed_tests / total_tests * 100,
        'status': 'PASS' if passed_tests >= 4 else 'FAIL'
    }
    
    print(f"\n🎯 Test Results: {passed_tests}/{total_tests} tests passed")
    print(f"Overall Status: {results['overall']['status']}")
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_test()
    
    # Save results to file
    results_file = Path.cwd() / '.task_orchestrator' / 'workspace_test_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Test results saved to: {results_file}")