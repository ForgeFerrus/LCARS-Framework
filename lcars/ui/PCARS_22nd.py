
"""
LCARS Interface - 22nd Century Edition
Palette-driven NX-01 (PCARS22ndCentury) interface: Projects, Data Analysis, Files, Simulation, Settings
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTabWidget, QListWidget, QTableWidget, QTableWidgetItem, QTreeView
from PyQt6.QtGui import QFileSystemModel
from lcars.themes.eras.PCARSPanel import PCARS22Panel, PCARS22Button, PCARS22MiniButton
from PyQt6.QtCore import Qt, QTimer, QDir
from PyQt6.QtGui import QFont
from pathlib import Path
from lcars.ui.login.pcars22_login import PCARS22LoginScreen
from lcars.themes.lcars_palette import LCARSEra, get_palette_by_name, get_era_palette, get_random_button_color 
import os
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PCARS22ndCentury(QMainWindow):
	def __init__(self, root_path=None, skip_login: bool = True):
		super().__init__()
		self.setWindowTitle("NX-01 Project Control (22nd Century)")
		self.showFullScreen()
		self.root_path = Path(root_path) if root_path else Path('.')
		# Використовуємо правильний ключ для палітри 22-го століття
		self.colors = get_palette_by_name("22nd")
		btn_colors = list(self.colors.get('button_colors', []))
		def _bc(i: int, default: str) -> str:
			try:
				return btn_colors[i]
			except Exception:
				return default
		self.colors.setdefault('panel', self.colors.get('panel_color', '#111111'))
		# Skip login and show main UI directly
		self._show_main_ui()

	def _show_login(self):
		self.login = PCARS22LoginScreen()
		self.login.login_successful.connect(self._show_main_ui)
		self.setCentralWidget(self.login)

	def _show_main_ui(self):
		# --- LCARS Full-Screen Layout ---
		# Основна панель без рамки
		main_widget = QWidget()
		main_widget.setStyleSheet("background: #000000;")
		main_layout = QHBoxLayout(main_widget)
		main_layout.setContentsMargins(0, 0, 0, 0)
		main_layout.setSpacing(0)
		
		# Get button colors for reuse
		btn_colors = list(self.colors.get('button_colors', []))
		self.btn_colors = btn_colors  # Save for later use

		# --- Left: Vertical LCARS Menu ---
		menu_widget = QWidget()
		menu_widget.setStyleSheet("background: #000000;")
		menu_widget.setFixedWidth(200)
		menu_layout = QVBoxLayout(menu_widget)
		menu_layout.setContentsMargins(20, 40, 10, 40)
		menu_layout.setSpacing(15)
		self.menu_buttons = []
		tab_names = ["PROJECTS", "DATA ANALYSIS", "FILES", "SIMULATION", "SETTINGS"]
		for idx, name in enumerate(tab_names):
			btn = PCARS22Button(label=name.upper(), number=f"{idx+1:02}-NX01", color=btn_colors[1] if len(btn_colors) > 1 else "#269EEE")
			btn.setMinimumHeight(54)
			btn.mousePressEvent = lambda a0, i=idx: self._switch_tab(i)
			menu_layout.addWidget(btn)
			self.menu_buttons.append(btn)
		menu_layout.addStretch()
		# menu_layout.addWidget(Indicator22(color="#FFE600", text="NX-01"))
		
		# Кнопка конструктора
		self.constructor_btn = PCARS22MiniButton(label="EDIT", color_index=2)
		self.constructor_btn.clicked.connect(self.open_constructor)
		menu_layout.addWidget(self.constructor_btn)
		
		# Кнопка функціонального редактора
		self.editor_btn = PCARS22MiniButton(label="DESIGN", color_index=3)
		self.editor_btn.clicked.connect(self.open_functional_editor)
		menu_layout.addWidget(self.editor_btn)
		
		self.exit_btn = PCARS22MiniButton(label="EXIT", color_index=1)
		self.exit_btn.clicked.connect(self.close)
		menu_layout.addWidget(self.exit_btn)
		main_layout.addWidget(menu_widget)

		# --- Center: Main Content Area ---
		center_widget = QWidget()
		center_widget.setStyleSheet("background: #000000;")
		center_layout = QVBoxLayout(center_widget)
		center_layout.setContentsMargins(30, 30, 30, 30)
		center_layout.setSpacing(20)

		# Header
		header_label = QLabel("NX-01 PROJECT CONTROL PANEL")
		header_label.setStyleSheet(f"""
			QLabel {{
				color: {btn_colors[2] if len(btn_colors) > 2 else '#FFE600'};
				font-size: 32px;
				font-weight: bold;
				background: transparent;
				letter-spacing: 3px;
				font-family: 'Arial', sans-serif;
			}}
		""")
		header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
		center_layout.addWidget(header_label)

		# --- Tabs ---
		self.tabs = []
		self.tabs_widget = QWidget()
		self.tabs_layout = QVBoxLayout(self.tabs_widget)
		self.tabs_layout.setContentsMargins(0, 0, 0, 0)
		self.tabs_layout.setSpacing(0)
		center_layout.addWidget(self.tabs_widget, 1)

		self._init_projects_tab(btn_colors)
		self._init_analysis_tab(btn_colors)
		self._init_files_tab(btn_colors)
		self._init_simulation_tab(btn_colors)
		self._init_settings_tab(btn_colors)
		self._switch_tab(0)

		# Footer
		footer_widget = QWidget()
		footer_widget.setStyleSheet("background: #000000;")
		footer_layout = QHBoxLayout(footer_widget)
		footer_layout.setContentsMargins(30, 15, 30, 15)
		
		footer_label = QLabel("LCARS NX-01 | 22nd Century | Stardate: 2151.1")
		footer_label.setStyleSheet(f"color: {btn_colors[1] if len(btn_colors) > 1 else '#FFE600'}; font-size: 18px; background: transparent;")
		footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
		footer_layout.addWidget(footer_label)
		footer_layout.addWidget(PCARS22MiniButton(label="HELP", color_index=0))
		center_layout.addWidget(footer_widget)

		main_layout.addWidget(center_widget, 1)
		self.setCentralWidget(main_widget)
		
		# Глобальна стилізація віджетів для усунення вигляду Windows
		self.setStyleSheet(f"""
			QMainWindow {{ background: #000; }}
			QListWidget, QTableWidget, QTreeView, QTextEdit {{
				background-color: #050505;
				color: {btn_colors[1] if len(btn_colors) > 1 else '#FFE600'};
				border: 1px solid #333;
				border-radius: 4px;
				font-family: 'Arial', sans-serif;
			}}
			QHeaderView::section {{
				background-color: #1A1A1A;
				color: {btn_colors[2] if len(btn_colors) > 2 else '#269EEE'};
				padding: 4px;
				border: 1px solid #333;
				font-weight: bold;
			}}
			QScrollBar:vertical {{
				border: none;
				background: #000;
				width: 10px;
			}}
			QScrollBar::handle:vertical {{
				background: {btn_colors[1] if len(btn_colors) > 1 else '#FFE600'};
				border-radius: 5px;
				min-height: 20px;
			}}
		""")


	def _switch_tab(self, idx):
		for i, tab in enumerate(self.tabs):
			tab.setVisible(i == idx)
		for i, btn in enumerate(self.menu_buttons):
			btn.setStyleSheet(f"background: {self.btn_colors[0] if i == idx else '#CCCCCC'}; color: #111; font-weight: bold;")
			
	def open_functional_editor(self):
		"""Відкрити функціональний редактор"""
		try:
			# Імпортуємо функціональний редактор
			from lcars.ui.functional_editor import FunctionalLCARSEditor
			editor_window = FunctionalLCARSEditor()
			editor_window.show()
			
			# Встановлюємо фокус на редактор
			editor_window.raise_()
			editor_window.activateWindow()
			
		except ImportError:
			# Якщо редактор не знайдено, показуємо повідомлення
			from PyQt6.QtWidgets import QMessageBox
			QMessageBox.information(self, "Editor", "Functional LCARS Editor not found.")
		except Exception as e:
			# Інші помилки
			from PyQt6.QtWidgets import QMessageBox
			QMessageBox.critical(self, "Error", f"Failed to open editor: {str(e)}")

	def open_constructor(self):
		"""Відкрити конструктор інтерфейсу"""
		try:
			# Імпортуємо реальний конструктор
			from lcars.themes.eras.Constructor import LCARSConstructor
			constructor_window = LCARSConstructor(faction="22nd")
			constructor_window.show()
			
			# Встановлюємо фокус на конструктор
			constructor_window.raise_()
			constructor_window.activateWindow()
			
		except ImportError:
			# Якщо конструктор не знайдено, показуємо повідомлення
			from PyQt6.QtWidgets import QMessageBox
			QMessageBox.information(self, "Constructor", "LCARS Constructor not found. Please check if Constructor.py exists.")
		except Exception as e:
			# Інші помилки
			from PyQt6.QtWidgets import QMessageBox
			QMessageBox.critical(self, "Error", f"Failed to open constructor: {str(e)}")


	def _init_projects_tab(self, btn_colors):
		# from lcars.themes.eras.PCARSConstructor import Radar22
		tab = PCARS22Panel()
		layout = QVBoxLayout(tab)
		# Декоративний LCARS-блок + Radar
		deco_row = QHBoxLayout()
		deco_row.addWidget(PCARS22Button(label="STD", number="01-STD", color="#FFE600"))
		deco_row.addWidget(PCARS22Button(label="DAT", number="02-DAT", color="#01B9E6"))
		deco_row.addWidget(PCARS22Button(label="MOD", number="03-MOD", color="#0798C9"))
		# deco_row.addWidget(Radar22())
		layout.addLayout(deco_row)
		# Заголовок
		label = QLabel("Discovered Projects (ENX*/NCC-*)")
		label.setStyleSheet(f"color: {btn_colors[0] if len(btn_colors) > 0 else '#FFE600'}; font-size: 26px; font-weight: bold; background: transparent;")
		layout.addWidget(label)
		# Індикатор статусу
		status_row = QHBoxLayout()
		status_row.addWidget(PCARS22MiniButton(label="SCAN", color_index=0))
		self.status_label = QLabel("READY")
		self.status_label.setStyleSheet(f"color: {btn_colors[1] if len(btn_colors) > 1 else '#FFE600'}; font-size: 20px; background: transparent;")
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
		self.open_btn = PCARS22Button(label="Open Project", number="01-OPEN", color=btn_colors[1] if len(btn_colors) > 1 else "#269EEE")
		self.open_btn.mousePressEvent = lambda a0: self._open_project()
		btn_row.addWidget(self.open_btn)
		btn_row.addWidget(PCARS22MiniButton(label="REFRESH", color_index=1))
		btn_row.addStretch()
		layout.addLayout(btn_row)
		tab.setStyleSheet(f"background: {self.colors['background']};")
		self.tabs.append(tab)
		self.tabs_layout.addWidget(tab)

	def _init_analysis_tab(self, btn_colors):
		# from lcars.themes.eras.PCARSConstructor import Indicator22
		tab = PCARS22Panel()
		layout = QVBoxLayout(tab)
		# Декоративний LCARS-блок + Indicator
		deco_row = QHBoxLayout()
		deco_row.addWidget(PCARS22Button(label="ANA", number="04-ANA", color="#FFE600"))
		deco_row.addWidget(PCARS22Button(label="VIS", number="05-VIS", color="#01B9E6"))
		deco_row.addWidget(PCARS22Button(label="REP", number="06-REP", color="#0798C9"))
		# deco_row.addWidget(Indicator22(color="#01B9E6", text="DATA"))
		layout.addLayout(deco_row)
		# Заголовок
		label = QLabel("Data Analysis")
		label.setStyleSheet(f"color: {btn_colors[0] if len(btn_colors) > 0 else '#FFE600'}; font-size: 26px; font-weight: bold; background: transparent;")
		layout.addWidget(label)
		# Індикатор статусу
		status_row = QHBoxLayout()
		status_row.addWidget(PCARS22MiniButton(label="ANALYZE", color_index=0))
		self.analysis_status = QLabel("WAITING")
		self.analysis_status.setStyleSheet(f"color: {btn_colors[1] if len(btn_colors) > 1 else '#FFE600'}; font-size: 20px; background: transparent;")
		status_row.addWidget(self.analysis_status)
		status_row.addStretch()
		layout.addLayout(status_row)
		# Таблиця даних
		self.analysis_table = QTableWidget(0, 3)
		self.analysis_table.setHorizontalHeaderLabels(["File", "Size (KB)", "Type"])
		layout.addWidget(self.analysis_table, 1)
		# Графік
		self.plot_canvas = FigureCanvas(Figure(figsize=(4,2)))
		layout.addWidget(self.plot_canvas)
		# Кнопки дій
		btn_row = QHBoxLayout()
		self.analyze_btn = PCARS22Button(label="Analyze Selected Project", number="02-ANALYZE", color=btn_colors[1] if len(btn_colors) > 1 else "#269EEE")
		self.analyze_btn.mousePressEvent = lambda a0: self._analyze_project()
		btn_row.addWidget(self.analyze_btn)
		btn_row.addWidget(PCARS22MiniButton(label="EXPORT", color_index=2))
		btn_row.addStretch()
		layout.addLayout(btn_row)
		tab.setStyleSheet(f"background: {self.colors['background']};")
		self.tabs.append(tab)
		self.tabs_layout.addWidget(tab)

	def _init_files_tab(self, btn_colors):
		# from lcars.themes.eras.PCARSConstructor import VerticalScale22
		tab = PCARS22Panel()
		layout = QVBoxLayout(tab)
		# Декоративний LCARS-блок + VerticalScale
		deco_row = QHBoxLayout()
		deco_row.addWidget(PCARS22Button(label="FIL", number="07-FIL", color="#FFE600"))
		deco_row.addWidget(PCARS22Button(label="DIR", number="08-DIR", color="#01B9E6"))
		deco_row.addWidget(PCARS22Button(label="SRC", number="09-SRC", color="#0798C9"))
		# deco_row.addWidget(VerticalScale22("FILES", color="#0798C9"))
		layout.addLayout(deco_row)
		# Заголовок
		label = QLabel("Project Files")
		label.setStyleSheet(f"color: {btn_colors[0] if len(btn_colors) > 0 else '#FFE600'}; font-size: 26px; font-weight: bold; background: transparent;")
		layout.addWidget(label)
		# Індикатор статусу
		status_row = QHBoxLayout()
		status_row.addWidget(PCARS22MiniButton(label="FILES", color_index=0))
		self.files_status = QLabel("READY")
		self.files_status.setStyleSheet(f"color: {btn_colors[1] if len(btn_colors) > 1 else '#FFE600'}; font-size: 20px; background: transparent;")
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

	def _init_simulation_tab(self, btn_colors):
		# from lcars.themes.eras.PCARSConstructor import Radar22
		tab = PCARS22Panel()
		layout = QVBoxLayout(tab)
		# Декоративний LCARS-блок + Radar
		deco_row = QHBoxLayout()
		deco_row.addWidget(PCARS22Button(label="SIM", number="10-SIM", color="#FFE600"))
		deco_row.addWidget(PCARS22Button(label="RUN", number="11-RUN", color="#01B9E6"))
		deco_row.addWidget(PCARS22Button(label="LOG", number="12-LOG", color="#0798C9"))
		# deco_row.addWidget(Radar22())
		layout.addLayout(deco_row)
		# Заголовок
		label = QLabel("Simulation")
		label.setStyleSheet(f"color: {btn_colors[0] if len(btn_colors) > 0 else '#FFE600'}; font-size: 26px; font-weight: bold; background: transparent;")
		layout.addWidget(label)
		# Індикатор статусу
		status_row = QHBoxLayout()
		status_row.addWidget(PCARS22MiniButton(label="SIM", color_index=0))
		self.sim_status = QLabel("IDLE")
		self.sim_status.setStyleSheet(f"color: {btn_colors[1] if len(btn_colors) > 1 else '#FFE600'}; font-size: 20px; background: transparent;")
		status_row.addWidget(self.sim_status)
		status_row.addStretch()
		layout.addLayout(status_row)
		tab.setStyleSheet(f"background: {self.colors['background']};")
		self.tabs.append(tab)
		self.tabs_layout.addWidget(tab)

	def _init_settings_tab(self, btn_colors):
		# from lcars.themes.eras.PCARSConstructor import LogBlock22
		tab = PCARS22Panel()
		layout = QVBoxLayout(tab)
		# Декоративний LCARS-блок + LogBlock
		deco_row = QHBoxLayout()
		deco_row.addWidget(PCARS22Button(label="CFG", number="13-CFG", color="#FFE600"))
		deco_row.addWidget(PCARS22Button(label="USR", number="14-USR", color="#01B9E6"))
		deco_row.addWidget(PCARS22Button(label="THE", number="15-THE", color="#0798C9"))
		# deco_row.addWidget(LogBlock22())
		layout.addLayout(deco_row)
		# Заголовок
		label = QLabel("Settings")
		label.setStyleSheet(f"color: {btn_colors[0] if len(btn_colors) > 0 else '#FFE600'}; font-size: 26px; font-weight: bold; background: transparent;")
		layout.addWidget(label)
		# Індикатор статусу
		status_row = QHBoxLayout()
		status_row.addWidget(PCARS22MiniButton(label="SETTINGS", color_index=0))
		self.settings_status = QLabel("READY")
		self.settings_status.setStyleSheet(f"color: {btn_colors[1] if len(btn_colors) > 1 else '#FFE600'}; font-size: 20px; background: transparent;")
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
		# Plot file size distribution
		ax = self.plot_canvas.figure.subplots()
		ax.clear()
		if sizes:
			ax.hist(sizes, bins=10, color=btn_colors[1] if len(btn_colors) > 1 else "#269EEE")
			ax.set_title("File Size Distribution (KB)")
			ax.set_xlabel("Size (KB)")
			ax.set_ylabel("Count")
		self.plot_canvas.draw()


if __name__ == "__main__":
	import sys
	print("LCARS_22nd.py LOADED")
	from PyQt6.QtWidgets import QApplication
	app = QApplication(sys.argv)
	window = PCARS22ndCentury(root_path=Path("."))
	window.show()
	sys.exit(app.exec())

