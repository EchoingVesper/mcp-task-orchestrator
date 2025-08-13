#!/usr/bin/env python3
"""
Simple PyPI Upload Script
For uploading already-built packages to PyPI
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / '.env')


def upload_to_pypi(test: bool = False):
    """Upload existing packages to PyPI"""
    token = os.getenv('PYPI_TEST_TOKEN' if test else 'PYPI_API_TOKEN')
    
    if not token:
        print(f"❌ {'Test' if test else ''}PyPI token not found!")
        print("\nTo set up your token:")
        print("1. Copy .env.example to .env")
        print("2. Add your PyPI token to the .env file")
        print("3. Get your token from: https://pypi.org/manage/account/token/")
        sys.exit(1)
    
    dist_dir = PROJECT_ROOT / 'dist'
    if not dist_dir.exists() or not list(dist_dir.glob('*')):
        print("❌ No packages found in dist/ directory!")
        print("  Run: python setup.py sdist bdist_wheel")
        sys.exit(1)
    
    repo_name = "TestPyPI" if test else "PyPI"
    print(f"📤 Uploading to {repo_name}...")
    
    cmd = [sys.executable, '-m', 'twine', 'upload']
    if test:
        cmd.extend(['--repository-url', 'https://test.pypi.org/legacy/'])
    
    cmd.extend(['-u', '__token__', '-p', token, 'dist/*'])
    
    try:
        # Run with output suppression for security
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              cwd=PROJECT_ROOT)
        
        if result.returncode == 0:
            print(f"✅ Successfully uploaded to {repo_name}!")
            if test:
                print("   View at: https://test.pypi.org/project/mcp-task-orchestrator/")
            else:
                print("   View at: https://pypi.org/project/mcp-task-orchestrator/")
        else:
            print("❌ Upload failed!")
            # Don't print stderr as it might contain the token
            print("   Check your token and try again")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Upload package to PyPI')
    parser.add_argument('--test', action='store_true', 
                       help='Upload to TestPyPI instead of PyPI')
    
    args = parser.parse_args()
    upload_to_pypi(test=args.test)