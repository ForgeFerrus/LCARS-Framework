
"""
LCARS Interface - 23rd Century Edition
Palette-driven TOS (PCARS23rdCentury) interface: Projects, Data Analysis, Files, Simulation, Settings
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QTableWidget, QTableWidgetItem, QTreeView
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt
from pathlib import Path
from lcars.themes.lcars_palette import get_palette_by_name
from lcars.themes.eras.pcars23_components import PCARS23Panel, PCARS23Button, PCARS23MiniButton
import os

class PCARS23rdCentury(QMainWindow):
    def __init__(self, root_path=None, selector=None):
        super().__init__()
        self.setWindowTitle("Constitution Class Project Control (23rd Century)")
        self.showFullScreen()
        self.root_path = Path(root_path) if root_path else Path('.')
        self.colors = get_palette_by_name("23rd")
        self._show_main_ui()

    def _show_main_ui(self):
        # --- LCARS Full-Screen Layout ---
        main_panel = PCARS23Panel()
        main_layout = QHBoxLayout(main_panel)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Left: Vertical LCARS Menu ---
        menu_panel = PCARS23Panel()
        menu_panel.setFixedWidth(180)
        menu_layout = QVBoxLayout(menu_panel)
        menu_layout.setContentsMargins(16, 32, 8, 32)
        menu_layout.setSpacing(18)
        self.menu_buttons = []
        tab_names = ["Projects", "Data Analysis", "Files", "Simulation", "Settings"]
        for idx, name in enumerate(tab_names):
            btn = PCARS23Button(label=name.upper(), number=f"{idx+1:02}-TOS", color=self.colors['accent1'])
            btn.setMinimumHeight(54)
            btn.mousePressEvent = lambda a0, i=idx: self._switch_tab(i)
            menu_layout.addWidget(btn)
            self.menu_buttons.append(btn)
        menu_layout.addStretch()
        menu_layout.addWidget(PCARS23MiniButton(label="EXIT"))
        main_layout.addWidget(menu_panel)

        # --- Center: Main Content ---
        center_panel = PCARS23Panel()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(24, 24, 24, 24)
        center_layout.setSpacing(16)

        # Header
        header_panel = PCARS23Panel()
        header_layout = QHBoxLayout(header_panel)
        header_label = QLabel("Constitution Class Project Control Panel")
        header_label.setStyleSheet(f"color: {self.colors['accent3']}; font-size: 38px; font-weight: bold; background: transparent;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(header_label, 2)
        center_layout.addWidget(header_panel)

        # Tabs
        self.tabs = []
        self.tabs_panel = PCARS23Panel()
        self.tabs_layout = QVBoxLayout(self.tabs_panel)
        self.tabs_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs_layout.setSpacing(0)
        center_layout.addWidget(self.tabs_panel, 1)

        self._init_projects_tab()
        self._init_analysis_tab()
        self._init_files_tab()
        self._init_simulation_tab()
        self._init_settings_tab()
        self._switch_tab(0)

        # Footer
        footer_panel = PCARS23Panel()
        footer_layout = QHBoxLayout(footer_panel)
        footer_label = QLabel("LCARS TOS | 23rd Century | Stardate: 2265.1")
        footer_label.setStyleSheet(f"color: {self.colors['accent2']}; font-size: 20px; background: transparent;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(PCARS23MiniButton(label="HELP"))
        footer_layout.addWidget(footer_label, 1)
        footer_layout.addWidget(PCARS23MiniButton(label="EXIT"))
        center_layout.addWidget(footer_panel)

        main_layout.addWidget(center_panel, 1)
        self.setCentralWidget(main_panel)

    def _switch_tab(self, idx):
        for i, tab in enumerate(self.tabs):
            tab.setVisible(i == idx)
        for i, btn in enumerate(self.menu_buttons):
            btn.setStyleSheet(f"background: {self.colors['accent1' if i == idx else 'panel']}; color: #111; font-weight: bold;")

    def _init_projects_tab(self):
        tab = PCARS23Panel()
        layout = QVBoxLayout(tab)
        # Декоративний LCARS-блок
        deco_row = QHBoxLayout()
        deco_row.addWidget(PCARS23Button(label="STD", number="01-STD", color="#44B5FF"))
        deco_row.addWidget(PCARS23Button(label="DAT", number="02-DAT", color="#3366FF"))
        deco_row.addWidget(PCARS23Button(label="MOD", number="03-MOD", color="#D80000"))
        layout.addLayout(deco_row)
        # Заголовок
        label = QLabel("Discovered Projects (ENX*/NCC-*)")
        label.setStyleSheet(f"color: {self.colors['accent1']}; font-size: 22px; font-weight: bold; background: transparent;")
        layout.addWidget(label)
        # Індикатор статусу
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS23MiniButton(label="SCAN", color="#44B5FF"))
        self.status_label = QLabel("READY")
        self.status_label.setStyleSheet(f"color: {self.colors['accent2']}; font-size: 18px; background: transparent;")
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        layout.addLayout(status_row)
        # Список проектів
        self.project_list = QListWidget()
        self._scan_projects()
        self.project_list.currentItemChanged.connect(self._on_project_selected)
        layout.addWidget(self.project_list, 1)
        # Кнопки дій
        btn_row = QHBoxLayout()
        self.open_btn = PCARS23Button(label="Open Project", number="01-OPEN", color=self.colors['accent2'])
        self.open_btn.mousePressEvent = lambda a0: self._open_project()
        btn_row.addWidget(self.open_btn)
        btn_row.addWidget(PCARS23MiniButton(label="REFRESH", color="#44B5FF"))
        btn_row.addStretch()
        layout.addLayout(btn_row)
        tab.setStyleSheet(f"background: {self.colors['background']};")
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)

    def _init_analysis_tab(self):
        tab = PCARS23Panel()
        layout = QVBoxLayout(tab)
        # Декоративний LCARS-блок
        deco_row = QHBoxLayout()
        deco_row.addWidget(PCARS23Button(label="ANA", number="04-ANA", color="#44B5FF"))
        deco_row.addWidget(PCARS23Button(label="VIS", number="05-VIS", color="#3366FF"))
        deco_row.addWidget(PCARS23Button(label="REP", number="06-REP", color="#D80000"))
        layout.addLayout(deco_row)
        # Заголовок
        label = QLabel("Data Analysis")
        label.setStyleSheet(f"color: {self.colors['accent1']}; font-size: 22px; font-weight: bold; background: transparent;")
        layout.addWidget(label)
        # Індикатор статусу
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS23MiniButton(label="ANALYZE", color="#44B5FF"))
        self.analysis_status = QLabel("WAITING")
        self.analysis_status.setStyleSheet(f"color: {self.colors['accent2']}; font-size: 18px; background: transparent;")
        status_row.addWidget(self.analysis_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        # Таблиця даних
        self.analysis_table = QTableWidget(0, 3)
        self.analysis_table.setHorizontalHeaderLabels(["File", "Size (KB)", "Type"])
        layout.addWidget(self.analysis_table, 1)
        # Кнопки дій
        btn_row = QHBoxLayout()
        self.analyze_btn = PCARS23Button(label="Analyze Selected Project", number="02-ANALYZE", color=self.colors['accent2'])
        self.analyze_btn.mousePressEvent = lambda a0: self._analyze_project()
        btn_row.addWidget(self.analyze_btn)
        btn_row.addWidget(PCARS23MiniButton(label="EXPORT", color="#44B5FF"))
        btn_row.addStretch()
        layout.addLayout(btn_row)
        tab.setStyleSheet(f"background: {self.colors['background']};")
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)

    def _init_files_tab(self):
        tab = PCARS23Panel()
        layout = QVBoxLayout(tab)
        # Декоративний LCARS-блок
        deco_row = QHBoxLayout()
        deco_row.addWidget(PCARS23Button(label="FIL", number="07-FIL", color="#44B5FF"))
        deco_row.addWidget(PCARS23Button(label="DIR", number="08-DIR", color="#3366FF"))
        deco_row.addWidget(PCARS23Button(label="SRC", number="09-SRC", color="#D80000"))
        layout.addLayout(deco_row)
        # Заголовок
        label = QLabel("Project Files")
        label.setStyleSheet(f"color: {self.colors['accent1']}; font-size: 22px; font-weight: bold; background: transparent;")
        layout.addWidget(label)
        # Індикатор статусу
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS23MiniButton(label="FILES", color="#44B5FF"))
        self.files_status = QLabel("READY")
        self.files_status.setStyleSheet(f"color: {self.colors['accent2']}; font-size: 18px; background: transparent;")
        status_row.addWidget(self.files_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        # Дерево файлів
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_view = QTreeView()
        self.file_view.setModel(self.file_model)
        layout.addWidget(self.file_view, 1)
        tab.setStyleSheet(f"background: {self.colors['background']};")
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)

    def _init_simulation_tab(self):
        tab = PCARS23Panel()
        layout = QVBoxLayout(tab)
        # Декоративний LCARS-блок
        deco_row = QHBoxLayout()
        deco_row.addWidget(PCARS23Button(label="SIM", number="10-SIM", color="#44B5FF"))
        deco_row.addWidget(PCARS23Button(label="RUN", number="11-RUN", color="#3366FF"))
        deco_row.addWidget(PCARS23Button(label="LOG", number="12-LOG", color="#D80000"))
        layout.addLayout(deco_row)
        # Заголовок
        label = QLabel("Simulation (stub)")
        label.setStyleSheet(f"color: {self.colors['accent1']}; font-size: 22px; font-weight: bold; background: transparent;")
        layout.addWidget(label)
        # Індикатор статусу
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS23MiniButton(label="SIM", color="#44B5FF"))
        self.sim_status = QLabel("IDLE")
        self.sim_status.setStyleSheet(f"color: {self.colors['accent2']}; font-size: 18px; background: transparent;")
        status_row.addWidget(self.sim_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        tab.setStyleSheet(f"background: {self.colors['background']};")
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)

    def _init_settings_tab(self):
        tab = PCARS23Panel()
        layout = QVBoxLayout(tab)
        # Декоративний LCARS-блок
        deco_row = QHBoxLayout()
        deco_row.addWidget(PCARS23Button(label="CFG", number="13-CFG", color="#44B5FF"))
        deco_row.addWidget(PCARS23Button(label="USR", number="14-USR", color="#3366FF"))
        deco_row.addWidget(PCARS23Button(label="THE", number="15-THE", color="#D80000"))
        layout.addLayout(deco_row)
        # Заголовок
        label = QLabel("Settings (stub)")
        label.setStyleSheet(f"color: {self.colors['accent1']}; font-size: 22px; font-weight: bold; background: transparent;")
        layout.addWidget(label)
        # Індикатор статусу
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS23MiniButton(label="SETTINGS", color="#44B5FF"))
        self.settings_status = QLabel("READY")
        self.settings_status.setStyleSheet(f"color: {self.colors['accent2']}; font-size: 18px; background: transparent;")
        status_row.addWidget(self.settings_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        tab.setStyleSheet(f"background: {self.colors['background']};")
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)

    def _scan_projects(self):
        self.project_list.clear()
        for root, dirs, files in os.walk(self.root_path):
            for d in dirs:
                if d.startswith("ENX") or d.startswith("NCC-"):
                    self.project_list.addItem(str(Path(root) / d))
        if self.project_list.count() > 0:
            self.project_list.setCurrentRow(0)

    def _on_project_selected(self, current, previous):
        if current:
            self.selected_project = Path(current.text())
        else:
            self.selected_project = None

    def _open_project(self):
        if self.selected_project:
            self.file_model.setRootPath(str(self.selected_project))
            self.file_view.setRootIndex(self.file_model.index(str(self.selected_project)))

    def _analyze_project(self):
        if not self.selected_project:
            return
        self._load_analysis_data(self.selected_project)

    def _load_analysis_data(self, project_path):
        self.analysis_table.setRowCount(0)
        sizes = []
        for root, dirs, files in os.walk(project_path):
            for f in files:
                fpath = Path(root) / f
                size_kb = round(fpath.stat().st_size / 1024, 2)
                ext = fpath.suffix
                row = self.analysis_table.rowCount()
                self.analysis_table.insertRow(row)
                self.analysis_table.setItem(row, 0, QTableWidgetItem(str(fpath.relative_to(project_path))))
                self.analysis_table.setItem(row, 1, QTableWidgetItem(str(size_kb)))
                self.analysis_table.setItem(row, 2, QTableWidgetItem(ext))
                sizes.append(size_kb)

# --- main launcher ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = PCARS23rdCentury(root_path=Path("."))
    window.show()
    sys.exit(app.exec())
