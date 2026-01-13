"""
LCARS UI Builder: drag-n-drop layout editor (Phase 2)
- Visual editor for LCARS layouts
- Supports drag-n-drop, property editing, saving/loading .lcars.json
- Integrates with theme engine and LCARS components
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QFileDialog, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QMouseEvent
import json
import os

# Import LCARS components and theme engine
from lcars.core.theme_engine import ThemeEngine
from lcars.ui.lcars_button import LCARSButton
from lcars.ui.lcars_panel import LCARSPanel
from lcars.ui.lcars_label import LCARSLabel
from lcars.ui.lcars_slider import LCARSSlider
from lcars.ui.lcars_status_indicator import LCARSStatusIndicator

THEME_PATH = os.path.join(os.path.dirname(__file__), '../../../themes/lcars_default.json')

class DraggableWidget(QFrame):
    def __init__(self, inner_widget, parent=None):
        super().__init__(parent)
        self.inner_widget = inner_widget
        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(2)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(inner_widget)
        self.setMouseTracking(True)
        self.dragging = False
        self.offset = QPoint()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.offset)
            self.move(new_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False

class LCARSUIBuilder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS UI Builder")
        self.setGeometry(100, 100, 1200, 800)
        self.theme = ThemeEngine(THEME_PATH)
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QHBoxLayout(self.central)
        self.palette = QListWidget()
        self.palette.setFixedWidth(200)
        self.layout.addWidget(self.palette)
        self.canvas = QWidget()
        self.canvas.setStyleSheet("background: #111;")
        self.canvas.setMinimumSize(800, 700)
        self.canvas_layout = QVBoxLayout(self.canvas)
        self.layout.addWidget(self.canvas)
        self.components = []
        self._populate_palette()
        self.palette.itemDoubleClicked.connect(self.add_component)

    def _populate_palette(self):
        for name in ["Panel", "Button", "Label", "Slider", "StatusIndicator"]:
            item = QListWidgetItem(name)
            self.palette.addItem(item)

    def add_component(self, item):
        name = item.text()
        if name == "Panel":
            widget = LCARSPanel(self.theme)
        elif name == "Button":
            widget = LCARSButton("Button", self.theme)
        elif name == "Label":
            widget = LCARSLabel("Label", self.theme)
        elif name == "Slider":
            widget = LCARSSlider(self.theme)
        elif name == "StatusIndicator":
            widget = LCARSStatusIndicator(self.theme)
        else:
            return
        drag_widget = DraggableWidget(widget, self.canvas)
        drag_widget.setGeometry(QRect(50, 50 + 40*len(self.components), 200, 40))
        drag_widget.show()
        self.components.append(drag_widget)

    def save_layout(self):
        layout_data = []
        for comp in self.components:
            geo = comp.geometry()
            comp_type = type(comp.inner_widget).__name__
            layout_data.append({
                "type": comp_type,
                "x": geo.x(),
                "y": geo.y(),
                "w": geo.width(),
                "h": geo.height(),
                # Add more properties as needed
            })
        fname, _ = QFileDialog.getSaveFileName(self, "Save Layout", "layout.lcars.json", "LCARS Layout (*.lcars.json)")
        if fname:
            with open(fname, 'w') as f:
                json.dump(layout_data, f, indent=2)

    def load_layout(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Load Layout", "", "LCARS Layout (*.lcars.json)")
        if fname:
            with open(fname, 'r') as f:
                layout_data = json.load(f)
            for comp in self.components:
                comp.setParent(None)
            self.components.clear()
            for item in layout_data:
                t = item["type"]
                if t == "LCARSPanel":
                    widget = LCARSPanel(self.theme)
                elif t == "LCARSButton":
                    widget = LCARSButton("Button", self.theme)
                elif t == "LCARSLabel":
                    widget = LCARSLabel("Label", self.theme)
                elif t == "LCARSSlider":
                    widget = LCARSSlider(self.theme)
                elif t == "LCARSStatusIndicator":
                    widget = LCARSStatusIndicator(self.theme)
                else:
                    continue
                drag_widget = DraggableWidget(widget, self.canvas)
                drag_widget.setGeometry(QRect(item["x"], item["y"], item["w"], item["h"]))
                drag_widget.show()
                self.components.append(drag_widget)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_S:
                self.save_layout()
            elif event.key() == Qt.Key.Key_O:
                self.load_layout()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    builder = LCARSUIBuilder()
    builder.show()
    sys.exit(app.exec())
