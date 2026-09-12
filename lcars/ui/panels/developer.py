from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from lcars.engineering.connector import engineering_core

class DeveloperPanel(QWidget):
    """
    Інженерна / Розробницька панель (Секція інтерфейсу).
    Взаємодіє з Колектором (Collector), відображає сирі метрики, RAM, споживання ресурсів, 
    та загальний стан системи в реальному часі.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.connect_engineering()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Заголовок
        self.lbl_title = QLabel("SYSTEM DIAGNOSTICS & TELEMETRY [DEV]")
        self.lbl_title.setStyleSheet("color: #CC99FF; font-family: 'Antonio'; font-size: 28px; font-weight: bold;")
        self.layout.addWidget(self.lbl_title)

        # Метрики
        self.lbl_ram = QLabel("RAM ALLOCATION: SCANNING...")
        self.lbl_ram.setStyleSheet("color: #FFFFFF; font-family: 'Antonio'; font-size: 18px;")
        self.layout.addWidget(self.lbl_ram)

        self.lbl_cpu = QLabel("CPU / CORE TEMP: SCANNING...")
        self.lbl_cpu.setStyleSheet("color: #FFFFFF; font-family: 'Antonio'; font-size: 18px;")
        self.layout.addWidget(self.lbl_cpu)

        self.lbl_net = QLabel("DATA STREAMS (UPLINK / DOWNLINK): SCANNING...")
        self.lbl_net.setStyleSheet("color: #FFFFFF; font-family: 'Antonio'; font-size: 18px;")
        self.layout.addWidget(self.lbl_net)

        # Сирий вивід (лог)
        self.lbl_log_title = QLabel("SYSTEM EVENT LOG")
        self.lbl_log_title.setStyleSheet("color: #CC99FF; font-family: 'Antonio'; font-size: 16px; margin-top: 10px;")
        self.layout.addWidget(self.lbl_log_title)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background-color: #111111; color: #CCCCCC; font-family: 'Consolas'; font-size: 12px; border: 1px solid #CC99FF;")
        self.layout.addWidget(self.txt_log)

    def connect_engineering(self):
        collector = engineering_core.get_subsystem("collector")
        if collector:
            # Підписуємось на сигнал від IObit-подібного Колектора
            collector.metrics_gathered.connect(self.on_metrics_update)

    def on_metrics_update(self, data: dict):
        """Отримує словник метрик напряму з engineering_core.collector і оновлює UI"""
        ram = data.get("ram_usage_percent", 0.0)
        ram_mb = data.get("ram_allocated_mb", 0.0)
        self.lbl_ram.setText(f"RAM ALLOCATION: {ram}% ({ram_mb:.0f} MB)")

        cpu = data.get("cpu_usage", 0.0)
        temp = data.get("core_temp_c", 0.0)
        self.lbl_cpu.setText(f"CPU LOAD: {cpu}% | CORE TEMP: {temp}°C")

        up = data.get("net_upload_kb", 0.0)
        down = data.get("net_download_kb", 0.0)
        self.lbl_net.setText(f"DATA STREAMS: UP {up} KB/s | DOWN {down} KB/s")

        status = data.get("status", "UNKNOWN")
        if status == "CRITICAL":
            self.lbl_title.setStyleSheet("color: #FF0000; font-family: 'Antonio'; font-size: 28px; font-weight: bold;")
        else:
            self.lbl_title.setStyleSheet("color: #CC99FF; font-family: 'Antonio'; font-size: 28px; font-weight: bold;")

    def log_message(self, msg: str):
        self.txt_log.append(msg)
