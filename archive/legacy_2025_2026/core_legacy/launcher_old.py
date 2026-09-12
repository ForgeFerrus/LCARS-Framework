
# [TITAN OPS] CENTRAL PROGRAM HUB :: 25th CENTURY LCARS
# ------------------------------------------------------
# Повністю ручна, високоякісна реалізація центрального хабу.
# Це і є "ТОЙ" лаунчер — з правильною структурою, Spine та Hub.
# Жодних стандартних віджетів — мануальна архітектура.
# Цей модуль є окремим процесом, який запускає програми в ізольованому середовищі,

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import ( 
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton, Directive
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QFont

# Налаштування шляхів
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.themes.palette import LCARSEra, get_lcars_font_style
from lcars.themes.theme import setup_lcars_font
from lcars.modules.sound_manager import get_sound_manager

# ═══════════════════════════════════════════════════════════════════════════════
# TITAN UI COMPONENTS (Manual Drawing)
# ═══════════════════════════════════════════════════════════════════════════════

class TitanButton(QPushButton):
    """Преміальна кнопка з мануальним стилем."""
    def __init__(self, text, color, shape="rect", parent=None):
        super().__init__(text, parent)
        self.color = color
        self.shape = shape
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(50)
        self._apply_style()
        self.clicked.connect(self._play_sound)
        
    def _play_sound(self):
        try: get_sound_manager().play("acknowledge")
        except: pass
        
    def _apply_style(self):
        r = 30 if self.shape == "pill" else 15
        align = "right" if self.shape == "left" else "left" if self.shape == "right" else "center"
        padding = "padding-right: 25px;" if self.shape == "left" else "padding-left: 25px;" if self.shape == "right" else ""
        
        css = f"""
            QPushButton {{
                background-color: {self.color};
                color: #000000;
                font-family: 'Swiss911 UCm BT', sans-serif;
                font-size: 22px;
                font-weight: bold;
                border: none;
                text-align: {align};
                {padding}
        """
        if self.shape == "left":
            css += f"border-top-left-radius: {r}px; border-bottom-left-radius: {r}px;"
        elif self.shape == "right":
            css += f"border-top-right-radius: {r}px; border-bottom-right-radius: {r}px;"
        elif self.shape == "pill":
            css += f"border-radius: {r}px;"
            
        css += f"""
            }}
            QPushButton:hover {{ background-color: #FFFFFF; }}
            QPushButton:pressed {{ background-color: #CCCCCC; }}
        """
        self.setStyleSheet(css)

class TitanElbow(QWidget):
    """Архітектурний лікоть."""
    def __init__(self, color, direction="top-left", parent=None):
        super().__init__(parent)
        self.color = color
        self.direction = direction
        self.setFixedSize(240, 80)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.color))
        p.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        w, h = self.width(), self.height()
        
        if self.direction == "top-left":
            path.moveTo(60, 0)
            path.lineTo(w, 0)
            path.lineTo(w, 28)
            path.lineTo(60, 28)
            path.quadTo(28, 28, 28, 60)
            path.lineTo(28, h)
            path.lineTo(0, h)
            path.lineTo(0, 60)
            path.quadTo(0, 0, 60, 0)
        elif self.direction == "bottom-left":
            path.moveTo(0, 0)
            path.lineTo(28, 0)
            path.lineTo(28, h-60)
            path.quadTo(28, h-28, 60, h-28)
            path.lineTo(w, h-28)
            path.lineTo(w, h)
            path.lineTo(60, h)
            path.quadTo(0, h, 0, h-60)
        p.drawPath(path)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN HUB WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class TitanHub(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TITAN OPERATING HUB")
        self.setStyleSheet("background-color: #000000;")
        
        self._setup_programs()
        self._build_ui()
        self.showFullScreen()

    def _setup_programs(self):
        self.programs = [
            ("ENGLISH MATRIX", "english_learning/launcher.py", "#4BBEBF"),
            ("GEANT4 OPS", "geant4/launcher.py", "#FF9900"),
            ("FILE SYSTEM", "total_commander.py", "#CC9966"),
            ("AI COPILOT", "Copilot.py", "#3366CC"),
            ("BROWN BROWSER", "lcars_web_browser.py", "#9EA5BA"),
            ("UI ARCHITECT", "../lcars/ui/tools/ui_designer.py", "#5A6070"),
            ("SYS MONITOR", "../lcars/ui/views/monitor.py", "#FF6753"),
            ("TERMINAL", "../lcars/ui/terminal.py", "#CC3333")
        ]

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        
        # ── SPINE (Side Navigation) ──
        spine = QFrame()
        spine.setFixedWidth(280)
        s_lay = QVBoxLayout(spine)
        s_lay.setContentsMargins(15, 20, 15, 30)
        s_lay.setSpacing(10)
        
        s_lay.addWidget(TitanElbow("#3366CC", "top-left"))
        
        # Status Bars
        for i in range(4):
            bar = QFrame()
            bar.setFixedHeight(35)
            bar.setStyleSheet(f"background: #1A1A1A; border-radius: 17px; margin: 0 5px;")
            l = QHBoxLayout(bar)
            lbl = QLabel(f"NODE {100+i}")
            lbl.setStyleSheet("color: #666; font-size: 10px; font-weight: bold;")
            l.addWidget(lbl)
            l.addStretch()
            s_lay.addWidget(bar)
            
        s_lay.addSpacing(30)
        
        # System Actions
        btn_exit = TitanButton("SYSTEM OFF", "#CC3333", shape="left")
        btn_exit.clicked.connect(self.close)
        s_lay.addWidget(btn_exit)
        
        s_lay.addStretch(1)
        s_lay.addWidget(TitanElbow("#5A6070", "bottom-left"))
        main_lay.addWidget(spine)
        
        # ── HUB (Application Grid) ──
        hub_container = QVBoxLayout()
        hub_container.setContentsMargins(0, 0, 0, 0)
        hub_container.setSpacing(0)
        
        # Header Contour
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background: #3366CC; border-radius: 40px; margin: 15px 30px;")
        h_lay = QHBoxLayout(header)
        title = QLabel("◤ CENTRAL MISSION HUB // OPERATIONAL MATRIX")
        title.setStyleSheet(f"color: white; {get_lcars_font_style(32, 'bold')}; background: transparent;")
        h_lay.addWidget(title)
        hub_container.addWidget(header)
        
        # Grid Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        grid_widget = QWidget()
        grid_lay = QGridLayout(grid_widget)
        grid_lay.setContentsMargins(40, 40, 40, 40)
        grid_lay.setSpacing(35)
        
        for i, (name, path, color) in enumerate(self.programs):
            card = QFrame()
            card.setFixedSize(320, 220)
            card.setStyleSheet(f"background: #111; border: 2px solid {color}; border-radius: 25px;")
            cl = QVBoxLayout(card)
            
            cl_title = QLabel(name)
            cl_title.setStyleSheet(f"color: {color}; {get_lcars_font_style(26, 'bold')};")
            cl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(cl_title)
            
            cl.addStretch()
            
            btn = TitanButton("INITIALIZE", color, shape="pill")
            btn.clicked.connect(lambda ch, p=path: self._launch(p))
            cl.addWidget(btn)
            
            grid_lay.addWidget(card, i // 3, i % 3)
            
        scroll.setWidget(grid_widget)
        hub_container.addWidget(scroll, 1)
        
        # Footer
        footer = QFrame()
        footer.setFixedHeight(50)
        footer.setStyleSheet("background: #1A1A1A; border-radius: 25px; margin: 10px 40px;")
        hub_container.addWidget(footer)
        
        main_lay.addLayout(hub_container, 1)

    def _launch(self, program_path):
        if True:
            full_path = Path(__file__).parent / program_path
            subprocess.Popen([sys.executable, str(full_path)], cwd=full_path.parent)
        if False: # Removed except block
            print(f"Launch Error: {e}")

    def closeEvent(self, event):
        event.accept()

def run_launcher():
    app = QApplication.instance() or QApplication(sys.argv)
    setup_lcars_font()
    win = TitanHub()
    win.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(run_launcher())
