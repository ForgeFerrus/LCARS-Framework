"""
LCARS Klingon Selector - Клінгонський екран вибору конфігурації.
Adapted from the Romulan selector for Klingon visuals.
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os

# Ensure project root is on sys.path so `import lcars...` works when running this
# view as a standalone script.
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
if root not in sys.path:
    sys.path.insert(0, root)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont, QLinearGradient

from lcars.themes.palette import FactionEra, get_faction_palette, LCARSEra, LCARSColorGenerator
from lcars.themes.theme import get_font_style, get_theme, setup_lcars_font
from lcars.ui.base.widgets import LCARSButton, ScanningBar
from lcars.modules.sound_manager import get_sound_manager


class KlingonSelectorView(QWidget):
    """Клінгонський селектор конфігурації."""
    selected = pyqtSignal(str, str)
    preview_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_faction = "KLINGON"
        self.selected_era = "24th"
        self._theme = None
        self.setup_ui()
        self._refresh_interface()
        self.apply_theme(self.selected_faction, self.selected_era)

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(10)

        header_lay = QHBoxLayout()
        self.title_lbl = QLabel("◢ KLINGON EMPIRE // WAR READY")
        self.title_lbl.setStyleSheet(f"color: #FFAA00; {get_font_style(24, 'normal')};")
        header_lay.addWidget(self.title_lbl)
        header_lay.addStretch()

        self.st_lbl = QLabel("HONOR: BLOOD")
        self.st_lbl.setStyleSheet(f"color: #FFCC66; {get_font_style(16, 'normal')};")
        header_lay.addWidget(self.st_lbl)
        self.main_layout.addLayout(header_lay)

        config_grid = QGridLayout()
        config_grid.setSpacing(12)

        era_frame = QFrame()
        era_frame.setStyleSheet("background-color: rgba(51, 10, 0, 200); border-radius: 8px;")
        era_layout = QVBoxLayout(era_frame)
        era_layout.setContentsMargins(12, 12, 12, 12)

        era_title = QLabel("◢ CHOOSE BATTLE ERA")
        era_title.setStyleSheet(f"color: #FFAA00; {get_font_style(18, 'bold')};")
        era_layout.addWidget(era_title)

        self.era_btn_group = []
        eras = [
            ("22nd", "EARLY CLANS", "#FF8800"),
            ("23rd", "CLASSIC HONOR", "#FF9900"),
            ("24th", "WARBLADE AGE", "#FFAA00"),
            ("25th", "MODERN EMPIRE", "#FFCC66"),
        ]
        for era_code, era_name, color in eras:
            btn = LCARSButton(era_name, color, shape="pill", auto_cycle=True)
            btn.setMinimumSize(200, 36)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            if era_code == "24th":
                btn.setChecked(True)
            btn.clicked.connect(lambda ch, e=era_code: self._set_era(e))
            era_layout.addWidget(btn)
            self.era_btn_group.append(btn)

        config_grid.addWidget(era_frame, 0, 0)

        systems_frame = QFrame()
        systems_frame.setStyleSheet("background-color: rgba(51, 10, 0, 200); border-radius: 8px;")
        systems_layout = QVBoxLayout(systems_frame)
        systems_layout.setContentsMargins(12, 12, 12, 12)

        systems_title = QLabel("◢ BATTLE SYSTEMS")
        systems_title.setStyleSheet(f"color: #FFAA00; {get_font_style(18, 'bold')};")
        systems_layout.addWidget(systems_title)

        systems = ["DISRUPTOR ARRAYS", "BATTLE RITUALS", "BOARDING TEAMS", "HONOR PROTOCOLS"]
        for s in systems:
            lbl = QLabel(f"• {s}")
            lbl.setStyleSheet(f"color: #FFCC66; {get_font_style(14, 'normal')};")
            systems_layout.addWidget(lbl)

        config_grid.addWidget(systems_frame, 0, 1)

        stealth_frame = QFrame()
        stealth_frame.setStyleSheet("background-color: rgba(51, 10, 0, 200); border-radius: 8px;")
        stealth_layout = QVBoxLayout(stealth_frame)
        stealth_layout.setContentsMargins(12, 12, 12, 12)

        stealth_title = QLabel("◢ BATTLE READINESS")
        stealth_title.setStyleSheet(f"color: #FFAA00; {get_font_style(18, 'bold')};")
        stealth_layout.addWidget(stealth_title)

        self.stealth_bar = ScanningBar("#FFAA00")
        stealth_layout.addWidget(self.stealth_bar)

        stealth_label = QLabel("READINESS: 92%")
        stealth_label.setStyleSheet(f"color: #FFCC66; {get_font_style(14, 'normal')};")
        stealth_layout.addWidget(stealth_label)

        config_grid.addWidget(stealth_frame, 1, 0, 1, 2)

        self.main_layout.addLayout(config_grid)

        launch_hbox = QHBoxLayout()
        self.launch_btn = LCARSButton("LAUNCH WARBAND", "#FFAA00", shape="pill")
        self.launch_btn.setMinimumSize(250, 46)
        self.launch_btn.clicked.connect(self.launch_system)
        launch_hbox.addWidget(self.launch_btn)
        launch_hbox.addStretch()

        v_confirm = QVBoxLayout()
        self.preview_lbl = QLabel("CONFIG: KLINGON // 24th")
        self.preview_lbl.setStyleSheet(f"color: white; {get_font_style(20, 'normal')}")
        v_confirm.addWidget(self.preview_lbl, alignment=Qt.AlignmentFlag.AlignRight)

        self.status_lbl = QLabel("FORGED IN HONOR")
        self.status_lbl.setStyleSheet(f"color: #FFAA00; {get_font_style(16, 'bold')}")
        v_confirm.addWidget(self.status_lbl, alignment=Qt.AlignmentFlag.AlignRight)

        launch_hbox.addLayout(v_confirm)
        self.main_layout.addLayout(launch_hbox)

    def _set_era(self, era):
        self.selected_era = era
        self._refresh_interface()
        get_sound_manager().play("click")
        if True:
            self.apply_theme(self.selected_faction, self.selected_era)
        if False: # Removed except block
            pass

    def _refresh_interface(self):
        self.preview_lbl.setText(f"CONFIG: {self.selected_faction} // {self.selected_era}")
        for btn in self.era_btn_group:
            if btn.isChecked():
                btn.setStyleSheet(btn.styleSheet().replace("background-color:", "background-color: #FFAA00;"))
            else:
                btn.setStyleSheet(btn.styleSheet().replace("#FFAA00", "#FF8800"))
        self.preview_changed.emit(self.selected_faction, self.selected_era)

    def apply_theme(self, faction: str, era: str):
        era_map = {"22nd": "22ND", "23rd": "23RD", "23st": "23ST", "24th": "24TH", "25th": "25TH", "29th": "29TH"}
        era_suffix = era_map.get(era, "24TH")
        enum_name = f"KLINGON_{era_suffix}"
        if True:
            faction_enum = getattr(FactionEra, enum_name)
        if False: # Removed except block
            faction_enum = FactionEra.KLINGON_24TH
        # start from faction palette
        palette = get_faction_palette(faction_enum)

        # map era string to LCARSEra
        era_map2 = {
            "22nd": LCARSEra.COMS_22ND,
            "23rd": LCARSEra.PCARS_23RD,
            "23st": LCARSEra.PCARS_23ST,
            "24th": LCARSEra.LCARS_24TH,
            "25th": LCARSEra.LCARS_25TH,
            "29th": LCARSEra.TCARS_29TH,
        }
        target_era = era_map2.get(era, LCARSEra.LCARS_24TH)

        gen = LCARSColorGenerator(target_era, faction_enum)
        gen.reset()

        theme = {
            "bg": palette.get("background", "#100400"),
            "panel": gen.get_next_color() or palette.get("panel_color", palette.get("panel_border", "#330000")),
            "accent": gen.get_next_color() or (palette.get("button_colors", ["#FFAA00"])[0]),
            "accent_bright": gen.get_next_color() or (palette.get("button_colors", ["#FFAA00"])[1] if len(palette.get("button_colors", []))>1 else palette.get("button_colors", ["#FFAA00"])[0]),
            "text": palette.get("panel_color", "#FFCC66")
        }

        self._theme = theme
        self.setStyleSheet(f"background-color: {theme['bg']};")
        self.title_lbl.setStyleSheet(f"color: {theme['accent_bright']}; {get_font_style(24, 'normal')};")
        self.st_lbl.setStyleSheet(f"color: {theme['text']}; {get_font_style(16, 'normal')};")
        self.preview_lbl.setStyleSheet(f"color: {theme['text']}; {get_font_style(20, 'normal')}")
        self.status_lbl.setStyleSheet(f"color: {theme['accent']}; {get_font_style(16, 'bold')}")

        panel_css = f"background-color: {theme['panel']}; border-radius:8px;"
        for frame in self.findChildren(QFrame):
            frame.setStyleSheet(panel_css)

        # Apply generator colors to era buttons
        for btn in self.era_btn_group:
            if True:
                btn.current_color = gen.get_next_color()
                btn.apply_style()
            if False: # Removed except block
                pass

        # launch button
        if True:
            if hasattr(self.launch_btn, 'update_color'):
                self.launch_btn.update_color(gen.get_next_color())
            else:
                self.launch_btn.setStyleSheet(f"background-color: {gen.get_next_color()};")
        if False: # Removed except block
            pass

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        w = self.width()
        h = self.height()
        if not self._theme:
            return
        accent = QColor(self._theme['accent'])
        pen = QPen(accent, 20)
        painter.setPen(pen)
        # aggressive diagonal slashes for Klingon aesthetic
        painter.drawLine(int(0.05*w), int(0.05*h), int(0.45*w), int(0.95*h))
        painter.drawLine(int(0.55*w), int(0.05*h), int(0.95*w), int(0.95*h))
        painter.end()

    def launch_system(self):
        get_sound_manager().play("ready")
        self.selected.emit(self.selected_faction, self.selected_era)


def main():
    app = QApplication(sys.argv)
    setup_lcars_font()
    window = KlingonSelectorView()
    window.setFixedSize(1365, 768)
    window.show()

    def _save_and_exit():
        path = "artifacts/klingon_preview.png"
        pix = window.grab()
        pix.save(path)
        print(f"Saved preview to {path}")
        app.quit()

    QTimer.singleShot(700, _save_and_exit)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
"""
LCARS Klingon Selector - Екран вибору конфігурації Клінгонської імперії.
Воїнський дизайн з акцентом на бойові системи.
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

