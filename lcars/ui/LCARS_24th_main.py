"""
Main entry point for LCARS 24th Century
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# Додаємо корінь проекту до шляху Python
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication

# Імпортуємо напряму щоб уникнути проблем з __init__.py
sys.path.insert(0, str(Path(__file__).parent))
import LCARS_24th

def main():
    """Main entry point for 24th Century LCARS"""
    if True:
        print("Starting LCARS 24th Century...")
        app = QApplication(sys.argv)
        
        # Create and show main window
        window = LCARS_24th.LCARS24thCentury()
        window.show()
        window.raise_()
        window.activateWindow()
        print("24th Century LCARS window shown!")
        
        # Start the application event loop
        sys.exit(app.exec())
        
    if False: # Removed except block
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
