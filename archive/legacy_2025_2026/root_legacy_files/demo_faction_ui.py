#!/usr/bin/env python3
"""
Демо фракційних LCARS інтерфейсів
Показує як виглядають кнопки та панелі різних фракцій
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                            QHBoxLayout, QWidget, QLabel, QTabWidget)
from PyQt6.QtCore import Qt

# Імпортуємо фракційні елементи
from lcars.themes.theme import (
    FactionLCARSInterface,
    KlingonLCARSButton,
    RomulanLCARSButton, 
    CardassianLCARSButton,
    KlingonLCARSPanel,
    RomulanLCARSPanel,
    CardassianLCARSPanel
)

class FactionDemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 LCARS Фракційні Інтерфейси Демо")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Головний layout
        main_layout = QVBoxLayout(central_widget)
        
        # Заголовок
        title = QLabel("⭐ STAR TREK LCARS ФРАКЦІЙНІ ІНТЕРФЕЙСИ ⭐")
        title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background-color: #000000;
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                text-align: center;
                border: 2px solid #217AFF;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Таби для різних фракцій
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #217AFF;
                background-color: #000000;
            }
            QTabBar::tab {
                background-color: #217AFF;
                color: #FFFFFF;
                padding: 8px 16px;
                font-weight: bold;
                border: 1px solid #FFFFFF;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #000000;
            }
        """)
        
        # Додаємо таби для кожної фракції
        tabs.addTab(self.create_klingon_demo(), "🔺 KLINGON")
        tabs.addTab(self.create_romulan_demo(), "🔻 ROMULAN") 
        tabs.addTab(self.create_cardassian_demo(), "🟠 CARDASSIAN")
        tabs.addTab(self.create_comparison_demo(), "⚖️ ПОРІВНЯННЯ")
        
        main_layout.addWidget(tabs)
        
        # Налаштування стилю вікна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
        """)
    
    def create_klingon_demo(self):
        """Створити демо Клінгонського інтерфейсу"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Заголовок
        title = QLabel("🔺 КЛІНГОНСЬКА ІМПЕРІЯ 🔺")
        title.setStyleSheet("""
            QLabel {
                color: #FF0000;
                background-color: #000000;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                text-align: center;
                border: 2px solid #CC0000;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Повний інтерфейс
        klingon_interface = FactionLCARSInterface("klingon", "24th")
        layout.addWidget(klingon_interface)
        
        # Окремі кнопки
        buttons_label = QLabel("Окремі елементи:")
        buttons_label.setStyleSheet("color: #FFFFFF; font-size: 16px; padding: 10px;")
        layout.addWidget(buttons_label)
        
        button_layout = QHBoxLayout()
        buttons = [
            KlingonLCARSButton("КОМАНДА"),
            KlingonLCARSButton("ЗБРОЯ"),
            KlingonLCARSButton("ЩИТИ"),
            KlingonLCARSButton("ЕНЕРГІЯ")
        ]
        
        for button in buttons:
            button_layout.addWidget(button)
        
        layout.addLayout(button_layout)
        
        # Панель
        panel = KlingonLCARSPanel()
        panel.setMinimumHeight(100)
        layout.addWidget(panel)
        
        return widget
    
    def create_romulan_demo(self):
        """Створити демо Ромуланського інтерфейсу"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Заголовок
        title = QLabel("🔻 РОМУЛАНСЬКА ЗВЕЗДНА ІМПЕРІЯ 🔻")
        title.setStyleSheet("""
            QLabel {
                color: #00FF99;
                background-color: #000000;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                text-align: center;
                border: 2px solid #006644;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Повний інтерфейс
        romulan_interface = FactionLCARSInterface("romulan", "24th")
        layout.addWidget(romulan_interface)
        
        # Окремі кнопки
        buttons_label = QLabel("Окремі елементи:")
        buttons_label.setStyleSheet("color: #00FF99; font-size: 16px; padding: 10px;")
        layout.addWidget(buttons_label)
        
        button_layout = QHBoxLayout()
        buttons = [
            RomulanLCARSButton("ТАЛ ШИАР"),
            RomulanLCARSButton("ПЛАЗМА"),
            RomulanLCARSButton("МАСКИРОВКА"),
            RomulanLCARSButton("ТЕЛЕПОРТ")
        ]
        
        for button in buttons:
            button_layout.addWidget(button)
        
        layout.addLayout(button_layout)
        
        # Панель
        panel = RomulanLCARSPanel()
        panel.setMinimumHeight(100)
        layout.addWidget(panel)
        
        return widget
    
    def create_cardassian_demo(self):
        """Створити демо Кардасіанського інтерфейсу"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Заголовок
        title = QLabel("🟠 КАРДАСІАНСЬКА СПІЛКА 🟠")
        title.setStyleSheet("""
            QLabel {
                color: #FF6600;
                background-color: #000000;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                text-align: center;
                border: 2px solid #CC3300;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Повний інтерфейс
        cardassian_interface = FactionLCARSInterface("cardassian", "24th")
        layout.addWidget(cardassian_interface)
        
        # Окремі кнопки
        buttons_label = QLabel("Окремі елементи:")
        buttons_label.setStyleSheet("color: #FF6600; font-size: 16px; padding: 10px;")
        layout.addWidget(buttons_label)
        
        button_layout = QHBoxLayout()
        buttons = [
            CardassianLCARSButton("ОБСЛУГА"),
            CardassianLCARSButton("БАЗА"),
            CardassianLCARSButton("СИСТЕМА"),
            CardassianLCARSButton("КОНТРОЛЬ")
        ]
        
        for button in buttons:
            button_layout.addWidget(button)
        
        layout.addLayout(button_layout)
        
        # Панель
        panel = CardassianLCARSPanel()
        panel.setMinimumHeight(100)
        layout.addWidget(panel)
        
        return widget
    
    def create_comparison_demo(self):
        """Створити демо порівняння всіх фракцій"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Заголовок
        title = QLabel("⚖️ ПОРІВНЯННЯ ФРАКЦІЙ ⚖️")
        title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background-color: #000000;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                text-align: center;
                border: 2px solid #217AFF;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Порівняння кнопок
        comparison_label = QLabel("Порівняння стилів кнопок:")
        comparison_label.setStyleSheet("color: #FFFFFF; font-size: 16px; padding: 10px;")
        layout.addWidget(comparison_label)
        
        # Klingon кнопки
        klingon_group = QWidget()
        klingon_layout = QVBoxLayout(klingon_group)
        klingon_title = QLabel("🔺 KLINGON - Червоні трикутні")
        klingon_title.setStyleSheet("color: #FF0000; font-weight: bold;")
        klingon_layout.addWidget(klingon_title)
        
        klingon_buttons = QHBoxLayout()
        klingon_buttons.addWidget(KlingonLCARSButton("КОМАНДА"))
        klingon_buttons.addWidget(KlingonLCARSButton("ЗБРОЯ"))
        klingon_layout.addLayout(klingon_buttons)
        layout.addWidget(klingon_group)
        
        # Romulan кнопки
        romulan_group = QWidget()
        romulan_layout = QVBoxLayout(romulan_group)
        romulan_title = QLabel("🔻 ROMULAN - Зелені трапеції")
        romulan_title.setStyleSheet("color: #00FF99; font-weight: bold;")
        romulan_layout.addWidget(romulan_title)
        
        romulan_buttons = QHBoxLayout()
        romulan_buttons.addWidget(RomulanLCARSButton("ТАЛ ШИАР"))
        romulan_buttons.addWidget(RomulanLCARSButton("ПЛАЗМА"))
        romulan_layout.addLayout(romulan_buttons)
        layout.addWidget(romulan_group)
        
        # Cardassian кнопки
        cardassian_group = QWidget()
        cardassian_layout = QVBoxLayout(cardassian_group)
        cardassian_title = QLabel("🟠 CARDASSIAN - Помаранчеві шестикутники")
        cardassian_title.setStyleSheet("color: #FF6600; font-weight: bold;")
        cardassian_layout.addWidget(cardassian_title)
        
        cardassian_buttons = QHBoxLayout()
        cardassian_buttons.addWidget(CardassianLCARSButton("ОБСЛУГА"))
        cardassian_buttons.addWidget(CardassianLCARSButton("БАЗА"))
        cardassian_layout.addLayout(cardassian_buttons)
        layout.addWidget(cardassian_group)
        
        # Порівняння панелей
        panels_label = QLabel("Порівняння панелей:")
        panels_label.setStyleSheet("color: #FFFFFF; font-size: 16px; padding: 10px;")
        layout.addWidget(panels_label)
        
        panels_layout = QHBoxLayout()
        panels_layout.addWidget(KlingonLCARSPanel())
        panels_layout.addWidget(RomulanLCARSPanel())
        panels_layout.addWidget(CardassianLCARSPanel())
        layout.addLayout(panels_layout)
        
        return widget

def main():
    app = QApplication(sys.argv)
    
    # Встановлюємо темну тему
    app.setStyleSheet("""
        QApplication {
            background-color: #000000;
            color: #FFFFFF;
        }
    """)
    
    window = FactionDemoWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
