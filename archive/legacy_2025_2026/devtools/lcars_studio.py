"""
LCARS Engineering Studio - The Omnipotent Interface Workplace
A high-fidelity development environment integrated directly into the LCARS Framework.
Combines visual construction, image analysis, and Geant4 project management.
"""

import sys
import json
import logging
import random
import os
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFrame, QStackedWidget, QListWidget, 
    QListWidgetItem, QFileDialog, QScrollArea, QSplitter, QProgressBar,
    QLineEdit, QColorDialog, QSpinBox
)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPalette, QPixmap, QPainter, QPen, QFont

# Enable project-wide imports
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Framework Imports
import lcars
from lcars.core.system import Coordinator
from lcars.core.vision import UIAnalyzer
from lcars.themes.lcars_palette import (
    LCARSEra, FactionEra, get_theme, get_random_button_color,
    get_lcars_font_style, setup_lcars_font
)
from lcars.ui.base.widgets import LCARSButton, LCARSElbow

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lcars.studio")

class DraggableWidget(QFrame):
    """A wrapper that makes any LCARS widget draggable and selectable."""
    selected = pyqtSignal(object)
    
    def __init__(self, widget, parent=None):
        super().__init__(parent)
        self.child_widget = widget
        self.child_widget.setParent(self)
        self.child_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.child_widget)
        
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.dragging = False
        self.drag_start_pos = QPoint()
        
        # UI metadata for the property editor
        self.metadata = {
            "text": getattr(widget, 'text', lambda: "")(),
            "color": getattr(widget, 'current_color', "#336699"),
            "type": type(widget).__name__
        }
        
        self.refresh_style()

    def refresh_style(self, selected=False):
        border = "2px solid #FFCC66" if selected else "1px dashed #444"
        self.setStyleSheet(f"DraggableWidget {{ border: {border}; background: transparent; }}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.pos()
            self.selected.emit(self)
            self.refresh_style(True)

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.drag_start_pos))

    def mouseReleaseEvent(self, event):
        self.dragging = False

class StudioCanvas(QFrame):
    """The main drawing board where widgets are placed and manipulated."""
    widgetSelected = pyqtSignal(object)

    def __init__(self, parent=None, era=LCARSEra.LCARS_25TH):
        super().__init__(parent)
        self.era = era
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: #050505; border: 2px solid #336699; border-radius: 20px;")
        self.background_image = None
        self.widgets = []
        self.selected_node = None
        self.setMinimumSize(1024, 768)

    def add_element(self, widget, pos=QPoint(100, 100)):
        wrapper = DraggableWidget(widget, self)
        wrapper.move(pos)
        wrapper.resize(widget.sizeHint() if widget.sizeHint().isValid() else QSize(120, 40))
        wrapper.selected.connect(self._handle_selection)
        wrapper.show()
        self.widgets.append(wrapper)
        return wrapper

    def _handle_selection(self, node):
        if self.selected_node and self.selected_node != node:
            self.selected_node.refresh_style(False)
        self.selected_node = node
        self.widgetSelected.emit(node)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.background_image:
            scaled_bg = self.background_image.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
            x = (self.width() - scaled_bg.width()) // 2
            y = (self.height() - scaled_bg.height()) // 2
            painter.drawPixmap(x, y, scaled_bg)
        
        painter.setPen(QPen(QColor(0, 102, 153, 50), 1, Qt.PenStyle.SolidLine))
        for x in range(0, self.width(), 40):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), 40):
            painter.drawLine(0, y, self.width(), y)

