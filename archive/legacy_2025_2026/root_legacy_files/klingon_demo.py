"""
Klingon Theme Demo for LCARS Framework
"""
import sys
from PyQt6.QtWidgets import QApplication
from lcars.themes.klingon_theme import create_klingon_interface

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Create and show the Klingon interface
    klingon_ui = create_klingon_interface()
    klingon_ui.setWindowTitle("Klingon Interface Demo")
    klingon_ui.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()