"""
CENTRAL COMMAND - MASTER BOOTLOADER
Unified Graphical Launch System for GEANT4 / LCARS Framework.
AUTONOMOUS VERSION - No external imports
"""

import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QStackedWidget, 
                           QGridLayout, QFrame, QButtonGroup, QSizePolicy, QMessageBox)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen, QBrush, QFontDatabase

# --- BUILT-IN PALETTE (TitanPalette equivalent) ---
class Colors:
    """Built-in LCARS color palette - no external dependencies"""
    Buttons = [
        "#2E86C1", "#1ABC9C", "#F39C12", "#E74C3C",
        "#9B59B6", "#34495E", "#16A085", "#2980B9"
    ]
    Panels = ["#17202A", "#212F3D", "#1B2631"]
    Accent = ["#F1C40F", "#EC7063"]
    Alert = ["#E74C3C", "#F39C12"]
    Orange = "#F39C12"
    Red = "#E74C3C"
    Blue = "#2E86C1"
    Black = "#000000"
    White = "#FFFFFF"

# --- CONFIG ---
FONT_FAMILY = "LCARS"
COLOR_ORANGE = Colors.Orange
COLOR_RED = Colors.Red
COLOR_BLUE = Colors.Blue
COLOR_BG = Colors.Black

# --- TEXTS ---
CURRENT_LANG = "EN"
TEXTS = {
    "EN": {
        "SELECT": "SELECT INTERFACE PROTOCOL",
        "EXIT": "EXIT",
        "LANG": "LANG: EN",
        "FED": "FEDERATION",
        "KLI": "KLINGON",
        "ROM": "ROMULAN",
        "CRD": "CARDASSIAN"
    },
    "UA": {
        "SELECT": "ВИБЕРІТЬ ПРОТОКОЛ",
        "EXIT": "ВИХІД",
        "LANG": "МОВА: UA",
        "FED": "ФЕДЕРАЦІЯ",
        "KLI": "КЛІНГОНИ",
        "ROM": "РОМУЛАНИ",
        "CRD": "КАРДАСІАНИ"
    }
}

# --- CUSTOM WIDGETS ---
class LcarsElbow(QFrame):
    """LCARS Elbow widget"""
    def __init__(self, color=COLOR_ORANGE, text="LCARS", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {color}; border-radius: 20px;")
        self.setFixedSize(200, 100)
        layout = QVBoxLayout(self)
        label = QLabel(text)
        label.setStyleSheet("color: #000000; font-weight: bold; font-size: 16px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

class LcarsButton(QPushButton):
    """LCARS styled button"""
    def __init__(self, text, color, shape="left", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        radius = "25px 5px 5px 25px" if "left" in shape else "5px 25px 25px 5px"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #000000;
                border: none;
                border-radius: {radius};
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #FFFFFF; }}
        """)

class LCARSButton(QPushButton):
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
    """Clickable faction card"""
    clicked = pyqtSignal()
    
    def __init__(self, name, code, color, parent=None):
        super().__init__(parent)
        self.name = name
        self.key = name
        self.code = code
        self.color = QColor(color)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 20px;
            }}
        """)
        self.setFixedSize(200, 150)
        self.setLineWidth(2)
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
        # Simple menu buttons (no eras)
        menu_items = [
            ("SYSTEM", Colors.Blue),
            ("TOOLS", Colors.Accent[0]),
            ("CONFIG", Colors.Buttons[1]),
        ]
        
        for label, color in menu_items:
            btn = LcarsButton(label, color, shape="left_round")
            btn.setCheckable(False)
            self.left_col.addWidget(btn)
            
        self.left_col.addStretch()
        
        # Exit Button
        self.btn_exit = LcarsButton("EXIT", Colors.Red, shape="left_round")
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
        
        # Simple action buttons using built-in colors
        c_fed = Colors.Buttons[0]
        c_kli = Colors.Buttons[2]
        c_rom = Colors.Buttons[1]
        c_crd = Colors.Buttons[3]
        
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
        self.update_style()

    def set_era(self, era):
        print(f"Era set to: {era}")

    def update_style(self):
        # Simplified - no era switching
        pass

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
        """Launch faction module with error handling"""
        print(f"Launch: {faction}")
        
        module_map = {
            "FED": ("LCARS_25th", "LCARS25thDashboard"),
            "KLI": ("Klingon_system", "KlingonMainWindow"),
            "ROM": ("romulan_components", "RomulanMainWindow"),
            "CRD": ("cardassian_theme", "CardassianMainWindow"),
        }
        
        try:
            if faction not in module_map:
                QMessageBox.warning(self, "LCARS", f"Unknown faction: {faction}")
                return
                
            module_name, class_name = module_map[faction]
            
            # Dynamic import with error handling
            try:
                # Use importlib to load from file directly
                import importlib.util
                file_path = os.path.join(os.path.dirname(__file__), f"{module_name}.py")
                
                if not os.path.exists(file_path):
                    raise ImportError(f"File not found: {file_path}")
                
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                widget_class = getattr(module, class_name)
                widget = widget_class()
            except (ImportError, AttributeError, FileNotFoundError) as e:
                print(f"Module import error: {e}")
                # Fallback: show info that module needs fixing
                QMessageBox.information(self, "LCARS", 
                    f"{faction} module not available.\n"
                    f"Module: {module_name}\n"
                    f"Error: {str(e)[:100]}")
                return
            
            # Embed widget
            widget.setWindowFlags(Qt.WindowType.Widget)
            wrapper = AppContainer(widget)
            wrapper.return_signal.connect(self.return_to_main)
            
            self.stack.addWidget(wrapper)
            self.stack.setCurrentWidget(wrapper)
            print(f"✅ {faction} module launched successfully")
            
        except Exception as e:
            print(f"Launch error: {e}")
            QMessageBox.critical(self, "LCARS Error", f"Failed to launch {faction}:\n{str(e)[:200]}")

    def return_to_main(self):
        # Remove current widget and go back to launcher
        current = self.stack.currentWidget()
        if current and current != self.launcher_widget:
            self.stack.removeWidget(current)
            current.deleteLater()
        self.stack.setCurrentWidget(self.launcher_widget)
                
    def launch_application(self, app_path):
        print(f"Launching application: {app_path}")
        try:
            # Add application launching logic here
            pass
        except Exception as e:
            print(f"Launch Error: {e}")
            import traceback
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
