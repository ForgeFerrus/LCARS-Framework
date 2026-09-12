
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen

class LCARSButton(QFrame):
    def __init__(self, text="", color="#FF9900", parent=None):
        super().__init__(parent)
        self.text = text
        self.color = QColor(color)
        self.setFixedSize(180, 40)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Малюємо LCARS кнопку
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.color.darker(120), 2))
        
        # Ліва половина з заокругленням
        points = [
            QPoint(20, 0),
            QPoint(self.width(), 0),
            QPoint(self.width(), self.height()),
            QPoint(20, self.height()),
            QPoint(0, self.height() // 2)
        ]
        painter.drawPolygon(points)
        
        # Текст
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(25, 15, self.width() - 30, 20, Qt.AlignmentFlag.AlignCenter, self.text)

class LCARSElbow(QFrame):
    def __init__(self, text="", color="#FF9900", corner="top-left", parent=None):
        super().__init__(parent)
        self.text = text
        self.color = QColor(color)
        self.corner = corner
        self.setFixedSize(200, 60)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.color.darker(120), 2))
        
        if self.corner == "top-left":
            points = [
                QPoint(0, 30),
                QPoint(30, 0),
                QPoint(200, 0),
                QPoint(200, 60),
                QPoint(30, 60),
                QPoint(0, 30)
            ]
        painter.drawPolygon(points)
        
        # Текст
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(40, 15, 150, 30, Qt.AlignmentFlag.AlignCenter, self.text)

class WorkingLCARS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS - WORKING")
        self.setGeometry(100, 100, 1200, 800)
        
        # Стиль
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QFrame {
                background-color: transparent;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Верхній рядок
        top_row = QHBoxLayout()
        top_row.setSpacing(0)
        
        # Верхній лівий лікоть
        elbow1 = LCARSElbow("TITANIUM CORE", "#FF9900", "top-left")
        top_row.addWidget(elbow1)
        
        # Центральна панель
        center_panel = QFrame()
        center_panel.setStyleSheet("background-color: #00CC00;")
        center_panel.setFixedHeight(60)
        center_layout = QHBoxLayout(center_panel)
        
        status = QLabel("SYSTEM ACTIVE")
        status.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold;")
        center_layout.addWidget(status)
        
        center_layout.addStretch()
        
        time_label = QLabel("03:55:23")
        time_label.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold;")
        center_layout.addWidget(time_label)
        
        top_row.addWidget(center_panel)
        
        # Верхній правий лікоть
        elbow2 = LCARSElbow("SECTOR 001", "#FF9900", "top-right")
        top_row.addWidget(elbow2)
        
        layout.addLayout(top_row)
        
        # Основна область
        main_area = QHBoxLayout()
        main_area.setSpacing(10)
        main_area.setContentsMargins(10, 10, 10, 10)
        
        # Ліва панель - кнопки
        left_panel = QVBoxLayout()
        left_panel.setSpacing(5)
        
        buttons = [
            ("BRIDGE", "#6699CC"),
            ("SENSORS", "#FF9900"),
            ("COMMS", "#CC99CC"),
            ("ENGINE", "#FFCC33"),
            ("DESIGNER", "#66CCCC")
        ]
        
        for text, color in buttons:
            btn = LCARSButton(text, color)
            left_panel.addWidget(btn)
            
        left_panel.addStretch()
        main_area.addLayout(left_panel)
        
        # Центральна область - чорний фон
        center = QFrame()
        center.setStyleSheet("background-color: #000000;")
        center.setMinimumSize(600, 400)
        main_area.addWidget(center)
        
        # Права панель - статус
        right_panel = QVBoxLayout()
        right_panel.setSpacing(5)
        
        status_items = [
            "POWER: 100%",
            "SHIELDS: 100%", 
            "WEAPONS: READY",
            "HULL: 100%"
        ]
        
        for item in status_items:
            label = QLabel(item)
            label.setStyleSheet("color: #FF9900; font-size: 14px; font-weight: bold;")
            right_panel.addWidget(label)
            
        right_panel.addStretch()
        main_area.addLayout(right_panel)
        
        layout.addLayout(main_area)
        
        # Нижній рядок
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(0)
        
        # Нижній лівий лікоть
        elbow3 = LCARSElbow("STATUS", "#8B4513", "bottom-left")
        bottom_row.addWidget(elbow3)
        
        # Нижня центральна панель
        bottom_center = QFrame()
        bottom_center.setStyleSheet("background-color: #FF9900;")
        bottom_center.setFixedHeight(40)
        bottom_row.addWidget(bottom_center)
        
        # Нижній правий лікоть  
        elbow4 = LCARSElbow("READY", "#8B4513", "bottom-right")
        bottom_row.addWidget(elbow4)
        
        layout.addLayout(bottom_row)

def main():
    app = QApplication(sys.argv)
    desktop = WorkingLCARS()
    desktop.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
