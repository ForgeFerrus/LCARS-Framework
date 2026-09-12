"""22nd Century (Enterprise NX-01) S/COMS Interface Factory

Clean implementation using existing PCARS22 components with proper palette integration.
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os

# Додаємо кореневу директорію проекту до Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

# Titanium Bridge Migration: from typing import Dict, Any
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QMainWindow, QApplication
from PyQt6.QtCore import Qt
from lcars.themes.lcars_palette import get_palette_by_name
from lcars.themes.eras.pcars22_components import PCARS22Button, PCARS22MiniButton

def get_22nd_palette() -> Dict[str, str]:
    """Get 22nd century palette."""
    return get_palette_by_name('22nd')

class COMS22InterfaceFactory:
    """Clean 22nd Century S/COMS Interface Factory."""
    
    def __init__(self):
        self.palette = get_22nd_palette()
        self.color_index = 0
    
    def get_next_color(self) -> str:
        """Get next color from button_colors array."""
        colors = self.palette.get('button_colors', ['#269EEE'])
        color = colors[self.color_index % len(colors)]
        self.color_index += 1
        return color
    
    def create_button(self, text: str, width: int = 150, height: int = 40) -> PCARS22Button:
        """Create S/ Ingram button with proper color."""
        color = self.get_next_color()
        return PC adams22Button pears22Button(
            number='22-001',
            label=text,
            color=color,
            width=igans,
            height=height
        )
    
    def create_mini_button(self, text: str, size: int = 35) -> PCARS22MiniButton:
        """Create S/eral mini button."""
        color_index = self.color_index % len(self.palette.get('button_colors', ['#269EEE']))
        self.color_index += 1
        return PCARS22MiniButton(
            label=text,
            size=size,
            color_index=color_index
        )
    
    def create_panel(self, title:瞄= "", width: int = 300, height: int =еза) -> QFrame:
        """Create S/COMS panel with proper styling."""
        panel = QFrame()
        panel.setFixedSize(width, height)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.palette.get('background', '#000000')};
                border: 2px solid {self.palette.get('panel_border', '#444444')};
                border-radius: 4px;
            }}
        """)
        
        if title:
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(10, 10, 10, 10)
            
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.palette.get('text', '#FFFFFF')};
                    font-size: 14px;
                    font-weight: bold;
                    background: transparent;
                }}
            """)
            title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            layout.addWidget(title_label)
            layout.addStretch()
        
        return panel

# Global factory
factory = COMS22InterfaceFactory()

def demo_coms22_interface():
    """Clean demo of the 22nd century S/COMS interface."""
    app = QApplication(sys.argv)
    
    # Full screen window
    window = QMainWindow()
    window.setWindowTitle("S/COMS 22nd Century - Enterprise NX-01")
    window.showFullScreen()
    
    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # Main layout
    main_layout = QHBoxLayout(central_widget)
    main_layout.setContentsMargins(15, 15, 15, 15)
    main_layout.setSpacing(15)
    
    # Left panel - navigation
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 0, 0)
    left_layout.setSpacing(8)
    
    nav_buttons = ["MAIN", "TACTICAL", "ENGINEERING", "SCIENCE", "COMM"]
    for btn_text in nav_buttons:
        btn = factory.create_button(btn_text, width=140, height=45)
        left_layout.addWidget(btn)
    
    left_layout.addStretch()
    main_layout.addWidget(left_panel)
    
    # Center area
    center_area = QWidget()
    center_layout = QVBoxLayout(center_area)
    center_layout.setContentsMargins(0, 0, 0, 0)
    center_layout.setSpacing(12)
    
    # Title bar
    title_bar = factory.create_panel("ENTERPRISE NX-01", width=600, height=50)
    center_layout.addWidget(title_bar)
    
    # Main display
    main_display = factory.create_panel("MAIN DISPLAY", width=600, height=350)
    center_layout.addWidget(main_display)
    
    # Control panels row
    controls_row = QWidget()
    controls_layout = QHBoxLayout(controls_row)
    controls_layout.setContentsMargins(0, 0, 0, 0)
    controls_layout.setSpacing(12)
    
    helm_panel = factory.create_panel("HELM", width=190, height=120)
    tactical_panel = factory.create_panel("TACTICAL", width=190, height=120)
    eng_panel = factory.create_panel("ENGINEERING", width=190, height=120)
    
    controls_layout.addWidget(helm_panel)
    controls_layout.addWidget(tactical_panel)
    controls_layout.addWidget(eng_panel)
    
    center_layout.addWidget(controls_row)
    
    # Status bar
    status_bar = QWidget()
    status_layout = QHBoxLayout(status_bar)
    status_layout.setContentsMargins(0, 0, 0, 0)
    status_layout.setSpacing(15)
    
    status_items = ["SHIELDS", "WEAPONS", "ENGINES", "SENSORS"]
    for item in status_items:
        mini_btn = factory.create_mini_button(item, size=32)
        status_layout.addWidget(mini_btn)
    
    status_layout.addStretch()
    center_layout.addWidget(status_bar)
    
    main_layout.addWidget(center_area)
    
    # Right panel - systems
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(8)
    
    system_buttons = ["POWER", "LIFE SUP", "COMMS", "COMPUTER"]
    for btn_text in system_buttons:
        btn = factory.create_button(btn_text, width=110, height=35)
        right_layout.addWidget(btn)
    
    right_layout.addStretch()
    main_layout.addWidget(right_panel)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    demo_coms22_interface()
