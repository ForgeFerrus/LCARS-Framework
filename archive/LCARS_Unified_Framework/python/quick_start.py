#!/usr/bin/env python3
"""
LCARS Unified Framework - Quick Start Script
Simple way to launch LCARS with unified imports
"""

import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import everything from lcars package
import lcars as lcars

def main():
    """Main entry point for quick start"""
    print("[LCARS] Unified Framework Quick Start")
    print("=" * 50)
    
    # Check what's available
    print(f"[LCARS] Desktop Available: {lcars.DESKTOP_AVAILABLE}")
    print(f"[LCARS] Version: {lcars.__version__}")
    print()
    
    # Create framework
    framework = lcars.create_framework()
    print(f"[LCARS] Framework created with era: {framework.era}")
    print(f"[LCARS] Theme accent: {framework.theme['accent']}")
    print()
    
    # Try to start desktop
    if lcars.DESKTOP_AVAILABLE:
        try:
            print("[LCARS] Starting desktop...")
            desktop = lcars.start_desktop()
            desktop.show()
            print("[LCARS] Desktop started successfully!")
        except Exception as e:
            print(f"[LCARS] Desktop error: {e}")
            print("[LCARS] Falling back to menu only...")
    
    # Start menu as fallback
    try:
        print("[LCARS] Starting menu...")
        menu = lcars.start_menu()
        menu.show_menu()
        print("[LCARS] Menu started successfully!")
    except Exception as e:
        print(f"[LCARS] Menu error: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
