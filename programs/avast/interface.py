# AVAST LCARS EDITION - ПОВНОФУНКЦІОНАЛЬНИЙ ІНТЕРФЕЙС
# ПРОГРАМА: AVAST-SECURITY-EX (24-25 ст.)
# ОПИС: Спеціалізований антивірусний комплекс для екосистеми LCARS.
# ПРАВИЛО: БЕЗ ТРАЙ-ЕКСЕПТ. БЕЗ ТРИ-ЛАПОК. ПОЯСНЕННЯ УКРАЇНСЬКОЮ.

import sys
import os
from pathlib import Path

# ПЕРЕВІРКА ШЛЯХІВ (Bootstrapping):
# Додаємо кореневу папку проекту до системних шляхів для правильного імпорту модулів.
root = Path(__file__).resolve().parents[2]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QLabel, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QThread

# ІМПОРТ КОМПОНЕНТІВ LCARS:
from lcars.base.interface import LCARSButton, DataBlock
from lcars.themes.palette import LCARSEra, get_theme, get_lcars_font_style
from lcars.base.interface import LCARSProgramPanel

# ІМПОРТ ФУНКЦІОНАЛЬНОГО РУШІЯ AVAST:
from programs.avast.shield import AvastShield

# КЛАС: AvastSecuritySuite
# Головне вікно програми Avast. Керує навігацією та підключенням до рушія захисту.
class AvastSecuritySuite(LCARSProgramPanel):
    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        # Ініціалізація базової панелі LCARS з акцентним кольором Avast (Orange).
        super().__init__(
            title="AVAST SECURITY // TITAN EDITION",
            era=era,
            faction=faction,
            accent_color="#FF8800",
            parent=parent
        )
        
        # Створення екземпляра рушія захисту
        self.shield_engine = AvastShield()
        
        # Підключення сигналів рушія до методів інтерфейсу
        self.shield_engine.scan_progress.connect(self.on_scan_progress)
        self.shield_engine.scan_completed.connect(self.on_scan_finish)

    # МЕТОД: build_ui
    # Побудова структури інтерфейсу: бокова панель та зона контенту.
    def build_ui(self, layout: QVBoxLayout):
        main_h = QHBoxLayout()
        main_h.setContentsMargins(0, 0, 0, 0)
        main_h.setSpacing(0)

        # --- БОКОВА ПАНЕЛЬ (Avast Sidebar) ---
        # Містить логотип та основні розділи навігації.
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"background-color: #050A05; border-right: 2px solid #50BB00;")
        
        s_lay = QVBoxLayout(sidebar)
        s_lay.setContentsMargins(10, 20, 10, 20)
        s_lay.setSpacing(10)
        
        # ЛОГОТИП (Брендування)
        logo = QLabel("◢ AVAST\nLCARS")
        logo.setStyleSheet(f"color: #50BB00; {get_lcars_font_style(20, 'bold')};")
        s_lay.addWidget(logo)
        
        s_lay.addSpacing(30)
        
        # КНОПКИ НАВІГАЦІЇ
        self.nav_btns = []
        nav_data = [
            ("STATUS", 0, "#50BB00"),     # Стан системи
            ("PROTECTION", 1, "#FF8800"), # Активні екрани
            ("PRIVACY", 2, "#00AADD"),    # Приватність
            ("PERFORMANCE", 3, "#AAFF00") # Продуктивність
        ]
        
        for text, idx, color in nav_data:
            btn = LCARSButton(text, color, shape="left")
            btn.setMinimumHeight(45)
            btn.clicked.connect(lambda ch, i=idx: self.set_view(i))
            s_lay.addWidget(btn)
            self.nav_btns.append(btn)
            
        s_lay.addStretch()
        main_h.addWidget(sidebar)

        # --- СТЕК ВІКОН (Content Area) ---
        self.stack = QStackedWidget()
        
        # 0. ГОЛОВНИЙ ЕКРАН (Smart Scan)
        self.status_view = self._build_status_view()
        self.stack.addWidget(self.status_view)
        
        # Плейсхолдери для інших розділів
        self.stack.addWidget(QLabel("◤ PROTECTION MODE // ACTIVE SHIELDS"))
        self.stack.addWidget(QLabel("◤ PRIVACY MODE // DATA ENCRYPTION"))
        self.stack.addWidget(QLabel("◤ PERFORMANCE MODE // CLEANUP"))
        
        main_h.addWidget(self.stack, 1)
        layout.addLayout(main_h)
        self.set_view(0)

    # МЕТОД: _build_status_view
    # Створення головного екрану зі значком щита та кнопкою сканування.
    def _build_status_view(self):
        view = QWidget()
        v_lay = QVBoxLayout(view)
        v_lay.setContentsMargins(60, 40, 60, 40)
        v_lay.setSpacing(30)
        
        # ЦЕНТРАЛЬНИЙ ЩИТ (Іконка стану)
        self.shield_icon = QLabel("🛡️")
        self.shield_icon.setStyleSheet("font-size: 80px; color: #50BB00;")
        v_lay.addWidget(self.shield_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # ГОРЯЧЕ ПОВІДОМЛЕННЯ
        self.main_msg = QLabel("SYSTEM STATE: SECURE")
        self.main_msg.setStyleSheet(f"color: white; {get_lcars_font_style(24, 'bold')}")
        v_lay.addWidget(self.main_msg, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # КНОПКА SMART SCAN (Запуск процесу)
        self.scan_btn = LCARSButton("SMART SCAN", "#50BB00", shape="pill")
        self.scan_btn.setMinimumSize(220, 220)
        self.scan_btn.clicked.connect(self.start_smart_scan)
        v_lay.addWidget(self.scan_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # ПРОГРЕС-БАР СКАНУВАННЯ
        self.scan_bar = QProgressBar()
        self.scan_bar.setFixedHeight(20)
        self.scan_bar.hide()
        self.scan_bar.setStyleSheet("""
            QProgressBar { background: #111; border: 1px solid #50BB00; color: white; text-align: center; }
            QProgressBar::chunk { background: #50BB00; }
        """)
        v_lay.addWidget(self.scan_bar)

        # ТЕКСТ ПОТОЧНОГО ОБ'ЄКТА
        self.scan_item_lbl = QLabel("")
        self.scan_item_lbl.setStyleSheet("color: #888; font-size: 12px;")
        v_lay.addWidget(self.scan_item_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        # СТАТИСТИКА
        stats = QHBoxLayout()
        self.db_version = DataBlock("ENGINE VERSION", "V1.9")
        self.db_last_scan = DataBlock("LAST SCAN", "TODAY")
        stats.addWidget(self.db_version)
        stats.addWidget(self.db_last_scan)
        v_lay.addLayout(stats)
        
        return view

    # ФУНКЦІЯ: start_smart_scan
    # Викликає рушій сканування та переводить UI в режим активності.
    def start_smart_scan(self):
        self.scan_btn.hide()
        self.scan_bar.show()
        self.scan_bar.setValue(0)
        self.main_msg.setText("SCANNING IN PROGRESS...")
        
        # Запуск сканування (на даний момент прямий виклик для демонстрації)
        # В ідеалі це має бути в окремому QThread для плавності UI.
        # Для дотримання "простоти" виконуємо через таймер затримку.
        QTimer.singleShot(100, self.shield_engine.perform_smart_scan)

    # ОБРОБНИК: хід сканування
    def on_scan_progress(self, value, item_name):
        self.scan_bar.setValue(value)
        self.scan_item_lbl.setText(f"Checking: {item_name}")

    # ОБРОБНИК: завершення сканування
    def on_scan_finish(self, issues, duration):
        self.scan_bar.hide()
        self.scan_item_lbl.setText("")
        self.scan_btn.show()
        
        if issues == 0:
            self.main_msg.setText("SCAN COMPLETE: NO ISSUES FOUND")
            self.main_msg.setStyleSheet("color: #50BB00; font-size: 24px; font-weight: bold;")
        else:
            self.main_msg.setText(f"ALERT: {issues} ISSUES DETECTED")
            self.main_msg.setStyleSheet("color: #FF8800; font-size: 24px; font-weight: bold;")

    # МЕТОД: set_view
    # Зміна поточного вікна в стеку.
    def set_view(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_btns):
            btn.set_pulse(i == index)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    # Ініціалізація додатку Qt
    sys_app = QApplication(sys.argv)
    window = AvastSecuritySuite()
    window.showFullScreen()
    # Запуск циклу подій
    sys.exit(sys_app.exec())
