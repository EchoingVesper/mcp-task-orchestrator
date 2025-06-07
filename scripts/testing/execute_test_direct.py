import sys
import os
from pathlib import Path

# Direct execution of test
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the test
exec(open('standalone_migration_test.py').read())