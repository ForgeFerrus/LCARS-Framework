"""
NX-01 STYLE LAUNCHER SELECTOR
ARCHITECT: TITAN V5.0
DESCRIPTION: Implementation of the 22nd Century NX-01 Industrial Launcher.
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from functools import partial

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGridLayout, QStackedWidget, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPolygonF

from lcars.themes.lcars_palette import (
    LCARSEra, get_lcars_font_style, FactionEra, get_theme
)
from lcars.ui.base.widgets import LCARSButton

class NX01Frame(QFrame):
    """Deeply industrial metal frame from the 22nd Century (NX-01)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(60, 60, 60, 60)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        frame_color = QColor("#CCCCCC") # Silver/Metal
        border_color = QColor("#444444") # Dark Industrial Border
        
        # 1. Main Background Panel
        p.fillRect(0, 0, w, h, QColor("#111111")) # Dark background inside frame
        
        # 2. Main Frame Structure (Beveled look with lines)
        p.setPen(QPen(border_color, 2))
        p.setBrush(QBrush(frame_color))
        
        # Top Bar
        p.drawRect(20, 20, w-40, 50)
        # Bottom Bar
        p.drawRect(20, h-70, w-40, 50)
        # Left Bar
        p.drawRect(20, 20, 50, h-40)
        # Right Bar
        p.drawRect(w-70, 20, 50, h-40)
        
        # Inner thin decorative lines
        p.setPen(QPen(QColor("#888888"), 1))
        p.drawRect(75, 75, w-150, h-150)

        # 3. Corner Lamps (High Fidelity)
        def draw_lamp(x, y, color):
            p.setBrush(QBrush(QColor(color)))
            p.setPen(QPen(border_color, 3))
            p.drawEllipse(x, y, 60, 60)
            # Gloss highlight
            p.setBrush(QBrush(QColor(255, 255, 255, 60)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(x+10, y+10, 20, 20)

        draw_lamp(15, 15, "#1A4A9B") # Blue Lamp (Top Left)
        draw_lamp(w-75, 15, "#D10000") # Red Lamp (Top Right)
        draw_lamp(15, h-75, "#CE6363") # Red/Orange (Bottom Left)
        draw_lamp(w-75, h-75, "#269EEE") # Light Blue (Bottom Right)

        # 4. Vertical text in UA/EN mix (Industrial)
        p.setPen(QPen(QColor("#111111")))
        font = QFont("Arial", 14)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 6)
        p.setFont(font)
        
        # Left Text: NX-01 ENTERPRISE / ЕНТЕРПРАЙЗ
        p.save()
        p.translate(45, h // 2)
        p.rotate(-90)
        p.drawText(QRect(-300, -15, 600, 30), Qt.AlignmentFlag.AlignCenter, "NX-01 ENTERPRISE :: ЕНТЕРПРАЙЗ")
        p.restore()
        
        # Right Text: INTERFACE COMMAND / КОМАНДУВАННЯ
        p.save()
        p.translate(w-45, h // 2)
        p.rotate(90)
        p.drawText(QRect(-300, -15, 600, 30), Qt.AlignmentFlag.AlignCenter, "INTERFACE COMMAND :: КОМАНДУВАННЯ")
        p.restore()

class NX01Button(LCARSButton):
    """High-fidelity Industrial Split-Button (22nd Century)."""
    def __init__(self, text, code, color, parent=None):
        super().__init__(text, color, era=LCARSEra.COMS_22ND, parent=parent)
        self.code = code
        self._use_coms_paint = True
        self.setFixedSize(240, 65)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        
        # Split: 55% Active Color, 45% Metal base
        top_h = int(rect.height() * 0.55)
        top_rect = rect.adjusted(0, 0, 0, -(rect.height() - top_h))
        bot_rect = rect.adjusted(0, top_h, 0, 0)
        
        # Hover/Press state logic
        c = QColor(self.current_color)
        if self.isDown(): c = c.darker(120)
        elif self.underMouse(): c = c.lighter(110)
        
        p.fillRect(top_rect, c)
        p.fillRect(bot_rect, QColor("#CCCCCC"))
        
        # Outline (Industrial feel)
        p.setPen(QPen(QColor("#444444"), 1))
        p.drawRect(rect.adjusted(0, 0, -1, -1))
        
        # Indicator Square (Top-Right)
        sq_size = 12
        sq_rect = QRect(rect.width() - sq_size - 4, 4, sq_size, sq_size)
        p.fillRect(sq_rect, QColor("#FFFFFF"))
        p.drawRect(sq_rect)
        
        # Inner circle in square (as per COMS_22.py)
        p.setBrush(QBrush(c))
        p.drawEllipse(sq_rect.adjusted(2, 2, -2, -2))

        # Texts
        title_font = QFont("Arial", 11, QFont.Weight.Bold)
        label_font = QFont("Arial", 9)
        
        # Top: Code (e.g. 22-051)
        p.setPen(QColor("black"))
        p.setFont(title_font)
        p.drawText(top_rect.adjusted(10, 0, -20, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.code)
        
        # Bottom: Label (e.g. STARFLEET)
        p.setFont(label_font)
        p.drawText(bot_rect.adjusted(10, 0, -10, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())

class NX01SelectorView(QWidget):
    selected = pyqtSignal(str, str) # faction, era
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_faction = "FEDERATION"
        self.selected_era = "22nd"
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.frame = NX01Frame()
        frame_layout = QHBoxLayout(self.frame)
        frame_layout.setContentsMargins(80, 80, 80, 80)
        
        # --- ЛІВА ПАНЕЛЬ (Фракції) ---
        left_col = QVBoxLayout()
        left_col.setSpacing(12)
        
        lbl_factions = QLabel("ФРАКЦІЇ")
        lbl_factions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_factions.setStyleSheet(f"color: white; {get_lcars_font_style(14, 'normal')}")
        left_col.addWidget(lbl_factions)
        
        factions = [
            ("UFP", "FEDERATION", "ФЕДЕРАЦІЯ", "#269EEE"),
            ("KLN", "KLINGON", "КЛІНГOНИ", "#D10000"),
            ("ROM", "ROMULAN", "РОМУЛАНЦІ", "#669966"),
            ("CAR", "CARDASSIAN", "КАРДАСІЯ", "#CE6363")
        ]
        
        for code, full, ua, col in factions:
            btn = NX01Button(ua, code, col)
            btn.setFixedSize(140, 60)
            btn.clicked.connect(partial(self._set_faction, full))
            left_col.addWidget(btn)
        
        left_col.addStretch()
        frame_layout.addLayout(left_col)
        
        # --- ЦЕНТРАЛЬНА ПАНЕЛЬ (ЕРИ ТА ЛОГО) ---
        center_vbox = QVBoxLayout()
        center_vbox.setSpacing(20)
        
        # Заголовок
        logo_container = QVBoxLayout()
        logo_lbl = QLabel("◢ STARFLEET COMMAND ◣")
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet(f"color: white; {get_lcars_font_style(28, 'normal')}")
        logo_container.addWidget(logo_lbl)
        
        sub_lbl = QLabel("ЦЕНТРАЛЬНИЙ ОБЧИСЛЮВАЛЬНИЙ ВУЗОЛ :: NX-01")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setStyleSheet(f"color: #CCCCCC; {get_lcars_font_style(12, 'normal')}")
        logo_container.addWidget(sub_lbl)
        
        center_vbox.addLayout(logo_container)
        
        # Сітка Ер (Ери тепер теж у промисловому стилі)
        era_grid = QGridLayout()
        era_grid.setSpacing(15)
        eras = [
            ("ЕНТЕРПРАЙЗ NX-01", "22-051", "22nd", "#5C5C5C"),
            ("КОНСТИТУЦІЯ (TOS)", "23-156", "23rd", "#FFE600"),
            ("ЕКСЦЕЛЬСІОР (TMP)", "23-702", "23st", "#2062EE"),
            ("ГАЛАКТИКА (TNG)", "24-540", "24th", "#9EFFB5"),
            ("ТИТАН (V5.0)", "25-100", "25th", "#2A7193"),
            ("ЮНІВЕРС (29ст)", "29-300", "29th", "#00A35F")
        ]
        
        for i, (name, code, val, col) in enumerate(eras):
            btn = NX01Button(name, code, col)
            btn.clicked.connect(partial(self._set_era, val))
            era_grid.addWidget(btn, i // 2, i % 2)
        
        center_vbox.addLayout(era_grid)
        center_vbox.addStretch()
        
        # Кнопка Активації
        self.btn_activate = NX01Button("ЗАПУСК СИСТЕМИ", "INIT", "#269EEE")
        self.btn_activate.setFixedSize(300, 75)
        self.btn_activate.clicked.connect(self._launch)
        center_vbox.addWidget(self.btn_activate, alignment=Qt.AlignmentFlag.AlignCenter)
        
        frame_layout.addLayout(center_vbox, 1)
        
        # --- ПРАВА ПАНЕЛЬ (Утиліти) ---
        right_col = QVBoxLayout()
        right_col.setSpacing(12)
        
        lbl_util = QLabel("СЕРВІС")
        lbl_util.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_util.setStyleSheet(f"color: white; {get_lcars_font_style(14, 'normal')}")
        right_col.addWidget(lbl_util)
        
        utils = [
            ("DAT", "DATA HUB", "#269EEE"),
            ("MOD", "MODES", "#5C5C5C"),
            ("OFF", "SHUTDOWN", "#CE6363")
        ]
        for code, label, col in utils:
            btn = NX01Button(label, code, col)
            btn.setFixedSize(140, 60)
            if code == "OFF": btn.clicked.connect(QApplication.instance().quit)
            right_col.addWidget(btn)
            
        right_col.addStretch()
        frame_layout.addLayout(right_col)
        
        layout.addWidget(self.frame)

    def _set_faction(self, f):
        self.selected_faction = f
        print(f"NX01-SEL: Faction set to {f}")

    def _set_era(self, e):
        self.selected_era = e
        print(f"NX01-SEL: Era set to {e}")

    def _launch(self):
        self.selected.emit(self.selected_faction, self.selected_era)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    # Titanium Bridge Migration: import sys
    app = QApplication(sys.argv)
    from lcars.themes.lcars_palette import setup_lcars_font
    setup_lcars_font()
    view = NX01SelectorView()
    view.showFullScreen()
    sys.exit(app.exec())
