"""
Isolinear Architect - The LCARS Development Environment.
Integrated IDE for building LCARS Views, Modules, and Themes across eras.
"""
import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QListWidget, QListWidgetItem, QFormLayout,
    QFrame, QComboBox, QTabWidget, QStackedWidget, QFileDialog
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect, QTimer, QMimeData
from PyQt6.QtGui import QColor, QMouseEvent, QDrag, QPixmap

from lcars.ui.base.widgets import LCARSButton, LCARSElbow
from lcars.themes.palette import get_lcars_font_style
from lcars.engineering.editor.edit_mode import EditMode

from lcars.core.vision import UIAnalyzer


class ArchitectCanvas(QFrame):
    """Integrated Drawing area."""
    selectionChanged = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #050505; border: 1px solid #111;")
        self.setMouseTracking(True)
        self.nodes = []
        self.selected_node = None
        self.background_image = None
        
        # Professional manipulation substrate
        self.edit_mode = EditMode(self)
        self.edit_mode.enabled = True
        self.edit_mode.set_elements(self.nodes)

    def set_background(self, pixmap):
        self.background_image = pixmap
        self.update()

    def mousePressEvent(self, event):
        # Implementation of "Click-to-Add" feature from user's old constructor
        parent = self.parentWidget()
        if parent and hasattr(parent, 'active_tool') and parent.active_tool:
            self._create_node_at(parent.active_tool, event.position().toPoint())
            return
        
        # Deselect logic
        if self.selected_node:
            self.selected_node.update_style(False)
            self.selected_node = None
        super().mousePressEvent(event)

    def _create_node_at(self, ntype, pos):
        # Access the Architect parent to use its creation factory
        parent = self.parentWidget()
        if hasattr(parent, 'create_widget_at'):
            parent.create_widget_at(ntype, pos)

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QPen
        qp = QPainter(self)
        
        # Draw Background Image (Blueprint)
        if self.background_image:
            qp.drawPixmap(self.rect(), self.background_image)

        qp.setPen(QPen(QColor(30,30,30), 1))
        # Neural Grid
        for x in range(0, self.width(), 50): qp.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), 50): qp.drawLine(0, y, self.width(), y)
        qp.end()

class ArchitectNode(QFrame):
    """Draggable wrapper with LCARS-selection aesthetics."""
    def __init__(self, inner_widget: QWidget, parent=None):
        super().__init__(parent)
        self.inner = inner_widget
        self.inner.setParent(self)
        self.inner.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.resize(inner_widget.size())
        
        self._dragging = False
        self._drag_start = QPoint()
        self.update_style(False)

    def update_style(self, selected: bool):
        color = "#FF9900" if selected else "#444"
        self.setStyleSheet(f"border: 2px solid {color}; background-color: transparent;")

    def mousePressEvent(self, a0):
        if not a0: return
        if a0.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start = a0.position().toPoint()
            canvas = self.parentWidget()
            if canvas and hasattr(canvas, 'selectionChanged'):
                # Deselect old node
                if hasattr(canvas, 'selected_node') and canvas.selected_node:
                    canvas.selected_node.update_style(False)
                
                setattr(canvas, 'selected_node', self)
                self.update_style(True)
                getattr(canvas, 'selectionChanged').emit(self)
            self.raise_()

    def mouseMoveEvent(self, a0):
        if self._dragging and a0:
            delta = a0.position().toPoint() - self._drag_start
            self.move(self.x() + delta.x(), self.y() + delta.y())

    def mouseReleaseEvent(self, a0):
        self._dragging = False

