#!/usr/bin/env python3
"""
LCARS Constructor Launcher
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")

try:
    # Try to run constructor directly
    constructor_path = project_root / "archive" / "legacy_junk" / "engineering_old" / "constructor.py"
    print(f"Constructor path: {constructor_path}")
    
    if constructor_path.exists():
        # Add the constructor directory to path
        sys.path.insert(0, str(constructor_path.parent))
        print(f"Added to path: {constructor_path.parent}")
        
        # Execute the constructor
        with open(constructor_path, 'r') as f:
            constructor_code = f.read()
        
        # Create a local namespace for execution
        constructor_namespace = {
            '__name__': '__main__',
            '__file__': str(constructor_path),
            'sys': sys,
            'Path': Path
        }
        
        exec(constructor_code, constructor_namespace)
    else:
        print(f"❌ Constructor file not found: {constructor_path}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error running constructor: {e}")
    import traceback
    traceback.print_exc()
