#!/usr/bin/env python3
"""
LCARS Theme Demo - Простий інтерфейс з алгоритмом палітр
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_random_button_color
from lcars.themes.theme import FactionEra, get_faction_palette
from lcars.ui.widgets.common import create_lcars_button

class LCARSThemeDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_palette = None
        self.palette_widgets = []
        self.button_container = None
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("LCARS FRAMEWORK - PALETTE DEMO")
        self.showFullScreen()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QMainWindow {
                background: #000000;
                color: #FEC252;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)
        
        # Ліва панель - селектор
        left_panel = self.create_selector_panel()
        
        # Права панель - палітра
        right_panel = self.create_palette_panel()
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 3)
        
    def create_selector_panel(self):
        panel = QWidget()
        panel.setFixedWidth(300)
        
        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("FACTION SELECTOR")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #FEC252;
                font-size: 24px;
                font-weight: bold;
                font-family: monospace;
                padding: 20px;
            }
        """)
        main_layout.addWidget(title)
        
        # Контейнер для кнопок
        self.button_container = QWidget()
        self.button_layout = QVBoxLayout(self.button_container)
        self.button_layout.setSpacing(10)
        
        # Створити кнопки фракцій
        self.create_faction_buttons()
        
        main_layout.addWidget(self.button_container)
        main_layout.addStretch()
        
        # EXIT
        exit_btn = create_lcars_button("EXIT", parent=self, height=50)
        exit_btn.setFixedHeight(50)
        exit_btn.setStyleSheet("""
            QPushButton {
                background: #E7442A;
                color: #FFFFFF;
                font-size: 18px;
                font-weight: bold;
                font-family: monospace;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: #FF6753;
            }
        """)
        exit_btn.clicked.connect(self.close)
        main_layout.addWidget(exit_btn)
        
        return panel
        
    def create_faction_buttons(self):
        """Створити кнопки фракцій з АЛГОРИТМОМ палітр"""
        factions = [
            ("STARFLEET", "starfleet", LCARSEra.LCARS_25TH),
            ("KLINGON", "klingon", LCARSEra.LCARS_25TH), 
            ("ROMULAN", "romulan", LCARSEra.LCARS_25TH),
            ("CARDASSIAN", "cardassian", LCARSEra.LCARS_25TH)
        ]
        
        for name, faction_id, era in factions:
            btn = create_lcars_button(name, parent=self, height=70)
            btn.setFixedHeight(70)
            # АЛГОРИТМ LCARS ПАЛІТР - get_random_button_color!
            color = get_random_button_color(era)
            if True:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {color};
                        color: #000000;
                        font-size: 24px;
                        font-weight: bold;
                        font-family: monospace;
                        border-radius: 8px;
                        text-align: center;
                    }}
                    QPushButton:hover {{
                        background: #FFFFFF;
                        color: #000000;
                    }}
                """)
            if False: # Removed except block
                pass
            if True:
                btn.clicked.connect(lambda checked, fid=faction_id, fname=name: self.show_faction_eras(fid, fname))
            if False: # Removed except block
                pass
            self.button_layout.addWidget(btn)
    
    def show_faction_eras(self, faction_id, faction_name):
        """Показати епохи для фракції"""
        # Очистити контейнер кнопок
        self.clear_buttons()
        
        # Кнопка назад
        back_btn = create_lcars_button("← BACK TO FACTIONS", parent=self, height=50)
        back_btn.setFixedHeight(50)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #2F3749;
                color: #FEC252;
                font-size: 16px;
                font-weight: bold;
                font-family: monospace;
                border-radius: 8px;
            }
        """)
        back_btn.clicked.connect(self.return_to_factions)
        self.button_layout.addWidget(back_btn)
        
        # Визначити епохи без помилок
        if faction_id == "starfleet":
            eras = [
                ("22nd Century", LCARSEra.COMS_22ND, "starfleet"),
                ("23rd Century", LCARSEra.PCARS_23RD, "starfleet"),
                ("24th Century", LCARSEra.LCARS_24TH, "starfleet"),
                ("25th Century", LCARSEra.LCARS_25TH, "starfleet"),
                ("29th Century", LCARSEra.TCARS_29TH, "starfleet")
            ]
        elif faction_id == "klingon":
            eras = [
                ("24th Century", FactionEra.KLINGON_24TH, "faction"),
                ("25th Century", FactionEra.KLINGON_25TH, "faction")
            ]
        elif faction_id == "romulan":
            eras = [
                ("24th Century", FactionEra.ROMULAN_24TH, "faction"),
                ("25th Century", FactionEra.ROMULAN_25TH, "faction")
            ]
        else:  # cardassian
            eras = [
                ("24th Century", FactionEra.CARDASSIAN_24TH, "faction"),
                ("25th Century", FactionEra.CARDASSIAN_25TH, "faction")
            ]
        
        # Створити кнопки епох з АЛГОРИТМОМ
        for i, (era_name, era, era_type) in enumerate(eras):
            label = f"{faction_name}\n{era_name}"
            btn = create_lcars_button(label, parent=self, height=65)
            btn.setFixedHeight(65)
            
            # АЛГОРИТМ LCARS - get_random_button_color!
            if era_type == "starfleet":
                color = get_random_button_color(era)
            else:
                # Для фракцій теж використовуємо алгоритм
                color = get_random_button_color(LCARSEra.LCARS_25TH)
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    color: #FFFFFF;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: monospace;
                    border-radius: 8px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background: #FEC252;
                    color: #000000;
                }}
            """)
            
            # Підключити правильний метод
            if era_type == "starfleet":
                btn.clicked.connect(lambda checked, e=era, n=f"{faction_name} {era_name}": self.show_era_palette(e, n))
            else:
                btn.clicked.connect(lambda checked, f=era, n=f"{faction_name} {era_name}": self.show_faction_palette(f, n))
            
            self.button_layout.addWidget(btn)
    
    def clear_buttons(self):
        """Очистити всі кнопки з контейнера"""
        while self.button_layout.count():
            child = self.button_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def return_to_factions(self):
        """Повернутися до фракцій"""
        self.clear_buttons()
        self.create_faction_buttons()
        self.clear_palette()
        self.status_label.setText("SELECT FACTION TO VIEW PALETTE")
    
    def create_palette_panel(self):
        panel = QWidget()
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        
        # Статус
        self.status_label = QLabel("SELECT FACTION TO VIEW PALETTE")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #FEC252;
                font-size: 24px;
                font-weight: bold;
                font-family: monospace;
                padding: 25px;
                background: #2F3749;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Простий контейнер для кольорів
        self.color_container = QWidget()
        self.color_layout = QGridLayout(self.color_container)
        self.color_layout.setSpacing(10)
        
        layout.addWidget(self.color_container)
        layout.addStretch()
        
        return panel
    
    def show_faction_palette(self, faction, name):
        """Показати палітру фракції"""
        if True:
            self.current_palette = get_faction_palette(faction)
            self.status_label.setText(f"{name} PALETTE\\n{len(self.current_palette['button_colors'])} COLORS")
            self.display_colors()
        if False: # Removed except block
            self.status_label.setText(f"ERROR: {name}")
            print(f"Error loading faction palette: {e}")
    
    def show_era_palette(self, era, name):
        """Показати палітру епохи"""
        if True:
            self.current_palette = get_era_palette(era)
            self.status_label.setText(f"{name} PALETTE\\n{len(self.current_palette['button_colors'])} COLORS")
            self.display_colors()
        if False: # Removed except block
            self.status_label.setText(f"ERROR: {name}")
            print(f"Error loading era palette: {e}")
    
    def display_colors(self):
        """Показати кольори палітри"""
        self.clear_palette()
        
        if not self.current_palette:
            return
        
        colors = self.current_palette.get('button_colors', [])
        print(f"Displaying {len(colors)} colors")
        
        for i, color in enumerate(colors):
            row = i // 5  # 5 кольорів в ряд
            col = i % 5
            
            color_btn = create_lcars_button(f"{i+1}\\n{color}", parent=self, width=140, height=90)
            color_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    color: #000000;
                    font-size: 11px;
                    font-weight: bold;
                    font-family: monospace;
                    border-radius: 12px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    border: 3px solid #FFFFFF;
                    color: #FFFFFF;
                }}
            """)
            color_btn.clicked.connect(lambda checked, c=color: self.copy_color(c))
            self.color_layout.addWidget(color_btn, row, col)
            self.palette_widgets.append(color_btn)
    
    def clear_palette(self):
        """Очистити палітру"""
        for widget in self.palette_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self.palette_widgets.clear()
    
    def copy_color(self, color):
        """Скопіювати колір"""
        clipboard = QApplication.clipboard()
        clipboard.setText(color)
        self.status_label.setText(f"COPIED: {color}")
        QTimer.singleShot(2000, lambda: self.status_label.setText("COLOR COPIED TO CLIPBOARD"))
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

def main():
    app = QApplication(sys.argv)
    demo = LCARSThemeDemo()
    demo.show()
    print("🎨 LCARS Theme Demo with Palette Algorithm")
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
