"""
CENTRAL COMMAND - MASTER BOOTLOADER
Unified Graphical Launch System for GEANT4 / LCARS Framework.
"""

import sys
import os
import traceback
from pathlib import Path

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QStackedWidget, 
                           QGridLayout, QFrame, QButtonGroup, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen, QBrush, QFontDatabase

# --- PATH SETUP ---
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- THEME/PALETTE IMPORT ---
try:
    from lcars.themes.theme import FactionEra, get_faction_palette
    from lcars.themes.palette import LCARSEra, ERA_COLOR_PALETTES, LCARSColorGenerator, get_theme
except ImportError as e:
    print(f"Theme System Import Failed: {e}")
    # Fallback/Mock for standalone run if needed (but user insisted on connecting them)
    sys.exit(1)

# --- CONFIG ---
FONT_FAMILY = "LCARS" # Will be verified at runtime

# Initial Palette (Starfleet 25th)
DEFAULT_PALETTE = ERA_COLOR_PALETTES[LCARSEra.LCARS_25TH]
COLOR_ORANGE = DEFAULT_PALETTE['button_colors'][7] # Approx Orange
COLOR_RED    = DEFAULT_PALETTE['button_colors'][4] # Approx Red
COLOR_BLUE   = DEFAULT_PALETTE['button_colors'][9] # Approx Blue
COLOR_BG     = "#000000"

TEXTS = {
    "EN": {
        "TITLE": "CENTRAL COMMAND",
        "ACCESS": "ACCESS CONTROL",
        "FED": "FEDERATION",
        "KLI": "KLINGON EMPIRE",
        "ROM": "ROMULAN STAR EMPIRE",
        "CRD": "CARDASSIAN UNION",
        "ERA_29": "29TH CENTURY",
        "ERA_25": "25TH CENTURY",
        "ERA_24ST": "24TH CENT. (SOV)",
        "ERA_24": "24TH CENTURY",
        "ERA_23ST": "23RD CENT. (MOV)",
        "ERA_23": "23RD CENTURY",
        "ERA_22": "22ND CENTURY",
        "EXIT": "SYSTEM EXIT",
        "LANG": "LANGUAGE: ENGLISH",
        "SELECT": "SELECT INTERFACE PROTOCOL"
    },
    "UA": {
        "TITLE": "ЦЕНТРАЛЬНЕ КОМАНДУВАННЯ",
        "ACCESS": "КОНТРОЛЬ ДОСТУПУ",
        "FED": "ФЕДЕРАЦІЯ",
        "KLI": "КЛІНГОНСЬКА ІМПЕРІЯ",
        "ROM": "РОМУЛАНСЬКА ЗОРЯНА ІМПЕРІЯ",
        "CRD": "КАРДАСІАНСЬКИЙ СОЮЗ",
        "ERA_29": "29-ТЕ СТОЛІТТЯ",
        "ERA_25": "25-ТЕ СТОЛІТТЯ",
        "ERA_24ST": "24-ТЕ (СОВЕРЕН)",
        "ERA_24": "24-ТЕ СТОЛІТТЯ",
        "ERA_23ST": "23-ТЄ (ФІЛЬМИ)",
        "ERA_23": "23-ТЄ СТОЛІТТЯ",
        "ERA_22": "22-ГЕ СТОЛІТТЯ",
        "EXIT": "ВИХІД ІЗ СИСТЕМИ",
        "LANG": "МОВА: УКРАЇНСЬКА",
        "SELECT": "ОБЕРІТЬ ПРОТОКОЛ ІНТЕРФЕЙСУ"
    }
}

CURRENT_LANG = "EN"

# --- CUSTOM WIDGETS ---

