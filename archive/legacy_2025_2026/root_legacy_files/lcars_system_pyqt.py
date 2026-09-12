#!/usr/bin/env python3
"""
LCARS система на PyQt6 з використанням згенерованих компонентів
Повноцінний інтерфейс з клінгонськими, ромуланськими та кардасіанськими елементами
"""

import sys
from pathlib import Path

# Додаємо шлях до lcars модулів
sys.path.insert(0, str(Path(__file__).parent))

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QGridLayout, QLabel, QFrame, QPushButton, QGroupBox
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal
    from PyQt6.QtGui import QFont, QPalette, QColor
except ImportError:
    print("❌ PyQt6 не встановлено. Встановіть: pip install PyQt6")
    sys.exit(1)

# Імпортуємо згенеровані компоненти
try:
    from lcars.themes.theme import (
        KlingonTriangleButton, RomulanTrapezoidButton, 
        CardassianHexagonButton, FactionEra, get_faction_palette
    )
    print("✅ LCARS компоненти завантажено")
except ImportError as e:
    print(f"❌ Помилка імпорту LCARS компонентів: {e}")
    sys.exit(1)

class LcarsSystemWindow(QMainWindow):
    """Головне вікно LCARS системи"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 LCARS Battle Cruiser Interface")
        self.setGeometry(100, 100, 1200, 800)
        
        # Налаштування темного стилю
        self.setup_dark_style()
        
        # Створення головного віджету
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Створення інтерфейсу
        self.setup_ui(central_widget)
        
        # Налаштування таймера
        self.setup_timer()
        
        print("✅ LCARS система ініціалізована")
    
    def setup_dark_style(self):
        """Налаштування темного стилю"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QLabel {
                color: #40E0D0;
                font-weight: bold;
            }
            QGroupBox {
                color: #40E0D0;
                font-weight: bold;
                border: 2px solid #40E0D0;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def setup_ui(self, parent):
        """Створення інтерфейсу"""
        main_layout = QVBoxLayout(parent)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Головна панель заголовка
        self.create_header_panel(main_layout)
        
        # Основна область
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        
        # Ліва панель - Клінгонські системи
        self.create_klingon_panel(content_layout)
        
        # Центральна область - Головний дисплей
        self.create_main_display(content_layout)
        
        # Права панель - Ромуланські системи
        self.create_romulan_panel(content_layout)
        
        # Нижня панель - Кардасіанські системи
        self.create_cardassian_panel(main_layout)
    
    def create_header_panel(self, parent_layout):
        """Створення головної панелі"""
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #40E0D0;
                border-radius: 5px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Заголовок
        title_label = QLabel("🚀 LCARS BATTLE CRUISER INTERFACE")
        title_label.setStyleSheet("""
            QLabel {
                color: #40E0D0;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Статусні індикатори
        status_layout = QHBoxLayout()
        status_colors = ["#00FF00", "#00FF00", "#FFFF00", "#FF0000"]
        
        for color in status_colors:
            indicator = QLabel()
            indicator.setFixedSize(15, 15)
            indicator.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    border-radius: 7px;
                }}
            """)
            status_layout.addWidget(indicator)
        
        header_layout.addLayout(status_layout)
        parent_layout.addWidget(header_frame)
    
    def create_klingon_panel(self, parent_layout):
        """Створення клінгонської панелі"""
        klingon_group = QGroupBox("🔺 KLINGON SYSTEMS")
        klingon_group.setFixedWidth(300)
        klingon_group.setStyleSheet("""
            QGroupBox {
                color: #FFD700;
                border: 2px solid #660000;
                background-color: #1a0a0a;
            }
        """)
        
        klingon_layout = QVBoxLayout(klingon_group)
        
        # Клінгонські кнопки для різних ер
        eras = [
            (FactionEra.KLINGON_22ND, "22ND"),
            (FactionEra.KLINGON_23RD, "23RD"),
            (FactionEra.KLINGON_24TH, "24TH"),
            (FactionEra.KLINGON_25TH, "25TH")
        ]
        
        # Рядок з кнопками ер
        era_layout = QHBoxLayout()
        for era, text in eras:
            button = KlingonTriangleButton(text, "black_circle", era)
            button.setFixedSize(65, 40)
            era_layout.addWidget(button)
        
        klingon_layout.addLayout(era_layout)
        
        # Тактичні системи
        tactical_label = QLabel("TACTICAL SYSTEMS")
        tactical_label.setStyleSheet("color: #FF6600; font-size: 14px;")
        klingon_layout.addWidget(tactical_label)
        
        # Сітка тактичних кнопок
        tactical_grid = QGridLayout()
        tactical_colors = ["#980000", "#CA0000", "#D73713", "#E7730E", "#FFCB66", "#F6EE24"]
        
        for i, color in enumerate(tactical_colors):
            row, col = i // 3, i % 3
            button = KlingonTriangleButton("", "black_circle", FactionEra.KLINGON_24TH)
            button.setFixedSize(55, 30)
            # Міняємо колір кнопки
            palette = get_faction_palette(FactionEra.KLINGON_24TH)
            button.main_color = color
            tactical_grid.addWidget(button, row, col)
        
        klingon_layout.addLayout(tactical_grid)
        
        # Системний статус
        self.create_status_panel(klingon_layout, "SYSTEM STATUS", "#40E0D0")
        
        klingon_layout.addStretch()
        parent_layout.addWidget(klingon_group)
    
    def create_main_display(self, parent_layout):
        """Створення головного дисплея"""
        main_group = QGroupBox("MAIN DISPLAY - TACTICAL VIEW")
        main_group.setStyleSheet("""
            QGroupBox {
                color: #40E0D0;
                border: 2px solid #40E0D0;
                background-color: #0a1a1a;
            }
        """)
        
        main_layout = QVBoxLayout(main_group)
        
        # Радарний дисплей
        radar_frame = QFrame()
        radar_frame.setFixedHeight(200)
        radar_frame.setStyleSheet("""
            QFrame {
                background-color: #001122;
                border: 2px solid #00FF99;
                border-radius: 5px;
            }
        """)
        
        radar_layout = QVBoxLayout(radar_frame)
        radar_layout.addStretch()
        
        # Імітація радара
        radar_label = QLabel("🎯 RADAR DISPLAY")
        radar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        radar_label.setStyleSheet("""
            QLabel {
                color: #00FF99;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        radar_layout.addWidget(radar_label)
        
        # Цільові маркери
        targets_label = QLabel("🔴 TARGETS: 3 ACTIVE")
        targets_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        targets_label.setStyleSheet("""
            QLabel {
                color: #FF0000;
                font-size: 12px;
            }
        """)
        radar_layout.addWidget(targets_label)
        
        radar_layout.addStretch()
        main_layout.addWidget(radar_frame)
        
        # Панель інформації
        info_frame = QFrame()
        info_frame.setFixedHeight(120)
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #FFD700;
                border-radius: 5px;
            }
        """)
        
        info_layout = QGridLayout(info_frame)
        
        # Системні параметри
        systems = [
            ("SHIELDS", "100%", "#00FF00"),
            ("WEAPONS", "READY", "#00FF00"),
            ("ENGINES", "95%", "#FFFF00"),
            ("HULL", "87%", "#FFFF00")
        ]
        
        for i, (name, value, color) in enumerate(systems):
            row, col = i // 2, i % 2
            
            # Назва системи
            name_label = QLabel(name)
            name_label.setStyleSheet(f"color: #40E0D0; font-size: 12px; font-weight: bold;")
            info_layout.addWidget(name_label, row * 2, col)
            
            # Значення
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
            info_layout.addWidget(value_label, row * 2 + 1, col)
        
        main_layout.addWidget(info_frame)
        main_layout.addStretch()
        
        parent_layout.addWidget(main_group)
    
    def create_romulan_panel(self, parent_layout):
        """Створення ромуланської панелі"""
        romulan_group = QGroupBox("🔻 ROMULAN SYSTEMS")
        romulan_group.setFixedWidth(250)
        romulan_group.setStyleSheet("""
            QGroupBox {
                color: #00FF99;
                border: 2px solid #00FF99;
                background-color: #0a1a1a;
            }
        """)
        
        romulan_layout = QVBoxLayout(romulan_group)
        
        # Ромуланські кнопки
        romulan_colors = ["#006666", "#00FF99", "#1C7736", "#99CC99"]
        
        for i, color in enumerate(romulan_colors):
            button = RomulanTrapezoidButton(f"ROM{i+1}", FactionEra.ROMULAN_24TH)
            button.setFixedSize(200, 30)
            # Міняємо колір
            button.main_color = color
            romulan_layout.addWidget(button)
        
        # Кардасіанські системи
        cardassian_label = QLabel("🔶 CARDASSIAN SYSTEMS")
        cardassian_label.setStyleSheet("color: #FFD700; font-size: 14px;")
        romulan_layout.addWidget(cardassian_label)
        
        # Кардасіанські кнопки
        cardassian_colors = ["#CC3300", "#FF4400", "#FF6600", "#FF9900"]
        
        for color in cardassian_colors:
            button = CardassianHexagonButton("", FactionEra.CARDASSIAN_24TH)
            button.setFixedSize(200, 25)
            button.main_color = color
            romulan_layout.addWidget(button)
        
        # Комунікаційна панель
        self.create_status_panel(romulan_layout, "COMMUNICATIONS", "#40E0D0")
        
        romulan_layout.addStretch()
        parent_layout.addWidget(romulan_group)
    
    def create_cardassian_panel(self, parent_layout):
        """Створення кардасіанської панелі"""
        cardassian_frame = QFrame()
        cardassian_frame.setFixedHeight(120)
        cardassian_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #FFD700;
                border-radius: 5px;
            }
        """)
        
        cardassian_layout = QHBoxLayout(cardassian_frame)
        cardassian_layout.setContentsMargins(15, 10, 15, 10)
        
        # Лівий блок - статус
        status_group = QGroupBox("SYSTEM STATUS")
        status_group.setFixedWidth(200)
        status_group.setStyleSheet("""
            QGroupBox {
                color: #FFD700;
                border: 1px solid #FFD700;
                background-color: transparent;
                font-size: 12px;
            }
        """)
        
        status_layout = QVBoxLayout(status_group)
        
        status_items = [
            ("ONLINE", "#00FF00"),
            ("WARNING", "#FFFF00"),
            ("CRITICAL", "#FF0000")
        ]
        
        for text, color in status_items:
            item_layout = QHBoxLayout()
            
            indicator = QLabel()
            indicator.setFixedSize(12, 12)
            indicator.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    border-radius: 6px;
                }}
            """)
            item_layout.addWidget(indicator)
            
            label = QLabel(text)
            label.setStyleSheet(f"color: {color}; font-size: 10px;")
            item_layout.addWidget(label)
            
            status_layout.addLayout(item_layout)
        
        cardassian_layout.addWidget(status_group)
        
        # Центральний блок - контрольні панелі
        control_group = QGroupBox("MAIN CONTROL PANELS")
        control_group.setStyleSheet("""
            QGroupBox {
                color: #40E0D0;
                border: 1px solid #40E0D0;
                background-color: transparent;
                font-size: 12px;
            }
        """)
        
        control_layout = QVBoxLayout(control_group)
        
        # Рядок контрольних кнопок
        control_row = QHBoxLayout()
        control_colors = ["#1a1a1a", "#2d1b1b", "#1b2d1b", "#2d2d1b"]
        control_borders = ["#40E0D0", "#CC0000", "#00FF99", "#FFD700"]
        
        for color, border in zip(control_colors, control_borders):
            button = QPushButton()
            button.setFixedSize(80, 40)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 2px solid {border};
                    border-radius: 5px;
                    color: white;
                    font-weight: bold;
                }}
            """)
            control_row.addWidget(button)
        
        control_layout.addLayout(control_row)
        cardassian_layout.addWidget(control_group)
        
        # Правий блок - час
        time_group = QGroupBox("STARDATE")
        time_group.setFixedWidth(150)
        time_group.setStyleSheet("""
            QGroupBox {
                color: #FFD700;
                border: 1px solid #FFD700;
                background-color: transparent;
                font-size: 12px;
            }
        """)
        
        time_layout = QVBoxLayout(time_group)
        
        stardate_label = QLabel("58432.7")
        stardate_label.setStyleSheet("""
            QLabel {
                color: #40E0D0;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        time_layout.addWidget(stardate_label)
        
        time_label = QLabel("TIME: 23:47:12")
        time_label.setStyleSheet("""
            QLabel {
                color: #00FF99;
                font-size: 12px;
            }
        """)
        time_layout.addWidget(time_label)
        
        cardassian_layout.addWidget(time_group)
        
        parent_layout.addWidget(cardassian_frame)
    
    def create_status_panel(self, parent_layout, title, color):
        """Створення панелі статусу"""
        status_frame = QFrame()
        status_frame.setFixedHeight(80)
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #2a1a1a;
                border: 1px solid {color};
                border-radius: 5px;
            }}
        """)
        
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")
        status_layout.addWidget(title_label)
        
        # Статусні індикатори
        for i in range(4):
            progress_frame = QFrame()
            progress_frame.setFixedHeight(3)
            progress_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: #{"00FF00" if i < 2 else "FFFF00" if i == 2 else "FF6600"};
                    border-radius: 1px;
                }}
            """)
            progress_frame.setMaximumWidth(100 - i * 10)
            status_layout.addWidget(progress_frame)
        
        parent_layout.addWidget(status_frame)
    
    def setup_timer(self):
        """Налаштування таймера для оновлення"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
    
    def update_time(self):
        """Оновлення часу"""
        # Тут можна додати логіку оновлення часу
        pass

def main():
    """Головна функція"""
    print("🚀 LCARS SYSTEM DEMONSTRATION")
    print("=" * 50)
    
    # Перевірка наявності компонентів
    try:
        from lcars.themes.theme import KlingonTriangleButton
        print("✅ LCARS компоненти доступні")
    except ImportError:
        print("❌ LCARS компоненти не знайдені")
        print("💡 Переконайтеся що theme.py існує")
        return
    
    print("\n🎯 Система містить:")
    print("   🔺 Клінгонські тактичні системи")
    print("   🔻 Ромуланські контрольні панелі")
    print("   🔶 Кардасіанські монітори")
    print("   📋 Головний тактичний дисплей")
    print("   🎯 Радарний дисплей")
    print("   ⏰ Системний таймер")
    
    print("\n🚀 Запуск LCARS системи...")
    print("💡 Для виходу закрийте вікно")
    
    app = QApplication(sys.argv)
    
    # Створення головного вікна
    window = LcarsSystemWindow()
    window.show()
    
    # Запуск додатку
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
