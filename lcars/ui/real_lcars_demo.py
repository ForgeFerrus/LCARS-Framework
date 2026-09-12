"""
Справжній LCARS Demo з різними формами кнопок для епох
22nd: прямокутні з гострими кутами (Enterprise NX-01)
23rd: круглі червоні (TOS)
24th: класичні заокруглені помаранчеві (TNG)
"""

# Titanium Bridge Migration: import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor

# Кольори для кожної епохи
ERA_COLORS = {
    '22nd': {
        'bg': '#1E3A8A',      # темно-синій
        'text': '#E0E0FF',    # світло-блакитний
        'border': '#4C4C7A'   # синя рамка
    },
    '23rd': {
        'bg': '#FF0000',      # червоний
        'text': '#FFFFFF',    # білий
        'border': '#D3A200'   # золотий
    },
    '24th': {
        'bg': '#FFCC66',      # помаранчевий
        'text': '#000000',    # чорний
        'border': '#664466'   # фіолетовий
    }
}

class LCARS22ndButton(QPushButton):
    """22nd століття - прямокутна з гострими кутами"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.apply_style()
        
    def apply_style(self):
        colors = ERA_COLORS['22nd']
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['bg']};
                color: {colors['text']};
                border: 2px solid {colors['border']};
                border-radius: 0px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
                font-family: 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: #2C4B9E;
            }}
            QPushButton:pressed {{
                background-color: #3B5DB8;
            }}
        """)

class LCARS23rdButton(QPushButton):
    """23rd століття - кругла червона кнопка"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(100, 100)
        self.apply_style()
        
    def apply_style(self):
        colors = ERA_COLORS['23rd']
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['bg']};
                color: {colors['text']};
                border: 3px solid {colors['border']};
                border-radius: 50px;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                font-family: 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
        """)

class LCARS24thButton(QPushButton):
    """24th століття - класична LCARS з заокругленнями"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.apply_style()
        
    def apply_style(self):
        colors = ERA_COLORS['24th']
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['bg']};
                color: {colors['text']};
                border: 2px solid {colors['border']};
                border-radius: 25px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 2px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
        """)

class LCARSLabel(QLabel):
    """LCARS текст"""
    
    def __init__(self, text, size=16, color='#FFFFFF', parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {size}px;
                font-weight: bold;
                background: transparent;
                letter-spacing: 2px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class LCARSPanel(QWidget):
    """LCARS панель"""
    
    def __init__(self, era='24th', parent=None):
        super().__init__(parent)
        colors = ERA_COLORS.get(era, ERA_COLORS['24th'])
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #000000;
                border: 2px solid {colors['border']};
                border-radius: 10px;
            }}
        """)

class RealLCARSDemo(QMainWindow):
    """Справжній LCARS демо з різними формами"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("REAL LCARS DEMO - Different Button Shapes")
        self.setGeometry(100, 100, 1400, 800)
        self.setup_ui()
        
    def setup_ui(self):
        # Фон
        self.setStyleSheet("background-color: #000000;")
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основний layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Заголовок
        header = LCARSLabel("LCARS INTERFACE - DIFFERENT ERAS", 24)
        main_layout.addWidget(header)
        
        # 22nd століття секція
        section_22nd = LCARSPanel('22nd')
        layout_22nd = QVBoxLayout(section_22nd)
        layout_22nd.setContentsMargins(20, 20, 20, 20)
        
        title_22nd = LCARSLabel("22nd CENTURY - ENTERPRISE NX-01", 18, ERA_COLORS['22nd']['text'])
        layout_22nd.addWidget(title_22nd)
        
        buttons_22nd = QHBoxLayout()
        buttons_22nd.addWidget(LCARS22ndButton("COMMAND"))
        buttons_22nd.addWidget(LCARS22ndButton("TACTICAL"))
        buttons_22nd.addWidget(LCARS22ndButton("SCIENCE"))
        layout_22nd.addLayout(buttons_22nd)
        
        main_layout.addWidget(section_22nd)
        
        # 23rd століття секція
        section_23rd = LCARSPanel('23rd')
        layout_23rd = QVBoxLayout(section_23rd)
        layout_23rd.setContentsMargins(20, 20, 20, 20)
        
        title_23rd = LCARSLabel("23rd CENTURY - STAR TREK TOS", 18, ERA_COLORS['23rd']['text'])
        layout_23rd.addWidget(title_23rd)
        
        buttons_23rd = QHBoxLayout()
        buttons_23rd.addWidget(LCARS23rdButton("RED"))
        buttons_23rd.addWidget(LCARS23rdButton("ALERT"))
        buttons_23rd.addWidget(LCARS23rdButton("WARP"))
        layout_23rd.addLayout(buttons_23rd)
        
        main_layout.addWidget(section_23rd)
        
        # 24th століття секція
        section_24th = LCARSPanel('24th')
        layout_24th = QVBoxLayout(section_24th)
        layout_24th.setContentsMargins(20, 20, 20, 20)
        
        title_24th = LCARSLabel("24th CENTURY - THE NEXT GENERATION", 18, ERA_COLORS['24th']['text'])
        layout_24th.addWidget(title_24th)
        
        buttons_24th = QHBoxLayout()
        buttons_24th.addWidget(LCARS24thButton("COMMAND"))
        buttons_24th.addWidget(LCARS24thButton("TACTICAL"))
        buttons_24th.addWidget(LCARS24thButton("SCIENCE"))
        layout_24th.addLayout(buttons_24th)
        
        main_layout.addWidget(section_24th)
        
        # Статус панель
        status_panel = LCARSPanel()
        status_layout = QHBoxLayout(status_panel)
        status_layout.setContentsMargins(20, 10, 20, 10)
        
        status_label = LCARSLabel("ALL SYSTEMS OPERATIONAL", 14, '#00CC66')
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        
        era_label = LCARSLabel("MULTI-ERA INTERFACE", 14, '#FFCC66')
        status_layout.addWidget(era_label)
        
        main_layout.addWidget(status_panel)

def main():
    app = QApplication(sys.argv)
    
    # Встановлюємо шрифт
    font = QFont("Arial", 10)
    app.setFont(font)
    
    window = RealLCARSDemo()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
