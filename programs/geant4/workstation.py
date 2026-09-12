import sys
from pathlib import Path
import sys

# --- СИСТЕМНА ІНІЦІАЛІЗАЦІЯ ---
current_file = Path(__file__).resolve()
# lcars/programs/geant4/workstation.py -> root is 4 levels up
project_root = current_file.parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QStackedWidget, QFrame, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

from lcars.themes.palette import (LCARSEra, get_theme, get_lcars_font_style,
                                        get_random_button_color)
from lcars.ui.base.widgets import (LCARSButton, LCARSElbow, ScanningBar, 
                                   LCARSContour, DataBlock, StatBar)
from .bridge import EnterpriseBridge

class Geant4Workstation(QWidget):
    """
    Geant4 Simulation Control Widget.
    Designed to be embedded in the Main LCARS Desktop.
    Uses dynamic LCARS theming (Era/Faction).
    """
    def __init__(self, parent=None, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__(parent)
        self.bridge = EnterpriseBridge()
        self.current_project = None
        
        self.era = era
        self.faction = faction
        self.theme = get_theme(self.era, self.faction)
        self.accent = self.theme['accent']
        self.secondary = self.theme['secondary']
        
        # make this top‑level widget look like an LCARS panel rather than a
        # normal OS window. ################################################################################
        # The Qt.WindowType.FramelessWindowHint removes the title bar and
        # borders; WindowStaysOnTopHint keeps it visible over other apps.
        # A translucent background attribute lets us draw a full‑sized
        # coloured rectangle without the default white.
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Ensure background matches theme
        self.setStyleSheet(f"background-color: {self.theme['bg']}; color: {self.theme['text']};")
        
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        # --- 1. HEADER (Elbow + Title) ---
        header = QHBoxLayout()
        header.setSpacing(5)
        
        self.elbow = LCARSElbow("top-left", color=self.accent, era=self.era, faction=self.faction)
        self.elbow.setMinimumSize(100, 60)
        header.addWidget(self.elbow)

        title_bar = LCARSContour(color=self.secondary, height=30, era=self.era, faction=self.faction)
        t_layout = QHBoxLayout(title_bar)
        t_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel(f"GEANT4 SIMULATION WORKSTATION // {self.era.value.upper()}")
        title.setStyleSheet(f"color: {self.theme['bg']}; {get_lcars_font_style(20, 'normal')}")
        t_layout.addWidget(title)
        
        header.addWidget(title_bar, 1)
        
        # Add a decorative cap
        cap = QFrame()
        cap.setMinimumSize(60, 30)
        cap.setStyleSheet(f"background-color: {self.accent}; border-bottom-right-radius: 30px;")
        header.addWidget(cap)
        
        self.layout.addLayout(header)

        # --- 2. BODY (Sidebar + Content + Right Info) ---
        body = QHBoxLayout()
        body.setSpacing(5)

        # LEFT SIDEBAR
        sidebar = QVBoxLayout()
        sidebar.setSpacing(5)
        
        self.buttons = {}
        btn_defs = [
            ("PROJECTS", 0),
            ("VISUALIZER", 1), 
            ("DETECTOR", 2), 
            ("DATA HUB", 3),
            ("IDE", 4)
        ]
        
        palette = self.theme['palette']
        for i, (text, idx) in enumerate(btn_defs):
            # Cycle through palette colors
            col = palette[i % len(palette)]
            btn = LCARSButton(text, col, shape="left", era=self.era, faction=self.faction)
            btn.setMinimumSize(160, 50)
            btn.clicked.connect(lambda checked, x=idx: self.display.setCurrentIndex(x))
            sidebar.addWidget(btn)
            self.buttons[text] = btn
            
        sidebar.addSpacing(20)
        self.btn_run = LCARSButton("SIMULATION RUN", self.theme['alerts'][0], shape="left", era=self.era, faction=self.faction)
        self.btn_run.setMinimumSize(160, 50)
        self.btn_run.clicked.connect(self.run_simulation)
        self.btn_run.setEnabled(False) 
        sidebar.addWidget(self.btn_run)
        
        sidebar.addStretch()
        
        # Vertical Scanning Bar
        self.scan_bar = ScanningBar(self.accent, orientation="vertical", faction=self.faction)
        sidebar.addWidget(self.scan_bar, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Elbow Bottom Left
        self.elb_bl = LCARSElbow("bottom-left", color=self.accent, era=self.era, faction=self.faction)
        self.elb_bl.setMinimumSize(160, 80)
        sidebar.addWidget(self.elb_bl)
        
        body.addLayout(sidebar)

        # CENTER DISPLAY
        self.display_frame = QFrame()
        # Ensure it has LCARS look (borders on top/bottom/right potentially)
        self.display_frame.setStyleSheet(f"background: {self.theme['bg']}; border-top: 4px solid {self.secondary}; border-bottom: 4px solid {self.accent};")
        
        d_layout = QVBoxLayout(self.display_frame)
        d_layout.setContentsMargins(10, 10, 10, 10)
        
        self.display = QStackedWidget()
        self.display.setStyleSheet("background: transparent; border: none;")

        # Page 0: Projects
        self.display.addWidget(self._create_projects_page())
        # Page 1: Visualizer
        self.display.addWidget(self._create_visualizer_page())
        # Page 2: Detector
        self.display.addWidget(self._create_detector_page())
        # Page 3: Data Hub
        self.display.addWidget(self._create_data_page())
        # Page 4: IDE / workspace
        self.display.addWidget(self._create_ide_page())

        d_layout.addWidget(self.display)
        body.addWidget(self.display_frame, 1) # Expand

        self.layout.addLayout(body, 1)
        
        # --- 3. FOOTER (Optional, usually included in sidebar elbow for pure LCARS) ---
        # We can add a simple bottom contour for closure
        footer = QHBoxLayout()
        footer.setContentsMargins(165, 0, 0, 0) # Offset for sidebar width
        f_cont = LCARSContour(color=self.secondary, height=20, era=self.era, faction=self.faction)
        footer.addWidget(f_cont)
        self.layout.addLayout(footer)

    def _create_projects_page(self):
        p = QWidget()
        l = QVBoxLayout(p)
        l.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        lbl = QLabel("SYSTEM FILE MANAGER ACCESS")
        lbl.setStyleSheet(f"color: {self.accent}; {get_lcars_font_style(24, 'normal')}")
        l.addWidget(lbl)
        
        l.addSpacing(20)
        
        btn_open = LCARSButton("OPEN PROJECT FOLDER", self.theme['palette'][2], shape="rect", era=self.era, faction=self.faction)
        btn_open.setMinimumSize(300, 60)
        btn_open.clicked.connect(self.open_project_dialog)
        l.addWidget(btn_open)
        
        l.addSpacing(20)
        
        self.proj_desc = QLabel("STATUS: STANDBY - NO PROJECT LOADED")
        self.proj_desc.setWordWrap(True)
        self.proj_desc.setStyleSheet(f"color: {self.theme['palette'][3]}; {get_lcars_font_style(18, 'normal')}")
        l.addWidget(self.proj_desc)
        
        return p

    def open_project_dialog(self):
        from PyQt6.QtWidgets import QFileDialog
        # use non-native Qt dialog to keep LCARS look instead of Windows file
        # picker
        dlg = QFileDialog(self, "Select Enterprise Project")
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        # start at last known root if available
        if hasattr(self.bridge, 'root') and self.bridge.root is not None:
            dlg.setDirectory(str(self.bridge.root))
        # avoid native (Windows) style
        dlg.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        if dlg.exec():
            folder = dlg.selectedFiles()[0]
            if folder:
                self.load_manual_project(folder)

    def load_manual_project(self, folder_path):
        import os
        path = Path(folder_path)
        exes = list(path.rglob("*.exe"))
        release_exes = [e for e in exes if "Release" in str(e) and "CompilerId" not in str(e)]
        candidates = release_exes if release_exes else exes
        
        if candidates:
            exe = max(candidates, key=lambda p: p.stat().st_mtime)
            self.current_project = {
                "name": path.name,
                "path": str(path),
                "exe": str(exe)
            }
            self.proj_desc.setText(f"PROJECT ONLINE: {path.name}\nEXECUTABLE: {exe.name}")
            self.btn_run.setEnabled(True)
            self.btn_run.setText(f"RUN: {path.name}")
            self.proj_desc.setStyleSheet(f"color: {self.theme['palette'][4]}; {get_lcars_font_style(18, 'normal')}")
        else:
            self.proj_desc.setText(f"ERROR: No valid executable (Release/Debug) found in {path.name}")
            self.current_project = None
            self.btn_run.setEnabled(False)
            self.proj_desc.setStyleSheet(f"color: {self.theme['alerts'][0]}; {get_lcars_font_style(18, 'normal')}")

    def run_simulation(self):
        if not self.current_project: return
        exe = self.current_project['exe']
        cwd = self.current_project['path']
        try:
            subprocess.Popen([exe], cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            self.proj_desc.setText(f"Launch Error: {e}")

    def _create_data_page(self):
        p = QWidget()
        l = QVBoxLayout(p)
        
        # Header for Data Page
        d_head = QHBoxLayout()
        lbl = QLabel("DATA ANALYSIS HUB")
        lbl.setStyleSheet(f"color: {self.theme['palette'][1]}; {get_lcars_font_style(24, 'normal')}")
        d_head.addWidget(lbl)
        
        d_head.addStretch()
        self.data_status = QLabel("AWAITING DATA LINK")
        self.data_status.setStyleSheet(f"color: {self.theme['palette'][2]}; {get_lcars_font_style(16, 'normal')}")
        d_head.addWidget(self.data_status)
        l.addLayout(d_head)
        
        # Matplotlib Canvas (optional)
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure

            self.figure = Figure(facecolor=self.theme['bg'], edgecolor='none')
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setStyleSheet(f"background-color: {self.theme['bg']};")
            l.addWidget(self.canvas, 1)
        except ImportError:
            placeholder = QLabel("Matplotlib not available")
            placeholder.setStyleSheet("color: red;")
            l.addWidget(placeholder, 1)
        
        # Toolbar
        tools = QHBoxLayout()
        btn_refresh = LCARSButton("REFRESH DATA", self.theme['palette'][0], shape="rect", era=self.era, faction=self.faction)
        btn_refresh.setMinimumSize(160, 40)
        btn_refresh.clicked.connect(self.load_data)
        tools.addWidget(btn_refresh)
        tools.addStretch()
        l.addLayout(tools)
        
        return p

    def load_data(self):
        if not self.current_project:
            self.data_status.setText("STATUS: OPEN A PROJECT FIRST")
            return
            
        files = self.bridge.get_data_files(self.current_project['path'])
        if not files:
            self.data_status.setText("STATUS: NO DATA FILES FOUND")
            return
            
        target = files[0]
        self.data_status.setText(f"SOURCE: {Path(target).name}")
        
        try:
            import csv
            x = []
            with open(target, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 1 and not row[0].startswith('#'):
                        vals = [float(v) for v in row if v.strip()]
                        if vals:
                            x.extend(vals)
            
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_facecolor(self.theme['bg'])
            
            # Using theme colors for the plot
            grid_color = "#333333"
            spine_color = self.secondary
            bar_color = self.accent
            
            ax.grid(True, color=grid_color, linestyle='-', linewidth=0.5)
            for spine in ax.spines.values():
                spine.set_color(spine_color)
                # Only show left and bottom spines for cleaner look
                spine.set_visible(False)
            
            ax.spines['left'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_color(spine_color)
            ax.spines['bottom'].set_color(spine_color)
            
            ax.tick_params(axis='x', colors=spine_color)
            ax.tick_params(axis='y', colors=spine_color)
            
            if len(x) > 0:
                ax.hist(x, bins=50, color=bar_color, alpha=0.9, edgecolor='none')
                ax.set_title(f"SPECTRUM ANALYSIS: {self.current_project['name']}", color=spine_color, fontsize=14)
            else:
                ax.text(0.5, 0.5, "NO VALID DATA", color=spine_color, ha='center')
                
            self.canvas.draw()
            
        except Exception as e:
            self.data_status.setText(f"ERROR: {str(e)}")

    def _create_ide_page(self):
        """Workspace page with file manager, editor and console."""
        from .ide_widget import IDEWidget
        w = QWidget()
        l = QVBoxLayout(w)
        hdr = QLabel("CODE WORKSPACE")
        hdr.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(24, 'normal')}")
        l.addWidget(hdr)
        l.addWidget(IDEWidget())
        return w

    def _create_visualizer_page(self):
        p = QWidget()
        l = QVBoxLayout(p)
        lbl = QLabel("VISUALIZATION MODULE")
        lbl.setStyleSheet(f"color: {self.theme['palette'][3]}; {get_lcars_font_style(24, 'normal')}")
        l.addWidget(lbl)
        
        # embed the 3D widget
        try:
            from .vispy_widget import Vispy3DWidget
            try:
                vispy_tab = Vispy3DWidget()
                l.addWidget(vispy_tab, 1)
            except TypeError as te:
                # signature mismatch or other init issue – fall back gracefully
                print("Vispy3DWidget init failed:", te)
                raise ImportError
        except ImportError:
            # fallback placeholder if the widget is unavailable or failed to init
            frame = QFrame()
            frame.setStyleSheet(f"background: #050505; border: 2px dashed {self.theme['palette'][3]};") 
            fl = QVBoxLayout(frame)
            fl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg = QLabel("GEANT4 VISUALIZATION RUNNING EXTERNALLY")
            msg.setStyleSheet(f"color: {self.theme['palette'][3]}; {get_lcars_font_style(18, 'normal')}")
            fl.addWidget(msg)
            l.addWidget(frame, 1)
        return p

    def _create_detector_page(self):
        p = QWidget()
        l = QVBoxLayout(p)
        lbl = QLabel("DETECTOR CONSTRUCTION")
        lbl.setStyleSheet(f"color: {self.theme['palette'][5]}; {get_lcars_font_style(24, 'normal')}")
        l.addWidget(lbl)
        
        l.addSpacing(20)
        
        form_layout = QVBoxLayout()
        params = ["WORLD SIZE X", "WORLD SIZE Y", "TARGET MATERIAL", "BEAM ENERGY"]
        for i, param in enumerate(params):
            row = QHBoxLayout()
            # Use alternating colors
            color = self.theme['palette'][i % len(self.theme['palette'])]
            
            pl = DataBlock(param, "EDIT", color, parent=p)
            row.addWidget(pl)
            row.addStretch()
            
            form_layout.addLayout(row)
            
        l.addLayout(form_layout)
        l.addStretch()
        return p

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    # Standalone testing with mock parent/theme
    app = QApplication(sys.argv)
    
    # Test with 25th Century Theme
    w = Geant4Workstation(era=LCARSEra.LCARS_25TH)
    # match the behavior of the real launcher: full screen and frameless
    w.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
    w.showMaximized()
    sys.exit(app.exec())
