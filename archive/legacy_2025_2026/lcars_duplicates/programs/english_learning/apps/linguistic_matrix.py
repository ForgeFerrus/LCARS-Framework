"""
Linguistic Matrix - LCARS Integrated Application
English Learning System as part of LCARS Framework
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Add project root to path
proj_root = Path(__file__).resolve().parents[3]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from lcars.themes.lcars_palette import get_theme, LCARSEra
# the external lcars.modules.linguistic_matrix package provides the backend
# service, not a GUI component; we actually don't use
# `create_linguistic_matrix_app` here so remove the faulty import.

class LinguisticMatrixLCARS:
    """LCARS Integrated Linguistic Matrix Application"""
    
    def __init__(self, era=LCARSEra.LCARS_24TH):
        self.era = era
        self.colors = get_theme(era)
        self.app = None
        self.window = None
    
    def initialize(self):
        """Initialize the application within LCARS framework"""
        try:
            # Create the Linguistic Matrix app
            self.app = create_linguistic_matrix_app(self.era)
            
            if self.app:
                self.window = self.app.get_window()
                return True
            else:
                return False
                
        except Exception as e:
            error_msg = f"Failed to initialize Linguistic Matrix:\n{str(e)}"
            QMessageBox.critical(None, "LCARS Integration Error", error_msg)
            return False
    
    def run(self):
        """Run the application"""
        if not self.app:
            return False
        
        try:
            # Show the window
            self.app.show()
            return True
            
        except Exception as e:
            error_msg = f"Failed to run Linguistic Matrix:\n{str(e)}"
            QMessageBox.critical(None, "Runtime Error", error_msg)
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        if self.app:
            self.app.cleanup()

def run_linguistic_matrix_lcars(era=LCARSEra.LCARS_24TH):
    """Main entry point for LCARS integration"""
    # Create QApplication first
    qt_app = QApplication.instance()
    if not qt_app:
        qt_app = QApplication(sys.argv)
        
        # Set LCARS styling
        qt_app.setStyle('Fusion')
        qt_app.setPalette(get_theme(era)['palette'][0])
        
        # Set LCARS font
        font = QFont("Arial", 10)
        qt_app.setFont(font)
    
    # Create application instance
    lmatrix_app = LinguisticMatrixLCARS(era)
    
    # Initialize
    if not lmatrix_app.initialize():
        sys.exit(1)
    
    # Run
    try:
        return qt_app.exec()
    except KeyboardInterrupt:
        print("◤ Linguistic Matrix terminated by user")
        lmatrix_app.cleanup()
        sys.exit(0)
    except Exception as e:
        print(f"◤ FATAL ERROR: {e}")
        lmatrix_app.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    print("◤ LINGUISTIC MATRIX - LCARS INTEGRATED SYSTEM")
    print("◤ Initializing English Language Acquisition System...")
    
    # Run the application
    run_linguistic_matrix_lcars()
