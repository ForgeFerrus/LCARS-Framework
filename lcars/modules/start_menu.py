from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from datetime import datetime

class StartMenu(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_start_menu()

    def setup_start_menu(self):
        """Create a custom LCARS-style start menu"""
        layout = QVBoxLayout()

        # Add system status
        self.system_status_label = QLabel("System Status: Online")
        self.system_status_label.setStyleSheet("color: orange; font-size: 18px;")
        layout.addWidget(self.system_status_label)

        # Add time and date
        self.time_date_label = QLabel()
        self.time_date_label.setStyleSheet("color: purple; font-size: 16px;")
        layout.addWidget(self.time_date_label)

        # Add buttons
        button_layout = QHBoxLayout()

        geant4_button = QPushButton("Geant4 Simulation")
        geant4_button.setStyleSheet("background-color: orange; color: black; border-radius: 15px;")
        geant4_button.clicked.connect(self.parent.show_simulation_tab)
        button_layout.addWidget(geant4_button)

        monitor_button = QPushButton("System Monitor")
        monitor_button.setStyleSheet("background-color: purple; color: black; border-radius: 15px;")
        monitor_button.clicked.connect(self.parent.show_system_monitor_tab)
        button_layout.addWidget(monitor_button)

        file_manager_button = QPushButton("File Manager")
        file_manager_button.setStyleSheet("background-color: blue; color: black; border-radius: 15px;")
        file_manager_button.clicked.connect(self.parent.show_file_manager_tab)
        button_layout.addWidget(file_manager_button)

        layout.addLayout(button_layout)

        # Add start menu to the main layout
        self.parent.centralWidget().layout().addLayout(layout)

        # Update time and date dynamically
        self.update_time_date()

    def update_time_date(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.time_date_label.setText(f"Time: {current_time} | Date: {current_date}")