class LCARSStudio(QMainWindow):
    """The Flagship IDE of the LCARS Framework."""
    
    def __init__(self):
        super().__init__()
        
        # 1. System Integration
        self.coordinator = lcars.get_system()
        if not self.coordinator:
            self.coordinator = Coordinator(headless=True)
            self.coordinator.start()
            lcars.set_system(self.coordinator)
        
        # 2. UI Configuration (LCARS Style)
        self.era = LCARSEra.LCARS_25TH
        self.theme = get_theme(self.era)
        self.accent = self.theme.get('accent', "#FFCC66")
        
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setStyleSheet(f"background-color: #000; color: white;")
        
        setup_lcars_font()
        self.init_ui()
        logger.info("Studio initialized in High-Fidelity Mode.")

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(15, 10, 15, 10)
        
        # --- HEADER ---
        header = QHBoxLayout()
        self.elbow_tl = LCARSElbow("top-left", color=self.accent, era=self.era)
        self.elbow_tl.setFixedSize(180, 80)
        header.addWidget(self.elbow_tl)
        
        title_bar = QFrame()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet(f"background-color: {self.accent}; border-radius: 5px;")
        t_layout = QHBoxLayout(title_bar)
        
        self.lbl_title = QLabel("◤ LCARS ENGINEERING CORE // INTERFACE_SYNTHESIS_STATION")
        self.lbl_title.setStyleSheet(f"color: black; {get_lcars_font_style(20, 'bold')}")
        t_layout.addWidget(self.lbl_title)
        t_layout.addStretch()
        
        self.lbl_clock = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.lbl_clock.setStyleSheet(f"color: black; {get_lcars_font_style(20, 'normal')}")
        t_layout.addWidget(self.lbl_clock)
        header.addWidget(title_bar, 1)
        
        self.main_layout.addLayout(header)

        # --- MAIN WORKSPACE ---
        workspace = QHBoxLayout()
        
        # Sidebar Controls
        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        
        nav = [
            ("CONSTRUCTOR", self.show_constructor, "#FF9966"),
            ("VISION_SCAN", self.show_vision, "#CC99FF"),
            ("PROJECT_LIB", self.show_projects, "#3399FF"),
            ("COMPONENT_GEN", self.show_gen, "#66CC66"),
            ("SYSTEM_LOG", self.show_log, "#FFCC66")
        ]
        
        for text, func, color in nav:
            btn = LCARSButton(text, color=color, era=self.era, shape="left")
            btn.setFixedSize(180, 45)
            btn.clicked.connect(func)
            sidebar.addWidget(btn)
            
        sidebar.addStretch()
        
        # Help / Info Panel
        self.info_panel = QFrame()
        self.info_panel.setFixedWidth(180)
        self.info_panel.setStyleSheet(f"border-left: 4px solid {self.accent}; padding-left: 10px;")
        ip_layout = QVBoxLayout(self.info_panel)
        ip_layout.addWidget(QLabel("◤ PROJECT DATA"))
        self.lbl_proj_count = QLabel(f"PROJS: {len(self.coordinator.project_manager.projects)}")
        self.lbl_proj_count.setStyleSheet("color: #FFCC66; font-size: 14px;")
        ip_layout.addWidget(self.lbl_proj_count)
        sidebar.addWidget(self.info_panel)
        
        btn_exit = LCARSButton("EXIT", color="#444", era=self.era, shape="left")
        btn_exit.setFixedSize(180, 45)
        btn_exit.clicked.connect(self.close)
        sidebar.addWidget(btn_exit)
        
        workspace.addLayout(sidebar)

        # Content Area
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: #000; border: 2px solid #336699; border-radius: 20px;")
        
        self._setup_studio_views()
        
        workspace.addWidget(self.stack, 1)
        self.main_layout.addLayout(workspace, 1)

        # --- FOOTER ---
        footer = QHBoxLayout()
        self.access_btn = LCARSButton("STUDIO / ACCESS", self.accent, era=self.era, shape="left")
        self.access_btn.setFixedSize(240, 65)
        footer.addWidget(self.access_btn)
        
        status_line = QFrame()
        status_line.setFixedHeight(45)
        status_line.setStyleSheet(f"background-color: {self.accent}; border-radius: 5px;")
        footer.addWidget(status_line, 1)
        
        elbow_br = LCARSElbow("bottom-right", color=self.accent, era=self.era)
        elbow_br.setFixedSize(120, 45)
        footer.addWidget(elbow_br)
        
        self.main_layout.addLayout(footer)

        # Timers
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)

    def _setup_studio_views(self):
        # 1. Constructor View (The Workbench)
        self.constructor_view = QWidget()
        cv_layout = QHBoxLayout(self.constructor_view)
        
        self.canvas = StudioCanvas(era=self.era)
        self.canvas.widgetSelected.connect(self._on_widget_selected)
        cv_layout.addWidget(self.canvas, 1)
        
        self.prop_panel = QFrame()
        self.prop_panel.setFixedWidth(280)
        self.prop_panel.setStyleSheet("background: #0a0a0a; border-left: 2px solid #336699; padding: 10px;")
        self.pp_layout = QVBoxLayout(self.prop_panel)
        pp_lbl = QLabel("◤ ELEMENT PROPERTIES")
        pp_lbl.setStyleSheet(f"color: {self.accent}; {get_lcars_font_style(16, 'bold')}")
        self.pp_layout.addWidget(pp_lbl)
        
        # Property Editors (Hidden by default)
        self.edit_group = QWidget()
        eg_layout = QVBoxLayout(self.edit_group)
        
        eg_layout.addWidget(QLabel("IDENTIFIER / TEXT:"))
        self.edit_text = QLineEdit()
        self.edit_text.setStyleSheet("background: #111; color: white; border: 1px solid #336699;")
        self.edit_text.textChanged.connect(self._update_widget_text)
        eg_layout.addWidget(self.edit_text)
        
        eg_layout.addWidget(QLabel("PRIMARY_COLOR:"))
        self.btn_color = QPushButton("SELECT COLOR")
        self.btn_color.setStyleSheet("background: #222; color: #FFCC66;")
        self.btn_color.clicked.connect(self._pick_color)
        eg_layout.addWidget(self.btn_color)
        
        dim_layout = QHBoxLayout()
        eg_layout.addWidget(QLabel("DIMENSIONS (W x H):"))
        self.spin_w = QSpinBox(); self.spin_w.setRange(20, 1000)
        self.spin_h = QSpinBox(); self.spin_h.setRange(20, 1000)
        self.spin_w.valueChanged.connect(self._update_widget_size)
        self.spin_h.valueChanged.connect(self._update_widget_size)
        dim_layout.addWidget(self.spin_w); dim_layout.addWidget(self.spin_h)
        eg_layout.addLayout(dim_layout)
        
        self.btn_delete = LCARSButton("DELETE NODE", color="#CC3333")
        self.btn_delete.clicked.connect(self._delete_widget)
        eg_layout.addSpacing(20)
        eg_layout.addWidget(self.btn_delete)
        
        self.pp_layout.addWidget(self.edit_group)
        self.edit_group.setVisible(False)
        
        self.prop_info = QLabel("NO ELEMENT SELECTED\nSelect a node on the canvas\nto modify its attributes.")
        self.prop_info.setStyleSheet("color: #666; font-size: 13px;")
        self.prop_info.setWordWrap(True)
        self.pp_layout.addWidget(self.prop_info)
        
        self.pp_layout.addStretch()
        
        btn_save = LCARSButton("SAVE INTERFACE", color="#33CC66")
        btn_save.clicked.connect(self._save_interface)
        self.pp_layout.addWidget(btn_save)
        
        cv_layout.addWidget(self.prop_panel)
        self.stack.addWidget(self.constructor_view)
        
        # 2. Vision Scan View
        self.vision_view = QWidget()
        vv_layout = QVBoxLayout(self.vision_view)
        vv_layout.setContentsMargins(50, 50, 50, 50)
        self.lbl_v_status = QLabel("◤ INSERT INTERFACE TEMPLATE FOR SPATIAL ANALYSIS")
        self.lbl_v_status.setStyleSheet(get_lcars_font_style(24, 'bold'))
        self.lbl_v_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vv_layout.addWidget(self.lbl_v_status)
        
        btn_v_load = LCARSButton("INITIATE SCAN", color="#CC99FF")
        btn_v_load.clicked.connect(self._vision_load)
        vv_layout.addWidget(btn_v_load, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.v_progress = QProgressBar()
        self.v_progress.setVisible(False)
        self.v_progress.setFixedHeight(30)
        self.v_progress.setStyleSheet("QProgressBar { border: 2px solid #336699; border-radius: 5px; background: #000; text-align: center; color: white; } QProgressBar::chunk { background-color: #FFCC66; }")
        vv_layout.addWidget(self.v_progress)
        
        self.stack.addWidget(self.vision_view)

        # 3. Project Lib View
        self.project_view = QWidget()
        pv_layout = QHBoxLayout(self.project_view)
        
        left_p = QVBoxLayout()
        p_title = QLabel("◤ ENTERPRISE PROJECT DATABASE")
        p_title.setStyleSheet(f"color: {self.accent}; {get_lcars_font_style(20, 'bold')}")
        left_p.addWidget(p_title)
        
        self.project_list = QListWidget()
        self.project_list.setStyleSheet("background: #050505; color: #FFCC66; border: 1px solid #336699; font-size: 16px; padding: 10px;")
        self.project_list.itemClicked.connect(self._on_project_selected)
        left_p.addWidget(self.project_list)
        pv_layout.addLayout(left_p, 1)
        
        self.detail_panel = QFrame()
        self.detail_panel.setFixedWidth(400)
        self.detail_panel.setStyleSheet("background: #0a0a0a; border-left: 2px solid #336699; padding: 15px;")
        dp_layout = QVBoxLayout(self.detail_panel)
        
        self.lbl_det_title = QLabel("◤ PROJECT_NAME")
        self.lbl_det_title.setStyleSheet(f"color: {self.accent}; {get_lcars_font_style(24, 'bold')}")
        dp_layout.addWidget(self.lbl_det_title)
        
        self.txt_det_info = QLabel("Select a project from the registry to view metrics and hardware specifications.")
        self.txt_det_info.setStyleSheet("color: white; font-size: 14px;")
        self.txt_det_info.setWordWrap(True)
        dp_layout.addWidget(self.txt_det_info)
        
        dp_layout.addStretch()
        
        self.btn_open_proj = LCARSButton("ENGINEER", color="#3399FF")
        self.btn_open_proj.setFixedSize(200, 50)
        self.btn_open_proj.setEnabled(False)
        dp_layout.addWidget(self.btn_open_proj, 0, Qt.AlignmentFlag.AlignCenter)
        
        pv_layout.addWidget(self.detail_panel)
        self.stack.addWidget(self.project_view)
        
        # 4. Component Gen View
        self.gen_view = QWidget()
        gv_layout = QVBoxLayout(self.gen_view)
        gv_layout.addWidget(QLabel("◤ SCHEMATIC_COMPONENTS"))
        
        comp_grid = QHBoxLayout()
        components = [
            ("BRICK_BUTTON", "#FFCC66"),
            ("ELBOW_JOINT", "#336699"),
            ("DATA_PANEL", "#FF9966"),
            ("STATUS_READOUT", "#66CC66")
        ]
        
        for name, color in components:
            c_btn = LCARSButton(name, color=color, era=self.era)
            c_btn.setFixedSize(160, 60)
            c_btn.clicked.connect(lambda ch, n=name: self._add_component_to_canvas(n))
            comp_grid.addWidget(c_btn)
            
        gv_layout.addLayout(comp_grid)
        gv_layout.addStretch()
        self.stack.addWidget(self.gen_view)
        
        # 5. Log View
        self.log_view = QWidget()
        lv_layout = QVBoxLayout(self.log_view)
        lv_layout.addWidget(QLabel("◤ CORE_SYSTEM_LOGS"))
        self.log_text = QListWidget()
        self.log_text.setStyleSheet("background: black; color: #00FF00; font-family: 'Consolas'; font-size: 12px;")
        lv_layout.addWidget(self.log_text)
        self.stack.addWidget(self.log_view)

    def _add_component_to_canvas(self, type_name):
        self.show_constructor()
        new_btn = LCARSButton(type_name, color="#336699", era=self.era)
        self.canvas.add_element(new_btn)
        logger.info(f"Deployed component: {type_name}")

    def _on_widget_selected(self, wrapper):
        self.edit_group.setVisible(True)
        self.prop_info.setVisible(False)
        
        # Block signals while setting values
        self.edit_text.blockSignals(True)
        self.spin_w.blockSignals(True)
        self.spin_h.blockSignals(True)
        
        self.edit_text.setText(wrapper.child_widget.text())
        self.spin_w.setValue(wrapper.width())
        self.spin_h.setValue(wrapper.height())
        
        self.edit_text.blockSignals(False)
        self.spin_w.blockSignals(False)
        self.spin_h.blockSignals(False)

    def _update_widget_text(self, text):
        if self.canvas.selected_node:
            self.canvas.selected_node.child_widget.setText(text)
            self.canvas.selected_node.metadata["text"] = text

    def _update_widget_size(self):
        if self.canvas.selected_node:
            self.canvas.selected_node.setFixedSize(self.spin_w.value(), self.spin_h.value())

    def _pick_color(self):
        if self.canvas.selected_node:
            color = QColorDialog.getColor()
            if color.isValid():
                hex_color = color.name().upper()
                self.canvas.selected_node.child_widget.set_color(hex_color)
                self.canvas.selected_node.metadata["color"] = hex_color

    def _delete_widget(self):
        if self.canvas.selected_node:
            self.canvas.widgets.remove(self.canvas.selected_node)
            self.canvas.selected_node.setParent(None)
            self.canvas.selected_node = None
            self.edit_group.setVisible(False)
            self.prop_info.setVisible(True)

    def _save_interface(self):
        data = []
        for w in self.canvas.widgets:
            data.append({
                "type": type(w.child_widget).__name__,
                "text": w.child_widget.text(),
                "x": w.x(),
                "y": w.y(),
                "w": w.width(),
                "h": w.height(),
                "color": w.child_widget.current_color
            })
        
        path, _ = QFileDialog.getSaveFileName(self, "Save Interface", "data/", "JSON (*.json)")
        if path:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Interface saved to {path}")

    def _refresh_projects(self):
        self.project_list.clear()
        projects = self.coordinator.project_manager.projects
        for name in sorted(projects.keys()):
            item = QListWidgetItem(f" [ PROJECT ] {name}")
            self.project_list.addItem(item)
        self.lbl_proj_count.setText(f"PROJS: {len(projects)}")

    def _on_project_selected(self, item):
        name = item.text().replace(" [ PROJECT ] ", "")
        proj = self.coordinator.project_manager.projects.get(name)
        if proj:
            self.lbl_det_title.setText(f"◤ {proj.name}")
            info = f"PATH: {proj.path}\n\n"
            info += f"BUILD: {proj.build_dir or 'NOT_FOUND'}\n"
            info += f"EXE: {proj.executable or 'NOT_CONFIGURED'}\n\n"
            info += f"DESCRIPTION:\n{proj.description or 'No analytical data available.'}"
            self.txt_det_info.setText(info)
            self.btn_open_proj.setEnabled(True)

    def _update_clock(self):
        self.lbl_clock.setText(datetime.now().strftime("%H:%M:%S"))

    def show_constructor(self): self.stack.setCurrentIndex(0)
    def show_vision(self): self.stack.setCurrentIndex(1)
    def show_projects(self): 
        self._refresh_projects()
        self.stack.setCurrentIndex(2)
    def show_gen(self): pass
    def show_log(self): self.stack.setCurrentIndex(3)

    def _vision_load(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select UI Template", "resources/", "Images (*.png *.jpg *.webp)")
        if path:
            self.v_progress.setVisible(True)
            self.v_progress.setValue(30)
            self.lbl_v_status.setText(f"◤ ANALYZING bluePRINT: {os.path.basename(path)}...")
            QTimer.singleShot(1500, lambda: self._complete_vision(path))

    def _complete_vision(self, path):
        self.v_progress.setValue(100)
        results = UIAnalyzer.analyze_background(path)
        if results:
            self.canvas.background_image = QPixmap(path)
            # Automap buttons found by vision engine
            for b in results.get('buttons', []) + results.get('faction_buttons', []):
                new_btn = LCARSButton("SCANNED_NODE", color="#FF9933", era=self.era)
                wrapper = self.canvas.add_element(new_btn, QPoint(b['x'], b['y']))
                wrapper.setFixedSize(b['w'], b['h'])
            
            self.stack.setCurrentIndex(0)
            self.v_progress.setVisible(False)
            self.canvas.update()
        else:
            self.lbl_v_status.setText("◤ ANALYSIS FAILURE: NO INTERFACE DETECTED")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LCARSStudio()
    window.show()
    sys.exit(app.exec())

    def init_ui(self):
        # Apply dark studio theme
        self.setStyleSheet("background-color: #111; color: #CCC; font-family: 'Segoe UI', Arial;")
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(5, 5, 5, 5)

        # --- TOP: TOOLBAR & PROJECT BROWSER ---
        top_bar = QFrame()
        top_layout = QHBoxLayout(top_bar)
        
        self.lbl_status = QLabel("◤ LCARS STUDIO | CONNECTED TO GEANT4 CLUSTER")
        self.lbl_status.setStyleSheet("color: #FFCC66; font-weight: bold; font-size: 14px;")
        top_layout.addWidget(self.lbl_status)
        
        top_layout.addStretch()
        
        self.btn_analyze = QPushButton("IMAGE ANALYSIS")
        self.btn_analyze.clicked.connect(self.open_vision_tool)
        top_layout.addWidget(self.btn_analyze)
        
        self.btn_save = QPushButton("COMPILE & SAVE")
        self.btn_save.setStyleSheet("background-color: #336699; color: white;")
        top_layout.addWidget(self.btn_save)
        
        layout.addWidget(top_bar)

        # --- MAIN: MULTI-PANE VIEW ---
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # A. LEFT: COMPONENT PALETTE & PROJECTS
        left_panel = QFrame()
        left_panel.setFixedWidth(250)
        lp_layout = QVBoxLayout(left_panel)
        
        lp_layout.addWidget(QLabel("◤ COMPONENT PALETTE"))
        self.palette_list = QListWidget()
        self.palette_list.addItem("LCARS Button (Standard)")
        self.palette_list.addItem("LCARS Elbow (Corner)")
        self.palette_list.addItem("LCARS Data Panel")
        self.palette_list.addItem("Geant4 Monitor")
        lp_layout.addWidget(self.palette_list)
        
        lp_layout.addWidget(QLabel("◤ GEANT4 PROJECTS"))
        self.project_list = QListWidget()
        self._refresh_projects()
        lp_layout.addWidget(self.project_list)
        
        main_splitter.addWidget(left_panel)
        
        # B. CENTER: CANVAS
        self.canvas_scroll = QScrollArea()
        self.canvas = StudioCanvas()
        self.canvas_scroll.setWidget(self.canvas)
        self.canvas_scroll.setWidgetResizable(True)
        main_splitter.addWidget(self.canvas_scroll)
        
        # C. RIGHT: PROPERTY INSPECTOR
        right_panel = QFrame()
        right_panel.setFixedWidth(280)
        rp_layout = QVBoxLayout(right_panel)
        rp_layout.addWidget(QLabel("◤ PROPERTY INSPECTOR"))
        
        self.prop_editor = QFrame()
        self.prop_editor.setStyleSheet("background: #1a1a1a; border-radius: 5px;")
        pe_layout = QVBoxLayout(self.prop_editor)
        pe_layout.addWidget(QLabel("X / Y / W / H"))
        pe_layout.addWidget(QLabel("Text Content"))
        pe_layout.addWidget(QLabel("Linked Signal"))
        pe_layout.addStretch()
        rp_layout.addWidget(self.prop_editor)
        
        main_splitter.addWidget(right_panel)
        
        layout.addWidget(main_splitter, 1)

    def _refresh_projects(self):
        """Fetches live projects from the ProjectManager."""
        self.project_list.clear()
        projects = self.coordinator.project_manager.projects
        for name in sorted(projects.keys()):
            item = QListWidgetItem(f"◎ {name}")
            self.project_list.addItem(item)

    def open_vision_tool(self):
        """Launches the background analyzer."""
        path, _ = QFileDialog.getOpenFileName(self, "Load Interface Blueprint", "resources/", "Images (*.png *.jpg)")
        if path:
            self.canvas.set_background(path)
            # Run vision engine
            results = UIAnalyzer.analyze_background(path)
            self._apply_vision_results(results)

    def _apply_vision_results(self, results):
        """Automatically places buttons on the canvas based on image analysis."""
        if not results: return
        
        # Auto-populate faction buttons
        for btn_data in results.get('faction_buttons', []):
            self.canvas.add_widget(
                LCARSButton, 
                QPoint(btn_data['x'], btn_data['y']),
                {'text': 'NAV', 'color': '#FF9966'}
            )
        
        self.lbl_status.setText(f"◤ VISION ENGINE: DETECTED {len(results.get('faction_buttons', []))} CORE REGIONS")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LCARSStudio()
    window.showMaximized()
    sys.exit(app.exec())
