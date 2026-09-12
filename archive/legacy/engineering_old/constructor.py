"""
LCARS Interface Constructor - Internal Engineering System.
Specialized for manual assembly of UI components from primitive shapes.
Uses the shared EditMode for manipulation.
"""
import json
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QListWidget, QListWidgetItem, QScrollArea, QSplitter,
    QLineEdit, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect

from lcars.ui.base.widgets import LCARSButton, LCARSElbow
# Stub for missing LcarsTile
class LCARSPanel(QFrame):
    def __init__(self, title="", color="#3366CC", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {color}; border-radius: 10px;")
        layout = QVBoxLayout(self)
        lbl = QLabel(title)
        lbl.setStyleSheet("color: #FFF; font-weight: bold;")
        layout.addWidget(lbl)
from lcars.engineering.editor.edit_mode import EditMode
from lcars.themes.palette import get_lcars_font_style

import logging
logger = logging.getLogger(__name__)

# Safe: try to import `ensure_bootstrap` but do NOT call it at import time.
try:
    from lcars.core.substrate import ensure_bootstrap
except ImportError:
    # If substrate not present in this environment, provide a no-op fallback
    def ensure_bootstrap():
        return None

class ConstructorCanvas(QFrame):
    """Integrated Assembly Floor."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000; border: 1px solid #3366CC;")
        self.setAcceptDrops(True)
        self.elements = []
        
        # Professional manipulation substrate (Shared Engineering Logic)
        self.edit_mode = EditMode(self)
        self.edit_mode.enabled = True
        self.edit_mode.set_elements(self.elements)

    def add_primitive(self, p_type, pos=QPoint(100, 100)):
        """Deploy a new primitive into the substrate."""
        if p_type == "BUTTON":
            w = LCARSButton("PRIMITIVE", "#FF9900")
            w.resize(140, 40)
        elif p_type == "ELBOW":
            w = LCARSElbow("top-left")
            w.resize(100, 100)
        elif p_type == "PANEL":
            w = QFrame()
            w.setStyleSheet("background-color: #222; border: 2px solid #555; border-radius: 5px;")
            w.resize(200, 150)
        elif p_type == "LABEL":
            w = QLabel("DATA_BLOCK")
            w.setStyleSheet("color: #99CCFF; font-family: 'Courier New'; font-weight: normal;")
            w.resize(120, 25)
        else: return

        w.setParent(self)
        w.move(pos)
        w.show()
        
        # Track element for EditMode and serialization
        self.elements.append({
            'widget': w,
            'type': p_type,
            'geom': [pos.x(), pos.y(), w.width(), w.height()],
            'text': getattr(w, 'text', lambda: "")() if hasattr(w, 'text') else ""
        })

class InterfaceConstructor(QWidget):
    """The 'Constructor' internal engineering program."""
    def __init__(self, system=None, parent=None):
        super().__init__(parent)
        self.system = system # Link to main system core
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        # --- LEFT: ASSEMBLY PALETTE ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        s_layout = QVBoxLayout(self.sidebar)
        
        lbl_head = QLabel("◤ UI CONSTRUCTOR")
        lbl_head.setStyleSheet(f"color: #FFCC00; {get_lcars_font_style(20, 'normal')}")
        s_layout.addWidget(lbl_head)
        
        lbl_sub = QLabel("MANUAL PRIMITIVE ASSEMBLY")
        lbl_sub.setStyleSheet("color: #666; font-size: 10px;")
        s_layout.addWidget(lbl_sub)
        
        # Primitive Factory
        primitives = [
            ("L-CURVE (ELBOW)", "ELBOW", "#3366CC"),
            ("STRUCTURAL PANEL", "PANEL", "#99CCFF"),
            ("DATA LABEL", "LABEL", "#CC66FF"),
            ("COMMAND BUTTON", "BUTTON", "#FF9900")
        ]
        
        for name, ptype, color in primitives:
            btn = LCARSButton(name, color, shape="left")
            btn.setFixedSize(210, 40)
            btn.clicked.connect(lambda ch, t=ptype: self.canvas.add_primitive(t))
            s_layout.addWidget(btn)
        
        s_layout.addStretch()
        
        # Operations
        btn_clear = LCARSButton("RESET CANVAS", "#990000", shape="left")
        btn_clear.setFixedSize(210, 40)
        btn_clear.clicked.connect(self.clear_canvas)
        s_layout.addWidget(btn_clear)

        self.main_layout.addWidget(self.sidebar)

        # --- CENTER: ASSEMBLY FLOOR ---
        self.canvas = ConstructorCanvas(self)
        self.main_layout.addWidget(self.canvas, 1)

        # --- RIGHT: PROPERTY STACK ---
        self.inspector = QFrame()
        self.inspector.setFixedWidth(220)
        i_layout = QVBoxLayout(self.inspector)
        
        lbl_i = QLabel("◤ PRIMITIVE DATA")
        lbl_i.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(18, 'normal')}")
        i_layout.addWidget(lbl_i)

        # Basic LCARS-style prop editors
        s_edit = "background: #080808; color: #FFF; border: 1px solid #444; height: 35px; border-radius: 5px;"
        
        self.edit_id = QLineEdit(); self.edit_id.setStyleSheet(s_edit)
        self.edit_id.setPlaceholderText("PRIMITIVE_ID")
        i_layout.addWidget(self.edit_id)
        
        self.edit_text = QLineEdit(); self.edit_text.setStyleSheet(s_edit)
        self.edit_text.setPlaceholderText("LABEL_TEXT")
        i_layout.addWidget(self.edit_text)

        i_layout.addStretch()
        
        btn_save = LCARSButton("SAVE SCHEMATIC", "#0088AA", shape="right")
        btn_save.setFixedSize(210, 45)
        # Link to a save logic here
        i_layout.addWidget(btn_save)

        self.main_layout.addWidget(self.inspector)

    def clear_canvas(self):
        """Clears the assembly floor."""
        for el in self.canvas.elements:
            el['widget'].deleteLater()
        self.canvas.elements.clear()
        print("◤ CONSTRUCTOR: Substrate reset.")

if __name__ == "__main__":
    try:
        ensure_bootstrap()
    except Exception:
        pass
    
    from PyQt6.QtWidgets import QApplication
    import sys
    
    try:
        from lcars.core.system import Kernel
    except ImportError:
        class Kernel:
            def __init__(self, headless=False):
                pass

    app = QApplication(sys.argv)
    system = Kernel(headless=True)

    win = QWidget()
    win.setWindowTitle("LCARS INTERNAL CONSTRUCTOR")
    win.resize(1200, 700)
    win.setStyleSheet("background-color: black;")
    l = QVBoxLayout(win)
    l.addWidget(InterfaceConstructor(system=system))
    win.show()
    sys.exit(app.exec())