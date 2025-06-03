#!/usr/bin/env python3
"""
Legacy installer wrapper for MCP Task Orchestrator.

DEPRECATED: This file exists for backward compatibility only.
Please use 'python run_installer.py' for the recommended installation method.

The optimized installer (run_installer.py) provides:
- Better import path handling
- Improved error messages
- Enhanced compatibility across Python environments
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    print("=" * 60)
    print("LEGACY INSTALLER DETECTED")
    print("=" * 60)
    print()
    print("⚠️  DEPRECATION NOTICE:")
    print("   This 'install.py' method is deprecated.")
    print()
    print("✅ RECOMMENDED METHOD:")
    print("   python run_installer.py")
    print()
    print("🔧 BENEFITS OF THE NEW METHOD:")
    print("   • Better import path handling")
    print("   • Improved error messages")
    print("   • Enhanced compatibility")
    print("   • Faster, more reliable installation")
    print()
    print("🚀 Redirecting to the optimized installer...")
    print("=" * 60)
    print()
    
    # Get the path to the optimized installer
    script_dir = Path(__file__).parent
    optimized_installer = script_dir / "run_installer.py"
    
    if not optimized_installer.exists():
        print("❌ Error: Could not find the optimized installer at:")
        print(f"   {optimized_installer}")
        print()
        print("📋 Please ensure you have the latest version:")
        print("   git pull origin main")
        print("   python run_installer.py")
        sys.exit(1)
    
    # Run the optimized installer with all the same arguments
    try:
        cmd = [sys.executable, str(optimized_installer)] + sys.argv[1:]
        result = subprocess.run(cmd, cwd=script_dir)
        
        if result.returncode == 0:
            print()
            print("=" * 60)
            print("MIGRATION COMPLETE!")
            print("=" * 60)
            print("✅ Installation successful using the optimized method.")
            print()
            print("📝 UPDATE YOUR SCRIPTS:")
            print("   Replace 'python install.py' with 'python run_installer.py'")
            print("   in any scripts or documentation you maintain.")
            print()
            print("🚀 Next time, use: python run_installer.py")
        
        sys.exit(result.returncode)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Installation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running optimized installer: {e}")
        print("\n🔧 Manual fallback:")
        print("   python run_installer.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
