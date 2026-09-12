"""
LCARS Integrated Launcher - Екран вибору фракції та ери.
Дозволяє користувачу налаштувати візуальне середовище системи.
"""
import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from lcars.themes.palette import (
    LCARSEra, LCARSColorGenerator, 
    FactionEra, get_random_button_color
)
from lcars.themes.theme import get_lcars_font_style
from lcars.ui.base.widgets import LCARSButton, ScanningBar
from lcars.modules.sound_manager import get_sound_manager

def log_to_database(component_name, action="LAUNCH"):
    """Записати дію компонента в базу даних"""
    if True:
        # Titanium Bridge Migration: import sqlite3
        # Titanium Bridge Migration: from datetime import datetime
        # Titanium Bridge Migration: from pathlib import Path
        
        # Шлях до бази даних
        db_path = Path(__file__).parent.parent.parent / "data" / "lcars.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Підключення до бази
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Створення таблиці якщо не існує
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ui_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                component TEXT,
                action TEXT,
                details TEXT
            )
        ''')
        
        # Запис логу
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO ui_logs (timestamp, component, action, details)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, component_name, action, f"UI Component {action} successful"))
        
        conn.commit()
        conn.close()
        
        print(f"[DB] Logged: {component_name} - {action}")
        
    if False: # Removed except block
        print(f"[DB] Error logging to database: {e}")

class SelectorView(QWidget):
    """Configuration selector for Faction and Era with proper LCARS architectural framing."""
    selected = pyqtSignal(str, str)  # faction, era
    preview_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_faction = "FEDERATION"
        self.selected_era = "25th"
        self.setup_ui()
        # Початкова синхронізація кольорів згідно з алгоритмом рандомізації
        self._refresh_interface()
        
        # Логування запуску компонента
        log_to_database("SelectorView", "INITIALIZE")

    def setup_ui(self):
        """Build configuration screen with pure LCARS design (no contours)."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # --- PURE LCARS HEADER ---
        self.title_lbl = QLabel("◤ LCARS CONFIGURATION")
        self.title_lbl.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(28, 'bold')};")
        self.main_layout.addWidget(self.title_lbl)

        # --- FACTION SELECTION ---
        faction_label = QLabel("◤ FACTION SELECTION")
        faction_label.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(20, 'bold')}; margin-bottom: 15px;")
        self.main_layout.addWidget(faction_label)
        
        faction_layout = QHBoxLayout()
        faction_layout.setSpacing(20)
        
        self.federation_btn = LCARSButton("FEDERATION", "#FF9900", shape="rectangle")
        self.federation_btn.setMinimumSize(180, 45)
        self.federation_btn.clicked.connect(lambda: self.select_faction("FEDERATION"))
        faction_layout.addWidget(self.federation_btn)
        
        self.klingon_btn = LCARSButton("KLINGON", "#FF3333", shape="rectangle")
        self.klingon_btn.setMinimumSize(180, 45)
        self.klingon_btn.clicked.connect(lambda: self.select_faction("KLINGON"))
        faction_layout.addWidget(self.klingon_btn)
        
        self.romulan_btn = LCARSButton("ROMULAN", "#33FF33", shape="rectangle")
        self.romulan_btn.setMinimumSize(180, 45)
        self.romulan_btn.clicked.connect(lambda: self.select_faction("ROMULAN"))
        faction_layout.addWidget(self.romulan_btn)
        
        self.cardassian_btn = LCARSButton("CARDASSIAN", "#FFAA00", shape="rectangle")
        self.cardassian_btn.setMinimumSize(180, 45)
        self.cardassian_btn.clicked.connect(lambda: self.select_faction("CARDASSIAN"))
        faction_layout.addWidget(self.cardassian_btn)
        
        faction_layout.addStretch()
        self.main_layout.addLayout(faction_layout)

        # --- ERA SELECTION ---
        era_label = QLabel("◤ TIME PERIOD")
        era_label.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(20, 'bold')}; margin-bottom: 15px;")
        self.main_layout.addWidget(era_label)
        
        era_layout = QHBoxLayout()
        era_layout.setSpacing(20)
        
        self.nx01_btn = LCARSButton("22nd", "#FFAA00", shape="rectangle")
        self.nx01_btn.setMinimumSize(140, 45)
        self.nx01_btn.clicked.connect(lambda: self.select_era("22nd"))
        era_layout.addWidget(self.nx01_btn)
        
        self.tng_btn = LCARSButton("23rd", "#FF9900", shape="rectangle")
        self.tng_btn.setMinimumSize(140, 45)
        self.tng_btn.clicked.connect(lambda: self.select_era("23rd"))
        era_layout.addWidget(self.tng_btn)
        
        self.voyager_btn = LCARSButton("24th", "#FF6600", shape="rectangle")
        self.voyager_btn.setMinimumSize(140, 45)
        self.voyager_btn.clicked.connect(lambda: self.select_era("24th"))
        era_layout.addWidget(self.voyager_btn)
        
        self.titan_btn = LCARSButton("25th", "#FF9900", shape="rectangle")
        self.titan_btn.setMinimumSize(140, 45)
        self.titan_btn.clicked.connect(lambda: self.select_era("25th"))
        era_layout.addWidget(self.titan_btn)
        
        self.tcars_btn = LCARSButton("29th", "#31C9F4", shape="rectangle")
        self.tcars_btn.setMinimumSize(140, 45)
        self.tcars_btn.clicked.connect(lambda: self.select_era("29th"))
        era_layout.addWidget(self.tcars_btn)
        
        era_layout.addStretch()
        self.main_layout.addLayout(era_layout)

        # --- CURRENT SELECTION DISPLAY ---
        self.selection_label = QLabel("CURRENT: FEDERATION // 25th CENTURY")
        self.selection_label.setStyleSheet(f"color: #FFAA00; {get_lcars_font_style(18, 'bold')}; margin: 20px 0;")
        self.selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.selection_label)

        # --- LAUNCH BUTTON ---
        launch_layout = QHBoxLayout()
        launch_layout.addStretch()
        
        self.launch_btn = LCARSButton("LAUNCH SYSTEM", "#00FF00", shape="pill")
        self.launch_btn.setMinimumSize(250, 60)
        self.launch_btn.clicked.connect(self.launch_system)
        launch_layout.addWidget(self.launch_btn)
        
        launch_layout.addStretch()
        self.main_layout.addLayout(launch_layout)
        
        self.main_layout.addStretch()
        
        # Set initial selection
        self.update_selection_display()
    
    def select_faction(self, faction):
        """Вибір фракції"""
        self.selected_faction = faction
        self.update_selection_display()
        get_sound_manager().play("click")
        
        # Оновлення вигляду кнопок
        self.update_button_styles()
    
    def select_era(self, era):
        """Вибір епохи"""
        self.selected_era = era
        self.update_selection_display()
        get_sound_manager().play("click")
        
        # Оновлення вигляду кнопок
        self.update_button_styles()
    
    def update_selection_display(self):
        """Оновлення відображення поточного вибору"""
        self.selection_label.setText(f"CURRENT: {self.selected_faction} // {self.selected_era} CENTURY")
    
    def update_button_styles(self):
        """Оновлення стилів кнопок відповідно до вибору"""
        # Оновлення кнопок фракцій
        for btn in [self.federation_btn, self.klingon_btn, self.romulan_btn, self.cardassian_btn]:
            if hasattr(btn, 'text'):
                if btn.text().upper() == self.selected_faction:
                    btn.setStyleSheet("background-color: #00FF00; color: black; font-weight: bold;")
                else:
                    # Відновлення оригінальних кольорів
                    original_colors = {
                        "FEDERATION": "#FF9900",
                        "KLINGON": "#FF3333", 
                        "ROMULAN": "#33FF33",
                        "CARDASSIAN": "#FFAA00"
                    }
                    color = original_colors.get(btn.text().upper(), "#FF9900")
                    btn.setStyleSheet(f"background-color: {color}; color: white;")
        
        # Оновлення кнопок епох
        era_buttons = [self.nx01_btn, self.tng_btn, self.voyager_btn, self.titan_btn, self.tcars_btn]
        for btn in era_buttons:
            if hasattr(btn, 'text'):
                btn_text = btn.text()
                if btn_text == self.selected_era:
                    btn.setStyleSheet("background-color: #00FF00; color: black; font-weight: bold;")
                else:
                    # Відновлення оригінальних кольорів
                    original_colors = {
                        "22nd": "#FFAA00",
                        "23rd": "#FF9900",
                        "24th": "#FF6600", 
                        "25th": "#FF9900",
                        "29th": "#31C9F4"
                    }
                    color = original_colors.get(btn_text, "#FF9900")
                    btn.setStyleSheet(f"background-color: {color}; color: white;")
    
    def launch_system(self):
        """Запуск системи з обраними параметрами"""
        print(f"[SELECTOR] Launching {self.selected_faction} ({self.selected_era}) system...")
        get_sound_manager().play("ready")
        self.selected.emit(self.selected_faction, self.selected_era)

    def _refresh_interface(self):
        """Повне оновлення інтерфейсу згідно з обраною палітрою (Living UI)."""
        target_era, target_faction = self._get_current_enums()
        
        from lcars.themes.palette import get_theme
        theme = get_theme(target_era, target_faction)
        primary = theme.get('primary', '#4BBEBF')
        secondary = theme.get('secondary', '#3366CC')
        
        self.selection_label.setText(f"CONFIG: {self.selected_faction} // {self.selected_era}")
        self.selection_label.setStyleSheet(f"color: {primary}; {get_lcars_font_style(20, 'normal')}")
        
        # Generator for structured randomization (Clean style - no architectural updates)
        gen = LCARSColorGenerator(target_era, target_faction)
        
        if hasattr(self, 'title_lbl'):
            self.title_lbl.setStyleSheet(f"color: {primary}; {get_lcars_font_style(24, 'normal')};")
            
        # 2. Update ALL buttons within view
        for btn in self.findChildren(LCARSButton):
            btn.era = target_era
            btn.faction = target_faction
            
            # Use generator to pick colors from NEW palette
            btn.current_color = gen.get_next_color()
            btn.apply_style()
            
        # 3. Special case for launch button
        self.launch_btn.update_color(primary)
        
        # Notify launcher
        self.preview_changed.emit(self.selected_faction, self.selected_era)

    def _get_current_enums(self):
        """Helper to resolve current era and faction enums."""
        from lcars.themes.palette import LCARSEra, FactionEra
        
        era_map = {
            "22nd": LCARSEra.COMS_22ND, "23rd": LCARSEra.PCARS_23RD,
            "23st": LCARSEra.PCARS_23ST, "24th": LCARSEra.LCARS_24TH,
            "24st": LCARSEra.LCARS_24ST, "25th": LCARSEra.LCARS_25TH,
            "29th": LCARSEra.TCARS_29TH
        }
        f_map = {
            "FEDERATION": None,
            "KLINGON": FactionEra.KLINGON,
            "ROMULAN": FactionEra.ROMULAN,
            "CARDASSIAN": FactionEra.CARDASSIAN
        }
        
        target_era = era_map.get(self.selected_era, LCARSEra.LCARS_25TH)
        target_faction = f_map.get(self.selected_faction.upper())
        return target_era, target_faction

# Автоматичний запуск при прямому виконанні файлу
if __name__ == "__main__":
    # Titanium Bridge Migration: import sys
    # Titanium Bridge Migration: from pathlib import Path
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    # Додаємо корінь проекту
    project_root = Path(__file__).parent.parent.parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("LCARS Selector Test")
    window.setGeometry(100, 100, 1000, 700)
    
    selector = SelectorView()
    window.setCentralWidget(selector)
    window.show()
    
    # Логування запуску
    log_to_database("SelectorView", "LAUNCH")
    
    print("LCARS Selector запущено - закрийте вікно для завершення")
    app.exec()
