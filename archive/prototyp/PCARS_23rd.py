"""
23rd Century LCARS Interface
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QFrame, QGridLayout, QApplication, QMainWindow)
from PyQt6.QtCore import Qt, QTimer

class BaseLCARSInterface(QMainWindow):
    """Base interface class"""
    def __init__(self, root_path, selector=None):
        super().__init__()
        self.root_path = root_path
        self.selector = selector
        self.setup_window()
        self.setup_colors()
        self.create_interface()
        
    def setup_window(self):
        """Setup basic window properties"""
        self.setWindowTitle("LCARS Interface")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
    def setup_colors(self):
        """Setup color scheme"""
        pass
        
    def create_interface(self):
        """Create the main interface"""
        layout = QVBoxLayout()
        
        # Add components
        layout.addWidget(self.create_header())
        layout.addWidget(self.create_content())
        layout.addWidget(self.create_footer())
        
        # Central widget
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        
    def create_header(self):
        """Create header - to be overridden"""
        return QFrame()
        
    def create_content(self):
        """Create content - to be overridden"""
        return QFrame()
        
    def create_footer(self):
        """Create footer - to be overridden"""
        return QFrame()
        
    def return_to_selector(self):
        """Return to selector"""
        if self.selector:
            self.selector.show()
        self.close()

class PCARS23rdCentury(BaseLCARSInterface):
    def __init__(self, root_path, selector=None):
        self.color_index = 0
        # Preserve a reference to the selector so the interface can return to it
        self.selector = selector
        super().__init__(root_path, selector)
        
    def get_title(self):
        return "CONSTITUTION CLASS COMMAND SYSTEM"
        
    def setup_colors(self):
        self.colors = {
            'schemes': [
                {
                    'background': '#000000',
                    'text': '#FFD700',  # Gold
                    'button': '#CD853F',  # Peru
                    'accent': '#FF4500'  # OrangeRed
                },
                {
                    'background': '#000000',
                    'text': '#FF4500',  # OrangeRed
                    'button': '#FFD700',  # Gold
                    'accent': '#CD853F'  # Peru
                },
                {
                    'background': '#000000',
                    'text': '#CD853F',  # Peru
                    'button': '#FF4500',  # OrangeRed
                    'accent': '#FFD700'  # Gold
                }
            ]
        }
        self.current_scheme = self.colors['schemes'][0]
        
    def create_header(self):
        header = QFrame()
        header.setFixedHeight(120)
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)
        
        # Left side buttons
        left_panel = QWidget()
        left_layout = QGridLayout()
        left_panel.setLayout(left_layout)
        
        # Create control buttons
        control_buttons = [
            "SHIELDS", "WEAPONS", "SENSORS", "COMMS",
            "ENGINES", "LIFE SUP", "TRANSPORT", "SECURITY"
        ]
        
        row = 0
        col = 0
        for btn_text in control_buttons:
            btn = QPushButton(btn_text)
            btn.setFixedSize(120, 40)
            left_layout.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
                
        header_layout.addWidget(left_panel)
        
        # Center title
        title = QLabel(self.get_title())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        
        # Right side status panel
        status_panel = QWidget()
        status_layout = QVBoxLayout()
        status_panel.setLayout(status_layout)
        
        status_labels = [
            "WARP CORE: ONLINE",
            "SHIELDS: 100%",
            "WEAPONS: READY"
        ]
        
        for status in status_labels:
            label = QLabel(status)
            label.setStyleSheet("font-size: 18px;")
            status_layout.addWidget(label)
            
        header_layout.addWidget(status_panel)
        
        return header
        
    def create_content(self):
        content = QFrame()
        content_layout = QGridLayout()
        content.setLayout(content_layout)
        
        # Main view sections
        sections = [
            ("SHIP STATUS", 0, 0),
            ("TACTICAL", 0, 1),
            ("NAVIGATION", 0, 2),
            ("ENGINEERING", 1, 0),
            ("SCIENCE", 1, 1),
            ("OPERATIONS", 1, 2)
        ]
        
        for title, row, col in sections:
            section = self.create_section(title)
            content_layout.addWidget(section, row, col)
            
        return content
        
    def create_section(self, title):
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 50%);
                border-radius: 10px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        section.setLayout(layout)
        
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 24px;
            padding: 10px;
        """)
        # Center section titles for better alignment
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Add some mock controls
        for i in range(3):
            btn = QPushButton(f"Control {i+1}")
            btn.setFixedHeight(40)
            layout.addWidget(btn)
            
        return section
        
    def create_footer(self):
        footer = QFrame()
        footer.setFixedHeight(100)
        footer_layout = QHBoxLayout()
        footer.setLayout(footer_layout)
        
        # Status message
        status = QLabel("ALL SYSTEMS NOMINAL - READY FOR ORDERS")
        status.setStyleSheet("font-size: 18px;")
        footer_layout.addWidget(status)
        
        # Spacer
        footer_layout.addStretch()
        
        # Exit button (return to launcher/selector)
        exit_btn = QPushButton("RETURN TO SELECTOR")
        exit_btn.clicked.connect(self.return_to_selector)
        exit_btn.setFixedSize(200, 50)
        footer_layout.addWidget(exit_btn)
        
        return footer
        
    def update_colors(self):
        """Rotate through color schemes"""
        self.color_index = (self.color_index + 1) % len(self.colors['schemes'])
        self.current_scheme = self.colors['schemes'][self.color_index]
        
        # Update all buttons
        for btn in self.findChildren(QPushButton):
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.current_scheme['button']};
                    color: {self.current_scheme['text']};
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    background-color: {self.current_scheme['accent']};
                }}
            """)
            
        # Update labels
        for label in self.findChildren(QLabel):
            label.setStyleSheet(f"""
                color: {self.current_scheme['text']};
                font-family: 'Arial';
            """)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from pathlib import Path
    
    print("Starting PCARS 23rd Century Prototype...")
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Get the root path (project directory)
    root_path = Path(__file__).parent.parent.parent
    print(f"Root path: {root_path}")
    
    # Create and show the 23rd century interface
    try:
        pears_interface = PCARS23rdCentury(root_path)
        print("PCARS23rdCentury created successfully")
        pears_interface.show()
        print("Window shown successfully")
        
        # Run the application
        print("Starting app.exec()...")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()