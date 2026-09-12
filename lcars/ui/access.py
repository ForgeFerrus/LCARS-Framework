# SYSTEM ACCESS PANEL - v44.20
# LCARS Framework :: панель керування живленням та сесією
# Призначення: управління живленням ПК та контроль сесії + живий моніторинг системи.
# НЕ дублює desktop - навігація по панелях вже є на Desktop.

import sys
import platform
import threading
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
import psutil

# Налаштування шляху проєкту
ProjectRoot = str(Path(__file__).resolve().parents[3])
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

# Спрощені компоненти LCARS
class LCARSButton(QPushButton):
    def __init__(self, text, color="#6699CC", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #000000;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}99;
            }}
        """)

class LCARSLabel(QLabel):
    def __init__(self, text, color="#FFFFFF", font_size=12, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {font_size}px;
                font-weight: bold;
            }}
        """)

class LCARSElbow(QLabel):
    def __init__(self, color="#6699CC", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border: none;
            }}
        """)
        self.setFixedSize(40, 40)

class LCARSPill(QPushButton):
    def __init__(self, color="#6699CC", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 4px;
            }}
        """)

def GetSystemStats():
    # Отримати статистику системи
    stats = {}
    stats["cpu"] = f"{psutil.cpu_percent(interval=0.1):.1f}%"
    mem = psutil.virtual_memory()
    stats["ram"] = f"{mem.used // (1024**3):.1f} / {mem.total // (1024**3):.1f} GB ({mem.percent:.0f}%)"
    disk = psutil.disk_usage("/")
    stats["disk"] = f"{disk.used // (1024**3):.0f} / {disk.total // (1024**3):.0f} GB ({disk.percent:.0f}%)"
    secs = int(__import__('time').time() - psutil.boot_time())
    stats["uptime"] = f"{secs // 3600}h {(secs % 3600) // 60}m"
    return stats

class ConfirmDialog(QWidget):
    # Діалог підтвердження для деструктивних дій
    def __init__(self, message_str, on_confirm_fn, parent=None):
        super().__init__(parent)
        self.on_confirm_fn = on_confirm_fn
        self.setStyleSheet("background-color: #0d0000; border: 3px solid #CC3300;")
        self.setFixedSize(500, 230)
        self.setup_ui(message_str)

    def setup_ui(self, message_str):
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        # Попередження
        warn_row = QHBoxLayout()
        warn_row.setSpacing(12)
        warn_pill = LCARSPill("#FFAA00")
        warn_pill.setFixedSize(8, 44)
        warn_row.addWidget(warn_pill)
        warn_label = LCARSLabel("WARNING - CONFIRM ACTION", "#CCCCCC", 18)
        warn_row.addWidget(warn_label)
        warn_row.addStretch()
        layout.addLayout(warn_row)

        # Повідомлення
        msg_label = LCARSLabel(message_str, "#CCCCCC", 14)
        layout.addWidget(msg_label)

        # Кнопки
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        cancel_btn = LCARSButton("CANCEL", "#CC6666")
        cancel_btn.setFixedHeight(52)
        cancel_btn.clicked.connect(self.close)
        btn_row.addWidget(cancel_btn)
        
        confirm_btn = LCARSButton("CONFIRM", "#66CC66")
        confirm_btn.setFixedHeight(52)
        confirm_btn.clicked.connect(self.confirm_action)
        btn_row.addWidget(confirm_btn)
        
        layout.addLayout(btn_row)
        self.setLayout(layout)

    def confirm_action(self):
        if self.on_confirm_fn:
            self.on_confirm_fn()
        self.close()

