#!/usr/bin/env python3
"""
Інтеграція QML KlingonButton в PyQt6 через QQuickWidget
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import QUrl, QObject, pyqtSignal
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtQuickWidgets import QQuickWidget

class QMLBridge(QObject):
    button_clicked = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
    
    def emit_button_clicked(self, button_name):
        self.button_clicked.emit(button_name)

class KlingonQMLWidget(QQuickWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Встановлюємо QML джерело
        self.setSource(QUrl.fromLocalFile("klingon_button_widget.qml"))
        
        # Створюємо мост
        self.bridge = QMLBridge()
        self.rootContext().setContextProperty("bridge", self.bridge)
        
        # Підключаємо сигнали
        self.bridge.button_clicked.connect(self.on_button_clicked)
    
    def on_button_clicked(self, button_name):
        print(f"QML Button clicked: {button_name}")

class KlingonDemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 QML Klingon Button Integration")
        self.setGeometry(100, 100, 1000, 800)
        
        # Прибираємо рамку
        self.setWindowFlags(self.windowFlags() | self.windowFlags().FramelessWindowHint)
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Ліва панель
        left_panel = QWidget()
        left_panel.setFixedWidth(200)
        left_panel.setStyleSheet("background-color: #ff9c00;")
        left_layout = QVBoxLayout(left_panel)
        
        # Кнопки управління
        from PyQt6.QtWidgets import QPushButton
        btn1 = QPushButton("22ND")
        btn1.setStyleSheet("background-color: #8B0000; color: white; font-weight: bold;")
        btn1.clicked.connect(lambda: self.update_klingon_color("#8B0000"))
        
        btn2 = QPushButton("23RD")
        btn2.setStyleSheet("background-color: #660000; color: white; font-weight: bold;")
        btn2.clicked.connect(lambda: self.update_klingon_color("#660000"))
        
        btn3 = QPushButton("24TH")
        btn3.setStyleSheet("background-color: #990000; color: white; font-weight: bold;")
        btn3.clicked.connect(lambda: self.update_klingon_color("#990000"))
        
        btn4 = QPushButton("25TH")
        btn4.setStyleSheet("background-color: #CC0000; color: white; font-weight: bold;")
        btn4.clicked.connect(lambda: self.update_klingon_color("#CC0000"))
        
        exit_btn = QPushButton("EXIT")
        exit_btn.setStyleSheet("background-color: #cc6666; color: white; font-weight: bold;")
        exit_btn.clicked.connect(self.close)
        
        left_layout.addWidget(QLabel("KLINGON ERAS"))
        left_layout.addWidget(btn1)
        left_layout.addWidget(btn2)
        left_layout.addWidget(btn3)
        left_layout.addWidget(btn4)
        left_layout.addWidget(exit_btn)
        left_layout.addStretch()
        
        main_layout.addWidget(left_panel)
        
        # Права панель з QML віджетом
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_panel.setStyleSheet("background-color: black;")
        
        # Заголовок
        title = QLabel("✅ QML Klingon ShapePath Button")
        title.setStyleSheet("color: #ff9c00; font-size: 24px; font-weight: bold;")
        right_layout.addWidget(title)
        
        # QML віджет з клінгонською кнопкою
        self.klingon_widget = KlingonQMLWidget()
        self.klingon_widget.setFixedSize(400, 300)
        self.klingon_widget.setStyleSheet("background-color: transparent;")
        right_layout.addWidget(self.klingon_widget, alignment=self.klingon_widget.AlignmentFlag.AlignCenter)
        
        # Інформація
        info = QLabel("✨ Векторна клінгонська кнопка з ShapePath\n✨ Інтегрована в PyQt6 через QQuickWidget\n✨ Динамічні кольори для різних ер\n✨ Згладжування країв (anti-aliasing)")
        info.setStyleSheet("color: #ff9c00; font-size: 14px;")
        info.setAlignment(self.info.AlignmentFlag.AlignCenter)
        right_layout.addWidget(info)
        
        right_layout.addStretch()
        main_layout.addWidget(right_panel)
    
    def update_klingon_color(self, color):
        """Оновлює колір клінгонської кнопки"""
        if self.klingon_widget.rootObject():
            self.klingon_widget.rootObject().setProperty("btnColor", color)

def main():
    app = QApplication(sys.argv)
    
    window = KlingonDemoWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
