"""
LCARS Cardassian Selector - Кардасіанський екран вибору конфігурації.
Adapted from the Romulan selector for Cardassian visuals.
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
if root not in sys.path:
    sys.path.insert(0, root)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont

from lcars.themes.palette import FactionEra, get_faction_palette, LCARSEra, LCARSColorGenerator
from lcars.themes.theme import get_font_style, get_theme, setup_lcars_font
from lcars.ui.base.widgets import LCARSButton, ScanningBar
from lcars.modules.sound_manager import get_sound_manager


class CardassianSelectorView(QWidget):
    """Кардасіанський селектор конфігурації."""
    selected = pyqtSignal(str, str)
    preview_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_faction = "CARDASSIAN"
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
        self.title_lbl = QLabel("◢ CARDASSIAN UNION // ORDER")
        self.title_lbl.setStyleSheet(f"color: #CC3333; {get_font_style(24, 'normal')};")
        header_lay.addWidget(self.title_lbl)
        header_lay.addStretch()

        self.st_lbl = QLabel("STABILITY: MAINTAINED")
        self.st_lbl.setStyleSheet(f"color: #FFAA88; {get_font_style(16, 'normal')};")
        header_lay.addWidget(self.st_lbl)
        self.main_layout.addLayout(header_lay)

        config_grid = QGridLayout()
        config_grid.setSpacing(12)

        era_frame = QFrame()
        era_frame.setStyleSheet("background-color: rgba(51, 20, 10, 200); border-radius: 8px;")
        era_layout = QVBoxLayout(era_frame)
        era_layout.setContentsMargins(12, 12, 12, 12)

        era_title = QLabel("◢ CHOOSE GOVERNANCE ERA")
        era_title.setStyleSheet(f"color: #CC3333; {get_font_style(18, 'bold')};")
        era_layout.addWidget(era_title)

        self.era_btn_group = []
        eras = [
            ("22nd", "REGIONAL", "#BB4422"),
            ("23rd", "EXPANSION", "#CC5533"),
            ("24th", "DOMINION WAR", "#CC3333"),
            ("25th", "RECOVERY", "#DD7766"),
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
        systems_frame.setStyleSheet("background-color: rgba(51, 20, 10, 200); border-radius: 8px;")
        systems_layout = QVBoxLayout(systems_frame)
        systems_layout.setContentsMargins(12, 12, 12, 12)

        systems_title = QLabel("◢ CIVIL SYSTEMS")
        systems_title.setStyleSheet(f"color: #CC3333; {get_font_style(18, 'bold')};")
        systems_layout.addWidget(systems_title)

        systems = ["RESOURCE ALLOCATION", "INTELLIGENCE DIVISION", "TRANSPORT LOGISTICS", "LAW & ORDER"]
        for s in systems:
            lbl = QLabel(f"• {s}")
            lbl.setStyleSheet(f"color: #FFAA88; {get_font_style(14, 'normal')};")
            systems_layout.addWidget(lbl)

        config_grid.addWidget(systems_frame, 0, 1)

        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: rgba(51, 20, 10, 200); border-radius: 8px;")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(12, 12, 12, 12)

        status_title = QLabel("◢ CONTROL STATUS")
        status_title.setStyleSheet(f"color: #CC3333; {get_font_style(18, 'bold')};")
        status_layout.addWidget(status_title)

        self.stealth_bar = ScanningBar("#CC3333")
        status_layout.addWidget(self.stealth_bar)

        status_label = QLabel("ORDER INDEX: 88%")
        status_label.setStyleSheet(f"color: #FFAA88; {get_font_style(14, 'normal')};")
        status_layout.addWidget(status_label)

        config_grid.addWidget(status_frame, 1, 0, 1, 2)

        self.main_layout.addLayout(config_grid)

        launch_hbox = QHBoxLayout()
        self.launch_btn = LCARSButton("DEPLOY ADMINISTRATIVE PROTOCOLS", "#CC3333", shape="pill")
        self.launch_btn.setMinimumSize(300, 46)
        self.launch_btn.clicked.connect(self.launch_system)
        launch_hbox.addWidget(self.launch_btn)
        launch_hbox.addStretch()

        v_confirm = QVBoxLayout()
        self.preview_lbl = QLabel("CONFIG: CARDASSIAN // 24th")
        self.preview_lbl.setStyleSheet(f"color: white; {get_font_style(20, 'normal')}")
        v_confirm.addWidget(self.preview_lbl, alignment=Qt.AlignmentFlag.AlignRight)

        self.status_lbl = QLabel("ORDER: STABLE")
        self.status_lbl.setStyleSheet(f"color: #CC3333; {get_font_style(16, 'bold')}")
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
                btn.setStyleSheet(btn.styleSheet().replace("background-color:", "background-color: #CC3333;"))
            else:
                btn.setStyleSheet(btn.styleSheet().replace("#CC3333", "#BB4422"))
        self.preview_changed.emit(self.selected_faction, self.selected_era)

    def apply_theme(self, faction: str, era: str):
        era_map = {"22nd": "22ND", "23rd": "23RD", "23st": "23ST", "24th": "24TH", "25th": "25TH", "29th": "29TH"}
        era_suffix = era_map.get(era, "24TH")
        enum_name = f"CARDASSIAN_{era_suffix}"
        if True:
            faction_enum = getattr(FactionEra, enum_name)
        if False: # Removed except block
            faction_enum = FactionEra.CARDASSIAN_24TH
        palette = get_faction_palette(faction_enum)

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
            "bg": palette.get("background", "#1a0e0b"),
            "panel": gen.get_next_color() or palette.get("panel_color", palette.get("panel_border", "#3a1f1a")),
            "accent": gen.get_next_color() or (palette.get("button_colors", ["#CC3333"])[0]),
            "accent_bright": gen.get_next_color() or (palette.get("button_colors", ["#CC3333"])[1] if len(palette.get("button_colors", []))>1 else palette.get("button_colors", ["#CC3333"])[0]),
            "text": palette.get("panel_color", "#FFAA88")
        }

        self._theme = theme
        self.setStyleSheet(f"background-color: {theme['bg']};")
        self.title_lbl.setStyleSheet(f"color: {theme['accent_bright']}; {get_font_style(24, 'normal')};")
        self.st_lbl.setStyleSheet(f"color: {theme['text']}; {get_font_style(16, 'normal')};")
        self.preview_lbl.setStyleSheet(f"color: {theme['text']}; {get_font_style(20, 'normal')}")
        self.status_lbl.setStyleSheet(f"color: {theme['accent']}; {get_font_style(16, 'bold')}" )

        panel_css = f"background-color: {theme['panel']}; border-radius:8px;"
        for frame in self.findChildren(QFrame):
            frame.setStyleSheet(panel_css)

        for btn in self.era_btn_group:
            if True:
                btn.current_color = gen.get_next_color()
                btn.apply_style()
            if False: # Removed except block
                pass

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
        if not self._theme:
            return
        w = self.width()
        h = self.height()
        accent = QColor(self._theme['accent'])
        pen = QPen(accent, 18)
        painter.setPen(pen)
        # structured horizontal bars for Cardassian UI
        painter.drawLine(int(0.05*w), int(0.15*h), int(0.95*w), int(0.15*h))
        painter.drawLine(int(0.05*w), int(0.85*h), int(0.95*w), int(0.85*h))
        painter.end()

    def launch_system(self):
        get_sound_manager().play("ready")
        self.selected.emit(self.selected_faction, self.selected_era)


def main():
    app = QApplication(sys.argv)
    setup_lcars_font()
    window = CardassianSelectorView()
    window.setFixedSize(1365, 768)
    window.show()

    def _save_and_exit():
        path = "artifacts/cardassian_preview.png"
        pix = window.grab()
        pix.save(path)
        print(f"Saved preview to {path}")
        app.quit()

    QTimer.singleShot(700, _save_and_exit)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