class KlingonSelectorView(QWidget):
    """Клінгонський селектор конфігурації з воїнською естетикою."""
    selected = pyqtSignal(str, str)  # faction, era
    preview_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_faction = "KLINGON"
        self.selected_era = "23rd"
        self.setup_ui()
        self._refresh_interface()

    def setup_ui(self):
        """Створення інтерфейсу в клінгонському стилі."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)

        # --- KLINGON HEADER ---
        header_lay = QHBoxLayout()
        header_lay.setContentsMargins(0, 0, 0, 10)
        
        self.title_lbl = QLabel("◤ KLINGON EMPIRE // BATTLE CONFIGURATION")
        self.title_lbl.setStyleSheet(f"color: #FF3333; {get_lcars_font_style(24, 'normal')};")
        header_lay.addWidget(self.title_lbl)
        header_lay.addStretch()
        
        # Статус імперії
        self.st_lbl = QLabel("EMPIRE STATUS: STRONG")
        self.st_lbl.setStyleSheet(f"color: #CC6666; {get_lcars_font_style(16, 'normal')};")
        header_lay.addWidget(self.st_lbl)
        
        self.main_layout.addLayout(header_lay)
        
        # --- CONFIGURATION GRID ---
        config_grid = QGridLayout()
        config_grid.setSpacing(15)
        
        # --- ERA SELECTION ---
        era_frame = QFrame()
        era_frame.setStyleSheet("background-color: rgba(51, 0, 0, 180); border-radius: 8px;")
        era_layout = QVBoxLayout(era_frame)
        era_layout.setContentsMargins(15, 15, 15, 15)
        
        era_title = QLabel("◤ CHOOSE BATTLE ERA")
        era_title.setStyleSheet(f"color: #FF3333; {get_lcars_font_style(18, 'bold')};")
        era_layout.addWidget(era_title)
        
        self.era_btn_group = []
        eras = [
            ("22nd", "EARLY EMPIRE", "#CC3333"),
            ("23rd", "CLASSIC EMPIRE", "#FF3333"),
            ("24th", "DOMINION WAR", "#FF6666"),
            ("25th", "REBORN EMPIRE", "#FF9999")
        ]
        
        for era_code, era_name, color in eras:
            btn = LCARSButton(era_name, color, shape="pill", auto_cycle=True)
            btn.setMinimumSize(200, 35)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            if era_code == "23rd":
                btn.setChecked(True)
            btn.clicked.connect(lambda ch, e=era_code: self._set_era(e))
            era_layout.addWidget(btn)
            self.era_btn_group.append(btn)
        
        config_grid.addWidget(era_frame, 0, 0)
        
        # --- BATTLE SYSTEMS ---
        systems_frame = QFrame()
        systems_frame.setStyleSheet("background-color: rgba(51, 0, 0, 180); border-radius: 8px;")
        systems_layout = QVBoxLayout(systems_frame)
        systems_layout.setContentsMargins(15, 15, 15, 15)
        
        systems_title = QLabel("◤ BATTLE SYSTEMS")
        systems_title.setStyleSheet(f"color: #FF3333; {get_lcars_font_style(18, 'bold')};")
        systems_layout.addWidget(systems_title)
        
        # Системи зброї
        weapons = ["DISRUPTORS", "PHOTON TORPEDOES", "BAT'LETH TRAINING", "HONOR SENSORS"]
        for weapon in weapons:
            weapon_label = QLabel(f"• {weapon}")
            weapon_label.setStyleSheet(f"color: #CC6666; {get_lcars_font_style(14, 'normal')};")
            systems_layout.addWidget(weapon_label)
        
        config_grid.addWidget(systems_frame, 0, 1)
        
        # --- HONOR STATUS ---
        honor_frame = QFrame()
        honor_frame.setStyleSheet("background-color: rgba(51, 0, 0, 180); border-radius: 8px;")
        honor_layout = QVBoxLayout(honor_frame)
        honor_layout.setContentsMargins(15, 15, 15, 15)
        
        honor_title = QLabel("◤ WARRIOR STATUS")
        honor_title.setStyleSheet(f"color: #FF3333; {get_lcars_font_style(18, 'bold')};")
        honor_layout.addWidget(honor_title)
        
        # Рівень честі
        self.honor_bar = ScanningBar("#FF3333")
        # ScanningBar - декоративний елемент, не має setRange
        honor_layout.addWidget(self.honor_bar)
        
        honor_label = QLabel("HONOR LEVEL: 85%")
        honor_label.setStyleSheet(f"color: #CC6666; {get_lcars_font_style(14, 'normal')};")
        honor_layout.addWidget(honor_label)
        
        config_grid.addWidget(honor_frame, 1, 0, 1, 2)
        
        self.main_layout.addLayout(config_grid)
        
        # --- LAUNCH CONTROLS ---
        launch_hbox = QHBoxLayout()
        launch_hbox.setSpacing(10)
        
        # Кнопка запуску
        self.launch_btn = LCARSButton("ENGAGE BATTLE SYSTEMS", "#FF3333", shape="pill")
        self.launch_btn.setMinimumSize(250, 45)
        self.launch_btn.clicked.connect(self.launch_system)
        launch_hbox.addWidget(self.launch_btn)
        
        launch_hbox.addStretch()
        
        # Попередній перегляд
        v_confirm = QVBoxLayout()
        self.preview_lbl = QLabel("CONFIG: KLINGON // 23rd")
        self.preview_lbl.setStyleSheet(f"color: white; {get_lcars_font_style(20, 'normal')}")
        v_confirm.addWidget(self.preview_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.status_lbl = QLabel("READY FOR HONOR")
        self.status_lbl.setStyleSheet(f"color: #FF3333; {get_lcars_font_style(16, 'bold')}")
        v_confirm.addWidget(self.status_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        
        launch_hbox.addLayout(v_confirm)
        
        self.main_layout.addLayout(launch_hbox)

    def _set_era(self, era):
        """Встановлення ери."""
        self.selected_era = era
        self._refresh_interface()
        get_sound_manager().play("click")

    def _refresh_interface(self):
        """Оновлення інтерфейсу."""
        self.preview_lbl.setText(f"CONFIG: {self.selected_faction} // {self.selected_era}")
        
        # Оновлення кольорів кнопок
        for btn in self.era_btn_group:
            if btn.isChecked():
                btn.setStyleSheet(btn.styleSheet().replace("background-color:", "background-color: #FF3333;"))
            else:
                btn.setStyleSheet(btn.styleSheet().replace("#FF3333", "#CC3333"))
        
        self.preview_changed.emit(self.selected_faction, self.selected_era)

    def launch_system(self):
        """Запуск системи."""
        get_sound_manager().play("ready")
        self.selected.emit(self.selected_faction, self.selected_era)

    def closeEvent(self, event):
        """Очищення при закритті."""
        # ScanningBar зупиняється автоматично
        event.accept()