class LcarsElbow(QWidget):
    """Classic LCARS Corner Elbow"""
    def __init__(self, color=COLOR_ORANGE, text="", parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.text = text
        self.setFixedSize(200, 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Draw Elbow Shape
        w, h = self.width(), self.height()
        bar_h = 30
        
        # Top bar
        painter.drawRect(0, 0, w, bar_h) 
        # Vertical bar (left)
        painter.drawRect(0, 0, 100, h)
        
        # Inner curve mask
        painter.setBrush(QColor(COLOR_BG))
        painter.drawRoundedRect(100, bar_h, w, h, 60, 60)
        
        # Draw Text
        if self.text:
            painter.setPen(QColor("black"))
            painter.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
            painter.drawText(105, 5, w-105, bar_h-10, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self.text)


class LcarsButton(QPushButton):
    """Standard LCARS Pill/Block Button with Animation Support"""
    def __init__(self, text, color, parent=None, shape="pill"):
        super().__init__(text, parent)
        self.key = text 
        self._color = QColor(color)
        self.shape_type = shape
        self.setMinimumHeight(60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("border: none; background: transparent;")
        
    def _get_color(self):
        return self._color
        
    def _set_color(self, val):
        self._color = QColor(val)
        self.update()

    # Define the property for QPropertyAnimation to usage
    color = pyqtProperty(QColor, _get_color, _set_color)

    def set_color(self, color, animated=True):
        if not animated:
            self._set_color(color)
            return

        # Stop existing
        if hasattr(self, 'anim') and self.anim.state() == QPropertyAnimation.State.Running:
            self.anim.stop()
            
        self.anim = QPropertyAnimation(self, b"color")
        self.anim.setDuration(300) # 300ms smooth transition
        self.anim.setStartValue(self._color)
        self.anim.setEndValue(QColor(color))
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.anim.start()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        bg = self._color
        text_col = QColor("black")
        
        # ACTIVE STATE (Selected Era)
        # We blend the active color or override
        if self.isChecked():
            bg = QColor("#DDDDDD") 
        elif self.underMouse(): 
            bg = bg.lighter(120)
        elif self.isDown(): 
            bg = bg.darker(120)
        
        painter.setBrush(bg)
        painter.setPen(Qt.PenStyle.NoPen)
        
        if self.shape_type == "pill":
            radius = rect.height() / 2
            painter.drawRoundedRect(rect, radius, radius)
        elif self.shape_type == "left_round":
             path = QPainterPath()
             path.addRoundedRect(0, 0, rect.width(), rect.height(), rect.height()/2, rect.height()/2)
             painter.drawPath(path)
             # Fill right corners
             painter.drawRect(int(rect.width()/2), 0, int(rect.width()/2), int(rect.height()))
        elif self.shape_type == "rect":
             painter.drawRect(rect)
             
        # Text
        painter.setPen(text_col)
        painter.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Normal))
        
        # Align Right for LCARS menu buttons usually
        align = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter if self.shape_type == "left_round" else Qt.AlignmentFlag.AlignCenter
        margin = 20 if self.shape_type == "left_round" else 0
        painter.drawText(rect.adjusted(0,0,-margin,0), align, self.text())


class FactionCard(QFrame):
    clicked = pyqtSignal()
    
    def __init__(self, key, code, color, parent=None):
        super().__init__(parent)
        self.key = key
        self.color = QColor(color)
        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(2)
        self.code = code
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(220)
        
    def set_color(self, color):
        self.color = QColor(color)
        self.update()
        
    def mousePressEvent(self, event):
        self.clicked.emit()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        
        # Border
        pen = QPen(self.color)
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawRoundedRect(5, 5, w-10, h-10, 20, 20)
        
        # Fill faint
        painter.setBrush(QColor(self.color.red(), self.color.green(), self.color.blue(), 30))
        painter.drawRoundedRect(5, 5, w-10, h-10, 20, 20)
        
        # Code Big
        painter.setPen(QColor(self.color.red(), self.color.green(), self.color.blue(), 80))
        # FIXED: Removed Bold
        painter.setFont(QFont(FONT_FAMILY, 80, QFont.Weight.Normal))
        painter.drawText(20, 20, w-40, h-40, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom, self.code)
        
        # Title
        painter.setPen(self.color)
        # Use localized text
        title = TEXTS[CURRENT_LANG][self.key]
        
        # Auto-size font?
        font_size = 24
        if len(title) > 15: font_size = 18 
        # FIXED: Removed Bold
        painter.setFont(QFont(FONT_FAMILY, font_size, QFont.Weight.Normal))
        
        painter.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, title)

