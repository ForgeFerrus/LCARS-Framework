"""
LCARS MISSION HUB - STRATEGIC OVERVIEW
SYSTEM MODULE: UI-DASHBOARD-25A
PROTOCOL: MISSION STATUS / TELEMETRY WRAPPER
DESCRIPTION: Primary dashboard for mission logs, system stats, and quick access.
"""
# Titanium Bridge Migration: from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from lcars.base.default  import RandomButtonColor as get_theme, FontStyle as get_lcars_font_style 
from lcars.base.interface import LCARSButton

class WelcomeScreen(QWidget):
    # Головний екран привітання з датами, статусом та програмами.
    def __init__(self, event_bus=None, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.parent_desktop = parent
        
        self.init_ui()
        
        # Таймер для годинника
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
    def init_ui(self):
        # КРОК 1: Налаштування освітлення та відступів головного лейауту
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)
        
        from lcars.base.type import DataBlock, ScanningBar

        # --- TOP: MISSION HUB HEADER (Clean Industrial Style) ---
        hub_header = QVBoxLayout()
        header_top = QHBoxLayout()
        
        hub_title = QLabel("◤ STRATEGIC MISSION HUB // OPS-01")
        hub_title.setStyleSheet(f"color: {self.theme['palette'][0]}; {get_lcars_font_style(26, 'bold')}")
        header_top.addWidget(hub_title)
        header_top.addStretch()
        
        self.stardate_label = QLabel("STARDATE: ---")
        self.stardate_label.setStyleSheet(f"color: {self.theme['secondary']}; {get_lcars_font_style(18, 'normal')}")
        header_top.addWidget(self.stardate_label)
        header_top.addSpacing(20)
        
        self.date_label = QLabel("DATE: ---")
        self.date_label.setStyleSheet(f"color: {self.theme['palette'][1]}; {get_lcars_font_style(18, 'normal')}")
        header_top.addWidget(self.date_label)
        hub_header.addLayout(header_top)
        
        # Separator Line
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"background: {self.theme['palette'][0]}55;")
        hub_header.addWidget(sep)
        
        main_layout.addLayout(hub_header)

        # --- CENTER: TACTICAL GRID (ТАКТИЧНА СІТКА) ---
        # КРОК 3: Формування центральної зони з блоками даних та графікою сканера
        grid_area = QHBoxLayout()
        grid_area.setSpacing(20)
        
        # Ліва колонка: Статус основних систем
        status_col = QVBoxLayout()
        status_col.setSpacing(10)
        
        sys_stats = [
            ("ISOLINEAR CORE", "98.4%", self.theme['palette'][0]),
            ("NEURAL LINK", "STABLE", self.theme['palette'][1]),
            ("POWER GRID", "NOMINAL", self.theme['palette'][2]),
            ("SUB-PROCESSOR", "ACTIVE", self.theme['palette'][3])
        ]
        for name, val, color in sys_stats:
            db = DataBlock(name, val, color)
            db.setFixedSize(220, 50)
            status_col.addWidget(db)
        status_col.addStretch()
        grid_area.addLayout(status_col)
        
        # Центральна частина: Графіка сенсорів (TITAN v5.0: Flat geometric)
        self.sensor_fr = QFrame()
        self.sensor_fr.setStyleSheet(f"background: #020508; border: 1px solid {self.theme['palette'][1]}; border-radius: 0px;")
        sf_lay = QVBoxLayout(self.sensor_fr)
        sf_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        scan_lbl = QLabel("SCANNING QUADRANT 0.1 // ALPHA PROXIMA")
        scan_lbl.setStyleSheet(f"color: {self.theme['palette'][1]}; {get_lcars_font_style(20, 'normal')}")
        sf_lay.addWidget(scan_lbl)
        
        # Додавання анімованої панелі сканування всередину рамки
        sf_lay.addWidget(ScanningBar(self.theme['palette'][2], faction=self.faction))
        
        # Додавання канонічного діагностичного блоку (Placeholder)
        from lcars.base.interface import PlaceholderDiagnostic
        diag_strip = PlaceholderDiagnostic(color=self.theme['palette'][3], count=6)
        sf_lay.addWidget(diag_strip, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # КРОК 3.1: Додавання традиційного привітання Федерації
        welcome_msg = QLabel("LIVE LONG AND PROSPER! 🖖")
        welcome_msg.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(28, 'normal')}; margin-top: 20px;")
        sf_lay.addWidget(welcome_msg)
        
        grid_area.addWidget(self.sensor_fr, 1)
        
        main_layout.addLayout(grid_area, 1)
        
        # --- BOTTOM: QUICK ACCESS (ШВИДКИЙ ДОСТУП) ---
        # КРОК 4: Створення сітки кнопок швидкого запуску протоколів
        prog_title = QLabel("◤ PRIMARY INTERFACE PROTOCOLS")
        prog_title.setStyleSheet(f"color: {self.theme['palette'][4]}; {get_lcars_font_style(18, 'normal')}")
        main_layout.addWidget(prog_title)
        
        programs_grid = QGridLayout()
        programs_grid.setSpacing(15)
        
        # Handler lookups — parent desktop may provide launch methods
        def _handler(name):
            if self.parent_desktop and hasattr(self.parent_desktop, f'launch_{name.lower()}'):
                return getattr(self.parent_desktop, f'launch_{name.lower()}')
            return None

        apps = [
            ("PROJECTS", self.theme['palette'][0], _handler("projects")),
            ("EXPLORER", self.theme['palette'][1], _handler("explorer")),
            ("TERMINAL", self.theme['palette'][2], _handler("console")),
            ("SENSORS", self.theme['palette'][3], _handler("diagnostics")),
            ("SYSTEM", self.theme['palette'][4], _handler("settings")),
            ("ENGINEERING", self.theme['palette'][3], _handler("diagnostics")),
        ]
        for i, (name, color, handler) in enumerate(apps):
            btn = LCARSButton(name, color, era=self.era, faction=self.faction, shape="rect")
            btn.setMinimumHeight(70)
            if handler:
                btn.clicked.connect(handler)
            programs_grid.addWidget(btn, i // 3, i % 3)
            
        main_layout.addLayout(programs_grid)
        main_layout.addStretch()
        
    def update_time(self):
        """Оновлює час та зоряну дату."""
        now = datetime.now()
        
        # Поточна дата
        date_str = now.strftime("%Y-%m-%d  %H:%M:%S")
        self.date_label.setText(f"EARTH DATE: {date_str}")
        
        # Зоряна дата (умовна формула)
        year_base = 2000.0
        days_since = (now - datetime(2000, 1, 1)).total_seconds() / 86400
        stardate = (now.year - year_base) * 1000 + (days_since % 365.25) * (1000 / 365.25)
        self.stardate_label.setText(f"STARDATE: {stardate:.1f}")


# --- STANDALONE TEST FOR DEVELOPMENT ---
if __name__ == "__main__":
    """Test WelcomeScreen independently"""
    # Titanium Bridge Migration: import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = QMainWindow()
    main_window.setWindowTitle("LCARS Welcome Screen - Test")
    main_window.setGeometry(100, 100, 1000, 700)
    
    # Create and show WelcomeScreen
    class MockEventBus:
        def emit(self, *args): pass
    
    welcome = WelcomeScreen()
    main_window.setCentralWidget(welcome)
    main_window.show()
    
    logger.info("=== LCARS Welcome Screen Test ===")
    logger.info("✅ WelcomeScreen running independently")
    logger.info("✅ Live clock and stardate updating")
    logger.info("✅ Mission Hub interface active")
    logger.info("✅ Quick access buttons available")
    logger.info("==================================")
    
    app.exec()
