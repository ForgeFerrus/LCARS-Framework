# LCARS Onboard Computer Interface - Improved Version
# Справжній бортовий комп'ютер LCARS з повноцінним інтерфейсом
# Titanium Bridge Migration: import os, sys
# Titanium Bridge Migration: from pathlib import Path
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QFrame, QGridLayout, QProgressBar,
    QScrollArea, QSplitter, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QPen

# Додавання шляхів
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.themes.palette import LCARSEra
from lcars.themes.theme import get_theme, get_lcars_font_style, setup_lcars_font
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour
from lcars.core.board_computer import BoardComputer

class LCARSDisplay(QFrame):
    """Основний дисплей LCARS з анімованими елементами"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: #000000; border: 2px solid #FF9900;")
        self.animation_phase = 0
        
        # Таймер для анімації
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(100)
        
    def update_animation(self):
        self.animation_phase += 0.1
        if self.animation_phase > 2 * 3.14159:
            self.animation_phase = 0
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Основні кольори LCARS
        orange = QColor(255, 153, 0)
        blue = QColor(153, 204, 255)
        red = QColor(204, 51, 51)
        black = QColor(0, 0, 0)
        
        # Малюємо характерні елементи LCARS
        pen = QPen(orange, 3)
        painter.setPen(pen)
        
        # Верхня межа
        painter.drawLine(10, 10, self.width() - 10, 10)
        
        # Ліва межа з елбовом
        painter.drawLine(10, 10, 10, 100)
        painter.drawArc(10, 90, 40, 40, 90 * 16, 90 * 16)
        painter.drawLine(50, 130, 50, 200)
        
        # Анімовані елементи
        animated_x = 100 + int(50 * (1 + self.animation_phase) / 2)
        painter.setPen(QPen(blue, 2))
        painter.drawLine(animated_x, 50, animated_x + 100, 50)
        
        # Права межа
        painter.setPen(QPen(orange, 3))
        painter.drawLine(self.width() - 10, 10, self.width() - 10, 200)
        
        # Нижня межа
        painter.drawLine(10, self.height() - 10, self.width() - 10, self.height() - 10)
        
        # Текст
        painter.setPen(QPen(blue, 1))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(100, 150, "LCARS INTERFACE")
        painter.drawText(100, 170, f"STATUS: {'ONLINE' if int(self.animation_phase * 10) % 2 == 0 else 'ACTIVE'}")

class SystemMonitor(QWidget):
    """Монітор системних параметрів в стилі LCARS"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Таймер оновлення
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(2000)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("SYSTEM MONITOR")
        title.setStyleSheet(f"""
            color: #FF9900;
            {get_lcars_font_style(16, 'bold')};
            padding: 5px;
            border-bottom: 2px solid #FF9900;
        """)
        layout.addWidget(title)
        
        # Метрики
        self.metrics = {}
        metric_data = [
            ("CPU USAGE", "#99CCFF"),
            ("MEMORY", "#FF9900"),
            ("POWER", "#66CC66"),
            ("TEMPERATURE", "#CC6666"),
            ("SHIELDS", "#6699CC"),
            ("WEAPONS", "#CC3333")
        ]
        
        for name, color in metric_data:
            container = QFrame()
            container.setStyleSheet("background-color: #111111; border: 1px solid #333333;")
            
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(10, 5, 10, 5)
            
            # Назва
            label = QLabel(name)
            label.setStyleSheet(f"""
                color: {color};
                {get_lcars_font_style(12, 'bold')};
                min-width: 120px;
            """)
            container_layout.addWidget(label)
            
            # Прогрес бар
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(random.randint(20, 90))
            progress.setTextVisible(False)
            progress.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #222222;
                    border: none;
                    height: 20px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                }}
            """)
            container_layout.addWidget(progress)
            
            # Значення
            value_label = QLabel(f"{progress.value()}%")
            value_label.setStyleSheet(f"""
                color: white;
                {get_lcars_font_style(12, 'normal')};
                min-width: 40px;
            """)
            container_layout.addWidget(value_label)
            
            self.metrics[name] = {
                'progress': progress,
                'label': value_label,
                'color': color
            }
            
            layout.addWidget(container)
        
        layout.addStretch()
        
    def update_metrics(self):
        """Оновлення метрик з симуляцією"""
        for name, data in self.metrics.items():
            # Симуляція зміни значень
            current = data['progress'].value()
            change = random.randint(-10, 10)
            new_value = max(10, min(100, current + change))
            
            data['progress'].setValue(new_value)
            data['label'].setText(f"{new_value}%")
            
            # Зміна кольору при високих значеннях
            if new_value > 80:
                color = "#CC3333"  # Червоний
            elif new_value > 60:
                color = "#FF9900"  # Помаранчевий
            else:
                color = data['color']  # Оригінальний колір
                
            data['progress'].setStyleSheet(f"""
                QProgressBar {{
                    background-color: #222222;
                    border: none;
                    height: 20px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                }}
            """)

class CommunicationPanel(QWidget):
    """Панель зв'язку з AI"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("MAJEL CORE INTERFACE")
        title.setStyleSheet(f"""
            color: #99CCFF;
            {get_lcars_font_style(16, 'bold')};
            padding: 5px;
            border-bottom: 2px solid #99CCFF;
        """)
        layout.addWidget(title)
        
        # Область відповідей
        self.response_area = QTextEdit()
        self.response_area.setReadOnly(True)
        self.response_area.setMaximumHeight(200)
        self.response_area.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #99CCFF;
                border: 1px solid #333333;
                font-family: 'Courier New';
                font-size: 12px;
            }
        """)
        self.response_area.setPlainText("◤ MAJEL CORE ONLINE\n◤ Ready for commands...\n")
        layout.addWidget(self.response_area)
        
        # Кнопки швидких команд
        commands_layout = QHBoxLayout()
        
        quick_commands = [
            ("SYSTEM SCAN", "#CC3333"),
            ("Diagnostics", "#FF9900"),
            ("STATUS", "#66CC66"),
            ("LOGS", "#6699CC")
        ]
        
        for cmd_text, color in quick_commands:
            btn = QPushButton(cmd_text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: #000000;
                    border: none;
                    {get_lcars_font_style(10, 'bold')};
                    padding: 8px 12px;
                    text-transform: uppercase;
                }}
                QPushButton:hover {{
                    background-color: #FFFFFF;
                    color: {color};
                }}
            """)
            btn.clicked.connect(lambda checked, cmd=cmd_text: self.execute_command(cmd))
            commands_layout.addWidget(btn)
        
        layout.addLayout(commands_layout)
        
    def execute_command(self, command):
        """Виконання команди"""
        self.response_area.append(f"◤ EXECUTING: {command}")
        
        # Симуляція відповіді
        responses = {
            "SYSTEM SCAN": "◤ Scanning all systems...\n◤ All systems operational",
            "Diagnostics": "◤ Running diagnostics...\n◤ No issues detected",
            "STATUS": "◤ System Status: OPTIMAL\n◤ All subsystems online",
            "LOGS": "◤ Accessing system logs...\n◤ Recent activity: Normal"
        }
        
        QTimer.singleShot(1000, lambda: self.response_area.append(f"◤ {responses.get(command, 'Command processed')}"))
        QTimer.singleShot(1500, lambda: self.response_area.append("◤ Ready for next command...\n"))