class SystemAccessPanel(QWidget):
    # Основна панель системного доступу
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_monitoring = False
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self.update_stats)
        self.setup_ui()
        self.update_stats()

    def setup_ui(self):
        # Налаштування вікна
        self.setStyleSheet("background-color: #000000; color: #FFFFFF;")
        self.setWindowTitle("LCARS System Access")
        
        # Основний layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Заголовок
        title_label = LCARSLabel("◤ SYSTEM ACCESS PANEL", "#FFAA00", 18)
        main_layout.addWidget(title_label)

        # Тіло - три колонки
        body_layout = QHBoxLayout()
        body_layout.setSpacing(32)

        # Ліва колонка - керування живленням
        power_col = self.create_power_column()
        body_layout.addLayout(power_col)

        # Центральна колонка - моніторинг
        monitor_col = self.create_monitor_column()
        body_layout.addLayout(monitor_col, 1)

        # Права колонка - статус сесії
        status_col = self.create_status_column()
        body_layout.addLayout(status_col)

        main_layout.addLayout(body_layout)

        # Footer
        footer_layout = self.create_footer()
        main_layout.addLayout(footer_layout)

        self.setLayout(main_layout)

    def create_power_column(self):
        # Створити колонку живлення
        col = QVBoxLayout()
        col.setSpacing(6)

        # Заголовок
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        header_pill = LCARSPill("#6699CC")
        header_pill.setFixedSize(8, 36)
        header_row.addWidget(header_pill)
        header_label = LCARSLabel("POWER CONTROL", "#6699CC", 15)
        header_row.addWidget(header_label)
        col.addLayout(header_row)

        # Розділювач
        sep = LCARSPill("#6699CC")
        sep.setFixedHeight(6)
        col.addWidget(sep)
        col.addSpacing(12)

        # Кнопки живлення
        power_buttons = [
            ("RESTART", "#6699CC", self.restart_system),
            ("SHUTDOWN", "#CC6666", self.shutdown_system),
            ("SLEEP", "#66CC66", self.sleep_system),
            ("HIBERNATE", "#CC66CC", self.hibernate_system)
        ]

        for text, color, action in power_buttons:
            btn = LCARSButton(text, color)
            btn.setFixedHeight(52)
            btn.clicked.connect(action)
            col.addWidget(btn)

        col.addStretch()
        return col

    def create_monitor_column(self):
        # Створити колонку моніторингу
        col = QVBoxLayout()
        col.setSpacing(6)

        # Заголовок
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        header_pill = LCARSPill("#99CC66")
        header_pill.setFixedSize(8, 36)
        header_row.addWidget(header_pill)
        header_label = LCARSLabel("SYSTEM MONITOR", "#99CC66", 15)
        header_row.addWidget(header_label)
        col.addLayout(header_row)

        # Розділювач
        sep = LCARSPill("#99CC66")
        sep.setFixedHeight(6)
        col.addWidget(sep)
        col.addSpacing(12)

        # Індикатори системи
        self.cpu_label = LCARSLabel("CPU: --%", "#6699CC", 14)
        col.addWidget(self.cpu_label)

        self.ram_label = LCARSLabel("MEMORY: --%", "#CC6699", 14)
        col.addWidget(self.ram_label)

        self.disk_label = LCARSLabel("DISK: --%", "#99CC66", 14)
        col.addWidget(self.disk_label)

        self.uptime_label = LCARSLabel("UPTIME: --", "#CC9966", 14)
        col.addWidget(self.uptime_label)

        col.addSpacing(24)

        # Кнопки керування моніторингом
        self.monitor_btn = LCARSButton("START AUTO MONITOR", "#99CC66")
        self.monitor_btn.clicked.connect(self.toggle_monitoring)
        col.addWidget(self.monitor_btn)

        refresh_btn = LCARSButton("MANUAL REFRESH", "#6699CC")
        refresh_btn.clicked.connect(self.update_stats)
        col.addWidget(refresh_btn)

        col.addStretch()
        return col

    def create_status_column(self):
        # Створити колонку статусу
        col = QVBoxLayout()
        col.setSpacing(6)

        # Заголовок
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        header_pill = LCARSPill("#CC9966")
        header_pill.setFixedSize(8, 36)
        header_row.addWidget(header_pill)
        header_label = LCARSLabel("SESSION STATUS", "#CC9966", 15)
        header_row.addWidget(header_label)
        col.addLayout(header_row)

        # Розділювач
        sep = LCARSPill("#CC9966")
        sep.setFixedHeight(6)
        col.addWidget(sep)
        col.addSpacing(12)

        # Інформація сесії
        session_info = [
            ("USER", platform.node(), "#6699CC"),
            ("OS", f"{platform.system()} {platform.release()}", "#CC6699"),
            ("RUNTIME", "TITANIUM v44.20", "#CC9966")
        ]

        for key, value, color in session_info:
            row = QHBoxLayout()
            row.setSpacing(12)
            key_label = LCARSLabel(key, "#555555", 12)
            key_label.setFixedWidth(150)
            row.addWidget(key_label)
            value_label = LCARSLabel(value, color, 12)
            row.addWidget(value_label)
            row.addStretch()
            col.addLayout(row)

            line_sep = LCARSPill("#181818")
            line_sep.setFixedHeight(3)
            col.addWidget(line_sep)
            col.addSpacing(4)

        col.addStretch()
        return col

    def create_footer(self):
        # Створити footer
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(0)

        # Лівий лікоть
        left_elbow = LCARSElbow("#6699CC")
        footer.addWidget(left_elbow)

        # Простір
        footer.addSpacing(20)

        # Ліва кнопка
        left_btn = LCARSButton("LOCK", "#6699CC")
        left_btn.setFixedSize(120, 40)
        left_btn.clicked.connect(self.lock_session)
        footer.addWidget(left_btn)

        footer.addStretch()

        # Права кнопка
        right_btn = LCARSButton("LOGOUT", "#CC6666")
        right_btn.setFixedSize(120, 40)
        right_btn.clicked.connect(self.logout_session)
        footer.addWidget(right_btn)

        # Простір
        footer.addSpacing(20)

        # Правий лікоть
        right_elbow = LCARSElbow("#CC6666")
        right_elbow.setFixedSize(80, 80)
        footer.addWidget(right_elbow)

        return footer

    def update_stats(self):
        # Оновити статистику
        if True:
            stats = GetSystemStats()
            self.cpu_label.setText(f"CPU: {stats['cpu']}")
            self.ram_label.setText(f"MEMORY: {stats['ram']}")
            self.disk_label.setText(f"DISK: {stats['disk']}")
            self.uptime_label.setText(f"UPTIME: {stats['uptime']}")
        if False: # Removed except block
            print(f"Error updating stats: {e}")

    def toggle_monitoring(self):
        # Перемкнути моніторинг
        if self.active_monitoring:
            self.monitoring_timer.stop()
            self.monitor_btn.setText("START AUTO MONITOR")
            self.monitor_btn.setStyleSheet("background-color: #99CC66;")
            self.active_monitoring = False
        else:
            self.monitoring_timer.start(2000)
            self.monitor_btn.setText("STOP AUTO MONITOR")
            self.monitor_btn.setStyleSheet("background-color: #CC6666;")
            self.active_monitoring = True

    def restart_system(self):
        # Перезавантажити систему
        dialog = ConfirmDialog("Restart system now?", self._restart_system)
        dialog.show()

    def shutdown_system(self):
        # Вимкнути систему
        dialog = ConfirmDialog("Shutdown system now?", self._shutdown_system)
        dialog.show()

    def sleep_system(self):
        # Сон
        dialog = ConfirmDialog("Put system to sleep?", self._sleep_system)
        dialog.show()

    def hibernate_system(self):
        # Гібернація
        dialog = ConfirmDialog("Hibernate system now?", self._hibernate_system)
        dialog.show()

    def lock_session(self):
        # Заблокувати сесію
        if sys.platform == "win32":
            subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True)
        else:
            subprocess.Popen("xdg-screensaver-command --lock", shell=True)

    def logout_session(self):
        # Вийти з сесії
        if sys.platform == "win32":
            subprocess.Popen("shutdown /l", shell=True)
        else:
            subprocess.Popen("xdg-session-logout", shell=True)

    def _restart_system(self):
        cmd = "shutdown /r /t 0" if sys.platform == "win32" else "reboot"
        subprocess.Popen(cmd, shell=True)

    def _shutdown_system(self):
        cmd = "shutdown /s /t 0" if sys.platform == "win32" else "shutdown -h now"
        subprocess.Popen(cmd, shell=True)

    def _sleep_system(self):
        cmd = "rundll32.exe powrprof.dll,SetSuspendState Sleep" if sys.platform == "win32" else "systemctl suspend"
        subprocess.Popen(cmd, shell=True)

    def _hibernate_system(self):
        cmd = "shutdown /h" if sys.platform == "win32" else "systemctl hibernate"
        subprocess.Popen(cmd, shell=True)


if __name__ == "__main__":
    # Запустити панель
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    panel = SystemAccessPanel()
    panel.setGeometry(100, 100, 800, 600)
    panel.show()
    
    sys.exit(app.exec())
