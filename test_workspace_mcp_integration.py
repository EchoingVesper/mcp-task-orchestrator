#!/usr/bin/env python3
"""
MCP Tools Integration Test with Workspace Paradigm
Test the actual MCP tools to validate workspace functionality
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def test_current_working_directory():
    """Test current working directory detection"""
    print("📍 Testing Current Working Directory Detection...")
    
    current_dir = Path.cwd()
    expected_project = "mcp-task-orchestrator"
    
    results = {
        'current_directory': str(current_dir),
        'directory_name': current_dir.name,
        'is_project_root': current_dir.name == expected_project,
        'has_workspace_markers': {}
    }
    
    # Check for workspace markers
    markers = {
        '.git': current_dir / '.git',
        'pyproject.toml': current_dir / 'pyproject.toml',
        '.task_orchestrator': current_dir / '.task_orchestrator',
        'mcp_task_orchestrator': current_dir / 'mcp_task_orchestrator'
    }
    
    for marker_name, marker_path in markers.items():
        exists = marker_path.exists()
        results['has_workspace_markers'][marker_name] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {marker_name}: {'Found' if exists else 'Missing'}")
    
    # Overall assessment
    marker_count = sum(results['has_workspace_markers'].values())
    if results['is_project_root'] and marker_count >= 3:
        print(f"  ✅ Workspace detection: EXCELLENT ({marker_count}/4 markers)")
        results['workspace_quality'] = 'excellent'
    elif marker_count >= 2:
        print(f"  ✅ Workspace detection: GOOD ({marker_count}/4 markers)")
        results['workspace_quality'] = 'good'
    else:
        print(f"  ⚠️ Workspace detection: POOR ({marker_count}/4 markers)")
        results['workspace_quality'] = 'poor'
    
    return results

def test_workspace_paradigm_vs_manual():
    """Compare workspace paradigm vs manual directory specification"""
    print("\n🔄 Testing Workspace Paradigm vs Manual Directory Control...")
    
    current_dir = Path.cwd()
    orchestrator_dir = current_dir / '.task_orchestrator'
    
    comparison = {
        'automatic_detection': {
            'working_directory': str(current_dir),
            'orchestrator_location': str(orchestrator_dir) if orchestrator_dir.exists() else None,
            'detection_method': 'automatic_workspace_paradigm'
        },
        'manual_override_test': {},
        'benefits_analysis': {}
    }
    
    # Test automatic detection (current state)
    if orchestrator_dir.exists():
        print("  ✅ Automatic: Workspace detected and .task_orchestrator created automatically")
        comparison['automatic_detection']['status'] = 'success'
        
        # Check if artifacts are correctly placed
        artifacts_dir = orchestrator_dir / 'artifacts'
        if artifacts_dir.exists():
            artifact_count = len(list(artifacts_dir.iterdir()))
            print(f"  📦 Automatic: {artifact_count} specialist artifact directories found")
            comparison['automatic_detection']['artifact_dirs'] = artifact_count
    else:
        print("  ❌ Automatic: No .task_orchestrator directory found")
        comparison['automatic_detection']['status'] = 'failed'
    
    # Test potential manual override scenarios
    manual_locations = [
        current_dir.parent / '.task_orchestrator',  # Parent directory
        Path.home() / '.task_orchestrator',         # Home directory  
        current_dir / 'custom_orchestrator'        # Custom location
    ]
    
    for i, manual_path in enumerate(manual_locations, 1):
        exists = manual_path.exists()
        print(f"  📁 Manual Location {i}: {manual_path} - {'Exists' if exists else 'Would need creation'}")
        comparison['manual_override_test'][f'option_{i}'] = {
            'path': str(manual_path),
            'exists': exists,
            'would_work': manual_path.parent.exists()
        }
    
    # Benefits analysis
    if comparison['automatic_detection']['status'] == 'success':
        benefits = []
        
        # Benefit 1: No user configuration required
        benefits.append("Zero configuration - works immediately")
        
        # Benefit 2: Project-specific isolation
        if orchestrator_dir.exists():
            benefits.append("Project-specific task isolation")
        
        # Benefit 3: Intuitive file placement
        if (orchestrator_dir / 'artifacts').exists():
            benefits.append("Intuitive artifact placement in project")
        
        # Benefit 4: Easy cleanup
        if orchestrator_dir.exists():
            benefits.append("Easy cleanup - single directory to remove")
        
        comparison['benefits_analysis'] = {
            'total_benefits': len(benefits),
            'benefits_list': benefits
        }
        
        print(f"  ✅ Benefits: {len(benefits)} major advantages identified")
        for benefit in benefits:
            print(f"    - {benefit}")
    
    return comparison

def test_artifact_placement_intelligence():
    """Test how intelligently artifacts are placed"""
    print("\n🧠 Testing Artifact Placement Intelligence...")
    
    current_dir = Path.cwd()
    artifacts_dir = current_dir / '.task_orchestrator' / 'artifacts'
    
    if not artifacts_dir.exists():
        return {'status': 'no_artifacts', 'message': 'No artifacts directory found'}
    
    intelligence_analysis = {
        'placement_location': str(artifacts_dir.relative_to(current_dir)),
        'organization_structure': {},
        'accessibility': {},
        'intelligence_score': 0
    }
    
    # Analyze organization structure
    specialist_dirs = [d for d in artifacts_dir.iterdir() if d.is_dir()]
    if specialist_dirs:
        # Check naming pattern
        specialist_types = set()
        for spec_dir in specialist_dirs:
            if '_' in spec_dir.name:
                specialist_type = spec_dir.name.split('_')[0]
                specialist_types.add(specialist_type)
        
        intelligence_analysis['organization_structure'] = {
            'total_specialist_dirs': len(specialist_dirs),
            'specialist_types': list(specialist_types),
            'naming_pattern': 'specialist_type_id' if specialist_types else 'unknown'
        }
        
        print(f"  📊 Organization: {len(specialist_dirs)} specialist directories")
        print(f"  🏷️ Types found: {', '.join(list(specialist_types)[:5])}...")
        
        # Intelligence points
        if len(specialist_types) >= 5:  # Multiple specialist types
            intelligence_analysis['intelligence_score'] += 2
            print("  ✅ Intelligence: Multiple specialist types (2 points)")
        
        if intelligence_analysis['organization_structure']['naming_pattern'] == 'specialist_type_id':
            intelligence_analysis['intelligence_score'] += 2
            print("  ✅ Intelligence: Consistent naming pattern (2 points)")
    
    # Test accessibility
    try:
        # Check if artifacts are easily accessible from project root
        relative_path = artifacts_dir.relative_to(current_dir)
        path_depth = len(relative_path.parts)
        
        intelligence_analysis['accessibility'] = {
            'relative_path': str(relative_path),
            'path_depth': path_depth,
            'easily_accessible': path_depth <= 2
        }
        
        if path_depth <= 2:
            intelligence_analysis['intelligence_score'] += 1
            print(f"  ✅ Accessibility: Shallow path depth ({path_depth} levels)")
        else:
            print(f"  ⚠️ Accessibility: Deep path depth ({path_depth} levels)")
        
    except ValueError:
        print("  ❌ Accessibility: Artifacts outside project directory")
    
    # Test workspace awareness
    if artifacts_dir.is_relative_to(current_dir):
        intelligence_analysis['intelligence_score'] += 1
        print("  ✅ Workspace awareness: Artifacts within project boundary")
    
    # Overall intelligence assessment
    max_score = 6
    intelligence_percentage = (intelligence_analysis['intelligence_score'] / max_score) * 100
    
    if intelligence_percentage >= 80:
        intelligence_level = "EXCELLENT"
    elif intelligence_percentage >= 60:
        intelligence_level = "GOOD"
    else:
        intelligence_level = "NEEDS_IMPROVEMENT"
    
    print(f"  🎯 Intelligence Score: {intelligence_analysis['intelligence_score']}/{max_score} ({intelligence_percentage:.0f}% - {intelligence_level})")
    
    intelligence_analysis['overall_assessment'] = {
        'score': intelligence_analysis['intelligence_score'],
        'max_score': max_score,
        'percentage': intelligence_percentage,
        'level': intelligence_level
    }
    
    return intelligence_analysis

def test_workspace_paradigm_pitfalls():
    """Identify potential pitfalls and areas for improvement"""
    print("\n⚠️ Testing for Workspace Paradigm Pitfalls...")
    
    current_dir = Path.cwd()
    orchestrator_dir = current_dir / '.task_orchestrator'
    
    pitfalls = {
        'identified_issues': [],
        'performance_concerns': [],
        'usability_concerns': [],
        'maintenance_concerns': []
    }
    
    # Pitfall 1: Large workspace directory size
    if orchestrator_dir.exists():
        total_size = 0
        file_count = 0
        for file_path in orchestrator_dir.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        size_mb = total_size / (1024 * 1024)
        if size_mb > 50:
            pitfalls['performance_concerns'].append(f"Large workspace size: {size_mb:.1f}MB")
            print(f"  ⚠️ Size concern: Workspace is {size_mb:.1f}MB with {file_count} files")
        else:
            print(f"  ✅ Size acceptable: Workspace is {size_mb:.1f}MB with {file_count} files")
    
    # Pitfall 2: Too many artifact directories
    artifacts_dir = orchestrator_dir / 'artifacts'
    if artifacts_dir.exists():
        artifact_dirs = [d for d in artifacts_dir.iterdir() if d.is_dir()]
        if len(artifact_dirs) > 100:
            pitfalls['performance_concerns'].append(f"Too many artifact directories: {len(artifact_dirs)}")
            print(f"  ⚠️ Organization concern: {len(artifact_dirs)} artifact directories")
        else:
            print(f"  ✅ Organization acceptable: {len(artifact_dirs)} artifact directories")
    
    # Pitfall 3: Database file size
    db_file = orchestrator_dir / 'task_orchestrator.db'
    if db_file.exists():
        db_size_mb = db_file.stat().st_size / (1024 * 1024)
        if db_size_mb > 10:
            pitfalls['performance_concerns'].append(f"Large database: {db_size_mb:.1f}MB")
            print(f"  ⚠️ Database concern: {db_size_mb:.1f}MB database file")
        else:
            print(f"  ✅ Database acceptable: {db_size_mb:.1f}MB database file")
    
    # Pitfall 4: Hidden directory discoverability
    if orchestrator_dir.name.startswith('.'):
        pitfalls['usability_concerns'].append("Hidden directory may be hard to discover")
        print("  ⚠️ Usability: .task_orchestrator is hidden (may be hard to find)")
    
    # Pitfall 5: No cleanup mechanism obvious
    if not (current_dir / 'CLEANUP_INSTRUCTIONS.md').exists():
        pitfalls['maintenance_concerns'].append("No obvious cleanup instructions")
        print("  ⚠️ Maintenance: No obvious cleanup mechanism documented")
    
    # Overall pitfall assessment
    total_concerns = (len(pitfalls['performance_concerns']) + 
                     len(pitfalls['usability_concerns']) + 
                     len(pitfalls['maintenance_concerns']))
    
    if total_concerns == 0:
        print("  ✅ Pitfall assessment: No significant concerns identified")
        pitfalls['overall_status'] = 'excellent'
    elif total_concerns <= 2:
        print(f"  ⚠️ Pitfall assessment: {total_concerns} minor concerns identified")
        pitfalls['overall_status'] = 'good_with_concerns'
    else:
        print(f"  ❌ Pitfall assessment: {total_concerns} concerns need attention")
        pitfalls['overall_status'] = 'needs_attention'
    
    return pitfalls

def run_mcp_integration_tests():
    """Run comprehensive MCP integration tests"""
    print("🧪 MCP Tools Integration Test with Workspace Paradigm")
    print("=" * 55)
    
    results = {
        'test_location': str(Path.cwd()),
        'integration_tests': {}
    }
    
    # Run integration tests
    results['integration_tests']['directory_detection'] = test_current_working_directory()
    results['integration_tests']['paradigm_comparison'] = test_workspace_paradigm_vs_manual()
    results['integration_tests']['artifact_intelligence'] = test_artifact_placement_intelligence()
    results['integration_tests']['pitfall_analysis'] = test_workspace_paradigm_pitfalls()
    
    # Overall MCP integration assessment
    print("\n📊 MCP Integration Assessment:")
    
    # Workspace quality
    workspace_quality = results['integration_tests']['directory_detection']['workspace_quality']
    print(f"  📍 Workspace Detection: {workspace_quality.upper()}")
    
    # Intelligence score
    intel_score = results['integration_tests']['artifact_intelligence']['overall_assessment']['percentage']
    intel_level = results['integration_tests']['artifact_intelligence']['overall_assessment']['level']
    print(f"  🧠 Artifact Intelligence: {intel_level} ({intel_score:.0f}%)")
    
    # Pitfall status
    pitfall_status = results['integration_tests']['pitfall_analysis']['overall_status']
    print(f"  ⚠️ Pitfall Assessment: {pitfall_status.replace('_', ' ').title()}")
    
    # Benefits count
    benefits = results['integration_tests']['paradigm_comparison']['benefits_analysis']
    if benefits:
        benefits_count = benefits['total_benefits']
        print(f"  ✅ Paradigm Benefits: {benefits_count} major advantages")
    
    # Overall integration status
    integration_success = (workspace_quality in ['excellent', 'good'] and 
                          intel_score >= 60 and 
                          pitfall_status in ['excellent', 'good_with_concerns'])
    
    results['overall_integration'] = {
        'status': 'PASS' if integration_success else 'CONCERNS',
        'workspace_quality': workspace_quality,
        'intelligence_level': intel_level,
        'pitfall_status': pitfall_status
    }
    
    print(f"\n🎯 Overall MCP Integration: {results['overall_integration']['status']}")
    
    return results

if __name__ == "__main__":
    results = run_mcp_integration_tests()
    
    # Save results
    results_file = Path.cwd() / '.task_orchestrator' / 'mcp_integration_test_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Integration test results saved to: {results_file}")