#!/usr/bin/env python3
"""
REAL LCARS DESKTOP - Authentic LCARS Geometry
Справжній LCARS з правильною геометрією та дизайном
"""
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QGridLayout, QSplitter, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QDateTime, QRect
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QBrush, QPen
from PyQt6.QtCore import QPoint

class LCARSElbowWidget(QFrame):
    """Справжній LCARS лікоть"""
    def __init__(self, corner="top-left", color="#FF9900"):
        super().__init__()
        self.corner = corner
        self.color = QColor(color)
        self.setFixedSize(200, 80)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Встановлюємо колір
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.color.darker(120), 2))
        
        # Малюємо лікоть залежно від кута
        if self.corner == "top-left":
            # Верхній лівий лікоть
            points = [
                QPoint(0, 40),
                QPoint(40, 0),
                QPoint(200, 0),
                QPoint(200, 80),
                QPoint(40, 80),
                QPoint(0, 40)
            ]
        elif self.corner == "top-right":
            # Верхній правий лікоть
            points = [
                QPoint(160, 0),
                QPoint(200, 40),
                QPoint(200, 80),
                QPoint(0, 80),
                QPoint(0, 0),
                QPoint(160, 0)
            ]
        elif self.corner == "bottom-left":
            # Нижній лівий лікоть
            points = [
                QPoint(0, 40),
                QPoint(40, 80),
                QPoint(200, 80),
                QPoint(200, 0),
                QPoint(40, 0),
                QPoint(0, 40)
            ]
        else:  # bottom-right
            # Нижній правий лікоть
            points = [
                QPoint(160, 80),
                QPoint(200, 40),
                QPoint(200, 0),
                QPoint(0, 0),
                QPoint(0, 80),
                QPoint(160, 80)
            ]
            
        painter.drawPolygon(points)

