import sys
from pathlib import Path

# Додаємо корінь проекту до шляху Python
project_root = str(Path('.').absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class SimpleBaseLCARS(QMainWindow):
    def __init__(self, root_path=None):
        super().__init__()
        self.setWindowTitle("Base LCARS Interface")
        self.showFullScreen()
        
        # Colors
        self.colors = {
            'background': '#000000',
            'text': '#FFFFFF', 
            'accent': '#FF9900',
            'primary': '#3366CC',
            'secondary': '#4477DD',
            'warning': '#FF4444'
        }
        
        # Animation
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_colors)
        self.color_timer.start(3000)  # 3 seconds
        
        self.animated_elements = []
        self.setup_ui()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # Header
        header = QFrame()
        header.setFixedHeight(120)
        header_layout = QHBoxLayout(header)
        
        title = QLabel("BASE LCARS INTERFACE")
        title.setFont(QFont('Arial', 36, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {self.colors['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        self.animated_elements.append(title)
        
        layout.addWidget(header)
        
        # Content
        content = QFrame()
        content_layout = QVBoxLayout(content)
        
        # Some buttons
        button_layout = QHBoxLayout()
        for i in range(4):
            btn = QPushButton(f"SYSTEM {i+1}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.colors['primary']};
                    color: #000000;
                    border: 3px solid {self.colors['accent']};
                    border-radius: 15px;
                    padding: 20px;
                    font-weight: bold;
                    font-size: 18px;
                    min-height: 80px;
                }}
            """)
            button_layout.addWidget(btn)
            self.animated_elements.append(btn)
        
        content_layout.addLayout(button_layout)
        
        # Status
        status = QLabel("STATUS: ALL SYSTEMS OPERATIONAL")
        status.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        status.setStyleSheet(f"color: {self.colors['text']}; padding: 20px;")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(status)
        self.animated_elements.append(status)
        
        layout.addWidget(content)
        
        # Footer
        footer = QFrame()
        footer.setFixedHeight(100)
        footer_layout = QHBoxLayout(footer)
        
        return_btn = QPushButton("RETURN TO MAIN")
        return_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.colors['warning']};
                color: {self.colors['text']};
                border: none;
                border-radius: 10px;
                padding: 15px;
                font-size: 18px;
                min-width: 200px;
            }}
        """)
        return_btn.clicked.connect(self.close)
        footer_layout.addWidget(return_btn)
        self.animated_elements.append(return_btn)
        
        layout.addWidget(footer)
        
    def update_colors(self):
        import random
        colors = [self.colors['primary'], self.colors['accent'], self.colors['secondary']]
        
        for element in self.animated_elements:
            try:
                if isinstance(element, QPushButton):
                    color = random.choice(colors)
                    element.setStyleSheet(f"""
                        QPushButton {{
                            background: {color};
                            color: #000000;
                            border: 3px solid {self.colors['accent']};
                            border-radius: 15px;
                            padding: 20px;
                            font-weight: bold;
                            font-size: 18px;
                            min-height: 80px;
                        }}
                    """)
                elif isinstance(element, QLabel):
                    color = random.choice(colors)
                    element.setStyleSheet(f"color: {color}; padding: 20px;")
            except:
                pass

def main():
    app = QApplication([])
    window = SimpleBaseLCARS()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