class OnboardComputerImproved(QWidget):
    """Покращений бортовий комп'ютер LCARS"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.era = LCARSEra.LCARS_25TH
        self.theme = get_theme(self.era)
        self.init_ui()
        
    def init_ui(self):
        # Налаштування вікна
        self.setFixedSize(1200, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #FFFFFF;
            }
        """)
        
        # Головний layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Ліва панель - монітор системи
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #0A0A0A; border: 2px solid #FF9900;")
        left_panel.setFixedWidth(300)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # LCARS Display
        self.display = LCARSDisplay()
        left_layout.addWidget(self.display)
        
        # System Monitor
        self.monitor = SystemMonitor()
        left_layout.addWidget(self.monitor)
        
        # Права панель - комунікація
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #0A0A0A; border: 2px solid #99CCFF;")
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Communication Panel
        self.comm_panel = CommunicationPanel()
        right_layout.addWidget(self.comm_panel)
        
        # Додаємо панелі до головного layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # Сигнали для закриття
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

def main():
    """Запуск покращеного бортового комп'ютера"""
    app = QApplication(sys.argv)
    
    # Налаштування шрифту LCARS
    setup_lcars_font()
    
    # Створення вікна
    computer = OnboardComputerImproved()
    computer.setWindowTitle("LCARS :: ONBOARD COMPUTER :: IMPROVED")
    computer.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
