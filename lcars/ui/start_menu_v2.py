"""
LCARS High-Fidelity Start Menu (Access Menu)
A sophisticated grid-based overlay for system navigation.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QPushButton, QFrame, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from lcars.themes.lcars_palette import (
    LCARSEra, get_theme, get_lcars_font_style, 
    get_random_button_color, setup_lcars_font
)
from lcars.ui.base.widgets import LCARSButton

class LCARSStartMenu(QWidget):
    """Full-screen overlay start menu."""
    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Blur-like effect via semi-transparent dark background
        self.background = QFrame(self)
        self.background.setStyleSheet("background-color: rgba(0, 0, 0, 220);")
        
        self.init_ui()

    def resizeEvent(self, a0):
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.container.move((self.width() - self.container.width()) // 2, (self.height() - self.container.height()) // 2)
        super().resizeEvent(a0)

    def init_ui(self):
        self.container = QFrame(self)
        self.container.setFixedSize(1000, 700)
        self.container.setStyleSheet(f"background: #050505; border: 2px solid {self.theme['accent']}; border-radius: 20px;")
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("◤ MAIN ACCESS MENU")
        header.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(32, 'normal')}")
        layout.addWidget(header)
        
        grid = QGridLayout()
        grid.setSpacing(15)
        
        categories = [
            ("COMMUNICATIONS", "#99CCFF"),
            ("SENSORS", "#FF9966"),
            ("ENGINEERING", "#FFFF99"),
            ("TACTICAL", "#CC0000"),
            ("LOGISTICS", "#99FF99"),
            ("COMPUTING", "#CC99FF"),
            ("ASTROMETRICS", "#3399FF"),
            ("ARCHIVES", "#B1957A")
        ]
        
        for i, (name, color) in enumerate(categories):
            btn = QPushButton(name)
            btn.setFixedSize(220, 80)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: black;
                    border-radius: 5px;
                    {get_lcars_font_style(20, 'normal')}
                }}
                QPushButton:hover {{ background-color: white; }}
            """)
            grid.addWidget(btn, i // 3, i % 3)
            
        layout.addLayout(grid)
        layout.addStretch()
        
        # Close Button
        close_btn = LCARSButton("DISMISS", "#666666", era=self.era, faction=self.faction)
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignRight)

    def show_menu(self):
        self.showFullScreen()
        self.raise_()
