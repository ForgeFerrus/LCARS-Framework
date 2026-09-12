#!/usr/bin/env python3
"""
Simple LCARS Launcher - Launches working demo
This launcher opens the simple demo without theme.py dependencies.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Launch the simple LCARS demo"""
    demo_path = Path(__file__).parent / "demo" / "simple_demo_launcher.py"
    
    if demo_path.exists():
        print("🚀 Launching LCARS Simple Demo...")
        print("📍 Location:", demo_path)
        print("🎮 Features: All factions, simple interface, no dependencies")
        print("-" * 50)
        
        # Import and run the simple demo
        os.chdir(demo_path.parent)
        exec(open(demo_path).read())
    else:
        print("❌ Error: Simple demo not found!")
        print(f"🔍 Looking for: {demo_path}")
        print("💡 Please ensure the demo folder exists with simple_demo_launcher.py")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
