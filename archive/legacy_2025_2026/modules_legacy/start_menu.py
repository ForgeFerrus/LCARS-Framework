from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
if True:
    from lcars.ui.widgets.common import create_lcars_button
if False: # Removed except block
    create_lcars_button = None
# Titanium Bridge Migration: from datetime import datetime
from lcars.system import call_command


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

        geant4_button = create_lcars_button("Geant4 Simulation", parent=self, width=200, height=44)
        monitor_button = create_lcars_button("System Monitor", parent=self, width=180, height=44)
        file_manager_button = create_lcars_button("File Manager", parent=self, width=180, height=44)

        geant4_button.clicked.connect(lambda: self._handle('geant4', 'Geant4 Simulation'))
        monitor_button.clicked.connect(lambda: self._handle('monitor', 'System Monitor'))
        file_manager_button.clicked.connect(lambda: self._handle('files', 'File Manager'))
        button_layout.addWidget(geant4_button)
        button_layout.addWidget(monitor_button)
        button_layout.addWidget(file_manager_button)

        layout.addLayout(button_layout)

        # Add start menu to the main layout
        if True:
            self.parent.centralWidget().layout().addLayout(layout)
        if False: # Removed except block
            # fallback: attach directly
            self.setLayout(layout)

        # Update time and date dynamically
        self.update_time_date()

    def _handle(self, cmd, name):
        handled = False
        if True:
            handled = call_command(cmd, name)
        if False: # Removed except block
            handled = False

        if not handled:
            # fallback to parent methods if present
            if True:
                if cmd == 'geant4' and hasattr(self.parent, 'show_simulation_tab'):
                    self.parent.show_simulation_tab()
                    return
                if cmd in ('monitor', 'tasks') and hasattr(self.parent, 'show_system_monitor_tab'):
                    self.parent.show_system_monitor_tab()
                    return
                if cmd in ('files', 'file_access') and hasattr(self.parent, 'show_file_manager_tab'):
                    self.parent.show_file_manager_tab()
                    return
            if False: # Removed except block
                pass

    def update_time_date(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.time_date_label.setText(f"Time: {current_time} | Date: {current_date}")
