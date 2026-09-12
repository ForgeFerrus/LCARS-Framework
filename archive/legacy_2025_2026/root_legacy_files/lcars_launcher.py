#!/usr/bin/env python3
"""
LCARS Framework Main Launcher
Головний лаунчер системи LCARS з вибором режимів запуску
"""
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QPushButton, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor

# Додавання шляхів
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from lcars.themes.theme import get_lcars_font_style, setup_lcars_font
from lcars.themes.palette import LCARSEra

class LCARSButton(QPushButton):
    """Спеціалізована кнопка LCARS"""
    
    def __init__(self, text, color, size="medium"):
        super().__init__(text)
        self.color = color
        self.size = size
        
        # Розміри залежно від типу
        if size == "large":
            self.setMinimumHeight(60)
            self.setMinimumWidth(300)
        elif size == "medium":
            self.setMinimumHeight(45)
            self.setMinimumWidth(250)
        else:  # small
            self.setMinimumHeight(35)
            self.setMinimumWidth(200)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #000000;
                border: none;
                {get_lcars_font_style(14 if size == "large" else 12, 'bold')};
                padding: 10px 20px;
                text-transform: uppercase;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #FFFFFF;
                color: {color};
            }}
            QPushButton:pressed {{
                background-color: {color};
                color: #FFFFFF;
            }}
        """)

class LCARSDisplay(QFrame):
    """Анімований дисплей LCARS"""
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 200)
        self.setStyleSheet("background-color: #000000; border: 2px solid #FF9900;")
        self.animation_phase = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(150)
        
    def update_animation(self):
        self.animation_phase += 0.1
        if self.animation_phase > 2 * 3.14159:
            self.animation_phase = 0
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        orange = QColor(255, 153, 0)
        blue = QColor(153, 204, 255)
        
        pen = painter.pen()
        pen.setColor(orange)
        pen.setWidth(3)
        painter.setPen(pen)
        
        # Малюємо характерні елементи LCARS
        painter.drawLine(10, 10, self.width() - 10, 10)
        painter.drawLine(10, 10, 10, 80)
        painter.drawArc(10, 70, 40, 40, 90 * 16, 90 * 16)
        painter.drawLine(50, 110, 50, 180)
        
        # Анімовані елементи
        animated_x = 100 + int(30 * (1 + self.animation_phase) / 2)
        pen.setColor(blue)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(animated_x, 50, animated_x + 80, 50)
        
        # Текст
        pen.setColor(blue)
        painter.setPen(pen)
        font = QFont("Arial", 14, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(100, 130, "LCARS SYSTEM")
        painter.drawText(100, 150, f"STATUS: {'ONLINE' if int(self.animation_phase * 10) % 2 == 0 else 'ACTIVE'}")

class MainLauncher(QMainWindow):
    """Головний лаунчер LCARS"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Framework - Main Launcher")
        self.setFixedSize(900, 700)
        self.setStyleSheet("background-color: #000000;")
        
        self.init_ui()
        self.center_on_screen()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Верхній рядок з дисплеєм
        top_layout = QHBoxLayout()
        
        # Заголовок
        title_container = QFrame()
        title_layout = QVBoxLayout(title_container)
        
        title = QLabel("LCARS FRAMEWORK")
        title.setStyleSheet(f"""
            color: #FF9900;
            {get_lcars_font_style(24, 'bold')};
            text-align: center;
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title)
        
        subtitle = QLabel("Library of Computer Access & Retrieval System")
        subtitle.setStyleSheet(f"""
            color: #99CCFF;
            {get_lcars_font_style(14, 'normal')};
            text-align: center;
            padding: 5px;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)
        
        top_layout.addWidget(title_container)
        top_layout.addStretch()
        
        # LCARS Display
        self.display = LCARSDisplay()
        top_layout.addWidget(self.display)
        
        main_layout.addLayout(top_layout)
        
        # Роздільник
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #FF9900; height: 2px;")
        main_layout.addWidget(separator)
        
        # Кнопки запуску
        buttons_container = QFrame()
        buttons_layout = QGridLayout(buttons_container)
        buttons_layout.setSpacing(15)
        
        # Основні режими
        onboard_lcars_btn = LCARSButton("ONBOARD COMPUTER (AUTHENTIC)", "#CC3333", "large")
        onboard_lcars_btn.clicked.connect(self.launch_onboard_lcars)
        buttons_layout.addWidget(onboard_lcars_btn, 0, 0, 1, 2)  # Розтягнути на 2 колонки
        
        onboard_real_btn = LCARSButton("ONBOARD (REAL AI)", "#3366CC", "large")
        onboard_real_btn.clicked.connect(self.launch_onboard_real)
        buttons_layout.addWidget(onboard_real_btn, 1, 0, 1, 2)  # Розтягнути на 2 колонки
        
        onboard_original_btn = LCARSButton("ONBOARD (Original)", "#666666", "large")
        onboard_original_btn.clicked.connect(self.launch_onboard_original)
        buttons_layout.addWidget(onboard_original_btn, 2, 0, 1, 2)  # Розтягнути на 2 колонки
        
        # Додаткові режими
        launcher_btn = LCARSButton("SYSTEM LAUNCHER", "#66CC66", "medium")
        launcher_btn.clicked.connect(self.launch_system_launcher)
        buttons_layout.addWidget(launcher_btn, 3, 0)
        
        desktop_btn = LCARSButton("FULL DESKTOP", "#3366CC", "medium")
        desktop_btn.clicked.connect(self.launch_desktop)
        buttons_layout.addWidget(desktop_btn, 3, 1)
        
        # Інженерний сендбокс
        sandbox_btn = LCARSButton("ENGINEERING SANDBOX", "#CC6633", "large")
        sandbox_btn.clicked.connect(self.launch_sandbox)
        buttons_layout.addWidget(sandbox_btn, 4, 0, 1, 2)  # Розтягнути на 2 колонки
        
        # Інструменти
        tools_btn = LCARSButton("DEVELOPER TOOLS", "#9966CC", "medium")
        tools_btn.clicked.connect(self.launch_tools)
        buttons_layout.addWidget(tools_btn, 5, 0)
        
        settings_btn = LCARSButton("SETTINGS", "#CC9966", "medium")
        settings_btn.clicked.connect(self.launch_settings)
        buttons_layout.addWidget(settings_btn, 5, 1)
        
        main_layout.addWidget(buttons_container)
        main_layout.addStretch()
        
        # Нижня панель статусу
        status_container = QFrame()
        status_container.setStyleSheet("background-color: #0A0A0A; border: 1px solid #333333;")
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_label = QLabel("SYSTEM READY")
        self.status_label.setStyleSheet(f"""
            color: #99CCFF;
            {get_lcars_font_style(12, 'normal')};
        """)
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        version_label = QLabel("v2.0 - TITAN ERA")
        version_label.setStyleSheet(f"""
            color: #666666;
            {get_lcars_font_style(10, 'normal')};
        """)
        status_layout.addWidget(version_label)
        
        main_layout.addWidget(status_container)
        
    def center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)
            
    def launch_onboard_lcars(self):
        """Запуск аутентичного бортового комп'ютера"""
        self.status_label.setText("Launching AUTHENTIC BOARD COMPUTER...")
        QTimer.singleShot(500, self._run_onboard_lcars)
        
    def launch_onboard_real(self):
        """Запуск справжнього бортового комп'ютера з AI"""
        self.status_label.setText("Launching REAL ONBOARD COMPUTER with AI...")
        QTimer.singleShot(500, self._run_onboard_real)
        
    def launch_onboard_original(self):
        """Запуск оригінального бортового комп'ютера"""
        self.status_label.setText("Launching ORIGINAL ONBOARD COMPUTER...")
        QTimer.singleShot(500, self._run_onboard_original)
        
    def launch_desktop(self):
        """Запуск повного десктопа"""
        self.status_label.setText("Launching FULL DESKTOP...")
        QTimer.singleShot(500, self._run_desktop)
        
    def launch_system_launcher(self):
        """Запуск системного лаунчера"""
        self.status_label.setText("Launching SYSTEM LAUNCHER...")
        QTimer.singleShot(500, self._run_system_launcher)
        
    def launch_sandbox(self):
        """Запуск інженерного сендбоксу"""
        self.status_label.setText("Launching ENGINEERING SANDBOX...")
        QTimer.singleShot(500, self._run_sandbox)
        
    def launch_tools(self):
        """Запуск інструментів розробника"""
        self.status_label.setText("DEVELOPER TOOLS - Coming Soon...")
        
    def launch_settings(self):
        """Запуск налаштувань"""
        self.status_label.setText("SETTINGS - Coming Soon...")
        
    def _run_sandbox(self):
        try:
            import subprocess
            subprocess.Popen([sys.executable, "launch_minimal.py"], 
                           cwd=project_root, 
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.status_label.setText("✓ ENGINEERING SANDBOX launched")
        except Exception as e:
            self.status_label.setText(f"✗ Error: {str(e)}")
            
    def _run_onboard_lcars(self):
        try:
            import subprocess
            subprocess.Popen([sys.executable, "launch_onboard_lcars.py"], 
                           cwd=project_root, 
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.status_label.setText("✓ AUTHENTIC BOARD COMPUTER launched")
        except Exception as e:
            self.status_label.setText(f"✗ Error: {str(e)}")
            
    def _run_onboard_real(self):
        try:
            import subprocess
            subprocess.Popen([sys.executable, "launch_onboard_real.py"], 
                           cwd=project_root, 
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.status_label.setText("✓ REAL ONBOARD COMPUTER with AI launched")
        except Exception as e:
            self.status_label.setText(f"✗ Error: {str(e)}")
            
    def _run_onboard_original(self):
        try:
            import subprocess
            subprocess.Popen([sys.executable, "launch_onboard.py"], 
                           cwd=project_root,
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.status_label.setText("✓ ORIGINAL ONBOARD COMPUTER launched")
        except Exception as e:
            self.status_label.setText(f"✗ Error: {str(e)}")
            
    def _run_desktop(self):
        try:
            from lcars.ui.launcher import LCARSLauncher as DesktopLauncher
            self.desktop = DesktopLauncher(require_auth=False)
            self.desktop.exec()
            self.status_label.setText("✓ FULL DESKTOP launched")
        except Exception as e:
            self.status_label.setText(f"✗ Error: {str(e)}")
            
    def _run_system_launcher(self):
        try:
            import subprocess
            subprocess.Popen([sys.executable, "start_lcars.py"], 
                           cwd=project_root,
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.status_label.setText("✓ SYSTEM LAUNCHER launched")
        except Exception as e:
            self.status_label.setText(f"✗ Error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Налаштування шрифту LCARS
    setup_lcars_font()
    
    # Створення головного лаунчера
    launcher = MainLauncher()
    launcher.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
