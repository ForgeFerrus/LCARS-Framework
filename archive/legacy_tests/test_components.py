#!/usr/bin/env python3
"""
Simple Test for LCARS Components
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from pathlib import Path

# Add project root to path
current_file = Path(__file__).resolve()
project_root = current_file.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lcars.ui.onboard import SystemStatusPanel, CORE_AVAILABLE
    from lcars.themes.palette import LCARSEra
    print("✅ Successfully imported SystemStatusPanel")
    print("✅ BoardComputer integration:", CORE_AVAILABLE)
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def main():
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = QMainWindow()
    main_window.setWindowTitle("LCARS Components Test")
    main_window.setGeometry(100, 100, 500, 400)
    
    # Create SystemStatusPanel
    try:
        status_panel = SystemStatusPanel(parent=main_window, era=LCARSEra.LCARS_25TH)
        main_window.setCentralWidget(status_panel)
        
        print("=== LCARS System Status Panel Test ===")
        print("✅ SystemStatusPanel created successfully")
        print("✅ CPU/MEM/PWR monitoring should be active")
        print("✅ Alert buttons should be visible")
        print("✅ BoardComputer integration:", CORE_AVAILABLE)
        
        main_window.show()
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error creating SystemStatusPanel: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