class IsolinearArchitect(QWidget):
    """Integrated LCARS Development Environment."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_tool = None
        self.init_ui()

    def init_ui(self):
        # Professional LCARS layout: Zero margins, strict color-coded regions
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)
        
        # --- LEFT: MATRIX CONTROL (Sidebar) ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(210)
        self.sidebar.setStyleSheet("background-color: transparent;")
        self.palette_layout = QVBoxLayout(self.sidebar)
        self.palette_layout.setContentsMargins(0, 0, 0, 0)
        self.palette_layout.setSpacing(8)
        
        # Upper Junction
        ue = LCARSElbow("top-left")
        ue.setFixedSize(210, 50)
        self.palette_layout.addWidget(ue)
        
        lbl_p = QLabel("MATRIX CONTROL")
        lbl_p.setStyleSheet(f"color: #FFCC00; {get_lcars_font_style(20, 'normal')} padding-left: 10px;")
        self.palette_layout.addWidget(lbl_p)
        
        # Deployment Tools
        tools = [
            ("DEPLOY BUTTON", "BUTTON", "#FF9900"),
            ("DEPLOY ELBOW", "ELBOW", "#3366CC"),
            ("DEPLOY PANEL", "PANEL", "#99CCFF"),
            ("DEPLOY LABEL", "LABEL", "#CC66FF"),
            ("DEPLOY IMAGE", "IMAGE", "#FFCC00"),
            ("DEPLOY CONSOLE", "CONSOLE", "#00FF00")
        ]
        
        for name, ptype, color in tools:
            btn = LCARSButton(name, color, shape="left")
            btn.setFixedSize(200, 40)
            btn.clicked.connect(lambda ch, t=ptype: self.set_tool(t))
            self.palette_layout.addWidget(btn)
        
        self.palette_layout.addStretch()

        # RECONSTRUCTION TOOLS
        self.btn_blueprint = LCARSButton("LOAD BLUEPRINT", "#6699FF", shape="left")
        self.btn_blueprint.setFixedSize(200, 40)
        self.btn_blueprint.clicked.connect(self.load_blueprint)
        self.palette_layout.addWidget(self.btn_blueprint)
        
        # System Link
        self.btn_computer = LCARSButton("MAJEL : RECONSTRUCT", "#CC66FF", shape="left")
        self.btn_computer.setFixedSize(200, 45)
        self.btn_computer.clicked.connect(self.run_reconstruction)
        self.palette_layout.addWidget(self.btn_computer)
        
        self.main_layout.addWidget(self.sidebar)

        # --- CENTER: NEURAL SUBSTRATE (Integrated Canvas) ---
        self.canvas_area = QVBoxLayout()
        self.canvas_area.setSpacing(5)
        
        self.canvas_header = QLabel("◤ ISOLINEAR SUBSTRATE v4.5 // SYSTEM INTEGRATED")
        self.canvas_header.setStyleSheet("color: #333; font-size: 10px; margin-left: 5px;")
        self.canvas_area.addWidget(self.canvas_header)
        
        self.canvas = ArchitectCanvas(self)
        self.canvas.selectionChanged.connect(self.on_selection_changed)
        self.canvas_area.addWidget(self.canvas, 1)
        self.main_layout.addLayout(self.canvas_area, 1)

        # --- RIGHT: PROPERTY RACK (Data Input) ---
        self.inspector_panel = QFrame()
        self.inspector_panel.setFixedWidth(220)
        self.inspector_panel.setStyleSheet("background-color: transparent;")
        self.inspector = QVBoxLayout(self.inspector_panel)
        self.inspector.setContentsMargins(0, 0, 0, 0)
        self.inspector.setSpacing(10)
        
        # Right Junction
        re = LCARSElbow("bottom-right")
        re.setFixedSize(220, 50)
        self.inspector.addWidget(re)

        lbl_i = QLabel("NODE DATA")
        lbl_i.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(18, 'normal')} padding-right: 10px;")
        lbl_i.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.inspector.addWidget(lbl_i)
        
        # LCARS-Styled Inputs
        s_edit = "background: #080808; color: #FFF; border: 1px solid #444; height: 35px; border-radius: 5px; font-family: 'Courier New';"
        
        self.obj_id = QLineEdit(); self.obj_id.setStyleSheet(s_edit)
        self.obj_id.setPlaceholderText("NODE_ID")
        self.inspector.addWidget(self.obj_id)
        
        self.obj_text = QLineEdit(); self.obj_text.setStyleSheet(s_edit)
        self.obj_text.setPlaceholderText("NODE_LABEL")
        self.inspector.addWidget(self.obj_text)
        
        # Gradation Selectors
        self.combo_type = QComboBox(); self.combo_type.setStyleSheet(s_edit)
        self.combo_type.addItems(["VIEW", "MODULE", "THEME", "ERA_TEMPLATE"])
        self.inspector.addWidget(self.combo_type)
        
        self.combo_era = QComboBox(); self.combo_era.setStyleSheet(s_edit)
        self.combo_era.addItems(["24th Century", "25th Century", "23rd Century", "22nd Century", "29th Century"])
        self.inspector.addWidget(self.combo_era)
        
        self.combo_faction = QComboBox(); self.combo_faction.setStyleSheet(s_edit)
        self.combo_faction.addItems(["Federation", "Klingon Empire", "Romulan Star Empire", "Cardassian Union"])
        self.inspector.addWidget(self.combo_faction)
        
        self.inspector.addStretch()
        
        # Commit Node
        self.btn_export = LCARSButton("COMMIT", "#3366CC", shape="right")
        self.btn_export.setFixedSize(210, 50)
        self.btn_export.clicked.connect(self.export_project)
        self.inspector.addWidget(self.btn_export)
        
        self.main_layout.addWidget(self.inspector_panel)

    def set_tool(self, tool_type):
        self.active_tool = tool_type
        print(f"◤ ARCHITECT: Tool active -> {tool_type}")

    def on_selection_changed(self, node):
        if node and node.inner:
            self.obj_id.setText(node.objectName() or "node")
            if hasattr(node.inner, 'text'):
                self.obj_text.setText(node.inner.text())
            elif isinstance(node.inner, QLabel):
                self.obj_text.setText(node.inner.text())

    def load_blueprint(self):
        """Loads a background image for neural reconstruction."""
        path, _ = QFileDialog.getOpenFileName(self, "Open Blueprint", "resources/", "Images (*.png *.jpg *.webp)")
        if path:
            pixmap = QPixmap(path)
            self.canvas.set_background(pixmap)
            self.current_blueprint = path
            print(f"◤ ARCHITECT: Blueprint loaded -> {path}")

    def run_reconstruction(self):
        """Uses UIAnalyzer to auto-deploy nodes based on blueprint vision."""
        if not hasattr(self, 'current_blueprint'):
            print("◤ ARCHITECT: Error - No blueprint loaded.")
            return
        
        if not UIAnalyzer:
            print("◤ ARCHITECT: Error - UIAnalyzer module unavailable.")
            return

        print("◤ ARCHITECT: Initiating Neural Reconstruction...")
        results = UIAnalyzer.analyze_background(self.current_blueprint)
        
        if not results:
            print("◤ ARCHITECT: Reconstruction failed.")
            return

        # Deploy detected faction buttons
        for btn in results.get('faction_buttons', []):
            self.create_widget_at("BUTTON", QPoint(btn['x'], btn['y']))
            if self.canvas.selected_node:
                self.canvas.selected_node.inner.resize(btn['w'], btn['h'])
                self.canvas.selected_node.resize(btn['w'], btn['h'])

        print(f"◤ ARCHITECT: Reconstruction complete. Nodes deployed: {len(results.get('faction_buttons', []))}")

    def open_computer_interface(self):
        """Launches the Majel-class Onboard Computer interface."""
        try:
            from lcars.ui.onboard import
import logging
logger = logging.getLogger(__name__)

 OnboardComputerView
            # If we are in a parent that has a stack, we might want to signal it
            # But for now, showing a frameless window is a good fallback
            self.computer_overlay = OnboardComputerView()
            self.computer_overlay.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            self.computer_overlay.resize(800, 600)
            self.computer_overlay.show()
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            logger.exception("Unhandled exception in %s: %s", __file__, e)
            raise

            pass

    def export_project(self):
        """Routes the project and generates logic bytes."""
        cat = self.combo_type.currentText()
        era = self.combo_era.currentText()
        fac = self.combo_faction.currentText()
        name = self.obj_id.text() or "new_node"
        
        root = Path("c:/Users/Forge/MyProject/LCARS-Framework")
        f_slug = fac.lower().replace(" ", "_").split("_")[0] # e.g. 'federation'
        e_slug = era.lower().replace(" ", "_").split("_")[0] # e.g. '24th'
        
        if "VIEW" in cat:
            # Gradation for views: lcars/ui/views/{faction}/{era}/
            dir_ = root / "lcars" / "ui" / "views" / f_slug / e_slug
        elif "MODULE" in cat:
            # Plugins: plugins/{name}/
            dir_ = root / "plugins" / name.lower()
        else:
            # Themes: lcars/themes/{faction}/
            dir_ = root / "lcars" / "themes" / f_slug

        dir_.mkdir(parents=True, exist_ok=True)
        
        # Write Manifest/Metadata
        meta = {"name": name, "cat": cat, "era": era, "fac": fac, "agent": True}
        if "MODULE" in cat:
            with open(dir_ / "plugin.yaml", "w") as f:
                f.write(f"name: {name}\nversion: 1.0.0\nera: {era}\n")
        else:
            with open(dir_ / f"{name}_manifest.json", "w") as f:
                json.dump(meta, f, indent=4)

        # Generate Source
        self._generate_source(dir_, name, cat, era, fac)
        print(f"✅ EXPORT COMPLETE: {dir_}")

    def _generate_source(self, dir_: Path, name: str, cat: str, era: str, fac: str):
        """Generates LCARS-compliant source code with Majel Agent links."""
        cname = "".join(x.capitalize() for x in name.replace("_", " ").split())
        
        if "MODULE" in cat:
            # Plugin system format
            file_path = dir_ / f"{name.lower()}_plugin.py"
            code = f'from lcars.core.plugin_system import LCARSPlugin\n'
            code += 'try: from lcars.ui.onboard_computer import OnboardComputerView\nexcept: OnboardComputerView = None\n\n'
            code += f'class {cname}Plugin(LCARSPlugin):\n'
            code += '    def on_load(self): return True\n'
            code += '    def on_unload(self): pass\n'
            code += '    def ask_agent(self, q): \n'
            code += '        if OnboardComputerView: \n'
            code += '             c = OnboardComputerView(); c.show()\n'
        elif "VIEW" in cat:
            # View format
            file_path = dir_ / f"{name.lower()}.py"
            code = 'from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel\n'
            code += 'try: from lcars.ui.onboard_computer import OnboardComputerView\nexcept: OnboardComputerView = None\n\n'
            code += f'class {cname}View(QWidget):\n'
            code += '    def __init__(self, parent=None):\n'
            code += '        super().__init__(parent)\n'
            code += '        self.layout = QVBoxLayout(self)\n'
            code += f'        self.layout.addWidget(QLabel("{fac.upper()} {era.upper()} CORE"))\n'
            code += '    def ask_computer(self):\n'
            code += '        if OnboardComputerView: self.c = OnboardComputerView(); self.c.show()\n'
        else:
            # Theme/Other
            file_path = dir_ / f"{name.lower()}_theme.py"
            code = f'# Theme configuration for {fac} ({era})\n'
            code += f'COLORS = {{"primary": "#FF9900", "secondary": "#3366CC"}}\n'

        with open(file_path, "w") as f:
            f.write(code)

    def create_widget_at(self, widget_type: str, pos: QPoint):
        """Standardized LCARS Node Deployment."""
        if "BUTTON" in widget_type:
            inner = LCARSButton("NEW_NODE", "#FF9900")
            inner.resize(140, 40)
        elif "ELBOW" in widget_type:
            inner = LCARSElbow("top-left")
            inner.resize(100, 100)
        elif "PANEL" in widget_type:
            inner = QFrame()
            inner.setStyleSheet("background-color: #222; border: 2px solid #555;")
            inner.resize(200, 150)
        elif "IMAGE" in widget_type:
            inner = QLabel("IMAGE_HOLDER")
            inner.setStyleSheet("border: 1px dashed #666; background-color: #111;")
            inner.setAlignment(Qt.AlignmentFlag.AlignCenter)
            inner.resize(200, 150)
        elif "CONSOLE" in widget_type:
            inner = QTextEdit()
            inner.setStyleSheet("background-color: black; color: #00FF00; border: 1px solid #333; font-family: 'Courier New';")
            inner.setText("◤ SYSTEM_LOG :: INITIALIZING...")
            inner.resize(300, 200)
        else:
            inner = QLabel("SPECIMEN")
            inner.setStyleSheet("color: white; font-family: 'Courier New';")
            inner.resize(100, 30)

        node = ArchitectNode(inner, self.canvas)
        node.move(pos)
        node.show()

        # Sync with EditMode
        self.canvas.nodes.append({
            'widget': node,
            'geom': [pos.x(), pos.y(), inner.width(), inner.height()],
            'color': '#FF9900',
            'text': 'NEW_NODE'
        })

        # Auto-select new node
        if self.canvas.selected_node:
             self.canvas.selected_node.update_style(False)
        self.canvas.selected_node = node
        node.update_style(True)
        self.obj_id.setText(f"node_{len(self.canvas.nodes)}")
        
        print(f"◤ ARCHITECT: Node Deployment -> {widget_type} at {pos.x()}:{pos.y()}")


