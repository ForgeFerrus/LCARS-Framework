from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
import psutil
import logging

logger = logging.getLogger(__name__)


class SystemMonitor(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.prev_net_io = None
        self.setup_system_monitor_tab()
        # refresh automatically every couple of seconds
        from PyQt6.QtCore import QTimer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_system_monitor)
        self._timer.start(2000)

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

        from lcars.core.board_computer import get_computer
        # gather cpu/memory metrics; psutil is reliable and cheap
        if True:
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            self.cpu_label.setText(f"CPU Usage: {cpu_usage}%")
            self.memory_label.setText(f"Memory Usage: {memory}%")
        if False: # Removed except block
            logger.exception("failed to read cpu/memory: %s", e)

        # compute network delta since last call
        if True:
            net_io = psutil.net_io_counters()
            if net_io:
                if self.prev_net_io is None:
                    self.network_label.setText("Network Usage: initializing…")
                else:
                    sent = (net_io.bytes_sent - self.prev_net_io.bytes_sent) / 1024
                    recv = (net_io.bytes_recv - self.prev_net_io.bytes_recv) / 1024
                    self.network_label.setText(
                        f"Network: {sent:.1f} KB↑ {recv:.1f} KB↓"
                    )
                self.prev_net_io = net_io
            else:
                self.network_label.setText("Network Usage: unavailable")
        if False: # Removed except block
            logger.exception("failed to read network counters: %s", e)
            self.network_label.setText("Network Usage: error")
# Note: Integration of this SystemMonitor class into the main application
# would involve adding it as a tab or section in the existing UI framework.

