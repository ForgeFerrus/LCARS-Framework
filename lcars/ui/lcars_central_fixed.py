#!/usr/bin/env python3
"""
LCARS Central Command - Головний лаунчер
Центральний пункт управління всіма LCARS додатками
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import subprocess
import random
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QGridLayout,
                           QGroupBox, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QProcess, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QPixmap, QColor
# Titanium Bridge Migration: from datetime import datetime

# Додаємо корінь проекту до шляху Python
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import lcars.themes.lcars_palette as palette_module
from lcars.themes.lcars_palette import LCARSEra, get_era_palette

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._color = QColor()
        self._target_color = QColor()
        
    def set_color(self, color):
        self._color = color
        self.setStyleSheet(f"background-color: {color.name()};")
        
    def get_color(self):
        return self._color
        
    def animate_to_color(self, target_color, duration=1000):
        self._target_color = QColor(target_color)
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setDuration(duration)
        self.animation.setStartValue(self._color)
        self.animation.setEndValue(self._target_color)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()
        
    color = pyqtProperty(QColor, get_color, set_color)

class LCARSCentralCommand(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Поточна епоха
        self.current_era = LCARSEra.PCARS_23ST
        
        # Просто отримуємо палітру і все
        palette = get_era_palette(self.current_era)
        self.colors = palette  # Ось і все! Ніяких ключів!
        
        # Процеси додатків
        self.running_processes = {}
        self.app_buttons = {}
        self.app_status_labels = {}
        self.era_buttons = []  # Зберігаємо кнопки епох
        
        self.setup_window()
        self.setup_ui()
        self.apply_style()
        
        # Таймер для оновлення
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)
        
    def change_era(self, era):
        """Змінити епоху з анімацією кольорів"""
        self.current_era = era
        old_colors = self.colors.copy()
        self.colors = get_era_palette(era)
        
        # Просто змінюємо кольори кнопок з вашого алгоритму
        self.animate_button_colors(era)
        
        # Оновлюємо стан кнопок
        for btn in self.era_buttons:
            btn.setChecked(btn.text() == era.value)
        
        self.log_message(f"Switched to {era.value} era")
        
    def animate_button_colors(self, era):
        """Анімація кольорів кнопок з готового алгоритму"""
        for i, btn in enumerate(self.era_buttons):
            # Спочатку випадковий колір для ефекту
            random_color = palette_module.get_random_button_color(era)
            # Потім правильний колір по циклу
            correct_color = palette_module.get_button_color_cycle(era, i)
            
            # Затримка між кнопками для ефекту хвилі
            delay = i * 150  # Кожна наступна кнопка через 150мС
            
            # Спочатку показуємо випадковий колір
            QTimer.singleShot(delay, lambda b=btn, c=random_color: 
                           b.animate_to_color(c, 400))
            
            # Потім змінюємо на правильний колір
            QTimer.singleShot(delay + 500, lambda b=btn, c=correct_color: 
                           b.animate_to_color(c, 600))
        
        # Застосовуємо повний стиль після анімації
        QTimer.singleShot(1500, self.apply_style)
        
    def animate_color_transition(self, old_palette, new_palette):
        """Анімація переходу між палітрами"""
        # Анімуємо зміну кольору кнопок епох
        for i, btn in enumerate(self.era_buttons):
            if i < len(new_palette['button_colors']):
                btn.animate_to_color(new_palette['button_colors'][i], 1500)
        
        # Застосовуємо новий стиль після анімації
        QTimer.singleShot(1600, self.apply_style)
        
    def setup_window(self):
        """Налаштування вікна"""
        self.setWindowTitle("LCARS Central Command")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        
    def setup_ui(self):
        """Створення інтерфейсу"""
        
        # Спочатку створюємо контейнер для кнопок епох
        era_container = QWidget()
        era_layout = QHBoxLayout(era_container)
        
        # Додаємо кнопки епох
        for i, era in enumerate(LCARSEra):
            btn = AnimatedButton(era.value)
            btn.setCheckable(True)
            btn.setChecked(era == self.current_era)
            btn.setObjectName("lcars_era_button")
            btn.clicked.connect(lambda checked, e=era: self.change_era(e))
            
            # Встановлюємо початковий колір з алгоритму
            initial_color = palette_module.get_button_color_cycle(self.current_era, i)
            btn.set_color(QColor(initial_color))
            
            era_layout.addWidget(btn)
            self.era_buttons.append(btn)
        
        # Вставляємо кнопки епох на початок
        self.main_layout.insertWidget(0, era_container)
        
        # Заголовок
        header_layout = QHBoxLayout()
        
        # Логотип/Заголовок
        title = QLabel("LCARS CENTRAL COMMAND")
        title.setObjectName("lcars_main_title")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(title)
        
        # Статус
        self.status_label = QLabel("ALL SYSTEMS OPERATIONAL")
        self.status_label.setObjectName("lcars_status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(self.status_label)
        
        self.main_layout.addLayout(header_layout)
        
        # Час
        self.time_label = QLabel()
        self.time_label.setObjectName("lcars_time")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.time_label)
        
        # Основний контент
        content_layout = QHBoxLayout()
        
        # Ліва панель - додатки
        self.create_applications_panel(content_layout)
        
        # Права панель - статус
        self.create_status_panel(content_layout)
        
        self.main_layout.addLayout(content_layout)
        
        # Нижня панель - швидкі дії
        self.create_quick_actions()

    def create_applications_panel(self, parent_layout):
        """Панель додатків"""
        apps_group = QGroupBox("APPLICATIONS")
        apps_group.setObjectName("lcars_group")
        apps_layout = QGridLayout(apps_group)
        
        # Список додатків
        applications = [
            {
                'name': 'LCARS Framework v3.0',
                'description': 'Plugin Edition with Event System',
                'file': 'lcars_v3.py',
                'status': 'stopped',
                'icon': '🚀'
            },
            {
                'name': 'LCARS Simple Interface',
                'description': 'Clean and functional interface',
                'file': 'lcars_simple.py',
                'status': 'stopped',
                'icon': '🎨'
            },
            {
                'name': 'LCARS 25th Century',
                'description': 'Advanced 25th century interface with full features',
                'file': 'lcars/ui/LCARS_25th.py',
                'status': 'stopped',
                'icon': '🖥️'
            },
            {
                'name': 'System Monitor',
                'description': 'Real-time system monitoring',
                'file': 'lcars_monitor.py',
                'status': 'stopped',
                'icon': '📊'
            },
            {
                'name': 'Demo Window',
                'description': 'Interface demonstration',
                'file': 'demo_window.py',
                'status': 'stopped',
                'icon': '🎭'
            },
            {
                'name': 'Integration Tests',
                'description': 'Plugin system testing',
                'file': 'tests/test_integration_phase1.py',
                'status': 'stopped',
                'icon': '🧪'
            },
            {
                'name': 'Health Check',
                'description': 'System diagnostics',
                'file': 'health_check.bat',
                'status': 'stopped',
                'icon': '⚕️'
            }
        ]
        
        for i, app in enumerate(applications):
            row = i // 2
            col = (i % 2) * 3
            
            # Іконка
            icon_label = QLabel(app['icon'])
            icon_label.setObjectName("lcars_app_icon")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            apps_layout.addWidget(icon_label, row, col)
            
            # Інформація про додаток
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(5, 0, 5, 0)
            
            name_label = QLabel(app['name'])
            name_label.setObjectName("lcars_app_name")
            info_layout.addWidget(name_label)
            
            desc_label = QLabel(app['description'])
            desc_label.setObjectName("lcars_app_desc")
            info_layout.addWidget(desc_label)
            
            status_label = QLabel(f"Status: {app['status'].upper()}")
            status_label.setObjectName("lcars_app_status")
            info_layout.addWidget(status_label)
            self.app_status_labels[app['file']] = status_label
            
            apps_layout.addWidget(info_widget, row, col + 1)
            
            # Кнопка запуску
            launch_btn = QPushButton("LAUNCH")
            launch_btn.setObjectName("lcars_launch_button")
            launch_btn.clicked.connect(lambda checked, filename=app['file']: self.launch_application(filename))
            apps_layout.addWidget(launch_btn, row, col + 2)
            self.app_buttons[app['file']] = launch_btn
            
        parent_layout.addWidget(apps_group, 2)
        
    def create_status_panel(self, parent_layout):
        """Панель статусу"""
        status_group = QGroupBox("SYSTEM STATUS")
        status_group.setObjectName("lcars_group")
        status_layout = QVBoxLayout(status_group)
        
        # Системна інформація
        system_info = QLabel()
        system_info.setObjectName("lcars_system_info")
        
        import platform
        info_text = f"""Platform: {platform.system()} {platform.release()}
            Python: {platform.python_version()}
            Architecture: {platform.machine()}
            Processor: {platform.processor()[:50]}"""
        
        system_info.setText(info_text)
        status_layout.addWidget(system_info)
        
        # Статус процесів
        process_label = QLabel("RUNNING PROCESSES")
        process_label.setObjectName("lcars_section_title")
        status_layout.addWidget(process_label)
        
        self.process_list = QTextEdit()
        self.process_list.setObjectName("lcars_process_list")
        self.process_list.setMaximumHeight(150)
        self.process_list.setPlainText("No applications running...")
        status_layout.addWidget(self.process_list)
        
        # Логи
        log_label = QLabel("SYSTEM LOGS")
        log_label.setObjectName("lcars_section_title")
        status_layout.addWidget(log_label)
        
        self.log_display = QTextEdit()
        self.log_display.setObjectName("lcars_log_display")
        self.log_display.setMaximumHeight(200)
        self.log_display.setPlainText("LCARS Central Command initialized...\\nAll systems ready...")
        status_layout.addWidget(self.log_display)
        
        parent_layout.addWidget(status_group, 1)
        
    def create_quick_actions(self):
        """Швидкі дії"""
        actions_layout = QHBoxLayout()
        
        quick_actions = [
            ("🔄 REFRESH ALL", self.refresh_all),
            ("⏹️ STOP ALL", self.stop_all_applications),
            ("🧪 RUN TESTS", self.run_tests),
            ("⚙️ CONFIGURATION", self.open_configuration),
            ("📋 DOCUMENTATION", self.open_documentation),
            ("🚪 EXIT", self.close_application)
        ]
        
        for text, func in quick_actions:
            btn = QPushButton(text)
            btn.setObjectName("lcars_quick_button")
            btn.clicked.connect(func)
            actions_layout.addWidget(btn)
            
        self.main_layout.addLayout(actions_layout)

    def apply_style(self):
        """Застосування LCARS стилів"""
        style = f"""
        QMainWindow {{
            background-color: {self.colors['background']};
        }}
        
        #lcars_main_title {{
            color: {self.colors['background']};
            font-size: 28px;
            font-weight: bold;
            padding: 15px 25px;
            background-color: {self.colors['button_colors'][0]};
            border-radius: 15px;
            margin: 5px;
        }}
        
        #lcars_status {{
            color: {self.colors['background']};
            font-size: 16px;
            font-weight: bold;
            padding: 15px 25px;
            background-color: {self.colors['alert_colors'][0]};
            border-radius: 15px;
            margin: 5px;
        }}
        
        #lcars_time {{
            color: {self.colors['text']};
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            text-align: center;
        }}
        
        #lcars_group {{
            color: {self.colors['text']};
            font-weight: bold;
            font-size: 16px;
            border: 3px solid {self.colors['button_colors'][1]};
            border-radius: 12px;
            margin: 5px;
            padding: 15px;
        }}
        
        #lcars_app_icon {{
            font-size: 32px;
            padding: 10px;
            background-color: {self.colors['button_colors'][0]};
            border-radius: 20px;
            margin: 5px;
        }}
        
        #lcars_app_name {{
            color: {self.colors['button_colors'][0]};
            font-size: 14px;
            font-weight: bold;
            margin: 2px;
        }}
        
        #lcars_app_desc {{
            color: {self.colors['text']};
            font-size: 11px;
            margin: 1px;
        }}
        
        #lcars_app_status {{
            color: {self.colors['button_colors'][1]};
            font-size: 10px;
            font-weight: bold;
            margin: 1px;
        }}
        
        #lcars_launch_button {{
            background-color: {self.colors['button_colors'][2]};
            color: {self.colors['background']};
            font-size: 12px;
            font-weight: bold;
            padding: 10px 15px;
            border: none;
            border-radius: 15px;
            margin: 5px;
        }}
        
        #lcars_launch_button:hover {{
            background-color: {self.colors['button_colors'][3]};
        }}
        
        #lcars_launch_button:disabled {{
            background-color: #666666;
            color: #999999;
        }}
        
        #lcars_system_info {{
            color: {self.colors['text']};
            font-size: 11px;
            font-family: 'Courier New';
            padding: 10px;
            background-color: {self.colors['background']};
            border: 1px solid {self.colors['button_colors'][1]};
            border-radius: 8px;
        }}
        
        #lcars_section_title {{
            color: {self.colors['background']};
            font-size: 14px;
            font-weight: bold;
            padding: 8px;
            background-color: {self.colors['button_colors'][0]};
            border-radius: 8px;
            margin: 5px 0;
        }}
        
        #lcars_process_list {{
            background-color: {self.colors['background']};
            color: {self.colors['alert_colors'][0]};
            border: 2px solid {self.colors['alert_colors'][0]};
            border-radius: 8px;
            font-family: 'Courier New';
            font-size: 10px;
            padding: 8px;
        }}
        
        #lcars_log_display {{
            background-color: {self.colors['background']};
            color: {self.colors['text']};
            border: 2px solid {self.colors['button_colors'][1]};
            border-radius: 8px;
            font-family: 'Courier New';
            font-size: 10px;
            padding: 8px;
        }}
        
        #lcars_quick_button {{
            background-color: {self.colors['button_colors'][1]};
            color: {self.colors['background']};
            font-size: 12px;
            font-weight: bold;
            padding: 12px 20px;
            border: none;
            border-radius: 18px;
            margin: 5px;
        }}
        
        #lcars_quick_button:hover {{
            background-color: {self.colors['button_colors'][0]};
        }}
        
        #lcars_era_button {{
            background-color: {self.colors['button_colors'][1]};
            color: {self.colors['background']};
            font-size: 14px;
            font-weight: bold;
            padding: 12px 20px;
            border: 2px solid {self.colors['button_colors'][0]};
            border-radius: 15px;
            margin: 5px;
        }}
        
        #lcars_era_button:hover {{
            background-color: {self.colors['button_colors'][0]};
            border-color: {self.colors['button_colors'][2]};
        }}
        
        #lcars_era_button:checked {{
            background-color: {self.colors['button_colors'][0]};
            border-color: {self.colors['alert_colors'][0]};
            border-width: 3px;
        }}
        """
        
        self.setStyleSheet(style)
        
    def update_status(self):
        """Оновлення статусу"""
        # Час
        current_time = datetime.now().strftime("STARDATE %Y.%m.%d - %H:%M:%S")
        self.time_label.setText(current_time)
        
        # Статус процесів
        running_apps = []
        for filename, process in self.running_processes.items():
            if process and process.state() == QProcess.ProcessState.Running:
                running_apps.append(filename)
                if filename in self.app_status_labels:
                    self.app_status_labels[filename].setText("Status: RUNNING")
                    self.app_status_labels[filename].setStyleSheet(f"color: {self.colors['alert_colors'][0]};")
                if filename in self.app_buttons:
                    self.app_buttons[filename].setText("STOP")
                    self.app_buttons[filename].setEnabled(True)
            else:
                if filename in self.app_status_labels:
                    self.app_status_labels[filename].setText("Status: STOPPED")
                    self.app_status_labels[filename].setStyleSheet(f"color: {self.colors['text']};")
                if filename in self.app_buttons:
                    self.app_buttons[filename].setText("LAUNCH")
                    self.app_buttons[filename].setEnabled(True)
        
        # Оновлення списку процесів
        if running_apps:
            process_text = "\\n".join([f"• {app}" for app in running_apps])
            self.process_list.setPlainText(process_text)
        else:
            self.process_list.setPlainText("No applications running...")
            
    def launch_application(self, filename):
        """Запуск додатка"""
        if filename in self.running_processes and self.running_processes[filename]:
            process = self.running_processes[filename]
            if process.state() == QProcess.ProcessState.Running:
                # Зупинити процес
                process.terminate()
                self.log_message(f"Stopping {filename}...")
                return
        
        # Запустити новий процес
        self.log_message(f"Launching {filename}...")
        
        process = QProcess(self)
        python_exe = sys.executable
        
        if filename.endswith('.bat'):
            process.start(filename)
        else:
            # Додаємо корінь проекту до шляху для запуску
            if not filename.startswith('lcars/ui/'):
                full_path = str(Path(project_root) / filename)
            else:
                full_path = str(Path(project_root) / filename)
            
            # Для LCARS_25th.py додаємо root_path як аргумент
            if 'LCARS_25th.py' in filename:
                process.start(python_exe, [full_path, project_root])
            else:
                process.start(python_exe, [full_path])
            
        self.running_processes[filename] = process
        
        # Заблокувати кнопку на час запуску
        if filename in self.app_buttons:
            self.app_buttons[filename].setEnabled(False)
            self.app_buttons[filename].setText("STARTING...")
            
    def log_message(self, message):
        """Додати повідомлення в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")
        
        # Обмежити кількість рядків в логу
        lines = self.log_display.toPlainText().split('\\n')
        if len(lines) > 20:
            self.log_display.setPlainText('\\n'.join(lines[-20:]))
            
    def refresh_all(self):
        """Оновити все"""
        self.log_message("Refreshing all status...")
        self.update_status()
        
    def stop_all_applications(self):
        """Зупинити всі додатки"""
        self.log_message("Stopping all applications...")
        for filename, process in self.running_processes.items():
            if process and process.state() == QProcess.ProcessState.Running:
                process.terminate()
                
    def run_tests(self):
        """Запустити тести"""
        self.log_message("Running integration tests...")
        self.launch_application("tests/test_integration_phase1.py")
        
    def open_configuration(self):
        """Відкрити конфігурацію"""
        QMessageBox.information(self, "LCARS", "Configuration editor coming soon!")
        
    def open_documentation(self):
        """Відкрити документацію"""
        QMessageBox.information(self, "LCARS", "Documentation viewer coming soon!")
        
    def close_application(self):
        """Закрити додаток"""
        reply = QMessageBox.question(self, "LCARS Central Command", 
                                   "Are you sure you want to exit?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.stop_all_applications()
            self.close()

def main():
    """Головна функція"""
    app = QApplication(sys.argv)
    
    window = LCARSCentralCommand()
    window.show()
    
    print("🎛️ LCARS Central Command запущено!")
    print("🚀 Центральний пункт управління всіма додатками")
    print("🖖 Live long and prosper!")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
