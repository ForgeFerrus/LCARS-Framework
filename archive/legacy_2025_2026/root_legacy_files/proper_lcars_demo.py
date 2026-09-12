#!/usr/bin/env python3
"""
Правильні LCARS компоненти з трикутниками, трапеціями та шестикутниками
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                            QHBoxLayout, QWidget, QLabel, QPushButton)
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QPolygon, QColor, QBrush, QPen

# Правильні LCARS компоненти
class LCARSTriangleButton(QPushButton):
    """LCARS трикутна кнопка (Klingon style)"""
    def __init__(self, text, color="#CC0000", text_color="#FFFFFF", parent=None):
        super().__init__(text, parent)
        self.color = QColor(color)
        self.text_color = QColor(text_color)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }
        """)
        self.setFixedSize(120, 60)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Малюємо трикутник
        triangle = QPolygon([
            QPoint(0, self.height()),
            QPoint(self.width(), self.height()),
            QPoint(self.width() // 2, 0)
        ])
        
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.text_color, 2))
        painter.drawPolygon(triangle)
        
        # Малюємо текст
        painter.setPen(self.text_color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class LCARSTrapezoidButton(QPushButton):
    """LCARS трапецієподібна кнопка (Romulan style)"""
    def __init__(self, text, color="#006644", text_color="#00FF99", parent=None):
        super().__init__(text, parent)
        self.color = QColor(color)
        self.text_color = QColor(text_color)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #00FF99;
                font-weight: bold;
                font-style: italic;
                font-size: 12px;
                padding: 5px;
            }
        """)
        self.setFixedSize(120, 60)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Малюємо трапецію
        trapezoid = QPolygon([
            QPoint(10, self.height()),
            QPoint(self.width() - 10, self.height()),
            QPoint(self.width() - 5, 0),
            QPoint(5, 0)
        ])
        
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.text_color, 2))
        painter.drawPolygon(trapezoid)
        
        # Малюємо текст
        painter.setPen(self.text_color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class LCARSHexagonButton(QPushButton):
    """LCARS шестикутна кнопка (Cardassian style)"""
    def __init__(self, text, color="#CC3300", text_color="#FFFFFF", parent=None):
        super().__init__(text, parent)
        self.color = QColor(color)
        self.text_color = QColor(text_color)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-weight: bold;
                font-size: 11px;
                padding: 5px;
            }
        """)
        self.setFixedSize(100, 60)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Малюємо шестикутник
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(self.width(), self.height()) // 2 - 5
        
        hexagon = QPolygon()
        # Створюємо правильний шестикутник
        for i in range(6):
            angle = i * 60
            x = int(center_x + radius * 0.866 * (1 if i % 2 == 0 else 0.5))
            y = int(center_y + radius * (0.5 if i % 2 == 0 else -0.5))
            hexagon.append(QPoint(x, y))
        
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.text_color, 2))
        painter.drawPolygon(hexagon)
        
        # Малюємо текст
        painter.setPen(self.text_color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class LCARSPanel(QWidget):
    """LCARS панель з правильними формами"""
    def __init__(self, color="#000000", border_color="#217AFF", parent=None):
        super().__init__(parent)
        self.bg_color = QColor(color)
        self.border_color = QColor(border_color)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border: 2px solid {border_color};
                border-radius: 0px;
            }}
        """)
        self.setMinimumHeight(80)

class ProperLCARSDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Правильні LCARS Компоненти")
        self.setGeometry(300, 300, 800, 600)
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Заголовок
        title = QLabel("⭐ ПРАВИЛЬНІ LCARS ФОРМИ ⭐")
        title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background-color: #000000;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                text-align: center;
                border: 2px solid #217AFF;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Klingon секція
        klingon_label = QLabel("🔺 KLINGON - ТРИКУТНИКИ")
        klingon_label.setStyleSheet("""
            QLabel {
                color: #FF0000;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        layout.addWidget(klingon_label)
        
        klingon_panel = LCARSPanel("#000000", "#CC0000")
        klingon_layout = QHBoxLayout(klingon_panel)
        
        klingon_buttons = [
            LCARSTriangleButton("КОМАНДА", "#CC0000"),
            LCARSTriangleButton("ЗБРОЯ", "#FF0000"),
            LCARSTriangleButton("ЩИТИ", "#990000"),
            LCARSTriangleButton("ЕНЕРГІЯ", "#660000")
        ]
        
        for button in klingon_buttons:
            klingon_layout.addWidget(button)
        
        layout.addWidget(klingon_panel)
        
        # Romulan секція
        romulan_label = QLabel("🔻 ROMULAN - ТРАПЕЦІЇ")
        romulan_label.setStyleSheet("""
            QLabel {
                color: #00FF99;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        layout.addWidget(romulan_label)
        
        romulan_panel = LCARSPanel("#000000", "#006644")
        romulan_layout = QHBoxLayout(romulan_panel)
        
        romulan_buttons = [
            LCARSTrapezoidButton("ТАЛ ШИАР", "#006644"),
            LCARSTrapezoidButton("ПЛАЗМА", "#008866"),
            LCARSTrapezoidButton("МАСКИРОВКА", "#004433"),
            LCARSTrapezoidButton("ТЕЛЕПОРТ", "#002211")
        ]
        
        for button in romulan_buttons:
            romulan_layout.addWidget(button)
        
        layout.addWidget(romulan_panel)
        
        # Cardassian секція
        cardassian_label = QLabel("🟠 CARDASSIAN - ШЕСТИКУТНИКИ")
        cardassian_label.setStyleSheet("""
            QLabel {
                color: #FF6600;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        layout.addWidget(cardassian_label)
        
        cardassian_panel = LCARSPanel("#000000", "#CC3300")
        cardassian_layout = QHBoxLayout(cardassian_panel)
        
        cardassian_buttons = [
            LCARSHexagonButton("ОБСЛУГА", "#CC3300"),
            LCARSHexagonButton("БАЗА", "#FF4400"),
            LCARSHexagonButton("СИСТЕМА", "#FF6600"),
            LCARSHexagonButton("КОНТРОЛЬ", "#992200")
        ]
        
        for button in cardassian_buttons:
            cardassian_layout.addWidget(button)
        
        layout.addWidget(cardassian_panel)
        
        # Інформація
        info_label = QLabel("🎨 Це справжні LCARS форми з трикутниками, трапеціями та шестикутниками!")
        info_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
                padding: 15px;
                background-color: #111111;
                border: 1px solid #333333;
            }
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Стиль вікна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
        """)
        
        print("🎯 Правильні LCARS компоненти створено!")
    
    def showEvent(self, event):
        super().showEvent(event)
        print("👁️ Вікно з правильними LCARS формами показано!")
        self.raise_()
        self.activateWindow()

def main():
    print("🚀 Запускаємо правильні LCARS компоненти...")
    app = QApplication(sys.argv)
    
    window = ProperLCARSDemo()
    window.show()
    
    print("⚡ Програма запущена!")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
