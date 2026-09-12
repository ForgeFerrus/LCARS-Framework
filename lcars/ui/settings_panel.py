# LCARS Settings Panel
# This is a PyQt6-based settings panel for full system configuration (except BIOS/environment).

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget, QFormLayout, QLineEdit, QComboBox, QCheckBox, QApplication)
from PyQt6.QtCore import Qt
from lcars.core.system import MasterSystem

class SettingsPanel(QWidget):
    def __init__(self, master_system: MasterSystem):
        super().__init__()
        self.master_system = master_system
        self.setWindowTitle("LCARS System Settings")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_general_tab(), "General")
        self.tabs.addTab(self._create_modules_tab(), "Modules")
        self.tabs.addTab(self._create_engineering_tab(), "Engineering")
        self.tabs.addTab(self._create_plugins_tab(), "Plugins")
        self.tabs.addTab(self._create_copilot_tab(), "Copilot")
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def _create_general_tab(self):
        tab = QWidget()
        form = QFormLayout()
        form.addRow("Era", QLineEdit(str(self.master_system.era)))
        form.addRow("Faction", QLineEdit(str(self.master_system.faction)))
        form.addRow("Alert Level", QLineEdit(str(self.master_system.alert.current_level.name)))
        form.addRow("Language", QLineEdit(str(self.master_system.config.get('app', 'language', 'en'))))
        form.addRow("Theme", QLineEdit(str(self.master_system.config.get('app', 'theme', 'default'))))
        form.addRow("Edit Mode", QLineEdit(str(self.master_system.config.get('app', 'edit_mode', 'normal'))))
        tab.setLayout(form)
        return tab

    def _create_modules_tab(self):
        tab = QWidget()
        form = QFormLayout()
        form.addRow("Project Manager", QCheckBox())
        form.addRow("Sound Manager", QCheckBox())
        form.addRow("Mode Manager", QCheckBox())
        form.addRow("Network Manager", QCheckBox())
        form.addRow("Memory", QCheckBox())
        tab.setLayout(form)
        return tab

    def _create_engineering_tab(self):
        tab = QWidget()
        form = QFormLayout()
        form.addRow("Telemetry", QCheckBox())
        form.addRow("Metrics Thread", QCheckBox())
        form.addRow("Nova Act", QCheckBox())
        tab.setLayout(form)
        return tab

    def _create_plugins_tab(self):
        tab = QWidget()
        form = QFormLayout()
        form.addRow("Plugin Manager", QCheckBox())
        tab.setLayout(form)
        return tab

    def _create_copilot_tab(self):
        tab = QWidget()
        form = QFormLayout()
        form.addRow("Copilot Enabled", QCheckBox())
        form.addRow("Model", QLineEdit("qwen/qwen3-32b"))
        tab.setLayout(form)
        return tab

if __name__ == "__main__":
    # Titanium Bridge Migration: import sys
    app = QApplication(sys.argv)
    ms = MasterSystem()
    panel = SettingsPanel(ms)
    panel.show()
    sys.exit(app.exec())
