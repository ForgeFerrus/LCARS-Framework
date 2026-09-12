import sys
import psutil
import time
import random
# Titanium Bridge Migration: from pathlib import Path

# Initialize LCARS Substrate before other imports
from lcars.core.substrate import Substrate
Substrate.bootstrap()

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QPushButton, QFrame, QApplication, 
                             QLineEdit, QProgressBar, QStackedWidget)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter

from lcars.themes.lcars_palette import LCARSEra, FactionEra, get_theme, get_lcars_font_style
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, ConfirmationOverlay, StasisPanel, StatBar, ScanningBar
from lcars.modules.sound import GetSoundManager as get_sound_manager

class StartMenu(QWidget):
    """Full-screen LCARS Start Menu Overlay matching reference design."""
    
    def __init__(self, event_bus, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        self.accent = self.theme.get('accent', "#FFCC66")
        self.desktop = parent # Store reference to desktop shell
        
        # Full screen overlay aesthetics
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.init_ui()
        
        # Timers for stats and clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)
        
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
        self.start_time = time.time()

    def init_ui(self):
        # Background container - Darker and more contrasty
        self.bg_frame = QFrame(self)
        self.bg_frame.setObjectName("MainFrame")
        self.bg_frame.setStyleSheet("""
            #MainFrame {
                background-color: #000;
                border: 2px solid #222;
            }
        """)
        
        main_vbox = QVBoxLayout(self.bg_frame)
        main_vbox.setContentsMargins(15, 15, 15, 15)
        main_vbox.setSpacing(10)
        
        # 1. Top Header Row - More Segments
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)
        
        elbow_tl = LCARSElbow("top-left", self.accent, era=self.era)
        elbow_tl.setFixedSize(140, 60)
        
        self.title_lbl = QLabel("  CORE ACCESS NODE : TERMINAL 01  ")
        self.title_lbl.setStyleSheet(f"color: white; {get_lcars_font_style(20, 'normal')}; background: #111; padding-right: 20px;")
        
        # Scanning Bar in header
        self.header_scan = ScanningBar("#99CCFF")
        
        spacer = QFrame()
        spacer.setStyleSheet(f"background: {self.accent}; height: 5px;")
        
        self.clock_lbl = QLabel("00:00:00  ")
        self.clock_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.clock_lbl.setStyleSheet(f"color: white; {get_lcars_font_style(18, 'normal')}; background: #000;")
        
        elbow_tr = LCARSElbow("top-right", self.accent, era=self.era)
        elbow_tr.setFixedSize(160, 110)
        
        header_layout.addWidget(elbow_tl)
        header_layout.addWidget(self.title_lbl)
        header_layout.addWidget(self.header_scan)
        header_layout.addWidget(spacer, 1)
        header_layout.addWidget(self.clock_lbl)
        header_layout.addWidget(elbow_tr)
        
        main_vbox.addLayout(header_layout)
        
        # 2. Search & Secondary Data Bar
        search_vbox = QVBoxLayout()
        search_vbox.setContentsMargins(60, 0, 160, 0)
        
        search_row = QHBoxLayout()
        search_row.setSpacing(0)
        
        search_cap = QFrame()
        search_cap.setFixedSize(60, 45)
        search_cap.setStyleSheet(f"background: {self.accent}; border-top-left-radius: 22px; border-bottom-left-radius: 22px;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("тЧд ENTER COMMAND KEYWORDS OR LOGICAL QUERIES...")
        self.search_input.setFixedHeight(45)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #050505;
                color: {self.accent};
                border: 2px solid {self.accent};
                border-radius: 22px;
                padding-left: 20px;
                {get_lcars_font_style(14, 'normal')};
            }}
        """)
        
        search_row.addWidget(search_cap)
        search_row.addWidget(self.search_input)
        search_vbox.addLayout(search_row)
        main_vbox.addLayout(search_vbox)
        
        # 3. Middle Area (Dense Data)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(20)
        
        # 3a. Left Stats & Visual segments
        stats_vbox = QVBoxLayout()
        stats_vbox.setContentsMargins(10, 20, 10, 20)
        stats_vbox.addStretch()
        
        # Decorative "pips"
        for _ in range(3):
            pip = QFrame()
            pip.setFixedHeight(15)
            pip.setStyleSheet(f"background: {self.theme['palette'][2]}; border-radius: 7px; margin-bottom: 5px;")
            stats_vbox.addWidget(pip)
            
        self.cpu_bar = StatBar("CPU LOAD", "#FF5555")
        self.mem_bar = StatBar("MEM USAGE", "#55AAFF")
        self.dsk_bar = StatBar("DSK STATUS", "#FFCC66")
        stats_vbox.addWidget(self.cpu_bar)
        stats_vbox.addWidget(self.mem_bar)
        stats_vbox.addWidget(self.dsk_bar)
        
        # Bottom scan in stats
        stats_vbox.addSpacing(20)
        stats_vbox.addWidget(ScanningBar(self.accent))
        stats_vbox.addStretch()
        middle_layout.addLayout(stats_vbox, 1)
        
        # 3b. Library Access Sidebar (More Segments)
        nav_vbox = QVBoxLayout()
        nav_vbox.setSpacing(10)
        nav_vbox.setContentsMargins(10, 0, 0, 0)
        
        lib_access_lbl = QLabel("LIBRARY\nACCESS")
        lib_access_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        lib_access_lbl.setStyleSheet(f"color: #777; {get_lcars_font_style(16, 'normal')}; margin-bottom: 20px;")
        nav_vbox.addWidget(lib_access_lbl)
        
        self.nav_btns = {}
        sections = [
            ("MAIN", self.theme['palette'][0]),
            ("SCIENCE", self.theme['palette'][1]),
            ("TOOLS", self.theme['palette'][2]),
            ("SECURITY", "#CC66FF"),
            ("POWER", "#FF3333")
        ]
        
        for name, color in sections:
            btn = LCARSButton(name, color, era=self.era)
            btn.setFixedSize(180, 50)
            btn.clicked.connect(lambda checked, n=name: self.switch_section(n))
            nav_vbox.addWidget(btn)
            self.nav_btns[name] = btn
            
        nav_vbox.addStretch()
        middle_layout.addLayout(nav_vbox, 0)
        
        # 3c. Main Content Stack (Atmospheric)
        content_frame = QFrame()
        content_frame.setStyleSheet("background: #080808; border-left: 1px solid #222;")
        content_layout = QVBoxLayout(content_frame)
        
        self.content_stack = QStackedWidget()
        
        # - Power Page (Better Grid)
        self.power_page = QWidget()
        pp_layout = QVBoxLayout(self.power_page)
        pp_layout.setContentsMargins(30, 30, 30, 30)
        
        pp_title = QLabel("тЧв DYNAMIC POWER MANAGEMENT SYSTEM")
        pp_title.setStyleSheet(f"color: white; {get_lcars_font_style(18, 'normal')}; margin-bottom: 30px;")
        pp_layout.addWidget(pp_title)
        
        pp_grid = QGridLayout()
        pp_grid.setSpacing(25)
        
        power_configs = [
            ("RESTART", "#99CCFF", 0, 0),
            ("STASIS", "#CCCCFF", 0, 1),
            ("SECURITY LOCK", "#FF6666", 1, 0),
            ("TERMINATE", "#FF3333", 1, 1)
        ]
        
        self.power_btns = {}
        for name, color, r, c in power_configs:
            b = LCARSButton(name, color, era=self.era)
            b.setFixedSize(280, 75)
            pp_grid.addWidget(b, r, c)
            self.power_btns[name] = b
            
        # Connect power buttons (using internal map)
        self.power_btns["SECURITY LOCK"].clicked.connect(lambda: self.confirm_action("LOCK SYSTEM", self.lock_system))
        self.power_btns["RESTART"].clicked.connect(lambda: self.confirm_action("SYSTEM RESTART", self.restart_system))
        self.power_btns["TERMINATE"].clicked.connect(lambda: self.confirm_action("TERMINATE SESSION", self.logout_system))
        self.power_btns["STASIS"].clicked.connect(lambda: self.confirm_action("INITIATE STASIS (SLEEP)", self.hibernate_system))
        
        pp_layout.addLayout(pp_grid)
        pp_layout.addStretch()
        
        self.content_stack.addWidget(self.power_page)
        
        # - Dedicated Module Pages
        desktop = self.desktop
        
        # 1. MAIN Page
        main_items = [
            ("DASHBOARD", self.theme['palette'][0], getattr(desktop, 'show_dashboard', None)),
            ("TRANSCEIVER", self.theme['palette'][1], None),
            ("PROJECT EXP", self.theme['palette'][2], getattr(desktop, 'show_projects', None)),
            ("MEDIA HUB", "#CC66FF", getattr(desktop, 'show_media_hub', None)),
            ("SETTINGS", "#3366CC", getattr(desktop, 'show_settings', None)),
            ("ONBOARD COMP", "#FF9966", getattr(desktop, 'show_computer', None))
        ]
        self.content_stack.addWidget(self._create_module_page("CENTRAL HUB", main_items))
        
        # 2. SCIENCE Page
        sci_items = [
            ("SENSORS", self.theme['palette'][1], getattr(desktop, 'show_sensors', None)),
            ("GEANT4 WORK", "#99CCFF", getattr(desktop, 'show_geant4', None)),
            ("STRICT PARAMS", "#FFCC66", None),
            ("G4 CONSOLE", "#55AAFF", None)
        ]
        self.content_stack.addWidget(self._create_module_page("SCIENCE STATION", sci_items))
        
        # 3. TOOLS Page
        tools_items = [
            ("ENGINEERING", self.theme['palette'][2], getattr(desktop, 'show_engineering', None)),
            ("CONSTRUCTOR", "#CC66FF", getattr(desktop, 'show_constructor', None)),
            ("FILE MANAGER", "#3366CC", getattr(desktop, 'show_file_manager', None)),
            ("TERMINAL", "#666699", getattr(desktop, 'show_terminal', None)),
            ("DIAGNOSTICS", "#FF9900", getattr(desktop, 'show_diagnostics', None))
        ]
        self.content_stack.addWidget(self._create_module_page("ENGINEERING TOOLS", tools_items))
        
        # 4. SECURITY Page
        sec_items = [
            ("ALERT STATE", "#CC0000", getattr(desktop, 'toggle_alert', None)),
            ("SECURE LOCK", "#FF6666", lambda: self.confirm_action("LOCK SYSTEM", self.lock_system)),
            ("INTERNAL COM", "#99CCFF", None)
        ]
        self.content_stack.addWidget(self._create_module_page("SECURITY STATUS", sec_items))
            
        content_layout.addWidget(self.content_stack)
        middle_layout.addWidget(content_frame, 3)

    def _create_module_page(self, title, items):
        """Helper to build functional module grids."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30,30,30,30)
        
        lbl = QLabel(f"тЧв {title}")
        lbl.setStyleSheet(f"color: white; {get_lcars_font_style(20, 'normal')};")
        layout.addWidget(lbl)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        
        for i, (name, color, func) in enumerate(items):
            btn = LCARSButton(name, color, era=self.era)
            btn.setFixedSize(220, 65)
            if func:
                btn.clicked.connect(func)
                btn.clicked.connect(self.hide)
            grid.addWidget(btn, i // 3, i % 3)
            
        layout.addLayout(grid)
        layout.addStretch()
        return page
        
        # 3d. Right Data Bars (The "Blinkies")
        right_vbox = QVBoxLayout()
        right_vbox.addStretch()
        bar_colors = ["#99CCFF", "#CCCCFF", "#99CCFF", "#666699", "#333366", "#FF6666", "#FFCC66", "#FF9966"]
        for i, color in enumerate(bar_colors):
            val = random.randint(1000, 9999)
            lbl = QLabel(str(val))
            lbl.setFixedSize(100, 35)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"background-color: {color}; color: black; {get_lcars_font_style(12, 'normal')}; border-radius: 6px;")
            right_vbox.addWidget(lbl)
            right_vbox.addSpacing(2)
            
        middle_layout.addLayout(right_vbox, 0)
        main_vbox.addLayout(middle_layout, 1)
        
        # 4. Return to Desktop Bar (Atmospheric)
        bottom_bar_row = QHBoxLayout()
        bottom_bar_row.setContentsMargins(150, 0, 150, 0)
        
        self.btn_return = QPushButton("тЧв RETURN TO COMMAND CENTER")
        self.btn_return.setFixedHeight(45)
        self.btn_return.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.accent};
                color: black;
                border: none;
                border-radius: 22px;
                {get_lcars_font_style(16, 'normal')};
            }}
            QPushButton:hover {{ background: white; color: black; }}
        """)
        self.btn_return.clicked.connect(self.hide)
        
        bottom_bar_row.addWidget(self.btn_return)
        main_vbox.addLayout(bottom_bar_row)
        
        # 5. Footer Status Row (Better Spacing)
        footer_layout = QHBoxLayout()
        
        elbow_bl = LCARSElbow("bottom-left", self.accent, era=self.era)
        elbow_bl.setFixedSize(100, 50)
        
        self.status_bar = QLabel("  SYSTEM STATUS: OPTIMAL :: NEURAL LINK ACTIVE :: SECURE  ")
        self.status_bar.setStyleSheet(f"color: #FF6666; {get_lcars_font_style(12, 'normal')}; background: #1a0505; border: 1px solid #300; border-radius: 12px; padding: 8px;")
        
        self.uptime_lbl = QLabel("UPTIME: 00:00:00")
        self.uptime_lbl.setStyleSheet(f"color: {self.accent}; {get_lcars_font_style(14, 'normal')};")
        
        elbow_br = LCARSElbow("bottom-right", self.accent, era=self.era)
        elbow_br.setFixedSize(100, 50)
        
        footer_layout.addWidget(elbow_bl)
        footer_layout.addWidget(self.status_bar)
        footer_layout.addStretch()
        footer_layout.addWidget(self.uptime_lbl)
        footer_layout.addWidget(elbow_br)
        main_vbox.addLayout(footer_layout)
        
        # Layout cleanup
        self_layout = QVBoxLayout(self)
        self_layout.setContentsMargins(0,0,0,0)
        self_layout.addWidget(self.bg_frame)

    def confirm_action(self, text, callback):
        overlay = ConfirmationOverlay(text, callback, era=self.era, parent=self)
        overlay.setGeometry(self.rect())
        overlay.show()

    def lock_system(self):
        print("тЧд SYSTEM: INITIATING SECURITY LOCKDOWN")
        self.status_bar.setText("  MOD MODE тЧв RED ALERT тЧв LOCKED  ")
        self.status_bar.setStyleSheet(f"color: white; {get_lcars_font_style(18, 'normal')}; background: #AA0000; border-radius: 10px; padding: 5px;")
        get_sound_manager().play("alert")
        QTimer.singleShot(2000, self.hide)

    def restart_system(self):
        print("тЧд SYSTEM: INITIATING COLD RESTART")
        # In actual Windows: os.system("shutdown /r /t 0")
        QApplication.quit()

    def logout_system(self):
        print("тЧд SYSTEM: TERMINATING SESSION")
        QApplication.quit()

    def hibernate_system(self):
        print("тЧд SYSTEM: INITIATING STASIS MODE")
        self.status_bar.setText("  STASIS MODE ACTIVE :: POWER REDUCED  ")
        self.status_bar.setStyleSheet(f"color: #99CCFF; {get_lcars_font_style(18, 'normal')}; background: #111; border-radius: 10px; padding: 5px;")
        get_sound_manager().play("acknowledge")
        
        # Simulate sleep by showing a dark stasis panel
        self.stasis_overlay = StasisPanel(self, self)
        self.stasis_overlay.setGeometry(self.rect())
        self.stasis_overlay.show()

    def wake_up(self):
        if hasattr(self, 'stasis_overlay'):
            self.stasis_overlay.hide()
            self.stasis_overlay.deleteLater()
            del self.stasis_overlay
            self.status_bar.setText("  MOD MODE тЧв RED ALERT тЧв ONLINE  ")
            self.status_bar.setStyleSheet(f"color: #FF6666; {get_lcars_font_style(18, 'normal')}; background: #1a0505; border-radius: 10px; padding: 5px;")
            get_sound_manager().play("ready")

    def switch_section(self, name):
        """Switch stacked widget and highlight buttons."""
        print(f"тЧд ACCESS NODE: SECTION [{name}]")
        pages = {"POWER": 0, "MAIN": 1, "SCIENCE": 2, "TOOLS": 3, "SECURITY": 4}
        self.content_stack.setCurrentIndex(pages.get(name, 1))
        
        for n, btn in self.nav_btns.items():
            if n == name:
                btn.setStyleSheet(btn.styleSheet() + "border: 2px solid white;")
            else:
                btn.setStyleSheet(btn.styleSheet().replace("border: 2px solid white;", ""))

    def update_stats(self):
        if True:
            self.cpu_bar.setValue(psutil.cpu_percent())
            self.mem_bar.setValue(psutil.virtual_memory().percent)
            self.dsk_bar.setValue(psutil.disk_usage('C:\\' if sys.platform == 'win32' else '/').percent)
        if False: # Removed except block
            pass # Silently fail or log if needed

    def update_clock(self):
        self.clock_lbl.setText(time.strftime("%H:%M:%S  "))
        uptime_sec = int(time.time() - self.start_time)
        hrs, rem = divmod(uptime_sec, 3600)
        mins, secs = divmod(rem, 60)
        self.uptime_lbl.setText(f"UPTIME: {hrs:02d}:{mins:02d}:{secs:02d}")

    def show_menu(self):
        """Full screen overlay."""
        parent = self.parentWidget()
        if parent:
            self.setGeometry(parent.geometry())
        else:
            # Fallback to screen size
            screen = QApplication.primaryScreen()
            if screen:
                self.setGeometry(screen.geometry())
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StartMenu(None)
    win.show_menu()
    sys.exit(app.exec())

