from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
import psutil

class SystemMonitor(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_system_monitor_tab()

    def setup_system_monitor_tab(self):
        layout = QVBoxLayout()

        # CPU usage
        self.cpu_label = QLabel("CPU Usage: 0%")
        layout.addWidget(self.cpu_label)

        # Memory usage
        self.memory_label = QLabel("Memory Usage: 0%")
        layout.addWidget(self.memory_label)

        # Network usage
        self.network_label = QLabel("Network Usage: 0 KB/s")
        layout.addWidget(self.network_label)

        # Update button
        update_button = QPushButton("Update System Monitor")
        update_button.clicked.connect(self.update_system_monitor)
        layout.addWidget(update_button)

        self.setLayout(layout)

    def update_system_monitor(self):
        # Get CPU usage
        cpu_usage = psutil.cpu_percent()
        self.cpu_label.setText(f"CPU Usage: {cpu_usage}%")

        # Get memory usage
        memory = psutil.virtual_memory()
        self.memory_label.setText(f"Memory Usage: {memory.percent}%")

        # Get network usage (example: bytes sent/received)
        try:
            net_io = psutil.net_io_counters()
            if net_io and not isinstance(net_io, dict) and hasattr(net_io, 'bytes_sent'):
                self.network_label.setText(f"Network Usage: {net_io.bytes_sent / 1024:.2f} KB sent")
            else:
                self.network_label.setText("Network Usage: Not available")
        except Exception as e:
            self.network_label.setText("Network Usage: Error")
            print(f"Error fetching network usage: {e}")

# Note: Integration of this SystemMonitor class into the main application
# would involve adding it as a tab or section in the existing UI framework.
