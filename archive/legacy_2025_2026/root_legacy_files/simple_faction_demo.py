#!/usr/bin/env python3
"""
Просте демо фракційних LCARS інтерфейсів
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                            QHBoxLayout, QWidget, QLabel, QPushButton)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPolygon, QColor, QBrush, QPen

# Імпортуємо палітри та готові компоненти
try:
    from lcars.themes.theme import (
        FactionEra,
        get_faction_palette,
        KlingonTriangleButton,
        RomulanTrapezoidButton,
        RomulanTrapezoidButton2,
        CardassianHexagonButton,
        QMLKlingonButton
    )
    print("✅ Імпорт компонентів успішний!")
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    sys.exit(1)

class SimpleFactionDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Фракційні LCARS Інтерфейси")
        self.setGeometry(100, 100, 1000, 800)
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Головний layout
        main_layout = QVBoxLayout(central_widget)
        
        # Заголовок
        title = QLabel("⭐ ФРАКЦІЙНІ LCARS ІНТЕРФЕЙСИ ⭐")
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
        
        # Панель управління епохами
        control_panel = QWidget()
        control_panel.setStyleSheet("""
            QWidget {
                background-color: #111111;
                border: 1px solid #333333;
                padding: 10px;
            }
        """)
        control_layout = QHBoxLayout(control_panel)
        
        # Вибір фракції
        faction_label = QLabel("Фракція:")
        faction_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        control_layout.addWidget(faction_label)
        
        self.faction_combo = QPushButton("Klingon")
        self.faction_combo.setStyleSheet("""
            QPushButton {
                background-color: #CC0000;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                padding: 5px 15px;
                font-weight: bold;
            }
        """)
        self.faction_combo.clicked.connect(self.switch_faction)
        control_layout.addWidget(self.faction_combo)
        
        # Вибір епохи
        era_label = QLabel("Епоха:")
        era_label.setStyleSheet("color: #FFFFFF; font-weight: bold; margin-left: 20px;")
        control_layout.addWidget(era_label)
        
        self.era_combo = QPushButton("24th")
        self.era_combo.setStyleSheet("""
            QPushButton {
                background-color: #217AFF;
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
                padding: 5px 15px;
                font-weight: bold;
            }
        """)
        self.era_combo.clicked.connect(self.switch_era)
        control_layout.addWidget(self.era_combo)
        
        # Інформація про палітру
        self.palette_info = QLabel("Палітра: klingon_24th")
        self.palette_info.setStyleSheet("color: #00FF00; font-weight: bold; margin-left: 20px;")
        control_layout.addWidget(self.palette_info)
        
        control_layout.addStretch()
        main_layout.addWidget(control_panel)
        
        # Контейнер для фракційних інтерфейсів
        self.faction_container = QWidget()
        self.faction_layout = QVBoxLayout(self.faction_container)
        main_layout.addWidget(self.faction_container)
        
        # Поточні налаштування
        self.current_faction = "klingon"
        self.current_era = "24th"
        
        # Встановлюємо поточну еру фракції
        faction_era_key = f"{self.current_faction}_{self.current_era}"
        for era in FactionEra:
            if era.value == faction_era_key:
                self.current_faction_era = era
                break
        else:
            self.current_faction_era = FactionEra.KLINGON_24TH
        
        # Створюємо початковий інтерфейс
        self.update_faction_interface()
        
        # Налаштування стилю вікна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
        """)
    
    def switch_faction(self):
        """Переключити фракцію"""
        factions = ["klingon", "romulan", "cardassian"]
        current_index = factions.index(self.current_faction)
        next_index = (current_index + 1) % len(factions)
        self.current_faction = factions[next_index]
        
        # Оновлюємо кнопку
        faction_colors = {
            "klingon": "#CC0000",
            "romulan": "#006644", 
            "cardassian": "#CC3300"
        }
        self.faction_combo.setText(self.current_faction.upper())
        self.faction_combo.setStyleSheet(f"""
            QPushButton {{
                background-color: {faction_colors[self.current_faction]};
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
                padding: 5px 15px;
                font-weight: bold;
            }}
        """)
        
        self.update_faction_interface()
    
    def switch_era(self):
        """Переключити епоху"""
        eras = ["22nd", "23rd", "24th", "25th", "29th"]
        current_index = eras.index(self.current_era)
        next_index = (current_index + 1) % len(eras)
        self.current_era = eras[next_index]
        
        self.era_combo.setText(self.current_era)
        self.update_faction_interface()
    
    def update_faction_interface(self):
        """Оновити інтерфейс фракції"""
        # Очищуємо старий контейнер
        for i in reversed(range(self.faction_layout.count())):
            child = self.faction_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Отримуємо палітру
        faction_era_key = f"{self.current_faction}_{self.current_era}"
        palette = None
        
        for era in FactionEra:
            if era.value == faction_era_key:
                palette = get_faction_palette(era)
                break
        
        if not palette:
            palette = get_faction_palette(FactionEra.KLINGON_24TH)
        
        # Оновлюємо інформацію
        self.palette_info.setText(f"Палітра: {faction_era_key}")
        
        # Встановлюємо поточну еру фракції
        for era in FactionEra:
            if era.value == faction_era_key:
                self.current_faction_era = era
                break
        else:
            # Якщо не знайдено, використовуємо базову
            if self.current_faction == "klingon":
                self.current_faction_era = FactionEra.KLINGON_24TH
            elif self.current_faction == "romulan":
                self.current_faction_era = FactionEra.ROMULAN_24TH
            elif self.current_faction == "cardassian":
                self.current_faction_era = FactionEra.CARDASSIAN_24TH
        
        # Створюємо фракційний інтерфейс
        if self.current_faction == "klingon":
            self.create_klingon_interface(palette)
        elif self.current_faction == "romulan":
            self.create_romulan_interface(palette)
        elif self.current_faction == "cardassian":
            self.create_cardassian_interface(palette)
    
    def create_klingon_interface(self, palette):
        """Створити клінгонський інтерфейс"""
        # Заголовок
        header = QLabel(f"🔺 KLINGON {self.current_era.upper()}")
        header.setStyleSheet(f"""
            QLabel {{
                color: #FF0000;
                background-color: {palette.get('panel_color', '#000000')};
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                border: 2px solid {palette.get('panel_border', '#CC0000')};
            }}
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.faction_layout.addWidget(header)
        
        # Панель з кнопками
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {palette.get('panel_color', '#000000')};
                border: 2px solid {palette.get('panel_border', '#CC0000')};
                border-radius: 0px;
            }}
        """)
        panel.setMinimumHeight(80)
        button_layout = QHBoxLayout(panel)
        
        # Кнопки з палітри
        button_colors = palette.get('button_colors', ['#CC0000', '#FF0000', '#990000'])
        button_texts = ["КОМАНДА", "ЗБРОЯ", "ЩИТИ", "ЕНЕРГІЯ", "ЩИТИ", "СЕНСОРИ", "ТЕЛЕПОРТ"]
        
        for i, text in enumerate(button_texts[:7]):  # Беремо перші 7 кнопок
            color = button_colors[i % len(button_colors)]
            # Використовуємо тільки QPushButton кнопки
            button = KlingonTriangleButton("", "black_circle", self.current_faction_era)  # Порожній текст
            button_layout.addWidget(button)
        
        self.faction_layout.addWidget(panel)
        
        # Додаткові елементи
        self.create_palette_info(palette)
    
    def create_romulan_interface(self, palette):
        """Створити ромуланський інтерфейс"""
        # Заголовок
        header = QLabel(f"🔻 ROMULAN {self.current_era.upper()}")
        header.setStyleSheet(f"""
            QLabel {{
                color: #00FF99;
                background-color: {palette.get('panel_color', '#000000')};
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                border: 2px solid {palette.get('panel_border', '#006644')};
            }}
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.faction_layout.addWidget(header)
        
        # Панель з кнопками
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {palette.get('panel_color', '#000000')};
                border: 2px solid {palette.get('panel_border', '#006644')};
                border-radius: 0px;
            }}
        """)
        panel.setMinimumHeight(80)
        button_layout = QHBoxLayout(panel)
        
        # Кнопки з палітри
        button_colors = palette.get('button_colors', ['#006644', '#008866', '#004433'])
        button_texts = ["ТАЛ ШИАР", "ПЛАЗМА", "МАСКИРОВКА", "ТЕЛЕПОРТ", "СЕНСОРИ", "ЩИТИ", "ВЕКТОР"]
        
        for i, text in enumerate(button_texts[:7]):
            color = button_colors[i % len(button_colors)]
            if i % 2 == 0:
                button = RomulanTrapezoidButton("", self.current_faction_era)  # Порожній текст
            else:
                button = RomulanTrapezoidButton2("", self.current_faction_era)  # Порожній текст
            button_layout.addWidget(button)
        
        self.faction_layout.addWidget(panel)
        self.create_palette_info(palette)
    
    def create_cardassian_interface(self, palette):
        """Створити кардасіанський інтерфейс"""
        # Заголовок
        header = QLabel(f"🟠 CARDASSIAN {self.current_era.upper()}")
        header.setStyleSheet(f"""
            QLabel {{
                color: #FF6600;
                background-color: {palette.get('panel_color', '#000000')};
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                border: 2px solid {palette.get('panel_border', '#CC3300')};
            }}
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.faction_layout.addWidget(header)
        
        # Панель з кнопками
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {palette.get('panel_color', '#000000')};
                border: 2px solid {palette.get('panel_border', '#CC3300')};
                border-radius: 0px;
            }}
        """)
        panel.setMinimumHeight(80)
        button_layout = QHBoxLayout(panel)
        
        # Кнопки з палітри
        button_colors = palette.get('button_colors', ['#CC3300', '#FF4400', '#FF6600'])
        button_texts = ["ОБСЛУГА", "БАЗА", "СИСТЕМА", "КОНТРОЛЬ", "ОРДЕР", "ГАЛА", "СУД"]
        
        for i, text in enumerate(button_texts[:7]):
            color = button_colors[i % len(button_colors)]
            button = CardassianHexagonButton("", self.current_faction_era)  # Порожній текст
            button_layout.addWidget(button)
        
        self.faction_layout.addWidget(panel)
        self.create_palette_info(palette)
    
    def create_palette_info(self, palette):
        """Створити інформацію про палітру"""
        info_widget = QWidget()
        info_widget.setStyleSheet("""
            QWidget {
                background-color: #111111;
                border: 1px solid #333333;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_widget)
        
        # Заголовок інформації
        info_title = QLabel("📊 ІНФОРМАЦІЯ ПРО ПАЛІТРУ")
        info_title.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 16px;")
        info_layout.addWidget(info_title)
        
        # Кольори кнопок
        colors_text = "Кольори кнопок: " + ", ".join(palette.get('button_colors', [])[:8])
        colors_label = QLabel(colors_text)
        colors_label.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        colors_label.setWordWrap(True)
        info_layout.addWidget(colors_label)
        
        # Кольори тривоги
        alerts_text = "Кольори тривоги: " + ", ".join(palette.get('alert_colors', []))
        alerts_label = QLabel(alerts_text)
        alerts_label.setStyleSheet("color: #FF6666; font-size: 12px;")
        alerts_label.setWordWrap(True)
        info_layout.addWidget(alerts_label)
        
        # Колір панелі
        panel_color_text = f"Колір панелі: {palette.get('panel_color', '#000000')}"
        panel_color_label = QLabel(panel_color_text)
        panel_color_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
        info_layout.addWidget(panel_color_label)
        
        # Колір межі
        border_color_text = f"Колір межі: {palette.get('panel_border', '#666666')}"
        border_color_label = QLabel(border_color_text)
        border_color_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
        info_layout.addWidget(border_color_label)
        
        self.faction_layout.addWidget(info_widget)

def main():
    app = QApplication(sys.argv)
    
    # Встановлюємо темну тему
    app.setStyleSheet("""
        QApplication {
            background-color: #000000;
            color: #FFFFFF;
        }
    """)
    
    window = SimpleFactionDemo()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