class AppContainer(QWidget):
    """Wrapper for external apps to add a Back Button"""
    return_signal = pyqtSignal()

    def __init__(self, app_widget):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(app_widget)
        
        # Floating Return Button
        self.btn_back = QPushButton(self)
        self.btn_back.setText("◄ CENTRAL COMMAND")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        # Style: Semi-transparent red block top-left
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: rgba(150, 0, 0, 0.9);
                color: #FFCCCC;
                font-weight: bold;
                border: none;
                border-bottom-right-radius: 20px;
                padding: 15px 30px;
                font-family: Arial;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(200, 0, 0, 1.0);
                color: white;
            }
        """)
        self.btn_back.adjustSize()
        self.btn_back.clicked.connect(self.return_signal.emit)
        self.btn_back.move(0, 0)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Ensure button stays top left
        self.btn_back.move(0, 0)


class CentralCommandLoader(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load Font
        try:
            # Try to load lcars.ttf from resources
            font_path = os.path.join(project_root, "resources", "fonts", "lcars.ttf")
            if os.path.exists(font_path):
                id = QFontDatabase.addApplicationFont(font_path)
                families = QFontDatabase.applicationFontFamilies(id)
                if families:
                    global FONT_FAMILY
                    FONT_FAMILY = families[0]
                    print(f"Font loaded: {FONT_FAMILY}")
            else:
                print("Font file not found, using default.")
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            print(f"Font load warning: {e}")
            
        self.setWindowTitle("LCARS CENTRAL COMMAND")
        self.showFullScreen()
        self.setStyleSheet(f"background-color: {COLOR_BG}; color: {COLOR_ORANGE};")
        
        self.current_era = "25th"
        self.systems = {} # Cache for loaded protocols
        
        self.setup_ui()
        self.update_texts()

    def setup_ui(self):
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # --- PAGE 1: MAIN LAUNCHER ---
        self.launcher_widget = QWidget()
        self.main_layout = QHBoxLayout(self.launcher_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)
        
        # LEFT COLUMN (Navigation)
        self.left_col = QVBoxLayout()
        self.left_col.setSpacing(10)
        
        # Elbow
        self.elbow = LcarsElbow(COLOR_ORANGE, "LCARS")
        self.left_col.addWidget(self.elbow)
        

        # Era Buttons
        self.era_group = QButtonGroup()
        self.btn_eras = {}
        
        # Extended Eras
        eras_data = [
            ("29th", "ERA_29", ERA_COLOR_PALETTES[LCARSEra.TCARS_29TH]['button_colors'][0]),
            ("25th", "ERA_25", ERA_COLOR_PALETTES[LCARSEra.LCARS_25TH]['button_colors'][7]),
            ("24st", "ERA_24ST", ERA_COLOR_PALETTES[LCARSEra.LCARS_24ST]['button_colors'][5]), # 24th Century Sovereign
            ("24th", "ERA_24", ERA_COLOR_PALETTES[LCARSEra.LCARS_24TH]['button_colors'][1]),
            ("23st", "ERA_23ST", ERA_COLOR_PALETTES[LCARSEra.PCARS_23ST]['button_colors'][3]), # Movie Era
            ("23rd", "ERA_23", ERA_COLOR_PALETTES[LCARSEra.PCARS_23RD]['button_colors'][1]),
            ("22nd", "ERA_22", ERA_COLOR_PALETTES[LCARSEra.COMS_22ND]['button_colors'][0])
        ]

        
        for eid, key, color in eras_data:
            btn = LcarsButton(key, color, shape="left_round")
            btn.setCheckable(True)
            # Use factory to capture eid
            btn.clicked.connect(self.make_era_setter(eid))
            
            self.left_col.addWidget(btn)
            self.era_group.addButton(btn)
            self.btn_eras[key] = btn # Map key to button
            if eid == "25th": btn.setChecked(True)
            
        self.left_col.addStretch()
        
        # Exit Button
        c_exit = ERA_COLOR_PALETTES[LCARSEra.LCARS_25TH]['alert_colors'][1]
        self.btn_exit = LcarsButton("EXIT", c_exit, shape="left_round")
        self.btn_exit.clicked.connect(self.close)
        self.left_col.addWidget(self.btn_exit)
        
        self.main_layout.addLayout(self.left_col, 1)
        
        # CENTER AREA
        self.center_col = QVBoxLayout()
        self.center_col.setContentsMargins(20, 0, 0, 0)
        
        # Top Bar (Header)
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(30)
        
        # Bar Layout for Lang Switch
        bar_layout = QHBoxLayout(self.top_bar)
        bar_layout.setContentsMargins(20, 0, 20, 0)
        bar_layout.addStretch()
        
        self.btn_lang = QPushButton("LANG: EN")
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang.setStyleSheet("border: none; font-weight: normal; color: black; font-family: Arial;")
        self.btn_lang.clicked.connect(self.toggle_lang)
        bar_layout.addWidget(self.btn_lang)
        
        self.center_col.addWidget(self.top_bar)
        self.center_col.addSpacing(20)
        
        # Title
        self.lbl_title = QLabel("SELECT INTERFACE PROTOCOL")
        self.lbl_title.setFont(QFont(FONT_FAMILY, 28))
        self.lbl_title.setStyleSheet(f"color: {COLOR_ORANGE};")
        self.center_col.addWidget(self.lbl_title)
        
        # Faction Grid
        self.grid = QGridLayout()
        self.grid.setSpacing(30)
        
        # Initial Colors (25th Default)
        c_fed = ERA_COLOR_PALETTES[LCARSEra.LCARS_25TH]['button_colors'][9]
        c_kli = get_faction_palette(FactionEra.KLINGON_24TH)['button_colors'][2]
        c_rom = get_faction_palette(FactionEra.ROMULAN_24TH)['button_colors'][1]
        c_crd = get_faction_palette(FactionEra.CARDASSIAN_24TH)['button_colors'][0]
        
        # Reduce Height of FactionCard (Implicitly doing it in loop or constructor would be better)
        # But here we used class method incorrectly.
        
        self.card_fed = FactionCard("FED", "UFP", c_fed)
        self.card_fed.setFixedHeight(160)
        self.card_fed.clicked.connect(lambda: self.launch("FED"))
        self.grid.addWidget(self.card_fed, 0, 0)

        self.card_kli = FactionCard("KLI", "KDF", c_kli)
        self.card_kli.setFixedHeight(160)
        self.card_kli.clicked.connect(lambda: self.launch("KLI"))
        self.grid.addWidget(self.card_kli, 0, 1)

        self.card_rom = FactionCard("ROM", "RSE", c_rom)
        self.card_rom.setFixedHeight(160)
        self.card_rom.clicked.connect(lambda: self.launch("ROM"))
        self.grid.addWidget(self.card_rom, 1, 0)

        self.card_crd = FactionCard("CRD", "CU", c_crd)
        self.card_crd.setFixedHeight(160)
        self.card_crd.clicked.connect(lambda: self.launch("CRD"))
        self.grid.addWidget(self.card_crd, 1, 1)
        
        self.center_col.addLayout(self.grid)
        self.center_col.addStretch()
        
        self.main_layout.addLayout(self.center_col, 4)
        self.stack.addWidget(self.launcher_widget)
        
        # Refresh Style for Init
        self.update_style_for_era("25th")

    def make_era_setter(self, eid):
        return lambda: self.set_era(eid)

    def set_era(self, era):
        self.current_era = era
        print(f"Era set to: {era}")
        self.update_style_for_era(era)

    def update_style_for_era(self, era):
        # Determine Palette Key
        palette_key = LCARSEra.LCARS_25TH
        if era == "24th": palette_key = LCARSEra.LCARS_24TH
        elif era == "24st": palette_key = LCARSEra.LCARS_24ST
        elif era == "23st": palette_key = LCARSEra.PCARS_23ST
        elif era == "23rd": palette_key = LCARSEra.PCARS_23RD
        elif era == "22nd": palette_key = LCARSEra.COMS_22ND
        elif era == "29th": palette_key = LCARSEra.TCARS_29TH
            
        # Use Dynamic Generator
        gen = LCARSColorGenerator(palette_key)
        
        # 1. Update Layout Colors using Generator logic
        main_color = gen.get_color_at_index(0)
        accent_color = gen.get_color_at_index(4) if len(gen.palette) > 4 else main_color
        
        # Update Sidebar Buttons to match the CURRENT ERA palette
        # This makes the whole interface "skin" change
        # We skip checking 'eid' vs 'era' for color, we just apply the palette pattern
        idx = 2 # Start offset for buttons
        for btn in self.btn_eras.values():
            # Get next color in sequence from the generator
            # If btn is checked (active), we might handle it in paintEvent, 
            # but setting the base color to the palette ensures the 'theme' is consistent.
            col = gen.get_color_at_index(idx)
            btn.set_color(col, animated=True)
            idx += 1
            
        # Elbow
        self.elbow.color = QColor(main_color)
        self.elbow.update()
        
        # Header Bar
        self.top_bar.setStyleSheet(f"background-color: {main_color}; border-radius: 15px;")
        
        # Title Color
        self.lbl_title.setStyleSheet(f"color: {accent_color};")
        
        # Exit Button
        # Use Alert Palette from current era
        alert_col = gen.get_color_at_index(0, alert_level=1)
        self.btn_exit.set_color(alert_col, animated=True)
        
        # 2. Update Faction Cards with proper Era variants
        # FEDERATION - Use the generator's secondary color
        fed_col = gen.get_color_at_index(1)
        self.card_fed.set_color(fed_col)
        
        # ALIEN FACTIONS - Use their specific generators
        # Klingon
        try:
            k_key = f"klingon_{era}"
            if any(k.value == k_key for k in FactionEra):
                 k_pal = get_faction_palette(FactionEra(k_key)) # Dictionary
                 self.card_kli.set_color(k_pal['button_colors'][2]) # Red-ish usually
            else:
                 # Default logic if specific era missing
                 # Use alert color from current era as fallback for "Alien/Hostile" look
                 self.card_kli.set_color(gen.get_color_at_index(0, alert_level=1)) 
        except:
             self.card_kli.set_color("#CC0000")
        
        # Romulan
        try:
            r_key = f"romulan_{era}"
            if any(k.value == r_key for k in FactionEra):
                 r_pal = get_faction_palette(FactionEra(r_key))
                 self.card_rom.set_color(r_pal['button_colors'][1])
            else:
                 self.card_rom.set_color("#009900")
        except:
             self.card_rom.set_color("#009900")

        # Cardassia (Mostly 24th/25th)
        try:
            c_key = f"cardassian_{era}"
            # Mapping 23rd cardassians might fail, fallback to 24th
            if "23" in c_key or "22" in c_key: c_key = "cardassian_24th"
            
            # Simple check if enum value exists
            if any(k.value == c_key for k in FactionEra):
                 c_pal = get_faction_palette(FactionEra(c_key))
                 self.card_crd.set_color(c_pal['button_colors'][0])
            else:
                 self.card_crd.set_color("#CC8800")
        except:
             self.card_crd.set_color("#CC8800")
             
        # Final refresh of buttons
        for btn in self.btn_eras.values():
            btn.update()

    def toggle_lang(self):
        global CURRENT_LANG
        CURRENT_LANG = "UA" if CURRENT_LANG == "EN" else "EN"
        self.update_texts()

    def update_texts(self):
        t = TEXTS[CURRENT_LANG]
        self.lbl_title.setText(t["SELECT"])
        self.btn_lang.setText(t["LANG"])
        
        # Update Eras via stored keys
        for key, btn in self.btn_eras.items():
            btn.setText(t[key])
            
        self.btn_exit.setText(t["EXIT"])
        
        # Force repaint of cards
        self.card_fed.update()
        self.card_kli.update()
        self.card_rom.update()
        self.card_crd.update()

    def launch(self, faction):
        # Determine module based on Faction + Era
        print(f"Request Launch: {faction} @ {self.current_era}")
        
        try:
            widget = None
            if faction == "FED":
                if self.current_era == "25th":
                    from archive.lcars_central import LCARSDashboard
                    widget = LCARSDashboard()
                elif self.current_era == "22nd":
                    from archive.PCARS_22nd import PCARS22ndCentury
                    widget = PCARS22ndCentury()
                elif self.current_era == "23rd":
                    # Early 23rd / The Cage
                    from archive.PCARS_23rd_old import PCARS23Early
                    widget = PCARS23Early()
                elif self.current_era == "23st":
                    # Late 23rd / Movie Era
                    from archive.PCARS_23st import PCARS23Late
                    widget = PCARS23Late()
                else: 
                    # 24th Century default
                    from archive.LCARS_24th import LCARS24thCentury
                    widget = LCARS24thCentury()
            
            elif faction == "KLI":
                from archive.Klingon_system import KlingonSystem
                widget = KlingonSystem()
                
            elif faction == "ROM":
                from archive.romulan_components import RomulanComponentsDemo
                widget = RomulanComponentsDemo()
                
            elif faction == "CRD":
                from archive.cardassian_theme import CardassianSystem
                widget = CardassianSystem()

            if widget:
                # Embed the window in wrapper
                widget.setWindowFlags(Qt.WindowType.Widget)
                wrapper = AppContainer(widget)
                wrapper.return_signal.connect(self.return_to_main)
                
                self.stack.addWidget(wrapper)
                self.stack.setCurrentWidget(wrapper)
                
        except Exception as e:
                
            logger.exception("Unhandled exception in %s", __file__)
                
            raise

            print(f"Launch Error: {e}")
            import traceback
            traceback.print_exc()

    def return_to_main(self):
        # Remove current widget and go back to launcher
        current = self.stack.currentWidget()
        if current and current != self.launcher_widget:
            self.stack.removeWidget(current)
            current.deleteLater()
        self.stack.setCurrentWidget(self.launcher_widget)
                
    def launch_application(self, app_path):
        print(f"Launching application: {app_path}")
        print(f"Launch Error: {e}")
        import traceback
import logging
logger = logging.getLogger(__name__)
traceback.print_exc()

def main():
    app = QApplication(sys.argv)
    window = CentralCommandLoader()
    window.show()
    
    print("🖖 LCARS Central Command launched!")
    print("🚀 All systems operational")
    
    return app.exec()

if __name__ == "__main__":
    main()
