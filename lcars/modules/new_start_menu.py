from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget, QStackedWidget
from PyQt6.QtCore import QTimer, Qt

class NewStartMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: black;")
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Add LCARS header
        self.header_label = QLabel("LCARS Unified Control System")
        self.header_label.setStyleSheet("color: orange; font-size: 24px; font-weight: bold; text-align: center;")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.header_label)

        # Add system status
        self.system_status_label = QLabel("System Status: Online")
        self.system_status_label.setStyleSheet("color: rgb(255, 103, 83); font-size: 18px; border: none;")
        main_layout.addWidget(self.system_status_label)

        # Add time and date
        self.time_date_label = QLabel()
        self.time_date_label.setStyleSheet("color: rgb(255, 151, 123); font-size: 16px; border: none;")
        main_layout.addWidget(self.time_date_label)

        # Add main content area with stacked widget
        self.content_area = QStackedWidget()
        main_layout.addWidget(self.content_area, 1)

        # Add navigation buttons
        button_layout = QHBoxLayout()

        simulation_button = QPushButton("Geant4 Simulation")
        simulation_button.setStyleSheet("background-color: rgb(231, 68, 42); color: white; border: none; border-radius: 15px;")
        simulation_button.clicked.connect(self.show_simulation_tab)
        button_layout.addWidget(simulation_button)

        monitor_button = QPushButton("System Monitor")
        monitor_button.setStyleSheet("background-color: rgb(42, 113, 147); color: white; border: none; border-radius: 15px;")
        monitor_button.clicked.connect(self.show_monitor_tab)
        button_layout.addWidget(monitor_button)

        file_manager_button = QPushButton("File Manager")
        file_manager_button.setStyleSheet("background-color: rgb(55, 166, 209); color: white; border: none; border-radius: 15px;")
        file_manager_button.clicked.connect(self.show_file_manager_tab)
        button_layout.addWidget(file_manager_button)

        main_layout.addLayout(button_layout)

        # Add footer
        self.footer_label = QLabel("LCARS Framework - Version 2.0")
        self.footer_label.setStyleSheet("color: orange; font-size: 16px; text-align: center;")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.footer_label)

        # Initialize tabs
        self.setup_simulation_tab()
        self.setup_monitor_tab()
        self.setup_file_manager_tab()

        # Update time and date dynamically
        self.update_time_date()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_date)
        self.timer.start(1000)

    def update_time_date(self):
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.time_date_label.setText(f"Time: {current_time} | Date: {current_date}")

    def setup_simulation_tab(self):
        simulation_tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Simulation Tab"))
        simulation_tab.setLayout(layout)
        self.content_area.addWidget(simulation_tab)

    def setup_monitor_tab(self):
        monitor_tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("System Monitor Tab"))
        monitor_tab.setLayout(layout)
        self.content_area.addWidget(monitor_tab)

    def setup_file_manager_tab(self):
        file_manager_tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("File Manager Tab"))
        file_manager_tab.setLayout(layout)
        self.content_area.addWidget(file_manager_tab)

    def show_simulation_tab(self):
        self.content_area.setCurrentIndex(0)

    def show_monitor_tab(self):
        self.content_area.setCurrentIndex(1)

    def show_file_manager_tab(self):
        self.content_area.setCurrentIndex(2)