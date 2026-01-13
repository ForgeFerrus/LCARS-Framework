"""
LCARS Constructor - Simple Working Version
Basic drag-and-drop interface editor
"""

import sys
import random
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor, QPainter

# Add project root
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.themes.lcars_palette import LCARSEra, get_era_palette

class DraggableWidget(QFrame):
    def __init__(self, parent=None, widget_type="Button"):
        super().__init__(parent)
        self.widget_type = widget_type
        self.selected = False
        self.dragging = False
        self.drag_start = QPoint()
        
        # Set size based on type
        if widget_type == "Button":
            self.setFixedSize(120, 40)
            self.color = QColor("#37A6D1")
        elif widget_type == "Panel":
            self.setFixedSize(200, 100)
            self.color = QColor("#1A2332")
        elif widget_type == "Display":
            self.setFixedSize(250, 150)
            self.color = QColor("#0A0E1A")
        else:
            self.setFixedSize(100, 100)
            self.color = QColor("#9EA5BA")
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color.name()};
                border: 2px solid transparent;
                border-radius: 10px;
            }}
        """)
        
        # Add label
        self.label = QLabel(widget_type.upper())
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: white; font-weight: bold;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        
        self.setMouseTracking(True)
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.selected:
            painter = QPainter(self)
            painter.setPen(QColor("#FF9F1C"))
            painter.drawRect(0, 0, self.width()-1, self.height()-1)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start = event.pos()
            self.parent().select_widget(self)
            self.raise_()
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.drag_start)
            self.move(new_pos)
    
    def mouseReleaseEvent(self, event):
        self.dragging = False

class LCARSConstructor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Constructor")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showMaximized()
        
        # Get 25th century palette
        self.palette = get_era_palette(LCARSEra.LCARS_25TH)
        self.setStyleSheet(f"background-color: {self.palette['background']};")
        
        self.widgets = []
        self.selected_widget = None
        
        self.setup_ui()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("◢ LCARS CONSTRUCTOR")
        title.setStyleSheet(f"""
            color: black; 
            background-color: {self.palette['button_colors'][0]}; 
            font-size: 24px; 
            font-weight: bold; 
            padding: 10px; 
            border-radius: 10px;
        """)
        header.addWidget(title)
        header.addStretch()
        
        # Exit button
        exit_btn = QPushButton("EXIT")
        exit_btn.setStyleSheet(f"""
            background-color: {self.palette['alert_colors'][0]}; 
            color: black; 
            font-weight: bold; 
            padding: 10px; 
            border-radius: 10px;
        """)
        exit_btn.clicked.connect(self.close)
        header.addWidget(exit_btn)
        
        layout.addLayout(header)
        
        # Main content
        content = QHBoxLayout()
        
        # Left panel - tools
        tools = QFrame()
        tools.setStyleSheet(f"""
            background-color: {self.palette['panel_bg']}; 
            border: 2px solid {self.palette['button_colors'][1]}; 
            border-radius: 15px;
        """)
        tools_layout = QVBoxLayout(tools)
        
        tools_title = QLabel("WIDGETS")
        tools_title.setStyleSheet(f"color: {self.palette['button_colors'][0]}; font-weight: bold; font-size: 16px;")
        tools_layout.addWidget(tools_title)
        
        # Widget creation buttons
        for widget_type in ["Button", "Panel", "Display", "Label"]:
            btn = QPushButton(f"ADD {widget_type}")
            btn.setStyleSheet(f"""
                background-color: {self.palette['button_colors'][1]}; 
                color: black; 
                font-weight: bold; 
                padding: 8px; 
                margin: 2px;
                border-radius: 8px;
            """)
            btn.clicked.connect(lambda checked, t=widget_type: self.add_widget(t))
            tools_layout.addWidget(btn)
        
        # Control buttons
        clear_btn = QPushButton("CLEAR ALL")
        clear_btn.setStyleSheet(f"""
            background-color: {self.palette['alert_colors'][0]}; 
            color: black; 
            font-weight: bold; 
            padding: 8px; 
            margin: 2px;
            border-radius: 8px;
        """)
        clear_btn.clicked.connect(self.clear_all)
        tools_layout.addWidget(clear_btn)
        
        tools_layout.addStretch()
        content.addWidget(tools)
        
        # Canvas area
        self.canvas = QFrame()
        self.canvas.setStyleSheet(f"""
            background-color: {self.palette['background']}; 
            border: 2px solid {self.palette['button_colors'][2]}; 
            border-radius: 15px;
        """)
        content.addWidget(self.canvas, 1)
        
        layout.addLayout(content)
        
        # Status bar
        self.status = QLabel("READY - Click ADD buttons to create widgets")
        self.status.setStyleSheet(f"color: {self.palette['text']}; font-size: 12px;")
        layout.addWidget(self.status)
    
    def add_widget(self, widget_type):
        widget = DraggableWidget(self.canvas, widget_type)
        
        # Random position
        x = random.randint(50, self.canvas.width() - 200)
        y = random.randint(50, self.canvas.height() - 150)
        widget.move(x, y)
        
        widget.show()
        self.widgets.append(widget)
        
        self.status.setText(f"Added {widget_type} - Total widgets: {len(self.widgets)}")
    
    def select_widget(self, widget):
        # Deselect all
        for w in self.widgets:
            w.selected = False
            w.update()
        
        # Select new widget
        self.selected_widget = widget
        widget.selected = True
        widget.update()
        
        self.status.setText(f"Selected: {widget.widget_type} at ({widget.x()}, {widget.y()})")
    
    def clear_all(self):
        for widget in self.widgets:
            widget.deleteLater()
        self.widgets.clear()
        self.selected_widget = None
        self.status.setText("Canvas cleared - All widgets removed")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LCARSConstructor()
    window.show()
    sys.exit(app.exec())