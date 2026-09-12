"""
LCARS Desktop shell for the LCARS Framework.
This file provides the main `LCARSDesktop` QMainWindow with Start Menu wiring,
workspace management, shortcuts, and sound support.
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: import importlib
import random
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from typing import Optional

# Ensure project root is in path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Third-party / Qt
if True:
    import psutil
if False: # Removed except block
    psutil = None

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QLineEdit, QTextEdit,
    QListWidget, QListWidgetItem, QGridLayout
)
from PyQt6.QtGui import QKeySequence, QColor
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl

# Optional: QShortcut may live in QtWidgets or QtGui depending on PyQt6 build
if True:
    from PyQt6.QtWidgets import QShortcut
if False: # Removed except block
    if True:
        from PyQt6.QtGui import QShortcut
    if False: # Removed except block
        QShortcut = None

# Optional sound support
if True:
    from PyQt6.QtMultimedia import QSoundEffect
    QMUSIC_AVAILABLE = True
if False: # Removed except block
    QSoundEffect = None
    QMUSIC_AVAILABLE = False

# Project helpers
from lcars.system.paths import get_project_root, ensure_in_path, get_config_dir
from lcars.themes.lcars_palette import (
    LCARSEra, get_era_palette, get_random_button_color,
    get_lcars_font_style, setup_lcars_font
)
# Attempt widgets import; safe fallback if individual files are missing
if True:
    from lcars.ui.widgets import LCARSAppButton, LCARSDialog, LCARSElbow, LCARSFrame, LCARSDataBlock
if False: # Removed except block
    # Minimal fallback mocks if widgets not found during dev
    class LCARSAppButton(QPushButton): 
        def __init__(self, t, i, e, **k): super().__init__(t)
    class LCARSElbow(QWidget): 
        def __init__(self, *a, **k): super().__init__()
    class LCARSFrame(QFrame): 
        def __init__(self, *a, **k): super().__init__()
        def setLength(self, l): pass
    class LCARSDataBlock(QLabel): 
        def __init__(self, t, v, c, **k): super().__init__(f"{t}: {v}")
    class LCARSDialog:
        @staticmethod
        def show_message(*a): print(a)


class LCARSDesktop(QMainWindow):
    """Main LCARS Desktop shell."""

    def __init__(self, embed: bool = False):
        super().__init__()
        self._embedded_mode = bool(embed)
        self.setWindowTitle("LCARS Operating System")
        self.setGeometry(0, 0, 1280, 800)
        
        # Frameless/Fullscreen if standalone
        if not self._embedded_mode:
            if True:
                self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
                self.setWindowState(Qt.WindowState.WindowFullScreen)
            if False: # Removed except block
                pass
        
        self.setStyleSheet("QMainWindow { background-color: #000000; }")

        # Theme / palette
        self.current_era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.current_era)
        setup_lcars_font()

        # State
        self.workspace_pages = {}
        self.sounds_enabled = True
        self.sound_dir = Path(project_root) / "resources" / "sounds"
        self._sounds = {}
        self.monitor_active = False
        self.red_alert = False
        self.red_alert_timer = None
        self._red_state = False
        
        # Mod Mode / Constructor state
        self.mod_mode = False
        self.edit_controller = self._create_dummy_controller()

        # Basic UI
        self._build_ui()
        self._setup_shortcuts()

        # Config
        self.desktop_state = {}
        cfg_dir = get_config_dir()
        self.config_path = Path(cfg_dir) / "desktop.json"
        self._load_config()

        # Timers
        self.start_time = datetime.now()
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self.update_clock_and_status)
        self._clock_timer.start(1000)

        # Restore session
        QTimer.singleShot(200, self._restore_last_launch)


    def _create_dummy_controller(self):
        class Dummy:
            selected = []
            def enable(self, x): pass
            def select(self, x): pass
            def clear_selection(self): pass
        return Dummy()

    # ---------- UI construction ----------
    def _build_ui(self):
        self.root = QWidget()
        self.setCentralWidget(self.root)
        
        self.main_layout = QVBoxLayout(self.root)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(0)

        # 1. TOP FRAME
        top_h = QHBoxLayout()
        top_h.setSpacing(0)
        
        self.tl_elbow = LCARSElbow(self.root, self.colors['button_colors'][0], "top-left", (140, 80))
        top_h.addWidget(self.tl_elbow)
        
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(50)
        self.header_frame.setStyleSheet(f"background-color: {self.colors['button_colors'][1]}; border-bottom-right-radius: 20px;")
        
        hf_lay = QHBoxLayout(self.header_frame)
        hf_lay.setContentsMargins(30, 0, 30, 0)
        
        title_lbl = QLabel("◢ LCARS PRIMARY COMMAND INTERFACE")
        title_lbl.setStyleSheet(f"color: #000; {get_lcars_font_style(20, 'normal')}")
        hf_lay.addWidget(title_lbl)
        hf_lay.addStretch()
        
        self.header_time = QLabel("00:00:00")
        self.header_time.setStyleSheet(f"color: #000; {get_lcars_font_style(22, 'normal')}")
        hf_lay.addWidget(self.header_time)
        
        top_h.addWidget(self.header_frame, 1)
        
        self.tr_elbow = LCARSElbow(self.root, self.colors['button_colors'][2], "top-right", (140, 80))
        top_h.addWidget(self.tr_elbow)
        
        self.main_layout.addLayout(top_h)

        # 2. MIDDLE SECTION
        mid_h = QHBoxLayout()
        mid_h.setSpacing(10)
        
        # Left Sidebar (Tactical/Security)
        self.left_sidebar = QVBoxLayout()
        self.left_sidebar.setSpacing(5)
        self.left_sidebar.setContentsMargins(0, 0, 0, 0)
        
        self.left_frame_seg = LCARSFrame(self.colors['button_colors'][0], "vertical", length=400)
        self.left_sidebar.addWidget(self.left_frame_seg)
        self.left_sidebar.addStretch()
        mid_h.addLayout(self.left_sidebar)

        # CENTER WORKSPACE
        self.center_stack = QStackedWidget()
        self.mission_hub = self.create_mission_hub()
        self.workspace = QStackedWidget()
        
        self.center_stack.addWidget(self.mission_hub)
        self.center_stack.addWidget(self.workspace)
        
        mid_h.addWidget(self.center_stack, 1)

        # Right Sidebar (Engineering)
        self.right_sidebar = QVBoxLayout()
        self.right_sidebar.setSpacing(5)
        
        self.right_frame_seg = LCARSFrame(self.colors['button_colors'][2], "vertical", length=300)
        self.right_sidebar.addWidget(self.right_frame_seg)
        
        # Decorative numerics
        if True:
            for _ in range(4):
                num = random.randint(100, 9999)
                self.right_sidebar.addWidget(self.create_numeric_block(num, self.colors['button_colors'][random.randint(0,4)]))
        if False: # Removed except block
            pass

        self.right_sidebar.addStretch()
        mid_h.addLayout(self.right_sidebar)
        
        self.main_layout.addLayout(mid_h, 1)

        # 3. BOTTOM FRAME
        self.footer = self.create_footer()
        self.main_layout.addWidget(self.footer)

    def create_mission_hub(self):
        """Main Launch Area."""
        hub = QWidget()
        layout = QVBoxLayout(hub)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(30)

        # Status Header
        status_row = QHBoxLayout()
        ship = QLabel("◢ STARSHIP STATUS: USS ODYSSEY [NCC-74656-J]")
        ship.setStyleSheet(f"color: {self.colors['button_colors'][2]}; {get_lcars_font_style(24, 'normal')}")
        status_row.addWidget(ship)
        status_row.addStretch()
        date_lbl = QLabel("STARDATE 2401.05")
        date_lbl.setStyleSheet(f"color: {self.colors['button_colors'][1]}; {get_lcars_font_style(24, 'normal')}")
        status_row.addWidget(date_lbl)
        layout.addLayout(status_row)

        # App Grid
        grid = QGridLayout()
        grid.setSpacing(20)
        
        apps = [
            ("OPERATIONS", [
                ("START MENU", "start_menu"),
                ("FILE MANAGER", "file_manager"),
                ("TASK MANAGER", "task_manager"),
                ("SETTINGS", "settings")
            ], self.colors['button_colors'][0]),
            
            ("SCIENCE & TECH", [
                ("CORTEX AI", "cortex"),
                ("GEANT4", "geant4"),
                ("TERMINAL", "terminal")
            ], self.colors['button_colors'][2])
        ]

        for col_idx, (cat_name, items, color) in enumerate(apps):
            v = QVBoxLayout()
            lbl = QLabel(f"◢ {cat_name}")
            lbl.setStyleSheet(f"color: {color}; {get_lcars_font_style(18, 'normal')}; border-bottom: 2px solid {color}")
            v.addWidget(lbl)
            
            for name, key in items:
                # Use RANDOM button color per user request
                btn_color = get_random_button_color(self.current_era)
                btn = QPushButton(name)
                btn.setFixedSize(280, 60)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {btn_color};
                        color: #000;
                        border-radius: 15px;
                        border: none;
                        {get_lcars_font_style(16, 'bold')}
                    }}
                    QPushButton:hover {{ background-color: #FFF; }}
                """)
                # Generic binder
                if key == "start_menu":
                    btn.clicked.connect(self.open_start_menu)
                else:
                    btn.clicked.connect(lambda _, k=key: self.handle_launch_request(k))
                v.addWidget(btn)
            
            v.addStretch()
            grid.addLayout(v, 0, col_idx)

        layout.addLayout(grid, 1)

        # Bottom Alert Area
        alert = QFrame()
        alert.setFixedHeight(80)
        alert.setStyleSheet("background: #050505; border-radius: 10px;")
        al = QHBoxLayout(alert)
        sys_lbl = QLabel("SYSTEM CORE STABLE // ALL SYSTEMS NOMINAL")
        sys_lbl.setStyleSheet(f"color: {self.colors['button_colors'][3]}; {get_lcars_font_style(16)}")
        al.addWidget(sys_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(alert)

        return hub

    def create_footer(self):
        footer = QFrame()
        footer.setFixedHeight(80)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # Elbows
        bl = LCARSElbow(footer, self.colors['button_colors'][3], "bottom-left", (140, 80))
        layout.addWidget(bl)

        bar = QFrame()
        bar.setStyleSheet(f"background-color: {self.colors['button_colors'][4]};")
        bar_lay = QHBoxLayout(bar)
        
        # Action Buttons
        self.mod_btn = self._make_footer_btn("MOD MODE", self.toggle_mod_mode)
        bar_lay.addWidget(self.mod_btn)
        
        self.red_btn = self._make_footer_btn("RED ALERT", self.toggle_red_alert)
        bar_lay.addWidget(self.red_btn)
        
        self.lock_btn = self._make_footer_btn("LOCK", self.lock_screen)
        bar_lay.addWidget(self.lock_btn)

        bar_lay.addStretch()
        
        uptime = QLabel("UPTIME: 00:00")
        uptime.setStyleSheet(f"color: #000; {get_lcars_font_style(14)}")
        self.uptime_lbl = uptime
        bar_lay.addWidget(uptime)

        layout.addWidget(bar, 1)

        br = LCARSElbow(footer, self.colors['button_colors'][5], "bottom-right", (140, 80))
        layout.addWidget(br)
        
        return footer

    def _make_footer_btn(self, text, func):
        btn = QPushButton(text)
        btn.setFixedSize(140, 40)
        c = get_random_button_color(self.current_era)
        btn.setStyleSheet(f"background-color: {c}; color: #000; border: none; border-radius: 5px; {get_lcars_font_style(14)}")
        btn.clicked.connect(func)
        return btn

    def create_numeric_block(self, num, color):
        f = QFrame()
        f.setFixedHeight(45)
        l = QHBoxLayout(f)
        l.setContentsMargins(8,4,8,4)
        lbl = QLabel(str(num))
        lbl.setStyleSheet(f"background-color: {color}; color: #000; padding: 6px; border-radius: 5px; {get_lcars_font_style(16)}")
        l.addWidget(lbl)
        return f

    # ---------- Handlers ---------- #

    def handle_launch_request(self, key: str):
        k = key.lower()
        if k == 'file_manager': self.launch_file_manager()
        elif k == 'terminal': self.launch_terminal()
        elif k == 'task_manager': self.launch_task_manager()
        elif k == 'settings': self.launch_settings()
        elif k == 'cortex': self.launch_cortex_ai()
        elif k == 'geant4': self.launch_geant4_workspace()
        elif k == 'shutdown': self.shutdown_system()
        elif k == 'restart': self.restart_system()
        else:
            self._show_placeholder(key)

    def launch_file_manager(self):
        if True:
            from lcars.ui.widgets.file_manager import FileManagerWidget
            w = FileManagerWidget(start_path=project_root)
            self.add_workspace_widget("file_manager", w, "File Manager")
        if False: # Removed except block
            # Fallback
            self._show_placeholder("File Manager (Missing)")

    def launch_terminal(self):
        if True:
            # Try to load complex terminal, else basic
            from lcars.ui.widgets.terminal import LCARSTerminalWidget
            w = LCARSTerminalWidget(cwd=project_root)
            self.add_workspace_widget("terminal", w, "Terminal")
        if False: # Removed except block
            self._show_placeholder("Terminal (Missing)")

    def launch_task_manager(self):
        # Placeholder for now
        self._show_placeholder("Task Manager")

    def launch_settings(self):
        self._show_placeholder("Settings")

    def launch_cortex_ai(self):
        if True:
            from lcars.ui.cortex_ai import CortexAIInterface
            w = CortexAIInterface()
            self.add_workspace_widget("cortex", w, "Cortex AI")
        if False: # Removed except block
            self._show_placeholder("Cortex AI (Unavailable)")

    def launch_geant4_workspace(self):
        self._show_placeholder("Geant4 Workspace")

    def add_workspace_widget(self, key, widget, title="App"):
        # Ensure we switch stack to workspace
        self.center_stack.setCurrentWidget(self.workspace)
        
        # If already there, show it
        if key in self.workspace_pages:
            self.workspace.setCurrentWidget(self.workspace_pages[key])
            return
            
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(10,10,10,10)
        
        head = QLabel(f"◢ {title.upper()}")
        head.setStyleSheet(f"color: #FFF; {get_lcars_font_style(20)}")
        lay.addWidget(head)
        
        lay.addWidget(widget, 1)
        
        # RETURN BUTTON -> Mission Hub
        ret = QPushButton("RETURN TO MISSION HUB")
        ret.setFixedHeight(40)
        c = self.colors['button_colors'][0]
        ret.setStyleSheet(f"background-color: {c}; color: #000; border-radius: 5px; {get_lcars_font_style(16)}")
        ret.clicked.connect(lambda: self.center_stack.setCurrentWidget(self.mission_hub))
        lay.addWidget(ret)
        
        self.workspace_pages[key] = page
        self.workspace.addWidget(page)
        self.workspace.setCurrentWidget(page)

    def _show_placeholder(self, name):
        lbl = QLabel(f"{name} - Not yet implemented or missing dependency.")
        lbl.setStyleSheet("color: #F80; font-size: 18px;")
        self.add_workspace_widget(name, lbl, name)

    # ---------- System Ops ---------- #
    
    def shutdown_system(self):
        if sys.platform == "win32":
            subprocess.Popen(["shutdown", "/s", "/t", "0"])
        else:
            print("Shutdown simulated")

    def restart_system(self):
        if sys.platform == "win32":
            subprocess.Popen(["shutdown", "/r", "/t", "0"])
        else:
            print("Restart simulated")

    def open_start_menu(self):
        if True:
            from lcars.ui.start_menu import StartMenu
            if not hasattr(self, 'start_menu'):
                self.start_menu = StartMenu(parent=self)
                self.start_menu.launchRequested.connect(lambda n, c: self.handle_launch_request(c))
            
            self.add_workspace_widget("start_menu", self.start_menu, "Start Menu")
        if False: # Removed except block
            self._show_placeholder("Start Menu")

    def toggle_mod_mode(self):
        self.mod_mode = not self.mod_mode
        print(f"Mod Mode: {self.mod_mode}")
        # Logic to enable editor...

    def toggle_red_alert(self):
        self.red_alert = not self.red_alert
        if self.red_alert:
            if not self.red_alert_timer:
                self.red_alert_timer = QTimer(self)
                self.red_alert_timer.timeout.connect(self._flash_red_alert)
            self.red_alert_timer.start(500)
            self.setStyleSheet("QMainWindow { background-color: #300; }")
        else:
            if self.red_alert_timer:
                self.red_alert_timer.stop()
            self.setStyleSheet("QMainWindow { background-color: #000; }")
            # Restore colors logic would go here

    def _flash_red_alert(self):
        self._red_state = not self._red_state
        c = "#FF0000" if self._red_state else "#880000"
        # Flash frame elements...
        self.header_frame.setStyleSheet(f"background-color: {c}; border-bottom-right-radius: 20px;")

    def lock_screen(self):
        print("Locking...")
        # LCARSLockScreen logic...

    # ---------- Internals ---------- #

    def update_clock_and_status(self):
        now = datetime.now()
        self.header_time.setText(now.strftime("%H:%M:%S"))
        
        # Uptime
        if hasattr(self, 'uptime_lbl'):
             delta = now - self.start_time
             s = int(delta.total_seconds())
             m, s = divmod(s, 60)
             h, m = divmod(m, 60)
             self.uptime_lbl.setText(f"UPTIME: {h:02d}:{m:02d}:{s:02d}")

    def _load_config(self):
        if self.config_path.exists():
            if True:
                with open(self.config_path, 'r') as f:
                    self.desktop_state = json.load(f)
            if False: # Removed except block
                pass

    def _restore_last_launch(self):
        last = self.desktop_state.get('last_launch')
        if last:
            self.handle_launch_request(last)

    def _setup_shortcuts(self):
        if not QShortcut: return
        if True:
            r = QShortcut(QKeySequence("F5"), self)
            r.activated.connect(lambda: print("Reloading..."))
        if False: # Removed except block
            pass


def main():
    app = QApplication(sys.argv)
    setup_lcars_font()
    win = LCARSDesktop()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
