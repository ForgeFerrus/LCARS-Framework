"""
22nd Century LCARS Interface
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QApplication, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

class PCARS22ndCentury(QMainWindow):
    def __init__(self, root_path, selector=None):
        """22nd century interface.

        Accepts an optional selector reference so the interface can return control
        to the launcher (selector.show()).
        """
        super().__init__()
        self.root_path = root_path
        self.selector = selector
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("22nd Century PCARS - NX-01 Era")
        
        # Set early LCARS style (more utilitarian)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000033;
            }
            QLabel {
                color: #66B2FF;
                font-family: 'Arial';
            }
            QPushButton {
                background-color: #003366;
                color: #66B2FF;
                border: 1px solid #3399FF;
            }
            QPushButton:hover {
                background-color: #0066CC;
            }
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("NX-CLASS OPERATIONAL INTERFACE")
        title.setStyleSheet("""
            font-size: 24px;
            color: #3399FF;
            padding: 10px;
            background-color: #000066;
            border-radius: 5px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Early LCARS elements with more basic styling
        systems_label = QLabel("EXPERIMENTAL WARP 5 COMPLEX")
        systems_label.setStyleSheet("font-size: 18px; color: #66B2FF;")
        systems_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(systems_label)
        
        # Status display
        status = QLabel("SYSTEMS OPERATIONAL - READY FOR LAUNCH")
        status.setStyleSheet("color: #00FF00; font-size: 16px;")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status)

        # Add a return button so the user can go back to the selector/launcher
        from PyQt6.QtWidgets import QPushButton
        return_btn = QPushButton("RETURN TO LAUNCHER")
        return_btn.setFixedSize(360, 64)
        return_btn.setStyleSheet("""
            QPushButton {
                background-color: #3399FF;
                color: #000000;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #66BBFF;
            }
        """)
        return_btn.clicked.connect(self.return_to_selector)
        layout.addSpacing(12)
        layout.addWidget(return_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def return_to_selector(self):
        # Try to show the selector (launcher) if provided, then close this window
        try:
            if self.selector is not None:
                # selector may have been hidden instead of closed by the launcher
                try:
                    self.selector.show()
                except Exception:
                    pass
        except Exception:
            pass
        # Close this interface
        try:
            self.close()
        except Exception:
            pass

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from pathlib import Path
    
    print("Starting PCARS 22nd Century Prototype...")
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Get the root path (project directory)
    root_path = Path(__file__).parent.parent.parent
    print(f"Root path: {root_path}")
    
    # Create and show the 22nd century interface
    try:
        nx_interface = PCARS22ndCentury(root_path)
        print("PCARS22ndCentury created successfully")
        nx_interface.show()
        print("Window shown successfully")
        
        # Run the application
        print("Starting app.exec()...")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()