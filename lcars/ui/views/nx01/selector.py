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

from lcars.themes.palette import (
    LCARSEra, get_lcars_font_style, FactionEra, get_theme
)
from lcars.ui.base.widgets import LCARSButton

class NX01Frame(QFrame):
    """Simple, authentic metal frame of the 22nd Century (NX-01)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(60, 60, 60, 60)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        frame_color = QColor("#CCCCCC") # Metal
        
        # 1. Main Frame Background
        p.fillRect(0, 0, w, h, Qt.GlobalColor.black)
        
        # 2. Industrial Bars (Static and Clean)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(frame_color))
        
        # Outline Bars
        p.drawRect(20, 20, 40, h-40) # Left
        p.drawRect(w-60, 20, 40, h-40) # Right
        p.drawRect(20, 20, w-40, 30) # Top
        p.drawRect(20, h-50, w-40, 30) # Bottom

        # 3. Corner Lamps (TL Blue, TR Red)
        p.setBrush(QBrush(QColor("#1A4A9B"))) # Blue
        p.drawEllipse(15, 15, 50, 50)
        
        p.setBrush(QBrush(QColor("#D10000"))) # Red
        p.drawEllipse(w-65, 15, 50, 50)

        # 4. Vertical Text (Authentic labels)
        p.setPen(QPen(Qt.GlobalColor.black))
        font = QFont("Arial", 14)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 5)
        p.setFont(font)
        
        # Left Text
        p.save()
        p.translate(40, h // 2)
        p.rotate(-90)
        p.drawText(QRect(-200, -15, 400, 30), Qt.AlignmentFlag.AlignCenter, "NX-01 ENTERPRISE")
        p.restore()
        
        # Right Text
        p.save()
        p.translate(w-40, h // 2)
        p.rotate(90)
        p.drawText(QRect(-200, -15, 400, 30), Qt.AlignmentFlag.AlignCenter, "INTERFACE")
        p.restore()

class NX01Button(LCARSButton):
    """Authentic Split-Button (NX-01 Era)."""
    def __init__(self, text, code, color, parent=None):
        super().__init__(text, color, era=LCARSEra.COMS_22ND, parent=parent)
        self.code = code
        self._use_coms_paint = True
        self.setMinimumSize(220, 60)

    def paintEvent(self, event):
        p = QPainter(self)
        rect = self.rect()
        
        # Split: 55% Color, 45% Metal
        top_h = int(rect.height() * 0.55)
        top_rect = rect.adjusted(0, 0, 0, -(rect.height() - top_h))
        bot_rect = rect.adjusted(0, top_h, 0, 0)
        
        p.fillRect(top_rect, QColor(self.current_color))
        p.fillRect(bot_rect, QColor("#CCCCCC"))
        
        # Dot in top-right (as seen in some 22nd designs)
        p.setBrush(QBrush(Qt.GlobalColor.white))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(rect.width() - 12, 12, 6, 6)

        # Labels
        p.setPen(QColor("black"))
        p.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        p.drawText(top_rect.adjusted(10, 0, -20, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.code)
        
        p.setFont(QFont("Arial", 8))
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
            btn.setMinimumSize(140, 60)
            btn.clicked.connect(partial(self._set_faction, full))
            left_col.addWidget(btn)
        
        left_col.addStretch()
        frame_layout.addLayout(left_col)
        
        # --- CENTRAL PANEL (ERAS AND LOGO) ---
        center_vbox = QVBoxLayout()
        center_vbox.setSpacing(20)
        
        # Header
        logo_container = QVBoxLayout()
        logo_lbl = QLabel("STARFLEET COMMAND ◣")
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet(f"color: white; {get_lcars_font_style(28, 'normal')}")
        logo_container.addWidget(logo_lbl)
        
        sub_lbl = QLabel("CENTRAL PROCESSING NODE :: NX-01")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setStyleSheet(f"color: #CCCCCC; {get_lcars_font_style(12, 'normal')}")
        logo_container.addWidget(sub_lbl)
        
        center_vbox.addLayout(logo_container)
        
        # Era Grid (Industrial Style)
        era_grid = QGridLayout()
        era_grid.setSpacing(15)
        eras = [
            ("ENTERPRISE NX-01", "22-051", "22nd", "#5C5C5C"),
            ("CONSTITUTION (TOS)", "23-156", "23rd", "#FFE600"),
            ("EXCELSIOR (TMP)", "23-702", "23st", "#2062EE"),
            ("GALAXY (TNG)", "24-540", "24th", "#9EFFB5"),
            ("TITAN (V5.0)", "25-100", "25th", "#2A7193"),
            ("UNIVERSE (29ct)", "29-300", "29th", "#00A35F")
        ]
        
        for i, (name, code, val, col) in enumerate(eras):
            btn = NX01Button(name, code, col)
            btn.clicked.connect(partial(self._set_era, val))
            era_grid.addWidget(btn, i // 2, i % 2)
        
        center_vbox.addLayout(era_grid)
        center_vbox.addStretch()
        
        # Activation Control
        self.btn_activate = NX01Button("CONFIRM SYSTEM INITIALIZATION", "INIT", "#269EEE")
        self.btn_activate.setMinimumSize(400, 75)
        self.btn_activate.clicked.connect(self._launch)
        center_vbox.addWidget(self.btn_activate, alignment=Qt.AlignmentFlag.AlignCenter)
        
        frame_layout.addLayout(center_vbox, 1)
        
        # --- RIGHT PANEL (Utilities) ---
        right_col = QVBoxLayout()
        right_col.setSpacing(12)
        
        lbl_util = QLabel("SERVICE")
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
            btn.setMinimumSize(140, 60)
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
    from lcars.themes.palette import setup_lcars_font
    setup_lcars_font()
    view = NX01SelectorView()
    view.showFullScreen()
    sys.exit(app.exec())
