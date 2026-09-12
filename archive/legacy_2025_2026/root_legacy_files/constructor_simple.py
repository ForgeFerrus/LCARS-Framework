#!/usr/bin/env python3
"""
LCARS Constructor - Simple & Working Version
25th Century Style + AI Builder
"""

import sys
from pathlib import Path

# Bootstrap
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "lcars" / "themes"))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QTabWidget, QTextEdit, QLabel, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor

# Simple imports
try:
    from primitives import get_universal_primitives
    from lcars_palette import get_random_button_color, LCARSEra
    print("✅ LCARS modules loaded")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# =====================
# SIMPLE CANVAS
# =====================

class SimpleCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.primitives = get_universal_primitives()
        self.setup_style()
        
    def setup_style(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1C3C55, stop:1 #0A1929);
                border: 3px solid #2A7193;
                border-radius: 8px;
            }
        """)
        
    def add_element(self, element_type, x=50, y=50):
        """Додає елемент на канвас"""
        try:
            if element_type in self.primitives:
                widget = self.primitives[element_type]()
                widget.setParent(self)
                widget.move(x, y)
                widget.resize(120, 60)
                
                # Стиль LCARS
                if hasattr(widget, 'setColor'):
                    widget.setColor(get_random_button_color(LCARSEra.LCARS_25TH))
                else:
                    widget.setStyleSheet(f"""
                        QWidget {{
                            background: {get_random_button_color(LCARSEra.LCARS_25TH)};
                            border: 2px solid #37A6D1;
                            border-radius: 4px;
                            color: white;
                            font-weight: bold;
                        }}
                    """)
                
                widget.show()
                self.elements.append(widget)
                print(f"✅ Added {element_type}")
                return widget
        except Exception as e:
            print(f"❌ Error adding {element_type}: {e}")
        return None
        
    def clear(self):
        """Очищує канвас"""
        for element in self.elements:
            element.deleteLater()
        self.elements.clear()
        print("🧹 Canvas cleared")

# =====================
# AI BUILDER
# =====================

class AIBuilder(QWidget):
    build_requested = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("◢ AI BUILDER")
        title.setStyleSheet("""
            QLabel {
                color: #37A6D1;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background: #2F3749;
                border: 2px solid #52596E;
                border-radius: 8px;
            }
        """)
        layout.addWidget(title)
        
        # Build buttons
        buttons = [
            ("Basic Layout", "#4BBEBF", "basic"),
            ("Control Panel", "#FF6753", "control"),
            ("Status Panel", "#66FF66", "status"),
            ("Clear Canvas", "#E7442A", "clear")
        ]
        
        for text, color, action in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {color}, stop:1 {color}dd);
                    color: white;
                    border: 2px solid {color};
                    padding: 12px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: {color}cc;
                }}
            """)
            btn.clicked.connect(lambda checked, a=action: self.build_requested.emit(a))
            layout.addWidget(btn)
            
        layout.addStretch()

# =====================
# MAIN WINDOW
# =====================

class LCARSConstructor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Constructor - 25th Century")
        self.setGeometry(100, 100, 1200, 800)
        
        # LCARS стиль
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2F3749, stop:1 #1C3C55);
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel
        left_panel = QTabWidget()
        left_panel.setMaximumWidth(300)
        
        # LCARS стиль для вкладок
        left_panel.setStyleSheet("""
            QTabWidget::pane {
                border: 3px solid #52596E;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2F3749, stop:1 #1C3C55);
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #6D748C;
                color: white;
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #37A6D1;
            }
        """)
        
        # Primitives tab
        self.primitives_list = QListWidget()
        for name in sorted(get_universal_primitives().keys()):
            self.primitives_list.addItem(QListWidgetItem(name))
        self.primitives_list.setStyleSheet("""
            QListWidget {
                background: #1C3C55;
                color: white;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background: #37A6D1;
            }
        """)
        self.primitives_list.itemDoubleClicked.connect(self.add_primitive)
        left_panel.addTab(self.primitives_list, "◢ PRIMITIVES")
        
        # AI Builder tab
        self.ai_builder = AIBuilder()
        self.ai_builder.build_requested.connect(self.ai_build)
        left_panel.addTab(self.ai_builder, "◢ AI BUILDER")
        
        splitter.addWidget(left_panel)
        
        # Canvas
        self.canvas = SimpleCanvas()
        splitter.addWidget(self.canvas)
        
        # Set splitter sizes
        splitter.setSizes([300, 900])
        
    def add_primitive(self, item):
        """Додає примітив з подвійним кліком"""
        element_type = item.text()
        x = 50 + len(self.canvas.elements) * 30
        y = 50 + len(self.canvas.elements) * 20
        self.canvas.add_element(element_type, x, y)
        
    def ai_build(self, build_type):
        """AI побудова інтерфейсів"""
        if build_type == "clear":
            self.canvas.clear()
            return
            
        self.canvas.clear()
        
        if build_type == "basic":
            # Базовий макет
            self.canvas.add_element("Rect", 20, 20)
            for i in range(5):
                self.canvas.add_element("Button", 30, 40 + i * 70)
            self.canvas.add_element("Rect", 200, 20)
            self.canvas.add_element("Display", 220, 40)
            for i in range(4):
                self.canvas.add_element("Indicator", 30, 400 + i * 50)
                
        elif build_type == "control":
            # Панель управління
            self.canvas.add_element("Rect", 50, 50)
            controls = ["POWER", "SYSTEMS", "WEAPONS", "SHIELDS"]
            for i, text in enumerate(controls):
                btn = self.canvas.add_element("Button", 70, 80 + i * 70)
                if btn and hasattr(btn, 'setText'):
                    btn.setText(text)
            self.canvas.add_element("Display", 250, 80)
            
        elif build_type == "status":
            # Панель статусу
            self.canvas.add_element("Rect", 50, 50)
            self.canvas.add_element("Label", 70, 80)
            for i in range(6):
                self.canvas.add_element("Indicator", 70 + (i % 3) * 150, 120 + (i // 3) * 60)
            self.canvas.add_element("Display", 70, 250)

# =====================
# RUN
# =====================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # LCARS font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    window = LCARSConstructor()
    window.show()
    
    print("🚀 LCARS Constructor started!")
    print("📋 Double-click primitives to add elements")
    print("🤖 Use AI Builder tab for auto-layouts")
    
    sys.exit(app.exec())
