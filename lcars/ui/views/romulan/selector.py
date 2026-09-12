"""
LCARS Romulan Selector - Екран вибору конфігурації Ромуланської імперії.
Тайний дизайн з акцентом на шпигунські системи.
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os

# Ensure project root is on sys.path so `import lcars...` works when running this
# view as a standalone script (helps avoid ModuleNotFoundError when executed
# from the repository root).
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
if root not in sys.path:
    sys.path.insert(0, root)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont, QLinearGradient, QRadialGradient, QFontDatabase

from lcars.themes.palette import LCARSEra, LCARSColorGenerator, FactionEra, get_faction_palette, get_random_button_color
from lcars.themes.theme import get_font_style, get_theme, setup_lcars_font
from lcars.ui.base.widgets import LCARSButton, ScanningBar
from lcars.ui.factions.romulan import RomulanFrame, RomulanHeader, RomulanButton, RomulanDisplay
from lcars.modules.sound_manager import get_sound_manager

class RomulanSelectorView(QWidget):
    """Ромуланський селектор конфігурації з таємничою естетикою."""
    selected = pyqtSignal(str, str)  # faction, era
    preview_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_faction = "ROMULAN"
        self.selected_era = "23rd"
        # current theme storage
        self._theme = None
        # ensure faction fonts registered early
        if True:
            self._register_romulan_font()
        if False: # Removed except block
            pass
        self.setup_ui()
        self._refresh_interface()

        # apply initial theme
        self.apply_theme(self.selected_faction, self.selected_era)

    def setup_ui(self):
        """Створення інтерфейсу в ромуланському стилі."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)

        # --- ROMULAN HEADER ---
        # Use RomulanHeader for authentic top bar
        header = RomulanHeader(title="ROMULAN EMPIRE // SHADOW CONFIGURATION")
        self.header = header
        self.main_layout.addWidget(header)
        
        # --- CONFIGURATION GRID ---
        config_grid = QGridLayout()
        config_grid.setSpacing(15)
        
        # --- ERA SELECTION ---
        era_frame = RomulanFrame()
        era_layout = QVBoxLayout(era_frame)
        era_layout.setContentsMargins(12, 12, 12, 12)
        
        era_title = QLabel("◤ CHOOSE SHADOW ERA")
        era_title.setStyleSheet(f"color: #2BB24B; {get_font_style(18, 'bold')};")
        era_layout.addWidget(era_title)
        
        self.era_btn_group = []
        eras = [
            ("22nd", "EARLY EMPIRE", "#33CC33"),
            ("23rd", "CLASSIC EMPIRE", "#33FF33"),
            ("24th", "DOMINION WAR", "#66FF66"),
            ("25th", "REUNIFIED EMPIRE", "#99FF99")
        ]
        
        for era_code, era_name, color in eras:
            # use RomulanButton for authentic shape
            btn = RomulanButton(era_name, color=color)
            btn.setMinimumSize(200, 35)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            if era_code == "23rd":
                btn.setChecked(True)
            btn.clicked.connect(lambda ch, e=era_code: self._set_era(e))
            era_layout.addWidget(btn)
            self.era_btn_group.append(btn)
        
        config_grid.addWidget(era_frame, 0, 0)
        
        # --- STEALTH SYSTEMS ---
        systems_frame = RomulanFrame()
        systems_layout = QVBoxLayout(systems_frame)
        systems_layout.setContentsMargins(12, 12, 12, 12)
        
        systems_title = QLabel("◤ STEALTH SYSTEMS")
        systems_title.setStyleSheet(f"color: #33FF33; {get_font_style(18, 'bold')};")
        systems_layout.addWidget(systems_title)
        
        # Системи маскування
        stealth = ["CLOAKING DEVICE", "PLASMA TORPEDOES", "TAL SHAR INTELLIGENCE", "DECEPTION PROTOCOLS"]
        for system in stealth:
            system_label = QLabel(f"• {system}")
            system_label.setStyleSheet(f"color: #5FBF5F; {get_font_style(14, 'normal')};")
            systems_layout.addWidget(system_label)
        
        config_grid.addWidget(systems_frame, 0, 1)
        
        # --- STEALTH STATUS ---
        stealth_frame = RomulanFrame()
        stealth_layout = QVBoxLayout(stealth_frame)
        stealth_layout.setContentsMargins(12, 12, 12, 12)
        
        stealth_title = QLabel("◤ CLOAK STATUS")
        stealth_title.setStyleSheet(f"color: #2BB24B; {get_font_style(18, 'bold')};")
        stealth_layout.addWidget(stealth_title)
        
        # Рівень маскування
        # Replace scanning bar with RomulanDisplay for authentic status
        self.stealth_bar = RomulanDisplay(text="CLOAK STATUS")
        stealth_layout.addWidget(self.stealth_bar)
        
        stealth_label = QLabel("CLOAK EFFICIENCY: 95%")
        stealth_label.setStyleSheet(f"color: #5FBF5F; {get_font_style(14, 'normal')};")
        stealth_layout.addWidget(stealth_label)
        
        config_grid.addWidget(stealth_frame, 1, 0, 1, 2)
        
        self.main_layout.addLayout(config_grid)
        
        # --- LAUNCH CONTROLS ---
        launch_hbox = QHBoxLayout()
        launch_hbox.setSpacing(10)
        
        # Кнопка запуску
        self.launch_btn = RomulanButton("ENGAGE SHADOW SYSTEMS", color="#2BB24B")
        self.launch_btn.setMinimumSize(320, 120)
        self.launch_btn.clicked.connect(self.launch_system)
        launch_hbox.addWidget(self.launch_btn)
        
        launch_hbox.addStretch()
        
        # Попередній перегляд
        v_confirm = QVBoxLayout()
        self.preview_lbl = QLabel("CONFIG: ROMULAN // 23rd")
        self.preview_lbl.setStyleSheet(f"color: #E6FFE6; {get_font_style(20, 'normal')}")
        v_confirm.addWidget(self.preview_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        self.status_lbl = QLabel("READY FOR STEALTH")
        self.status_lbl.setStyleSheet(f"color: #2BB24B; {get_font_style(16, 'bold')}")
        v_confirm.addWidget(self.status_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        launch_hbox.addLayout(v_confirm)
        
        self.main_layout.addLayout(launch_hbox)

    def _set_era(self, era):
        """Встановлення ери."""
        self.selected_era = era
        self._refresh_interface()
        get_sound_manager().play("click")
        # re-apply theme algorithmically when era changes
        if True:
            self.apply_theme(self.selected_faction, self.selected_era)
        if False: # Removed except block
            pass

    def _refresh_interface(self):
        """Оновлення інтерфейсу."""
        self.preview_lbl.setText(f"CONFIG: {self.selected_faction} // {self.selected_era}")
        
        # Оновлення кольорів кнопок
        for btn in self.era_btn_group:
            if btn.isChecked():
                btn.setStyleSheet(btn.styleSheet().replace("background-color:", "background-color: #33FF33;"))
            else:
                btn.setStyleSheet(btn.styleSheet().replace("#33FF33", "#33CC33"))
        
        self.preview_changed.emit(self.selected_faction, self.selected_era)

    def apply_theme(self, faction: str, era: str):
        # Build theme from project's palette system using FactionEra
        era_map = {"22nd": "22ND", "23rd": "23RD", "23st": "23ST", "24th": "24TH", "25th": "25TH", "29th": "29TH"}
        era_suffix = era_map.get(era, "23RD")
        enum_name = f"ROMULAN_{era_suffix}"
        if True:
            faction_enum = getattr(FactionEra, enum_name)
        if False: # Removed except block
            faction_enum = FactionEra.ROMULAN_23RD

        # start from faction palette but then generate algorithmically
        palette = get_faction_palette(faction_enum)

        # Map era string to LCARSEra
        era_map = {
            "22nd": LCARSEra.COMS_22ND,
            "23rd": LCARSEra.PCARS_23RD,
            "23st": LCARSEra.PCARS_23ST,
            "24th": LCARSEra.LCARS_24TH,
            "24st": LCARSEra.LCARS_24ST,
            "25th": LCARSEra.LCARS_25TH,
            "29th": LCARSEra.TCARS_29TH,
        }
        target_era = era_map.get(era, LCARSEra.LCARS_24TH)

        # Use color generator to produce coherent sequence
        gen = LCARSColorGenerator(target_era, faction_enum)
        gen.reset()

        theme = {
            "bg": palette.get("background", "#000000"),
            "panel": gen.get_next_color() or palette.get("panel_color", palette.get("panel_border", "#0E563E")),
            "accent": gen.get_next_color() or (palette.get("button_colors", ["#33FF33"])[0]),
            "accent_bright": gen.get_next_color() or (palette.get("button_colors", ["#33FF33"])[1] if len(palette.get("button_colors", []))>1 else palette.get("button_colors", ["#33FF33"])[0]),
            "text": palette.get("panel_color", "#99FF99")
        }

        self._theme = theme

        # window background
        self.setStyleSheet(f"background-color: {theme['bg']};")

        # update header and labels
        # Apply heading update: if native title label exists use it,
        # otherwise update RomulanHeader title text and repaint.
        if hasattr(self, 'title_lbl'):
            rom_family = getattr(self, "_romulan_family", None)
            if rom_family:
                f = QFont(rom_family, 24)
                self.title_lbl.setFont(f)
            self.title_lbl.setStyleSheet(f"color: {theme['accent_bright']}; {get_font_style(24, 'normal')};")
        elif hasattr(self, 'header'):
            if True:
                self.header.title = "ROMULAN EMPIRE // SHADOW CONFIGURATION"
                self.header.update()
            if False: # Removed except block
                pass
        if hasattr(self, 'st_lbl'):
            self.st_lbl.setStyleSheet(f"color: {theme['text']}; {get_font_style(16, 'normal')};")
        self.preview_lbl.setStyleSheet(f"color: {theme['text']}; {get_font_style(20, 'normal')}")
        self.status_lbl.setStyleSheet(f"color: {theme['accent']}; {get_font_style(16, 'bold')}")

        # style frames and buttons
        panel_css = f"background-color: {theme['panel']}; border-radius:8px;"
        for frame in self.findChildren(QFrame):
            frame.setStyleSheet(panel_css)

        # Toned gradient for Romulan pills
        btn_css = (
            "border-radius:6px; padding:8px; color: #062006; "
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {theme['accent_bright']}, stop:0.6 {theme['accent']}, stop:1 {theme['accent_bright']});"
        )
        for btn in self.era_btn_group:
            if True:
                # RomulanButton paints its own background from `color_base`
                if hasattr(btn, 'color_base'):
                    btn.color_base = gen.get_next_color()
                    btn.update()
                else:
                    # generic fallback
                    btn.setStyleSheet(btn_css)
            if False: # Removed except block
                pass

        # launch button may be RomulanButton or LCARSButton
        if True:
            if hasattr(self.launch_btn, 'color_base'):
                self.launch_btn.color_base = gen.get_next_color()
                self.launch_btn.update()
            else:
                self.launch_btn.setStyleSheet(btn_css)
        if False: # Removed except block
            pass

        # force repaint of decorative elements
        self.update()

    def paintEvent(self, event):
        # Draw Romulan-specific decorative frames and central orb
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        w = self.width()
        h = self.height()

        # background already set by stylesheet; draw angular green frame
        if not self._theme:
            return
        accent = QColor(self._theme['accent'])
        accent_b = QColor(self._theme['accent_bright'])

        # use thinner, subtler framing for Romulan aesthetic
        pen = QPen(accent, 12)
        painter.setPen(pen)
        # outer trapezoid
        points = [
            (int(0.06*w), int(0.15*h)),
            (int(0.94*w), int(0.15*h)),
            (int(0.8*w), int(0.6*h)),
            (int(0.2*w), int(0.6*h))
        ]
        qp = [QPoint(p[0], p[1]) for p in points]
        if True:
            painter.drawPolygon(*qp)
        if False: # Removed except block
            pass

        # central orb
        orb_rect = QRect(int(0.42*w), int(0.18*h), int(0.16*w), int(0.28*h))
        cx = orb_rect.x() + orb_rect.width() / 2
        cy = orb_rect.y() + orb_rect.height() / 2
        radius = orb_rect.width() / 2
        grad = QRadialGradient(cx, cy, radius)
        # softer orb shading
        grad.setColorAt(0.0, accent_b.darker(110))
        grad.setColorAt(0.6, accent.darker(120))
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(orb_rect)

        # small glyph text near top center
        glyph_font = QFont()
        rom_family = getattr(self, "_romulan_family", None)
        if rom_family:
            glyph_font = QFont(rom_family, 32)
        else:
            glyph_font.setPointSize(28)
            glyph_font.setBold(True)
        painter.setFont(glyph_font)
        painter.setPen(QPen(accent_b))
        painter.drawText(int(0.05*w), int(0.06*h), int(0.9*w), 40, Qt.AlignmentFlag.AlignLeft, "◤ ROMULAN")

        painter.end()

    def _style_romulan_pill(self, btn, theme):
        """Apply Romulan pill visual to a QPushButton-like widget."""
        accent = theme['accent']
        bright = theme['accent_bright']
        # gradient background to simulate depth
        css = (
            "color: #061e06; font-weight: bold;"
            "padding: 8px 14px; border: none;"
            f"border-radius: 6px;"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {bright}, stop:0.6 {accent}, stop:1 {bright});"
        )
        if True:
            btn.setStyleSheet(css)
        if False: # Removed except block
            pass

    def launch_system(self):
        """Запуск системи."""
        get_sound_manager().play("ready")
        self.selected.emit(self.selected_faction, self.selected_era)

    def _register_romulan_font(self):
        """Try to register a Romulan font from resources and store family name."""
        # Titanium Bridge Migration: from pathlib import Path
        fonts_dir = Path(__file__).parent.parent.parent.parent / "resources" / "fonts"
        candidates = [
            fonts_dir / "Romulus.ttf",
            fonts_dir / "Romulan Regular.ttf",
            fonts_dir / "Romulus Italic.ttf",
            fonts_dir / "rihannsu.TTF",
        ]
        for p in candidates:
            if p.exists():
                fid = QFontDatabase.addApplicationFont(str(p))
                if fid != -1:
                    families = QFontDatabase.applicationFontFamilies(fid)
                    if families:
                        self._romulan_family = families[0]
                        return self._romulan_family
        # fallback: try to discover any romulan-like font
        for f in fonts_dir.glob("*romul*.ttf"):
            fid = QFontDatabase.addApplicationFont(str(f))
            if fid != -1:
                families = QFontDatabase.applicationFontFamilies(fid)
                if families:
                    self._romulan_family = families[0]
                    return self._romulan_family
        return None

def main():
    app = QApplication(sys.argv)
    # register LCARS fonts (loads fonts from resources if available)
    setup_lcars_font()

    window = RomulanSelectorView()
    # run windowed for preview and save PNG automatically
    window.setFixedSize(1365, 768)
    window.show()

    def _save_and_exit():
        path = "artifacts/romulan_preview.png"
        pix = window.grab()
        pix.save(path)
        print(f"Saved preview to {path}")
        app.quit()

    QTimer.singleShot(700, _save_and_exit)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