class LCARSButton(QFrame):
    """Справжня LCARS кнопка"""
    def __init__(self, text="", color="#FF9900", width=120, height=30):
        super().__init__()
        self.text = text
        self.color = QColor(color)
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            LCARSButton {{
                background: transparent;
            }}
        """)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Встановлюємо колір
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.color.darker(120), 2))
        
        # Малюємо прямокутник зі скосами
        points = [
            QPoint(10, 0),
            QPoint(self.width() - 10, 0),
            QPoint(self.width(), self.height() // 2),
            QPoint(self.width() - 10, self.height()),
            QPoint(10, self.height()),
            QPoint(0, self.height() // 2)
        ]
        
        painter.drawPolygon(points)
        
        # Малюємо текст
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)

class LCARSPanel(QFrame):
    """Справжня LCARS панель"""
    def __init__(self, color="#FF9900"):
        super().__init__()
        self.color = QColor(color)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Встановлюємо колір
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.color.darker(120), 2))
        
        # Малюємо панель з заокругленими кутами
        painter.drawRoundedRect(2, 2, self.width() - 4, self.height() - 4, 10, 10)

class RealLCARSDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("REAL LCARS DESKTOP")
        self.setGeometry(100, 100, 1400, 900)
        
        # LCARS кольори
        self.lcars_orange = "#FF9900"
        self.lcars_purple = "#CC99CC"
        self.lcars_red = "#CC6666"
        self.lcars_blue = "#6699CC"
        self.lcars_green = "#66CC66"
        self.lcars_black = "#000000"
        
        # Встановлюємо стиль
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.lcars_black};
            }}
            QLabel {{
                color: #FFFFFF;
                background-color: transparent;
                font-weight: bold;
            }}
        """)
        
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """Створення справжнього LCARS інтерфейсу"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Головний layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Верхній рядок - лікоть + заголовок
        top_row = QHBoxLayout()
        top_row.setSpacing(0)
        
        # Верхній лівий лікоть
        top_elbow = LCARSElbowWidget("top-left", self.lcars_orange)
        top_row.addWidget(top_elbow)
        
        # Центральна панель заголовка
        header_panel = LCARSPanel(self.lcars_orange)
        header_panel.setFixedHeight(80)
        header_layout = QHBoxLayout(header_panel)
        
        title = QLabel("LCARS DESKTOP")
        title.setStyleSheet("color: #000000; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        time_label = QLabel("00:00:00")
        time_label.setStyleSheet("color: #000000; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(time_label)
        
        top_row.addWidget(header_panel)
        
        # Верхній правий лікоть
        right_elbow = LCARSElbowWidget("top-right", self.lcars_orange)
        top_row.addWidget(right_elbow)
        
        main_layout.addLayout(top_row)
        
        # Основна область
        main_content = QHBoxLayout()
        main_content.setSpacing(10)
        main_content.setContentsMargins(10, 10, 10, 10)
        
        # Ліва панель - вертикальні кнопки
        left_panel = QVBoxLayout()
        left_panel.setSpacing(5)
        
        # Кнопки систем
        systems = [
            ("WEAPONS", self.lcars_red),
            ("SHIELDS", self.lcars_blue),
            ("CLOAK", self.lcars_purple),
            ("COMMS", self.lcars_green),
            ("ENGINEERING", self.lcars_orange),
            ("MEDICAL", self.lcars_purple),
            ("LIBRARY", self.lcars_blue),
            ("SECURITY", self.lcars_red)
        ]
        
        for text, color in systems:
            btn = LCARSButton(text, color, 150, 35)
            left_panel.addWidget(btn)
            
        left_panel.addStretch()
        main_content.addLayout(left_panel)
        
        # Центральна область
        center_area = QVBoxLayout()
        center_area.setSpacing(10)
        
        # Радарна панель
        radar_panel = LCARSPanel(self.lcars_orange)
        radar_panel.setFixedSize(400, 400)
        radar_layout = QVBoxLayout(radar_panel)
        
        radar_title = QLabel("TACTICAL DISPLAY")
        radar_title.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold;")
        radar_layout.addWidget(radar_title)
        
        # Радарний дисплей
        radar_display = LCARSPanel(self.lcars_black)
        radar_display.setStyleSheet("border: 2px solid #FF9900;")
        radar_layout.addWidget(radar_display)
        
        center_area.addWidget(radar_panel)
        
        # Кнопки управління
        control_row = QHBoxLayout()
        
        scan_btn = LCARSButton("SCAN", self.lcars_green, 120, 35)
        combat_btn = LCARSButton("COMBAT", self.lcars_red, 120, 35)
        alert_btn = LCARSButton("RED ALERT", self.lcars_red, 120, 35)
        
        control_row.addWidget(scan_btn)
        control_row.addWidget(combat_btn)
        control_row.addWidget(alert_btn)
        control_row.addStretch()
        
        center_area.addLayout(control_row)
        center_area.addStretch()
        
        main_content.addLayout(center_area)
        
        # Права панель - статус
        right_panel = QVBoxLayout()
        right_panel.setSpacing(5)
        
        # Статусні індикатори
        status_items = [
            ("POWER LEVEL", self.lcars_green),
            ("SHIELDS", self.lcars_blue),
            ("WEAPONS", self.lcars_red),
            ("HULL INTEGRITY", self.lcars_orange),
            ("WARP DRIVE", self.lcars_purple),
            ("IMPULSE", self.lcars_green),
            ("SENSORS", self.lcars_blue)
        ]
        
        for text, color in status_items:
            # Назва
            label = QLabel(text)
            label.setStyleSheet(f"color: {color}; font-size: 12px;")
            right_panel.addWidget(label)
            
            # Індикатор
            indicator = LCARSPanel(color)
            indicator.setFixedHeight(20)
            right_panel.addWidget(indicator)
            
        right_panel.addStretch()
        main_content.addLayout(right_panel)
        
        main_layout.addLayout(main_content)
        
        # Нижній рядок - лікті
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(0)
        
        # Нижній лівий лікоть
        bottom_left_elbow = LCARSElbowWidget("bottom-left", self.lcars_orange)
        bottom_row.addWidget(bottom_left_elbow)
        
        # Центральна нижня панель
        bottom_panel = LCARSPanel(self.lcars_orange)
        bottom_panel.setFixedHeight(60)
        bottom_layout = QHBoxLayout(bottom_panel)
        
        # Кнопки управління
        controls = [
            ("LAUNCH", self.lcars_green),
            ("RESTART", self.lcars_orange),
            ("SAVE", self.lcars_blue),
            ("FILES", self.lcars_purple),
            ("SEARCH", self.lcars_green),
            ("EXIT", self.lcars_red)
        ]
        
        for text, color in controls:
            btn = LCARSButton(text, color, 100, 30)
            bottom_layout.addWidget(btn)
            
        bottom_layout.addStretch()
        bottom_row.addWidget(bottom_panel)
        
        # Нижній правий лікоть
        bottom_right_elbow = LCARSElbowWidget("bottom-right", self.lcars_orange)
        bottom_row.addWidget(bottom_right_elbow)
        
        main_layout.addLayout(bottom_row)
        
    def setup_timer(self):
        """Налаштування таймера"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
    def update_time(self):
        """Оновлення часу"""
        # Оновлення часу можна додати пізніше
        pass

def main():
    app = QApplication(sys.argv)
    
    # Темна тема
    app.setStyle("Fusion")
    dark_palette = app.palette()
    dark_palette.setColor(dark_palette.ColorRole.Window, QColor(0, 0, 0))
    dark_palette.setColor(dark_palette.ColorRole.WindowText, QColor(255, 255, 255))
    app.setPalette(dark_palette)
    
    desktop = RealLCARSDesktop()
    desktop.show()
    
    print("🚀 REAL LCARS Desktop Started")
    print("📐 Authentic LCARS Geometry")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
