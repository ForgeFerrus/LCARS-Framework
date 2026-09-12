#!/usr/bin/env python3
"""Test script to verify terminal and system_menu imports work correctly."""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_terminal_import():
    """Test that LCARSTerminal can be imported."""
    try:
        from lcars.ui.terminal import LCARSTerminal
        print("✓ LCARSTerminal imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing LCARSTerminal: {e}")
        return False

def test_system_menu_import():
    """Test that SystemMenu can be imported."""
    try:
        from lcars.ui.system_menu import SystemMenu
        print("✓ SystemMenu imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing SystemMenu: {e}")
        return False

def test_power_import():
    """Test that SystemPower can be imported."""
    try:
        from lcars.system.power import SystemPower
        print("✓ SystemPower imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing SystemPower: {e}")
        return False

def main():
    print("Testing LCARS-Framework imports...")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_power_import()
    all_passed &= test_terminal_import()
    all_passed &= test_system_menu_import()
    
    print("=" * 50)
    if all_passed:
        print("✓ All imports successful!")
        return 0
    else:
        print("✗ Some imports failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())