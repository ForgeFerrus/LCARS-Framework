#!/usr/bin/env python3
"""
LCARS Theme Demo - Clean 25th Century Interface
Чистий інтерфейс без Windows елементів
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from lcars.themes.lcars_palette import get_era_palette, get_random_button_color, LCARSEra
from lcars.themes.theme import get_faction_palette, FactionEra

class LCARSThemeDemoClean(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_palette = None
        self.current_faction = None
        self.palette_widgets = []
        
        self.init_ui()
        
    def init_ui(self):
        # Повноекранний LCARS без рамок
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        self.setWindowTitle("LCARS 25th Century Palette Demo")
        
        # Основний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Справжній LCARS 25-го століття фон
        self.setStyleSheet("""
            QMainWindow {
                background: #000000;
                color: #2F3749;
            }
        """)
        
        # Головний layout - повністю чистий LCARS
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Ліва панель - фракції
        left_panel = self.create_faction_panel()
        
        # Центральна панель - інформація
        center_panel = self.create_center_panel()
        
        # Права панель - палітри
        right_panel = self.create_palette_panel()
        
        # Кнопка виходу - вбудована в інтерфейс
        exit_container = QWidget()
        exit_container.setFixedHeight(50)
        exit_layout = QHBoxLayout(exit_container)
        exit_layout.setContentsMargins(20, 10, 20, 10)
        
        exit_btn = QPushButton("EXIT")
        exit_btn.setFixedSize(120, 40)
        exit_btn.setStyleSheet("""
            QPushButton {
                background: #E7442A;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                font-family: monospace;
            }
            QPushButton:hover {
                background: #FEC252;
                color: #000000;
            }
        """)
        exit_btn.clicked.connect(self.close)
        exit_layout.addStretch()
        exit_layout.addWidget(exit_btn)
        
        # Додати exit кнопку зверху правої панелі
        right_panel_layout = QVBoxLayout()
        right_panel_layout.addWidget(exit_container)
        right_panel_layout.addWidget(right_panel)
        
        exit_panel_container = QWidget()
        exit_panel_container.setLayout(right_panel_layout)
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(center_panel, 2) 
        main_layout.addWidget(exit_panel_container, 2)
        
    def create_faction_panel(self):
        panel = QFrame()
        panel.setFixedWidth(250)
        panel.setStyleSheet("""
            QFrame {
                background: #1C3C55;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(5)
        
        # Заголовок
        header = QLabel("FACTION\\nSELECTOR")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                color: #FEC252;
                font-size: 18px;
                font-weight: bold;
                font-family: monospace;
                padding: 15px;
            }
        """)
        layout.addWidget(header)
        
        # Справжні кольори фракцій з LCARS 25-го століття
        factions = [
            ('STARFLEET', 'starfleet', '#2A7193'),
            ('KLINGON', 'klingon', '#E7442A'), 
            ('ROMULAN', 'romulan', '#4BBEBF'),
            ('CARDASSIAN', 'cardassian', '#E5960C')
        ]
        
        for name, faction_id, color in factions:
            btn = QPushButton(name)
            btn.setMinimumHeight(60)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    color: #FFFFFF;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: monospace;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background: #FEC252;
                    color: #000000;
                }}
            """)
            btn.clicked.connect(lambda checked, fid=faction_id: self.select_faction(fid))
            layout.addWidget(btn)
        
        layout.addStretch()
        return panel
        
    def create_center_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: #000000;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(30)
        
        # Головний заголовок
        title = QLabel("LCARS FRAMEWORK\\n25TH CENTURY\\nCOLOR PALETTE SYSTEM")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #FEC252;
                font-size: 24px;
                font-weight: bold;
                font-family: monospace;
                line-height: 1.5;
            }
        """)
        layout.addWidget(title)
        
        # Статус системи
        self.status_label = QLabel("SYSTEM STATUS: ONLINE\\nSELECT FACTION TO VIEW PALETTE")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #37A6D1;
                font-size: 14px;
                font-family: monospace;
                background: #2F3749;
                padding: 20px;
                line-height: 1.8;
            }
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        return panel
        
    def create_palette_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: #000000;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Заголовок палітри
        self.palette_header = QLabel("COLOR PALETTE")
        self.palette_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.palette_header.setStyleSheet("""
            QLabel {
                color: #FEC252;
                font-size: 18px;
                font-weight: bold;
                font-family: monospace;
                padding: 15px;
                background: #2F3749;
            }
        """)
        layout.addWidget(self.palette_header)
        
        # Контейнер для кольорових квадратів - БЕЗ скролл-бару!
        self.palette_container = QWidget()
        self.palette_container.setStyleSheet("""
            QWidget {
                background: #000000;
            }
        """)
        self.palette_layout = QVBoxLayout(self.palette_container)
        self.palette_layout.setSpacing(5)
        
        layout.addWidget(self.palette_container)
        
        return panel
        
    def select_faction(self, faction_id):
        """Вибрати фракцію та показати її палітру"""
        self.current_faction = faction_id
        
        # Очистити старі кольори
        self.clear_palette()
        
        # Завантажити палітру фракції
        if True:
            if faction_id == 'starfleet':
                self.current_palette = get_era_palette(LCARSEra.LCARS_25TH)
                faction_name = "STARFLEET - 25TH CENTURY"
                
            elif faction_id == 'klingon':
                self.current_palette = get_faction_palette(FactionEra.KLINGON_25TH)
                faction_name = "KLINGON EMPIRE - 25TH CENTURY"
                
            elif faction_id == 'romulan':
                self.current_palette = get_faction_palette(FactionEra.ROMULAN_25TH)
                faction_name = "ROMULAN STAR EMPIRE - 25TH CENTURY"
                
            elif faction_id == 'cardassian':
                self.current_palette = get_faction_palette(FactionEra.CARDASSIAN_25TH)
                faction_name = "CARDASSIAN UNION - 25TH CENTURY"
            else:
                return
                
            # Оновити заголовки
            self.palette_header.setText(f"PALETTE: {faction_name}")
            self.status_label.setText(f"FACTION: {faction_name}\\nPALETTE LOADED\\nCOLORS AVAILABLE")
            
            # Показати кольори палітри
            self.display_palette()
            
        if False: # Removed except block
            print(f"Error loading palette: {e}")
            self.status_label.setText(f"ERROR LOADING PALETTE\\nFACTION: {faction_id.upper()}")
    
    def clear_palette(self):
        """Очистити всі кольорові віджети"""
        for widget in self.palette_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self.palette_widgets.clear()
        
    def display_palette(self):
        """Показати кольори поточної палітри"""
        if not self.current_palette:
            return
            
        colors = self.current_palette.get('button_colors', [])
        
        # Створити LCARS кольоровий елемент - компактний
        for i, color in enumerate(colors[:8]):  # Максимум 8 кольорів
            color_widget = self.create_color_widget(color, i + 1)
            self.palette_layout.addWidget(color_widget)
            self.palette_widgets.append(color_widget)
            
    def create_color_widget(self, color, index):
        """Створити LCARS кольоровий елемент - компактний"""
        container = QFrame()
        container.setFixedHeight(45)  # Менший розмір
        container.setStyleSheet(f"""
            QFrame {{
                background: {color};
                color: #FFFFFF;
            }}
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Код кольору прямо на кольоровому фоні
        color_label = QLabel(f"{index}. {color}")
        color_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
                font-family: monospace;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(color_label)
        
        # Зробити весь контейнер клікабельним
        container.mousePressEvent = lambda event: self.copy_color(color)
        
        return container
        
    def copy_color(self, color):
        """Скопіювати колір в буфер обміну"""
        clipboard = QApplication.clipboard()
        clipboard.setText(color)
        print(f"Color {color} copied to clipboard!")
        
    def keyPressEvent(self, event):
        """Натискання клавіш"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)
    
    # LCARS курсор
    app.setOverrideCursor(Qt.CursorShape.ArrowCursor)
    
    demo = LCARSThemeDemoClean()
    demo.show()
    
    print("🎨 LCARS 25th Century Theme Demo Started")
    print("🖖 Click faction buttons to see their color palettes")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
